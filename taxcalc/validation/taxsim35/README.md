Validation of Tax-Calculator against Internet TAXSIM-35
=======================================================

The general cross-model validation process described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)
is being executed in this directory using
[TAXSIM-35](https://taxsim.nber.org/taxsim35/).

We are in the process of comparing Tax-Calculator and TAXSIM-35
results generated from several assumption sets in the `taxsim_input.py`
script for years beginning with 2018. Each INPUT file is
used to generate a TAXSIM-35 OUTPUT file by uploading it to the
TAXSIM-35 website and requesting detailed intermediate calculations.
And each INPUT file is translated into a CSV-formatted input file that
is read by the Tax-Calculator `tc` CLI tool to generate output that is
then transformed into an OUTPUT file having the TAXSIM-35 format.
Finally, these two OUTPUT files are compared using the `main_comparison.py`
script. See the `tests_35.py` script in this directory for more details.

The following results are for INPUT files containing 100,000
randomly-generated filing units for a given year. The random sampling
is such that a different sample is drawn for each year. In each INPUT
file three state-related variables are set to zero for every filing
unit, one variable specifies the year, and another specifies a filing
unit id, which leaves twenty-two input variables that are set to
randomly-generated values.

In order to handle known differences in assumptions between the two
models, we use the `taxsim_emulation.json` "reform" file to make
Tax-Calculator operate like TAXSIM-35. See the
[`taxsim_emulation.json`
file](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim35/taxsim_emulation.json)
for details.

In the following results, when we say "same results" we mean that the
federal individual income tax liabilities and payroll tax liabilities
being compared have differences of no larger than one cent.

For information on the variable names illustrated in `taxsim_input.py`,
the document that generates data for input into TAXSIM-35, see the TAXSIM-35 website listed above.


Instructions
------------------
1. Navigate to `taxcalc/validation/taxsim35` and run the Python script `tests_35.py`.
2. If you would like to generate new input files and and get new files from TAXSIM-35,
just delete all of the `.in.out-taxsim` files. On Mac/Linux, this can be done with
`rm -f *.in.out-taxsim`.


Troubleshooting
------------------
If the TAXSIM-35 validation code throws errors such as `.in files not found`,
`.out files not found` or that any parameter within `policy_current_law.json`
does not exist, please try these 2 steps:

1. Make sure that the `taxcalc` conda package is installed
2. If you have Tax-Calculator downloaded locally, navigate to the root directory
and run `pip install -e .` This will install the current source code into the `taxcalc`
CLI.


Description of Randomly Generated Assumption Sets
------------------

**a18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twelve of the TAXSIM-35
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-35 input variables numbered from 13
through 27.

**b18 ASSUMPTION SET**:

2018 INPUT file that specifies the first twenty-one of the TAXSIM-35
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-35 input variables except variables 28-35,
which are the variables representing the new QBI-related variables.
Two of those six are always set to zero because they specify transfer income
that is not taxed under the federal income tax or because they specify rent paid that
does not affect federal income tax liability. Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses.


**c18 ASSUMPTION SET**:

2018 INPUT file that specifies all the non-state TAXSIM-35 input
variables to be randomly generated values.


**a19 ASSUMPTION SET**:

2019 INPUT file that specifies the first twelve of the TAXSIM-35
input variables, which include demographic variables and labor income,
but sets to zero all the TAXSIM-35 input variables numbered from 13
through 27. (This is the same logic as used to generate the **a17**
sample except that a different stream of random numbers is used so that
the 100,000 filing units are completely different.)


**b19 ASSUMPTION SET**:

2019 INPUT file that specifies the first twenty-one of the TAXSIM-35
input variables, which include demographic variables, labor income,
capital income, and federally-taxable benefits, but set to zero all
the other six TAXSIM-35 input variables except variables 28-35,
which are the variables representing the new QBI-related variables.
Two of those six are always set to zero because they specify transfer income
that is not taxed under the federal income tax or because they specify rent paid that
does not affect federal income tax liability. Three of the remaining
four input variables are itemized expense amounts and the fourth is
child-care expenses. (This is the same logic as used to generate the
**b17** sample except that a different stream of random numbers is
used so that the 1,000 filing units are completely different.)


**c19 ASSUMPTION SET**:

2019 INPUT file that specifies all the non-state TAXSIM-35 input
variables to be randomly generated values. (This is the same logic as
used to generate the **c17** sample except that a different stream of
random numbers is used so that the 100,000 filing units are completely
different.)


Validation Results
------------------

The latest expected differences between Tax-Calculator and TAXSIM-35 can be found in the `expected_differences` folder in this directory.

These differences are summarized and explained in the [`Differences_Explained`](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/taxsim35/Differences_Explained.md) markdown file.

Differences are generally small, although we note larger differences due to how Tax-Calculator and TAXSIM-35 handle the following items:
* The computation of SECA taxes
* The 2020 Recovery Rebate Credit and Economic Impact Payments
* The 2021 Child Tax Credit
* Itemized deductions