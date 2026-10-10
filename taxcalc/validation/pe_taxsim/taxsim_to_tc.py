"""
Translates a TAXSIM-35 input sample into a Tax-Calculator CLI input
file (step 3 of the validation).

USAGE: python taxsim_to_tc.py LETTER YEAR

reads samples/LYY.in.csv.gz and writes work/LYY.in-tc.csv in the folder
containing this script.  The translation follows the input tables in
VARIABLES.md.
"""

import argparse
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd


VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2021
LAST_YEAR = 2025
MAX_DEPX = 5
HERE = Path(__file__).resolve().parent
RECORDS_VARIABLES = HERE.parents[1] / "records_variables.json"

# TAXSIM input variables that are copied unchanged (see VARIABLES.md)
COPY_MAP = {
    "taxsimid": "RECID",
    "year": "FLPDYR",
    "page": "age_head",
    "pwages": "e00200p",
    "swages": "e00200s",
    "scorp": "e26270",
    "intrec": "e00300",
    "stcg": "p22250",
    "ltcg": "p23250",
    "gssi": "e02400",
    "proptax": "e18500",
    "childcare": "e32800",
}

# Tax-Calculator input variables set to zero for every filing unit;
# all other unwritten input variables also default to zero, but these
# are written to make the VARIABLES.md assumptions explicit
ZERO_VARS = [
    "DSI", "blind_head", "blind_spouse", "PT_SSTB_income",
    "k1bx14p", "k1bx14s", "e18400",
]

# TAXSIM input variables that must be zero in every sample row because
# they have no Tax-Calculator translation (see VARIABLES.md)
MUST_BE_ZERO = ["nonprop", "transfers", "rentpaid", "pprofinc", "sprofinc"]

# Tax-Calculator input variables in output-file column order
TC_COLUMNS = (
    ["RECID", "FLPDYR", "MARS", "XTOT", "age_head", "age_spouse"]
    + ["nu06", "nu13", "nu18", "n24", "f2441", "EIC", "elderly_dependents"]
    + ["e00200p", "e00200s", "e00200", "e00900p", "e00900s", "e00900"]
    + ["e26270", "e02000", "e00600", "e00650", "e00300"]
    + ["p22250", "p23250", "e01500", "e01700", "e02400", "e02300"]
    + ["e18500", "e19200", "e32800"]
    + ZERO_VARS
)

# Tax-Calculator input variables that are integers
INT_COLUMNS = TC_COLUMNS[:TC_COLUMNS.index("e00200p")] + [
    "DSI", "blind_head", "blind_spouse", "PT_SSTB_income",
]


def translate(smpl):
    """
    Return DataFrame of Tax-Calculator input variables translated from
    the TAXSIM-35 input variables in DataFrame SMPL.
    """
    bad = [var for var in MUST_BE_ZERO if (smpl[var] != 0).any()]
    if bad:
        raise ValueError(f"nonzero values of untranslated {bad}")
    if not smpl.mstat.isin([1, 2]).all():
        raise ValueError("mstat not always 1 or 2")
    joint = (smpl.mstat == 2).to_numpy()
    depx = smpl.depx.to_numpy()
    tc = pd.DataFrame(
        {tcvar: smpl[tsvar].to_numpy() for tsvar, tcvar in COPY_MAP.items()}
    )
    # filing status, exemptions, and spouse age
    tc["MARS"] = np.where(joint, 2, np.where(depx > 0, 4, 1))
    tc["XTOT"] = depx + np.where(joint, 2, 1)
    tc["age_spouse"] = np.where(joint, smpl.sage, 0)
    # dependent counts from the ages of the depx dependents
    ages = smpl[[f"age{num}" for num in range(1, MAX_DEPX + 1)]].to_numpy()
    used = np.arange(MAX_DEPX)[np.newaxis, :] < depx[:, np.newaxis]

    def count(condition):
        return (used & condition).sum(axis=1)

    tc["nu06"] = count(ages < 6)
    tc["nu13"] = count(ages < 13)
    tc["f2441"] = tc["nu13"]
    tc["n24"] = count(ages < 17)
    # nu18 counts every person under 18 in the filing unit
    tc["nu18"] = (
        count(ages < 18)
        + (smpl.page < 18).astype(int)
        + (joint & (smpl.sage < 18)).astype(int)
    )
    tc["EIC"] = np.minimum(count(ages < 19), 3)
    tc["elderly_dependents"] = count(ages >= 65)
    # income
    tc["e00200"] = tc.e00200p + tc.e00200s
    tc["e00900p"] = smpl.psemp + smpl.pbusinc
    tc["e00900s"] = smpl.ssemp + smpl.sbusinc
    tc["e00900"] = tc.e00900p + tc.e00900s
    # otherprop is not QBI in PE, so it is not written to e27200 (D1)
    tc["e02000"] = smpl.otherprop + smpl.scorp
    tc["e00600"] = smpl.dividends
    tc["e00650"] = smpl.dividends
    tc["e01500"] = smpl.pensions
    tc["e01700"] = smpl.pensions
    tc["e02300"] = smpl.pui + smpl.sui
    # PE sums mortgage and otheritem into fully deductible interest
    tc["e19200"] = smpl.mortgage + smpl.otheritem
    for var in ZERO_VARS:
        tc[var] = 0
    tc = tc[TC_COLUMNS]
    return tc.astype({var: int for var in INT_COLUMNS})


def check_tc_input(tc, smpl):
    """
    Raise ValueError if Tax-Calculator input TC is invalid or
    inconsistent with TAXSIM-35 input sample SMPL.
    """
    errors = []

    def require(condition, msg):
        if not condition:
            errors.append(msg)

    with open(RECORDS_VARIABLES, "r", encoding="utf-8") as vfile:
        read_vars = json.load(vfile)["read"]
    unknown = sorted(set(tc.columns) - set(read_vars))
    require(not unknown, f"unknown Tax-Calculator variables {unknown}")
    require(list(tc.columns) == TC_COLUMNS, "unexpected columns")
    require(len(tc) == len(smpl), "row count differs from input")
    require(not tc.isna().any().any(), "missing values")
    require(tc.RECID.is_unique, "RECID values not unique")
    require(
        np.array_equal(tc.RECID.to_numpy(), smpl.taxsimid.to_numpy()),
        "RECID values differ from taxsimid",
    )
    require(tc.MARS.isin([1, 2, 4]).all(), "MARS not always 1, 2, or 4")
    require(
        np.array_equal(tc.MARS == 2, smpl.mstat == 2),
        "MARS inconsistent with mstat",
    )
    require(
        ((tc.MARS == 4) == ((smpl.mstat == 1) & (smpl.depx > 0))).all(),
        "MARS inconsistent with depx",
    )
    require(
        (tc.XTOT == smpl.depx + np.where(tc.MARS == 2, 2, 1)).all(),
        "XTOT inconsistent with MARS and depx",
    )
    require(
        np.allclose(tc.e00200, tc.e00200p + tc.e00200s),
        "e00200 != e00200p + e00200s",
    )
    require(
        np.allclose(tc.e00900, tc.e00900p + tc.e00900s),
        "e00900 != e00900p + e00900s",
    )
    nospouse = tc.MARS != 2
    spouse_vars = ["age_spouse", "e00200s", "e00900s"]
    require(
        (tc.loc[nospouse, spouse_vars] == 0).all().all(),
        "nonzero spouse variable for unmarried filing unit",
    )
    # nu18 can exceed nu13 only by dependents aged 13-17 plus a head or
    # spouse under 18; the dependent counts are nested by age
    adults_u18 = (tc.age_head < 18).astype(int) + (
        (tc.MARS == 2) & (tc.age_spouse < 18)
    ).astype(int)
    require(
        ((tc.nu06 <= tc.nu13) & (tc.nu13 <= tc.nu18 - adults_u18)).all(),
        "child counts not nested: nu06 <= nu13 <= nu18",
    )
    require(
        ((tc.nu13 <= tc.n24) & (tc.n24 <= tc.nu18 - adults_u18)).all(),
        "n24 not between nu13 and dependent part of nu18",
    )
    require((tc.f2441 == tc.nu13).all(), "f2441 != nu13")
    require(tc.EIC.between(0, 3).all(), "EIC not in [0,3] range")
    dep_counts = ["nu06", "nu13", "n24", "f2441", "EIC", "elderly_dependents"]
    require(
        (tc[dep_counts].le(smpl.depx, axis=0)).all().all(),
        "dependent count exceeds depx",
    )
    require(
        ((tc.e00600 >= tc.e00650) & (tc.e01500 >= tc.e01700)).all(),
        "e00600 < e00650 or e01500 < e01700",
    )
    require(
        (tc.e02000 >= tc.e26270).all(), "e02000 does not include e26270"
    )
    if errors:
        raise ValueError("Tax-Calculator input check failed: "
                         + "; ".join(errors))


def main():
    """
    Translate, check, and write the sample specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python taxsim_to_tc.py",
        description=(
            "Translates samples/LYY.in.csv.gz into the Tax-Calculator "
            "CLI input file work/LYY.in-tc.csv."
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
        "--indir",
        default=str(HERE / "samples"),
        help="input folder (default is samples next to this script)",
    )
    parser.add_argument(
        "--outdir",
        default=str(HERE / "work"),
        help="output folder (default is work next to this script)",
    )
    args = parser.parse_args()
    lyy = f"{args.LETTER}{args.YEAR % 100:02d}"
    infile = Path(args.indir) / f"{lyy}.in.csv.gz"
    if not infile.is_file():
        sys.stderr.write(f"ERROR: input file {infile} does not exist\n")
        return 1
    smpl = pd.read_csv(infile)
    if not (smpl.year == args.YEAR).all():
        sys.stderr.write(f"ERROR: {infile} contains a year other than "
                         f"{args.YEAR}\n")
        return 1
    tc = translate(smpl)
    check_tc_input(tc, smpl)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    tc.to_csv(outdir / f"{lyy}.in-tc.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
