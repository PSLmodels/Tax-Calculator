Validation of Tax-Calculator against Internet-TAXSIM
====================================================

The cross-model validation process described [here](../README.md) has used
[Internet-TAXSIM](http://users.nber.org/~taxsim/taxsim-calc9/index.html)
to generate step-three results.  

We are in the process of comparing Tax-Calculator and Internet-TAXSIM
results generated from the `a` and `d` assumption sets in the
`taxsim_in.tcl` script for the year 2015.  Each INPUT file is used to
generate a Tax-Calculator OUTPUT file using the `simtax.py` interface
to the Tax-Calculator with the `--taxsim2441` option.  And each INPUT
file is used to generate an Internet-TAXSIM OUTPUT file by uploading
it to the Internet-TAXSIM website using the `56 1` option (in order to
do the EITC property-income eligibility test exactly without any
smoothing of property income) and requesting detailed intermediate
calculations.  These two OUTPUT files are compared using the
`taxdiffs.tcl` script.  See the `tests` and `test` scripts in this
directory for more details.

Validation Results
------------------

Here is a summary of the cross-model validation results.

### 2015 `a` Sample ###

As of 07-Sep-2016, we have compared OUTPUT files for a 2015 `a` sample
of 100,000 randomly-generated filing units.  The payroll tax
liabilities and marginal payroll tax rates are exactly the same
(except for nine marginal payroll tax rates for filing units exactly
at the threshold of paying the Net Investment Income Tax, where the
marginal rate is not well defined).  The intermediate income tax
results are in close agreement with the largest difference being
slightly more that a dollar (except for three large differences in AMT
taxable income, which do not translate into differences in AMT
liability).  The largest difference in total income tax liability is
one cent in absolute value.  And there are no meaningful differences
in marginal income tax rates.  See the `a15.taxdiffs` file for details
on the differences.

### 2015 `d` Sample ###

As of 07-Sep-2016, we have compared OUTPUT files for a 2015 `d` sample
of 100,000 randomly-generated filing units.  Each filing unit in the
`d` sample has additional tax attributes beyond those present in the
`a` sample, including three kinds of itemized-deduction expenses,
child care expenses, and other property income.  The marginal tax
rates are essentially the same in the two OUTPUT files, the payroll
tax liabilities are exactly the same (down to the penny), and the
federal income tax liabilities are differnt by no more than one cent.
See the `d15.taxdiffs` file for details on the differences.
