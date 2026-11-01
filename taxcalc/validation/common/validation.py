"""
Runs the validation for each specified assumption-set letter and year
of a validation workflow.  It is used by the validate.py script in each
workflow folder (validation/WORKFLOW), whose name is the "prog" below.

USAGE: python validate.py [--letters LETTERS] [--years YEARS]
                          [--tolerance T] [--regen [--size N]]
                          [--datadir DIR]

By default, runs steps 3-5 (taxsim_to_tc.py, run_tc.py, compare.py in
this folder) for every letter (abc) and every year in the workflow
default year range using the committed samples and other-model
outputs, and prints each comparison summary.  With --regen, first runs
steps 1-2 (generate_sample.py in this folder and the workflow's
run_M.py --force, where M is the other model's label), which
OVERWRITES the samples and other-model outputs in DATADIR; those
outputs are committed, so regenerate them only deliberately (see the
workflow README.md).

DATADIR (default is the workflow folder) holds the samples, M_output,
and work folders, so a tiny trial run can be kept out of the committed
folders, for example:
  python validate.py --letters a --years 2023 --regen --size 100 \\
                     --datadir /some/scratch/folder
The exit code is 0 when every step runs without error and 1 otherwise.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
# pylint: disable-next=import-error
from workflows import VALID_LETTERS, WORKFLOWS

COMMON = Path(__file__).resolve().parent


def print_pin(wfl):
    """
    Print the information in the pin file of Workflow WFL, omitting the
    comment entries.
    """
    with open(wfl.folder / wfl.pin_file, "r", encoding="utf-8") as pfile:
        pin = json.load(pfile)
    print(f"===== {wfl.model.upper()}_PIN =====")
    for key, val in pin.items():
        if key.startswith("_"):
            continue
        if isinstance(val, list):
            val = " ".join(val)
        print(f"{key}: {val}")
    sys.stdout.flush()


def run_step(wfl, script, args):
    """
    Run SCRIPT with the list of string ARGS and return its exit code,
    where SCRIPT is in the folder of Workflow WFL or, if not there, in
    the common folder.
    """
    path = wfl.folder / script
    if not path.exists():
        path = COMMON / script
    cmd = [sys.executable, str(path)] + args
    return subprocess.run(cmd, check=False).returncode


def validate(wfl, letter, year, args, datadir):
    """
    Run the validation steps of Workflow WFL for LETTER and YEAR and
    return a result string: OK or the name of the step that failed to
    run.
    """
    sampledir = datadir / "samples"
    modeldir = datadir / wfl.output_dir
    workdir = datadir / "work"
    for folder in (sampledir, modeldir, workdir):
        folder.mkdir(parents=True, exist_ok=True)
    lyear = [letter, str(year)]
    wflow = ["--workflow", wfl.name]
    steps = []
    if args.regen:
        steps.append(("generate_sample.py", lyear + wflow + [
            "--size", str(args.size), "--outdir", str(sampledir)]))
        steps.append((wfl.runner, lyear + [
            "--force", "--indir", str(sampledir),
            "--outdir", str(modeldir)]))
    steps.append(("taxsim_to_tc.py", lyear + wflow + [
        "--indir", str(sampledir), "--outdir", str(workdir)]))
    steps.append(("run_tc.py", lyear + wflow + [
        "--workdir", str(workdir)]))
    steps.append(("compare.py", lyear + wflow + [
        "--tolerance", str(args.tolerance),
        "--modeldir", str(modeldir),
        "--workdir", str(workdir)]))
    for script, script_args in steps:
        if run_step(wfl, script, script_args) != 0:
            return f"ERROR in {script}"
    return "OK"


def year_parser(wfl):
    """
    Return a function that returns the list of years specified by its
    TEXT argument, a comma-separated list of years or year ranges
    (e.g., "2023,2024-2025"), all in the default year range of
    Workflow WFL.
    """
    def parse_years(text):
        years = []
        for item in text.split(","):
            first, _, last = item.strip().partition("-")
            years.extend(range(int(first), int(last or first) + 1))
        if not years or any(y not in wfl.years for y in years):
            raise argparse.ArgumentTypeError(
                f"years must be in [{wfl.first_year},{wfl.last_year}]"
            )
        return sorted(set(years))
    return parse_years


def main(workflow):
    """
    Run the validation of the WORKFLOW (a WORKFLOWS key) for the letters
    and years specified on the command line.
    """
    wfl = WORKFLOWS[workflow]
    letters_default = "".join(VALID_LETTERS)
    years_default = f"{wfl.first_year}-{wfl.last_year}"
    parser = argparse.ArgumentParser(
        prog="python validate.py",
        description=(
            f"Runs {wfl.name} validation steps 3-5 (and steps 1-2 with "
            "--regen) for each specified assumption-set letter and year."
        ),
    )
    parser.add_argument(
        "--letters",
        default=letters_default,
        help=f"assumption set letters (default {letters_default})",
    )
    parser.add_argument(
        "--years",
        type=year_parser(wfl),
        default=wfl.years,
        help=("comma-separated years or year ranges "
              f"(default {years_default})"),
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
        help=(f"also run steps 1-2, overwriting samples and "
              f"{wfl.model.upper()} outputs"),
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10000,
        help="sample size used with --regen (default 10000)",
    )
    parser.add_argument(
        "--datadir",
        default=str(wfl.folder),
        help=(f"folder holding samples, {wfl.output_dir}, and work "
              f"(default is validation/{wfl.name})"),
    )
    args = parser.parse_args()
    print_pin(wfl)
    letters = list(args.letters)
    if not letters or any(ltr not in VALID_LETTERS for ltr in letters):
        sys.stderr.write(
            f"ERROR: --letters must use only {letters_default}\n"
        )
        return 1
    datadir = Path(args.datadir).resolve()
    results = {}
    for letter in letters:
        for year in args.years:
            lyy = f"{letter}{year % 100:02d}"
            print(f"===== {lyy} =====", flush=True)
            results[lyy] = validate(wfl, letter, year, args, datadir)
    return 0 if all(res == "OK" for res in results.values()) else 1
