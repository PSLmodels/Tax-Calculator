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
[PR #749](https://github.com/open-source-economics/Tax-Calculator/pull/749) helpful.


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


Odd Marginal Tax Rate
==============

The Tax-Calculator offers the approximation of units' marginal tax rates (MTRs) using 
finite difference, where a small increase will be added to some specified income
type. For more details, you might find the [code lines](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/calculate.py#L174-L228) here helpful. 

During the course of testing the Tax-Calculator, we found that, under some circumstances,
filing units could end up having rather high (over 50%) MTRs. This means that, surprisingly,
more than 50% of those units' extra income will contribute to their tax liabilities.
There are, based on our current findings, two possible reasons that would result in 
such high MTR situation. 

The first case is that, when some unit has foreign tax credit (FTC), such credit can 
possibly wipe out the income tax liability, which plays as an offsetting force 
in the alternative minimum tax (AMT) calculation. Filing units with enough FTC that 
wipes out the income tax liability in the AMT calculation will need to take care
of more tax burden when given some extra income. More explicitly, we use the following
table to generalize such situation:

| |   Base                |     Base, Added a penny    |
| :-------------: |  :-------------: | :-------------: |
| Adjusted Gross Income |AGI         |AGI + 0.01|
| Standard Deduction    |      STD   |    STD |
| Taxable Income    |    AGI - STD   |   AGI - STD +0.01 |
| Income Tax    |     intax          |   intax + delta |
| Foreign Tax Credit    |  |FTC      |FTC  |
| AMTI | AGI                         |AGI + 0.01|
| Tentative Minimum Tax| TMT         | TMT + less_delta|
| AMT| TMT                           | TMT + less_delta|
| Tax Before Credits | TMT + intax   | TMT + less_delta + intax + delta|

Notice that, in this example, we have `intax + delta < FTC` so that FTC would 
wipe out the income tax, which should have neutralized the tentative minimum tax
if the inequality does not hold. Also, `delta > less_delta > 0` since, in brief, 
the `less_delta` is generated by more iterations in the tax form than `delta`,
and thus is less significant. 



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

