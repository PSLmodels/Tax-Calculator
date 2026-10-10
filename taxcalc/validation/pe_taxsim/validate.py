"""
Runs the validation for each specified assumption-set letter and year.

USAGE: python validate.py [--letters LETTERS] [--years YEARS]
                          [--tolerance T] [--regen [--size N]]
                          [--datadir DIR]

By default, runs steps 3-5 (taxsim_to_tc.py, run_tc.py, compare.py)
for every letter (abc) and year (2021-2025) using the committed
samples and PE outputs, and prints a pass/fail table.  With --regen,
first runs steps 1-2 (generate_sample.py, run_pe.py --force), which
OVERWRITES the samples and PE outputs in DATADIR; PE outputs are
committed, so regenerate them only deliberately (see PLAN.md).

DATADIR (default is the folder containing this script) holds the
samples, pe_output, expected_differences, and work folders, so a
tiny trial run can be kept out of the committed folders, for example:
  python validate.py --letters a --years 2021 --regen --size 100 \\
                     --datadir /some/scratch/folder
The exit code is 0 when every comparison passes and 1 otherwise.
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

VALID_LETTERS = "abc"
FIRST_YEAR = 2021
LAST_YEAR = 2025


def run_step(script, args):
    """
    Run SCRIPT in this folder with the list of string ARGS and return
    its exit code.
    """
    cmd = [sys.executable, str(HERE / script)] + args
    return subprocess.run(cmd, check=False).returncode


def validate(letter, year, args, datadir):
    """
    Run the validation steps for LETTER and YEAR and return a result
    string: PASS, FAIL, or the name of the step that failed to run.
    """
    sampledir = datadir / "samples"
    pedir = datadir / "pe_output"
    workdir = datadir / "work"
    expectdir = datadir / "expected_differences"
    for folder in (sampledir, pedir, workdir):
        folder.mkdir(parents=True, exist_ok=True)
    lyear = [letter, str(year)]
    steps = []
    if args.regen:
        steps.append(("generate_sample.py", lyear + [
            "--size", str(args.size), "--outdir", str(sampledir)]))
        steps.append(("run_pe.py", lyear + [
            "--force", "--indir", str(sampledir), "--outdir", str(pedir)]))
    steps.append(("taxsim_to_tc.py", lyear + [
        "--indir", str(sampledir), "--outdir", str(workdir)]))
    steps.append(("run_tc.py", lyear + ["--workdir", str(workdir)]))
    for script, script_args in steps:
        if run_step(script, script_args) != 0:
            return f"ERROR in {script}"
    code = run_step("compare.py", lyear + [
        "--tolerance", str(args.tolerance),
        "--pedir", str(pedir),
        "--workdir", str(workdir),
        "--expectdir", str(expectdir),
    ])
    return {0: "PASS", 1: "FAIL"}.get(code, "ERROR in compare.py")


def parse_years(text):
    """
    Return list of years specified by TEXT, a comma-separated list of
    years or year ranges (e.g., "2021,2023-2025").
    """
    years = []
    for item in text.split(","):
        first, _, last = item.strip().partition("-")
        years.extend(range(int(first), int(last or first) + 1))
    if not years or any(y < FIRST_YEAR or y > LAST_YEAR for y in years):
        raise argparse.ArgumentTypeError(
            f"years must be in [{FIRST_YEAR},{LAST_YEAR}]"
        )
    return sorted(set(years))


def main():
    """
    Run the validation for the letters and years specified on the
    command line.
    """
    parser = argparse.ArgumentParser(
        prog="python validate.py",
        description=(
            "Runs validation steps 3-5 (and steps 1-2 with --regen) for "
            "each specified assumption-set letter and year."
        ),
    )
    parser.add_argument(
        "--letters",
        default=VALID_LETTERS,
        help=f"assumption set letters (default {VALID_LETTERS})",
    )
    parser.add_argument(
        "--years",
        type=parse_years,
        default=list(range(FIRST_YEAR, LAST_YEAR + 1)),
        help=("comma-separated years or year ranges "
              f"(default {FIRST_YEAR}-{LAST_YEAR})"),
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1.0,
        help="compare.py tolerance (default 1)",
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="also run steps 1-2, overwriting samples and PE outputs",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10000,
        help="sample size used with --regen (default 10000)",
    )
    parser.add_argument(
        "--datadir",
        default=str(HERE),
        help=("folder holding samples, pe_output, expected_differences, "
              "and work (default is the folder containing this script)"),
    )
    args = parser.parse_args()
    letters = list(args.letters)
    if not letters or any(ltr not in VALID_LETTERS for ltr in letters):
        sys.stderr.write(f"ERROR: --letters must use only {VALID_LETTERS}\n")
        return 1
    datadir = Path(args.datadir).resolve()
    results = {}
    for letter in letters:
        for year in args.years:
            lyy = f"{letter}{year % 100:02d}"
            print(f"===== {lyy} =====", flush=True)
            results[lyy] = validate(letter, year, args, datadir)
    print("===== SUMMARY =====")
    for lyy, result in results.items():
        print(f"{lyy}: {result}")
    return 0 if all(r == "PASS" for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
