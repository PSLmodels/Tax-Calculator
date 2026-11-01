"""
Builds the Tax-Simulator price and wage index file ts_indexes.csv from
public data.

USAGE: python build_indexes.py DATADIR [--shift S] [--output FILE]

DATADIR must contain the FRED monthly series CPIAUCNS.csv (CPI-U, not
seasonally adjusted) and SUUR0000SA0.csv (chained CPI-U), downloaded
from https://fred.stlouisfed.org.  The output file has the columns
series (cpi, chained_cpi, awi), year, and growth, which is the form of
the Tax-Simulator indexes tibble.

The cpi and chained_cpi value for year t is the average of the monthly
index over the twelve months ending in August of year t + S (the IRS
definition in IRC section 1(f)(4) when S is zero, the default).  The
awi value for year t is the SSA national average wage index for year
t + S.  Tax-Simulator needs the cpi series to start no later than 1986.
"""

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# SSA national average wage index (https://www.ssa.gov/oact/cola/AWI.html),
# entered by hand and verified against the 2023-2026 OASDI wage bases
AWI = {
    2020: 55628.60,
    2021: 60575.07,
    2022: 63795.13,
    2023: 66621.80,
    2024: 69846.57,
}
CPI_FILES = {"cpi": "CPIAUCNS.csv", "chained_cpi": "SUUR0000SA0.csv"}


def monthly(path):
    """
    Return dictionary mapping (year, month) to the index value in the
    FRED csv file PATH.
    """
    vals = {}
    with open(path, "r", encoding="utf-8") as cfile:
        for row in csv.DictReader(cfile):
            year, month, _ = row["observation_date"].split("-")
            value = list(row.values())[1]
            if value:
                vals[(int(year), int(month))] = float(value)
    return vals


def sep_aug_average(vals, year):
    """
    Return the average of monthly VALS from September of YEAR-1 through
    August of YEAR, or None if any of those months is missing.
    """
    months = [(year - 1, m) for m in range(9, 13)]
    months += [(year, m) for m in range(1, 9)]
    if not all(key in vals for key in months):
        return None
    return sum(vals[key] for key in months) / 12


def growth_rows(series, level):
    """
    Return list of (SERIES, year, growth) tuples computed from the
    dictionary LEVEL that maps year to index level.
    """
    return [
        (series, year, level[year] / level[year - 1] - 1)
        for year in sorted(level)
        if year - 1 in level
    ]


def main():
    """
    Build and write the index file specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python build_indexes.py",
        description=(
            "Builds the Tax-Simulator index file ts_indexes.csv from "
            "FRED CPI-U and chained CPI-U data and SSA AWI values."
        ),
    )
    parser.add_argument(
        "DATADIR", help="folder containing the FRED csv files"
    )
    parser.add_argument(
        "--shift",
        type=int,
        default=0,
        help="year shift S (default is 0, the IRS definition)",
    )
    parser.add_argument(
        "--output",
        default=str(HERE / "ts_indexes.csv"),
        help="output file (default is ts_indexes.csv next to this script)",
    )
    args = parser.parse_args()
    datadir = Path(args.DATADIR)
    rows = []
    for series, fname in CPI_FILES.items():
        path = datadir / fname
        if not path.is_file():
            sys.stderr.write(f"ERROR: {path} does not exist\n")
            return 1
        vals = monthly(path)
        level = {}
        for year in range(1950, 2030):
            avg = sep_aug_average(vals, year + args.shift)
            if avg is not None:
                level[year] = avg
        rows += growth_rows(series, level)
    awi = {
        year: AWI[year + args.shift]
        for year in range(2015, 2030)
        if year + args.shift in AWI
    }
    rows += growth_rows("awi", awi)
    with open(args.output, "w", encoding="utf-8", newline="") as ofile:
        writer = csv.writer(ofile)
        writer.writerow(["series", "year", "growth"])
        for series, year, growth in rows:
            writer.writerow([series, year, f"{growth:.10f}"])
    sys.stderr.write(f"wrote {len(rows)} rows to {args.output}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
