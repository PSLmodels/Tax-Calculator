"""
Runs the tax-simulator-gpu batch command on a CSV file of tax units
(the part of step 2 of the validation that runs in the
tax-simulator-gpu environment; called by run_ts.py).

USAGE: python ts_batch.py RECORDS YEAR OUTFILE SHA

reads the tax-simulator-gpu records in CSV file RECORDS (written by
run_ts.py), writes them to a parquet file, runs the taxmodel.run.batch
command (tax-simulator-gpu commit SHA) on them under the YEAR default
law, and writes its output, plus the HI_EE_RATE column holding each
unit's employee HI tax rate, to CSV file OUTFILE and the batch command's
manifest to OUTFILE.manifest.json.

This script must be run with the Python of the tax-simulator-gpu
environment (uv run --project TSDIR --locked), so it imports nothing
from Tax-Calculator.  tax-simulator-gpu code is used but never
modified.
"""

import shutil
import sys
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxmodel.law import indexes
from taxmodel.run import batch
from taxmodel.scenario import law_by_year, provenance

# options of the batch command (see VARIABLES.md):
# --zero-draws makes every random rule apply to every unit it can, so
#   the child care credit has full take-up (the EITC pre-certification
#   check is not part of the default law);
# --bundled-macro uses the price indexes of the pinned Macro-Projections
#   publication that are part of the tax-simulator-gpu repository
BATCH_OPTIONS = ["--zero-draws", "--bundled-macro"]
HI_EE_RATE = "hi_ee_rate"


def hi_ee_rates(year):
    """
    Return array of the employee HI tax rate under the YEAR default law
    for each of the four tax-simulator-gpu filing statuses, after
    checking that the employee HI tax has a single rate.
    """
    growth = indexes.derive_index_table(indexes.BUNDLED_MACRO_PROJECTIONS)
    scenario = provenance.load_scenario([year], alternative=None,
                                        growth=growth)
    series = law_by_year.bind_annual_laws(
        scenario.values, scenario.years, scenario.law_table, [year]
    )
    payroll = series.by_year[0].calculator.payroll
    rates = np.asarray(payroll.hi_ee_rates, dtype=np.float64)
    brackets = np.asarray(payroll.hi_ee_brackets, dtype=np.float64)
    if rates.shape[0] != 4 or np.any(brackets[:, 0] != 0.0):
        raise ValueError("unexpected employee HI tax schedule shape")
    used = ~np.isnan(rates[:, 1:]) & ~np.isnan(brackets[:, 1:])
    if used.any():
        raise ValueError("employee HI tax has more than one rate")
    return rates[:, 0]


def main(records, year, outfile, sha):
    """
    Run the batch command as described in the module docstring.
    """
    year = int(year)
    tmpdir = Path(tempfile.mkdtemp())
    try:
        inpq = tmpdir / "records.parquet"
        outpq = tmpdir / "taxes.parquet"
        recs = pd.read_csv(records)
        recs.to_parquet(inpq, index=False)
        batch.main([
            "--records", str(inpq), "--year", str(year),
            "--out", str(outpq), "--commit", sha,
        ] + BATCH_OPTIONS)
        out = pd.read_parquet(outpq)
        if not np.array_equal(out.id.to_numpy(), recs.id.to_numpy()):
            raise ValueError("batch output ids differ from input ids")
        rates = hi_ee_rates(year)
        out[HI_EE_RATE] = rates[recs.filing_status.to_numpy(np.int64) - 1]
        out.to_csv(outfile, index=False)
        shutil.copyfile(f"{outpq}.manifest.json",
                        f"{outfile}.manifest.json")
    finally:
        shutil.rmtree(tmpdir)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("USAGE: python ts_batch.py RECORDS YEAR "
                         "OUTFILE SHA\n")
        sys.exit(1)
    sys.exit(main(*sys.argv[1:]))
