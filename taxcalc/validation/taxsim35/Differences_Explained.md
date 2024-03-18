# Explanations of known differences between Tax-Calculator and TAXSIM-35

This document explains the sources of known differences (that exceed $1) between Tax-Calculator and TAXSIM-35.  Numerical differences are noted in the {letter}{year}-taxdiffs-actual.csv files in this directory.

## `a` files:
### 2017

* No differences greater than $1 (though one obs with an marginal tax rate differences of 7.65 percent)

### 2018

* No differences greater than $1.


### 2019

* There is one record in the "a" file with a difference in the EITC amount of $196.22.  This record is of a single, 19 year old filer.  This person is below the age of 25 and therefore should receive $0 EITC, which is what Tax-Calculator reports.  TAXSIM-35 does not recognize this age threshold and incorrectly assigns this person $196.22 in EITC.
* The same record has a marginal tax rate difference of 7.65 percent, which is the phase in rate for the EITC and thus related to the above issue.

### 2020

* Numerous records in the test files with differences in the recovery rebate credit amount (RRC). The reasons TAXSIM-35 shows different results vary and include: TAXSIM-35 not counting qualifying children (e.g., file "a", id 7);  TAXSIM-35 not differentiating single/head of household filing status (e.g., file "a",id 31); and TAXSIM-35 not counting Economic Impact Payment 2 (e.g., file "a",id 33); TAXSIM-35 counts wrong number of child (e.g., file "a",id 59). Note that some of these are not errors per se, but can be related to different variable inputs in the two models.

### 2021

* In 2021, the Additional Child Tax Credit (ACTC), which historically was the refundable portion of the CTC, was subsumed by the refundability of the CTC more broadly with the ARPA. Tax-Calculator and TAXSIM-35 handle this differently in their model output.  Tax-Calculator keeps only the ACTC amount in the variable `c11070`, which is $0 for all filers in 2021.  On the other hand, TAXSIM-35 reports the refundable amount of the CTC (which is equivalent to the ACTC in most years, but not 2021).  Hence, we can expect differences in these two models due to different definitions of output variables in that year.  The file `process_taxcalc_output.py` makes and adjustment for 2021 to make the output from both models more comparable.

## `b` files:

The following are notes that explain differences in addition to those documented above for the `a` files.

### All years

* Differences in AGI between TAXMSIM and Tax-Calculator have to do with an incorrect calculation of the SECA tax liability in TAXSIM-35.  Half of the SECA tax amount is deductible from AGI on individuals' returns.
* TAXSIM-35 does not correctly calculate payroll tax liability, while Tax-Calculator calculations have been verified manually. Thus, payroll tax liability differs between the two models.  An updated version of TAXSIM (not available publicaly on 2024-02-29) shows not differences in FICA liability with Tax-Calculator.
* The AMT liability is zero in TAXSIM-35, but correct in Tax-Calculator, thus the AMT liability difference is the AMT liability in Tax-Calculator.
* Other differences (in `c04800`, `taxbc`, `c62100`, and `iitax_before_credits_ex_AMT`) are due to downstream effects of the differences documented above.

### 2020

* Three records in the test files with differences in the recovery rebate credit amount (RRC). The reasons TAXSIM-35 shows different results vary and include: TAXSIM-35 not counting qualifying children (e.g., file "a", id 7);  TAXSIM-35 not differentiating single/head of household filing status (e.g., file "a",id 31); and TAXSIM-35 not counting Economic Impact Payment 2 (e.g., file "a",id 33); TAXSIM-35 counts wrong number of child (e.g., file "a",id 59). Note that some of these are not errors per se, but can be related to different variable inputs in the two models.
* There is also a single record with a differences in `e02300`, unemployment insurance benefits, and input to the models.  This variable is zeroed out in TAXSIM-35, but not in Tax-Calculator.

## `c` files:

The following are notes that explain differences in addition to those documented above for the `b` files.

### All years

* The `c` file set is the only one that simulates itemized deduction amounts. We have documented differences in `c04470` in all years of the `c` files. In the version of TAXSIM-35 we are using, the itemized deduction is always returned as zero. Hand calculations have confirmed Tax-Calculator's itemized deduction amounts are correct.

### 2017

* There are differences in variable `c21040`, itemized deductions that are phased out.  This only affects the `c` set as itemized deductions are not included in records in the `a` and `b` sets.  Further, tax law only has a phase out of itemized deductions in 2017 and earlier, hence no affect on later years.  The root source of the error is the known differences in the handling of itemized deductions between TAXSIM-35 and Tax-Calculator noted above.