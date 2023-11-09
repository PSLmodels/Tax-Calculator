# Explanations of known differences between Tax-Calculator and TAXSIM-35

This document explains the sources of known differences (that exceed $1) between Tax-Calculator and TAXSIM-35.  Numerical differences are noted in the {letter}{year}-taxdiffs-actual.csv files in this directory.

## 2017
* No differences greater than $1 (though one obs with an marginal tax rate differences of 7.65 percent)

## 2018
* No differences greater than $1.


## 2019
* There is one record in the "a" file with a difference in the EITC amount of $196.22.  This record is of a single, 19 year old filer.  This person is below the age of 25 and therefore should receive $0 EITC, which is what Tax-Calculator reports.  TAXSIM-35 does not recognize this age threshold and incorrectly assigns this person $196.22 in EITC.
* The same record has a marginal tax rate difference of 7.65 percent, which is the phase in rate for the EITC and thus related to the above issue.

## 2020
* Numerous records in the test files with differences in the recorvery rebate credit amount (RRC). The reasons TAXSIM-35 shows different results vary and include: TAXSIM-35 not counting qualifying children (e.g., file "a", id 7);  TAXSIM-35 not differentiating single/head of household filing status (e.g., file "a",id 31); and TAXSIM-35 not counting Economic Impat Payment 2 (e.g., file "a",id 33); TAXSIM-35 counts wrong number of child (e.g., file "a",id 59). Note that some of these are not errors per se, but can be related to different variable inputs in the two models.


## 2021
* In 2021, the Additional Child Tax Credit (ACTC), which historically was the refundable portion of the CTC, was subsumbed by the refundability of the CTC more broadly with the ARPA. Tax-Calculator and TAXSIM-35 handle this differnetly in their model output.  Tax-Calculator keeps only the ACTC amount in the variable `c11070`, which is $0 for all filers in 2021.  On the other hand, TAXSIM-35 reports the refundable amount of the CTC (whih is equivalent to the ACTC in most years, but not 2021).  Hence, we can expect differences in these two models due to different definitions of output variables in that year.  The file `process_taxcalc_output.py` makes and adjustment for 2021 to make the output from both models more comparable.