Common Validation Tools
=======================

This folder contains tools shared by more than one cross-model
validation workflow.

- `generate_sample.py` writes a random sample of filing units in
  TAXSIM-35 input format.  Its required `--workflow` option names the
  validation workflow that uses the sample (`pe_taxsim` or the planned
  `tbly_ts`), which sets the default output folder
  (`validation/WORKFLOW/samples`) and the default maximum number of
  dependents.  Use `python generate_sample.py --help` for details, and
  see [`../pe_taxsim/README.md`](../pe_taxsim/README.md) and
  [`../pe_taxsim/VARIABLES.md`](../pe_taxsim/VARIABLES.md) for how
  the samples are used and what their variables mean.
