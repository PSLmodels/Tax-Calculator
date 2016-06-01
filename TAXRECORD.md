Tax Records
==============

The Tax-Calculator is capable of dealing with large amounts of input data, 
so long as each filing unit has variable names that are in the 
`VALID_READ_VARS` set in the
[records.py file](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/records.py). 
More details about the data input requirement can be found here in the 
[DATAPREP.md file](https://github.com/open-source-economics/Tax-Calculator/blob/master/DATAPREP.md). 

Thanks to such capability, we are able to test the current tax logic with as many 
'extreme' units as we want, and thus are able to find a couple tax units that 
are considered counter-intuitive against common sense. For instance, if allowed 
by the tax law, some unit should get better-off in terms of individual income 
tax liability when that person choose to have no deduction, or zero deduction amount.

This document stores units that would yield counter-intuitive results we have found, 
where all units listed are artificially made-up. During make-up process, we try to
use as few variables as possible so that our units will end up being rather simple. 
Adding more (valid) variables to those units, however, usually will not affect the 
counter-intuitive case we are trying to explain.


Optimization Puzzle
==============

Generally speaking, we take it for granted that filing units will end up being 
better-off when they choose the higher deduction amount among either standard 
deduction or itemized deduction. The unit we described in this section, however, 
should yield a lower tax liability when he/she choose to have a lower deduction amount.

The reason that accounts for this phenomenon is that: when choosing to have no deduction,
although this unit will pay higher regular tax, or '_taxbc', comparing 
to regular scenario that has deduction amount, his/her AMT tax liability will
end up being much lower. And thus this yields a comparatively lower individual 
income tax liability. To be more specific,
choosing no deduction amount will result in higher taxable income, this higher 
income will come into play in the AMT calculation (which is essentially 
introduced from Schedule D Tax Worksheet for form 1040) as an offsetting force, that 
eventually diminishes the AMT liability. That said, in these two cases, 
the difference for AMT part is larger than the difference resulting from 
'_taxbc' variable, in terms of absolute value, and thus this unit has lower 
individual income tax liability.

To replicate this phenomenon, the following unit needs to be fed through the 
Tax-Calculator with 2013 tax logic, without any extrapolation/blowup for the 
data input. Also, to allow units having zero deduction, you shall suppress all
the itemized deduction items. To do all these, you might find 
[PR #749](https://github.com/open-source-economics/Tax-Calculator/pull/749).


| Variable      | Value       |
|:-------------:|:-----------:|
| FLPDYR        | 2013        |
| MARS          | 2           | 
| e00300        | 14300       | 
| e00900        | 175000      |
| e02000        | -1795000    | 
| e03270        | 20000       | 
| e18400        | 40000       |
| e18500        | 2700        | 
| e19200        | 15700       | 
| e19700        | 3200        |
| p23250        | 4580000     | 
| e24515        | 2090000     | 