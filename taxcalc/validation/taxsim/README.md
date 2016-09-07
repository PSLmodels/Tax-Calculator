Validation of Tax-Calculator against Internet-TAXSIM
====================================================

The cross-model validation process described [here](../README.md) has used
[Internet-TAXSIM](http://users.nber.org/~taxsim/taxsim-calc9/index.html)
to generate step-three results.  

We are in the process of comparing Tax-Calculator and Internet-TAXSIM
results generated from the `a`, `b`, `c`, and `d`, assumption sets in
the `make_in.tcl` script for the years 2013 through 2015.  Each INPUT
file is used to generate a Tax-Calculator OUTPUT file using the
`simtax.py` interface to the Tax-Calculator.  And each INPUT file is
used to generate an Internet-TAXSIM OUTPUT file by uploading it to the
Internet-TAXSIM website using the `56 1` option (in order to do the
EITC property-income eligibility test exactly without any smoothing of
property income) and requesting detailed intermediate calculations.
These two OUTPUT files are compared using the `taxdiffs.tcl` script.
See the `tests` and `test` scripts in this directory for more details.

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
slightly more that a dollar (except for some large differences in AMT
taxable income, which do not translate into differences in AMT
liability).  The largest difference in total income tax liability is
five cents in absolute value.  There are, however, large differences
in a few marginal income tax rates, which will be investigated in the
future.  See the `a15.taxdiffs` file for details on the differences.
