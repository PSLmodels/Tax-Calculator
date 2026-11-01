Common Validation Tools
=======================

This folder contains tools shared by more than one cross-model
validation workflow.

- `generate_sample.py` writes a random sample of filing units in
  TAXSIM-35 input format.  Its required `--workflow` option names the
  validation workflow that uses the sample (`pe_taxsim` or the planned
  `tbly_ts`), which sets the default output folder
  (`validation/WORKFLOW/samples`), the default year range (2021-2025
  for `pe_taxsim` and 2023-2025 for `tbly_ts`), and the default maximum
  number of dependents.  Its `--all` option, used in place of the
  `LETTER` and `YEAR` arguments, writes a sample for every
  assumption-set letter and every year in the workflow's default
  year range.  Use `python generate_sample.py --help` for
  details, and see [`../pe_taxsim/README.md`](../pe_taxsim/README.md) and
  [`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md) for how
  the samples are used and what their variables mean.

- `workflows.py` defines each workflow's settings (the other model's
  label, such as `pe` or `ts`, the default year range, the default
  maximum number of dependents, and the pin file), which the other
  scripts in this folder use.

- `taxsim_to_tc.py`, `run_tc.py`, and `compare.py` are validation
  steps 3-5, which do not depend on which model produced the
  TAXSIM-format output.  Each takes `LETTER YEAR --workflow WORKFLOW`
  and works in the `validation/WORKFLOW` folder by default:
  `taxsim_to_tc.py` translates `samples/LYY.in.csv.gz` into the
  Tax-Calculator input file `work/LYY.in-tc.csv`; `run_tc.py` runs
  the Tax-Calculator CLI with the workflow's emulation reform
  (`M_emulation.json`, where `M` is the other model's label) and the
  variables in `dumpvars.txt`, and writes the TAXSIM-format output
  `work/LYY.out-tc.csv`; and `compare.py` compares
  `M_output/LYY.out-M.csv.gz` with it, writing the differences to
  `work/differences/`.  The variable translations are documented in
  [`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md).

- `validation.py` runs the steps for each letter and year; it is
  called by the `validate.py` script in each workflow folder, which
  is the command to use (see `python validate.py --help`).
