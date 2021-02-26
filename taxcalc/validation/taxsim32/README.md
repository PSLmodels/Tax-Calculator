Validation of Tax-Calculator against Internet TAXSIM-32
=======================================================

The general cross-model validation process described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)
is being executed in this directory using
[TAXSIM-32](https://users.nber.org/~taxsim/taxsim27/).

We are in the process of comparing Tax-Calculator and TAXSIM-32
results generated from several assumption sets in the `taxsim_input.py`
script for years beginning with 2018. Each INPUT file is
used to generate a TAXSIM-32 OUTPUT file by uploading it to the
TAXSIM-32 website and requesting detailed intermediate calculations.
And each INPUT file is translated into a CSV-formatted input file that
is read by the Tax-Calculator `tc` CLI tool to generate output that is
then transformed into an OUTPUT file having the TAXSIM-32 format.
Finally, these two OUTPUT files are compared using the `main_comparison.py`
script. See the `tests_32.py` script in this directory for more details.

The following results are for INPUT files containing 100,000
randomly-generated filing units for a given year. The random sampling
is such that a different sample is drawn for each year. In each INPUT
file three state-related variables are set to zero for every filing
unit, one variable specifies the year, and another specifies a filing
unit id, which leaves twenty-two input variables that are set to
randomly-generated values.

In order to handle known differences in assumptions between the two
models, we use the `taxsim_emulation.json` "reform" file to make
Tax-Calculator operate like TAXSIM-32. See the
[`taxsim_emulation.json`
file](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim32/taxsim_emulation.json)
for details.

In the following results, when we say "same results" we mean that the
federal individual income tax liabilities and payroll tax liabilities
being compared have differences of no larger than one cent.

For information on the variable names illustrated in `taxsim_input.py`,
the document that generates data for input into TAXSIM-32, see the TAXSIM-32 website listed above.


Instructions
------------------
1. Navigate to `taxcalc/validation/taxsim32` and run the Python script `tests_32.py`.
2. If you would like to generate new input files and and get new files from TAXSIM-32,
just delete all of the `.in.out-taxsim` files. On Mac/Linux, this can be done with
`rm -f *.in.out-taxsim`.


Troubleshooting
------------------
If the TAXSIM-32 validation code throws errors such as `.in files not found`,
`.out files not found` or that any parameter within `policy_current_law.json`
does not exist, please try these 2 steps:

1. Make sure that the `taxcalc` conda package is installed
2. If you have Tax-Calculator downloaded locally, navigate to the root directory
and run `pip install -e .` This will install the current source code into the `taxcalc`
CLI.


Validation Results
------------------

**a18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twelve of the TAXSIM-32
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-32 input variables numbered from 13
through 27.

Validation results using the then current-version of TAXSIM-32 on these dates:

**b18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twenty-one of the TAXSIM-32
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-32 input variables except variables 28-32,
which are the variables representing the new QBI-related variables.
Two of those six are always set to zero because they specify transfer income
that is not taxed under the federal income tax or because they specify rent paid that
does not affect federal income tax liability. Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses.

Validation results using the then current-version of TAXSIM-32 on these dates:

**c18 ASSUMPTION SET**:

2018 INPUT file that specifies all the non-state TAXSIM-32 input
variables to be randomly generated values.

Validation results using the then current-version of TAXSIM-32 on these dates:

**a19 ASSUMPTION SET**:

2019 INPUT file that specifies the first twelve of the TAXSIM-32
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-32 input variables numbered from 13
through 27. (This is the same logic as used to generate the **a17**
sample except that a different stream of random numbers is used so that
the 100,000 filing units are completely different.)

Validation results using the then current-version of TAXSIM-32 on these dates:

**b19 ASSUMPTION SET**:

2019 INPUT file that specifies the first twenty-one of the TAXSIM-32
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-32 input variables except variables 28-32,
which are the variables representing the new QBI-related variables.
Two of those six are always set to zero because they specify transfer income
that is not taxed under the federal income tax or because they specify rent paid that
does not affect federal income tax liability. Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses. (This is the same logic as used to generate the
**b17** sample except that a different stream of random numbers is
used so that the 100,000 filing units are completely different.)

Validation results using the then current-version of TAXSIM-32 on these dates:

**c19 ASSUMPTION SET**:

2019 INPUT file that specifies all the non-state TAXSIM-32 input
variables to be randomly generated values. (This is the same logic as
used to generate the **c17** sample except that a different stream of
random numbers is used so that the 100,000 filing units are completely
different.)

Validation results using the then current-version of TAXSIM-32 on these dates:
