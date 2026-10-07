"""
Runs policyengine-taxsim on a TAXSIM-35 input sample (step 2 of the
validation).

USAGE: python run_pe.py LETTER YEAR [--force]

reads samples/LYY.in.csv.gz and writes pe_output/LYY.out-pe.csv.gz and
pe_output/LYY.out-pe.stamp.json in the folder containing this script.

policyengine-taxsim runs in an ephemeral uv-managed environment that is
specified by pe_pin.json, so this script never imports PolicyEngine.
"""

import argparse
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import numpy as np
import pandas as pd


VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2021
LAST_YEAR = 2025
HERE = Path(__file__).resolve().parent
PIN_FILE = HERE / "pe_pin.json"

# TAXSIM idtl=2 output columns produced by the pinned policyengine-taxsim
# with state=0 input (see the Phase 0 entry in ../PLAN.md)
OUTPUT_COLUMNS = (
    ["taxsimid", "year", "state", "fiitax", "siitax", "fica", "tfica"]
    + ["v10", "v11", "v12", "v13", "v14", "v17"]
    + ["qbid", "niit", "addmed"]
    + ["v18", "v19", "v22", "v24", "v25", "v26", "v27", "v28", "v29"]
    + ["v32", "v34", "v35", "v36", "srebate"]
    + ["v37", "v38", "v39", "v40", "v42", "v43", "v44"]
    + ["actc", "cares", "frate", "srate"]
)


def read_pin():
    """
    Return dictionary containing the pe_pin.json contents.
    """
    with open(PIN_FILE, "r", encoding="utf-8") as pfile:
        return json.load(pfile)


def uvx_prefix(pin):
    """
    Return list containing the uvx command and options that select the
    pinned policyengine-taxsim environment.
    """
    uvx = shutil.which("uvx")
    if uvx is None:
        raise RuntimeError("uvx is not on PATH; see README.md for setup")
    repo = pin["policyengine_taxsim_repo"]
    sha = pin["policyengine_taxsim_sha"]
    return [
        uvx,
        "--python",
        pin["python_version"],
        "--from",
        f"git+{repo}@{sha}",
        "--with",
        f"policyengine-us=={pin['policyengine_us_version']}",
    ]


def pe_command(pin, infile, outfile):
    """
    Return list containing the command that runs policyengine-taxsim on
    INFILE and writes OUTFILE.
    """
    return (
        uvx_prefix(pin)
        + ["policyengine-taxsim", "policyengine", str(infile)]
        + ["--output", str(outfile)]
        + pin["pe_cli_options"]
    )


def resolved_versions(pin):
    """
    Return dictionary containing the package and Python versions that
    are actually used in the pinned environment.
    """
    code = (
        "import importlib.metadata as m, json, platform; "
        "print(json.dumps({"
        "'policyengine_us_version': m.version('policyengine-us'), "
        "'policyengine_core_version': m.version('policyengine-core'), "
        "'python_version_resolved': platform.python_version()}))"
    )
    proc = subprocess.run(
        uvx_prefix(pin) + ["python", "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def check_versions(pin, versions):
    """
    Raise RuntimeError if any resolved version differs from its pin.
    """
    errors = [
        f"{key} is {val} but pe_pin.json has {pin[key]}"
        for key, val in versions.items()
        if val != pin[key]
    ]
    if errors:
        raise RuntimeError("version check failed: " + "; ".join(errors))


def check_output(out, smpl):
    """
    Raise ValueError if PE output OUT is inconsistent with input SMPL.
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
    if "state" in out.columns:
        require((out.state == 0).all(), "state not zero")
    if errors:
        raise ValueError("PE output check failed: " + "; ".join(errors))


def sha256(path):
    """
    Return SHA-256 hex digest of the contents of file PATH.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    """
    Run policyengine-taxsim on the sample specified on the command line.
    """
    # pylint: disable=too-many-locals
    parser = argparse.ArgumentParser(
        prog="python run_pe.py",
        description=(
            "Runs the pinned policyengine-taxsim on samples/LYY.in.csv.gz "
            "and writes pe_output/LYY.out-pe.csv.gz plus a version stamp."
        ),
    )
    parser.add_argument(
        "LETTER", choices=VALID_LETTERS, help="assumption set letter"
    )
    parser.add_argument(
        "YEAR",
        type=int,
        choices=range(FIRST_YEAR, LAST_YEAR + 1),
        metavar="YEAR",
        help=f"tax year in [{FIRST_YEAR},{LAST_YEAR}]",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing PE output file",
    )
    parser.add_argument(
        "--indir",
        default=str(HERE / "samples"),
        help="input folder (default is samples next to this script)",
    )
    parser.add_argument(
        "--outdir",
        default=str(HERE / "pe_output"),
        help="output folder (default is pe_output next to this script)",
    )
    args = parser.parse_args()
    lyy = f"{args.LETTER}{args.YEAR % 100:02d}"
    infile = Path(args.indir) / f"{lyy}.in.csv.gz"
    outdir = Path(args.outdir)
    outfile = outdir / f"{lyy}.out-pe.csv.gz"
    stampfile = outdir / f"{lyy}.out-pe.stamp.json"
    if not infile.is_file():
        sys.stderr.write(f"ERROR: input file {infile} does not exist\n")
        return 1
    if outfile.exists() and not args.force:
        sys.stderr.write(
            f"ERROR: {outfile} exists; use --force to overwrite it\n"
        )
        return 1
    smpl = pd.read_csv(infile)
    if not (smpl.year == args.YEAR).all():
        sys.stderr.write(f"ERROR: {infile} contains a year other than "
                         f"{args.YEAR}\n")
        return 1
    pin = read_pin()
    versions = resolved_versions(pin)
    check_versions(pin, versions)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpin = Path(tmpdir) / f"{lyy}.in.csv"
        tmpout = Path(tmpdir) / f"{lyy}.out-pe.csv"
        tmpin.write_bytes(gzip.decompress(infile.read_bytes()))
        cmd = pe_command(pin, tmpin, tmpout)
        sys.stderr.write(f"running policyengine-taxsim on {infile.name}\n")
        start = time.time()
        subprocess.run(cmd, check=True)
        elapsed = time.time() - start
        out = pd.read_csv(tmpout)
        check_output(out, smpl)
        outdir.mkdir(parents=True, exist_ok=True)
        # store PE output bytes unchanged; zero gzip mtime makes the
        # file bytes depend only on the PE output
        outfile.write_bytes(gzip.compress(tmpout.read_bytes(), mtime=0))
    stamp = {
        "input_file": infile.name,
        "input_sha256": sha256(infile),
        "output_file": outfile.name,
        "output_sha256": sha256(outfile),
        "rows": len(out),
        "policyengine_taxsim_sha": pin["policyengine_taxsim_sha"],
        "pe_cli_options": pin["pe_cli_options"],
        **versions,
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


if __name__ == "__main__":
    sys.exit(main())
