"""
Compares policyengine-taxsim and Tax-Calculator TAXSIM-format output
(step 5 of the validation).

USAGE: python compare.py LETTER YEAR [--tolerance T]

reads pe_output/LYY.out-pe.csv.gz (written by run_pe.py) and
work/LYY.out-tc.csv (written by run_tc.py), and writes these files to
work/actual_differences/:
  LYY-taxdiffs-actual.csv   one row (taxsimid, variable, pe, tc, diff)
                            for each compared value whose absolute
                            difference, diff = tc - pe, exceeds T
                            (default $1)
  LYY-taxdiffs-summary.csv  for each compared variable, the number of
                            units compared, the number of differences,
                            and the maximum and mean absolute difference
and prints a summary of the differences.  The exit code is 0 on success
and 2 on error.
The compared variables follow the output table in VARIABLES.md.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2021
LAST_YEAR = 2025
DEFAULT_TOLERANCE = 1.0

# compared TAXSIM output variables, in the order of the VARIABLES.md
# output table
COMPARED_VARIABLES = (
    ["fiitax", "fica", "tfica", "addmed", "v44"]
    + ["v10", "v11", "v12", "v13", "v14", "v17", "qbid", "v18"]
    + ["v19", "v28", "v26", "v27", "niit"]
    + ["v22", "actc", "v24", "v25", "cares"]
)
DIFF_COLUMNS = ["taxsimid", "variable", "pe", "tc", "diff"]
SUMMARY_COLUMNS = ["variable", "compared", "count", "max_abs", "mean_abs"]


def compared_units(var, tco):
    """
    Return boolean array that is True for the units whose VAR value is
    compared, using Tax-Calculator TAXSIM-format output TCO.
    """
    if var == "v13":
        # TC zeroes standard for itemizers
        return (tco.v17 == 0).to_numpy()
    if var == "v17":
        # TC zeroes c04470 for non-itemizers
        return (tco.v13 == 0).to_numpy()
    if var == "v19":
        # TC c05200 matches PE only without preferential income
        return (tco.tc_dwks10 == 0).to_numpy()
    return np.ones(len(tco), dtype=bool)


def check_inputs(peo, tco, year):
    """
    Raise ValueError if PE output PEO and Tax-Calculator output TCO
    cannot be compared for YEAR.
    """
    errors = []
    for name, odf in (("PE", peo), ("TC", tco)):
        missing = [v for v in ["taxsimid", "year"] + COMPARED_VARIABLES
                   if v not in odf.columns]
        if missing:
            errors.append(f"{name} output lacks {missing}")
        elif odf[COMPARED_VARIABLES].isna().any().any():
            errors.append(f"{name} output has missing values")
        elif not (odf.year == year).all():
            errors.append(f"{name} output year is not always {year}")
    if "tc_dwks10" not in tco.columns:
        errors.append("TC output lacks tc_dwks10")
    if len(peo) != len(tco):
        errors.append("PE and TC outputs have different row counts")
    elif not np.array_equal(peo.taxsimid.to_numpy(),
                            tco.taxsimid.to_numpy()):
        errors.append("PE and TC outputs have different taxsimid values")
    if errors:
        raise ValueError("; ".join(errors))


def differences(peo, tco, tolerance):
    """
    Return (diffs, summary) DataFrames comparing PE output PEO with
    Tax-Calculator output TCO, where diffs contains the compared values
    whose absolute difference exceeds TOLERANCE.
    """
    diff_parts = []
    summary_rows = []
    for var in COMPARED_VARIABLES:
        compared = compared_units(var, tco)
        pev = peo[var].to_numpy().round(2)
        tcv = tco[var].to_numpy().round(2)
        diff = (tcv - pev).round(2)
        differ = compared & (np.abs(diff) > tolerance)
        absdiff = np.abs(diff[differ])
        summary_rows.append({
            "variable": var,
            "compared": int(compared.sum()),
            "count": int(differ.sum()),
            "max_abs": absdiff.max() if absdiff.size else 0.0,
            "mean_abs": absdiff.mean().round(2) if absdiff.size else 0.0,
        })
        diff_parts.append(pd.DataFrame({
            "taxsimid": peo.taxsimid.to_numpy()[differ],
            "variable": var,
            "pe": pev[differ],
            "tc": tcv[differ],
            "diff": diff[differ],
        }))
    diffs = pd.concat(diff_parts, ignore_index=True)[DIFF_COLUMNS]
    summary = pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS)
    return diffs, summary


def report(lyy, summary, tolerance):
    """
    Print the comparison results for sample LYY.
    """
    nonzero = summary[summary["count"] > 0]
    num_diffs = summary["count"].sum()
    print(f"{lyy}: {num_diffs} differences "
          f"(|tc - pe| > {tolerance:g}) in "
          f"{len(nonzero)} variables")
    if not nonzero.empty:
        print(nonzero.to_string(index=False))


def compare(lyy, year, tolerance, dirs):
    """
    Compare the PE and Tax-Calculator outputs for sample LYY in YEAR,
    write the actual-differences files, and print a report.  DIRS is a
    dictionary with the "pe" and "work" folders.
    """
    workdir = dirs["work"]
    peo = pd.read_csv(dirs["pe"] / f"{lyy}.out-pe.csv.gz")
    tco = pd.read_csv(workdir / f"{lyy}.out-tc.csv")
    check_inputs(peo, tco, year)
    diffs, summary = differences(peo, tco, tolerance)
    actdir = workdir / "actual_differences"
    actdir.mkdir(exist_ok=True)
    diffs.to_csv(actdir / f"{lyy}-taxdiffs-actual.csv",
                 index=False, float_format="%.2f")
    summary.to_csv(actdir / f"{lyy}-taxdiffs-summary.csv",
                   index=False, float_format="%.2f")
    report(lyy, summary, tolerance)


def main():
    """
    Compare the outputs for the sample specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python compare.py",
        description=(
            "Compares pe_output/LYY.out-pe.csv.gz with work/LYY.out-tc.csv "
            "and writes the differences to work/actual_differences/."
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
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=("absolute differences larger than this are reported "
              f"(default {DEFAULT_TOLERANCE:g})"),
    )
    parser.add_argument(
        "--pedir",
        default=str(HERE / "pe_output"),
        help="PE output folder (default is pe_output next to this script)",
    )
    parser.add_argument(
        "--workdir",
        default=str(HERE / "work"),
        help="working folder (default is work next to this script)",
    )
    args = parser.parse_args()
    if args.tolerance < 0:
        sys.stderr.write("ERROR: --tolerance must be non-negative\n")
        return 2
    lyy = f"{args.LETTER}{args.YEAR % 100:02d}"
    try:
        compare(
            lyy, args.YEAR, args.tolerance,
            {
                "pe": Path(args.pedir).resolve(),
                "work": Path(args.workdir).resolve(),
            },
        )
    except (FileNotFoundError, ValueError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
