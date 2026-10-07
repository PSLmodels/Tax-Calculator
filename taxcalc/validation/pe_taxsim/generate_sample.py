"""
Generates a random sample of tax filing units in TAXSIM-35 input format
for use as policyengine-taxsim input (step 1 of the validation).

USAGE: python generate_sample.py LETTER YEAR [--size N] [--offset K]

writes samples/LYY.in.csv.gz in the folder containing this script.
See VARIABLES.md for the input variables and their constraints.
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd


VALID_LETTERS = ["a", "b", "c"]
FIRST_YEAR = 2021
LAST_YEAR = 2025
DEFAULT_SIZE = 10_000
MAX_DEPX = 5
BASE_SEED = 123456789

# TAXSIM input columns written to each sample file, in output order
COLUMNS = (
    ["taxsimid", "year", "state", "mstat", "page", "sage", "depx"]
    + [f"age{num}" for num in range(1, MAX_DEPX + 1)]
    + [
        "pwages",
        "swages",
        "psemp",
        "ssemp",
        "dividends",
        "intrec",
        "stcg",
        "ltcg",
        "otherprop",
        "nonprop",
        "pensions",
        "gssi",
        "pui",
        "sui",
        "transfers",
        "rentpaid",
        "proptax",
        "otheritem",
        "childcare",
        "mortgage",
        "scorp",
        "pbusinc",
        "pprofinc",
        "sbusinc",
        "sprofinc",
        "idtl",
    ]
)

# columns that VARIABLES.md requires to be zero in every row
ALWAYS_ZERO = [
    "state",
    "nonprop",
    "transfers",
    "rentpaid",
    "pprofinc",
    "sprofinc",
]

# spouse columns that VARIABLES.md requires to be zero when mstat == 1
SPOUSE_COLUMNS = ["sage", "swages", "ssemp", "sui", "sbusinc"]


def assumption_set(letter):
    """
    Return dictionary containing the assumption parameters for LETTER.
    Dollar amounts are in thousands of dollars.
    """
    adict = {}
    # demographic attributes:
    adict["joint_frac"] = 0.60  # fraction of sample with mstat == 2
    adict["min_age"] = 17  # head age
    adict["max_age"] = 77  # head age
    adict["min_age_diff"] = -10  # spouse age minus head age
    adict["max_age_diff"] = 10  # spouse age minus head age
    adict["max_depx"] = MAX_DEPX  # number of dependents
    adict["min_dep_age"] = 1  # PE changes a zero dependent age to 10
    adict["max_dep_age"] = 23  # covers every child-count age boundary
    # labor income:
    adict["max_wages_yng"] = 500  # wages of person younger than 65
    adict["max_wages_old"] = 30  # wages of person aged 65 or older
    # all other income, child-care expenses, and itemized deductions:
    for name in [
        "semp",
        "divinc",
        "intinc",
        "stcg",
        "ltcg",
        "otherprop",
        "pension",
        "ssben",
        "uiben",
        "scorp",
        "businc",
        "ccexp",
        "proptax",
        "otheritem",
        "mortgage",
    ]:
        adict[f"min_{name}"] = 0
        adict[f"max_{name}"] = 0
    adict["business_frac"] = 0.0
    if letter in ["b", "c"]:
        # non-labor and business income:
        adict["max_semp"] = 350
        adict["max_divinc"] = 20
        adict["max_intinc"] = 20
        adict["min_stcg"] = -10
        adict["max_stcg"] = 10
        adict["min_ltcg"] = -10
        adict["max_ltcg"] = 10
        adict["max_otherprop"] = 30
        adict["max_pension"] = 60
        adict["max_ssben"] = 60
        adict["max_uiben"] = 10
        adict["max_scorp"] = 350
        adict["max_businc"] = 350
        # each business-income amount is nonzero for only this fraction
        # of units, so that many units have incomes low enough to get
        # the income-tested credits
        adict["business_frac"] = 0.25
    if letter == "c":
        # child-care expenses and itemized deductions:
        adict["max_ccexp"] = 10
        adict["max_proptax"] = 30
        adict["max_otheritem"] = 10
        adict["max_mortgage"] = 40
    return adict


def sample_seed(letter, year, offset):
    """
    Return the random-number-generator seed for the specified sample.
    """
    return [BASE_SEED, VALID_LETTERS.index(letter), year, offset]


def generate_sample(letter, year, size, offset):
    """
    Return DataFrame containing a random sample of SIZE filing units
    drawn using the LETTER assumption set for YEAR.
    """
    # pylint: disable=too-many-locals,too-many-statements
    assump = assumption_set(letter)
    rng = np.random.default_rng(sample_seed(letter, year, offset))
    zero = np.zeros(size, dtype=np.int64)

    def draw(name, nobs=size):
        """
        Return dollar amounts drawn uniformly from [min_name, max_name]
        thousands of dollars.
        """
        lo_val = assump.get(f"min_{name}", 0)
        hi_val = assump[f"max_{name}"]
        return rng.integers(lo_val, hi_val + 1, nobs) * 1000

    def draw_business(name):
        """
        Return dollar amounts that are drawn by draw(name) for a random
        business_frac fraction of units and that are zero for the rest.
        """
        nonzero = rng.random(size) < assump["business_frac"]
        return np.where(nonzero, draw(name), zero)

    smpl = pd.DataFrame({"taxsimid": np.arange(1, size + 1)})
    smpl["year"] = year
    smpl["state"] = 0
    # marital status and ages
    joint = rng.random(size) < assump["joint_frac"]
    smpl["mstat"] = np.where(joint, 2, 1)
    page = rng.integers(assump["min_age"], assump["max_age"] + 1, size)
    smpl["page"] = page
    age_diff = rng.integers(
        assump["min_age_diff"], assump["max_age_diff"] + 1, size
    )
    sage = np.maximum(page + age_diff, assump["min_age"])
    smpl["sage"] = np.where(joint, sage, zero)
    # dependents, with ages sorted youngest first and zero for unused slots
    depx = rng.integers(0, assump["max_depx"] + 1, size)
    smpl["depx"] = depx
    ages = rng.integers(
        assump["min_dep_age"],
        assump["max_dep_age"] + 1,
        (size, assump["max_depx"]),
    )
    slot = np.arange(assump["max_depx"])
    ages = np.where(slot < depx[:, np.newaxis], ages, 0)
    ages = np.sort(np.where(ages > 0, ages, 999), axis=1)
    ages = np.where(ages < 999, ages, 0)
    for num in range(1, assump["max_depx"] + 1):
        smpl[f"age{num}"] = ages[:, num - 1]
    # labor income
    pwages = np.where(page >= 65, draw("wages_old"), draw("wages_yng"))
    smpl["pwages"] = pwages
    swages = np.where(sage >= 65, draw("wages_old"), draw("wages_yng"))
    smpl["swages"] = np.where(joint, swages, zero)
    smpl["psemp"] = draw_business("semp")
    smpl["ssemp"] = np.where(joint, draw_business("semp"), zero)
    # non-labor income
    smpl["dividends"] = draw("divinc")
    smpl["intrec"] = draw("intinc")
    smpl["stcg"] = draw("stcg")
    smpl["ltcg"] = draw("ltcg")
    smpl["otherprop"] = draw("otherprop")
    smpl["nonprop"] = 0  # ignored by PE
    smpl["pensions"] = draw("pension")
    smpl["gssi"] = draw("ssben")
    smpl["pui"] = draw("uiben")
    smpl["sui"] = np.where(joint, draw("uiben"), zero)
    smpl["transfers"] = 0  # non-taxable
    smpl["rentpaid"] = 0  # used only by state income taxes
    # itemized deductions and child-care expenses
    smpl["proptax"] = draw("proptax")
    smpl["otheritem"] = draw("otheritem")
    has_young_dep = ((ages > 0) & (ages < 13)).any(axis=1)
    smpl["childcare"] = np.where(has_young_dep, draw("ccexp"), zero)
    smpl["mortgage"] = draw("mortgage")
    # business income
    smpl["scorp"] = draw_business("scorp")
    smpl["pbusinc"] = draw_business("businc")
    smpl["pprofinc"] = 0  # TC cannot represent per-person SSTB income
    smpl["sbusinc"] = np.where(joint, draw_business("businc"), zero)
    smpl["sprofinc"] = 0  # TC cannot represent per-person SSTB income
    smpl["idtl"] = 2
    return smpl[COLUMNS].astype(np.int64)


def check_sample(smpl, letter, year, size):
    """
    Raise ValueError if SMPL violates any of the VARIABLES.md constraints.
    """
    assump = assumption_set(letter)
    errors = []

    def require(condition, msg):
        if not condition:
            errors.append(msg)

    require(list(smpl.columns) == COLUMNS, "unexpected columns")
    require(len(smpl) == size, "wrong number of rows")
    require(not smpl.isna().any().any(), "missing values")
    require(
        (smpl.taxsimid == np.arange(1, size + 1)).all(), "taxsimid not 1..N"
    )
    require((smpl.year == year).all(), "wrong year")
    require((smpl.idtl == 2).all(), "idtl not 2")
    require(smpl.mstat.isin([1, 2]).all(), "mstat not 1 or 2")
    for col in ALWAYS_ZERO:
        require((smpl[col] == 0).all(), f"{col} not zero")
    single = smpl.mstat == 1
    for col in SPOUSE_COLUMNS:
        require((smpl.loc[single, col] == 0).all(), f"{col} not zero")
    require(
        smpl.page.between(assump["min_age"], assump["max_age"]).all(),
        "page out of range",
    )
    require(
        smpl.loc[~single, "sage"].ge(assump["min_age"]).all(),
        "sage out of range",
    )
    require(
        smpl.depx.between(0, assump["max_depx"]).all(), "depx out of range"
    )
    ages = smpl[[f"age{num}" for num in range(1, MAX_DEPX + 1)]].to_numpy()
    used = np.arange(MAX_DEPX) < smpl.depx.to_numpy()[:, np.newaxis]
    require((ages[~used] == 0).all(), "nonzero age of unused dependent")
    require(
        (
            (ages[used] >= assump["min_dep_age"])
            & (ages[used] <= assump["max_dep_age"])
        ).all(),
        "dependent age out of range",
    )
    young = ((ages > 0) & (ages < 13)).any(axis=1)
    require((smpl.loc[~young, "childcare"] == 0).all(), "childcare not zero")
    for col in ["stcg", "ltcg"]:
        require(
            smpl[col].between(
                assump[f"min_{col}"] * 1000, assump[f"max_{col}"] * 1000
            ).all(),
            f"{col} out of range",
        )
    money = [
        col
        for col in COLUMNS[COLUMNS.index("pwages"):-1]
        if col not in ["stcg", "ltcg"]
    ]
    require((smpl[money] >= 0).all().all(), "negative dollar amount")
    require(
        (smpl[COLUMNS[COLUMNS.index("pwages"):-1]] % 1000 == 0).all().all(),
        "dollar amount not a multiple of 1000",
    )
    if errors:
        raise ValueError("sample check failed: " + "; ".join(errors))


def main():
    """
    Generate, check, and write the sample specified on the command line.
    """
    parser = argparse.ArgumentParser(
        prog="python generate_sample.py",
        description=(
            "Writes samples/LYY.in.csv.gz containing a random sample of "
            "filing units in TAXSIM-35 input format."
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
        "--size",
        type=int,
        default=DEFAULT_SIZE,
        help=f"number of filing units (default {DEFAULT_SIZE})",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="random-number seed offset (default 0)",
    )
    parser.add_argument(
        "--outdir",
        default=str(Path(__file__).resolve().parent / "samples"),
        help="output folder (default is samples next to this script)",
    )
    args = parser.parse_args()
    if args.size < 1:
        sys.stderr.write("ERROR: --size must be positive\n")
        return 1
    if args.offset < 0:
        sys.stderr.write("ERROR: --offset must be non-negative\n")
        return 1
    smpl = generate_sample(args.LETTER, args.YEAR, args.size, args.offset)
    check_sample(smpl, args.LETTER, args.YEAR, args.size)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = f"{args.LETTER}{args.YEAR % 100:02d}.in.csv.gz"
    # a zero gzip mtime makes the file bytes depend only on the sample
    smpl.to_csv(
        outdir / fname,
        index=False,
        compression={"method": "gzip", "mtime": 0},
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
