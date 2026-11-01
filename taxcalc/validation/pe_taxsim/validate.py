"""
Runs the pe_taxsim validation (Tax-Calculator versus policyengine-taxsim)
for each specified assumption-set letter and year.

USAGE: python validate.py [--letters LETTERS] [--years YEARS]
                          [--tolerance T] [--regen [--size N]]
                          [--datadir DIR]

The validation logic is shared with the other workflows and lives in
../common/validation.py; see its docstring and README.md for details,
or use "python validate.py --help".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
# pylint: disable=wrong-import-position,import-error
from validation import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main("pe_taxsim"))
