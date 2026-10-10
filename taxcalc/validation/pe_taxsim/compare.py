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
The comparison passes when the actual differences are exactly the same
as those in expected_differences/LYY-taxdiffs-expect.csv, or when there
are no actual differences and no expected-differences file.  The exit
code is 0 when the comparison passes, 1 when it fails, and 2 on error.
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


def unexpected_differences(actual, expectfile):
    """
    Return DataFrame of the rows that are in only one of the ACTUAL
    differences and the EXPECTFILE differences (an empty DataFrame
    means they match exactly), with a "where" column saying which.
    A missing EXPECTFILE means that no differences are expected.
    """
    if expectfile.is_file():
        expect = pd.read_csv(expectfile)
        if list(expect.columns) != DIFF_COLUMNS:
            raise ValueError(f"{expectfile} does not have columns "
                             f"{DIFF_COLUMNS}")
    else:
        expect = pd.DataFrame(columns=DIFF_COLUMNS)
    # compare the values as they are written to the CSV files
    act = actual.astype({"taxsimid": int, "variable": str})
    exp = expect.astype({"taxsimid": int, "variable": str})
    for col in ["pe", "tc", "diff"]:
        act[col] = act[col].map(lambda x: f"{x:.2f}")
        exp[col] = exp[col].astype(float).map(lambda x: f"{x:.2f}")
    both = act.merge(exp, how="outer", on=DIFF_COLUMNS, indicator="where")
    both = both[both["where"] != "both"].reset_index(drop=True)
    both["where"] = both["where"].map(
        {"left_only": "actual_only", "right_only": "expect_only"}
    )
    return both


def report(lyy, summary, unexpected, tolerance, expectfile):
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
    if not expectfile.is_file():
        print(f"{lyy}: no {expectfile.name} file, so no differences "
              "are expected")
    if unexpected.empty:
        print(f"{lyy}: PASS")
    else:
        counts = unexpected["where"].value_counts()
        num_actual_only = counts.get("actual_only", 0)
        num_expect_only = counts.get("expect_only", 0)
        print(f"{lyy}: FAIL: {num_actual_only} actual "
              f"differences are not expected and "
              f"{num_expect_only} expected differences "
              "did not occur")


def compare(lyy, year, tolerance, dirs):
    """
    Compare the PE and Tax-Calculator outputs for sample LYY in YEAR,
    write the actual-differences files, print a report, and return
    True if the comparison passes.  DIRS is a dictionary with the
    "pe", "work", and "expect" folders.
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
    expectfile = dirs["expect"] / f"{lyy}-taxdiffs-expect.csv"
    unexpected = unexpected_differences(diffs, expectfile)
    report(lyy, summary, unexpected, tolerance, expectfile)
    return unexpected.empty


def main():
    """
    Compare the outputs for the sample specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python compare.py",
        description=(
            "Compares pe_output/LYY.out-pe.csv.gz with work/LYY.out-tc.csv "
            "and checks the differences against "
            "expected_differences/LYY-taxdiffs-expect.csv."
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
    parser.add_argument(
        "--expectdir",
        default=str(HERE / "expected_differences"),
        help=("expected-differences folder (default is "
              "expected_differences next to this script)"),
    )
    args = parser.parse_args()
    if args.tolerance < 0:
        sys.stderr.write("ERROR: --tolerance must be non-negative\n")
        return 2
    lyy = f"{args.LETTER}{args.YEAR % 100:02d}"
    try:
        passed = compare(
            lyy, args.YEAR, args.tolerance,
            {
                "pe": Path(args.pedir).resolve(),
                "work": Path(args.workdir).resolve(),
                "expect": Path(args.expectdir).resolve(),
            },
        )
    except (FileNotFoundError, ValueError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 2
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
