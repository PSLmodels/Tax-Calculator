"""
Runs the Tax-Calculator CLI on a translated sample and converts its
output into TAXSIM format (step 4 of the validation).

USAGE: python run_tc.py LETTER YEAR

reads work/LYY.in-tc.csv (written by taxsim_to_tc.py) and writes
work/LYY.dumpdb and work/LYY.out-tc.csv in the folder containing this
script.  The CLI runs with the pe_emulation.json reform and the
dumpvars.txt variables, and the TAXSIM-format output follows the output
table in VARIABLES.md.

The CLI is run as "python -m taxcalc.cli.tc" with the top-level folder
of this repository first on PYTHONPATH, so the working-tree
Tax-Calculator code is the code being validated.  Because the input
file is neither cps.csv nor tmd.csv, the CLI does not age the input
data (no growfactors are applied) and uses no weights.
"""

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT))
# pylint: disable=wrong-import-position,import-error
from taxcalc import Policy  # noqa: E402


VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2021
LAST_YEAR = 2025
EMULATION_FILE = HERE / "pe_emulation.json"
DUMPVARS_FILE = HERE / "dumpvars.txt"

# TAXSIM-format output columns written by this script: the federal
# policyengine-taxsim idtl=2 columns compared in step 5 (see
# VARIABLES.md), plus tc_dwks10, which step 5 needs to decide whether
# v19 is compared
OUTPUT_COLUMNS = (
    ["taxsimid", "year", "fiitax", "fica", "tfica", "addmed", "v44"]
    + ["v10", "v11", "v12", "v13", "v14", "v17", "qbid", "v18"]
    + ["v19", "v28", "v26", "v27", "niit"]
    + ["v22", "actc", "v24", "v25", "cares"]
    + ["tc_dwks10"]
)


def run_cli(lyy, year, workdir):
    """
    Run the Tax-Calculator CLI on workdir/LYY.in-tc.csv for YEAR and
    return the path of the --dumpdb output, renamed to workdir/LYY.dumpdb.
    """
    infile = workdir / f"{lyy}.in-tc.csv"
    if not infile.is_file():
        raise FileNotFoundError(f"input file {infile} does not exist; "
                                "run taxsim_to_tc.py first")
    # the CLI names its dumpdb output using the input file stem, the
    # two-digit tax year, and the reform file stem
    yy = f"{year % 100:02d}"
    cli_dumpdb = (
        workdir / f"{infile.stem}-{yy}-#-{EMULATION_FILE.stem}-#-#.dumpdb"
    )
    dumpdb = workdir / f"{lyy}.dumpdb"
    for path in (cli_dumpdb, dumpdb):
        path.unlink(missing_ok=True)
    cmd = [
        sys.executable, "-m", "taxcalc.cli.tc",
        infile.name, str(year),
        "--reform", str(EMULATION_FILE),
        "--dumpdb", "--dumpvars", str(DUMPVARS_FILE),
        "--silent",
    ]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO_ROOT)] + [p for p in [env.get("PYTHONPATH")] if p]
    )
    env.pop("TMD_AREA", None)
    proc = subprocess.run(
        cmd, cwd=workdir, env=env, capture_output=True, text=True,
        check=False,
    )
    if proc.returncode != 0 or not cli_dumpdb.is_file():
        sys.stderr.write(proc.stdout + proc.stderr)
        raise RuntimeError(f"Tax-Calculator CLI failed on {infile}")
    cli_dumpdb.rename(dumpdb)
    return dumpdb


def read_dumpdb(dumpdb):
    """
    Return DataFrame containing the reform table in the DUMPDB database,
    which holds the results under current-law policy plus the
    pe_emulation.json reform.
    """
    with sqlite3.connect(dumpdb) as dbcon:
        return pd.read_sql_query("SELECT * FROM reform", dbcon)


def fica_mc_trt_employee(year):
    """
    Return the employee HI payroll tax rate for YEAR under current-law
    policy plus the pe_emulation.json reform.
    """
    pol = Policy()
    pol.implement_reform(Policy.read_json_reform(str(EMULATION_FILE)))
    pol.set_year(year)
    return pol.FICA_mc_trt_employee[0]


def taxsim_output(tcv, year):
    """
    Return DataFrame of TAXSIM-format output computed from DataFrame TCV
    of Tax-Calculator dump variables for YEAR (see VARIABLES.md).
    """
    out = pd.DataFrame({
        "taxsimid": tcv.RECID,
        "year": tcv.FLPDYR,
        "fiitax": tcv.iitax,
        "fica": tcv.payrolltax,
        "tfica": tcv.payrolltax - tcv.ptax_er_p - tcv.ptax_er_s,
        "addmed": tcv.ptax_amc,
        "v44": fica_mc_trt_employee(year) * tcv.e00200 + tcv.ptax_amc,
        "v10": tcv.c00100,
        "v11": tcv.e02300,
        "v12": tcv.c02500,
        "v13": tcv.standard,
        "v14": tcv.c04600,
        "v17": tcv.c04470,
        "qbid": tcv.qbided,
        "v18": tcv.c04800,
        "v19": tcv.c05200,
        "v28": tcv.taxbc,
        "v26": tcv.c62100,
        "v27": tcv.c09600,
        "niit": tcv.niit,
        "v24": tcv.c07180 + tcv.CDCC_refund,
        "v25": tcv.eitc,
        "cares": tcv.recovery_rebate_credit,
        "tc_dwks10": tcv.dwks10,
    })
    if year == 2021:
        # ARPA made the whole child tax credit refundable; TC models the
        # increase as ctc_new and leaves c11070 at zero
        out["v22"] = tcv.c07220 + tcv.odc + tcv.ctc_new
        out["actc"] = tcv.c07220 + tcv.ctc_new
    else:
        out["v22"] = tcv.c07220 + tcv.odc
        out["actc"] = tcv.c11070
    return out[OUTPUT_COLUMNS].round(2)


def check_output(out, tcin, year):
    """
    Raise ValueError if TAXSIM-format output OUT is inconsistent with
    Tax-Calculator input TCIN for YEAR.
    """
    errors = []
    if list(out.columns) != OUTPUT_COLUMNS:
        errors.append("unexpected columns")
    if len(out) != len(tcin):
        errors.append("row count differs from input")
    elif not np.array_equal(out.taxsimid.to_numpy(), tcin.RECID.to_numpy()):
        errors.append("taxsimid values differ from input RECID")
    if not (out.year == year).all():
        errors.append(f"year not always {year}")
    if out.isna().any().any():
        errors.append("missing values")
    if errors:
        raise ValueError("TAXSIM-format output check failed: "
                         + "; ".join(errors))


def main():
    """
    Run the CLI and convert its output for the sample specified on the
    command line.
    """
    parser = argparse.ArgumentParser(
        prog="python run_tc.py",
        description=(
            "Runs the Tax-Calculator CLI on work/LYY.in-tc.csv and writes "
            "TAXSIM-format output to work/LYY.out-tc.csv."
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
        "--workdir",
        default=str(HERE / "work"),
        help="working folder (default is work next to this script)",
    )
    args = parser.parse_args()
    lyy = f"{args.LETTER}{args.YEAR % 100:02d}"
    workdir = Path(args.workdir).resolve()
    try:
        dumpdb = run_cli(lyy, args.YEAR, workdir)
    except (FileNotFoundError, RuntimeError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 1
    out = taxsim_output(read_dumpdb(dumpdb), args.YEAR)
    check_output(out, pd.read_csv(workdir / f"{lyy}.in-tc.csv"), args.YEAR)
    out.to_csv(workdir / f"{lyy}.out-tc.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
