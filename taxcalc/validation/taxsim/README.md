Validation of Tax-Calculator against Internet TAXSIM version 27
===============================================================

The general cross-model validation process described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)
is being executed in this directory using
[TAXSIM-27](https://users.nber.org/~taxsim/taxsim27/).

We are in the process of comparing Tax-Calculator and TAXSIM-27
results generated from several assumption sets in the `taxsim_in.py`
script for years beginning with 2015.  Each INPUT file is used to
generate a TAXSIM-27 OUTPUT file by uploading it to the TAXSIM-27
website and requesting detailed intermediate calculations.  And each
INPUT file is translated into a CSV-formatted input file that is read
by the Tax-Calculator `tc.py` tool to generate output that is then
transformed into an OUTPUT file having the TAXSIM-27 format.  Finally,
these two OUTPUT files are compared using the `taxdiffs.tcl` script.
See the `tests.sh` and `test.sh` scripts in this directory for more
details.

Validation Results
------------------

...
