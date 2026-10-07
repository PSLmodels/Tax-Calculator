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

The current validation compares Tax-Calculator's federal income and
payroll tax results for 2021 through 2025 with those of
[policyengine-taxsim](https://github.com/PolicyEngine/policyengine-taxsim),
a TAXSIM-35 emulator built on `policyengine-us`.  The tools, inputs,
expected differences, and instructions for rerunning the comparison
are in the [`pe_taxsim`](pe_taxsim/README.md) folder.

Earlier validation against NBER's Internet TAXSIM-35 (2017-2021) is
in this repository's git history, in the `taxcalc/validation/taxsim35`
folder.
