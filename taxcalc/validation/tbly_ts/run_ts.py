"""
Runs the tax-simulator-gpu federal income and payroll tax calculator on
a TAXSIM-35 input sample (step 2 of the validation).

USAGE: python run_ts.py LETTER YEAR [--force]
       python run_ts.py --all [--jobs N] [--force]

reads samples/LYY.in.csv.gz and writes ts_output/LYY.out-ts.csv.gz and
ts_output/LYY.out-ts.stamp.json in the folder containing this script.
The --all option runs every LETTER and YEAR combination, using N
concurrent processes.

tax-simulator-gpu is a Python model with its own pinned environment, so
this script translates the sample into tax-simulator-gpu tax units (see
VARIABLES.md), runs ts_batch.py in that environment using uv and a
clone of the tax-simulator-gpu repository at the commit pinned in
ts_pin.json, and translates the tax-simulator-gpu results into TAXSIM
output.  The clone is made if it does not exist.  The clone folder can
be specified by the --tsdir option or the TBLY_TS_DIR environment
variable, and the uv executable by the --uv option or the TBLY_TS_UV
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
BATCH_SCRIPT = HERE / "ts_batch.py"

# TAXSIM-formatted output columns written by this script (VARIABLES.md)
OUTPUT_COLUMNS = (
    ["taxsimid", "year", "fiitax", "fica", "tfica", "addmed", "v44"]
    + ["v10", "v11", "v12", "v13", "v14", "v17", "qbid", "v18"]
    + ["v19", "v28", "v26", "v27", "niit"]
    + ["v22", "actc", "v24", "v25", "cares"]
)

# TAXSIM inputs that have no tax-simulator-gpu translation (VARIABLES.md)
MUST_BE_ZERO = [
    "nonprop", "transfers", "rentpaid", "pprofinc", "sprofinc",
    "age4", "age5",
]

# tax-simulator-gpu record columns that are always zero (VARIABLES.md);
# ts_batch.py fails if a column the batch command reads is missing
ZERO_COLUMNS = [
    "alimony", "alimony_exp", "amt_ftc", "amt_nols", "aoc_exp",
    "auto_int_exp", "basis.equities", "basis.other_home",
    "basis.pass_throughs", "basis.primary_home", "basis.re_fund",
    "casualty_exp", "char_cash", "char_noncash", "divorce_year", "dpad",
    "early_penalty", "ed_exp", "ei_prior_yr", "estate", "estate_loss",
    "excess_ptc", "exempt_int", "farm", "farm1", "farm2",
    "first_mort_bal", "first_mort_int", "ftc", "gbc", "hsa_contr",
    "inv_int_exp", "ira_penalty", "job_exp", "keogh_contr", "kg_1250",
    "kg_collect", "kg_lt_basis", "kg_lt_years_held", "llc_exp", "male1",
    "med_exp", "net_ptc", "old_cred", "ot", "ot1", "ot2",
    "other_above_ded", "other_gains", "other_inc", "other_misc_exp",
    "other_nonref", "part_179", "part_active", "part_active_loss",
    "part_passive", "part_passive_loss", "part_se1", "part_se2",
    "prior_yr_cred", "q_death1", "q_death2", "recapture_tax",
    "rent_loss", "res_energy_cred", "salt_inc_sales", "salt_pers",
    "savers_cred", "scorp_179", "scorp_active_loss", "scorp_passive",
    "scorp_passive_loss", "se_health", "second_mort_bal",
    "second_mort_int", "sl_int_ded", "sstb_farm", "sstb_part",
    "sstb_scorp", "sstb_sole_prop", "state_ref", "tax_prep_exp", "tips",
    "tips1", "tips2", "tips_lh1", "tips_lh2", "trad_contr_er1",
    "trad_contr_er2", "trad_contr_ira", "tuition_ded", "txbl_ira_dist",
    "value.annuities", "value.bonds", "value.cash", "value.credit_cards",
    "value.credit_lines", "value.db", "value.dc", "value.equities",
    "value.installment_debt", "value.life_ins", "value.other_debt",
    "value.other_fin", "value.other_home", "value.other_mortgage",
    "value.other_nonfin", "value.pass_throughs", "value.primary_home",
    "value.primary_mortgage", "value.re_fund", "value.trusts",
    "wagebill_farm", "wagebill_part", "wagebill_scorp",
    "wagebill_sole_prop",
]


def read_pin():
    """
    Return dictionary containing the ts_pin.json contents.
    """
    with open(PIN_FILE, "r", encoding="utf-8") as pfile:
        return json.load(pfile)


def ts_folder(pin, tsdir):
    """
    Return Path of the tax-simulator-gpu clone: TSDIR if not None, else
    the TBLY_TS_DIR environment variable if set, else the default folder
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
    Make a shallow clone of the pinned tax-simulator-gpu commit in folder
    TSDIR if it does not exist, and raise RuntimeError if TSDIR is not
    an unmodified clone at the pinned commit.
    """
    sha = pin["tax_simulator_sha"]
    if not tsdir.exists():
        sys.stderr.write(
            f"cloning tax-simulator-gpu {sha[:12]} into {tsdir}\n"
        )
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


def uv_path(uv):
    """
    Return path of the uv executable: UV if not None, else the
    TBLY_TS_UV environment variable if set, else the uv on PATH.
    """
    if uv is None:
        uv = os.environ.get("TBLY_TS_UV")
    if uv is None:
        uv = shutil.which("uv")
        if uv is None:
            raise RuntimeError("uv is not on PATH; use --uv or TBLY_TS_UV")
    uv = Path(uv).expanduser()
    if not uv.is_file():
        raise RuntimeError(f"uv {uv} does not exist; see README.md")
    return uv


def sync_ts_environment(uv, tsdir):
    """
    Create or update the tax-simulator-gpu environment in folder TSDIR
    so that it contains exactly the package versions in its uv.lock file
    (without the development packages), and return the uv version.
    """
    subprocess.run(
        [str(uv), "sync", "--locked", "--no-dev", "--quiet"],
        cwd=tsdir,
        check=True,
    )
    return subprocess.run(
        [str(uv), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def check_sample(smpl, year):
    """
    Raise ValueError if TAXSIM input sample SMPL for YEAR cannot be
    translated into tax-simulator-gpu tax units.
    """
    errors = []

    def require(condition, msg):
        if not condition:
            errors.append(msg)

    require((smpl.year == year).all(), f"year not always {year}")
    require((smpl.state == 0).all(), "state not always zero")
    require(smpl.mstat.isin([1, 2, 6]).all(), "mstat not always 1, 2, or 6")
    require(smpl.depx.between(0, 3).all(), "depx not in [0,3]")
    require(not ((smpl.mstat == 6) & (smpl.depx > 0)).any(),
            "mstat 6 with dependents")
    for var in MUST_BE_ZERO:
        require((smpl[var] == 0).all(),
                f"nonzero values of untranslated {var}")
    for var in ["sage", "swages", "ssemp", "sbusinc", "sui"]:
        require((smpl.loc[smpl.mstat != 2, var] == 0).all(),
                f"nonzero {var} for non-joint unit")
    require(not smpl.isna().any().any(), "missing values in sample")
    if errors:
        raise ValueError("TAXSIM input check failed: " + "; ".join(errors))


def ts_records(smpl):
    """
    Return DataFrame of the tax-simulator-gpu tax units that correspond
    to the TAXSIM input sample SMPL (see VARIABLES.md).
    """
    joint = smpl.mstat.to_numpy() == 2
    depx = smpl.depx.to_numpy()
    # dependent ages, youngest first, NaN for absent dependents
    ages = smpl[["age1", "age2", "age3"]].to_numpy(dtype=np.float64)
    ages[np.arange(3)[np.newaxis, :] >= depx[:, np.newaxis]] = np.nan
    ages = np.sort(ages, axis=1)  # np.sort puts NaN last
    present = ~np.isnan(ages)
    recs = pd.DataFrame({
        "id": smpl.taxsimid.to_numpy(),
        "filing_status": np.select(
            [joint, smpl.mstat.to_numpy() == 6, depx > 0], [2, 3, 4], 1
        ),
        "weight": 1.0,
        "filer": 1,
        "dep_status": 0,
        "age1": smpl.page.to_numpy(dtype=np.float64),
        "age2": np.where(joint, smpl.sage, np.nan),
        "blind1": 0.0,
        "blind2": np.where(joint, 0.0, np.nan),
        "n_dep": depx,
    })
    for idx in range(3):
        num = idx + 1
        recs[f"dep_age{num}"] = ages[:, idx]
        recs[f"dep_ctc{num}"] = np.where(present[:, idx], 1.0, np.nan)
        recs[f"dep_ssn{num}"] = recs[f"dep_ctc{num}"]
    recs["n_dep_eitc"] = (present & (np.nan_to_num(ages) < 19)).sum(axis=1)
    recs["wages1"] = smpl.pwages.to_numpy()
    recs["wages2"] = smpl.swages.to_numpy()
    recs["wages"] = recs.wages1 + recs.wages2
    recs["sole_prop1"] = (smpl.psemp + smpl.pbusinc).to_numpy()
    recs["sole_prop2"] = (smpl.ssemp + smpl.sbusinc).to_numpy()
    recs["sole_prop"] = recs.sole_prop1 + recs.sole_prop2
    recs["scorp_active"] = smpl.scorp.to_numpy()
    recs["rent"] = smpl.otherprop.to_numpy()
    recs["div_pref"] = smpl.dividends.to_numpy()
    recs["div_ord"] = 0.0
    recs["txbl_int"] = smpl.intrec.to_numpy()
    recs["kg_st"] = smpl.stcg.to_numpy()
    recs["kg_lt"] = smpl.ltcg.to_numpy()
    recs["txbl_pens_dist"] = smpl.pensions.to_numpy()
    recs["gross_pens_dist"] = smpl.pensions.to_numpy()
    recs["gross_ss"] = smpl.gssi.to_numpy()
    recs["ui"] = (smpl.pui + smpl.sui).to_numpy()
    recs["salt_prop"] = smpl.proptax.to_numpy()
    # fully deductible, outside the SALT cap, no AMT add-back
    recs["other_item_exp"] = (smpl.mortgage + smpl.otheritem).to_numpy()
    recs["care_exp"] = smpl.childcare.to_numpy()
    zeros = pd.DataFrame(0.0, index=recs.index, columns=ZERO_COLUMNS)
    return pd.concat([recs, zeros], axis=1)


def taxsim_output(res, recs):
    """
    Return DataFrame of TAXSIM output computed from tax-simulator-gpu
    results RES for tax units RECS (see VARIABLES.md).
    """
    return pd.DataFrame({
        "taxsimid": res.id,
        "year": 0,  # set by caller
        "fiitax": res.liab_iit_net,
        "fica": res.liab_pr,
        "tfica": res.liab_pr - res.liab_fica_er1 - res.liab_fica_er2,
        "addmed": res.liab_add_med,
        "v44": res.hi_ee_rate * recs.wages + res.liab_add_med,
        "v10": res.agi,
        "v11": recs.ui,
        "v12": res.txbl_ss,
        "v13": res.std_ded,
        "v14": res.pe_ded,
        "v17": res.item_ded,
        "qbid": res.qbi_ded,
        "v18": res.txbl_inc,
        "v19": res.liab_ord,
        "v28": res.liab,
        "v26": res.amt_gross_inc,
        "v27": res.liab_amt,
        "niit": res.liab_niit,
        "v22": res.ctc_nonref,
        "actc": res.ctc_ref,
        "v24": res.cdctc_nonref + res.cdctc_ref,
        "v25": res.eitc,
        "cares": res.rebate,
    })


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


def check_manifest(manifest, year, sha):
    """
    Raise ValueError if the batch command MANIFEST is inconsistent with
    the YEAR and the pinned tax-simulator-gpu commit SHA.
    """
    errors = []
    if manifest["law_year"] != year:
        errors.append("law year differs from sample year")
    if manifest["commit"] != sha:
        errors.append("commit differs from pinned commit")
    if manifest["alternative"] is not None:
        errors.append("law is not the default law")
    if manifest["draw_seed"] != "all draws zero":
        errors.append("random draws are not zero")
    if manifest["columns_supplied_not_read"]:
        errors.append("columns supplied but not read: "
                      + " ".join(manifest["columns_supplied_not_read"]))
    if errors:
        raise ValueError("batch manifest check failed: " + "; ".join(errors))


def sha256(path):
    """
    Return SHA-256 hex digest of the contents of file PATH.
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_one(letter, year, force, dirs, tools):
    """
    Run tax-simulator-gpu on the LETTER and YEAR sample in folder
    dirs["in"] and write the TS output and its stamp to folder
    dirs["out"], overwriting existing TS output only when FORCE is True,
    using the tax-simulator-gpu clone tools["tsdir"] and uv executable
    tools["uv"] (None means use the default; see ts_folder and uv_path).
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
    check_sample(smpl, year)
    recs = ts_records(smpl)
    pin = read_pin()
    sha = pin["tax_simulator_sha"]
    tsdir = ts_folder(pin, tools["tsdir"])
    ensure_ts_clone(pin, tsdir)
    uv = uv_path(tools["uv"])
    uv_version = sync_ts_environment(uv, tsdir)
    with tempfile.TemporaryDirectory() as tmpdir:
        recsfile = Path(tmpdir) / f"{lyy}.records.csv"
        resfile = Path(tmpdir) / f"{lyy}.taxes.csv"
        recs.to_csv(recsfile, index=False)
        cmd = [str(uv), "run", "--no-sync", "--quiet", "python", "-I"]
        cmd += [str(BATCH_SCRIPT), str(recsfile), str(year)]
        cmd += [str(resfile), sha]
        sys.stderr.write(f"running tax-simulator-gpu on {infile.name}\n")
        start = time.time()
        subprocess.run(cmd, cwd=tsdir, check=True, stdout=subprocess.DEVNULL)
        elapsed = time.time() - start
        res = pd.read_csv(resfile)
        with open(f"{resfile}.manifest.json", "r", encoding="utf-8") as mfile:
            manifest = json.load(mfile)
    check_manifest(manifest, year, sha)
    if not np.array_equal(res.id.to_numpy(), recs.id.to_numpy()):
        raise ValueError("TS result ids differ from input ids")
    out = taxsim_output(res, recs)
    out["year"] = smpl.year.to_numpy()
    check_output(out, smpl)
    outdir.mkdir(parents=True, exist_ok=True)
    # zero gzip mtime makes the file bytes depend only on the TS output
    csv = out.to_csv(index=False, float_format="%.10g", lineterminator="\n")
    outfile.write_bytes(gzip.compress(csv.encode("utf-8"), mtime=0))
    stamp = {
        "input_file": infile.name,
        "input_sha256": sha256(infile),
        "output_file": outfile.name,
        "output_sha256": sha256(outfile),
        "rows": len(out),
        "tax_simulator_sha": sha,
        "run_ts_py_sha256": sha256(Path(__file__).resolve()),
        "ts_batch_py_sha256": sha256(BATCH_SCRIPT),
        "uv": uv_version,
        "jax": manifest["jax"],
        "devices": manifest["devices"],
        "index_table": manifest["index_table"],
        "law_values_by_filing_status":
            manifest["law_values_by_filing_status"],
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
    # make the clone and the environment once before the concurrent
    # runs, so that they do not all try to make them
    sys.stderr.write("checking the tax-simulator-gpu clone and "
                     "environment\n")
    pin = read_pin()
    tsdir = ts_folder(pin, tools["tsdir"])
    ensure_ts_clone(pin, tsdir)
    uv = uv_path(tools["uv"])
    sync_ts_environment(uv, tsdir)
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
        cmd += ["--tsdir", str(tsdir), "--uv", str(uv)]
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
    Run tax-simulator-gpu on the sample(s) specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python run_ts.py",
        description=(
            "Runs the pinned tax-simulator-gpu on samples/LYY.in.csv.gz "
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
        help=("tax-simulator-gpu clone folder (default is $TBLY_TS_DIR "
              "if set, else the folder named in ts_pin.json)"),
    )
    parser.add_argument(
        "--uv",
        default=None,
        help=("uv executable (default is $TBLY_TS_UV if set, else the "
              "uv on PATH)"),
    )
    args = parser.parse_args()
    dirs = {"in": args.indir, "out": args.outdir}
    tools = {"tsdir": args.tsdir, "uv": args.uv}
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
