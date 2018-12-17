Validation of Tax-Calculator against Internet TAXSIM version 27
===============================================================

The general cross-model validation process described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)
is being executed in this directory using
[TAXSIM-27](https://users.nber.org/~taxsim/taxsim27/).

We are in the process of comparing Tax-Calculator and TAXSIM-27
results generated from several assumption sets in the `taxsim_in.py`
script for selected years beginning with 2013.  Each INPUT file is
used to generate a TAXSIM-27 OUTPUT file by uploading it to the
TAXSIM-27 website and requesting detailed intermediate calculations.
And each INPUT file is translated into a CSV-formatted input file that
is read by the Tax-Calculator `tc` CLI tool to generate output that is
then transformed into an OUTPUT file having the TAXSIM-27 format.
Finally, these two OUTPUT files are compared using the `taxdiffs.tcl`
script.  See the `test.sh` scripts in this directory for more details.

The following results are for INPUT files containing 100,000
randomly-generated filing units for a given year.  The random sampling
is such that a different sample is drawn for each year.  In each INPUT
file three state-related variables are set to zero for every filing
unit, one variable specifies the year, and another specifies an filing
unit id, which leaves twenty-two input variables that are set to
randomly-generated values.

In order to handle known differences in assumptions between the two
models, we use the `taxsim_emulation.json` "reform" file to make
Tax-Calculator operate like TAXSIM-27.  See the
[`taxsim_emulation.json`
file](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim/taxsim_emulation.json)
for details.

In the following results, when we say "same results" we mean that the
federal individual income tax liabilities and payroll tax liabilities
being compared have differences of no larger than one cent.

Validation Results
------------------

**2018-12-17** : Same results for a 2017 INPUT file that specifies
the first twelve of the TAXSIM-27 input variables, which
include demographic variables and labor income, but set to zero all
the TAXSIM-27 input variables numbered from 13 through 27. (This is
the a17 assumption set.)

**2018-12-17** : Same results for a 2017 INPUT file that specifies the
first twenty-one of the TAXSIM-27 input variables, which include
demographic variables, labor income, capital income, and
federally-taxable benefits, but set to zero all the other six
TAXSIM-27 input variables.  Two of those six are always set to zero
because they specify trasfer income that is not taxed under the
federal income tax or because they specify rent paid that does not
affect federal income tax liability.  Three of the remaining four
input variables are itemized expense amounts and the fourth is
child-care expenses. (This is the b17 assumption set.)

**2018-12-17** : Same results for a 2017 INPUT file that specifies all
the non-state TAXSIM-27 input variables to be randomly generated
values.  (This is the c17 assumption set.)
