Validation of Tax-Calculator against Internet TAXSIM-27
=======================================================

The general cross-model validation process described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)
is being executed in this directory using
[TAXSIM-27](https://users.nber.org/~taxsim/taxsim27/).

We are in the process of comparing Tax-Calculator and TAXSIM-27
results generated from several assumption sets in the `taxsim_in.py`
script for years beginning with 2017.  Each INPUT file is
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
unit, one variable specifies the year, and another specifies a filing
unit id, which leaves twenty-two input variables that are set to
randomly-generated values.

In order to handle known differences in assumptions between the two
models, we use the `taxsim_emulation.json` "reform" file to make
Tax-Calculator operate like TAXSIM-27.  See the
[`taxsim_emulation.json`
file](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim27/taxsim_emulation.json)
for details.

In the following results, when we say "same results" we mean that the
federal individual income tax liabilities and payroll tax liabilities
being compared have differences of no larger than one cent.


Instructions
------------------

1. Use `taxsim_input.py` to create the `.in` files necessary to input into TAXSIM-27.
2. Head to the [TAXSIM-27 website](http://users.nber.org/~taxsim/taxsim27/) and under _Upload a file_, place each of the `.in` files in and save the outputs as `LYY.in.out-taxsim`. When you run the TAXSIM-27 simulation, make sure to switch _Show detailed intermediate calculations_ to _on_.
3. Open each of these `.in.out-taxsim` files and remove the first few lines containing the variable names.
4. Compress these files into a `.zip` file called `output-taxsim.zip`.
	- Make sure the `.in.out-taxsim` files have no (possibly hidden) extra extension attached to them, e.x. `.txt`.
	- Select all of the `.in.out-taxsim` files and compress those into `output-taxsim.zip`. **Do not** place these files into a new folder and compress that folder.
5. Navigate to `taxcalc/validation` and run `tests.sh`.


Validation Results
------------------

**a17 ASSUMPTION SET**:

2017 INPUT file that specifies the first twelve of the TAXSIM-27
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-27 input variables numbered from 13
through 27.

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2018-12-17 : same results
2. 2019-01-29 : same results
3. 2019-03-30 : same results
4. 2019-06-05 : same results

**b17 ASSUMPTION SET**:

2017 INPUT file that specifies the first twenty-one of the TAXSIM-27
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-27 input variables.  Two of those six are always
set to zero because they specify trasfer income that is not taxed
under the federal income tax or because they specify rent paid that
does not affect federal income tax liability.  Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses.

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2018-12-17 : same results
2. 2019-01-29 : same results
3. 2019-03-30 : same results
4. 2019-06-05 : same results

**c17 ASSUMPTION SET**:

2017 INPUT file that specifies all the non-state TAXSIM-27 input
variables to be randomly generated values.

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2018-12-17 : same results
2. 2019-01-29 : same results
3. 2019-03-30 : same results
4. 2019-06-05 : same results

**a18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twelve of the TAXSIM-27
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-27 input variables numbered from 13
through 27.  (This is the same logic as used to generate the **a17**
sample except that a different stream of random numbers is used so that
the 100,000 filing units are completely different.)

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2019-01-29 : same results (other dependent credit not included in ovar 22)
2. 2019-03-30 : same results (other dependent credit now included in ovar 22)
3. 2019-06-05 : same results (other dependent credit now included in ovar 22)

**b18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twenty-one of the TAXSIM-27
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-27 input variables.  Two of those six are always
set to zero because they specify trasfer income that is not taxed
under the federal income tax or because they specify rent paid that
does not affect federal income tax liability.  Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses.  (This is the same logic as used to generate the
**b17** sample except that a different stream of random numbers is
used so that the 100,000 filing units are completely different.)

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2019-03-30 : same results except for 422 itax diffs with largest being $13.00
2. 2019-06-05 : same results (other dependent credit now included in ovar 22)

**c18 ASSUMPTION SET**:

2018 INPUT file that specifies all the non-state TAXSIM-27 input
variables to be randomly generated values.  (This is the same logic as
used to generate the **c17** sample except that a different stream of
random numbers is used so that the 100,000 filing units are completely
different.)

Validation results using the then current-version of TAXSIM-27 on these dates:
1. 2019-03-30 : same results except for 327 itax diffs with largest being $13.00
2. 2019-06-05 : same results (other dependent credit now included in ovar 22)