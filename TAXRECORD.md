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
where all units listed are artificially made-up. 