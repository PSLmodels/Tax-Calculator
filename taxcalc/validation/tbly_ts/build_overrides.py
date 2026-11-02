"""
Builds ts_law_overrides.csv, which run_ts.R uses to replace indexed
Tax-Simulator tax law parameter values that differ from the IRS and SSA
published values.

USAGE: python build_overrides.py [--last-year YEAR] [--check]
                                 [--tsdir TSDIR] [--rscript RSCRIPT]

For each year from FIRST_YEAR through LAST_YEAR (both from run_ts.py),
this script runs dump_ts_law.R to get the Tax-Simulator (TS) baseline
law, built from ts_indexes.csv at the commit pinned in ts_pin.json, and
compares each TS variable in OVERRIDE and CHECK (below) with the
corresponding Tax-Calculator (TC) policy parameter value in
policy_current_law.json, which holds the IRS and SSA published values.

- A difference in an OVERRIDE variable is written to the overrides file
  as a row containing the year, the TS filing status, the TS variable,
  the TC value (value), and the TS value (ts_value).  OVERRIDE
  variables are the ones whose TS values differ from the published
  values only because TS's inflation indexation differs from the
  IRS's.  Only the cells that differ are written.

- A difference in a CHECK variable is never overridden.  It must be
  listed in KNOWN_TS_ERRORS, which documents parameter values that are
  wrong in the TS YAML files themselves and are left in place so that
  they show up as differences (see SUMMARY.md), or this script fails.
  An entry in KNOWN_TS_ERRORS that no longer matches a difference also
  makes this script fail.

The TS filing status codes are 1 (single), 2 (married filing jointly),
3 (married filing separately), and 4 (head of household).

The --check option writes nothing and exits with code one if the
generated file differs from the committed ts_law_overrides.csv.  The
--last-year option lets a new year be examined before LAST_YEAR in
run_ts.py is changed (see README.md).
"""

import argparse
import csv
import io
import math
import subprocess
import sys
import tempfile
from pathlib import Path

# pylint: disable=import-error
from run_ts import (
    FIRST_YEAR,
    LAST_YEAR,
    INDEXES_FILE,
    OVERRIDES_FILE,
    read_pin,
    ts_folder,
    ensure_ts_clone,
    rscript_path,
    check_r_versions,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT))
# pylint: disable=wrong-import-position
from taxcalc import Policy  # noqa: E402

DUMP_SCRIPT = HERE / "dump_ts_law.R"
FILING_STATUSES = (1, 2, 3, 4)
COLUMNS = ["year", "filing_status", "variable", "value", "ts_value"]


# TS variable -> (TC parameter, how the TC value is selected), where
# "mars" means the TC parameter is indexed by filing status, "scalar"
# means it is not, and an integer K means the TC parameter is indexed
# by the number of EITC qualifying children K
OVERRIDE = {
    **{f"ord.brackets{n}": (f"II_brk{n - 1}", "mars") for n in range(2, 8)},
    **{f"pref.brackets{n}": (f"CG_brk{n - 1}", "mars") for n in (2, 3)},
    "amt.brackets2": ("AMT_brk1", "mars"),
    "amt.exempt": ("AMT_em", "mars"),
    "amt.exempt_po_thresh": ("AMT_em_ps", "mars"),
    **{f"eitc.pi_end_{k}": ("EITC_c", k) for k in range(4)},
    **{f"eitc.po_thresh_{k}": ("EITC_ps", k) for k in range(4)},
    "eitc.inv_inc_limit": ("EITC_InvestIncome_c", "scalar"),
    "qbi.po_thresh_non_sstb": ("PT_qbid_taxinc_thd", "mars"),
    "qbi.po_thresh_sstb": ("PT_qbid_taxinc_thd", "mars"),
    "pr.oasdi_ee_brackets2": ("SS_Earnings_c", "scalar"),
    "pr.oasdi_er_brackets2": ("SS_Earnings_c", "scalar"),
}
CHECK = {
    "std.value": ("STD", "mars"),
    "std.bonus": ("STD_Aged", "mars"),
    "std.dep_floor": ("STD_Dep", "scalar"),
    "std.dep_earned_bonus": ("STD_Dep_earned_add", "scalar"),
    "ctc.value_young1": ("CTC_c", "scalar"),
    "ctc.value_old1": ("CTC_c", "scalar"),
    "ctc.value_other": ("ODC_c", "scalar"),
    "ctc.po_thresh1": ("CTC_ps", "mars"),
    "ctc.max_refund_young": ("ACTC_c", "scalar"),
    "ctc.max_refund_old": ("ACTC_c", "scalar"),
    "ctc.pi_thresh": ("ACTC_Income_thd", "scalar"),
    "cdctc.exp_limit": ("CDCC_c", "scalar"),
    "item.salt_limit": ("ID_AllTaxes_c", "mars"),
    "below.senior_ded_value": ("SeniorDed_c", "scalar"),
    "below.senior_ded_po_thresh": ("SeniorDed_ps", "mars"),
    "qbi.po_range_non_sstb": ("PT_qbid_taxinc_gap", "mars"),
    "qbi.po_range_sstb": ("PT_qbid_taxinc_gap", "mars"),
    "ss.brackets2": ("SS_thd1", "mars"),
    "ss.brackets3": ("SS_thd2", "mars"),
    "niit.brackets2": ("NIIT_thd", "mars"),
    "pr.add_med_brackets2": ("AMEDT_ec", "mars"),
}

# (TS variable, years or None for all, filing statuses or None for all)
# -> reason the CHECK difference is left in place
KNOWN_TS_ERRORS = {
    ("std.bonus", None, (3,)): (
        "TS uses the unmarried aged/blind amount for married filing "
        "separately (SUMMARY.md item 4)"
    ),
    ("std.value", (2025,), None): (
        "TS uses the pre-OBBBA 2025 standard deduction "
        "(SUMMARY.md item 5)"
    ),
}

# TC holds the EITC maximum credit and phase-in rate, not the earned
# income amount at the end of the phase-in, which the IRS rounds to a
# multiple of $10.  When more than one multiple of $10 is consistent
# with the TC maximum credit and rate, the IRS published amount must be
# given here: (year, number of qualifying children) -> amount
EITC_EARNED_AMOUNT = {
    (2025, 0): 8490,  # Rev. Proc. 2024-40
}


def eitc_earned_amount(policy, year, kids):
    """
    Return the IRS EITC earned income amount for YEAR and KIDS
    qualifying children implied by the POLICY maximum credit and
    phase-in rate, using EITC_EARNED_AMOUNT when that is ambiguous.
    """
    credit = policy.EITC_c[0][kids]
    rate = policy.EITC_rt[0][kids]
    lo_amt = int((credit - 0.5) / rate) // 10 * 10
    hi_amt = int((credit + 0.5) / rate) + 10
    candidates = [
        amt for amt in range(lo_amt, hi_amt + 1, 10)
        if math.floor(rate * amt + 0.5) == credit
    ]
    published = EITC_EARNED_AMOUNT.get((year, kids))
    if published is None:
        if len(candidates) != 1:
            raise ValueError(
                f"EITC earned income amount for {year} and {kids} "
                f"children is ambiguous ({candidates}); add the IRS "
                "published amount to EITC_EARNED_AMOUNT"
            )
        return candidates[0]
    if len(candidates) < 2 or published not in candidates:
        raise ValueError(
            f"EITC_EARNED_AMOUNT entry for {year} and {kids} children "
            f"is {published} but the TC values imply {candidates}"
        )
    return published


def tc_value(policy, year, variable, filing_status):
    """
    Return the TC value corresponding to TS VARIABLE and FILING_STATUS
    in YEAR, with POLICY already set to YEAR.
    """
    param, kind = {**OVERRIDE, **CHECK}[variable]
    if variable.startswith("eitc.pi_end_"):
        return eitc_earned_amount(policy, year, kind)
    value = getattr(policy, param)[0]
    if kind == "mars":
        return float(value[filing_status - 1])
    if kind == "scalar":
        return float(value)
    # EITC phase-out threshold by number of children
    value = value[kind]
    if filing_status == 2:
        value += policy.EITC_ps_addon_MarriedJ[0][kind]
    return float(value)


def dump_ts_law(year, tsdir, rscript):
    """
    Return dictionary mapping (filing_status, variable) to the TS value
    in YEAR.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        outfile = Path(tmpdir) / f"law{year}.csv"
        cmd = [str(rscript), "--vanilla", str(DUMP_SCRIPT), str(tsdir)]
        cmd += [str(year), str(INDEXES_FILE), str(outfile)]
        subprocess.run(cmd, check=True)
        with open(outfile, "r", encoding="utf-8") as lfile:
            return {
                (int(row["filing_status"]), row["variable"]):
                float(row["ts_value"])
                for row in csv.DictReader(lfile)
            }


def known_error(variable, year, filing_status):
    """
    Return the KNOWN_TS_ERRORS key that covers the arguments, or None.
    """
    for key in KNOWN_TS_ERRORS:
        var, years, statuses = key
        if (var == variable
                and (years is None or year in years)
                and (statuses is None or filing_status in statuses)):
            return key
    return None


def compare_year(year, law, policy, rows, problems):
    """
    Append to ROWS the overrides for YEAR given TS LAW, append to
    PROBLEMS any unexplained CHECK difference, and return the set of
    KNOWN_TS_ERRORS keys matched by a difference.
    """
    policy.set_year(year)
    matched = set()
    for variable in sorted({**OVERRIDE, **CHECK}):
        for fstat in FILING_STATUSES:
            if (fstat, variable) not in law:
                problems.append(f"{variable} is not a TS law variable")
                break
            tsval = law[(fstat, variable)]
            tcval = tc_value(policy, year, variable, fstat)
            if math.isclose(tsval, tcval, rel_tol=0.0, abs_tol=1e-6):
                continue
            if variable in OVERRIDE:
                rows.append([year, fstat, variable, tcval, tsval])
                continue
            key = known_error(variable, year, fstat)
            if key is None:
                problems.append(
                    f"{year} filing status {fstat} {variable}: TS value "
                    f"{tsval:g} differs from TC value {tcval:g} and is "
                    "not in KNOWN_TS_ERRORS"
                )
            else:
                matched.add(key)
    return matched


def number(val):
    """
    Return VAL formatted as an integer if it is one, else exactly.
    """
    return str(int(val)) if float(val).is_integer() else repr(val)


def overrides_text(rows):
    """
    Return the overrides csv contents for ROWS, sorted by variable,
    year, and filing status.
    """
    rows = sorted(rows, key=lambda r: (r[2], r[0], r[1]))
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(COLUMNS)
    for year, fstat, variable, value, tsval in rows:
        writer.writerow([year, fstat, variable, number(value),
                         number(tsval)])
    return buf.getvalue()


def build(last_year, tsdir, rscript):
    """
    Return the overrides csv contents for FIRST_YEAR through LAST_YEAR,
    after writing a summary to stderr, or raise RuntimeError.
    """
    pin = read_pin()
    tsdir = ts_folder(pin, tsdir)
    ensure_ts_clone(pin, tsdir)
    rscript = rscript_path(pin, rscript)
    check_r_versions(pin, rscript)
    policy = Policy()
    rows = []
    problems = []
    matched = set()
    years = range(FIRST_YEAR, last_year + 1)
    for year in years:
        sys.stderr.write(f"comparing {year} TS law with TC parameters\n")
        law = dump_ts_law(year, tsdir, rscript)
        matched |= compare_year(year, law, policy, rows, problems)
    report(rows, matched, years, problems)
    return overrides_text(rows)


def report(rows, matched, years, problems):
    """
    Write a summary of override ROWS and of the KNOWN_TS_ERRORS keys
    MATCHED in YEARS to stderr, or raise RuntimeError listing PROBLEMS
    and any KNOWN_TS_ERRORS entry that matched no difference.
    """
    for key, reason in KNOWN_TS_ERRORS.items():
        kyears = key[1]
        if kyears is not None and not set(kyears) & set(years):
            continue
        if key in matched:
            sys.stderr.write(f"not overridden: {key[0]}: {reason}\n")
        else:
            problems.append(f"KNOWN_TS_ERRORS entry {key} matches no "
                            "difference")
    if problems:
        raise RuntimeError("\n".join(problems))
    counts = {}
    for row in rows:
        counts[(row[0], row[2])] = counts.get((row[0], row[2]), 0) + 1
    for (year, variable), count in sorted(counts.items()):
        sys.stderr.write(f"override: {year} {variable} ({count} rows)\n")
    sys.stderr.write(f"{len(rows)} override rows\n")


def main():
    """
    Build or check ts_law_overrides.csv.
    """
    parser = argparse.ArgumentParser(
        prog="python build_overrides.py",
        description=(
            "Compares the pinned Tax-Simulator law with Tax-Calculator "
            "policy parameters and writes ts_law_overrides.csv."
        ),
    )
    parser.add_argument(
        "--last-year",
        type=int,
        default=LAST_YEAR,
        help=f"last year to include (default is {LAST_YEAR})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=("write nothing and fail if the generated file differs "
              "from the committed one"),
    )
    parser.add_argument(
        "--output",
        default=str(OVERRIDES_FILE),
        help="file to write (default is ts_law_overrides.csv)",
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
    if args.last_year < FIRST_YEAR:
        parser.error(f"--last-year must be at least {FIRST_YEAR}")
    try:
        text = build(args.last_year, args.tsdir, args.rscript)
    except (RuntimeError, ValueError) as err:
        sys.stderr.write(f"ERROR: {err}\n")
        return 1
    if args.check:
        same = OVERRIDES_FILE.read_text(encoding="utf-8") == text
        sys.stderr.write(
            "generated file is identical to ts_law_overrides.csv\n" if same
            else "ERROR: generated file differs from ts_law_overrides.csv\n"
        )
        return 0 if same else 1
    Path(args.output).write_text(text, encoding="utf-8")
    sys.stderr.write(f"wrote {args.output}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
