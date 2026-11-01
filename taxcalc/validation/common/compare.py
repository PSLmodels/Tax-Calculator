"""
Compares the other model's and Tax-Calculator's TAXSIM-format output
(step 5 of the validation).

USAGE: python compare.py LETTER YEAR --workflow WORKFLOW [--tolerance T]

in the validation/WORKFLOW folder, reads M_output/LYY.out-M.csv.gz
(written by run_M.py, where M is the other model's label: pe for
pe_taxsim, ts for tbly_ts) and work/LYY.out-tc.csv (written by
run_tc.py), and writes these files to work/differences/:
  LYY-taxdiffs.csv          one row (taxsimid, variable, M, tc, diff)
                            for each compared value whose absolute
                            difference, diff = tc - M, exceeds T
                            (default $1)
  LYY-taxdiffs-summary.csv  for each compared variable, the number of
                            units compared, the number of differences,
                            and the maximum and mean absolute difference
and prints a summary of the differences.  The exit code is 0 on success
and 2 on error.
The compared variables follow the output table in
../pe_taxsim/VARIABLES.md.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
# pylint: disable-next=import-error
from workflows import add_sample_arguments, parse_sample_arguments

DEFAULT_TOLERANCE = 1.0

# compared TAXSIM output variables, in the order of the
# ../pe_taxsim/VARIABLES.md output table
COMPARED_VARIABLES = (
    ["fiitax", "fica", "tfica", "addmed", "v44"]
    + ["v10", "v11", "v12", "v13", "v14", "v17", "qbid", "v18"]
    + ["v19", "v28", "v26", "v27", "niit"]
    + ["v22", "actc", "v24", "v25", "cares"]
)
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
        # TC c05200 matches the other model only without preferential
        # income
        return (tco.tc_dwks10 == 0).to_numpy()
    return np.ones(len(tco), dtype=bool)


def check_inputs(mdo, tco, year, model):
    """
    Raise ValueError if output MDO of the other MODEL and Tax-Calculator
    output TCO cannot be compared for YEAR.
    """
    errors = []
    mname = model.upper()
    for name, odf in ((mname, mdo), ("TC", tco)):
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
    if len(mdo) != len(tco):
        errors.append(f"{mname} and TC outputs have different row counts")
    elif not np.array_equal(mdo.taxsimid.to_numpy(),
                            tco.taxsimid.to_numpy()):
        errors.append(
            f"{mname} and TC outputs have different taxsimid values"
        )
    if errors:
        raise ValueError("; ".join(errors))


def differences(mdo, tco, tolerance, model):
    """
    Return (diffs, summary) DataFrames comparing output MDO of the
    other MODEL with Tax-Calculator output TCO, where diffs contains the
    compared values whose absolute difference exceeds TOLERANCE.
    """
    diff_parts = []
    summary_rows = []
    for var in COMPARED_VARIABLES:
        compared = compared_units(var, tco)
        mdv = mdo[var].to_numpy().round(2)
        tcv = tco[var].to_numpy().round(2)
        diff = (tcv - mdv).round(2)
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
            "taxsimid": mdo.taxsimid.to_numpy()[differ],
            "variable": var,
            model: mdv[differ],
            "tc": tcv[differ],
            "diff": diff[differ],
        }))
    diffs = pd.concat(diff_parts, ignore_index=True)[
        ["taxsimid", "variable", model, "tc", "diff"]
    ]
    summary = pd.DataFrame(summary_rows, columns=SUMMARY_COLUMNS)
    return diffs, summary


def report(lyy, summary, tolerance, model):
    """
    Print the comparison results for sample LYY.
    """
    nonzero = summary[summary["count"] > 0]
    num_diffs = summary["count"].sum()
    print(f"{lyy}: {num_diffs} differences "
          f"(|tc - {model}| > {tolerance:g}) in "
          f"{len(nonzero)} variables")
    if not nonzero.empty:
        print(nonzero.to_string(index=False))


def compare(lyy, year, tolerance, wfl, dirs):
    """
    Compare the other model's and Tax-Calculator's outputs for sample
    LYY in YEAR of Workflow WFL, write the differences files, and print
    a report.  DIRS is a dictionary with the "model" (other model's
    output) and "work" folders.
    """
    workdir = dirs["work"]
    model = wfl.model
    mdo = pd.read_csv(dirs["model"] / wfl.output_file(lyy))
    tco = pd.read_csv(workdir / f"{lyy}.out-tc.csv")
    check_inputs(mdo, tco, year, model)
    diffs, summary = differences(mdo, tco, tolerance, model)
    diffdir = workdir / "differences"
    diffdir.mkdir(exist_ok=True)
    diffs.to_csv(diffdir / f"{lyy}-taxdiffs.csv",
                 index=False, float_format="%.2f")
    summary.to_csv(diffdir / f"{lyy}-taxdiffs-summary.csv",
                   index=False, float_format="%.2f")
    report(lyy, summary, tolerance, model)


def main():
    """
    Compare the outputs for the sample specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python compare.py",
        description=(
            "Compares M_output/LYY.out-M.csv.gz with work/LYY.out-tc.csv "
            "and writes the differences to work/differences/ in the "
            "validation/WORKFLOW folder, where M is the other model's "
            "label (pe for pe_taxsim, ts for tbly_ts)."
        ),
    )
    add_sample_arguments(parser)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=("absolute differences larger than this are reported "
              f"(default {DEFAULT_TOLERANCE:g})"),
    )
    parser.add_argument(
        "--modeldir",
        help=("other model's output folder "
              "(default is validation/WORKFLOW/M_output)"),
    )
    parser.add_argument(
        "--workdir",
        help="working folder (default is validation/WORKFLOW/work)",
    )
    args, wfl, lyy = parse_sample_arguments(parser)
    if args.tolerance < 0:
        sys.stderr.write("ERROR: --tolerance must be non-negative\n")
        return 2
    modeldir = (Path(args.modeldir) if args.modeldir
                else wfl.folder / wfl.output_dir)
    workdir = Path(args.workdir) if args.workdir else wfl.folder / "work"
    try:
        compare(
            lyy, args.YEAR, args.tolerance, wfl,
            {"model": modeldir.resolve(), "work": workdir.resolve()},
        )
    except (FileNotFoundError, ValueError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
