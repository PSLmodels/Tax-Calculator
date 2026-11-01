"""
Runs the Tax-Simulator federal calculator on a TAXSIM-35 input sample
(step 2 of the validation).

USAGE: python run_ts.py LETTER YEAR [--force]
       python run_ts.py --all [--jobs N] [--force]

reads samples/LYY.in.csv.gz and writes ts_output/LYY.out-ts.csv.gz and
ts_output/LYY.out-ts.stamp.json in the folder containing this script.
The --all option runs every LETTER and YEAR combination, using N
concurrent processes.

Tax-Simulator is an R model, so this script runs run_ts.R with the
Rscript from the R environment specified in ts_pin.json, using a clone
of the Tax-Simulator repository at the commit pinned in ts_pin.json.
The clone is made if it does not exist.  The Tax-Simulator folder can
be specified by the --tsdir option or the TBLY_TS_DIR environment
variable, and Rscript by the --rscript option or the TBLY_TS_RSCRIPT
environment variable (see README.md).
"""

import argparse
import concurrent.futures
import datetime
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import numpy as np
import pandas as pd


VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2023
LAST_YEAR = 2025
DEFAULT_JOBS = 3
HERE = Path(__file__).resolve().parent
PIN_FILE = HERE / "ts_pin.json"
R_SCRIPT = HERE / "run_ts.R"
INDEXES_FILE = HERE / "ts_indexes.csv"
OVERRIDES_FILE = HERE / "ts_law_overrides.csv"

# TAXSIM-format output columns written by run_ts.R (see VARIABLES.md)
OUTPUT_COLUMNS = (
    ["taxsimid", "year", "fiitax", "fica", "tfica", "addmed", "v44"]
    + ["v10", "v11", "v12", "v13", "v14", "v17", "qbid", "v18"]
    + ["v19", "v28", "v26", "v27", "niit"]
    + ["v22", "actc", "v24", "v25", "cares"]
)


def read_pin():
    """
    Return dictionary containing the ts_pin.json contents.
    """
    with open(PIN_FILE, "r", encoding="utf-8") as pfile:
        return json.load(pfile)


def ts_folder(pin, tsdir):
    """
    Return Path of the Tax-Simulator clone: TSDIR if not None, else the
    TBLY_TS_DIR environment variable if set, else the default folder
    specified in PIN.
    """
    if tsdir is None:
        tsdir = os.environ.get("TBLY_TS_DIR")
    if tsdir is None:
        tsdir = pin["tax_simulator_dir_default"].replace(
            "<sha>", pin["tax_simulator_sha"]
        )
    return Path(tsdir).expanduser().resolve()


def git(tsdir, *args):
    """
    Return stdout of the git command with ARGS run in folder TSDIR.
    """
    proc = subprocess.run(
        ["git", "-C", str(tsdir), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def ensure_ts_clone(pin, tsdir):
    """
    Make a shallow clone of the pinned Tax-Simulator commit in folder
    TSDIR if it does not exist, and raise RuntimeError if TSDIR is not
    an unmodified clone at the pinned commit.
    """
    sha = pin["tax_simulator_sha"]
    if not tsdir.exists():
        sys.stderr.write(f"cloning Tax-Simulator {sha[:12]} into {tsdir}\n")
        tsdir.mkdir(parents=True)
        git(tsdir, "init", "--quiet")
        git(tsdir, "remote", "add", "origin", pin["tax_simulator_repo"])
        git(tsdir, "fetch", "--quiet", "--depth", "1", "origin", sha)
        git(tsdir, "checkout", "--quiet", "FETCH_HEAD")
    head = git(tsdir, "rev-parse", "HEAD")
    if head != sha:
        raise RuntimeError(
            f"{tsdir} is at commit {head} but ts_pin.json has {sha}"
        )
    if git(tsdir, "status", "--porcelain"):
        raise RuntimeError(f"{tsdir} contains modified or untracked files")


def rscript_path(pin, rscript):
    """
    Return path of the Rscript executable: RSCRIPT if not None, else the
    TBLY_TS_RSCRIPT environment variable if set, else the Rscript in the
    conda environment named in PIN.
    """
    if rscript is None:
        rscript = os.environ.get("TBLY_TS_RSCRIPT")
    if rscript is None:
        conda = shutil.which("conda")
        if conda is None:
            raise RuntimeError(
                "conda is not on PATH; use --rscript or TBLY_TS_RSCRIPT"
            )
        base = subprocess.run(
            [conda, "info", "--base"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        rscript = Path(base) / "envs" / pin["conda_env_name"] / "bin/Rscript"
    rscript = Path(rscript).expanduser()
    if not rscript.is_file():
        raise RuntimeError(f"Rscript {rscript} does not exist; see README.md")
    return rscript


def pinned_r_versions(pin):
    """
    Return dictionary mapping R package names (and "R" for r-base) to
    the versions pinned in PIN.
    """
    versions = {}
    for spec in pin["conda_packages"]:
        name, version = spec.split("=")
        name = name.removeprefix("r-")
        versions["R" if name == "base" else name] = version
    return versions


def resolved_r_versions(rscript, names):
    """
    Return dictionary mapping each of the R package NAMES (and "R") to
    the version installed in the R environment of RSCRIPT.
    """
    pkgs = ", ".join(f"'{name}'" for name in names if name != "R")
    code = (
        "cat(paste0('R=', getRversion()), sep = '\\n'); "
        f"for (p in c({pkgs})) "
        "cat(paste0(p, '=', packageVersion(p)), sep = '\\n')"
    )
    proc = subprocess.run(
        [str(rscript), "--vanilla", "-e", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return dict(
        line.split("=", 1) for line in proc.stdout.strip().splitlines()
    )


def check_r_versions(pin, rscript):
    """
    Return dictionary of resolved R and package versions, after raising
    RuntimeError if any of them differs from its pin.
    """
    pinned = pinned_r_versions(pin)
    resolved = resolved_r_versions(rscript, pinned.keys())
    errors = [
        f"{name} is {resolved.get(name)} but ts_pin.json has {version}"
        for name, version in pinned.items()
        if resolved.get(name) != version
    ]
    if errors:
        raise RuntimeError("version check failed: " + "; ".join(errors))
    return resolved


def check_output(out, smpl):
    """
    Raise ValueError if TS output OUT is inconsistent with input SMPL.
    """
    errors = []

    def require(condition, msg):
        if not condition:
            errors.append(msg)

    require(list(out.columns) == OUTPUT_COLUMNS, "unexpected columns")
    require(len(out) == len(smpl), "row count differs from input")
    if len(out) == len(smpl):
        require(
            np.array_equal(out.taxsimid.to_numpy(), smpl.taxsimid.to_numpy()),
            "taxsimid values differ from input",
        )
        require(
            np.array_equal(out.year.to_numpy(), smpl.year.to_numpy()),
            "year values differ from input",
        )
    require(not out.isna().any().any(), "missing values")
    if errors:
        raise ValueError("TS output check failed: " + "; ".join(errors))


def sha256(path):
    """
    Return SHA-256 hex digest of the contents of file PATH.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_one(letter, year, force, dirs, tools):
    """
    Run Tax-Simulator on the LETTER and YEAR sample in folder dirs["in"]
    and write the TS output and its stamp to folder dirs["out"],
    overwriting existing TS output only when FORCE is True, using the
    Tax-Simulator clone tools["tsdir"] and Rscript tools["rscript"]
    (None means use the default; see ts_folder and rscript_path).
    Return the exit code.
    """
    # pylint: disable=too-many-locals
    lyy = f"{letter}{year % 100:02d}"
    infile = Path(dirs["in"]) / f"{lyy}.in.csv.gz"
    outdir = Path(dirs["out"])
    outfile = outdir / f"{lyy}.out-ts.csv.gz"
    stampfile = outdir / f"{lyy}.out-ts.stamp.json"
    if not infile.is_file():
        sys.stderr.write(f"ERROR: input file {infile} does not exist\n")
        return 1
    if outfile.exists() and not force:
        sys.stderr.write(
            f"ERROR: {outfile} exists; use --force to overwrite it\n"
        )
        return 1
    smpl = pd.read_csv(infile)
    if not (smpl.year == year).all():
        sys.stderr.write(f"ERROR: {infile} contains a year other than "
                         f"{year}\n")
        return 1
    pin = read_pin()
    tsdir = ts_folder(pin, tools["tsdir"])
    ensure_ts_clone(pin, tsdir)
    rscript = rscript_path(pin, tools["rscript"])
    versions = check_r_versions(pin, rscript)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpout = Path(tmpdir) / f"{lyy}.out-ts.csv"
        cmd = [str(rscript), "--vanilla", str(R_SCRIPT), str(tsdir)]
        cmd += [str(infile.resolve()), str(tmpout)]
        cmd += [str(INDEXES_FILE), str(OVERRIDES_FILE)]
        sys.stderr.write(f"running Tax-Simulator on {infile.name}\n")
        start = time.time()
        subprocess.run(cmd, check=True)
        elapsed = time.time() - start
        out = pd.read_csv(tmpout)
        check_output(out, smpl)
        outdir.mkdir(parents=True, exist_ok=True)
        # store TS output bytes unchanged; zero gzip mtime makes the
        # file bytes depend only on the TS output
        outfile.write_bytes(gzip.compress(tmpout.read_bytes(), mtime=0))
    stamp = {
        "input_file": infile.name,
        "input_sha256": sha256(infile),
        "output_file": outfile.name,
        "output_sha256": sha256(outfile),
        "rows": len(out),
        "tax_simulator_sha": pin["tax_simulator_sha"],
        "run_ts_R_sha256": sha256(R_SCRIPT),
        "ts_indexes_sha256": sha256(INDEXES_FILE),
        "ts_law_overrides_sha256": sha256(OVERRIDES_FILE),
        "r_versions": versions,
        "run_date": datetime.date.today().isoformat(),
        "run_seconds": round(elapsed, 1),
    }
    with open(stampfile, "w", encoding="utf-8") as sfile:
        json.dump(stamp, sfile, indent=4)
        sfile.write("\n")
    sys.stderr.write(
        f"wrote {outfile.name} ({len(out)} rows, {elapsed:.0f} s)\n"
    )
    return 0


def run_all(force, dirs, tools, jobs):
    """
    Run every LETTER and YEAR combination using JOBS concurrent run_ts.py
    processes (see run_one for the meaning of the other arguments).
    Return the exit code.
    """
    # pylint: disable=too-many-locals
    # make the clone and check the R environment once before the
    # concurrent runs, so that they do not all try to clone
    sys.stderr.write("checking the Tax-Simulator clone and R environment\n")
    pin = read_pin()
    tsdir = ts_folder(pin, tools["tsdir"])
    ensure_ts_clone(pin, tsdir)
    rscript = rscript_path(pin, tools["rscript"])
    check_r_versions(pin, rscript)
    combos = [
        (letter, year)
        for letter in VALID_LETTERS
        for year in range(FIRST_YEAR, LAST_YEAR + 1)
    ]

    def run_child(combo):
        letter, year = combo
        cmd = [sys.executable, str(Path(__file__).resolve())]
        cmd += [letter, str(year), "--indir", dirs["in"]]
        cmd += ["--outdir", dirs["out"]]
        cmd += ["--tsdir", str(tsdir), "--rscript", str(rscript)]
        if force:
            cmd.append("--force")
        return subprocess.run(cmd, check=False, capture_output=True,
                              text=True)

    sys.stderr.write(f"running {len(combos)} samples using {jobs} "
                     "concurrent processes\n")
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(run_child, combo): combo for combo in combos}
        for future in concurrent.futures.as_completed(futures):
            letter, year = futures[future]
            proc = future.result()
            if proc.returncode == 0:
                lines = proc.stderr.strip().splitlines()
                sys.stderr.write((lines[-1] if lines else "done") + "\n")
            else:
                failures += 1
                sys.stderr.write(
                    f"ERROR: run_ts.py {letter} {year} failed with exit "
                    f"code {proc.returncode}:\n{proc.stdout}{proc.stderr}"
                )
    if failures:
        sys.stderr.write(f"ERROR: {failures} of {len(combos)} runs failed\n")
        return 1
    sys.stderr.write(f"all {len(combos)} runs succeeded\n")
    return 0


def main():
    """
    Run Tax-Simulator on the sample(s) specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python run_ts.py",
        description=(
            "Runs the pinned Tax-Simulator on samples/LYY.in.csv.gz "
            "and writes ts_output/LYY.out-ts.csv.gz plus a version stamp."
        ),
    )
    parser.add_argument(
        "LETTER",
        nargs="?",
        choices=VALID_LETTERS,
        help="assumption set letter (omit when using --all)",
    )
    parser.add_argument(
        "YEAR",
        nargs="?",
        type=int,
        choices=range(FIRST_YEAR, LAST_YEAR + 1),
        metavar="YEAR",
        help=(f"tax year in [{FIRST_YEAR},{LAST_YEAR}] "
              "(omit when using --all)"),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="run every LETTER and YEAR combination",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=DEFAULT_JOBS,
        help=("number of concurrent runs when using --all "
              f"(default is {DEFAULT_JOBS})"),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing TS output file",
    )
    parser.add_argument(
        "--indir",
        default=str(HERE / "samples"),
        help="input folder (default is samples next to this script)",
    )
    parser.add_argument(
        "--outdir",
        default=str(HERE / "ts_output"),
        help="output folder (default is ts_output next to this script)",
    )
    parser.add_argument(
        "--tsdir",
        default=None,
        help=("Tax-Simulator clone folder (default is $TBLY_TS_DIR if "
              "set, else the folder named in ts_pin.json)"),
    )
    parser.add_argument(
        "--rscript",
        default=None,
        help=("Rscript executable (default is $TBLY_TS_RSCRIPT if set, "
              "else Rscript in the conda environment named in "
              "ts_pin.json)"),
    )
    args = parser.parse_args()
    dirs = {"in": args.indir, "out": args.outdir}
    tools = {"tsdir": args.tsdir, "rscript": args.rscript}
    if args.all:
        if args.LETTER is not None or args.YEAR is not None:
            parser.error("LETTER and YEAR must be omitted when using --all")
        if args.jobs < 1:
            parser.error("--jobs must be at least one")
        return run_all(args.force, dirs, tools, args.jobs)
    if args.LETTER is None or args.YEAR is None:
        parser.error("LETTER and YEAR are required unless --all is used")
    return run_one(args.LETTER, args.YEAR, args.force, dirs, tools)


if __name__ == "__main__":
    sys.exit(main())
