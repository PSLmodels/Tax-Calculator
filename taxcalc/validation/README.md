Validation of Tax-Calculator Logic
==================================

Tax-Calculator computes USA federal income and payroll taxes for
samples of tax filing units.  Besides its unit tests and comparisons
with hand calculations based on IRS forms and instructions,
Tax-Calculator is validated by cross-model comparison: the same
randomly generated filing units are run through Tax-Calculator and
through an independently developed tax model, and the results are
compared.  Two independently developed models are unlikely to contain
the same bug, so each difference is investigated until it is either
fixed or explained.

Current cross-model validation
------------------------------

Tax-Calculator's federal income and payroll tax results are
currently compared with those of two other models:

- [policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim),
  a TAXSIM-35 emulator built on `policyengine-us`, for 2021 through
  2025, in the [`pe_taxsim`](pe_taxsim/README.md) folder; and
- the Budget Lab at Yale's
  [Tax-Simulator](https://github.com/Budget-Lab-Yale/Tax-Simulator)
  for 2023 through 2025, in the [`tbly_ts`](tbly_ts/README.md) folder.

Each folder contains the tools, inputs, expected differences, and
instructions for rerunning its comparison; `make valtest` reruns both
comparisons.

Tools shared by more than one validation workflow, such as the
script that generates the random samples of filing units, are in the
[`common`](common/README.md) folder.

A historical record of the earlier validation against NBER's Internet
TAXSIM-35 (2017-2021) is in the [`taxsim35`](taxsim35/README.md)
folder; the code used to run that validation is in this repository's
git history.
