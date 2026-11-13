"""
Defines the settings of each cross-model validation workflow, which
are used by the scripts in this folder.

Each workflow compares Tax-Calculator with another model ("the other
model") using TAXSIM-35 format samples and outputs, and lives in the
validation/WORKFLOW folder, which holds its samples, the other model's
committed outputs, its Tax-Calculator emulation reform, and the
git-ignored work folder.
"""

from dataclasses import dataclass
from pathlib import Path

VALIDATION_DIR = Path(__file__).resolve().parents[1]
VALID_LETTERS = ["a", "b", "c"]


@dataclass(frozen=True)
class Workflow:
    """
    Settings of one validation workflow.
    """
    name: str  # validation/NAME folder name
    model: str  # short label of the other model (e.g., pe)
    first_year: int  # first year in the default year range
    last_year: int  # last year in the default year range
    max_depx: int  # default maximum number of dependents in samples
    pin_file: str  # file that pins the other model's version

    @property
    def folder(self):
        """
        Path of the workflow folder.
        """
        return VALIDATION_DIR / self.name

    @property
    def output_dir(self):
        """
        Name of the folder holding the other model's outputs.
        """
        return f"{self.model}_output"

    @property
    def emulation_file(self):
        """
        Path of the reform file that makes Tax-Calculator adopt the
        modeling conventions of the other model.
        """
        return self.folder / f"{self.model}_emulation.json"

    @property
    def runner(self):
        """
        Name of the script in the workflow folder that runs the other
        model (step 2).
        """
        return f"run_{self.model}.py"

    def output_file(self, lyy):
        """
        Name of the other model's output file for sample LYY.
        """
        return f"{lyy}.out-{self.model}.csv.gz"

    @property
    def years(self):
        """
        List of the years in the default year range.
        """
        return list(range(self.first_year, self.last_year + 1))


WORKFLOWS = {
    wfl.name: wfl for wfl in [
        Workflow(
            name="pe_taxsim", model="pe", first_year=2021, last_year=2025,
            max_depx=5, pin_file="pe_pin.json",
        ),
        # tax-simulator-gpu records only three dependent ages
        Workflow(
            name="tbly_ts", model="ts", first_year=2023, last_year=2025,
            max_depx=3, pin_file="ts_pin.json",
        ),
    ]
}


def add_sample_arguments(parser):
    """
    Add the LETTER and YEAR positional arguments and the required
    --workflow option to argparse PARSER.
    """
    first = min(wfl.first_year for wfl in WORKFLOWS.values())
    last = max(wfl.last_year for wfl in WORKFLOWS.values())
    parser.add_argument(
        "LETTER", choices=VALID_LETTERS, help="assumption set letter"
    )
    parser.add_argument(
        "YEAR",
        type=int,
        metavar="YEAR",
        help=(f"tax year in the WORKFLOW default year range "
              f"(within [{first},{last}])"),
    )
    parser.add_argument(
        "--workflow",
        required=True,
        choices=list(WORKFLOWS),
        help="validation workflow (folder validation/WORKFLOW)",
    )


def parse_sample_arguments(parser):
    """
    Return (args, workflow, lyy) after parsing the command line with
    argparse PARSER, to which add_sample_arguments has been applied,
    where workflow is the Workflow named by --workflow and lyy is the
    sample name (e.g., a23).  Exits with an error message if YEAR is not
    in the workflow default year range.
    """
    args = parser.parse_args()
    wfl = WORKFLOWS[args.workflow]
    if args.YEAR not in wfl.years:
        parser.error(f"YEAR must be in the {wfl.name} default year range "
                     f"[{wfl.first_year},{wfl.last_year}]")
    return args, wfl, f"{args.LETTER}{args.YEAR % 100:02d}"
