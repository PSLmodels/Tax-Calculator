Policy parameters
=================

This section contains documentation of policy parameters in a format that is
easy to search and print.
The policy parameters are grouped here as they are are in the
[Tax-Brain webapp](https://www.compute.studio/PSLmodels/Tax-Brain/).
Parameters understood by Tax-Calculator and the `tc` CLI,
but not available on Tax-Brain,
are placed in an Other Parameters group at the end of the section.


## Parameter Indexing

### Offsets

####  `parameter_indexing_CPI_offset`  
_Description:_ Values are zero before 2017; reforms that introduce indexing with chained CPI would have values around -0.0025 beginning in the year before the first year policy parameters will have values computed with chained CPI.  
_Notes:_ See April 2013 CBO report entitled 'What Would Be the Effect on the Deficit of Using the Chained CPI to Index Benefit Programs and the Tax Code?', which includes this: 'The chained CPI grows more slowly than the traditional CPI does: an average of about 0.25 percentage points more slowly per year over the past decade.' <https://www.cbo.gov/publication/44089>  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: -0.0025  
2018: -0.0025  
2019: -0.0025  
2020: -0.0025  
2021: -0.0025  
2022: -0.0025  
2023: -0.0025  
2024: -0.0025  
2025: -0.0025  
2026: -0.0025  
_Valid Range:_ min = -0.005 and max = 0.005  
_Out-of-Range Action:_ error  


## Payroll Taxes

### Additional Medicare FICA

####  `AMEDT_ec`  
_Description:_ The Additional Medicare Tax rate, AMEDT_rt, applies to all earnings in excess of this excluded amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2014: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2015: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2016: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2017: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2018: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2019: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMEDT_rt`  
_Description:_ This is the rate applied to the portion of Medicare wages, RRTA compensation and self-employment income exceeding the Additional Medicare Tax earning exclusion.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.009  
2014: 0.009  
2015: 0.009  
2016: 0.009  
2017: 0.009  
2018: 0.009  
2019: 0.009  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Medicare FICA

####  `FICA_mc_trt`  
_Description:_ Medicare FICA rate, including both employer and employee.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.029  
2014: 0.029  
2015: 0.029  
2016: 0.029  
2017: 0.029  
2018: 0.029  
2019: 0.029  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Social Security FICA

####  `FICA_ss_trt`  
_Description:_ Social Security FICA rate, including both employer and employee.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.124  
2014: 0.124  
2015: 0.124  
2016: 0.124  
2017: 0.124  
2018: 0.124  
2019: 0.124  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `SS_Earnings_c`  
_Description:_ Individual earnings below this amount are subjected to Social Security (OASDI) payroll tax.  
_Notes:_ This parameter is indexed by the rate of growth in average wages, not by the price inflation rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 113700.0  
2014: 117000.0  
2015: 118500.0  
2016: 118500.0  
2017: 127200.0  
2018: 128400.0  
2019: 132900.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `SS_Earnings_thd`  
_Description:_ Individual earnings above this threshold are subjected to Social Security (OASDI) payroll tax, in addition to earnings below the maximum taxable earnings threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


## Social Security Taxability

### Threshold For Social Security Benefit Taxability 1

####  `SS_thd50`  
_Description:_ The first threshold for Social Security benefit taxability: if taxpayers have provisional income greater than this threshold, up to 50% of their Social Security benefit will be subject to tax under current law.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2014: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2015: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2016: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2017: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2018: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2019: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
_Valid Range:_ min = 0 and max = SS_thd85  
_Out-of-Range Action:_ error  


### Threshold For Social Security Benefit Taxability 2

####  `SS_thd85`  
_Description:_ The second threshold for Social Security taxability: if taxpayers have provisional income greater than this threshold, up to 85% of their Social Security benefit will be subject to tax under current law.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2014: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2015: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2016: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2017: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2018: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2019: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
_Valid Range:_ min = SS_thd50 and max = 9e+99  
_Out-of-Range Action:_ error  


## Above The Line Deductions

### Child And Elderly Care

####  `ALD_Dependents_hc`  
_Description:_ This decimal fraction, if greater than zero, reduces the portion of childcare costs that can be deducted from AGI.  
_Notes:_ The final adjustment would be (1-Haircut)*AverageChildcareCosts.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_Dependents_Child_c`  
_Description:_ The weighted average of childcare costs in the US. 7165 is the weighted average from the 'Child Care in America: 2016 State Fact Sheets'.  
_Notes:_ This is a weighted average of childcare costs in each state  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ALD_Dependents_Elder_c`  
_Description:_ A taxpayer can take an above the line deduction up to this amount if they have an elderly dependent. The Trump 2016 campaign proposal was for $5000.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ALD_Dependents_thd`  
_Description:_ A taxpayer can only claim the dependent care deduction if their total income is below this level. The Trump 2016 campaign proposal was for 250000 single, 500000 joint, 250000 separate, 500000 head of household].  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Misc. Adjustment Haircuts

####  `ALD_StudentLoan_hc`  
_Description:_ This decimal fraction can be applied to limit the student loan interest adjustment allowed.  
_Notes:_ The final adjustment amount will be (1-Haircut)*StudentLoanInterest.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_SelfEmploymentTax_hc`  
_Description:_ This decimal fraction, if greater than zero, reduces the employer equivalent portion of self-employment adjustment.  
_Notes:_ The final adjustment amount would be (1-Haircut)*SelfEmploymentTaxAdjustment.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_SelfEmp_HealthIns_hc`  
_Description:_ This decimal fraction, if greater than zero, reduces the health insurance adjustment for self-employed taxpayers.  
_Notes:_ The final adjustment amount would be (1-Haircut)*SelfEmployedHealthInsuranceAdjustment.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_KEOGH_SEP_hc`  
_Description:_ Under current law, contributions to Keogh or SEP plans can be fully deducted from gross income.  This haircut can be used to limit the adjustment allowed.  
_Notes:_ The final adjustment amount is (1-Haircut)*KEOGH_SEP_Contributinos.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_EarlyWithdraw_hc`  
_Description:_ Under current law, early withdraw penalty can be fully deducted from gross income. This haircut can be used to limit the adjustment allowed.  
_Notes:_ The final adjustment amount is (1-Haircut)*EarlyWithdrawPenalty.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_AlimonyPaid_hc`  
_Description:_ Under pre-TCJA law, the full amount of alimony paid is taken as an adjustment from gross income in arriving at AGI. This haircut can be used to change the deduction allowed.  
_Notes:_ The final adjustment amount would be (1-Haircut)*AlimonyPaid.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_AlimonyReceived_hc`  
_Description:_ Under pre-TCJA law, none of alimony received is taken as an adjustment from gross income in arriving at AGI. This haircut can be used to change the deduction allowed.  
_Notes:_ The final adjustment amount would be (1-Haircut)*AlimonyReceived.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_EducatorExpenses_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of educator expenses that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*EducatorExpenses.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_HSADeduction_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of a taxpayer's HSA deduction that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*HSA_Deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_IRAContributions_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of IRA contributions that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*IRA_Contribution.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_DomesticProduction_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of domestic production activity that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*DomesticProductionActivity.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_Tuition_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of tuition and fees that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*TuitionFees.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Misc. Exclusions

####  `ALD_InvInc_ec_rt`  
_Description:_ Decimal fraction of investment income base that can be excluded from AGI.  
_Notes:_ The final taxable investment income will be (1-_ALD_InvInc_ec_rt)*investment_income_base. Even though the excluded portion of investment income is not included in AGI, it still is included in investment income used to calculate the Net Investment Income Tax and Earned Income Tax Credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ALD_BusinessLosses_c`  
_Description:_ Business losses in excess of this amount may not be deducted from AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [250000.0, 500000.0, 250000.0, 250000.0, 500000.0]  
2019: [255000.0, 510000.0, 255000.0, 255000.0, 510000.0]  
2020: [258927.0, 517854.0, 258927.0, 258927.0, 517854.0]  
2021: [260817.17, 521634.33, 260817.17, 260817.17, 521634.33]  
2022: [263294.93, 526589.86, 263294.93, 263294.93, 526589.86]  
2023: [267454.99, 534909.98, 267454.99, 267454.99, 534909.98]  
2024: [272616.87, 545233.74, 272616.87, 272616.87, 545233.74]  
2025: [278069.21, 556138.41, 278069.21, 278069.21, 556138.41]  
2026: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


## Personal Exemptions

### Personal And Dependent Exemption Amount

####  `II_em`  
_Description:_ Subtracted from AGI in the calculation of taxable income, per taxpayer and dependent.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 3900.0  
2014: 3950.0  
2015: 4000.0  
2016: 4050.0  
2017: 4050.0  
2018: 0.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 4691.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Personal Exemption Phaseout Rate

####  `II_prt`  
_Description:_ Personal exemption amount will decrease by this rate for each dollar of AGI exceeding exemption phaseout start.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Repeal for Dependents Under Age 18

####  `II_no_em_nu18`  
_Description:_ Total personal exemptions will be decreased by the number of dependents under the age of 18.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


## Standard Deduction

### Additional Standard Deduction For Blind And Aged

####  `STD_Aged`  
_Description:_ To get the standard deduction for aged or blind individuals, taxpayers need to add this value to regular standard deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [1500.0, 1200.0, 1200.0, 1500.0, 1500.0]  
2014: [1550.0, 1200.0, 1200.0, 1550.0, 1550.0]  
2015: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2016: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2017: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2018: [1600.0, 1300.0, 1300.0, 1600.0, 1300.0]  
2019: [1650.0, 1300.0, 1300.0, 1650.0, 1300.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Standard Deduction Amount

####  `STD`  
_Description:_ Amount filing unit can use as a standard deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [6100.0, 12200.0, 6100.0, 8950.0, 12200.0]  
2014: [6200.0, 12400.0, 6200.0, 9100.0, 12400.0]  
2015: [6300.0, 12600.0, 6300.0, 9250.0, 12600.0]  
2016: [6300.0, 12600.0, 6300.0, 9300.0, 12600.0]  
2017: [6350.0, 12700.0, 6350.0, 9350.0, 12700.0]  
2018: [12000.0, 24000.0, 12000.0, 18000.0, 24000.0]  
2019: [12200.0, 24400.0, 12200.0, 18350.0, 24400.0]  
2020: [12387.88, 24775.76, 12387.88, 18632.59, 24775.76]  
2021: [12478.31, 24956.62, 12478.31, 18768.61, 24956.62]  
2022: [12596.85, 25193.71, 12596.85, 18946.91, 25193.71]  
2023: [12795.88, 25591.77, 12795.88, 19246.27, 25591.77]  
2024: [13042.84, 26085.69, 13042.84, 19617.72, 26085.69]  
2025: [13303.7, 26607.4, 13303.7, 20010.07, 26607.4]  
2026: [7355.0, 14711.0, 7355.0, 10831.0, 14711.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


## Nonrefundable Credits

### Child And Dependent Care

####  `CDCC_c`  
_Description:_ The maximum amount of credit allowed for each qualifying dependent.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 3000.0  
2014: 3000.0  
2015: 3000.0  
2016: 3000.0  
2017: 3000.0  
2018: 3000.0  
2019: 3000.0  
_Valid Range:_ min = 0 and max = 3000  
_Out-of-Range Action:_ error  


####  `CDCC_ps`  
_Description:_ For taxpayers with AGI over this amount, the credit is reduced by one percentage point each $2000 of AGI over this amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 15000.0  
2014: 15000.0  
2015: 15000.0  
2016: 15000.0  
2017: 15000.0  
2018: 15000.0  
2019: 15000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CDCC_crt`  
_Description:_ The maximum percentage rate in the AGI phaseout; this percentage rate decreases as AGI rises above the CDCC_ps level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 35.0  
2014: 35.0  
2015: 35.0  
2016: 35.0  
2017: 35.0  
2018: 35.0  
2019: 35.0  
_Valid Range:_ min = 0 and max = 100  
_Out-of-Range Action:_ error  


### Misc. Credit Limits

####  `CR_RetirementSavings_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the retirement savings credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*RetirementSavingsCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_ForeignTax_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the foreign tax credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ForeignTaxCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_ResidentialEnergy_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the residential energy credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ResidentialEnergyCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_GeneralBusiness_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the general business credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*GeneralBusinessCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_MinimumTax_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the previous year minimum tax credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*PreviousYearMinimumTaxCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_AmOppRefundable_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the refundable American Opportunity credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*RefundablePortionOfAmericanOpportunityCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_AmOppNonRefundable_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the nonrefundable American Opportunity credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*NonRefundablePortionOfAmericanOpportunityCredit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_SchR_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of Schedule R credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ScheduleRCredit  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_OtherCredits_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of other credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*OtherCredits.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_Education_hc`  
_Description:_ If greater than zero, this decimal fraction reduces the portion of education credits that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*EducationCredits.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Personal Nonrefundable Credit

####  `II_credit_nr`  
_Description:_ This credit amount is not refundable and is phased out based on AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `II_credit_nr_ps`  
_Description:_ The personal nonrefundable credit amount will be reduced for taxpayers with AGI higher than this threshold level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `II_credit_nr_prt`  
_Description:_ The personal nonrefundable credit amount will be reduced at this rate for each dollar of AGI exceeding the II_credit_nr_ps threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


## Child/Dependent Credits

### Additional Child Tax Credit

####  `ACTC_c`  
_Description:_ This refundable credit is applied to child dependents and phases out exactly like the CTC amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1000.0  
2016: 1000.0  
2017: 1000.0  
2018: 1400.0  
2019: 1400.0  
2020: 1400.0  
2021: 1400.0  
2022: 1500.0  
2023: 1500.0  
2024: 1500.0  
2025: 1600.0  
2026: 1000.0  
_Valid Range:_ min = 0 and max = CTC_c  
_Out-of-Range Action:_ error  


####  `ACTC_rt`  
_Description:_ This is the fraction of earnings used in calculating the ACTC, which is a partially refundable credit that supplements the CTC for some taxpayers.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ACTC_rt_bonus_under6family`  
_Description:_ For families with qualifying children under 6 years old, this bonus rate is added to the fraction of earnings (additional child tax credit rate) used in calculating the ACTC.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ACTC_Income_thd`  
_Description:_ The portion of earned income below this threshold does not count as base for the Additional Child Tax Credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 3000.0  
2014: 3000.0  
2015: 3000.0  
2016: 3000.0  
2017: 3000.0  
2018: 2500.0  
2019: 2500.0  
2020: 2500.0  
2021: 2500.0  
2022: 2500.0  
2023: 2500.0  
2024: 2500.0  
2025: 2500.0  
2026: 3000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ACTC_ChildNum`  
_Description:_ Families with this number of qualified children or more may qualify for a different formula to calculate the Additional Child Tax Credit, which is a partially refundable credit that supplements the Child Tax Credit for some taxpayers.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 3  
2014: 3  
2015: 3  
2016: 3  
2017: 3  
2018: 3  
2019: 3  
_Valid Range:_ min = 0 and max = 99  
_Out-of-Range Action:_ error  


### Child Tax Credit

####  `CTC_c`  
_Description:_ The maximum nonrefundable credit allowed for each child.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1000.0  
2016: 1000.0  
2017: 1000.0  
2018: 2000.0  
2019: 2000.0  
2020: 2000.0  
2021: 2000.0  
2022: 2000.0  
2023: 2000.0  
2024: 2000.0  
2025: 2000.0  
2026: 1000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_c_under6_bonus`  
_Description:_ The maximum amount of child tax credit allowed for each child is increased by this amount for qualifying children under 6 years old.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_ps`  
_Description:_ Child tax credit begins to decrease when MAGI is above this level; read descriptions of the dependent credit amounts for how they phase out when MAGI is above this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2014: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2015: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2016: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2017: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2020: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2021: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2022: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2023: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2024: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2025: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2026: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_prt`  
_Description:_ The amount of the credit starts to decrease at this rate if MAGI is higher than child tax credit phaseout start.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.05  
2014: 0.05  
2015: 0.05  
2016: 0.05  
2017: 0.05  
2018: 0.05  
2019: 0.05  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Other Dependent Tax Credit

####  `ODC_c`  
_Description:_ This nonrefundable credit is applied to non-child dependents and phases out along with the CTC amount.  
_Notes:_ Became current-law policy with passage of TCJA  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 500.0  
2019: 500.0  
2020: 500.0  
2021: 500.0  
2022: 500.0  
2023: 500.0  
2024: 500.0  
2025: 500.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


## Itemized Deductions

### Casualty

####  `ID_Casualty_frt`  
_Description:_ Taxpayers are eligible to deduct the portion of their gross casualty losses exceeding this fraction of AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Casualty_hc`  
_Description:_ This decimal fraction can be applied to limit the amount of casualty expense deduction allowed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Casualty_c`  
_Description:_ The amount of casualty expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Ceiling On The Amount Of Itemized Deductions Allowed

####  `ID_c`  
_Description:_ The amount of itemized deductions is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_AmountCap_rt`  
_Description:_ The gross allowable amount of specified itemized deductions is capped at this percent of AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_AmountCap_Switch`  
_Description:_ The cap on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
 for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


### Ceiling On The Benefit Of Itemized Deductions As A Percent Of Deductible Expenses

####  `ID_BenefitCap_rt`  
_Description:_ The benefit from specified itemized deductions is capped at this percent of the total deductible expenses.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_BenefitCap_Switch`  
_Description:_ The cap on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
 for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


### Charity

####  `ID_Charity_crt_all`  
_Description:_ The total deduction for charity is capped at this fraction of AGI.  
_Notes:_ When using PUF data, raising this parameter value may produce unexpected results because in PUF data the variables e19800 and e20100 are already capped.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.5  
2014: 0.5  
2015: 0.5  
2016: 0.5  
2017: 0.5  
2018: 0.6  
2019: 0.6  
2020: 0.6  
2021: 0.6  
2022: 0.6  
2023: 0.6  
2024: 0.6  
2025: 0.6  
2026: 0.5  
_Valid Range:_ min = 0 and max = 0.6  
_Out-of-Range Action:_ warn  


####  `ID_Charity_crt_noncash`  
_Description:_ The deduction for noncash charity contributions is capped at this fraction of AGI.  
_Notes:_ When using PUF data, raising this parameter value may produce unexpected results because in PUF data the variables e19800 and e20100 are already capped.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.3  
2014: 0.3  
2015: 0.3  
2016: 0.3  
2017: 0.3  
2018: 0.3  
2019: 0.3  
_Valid Range:_ min = 0 and max = 0.3  
_Out-of-Range Action:_ warn  


####  `ID_Charity_frt`  
_Description:_ Taxpayers are eligible to deduct the portion of their charitable expense exceeding this fraction of AGI.  
_Notes:_ This parameter allows for implementation of Option 52 from https://www.cbo.gov/sites/default/files/cbofiles/attachments/49638-BudgetOptions.pdf.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Charity_hc`  
_Description:_ This decimal fraction can be applied to limit the amount of charity expense deduction allowed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Charity_c`  
_Description:_ The amount of charity expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_Charity_f`  
_Description:_ Only charitable giving in excess of this dollar amount is eligible for a deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Interest Paid

####  `ID_InterestPaid_hc`  
_Description:_ This decimal fraction can be applied to limit the amount of interest paid deduction allowed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_InterestPaid_c`  
_Description:_ The amount of interest paid deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Itemized Deduction Limitation

####  `ID_ps`  
_Description:_ The itemized deductions will be reduced for taxpayers with AGI higher than this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [250000.0, 300000.0, 150000.0, 275000.0, 300000.0]  
2014: [254200.0, 305050.0, 152525.0, 279650.0, 305050.0]  
2015: [258250.0, 309900.0, 154950.0, 284050.0, 309900.0]  
2016: [259400.0, 311300.0, 155650.0, 285350.0, 311300.0]  
2017: [261500.0, 313800.0, 156900.0, 287650.0, 313800.0]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2020: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2021: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2022: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2023: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2024: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2025: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2026: [302907.0, 363489.0, 181744.0, 333198.0, 363489.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_prt`  
_Description:_ Taxpayers will not be eligible to deduct the full amount of itemized deduction if their AGI is above the phaseout start. The deductible portion would be decreased at this rate for each dollar exceeding the start.  
_Notes:_ This phaseout rate cannot be lower than 0.03 for each dollar, due to limited data on non-itemizers.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.03  
2014: 0.03  
2015: 0.03  
2016: 0.03  
2017: 0.03  
2018: 0.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 0.03  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_crt`  
_Description:_ The phaseout amount is capped at this fraction of the original total deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.8  
2014: 0.8  
2015: 0.8  
2016: 0.8  
2017: 0.8  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.8  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Medical Expenses

####  `ID_Medical_frt`  
_Description:_ Taxpayers are eligible to deduct the portion of their medical expenses exceeding this fraction of AGI.  
_Notes:_ When using PUF data, lowering this parameter value may produce unexpected results because PUF e17500 variable is zero below the floor.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.075  
2018: 0.075  
2019: 0.075  
2020: 0.075  
2021: 0.075  
2022: 0.075  
2023: 0.075  
2024: 0.075  
2025: 0.075  
2026: 0.075  
_Valid Range:_ min = 0.075 and max = 0.1  
_Out-of-Range Action:_ warn  


####  `ID_Medical_frt_add4aged`  
_Description:_ Elderly taxpayers have this fraction added to the value of the regular floor rate for deductible medical expenses.  This fraction was -0.025 from 2013 to 2016, but that was temporary and it changed to zero beginning in 2017.  
_Notes:_ When using PUF data, changing this parameter value may produce unexpected results because PUF e17500 variable is zero below the floor.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: -0.025  
2014: -0.025  
2015: -0.025  
2016: -0.025  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = -0.025 and max = 0.0  
_Out-of-Range Action:_ warn  


####  `ID_Medical_hc`  
_Description:_ This decimal fraction can be applied to limit the amount of medical expense deduction allowed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Medical_c`  
_Description:_ The amount of medical expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Miscellaneous

####  `ID_Miscellaneous_frt`  
_Description:_ Taxpayers are eligible to deduct the portion of their miscellaneous expense exceeding this fraction of AGI.  
_Notes:_ When using PUF data, lowering this parameter value may produce unexpected results because in PUF data the variable e20400 is zero below the floor.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0.02 and max = 1  
_Out-of-Range Action:_ warn  


####  `ID_Miscellaneous_hc`  
_Description:_ This decimal fraction can be applied to limit the amount of miscellaneous expense deduction allowed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_Miscellaneous_c`  
_Description:_ The amount of miscellaneous expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### State And Local Income And Sales Taxes

####  `ID_StateLocalTax_hc`  
_Description:_ This decimal fraction reduces the state and local income and sales tax deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_StateLocalTax_crt`  
_Description:_ The total deduction for state and local taxes is capped at this fraction of AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_StateLocalTax_c`  
_Description:_ The amount of state and local income and sales taxes deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### State And Local Taxes And Real Estate Taxes

####  `ID_AllTaxes_hc`  
_Description:_ This decimal fraction reduces all state and local taxes paid eligible to deduct in itemized deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_AllTaxes_c`  
_Description:_ The amount of state and local income, sales and real estate tax deductions is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2019: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2020: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2021: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2022: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2023: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2024: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2025: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2026: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### State, Local, And Foreign Real Estate Taxes

####  `ID_RealEstate_hc`  
_Description:_ This decimal fraction reduces real estate taxes paid eligible to deduct in itemized deduction.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_RealEstate_crt`  
_Description:_ The total deduction for all real estate taxes is capped at this fraction of AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_RealEstate_c`  
_Description:_ The amount of real estate taxes deduction is limited to this dollar amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Surtax On Itemized Deduction Benefits Above An AGI Threshold

####  `ID_BenefitSurtax_trt`  
_Description:_ The benefit from specified itemized deductions exceeding the credit is taxed at this rate. A surtax rate of 1 strictly limits the benefit from specified itemized deductions to the specified credit. In http://www.nber.org/papers/w16921, Feldstein, Feenberg, and MacGuineas propose a credit of 2% of AGI against a 100% tax rate; in their proposal, however, a broader set of tax benefits, including the employer provided health exclusion, would be taxed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_BenefitSurtax_crt`  
_Description:_ The surtax on specified itemized deductions applies to benefits in excess of this fraction of AGI. In http://www.nber.org/papers/w16921, Feldstein, Feenberg, and MacGuineas propose a credit of 2% of AGI against a 100% tax rate; in their proposal, however, a broader set of tax benefits, including the employer provided health exclusion, would be taxed.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `ID_BenefitSurtax_em`  
_Description:_ This amount is subtracted from itemized deduction benefits in the calculation of the itemized deduction benefit surtax. With ID_BenefitSurtax_crt set to 0.0 and ID_BenefitSurtax_trt set to 1.0, this amount serves as a dollar limit on the value of itemized deductions.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ID_BenefitSurtax_Switch`  
_Description:_ The surtax on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
 for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


## Capital Gains And Dividends

### AMT - Long Term Capital Gains And Qualified Dividends

####  `AMT_CG_rt1`  
_Description:_ Capital gain and qualified dividends (stacked on top of regular income) below threshold 1 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AMT_CG_brk1`  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this are taxed at AMT capital gain rate 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38600.0, 77200.0, 38600.0, 51700.0, 77200.0]  
2019: [39375.0, 78750.0, 39375.0, 52750.0, 78750.0]  
_Valid Range:_ min = 0 and max = AMT_CG_brk2  
_Out-of-Range Action:_ error  


####  `AMT_CG_rt2`  
_Description:_ Capital gain and qualified dividend (stacked on top of regular income) below threshold 2 and above threshold 1 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AMT_CG_brk2`  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this threshold and above bracket 1 are taxed at AMT capital gain rate 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [425800.0, 479000.0, 239500.0, 452400.0, 479000.0]  
2019: [434550.0, 488850.0, 244425.0, 461700.0, 488850.0]  
_Valid Range:_ min = AMT_CG_brk1 and max = AMT_CG_brk3  
_Out-of-Range Action:_ error  


####  `AMT_CG_rt3`  
_Description:_ The capital gain and qualified dividend (stacked on top of regular income) above threshold 2 and below threshold 3 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.2  
2014: 0.2  
2015: 0.2  
2016: 0.2  
2017: 0.2  
2018: 0.2  
2019: 0.2  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AMT_CG_brk3`  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this and above bracket 2 are taxed at capital gain rate 3; above thisthey are taxed at AMT capital gain rate 4.  Default value is essentially infinity.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = AMT_CG_brk2 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMT_CG_rt4`  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 3 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Regular - Long Term Capital Gains And Qualified Dividends

####  `CG_rt1`  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are below threshold 1 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CG_brk1`  
_Description:_ The gains and dividends (stacked on top of regular income) below this are taxed at capital gain rate 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38600.0, 77200.0, 38600.0, 51700.0, 77200.0]  
2019: [39375.0, 78750.0, 39375.0, 52750.0, 78750.0]  
_Valid Range:_ min = 0 and max = CG_brk2  
_Out-of-Range Action:_ error  


####  `CG_rt2`  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are below threshold 2 and above threshold 1 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CG_brk2`  
_Description:_ The gains and dividends (stacked on top of regular income) below this and above top of bracket 1 are taxed at capital gain rate 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [425800.0, 479000.0, 239500.0, 452400.0, 479000.0]  
2019: [434550.0, 488850.0, 244425.0, 461700.0, 488850.0]  
_Valid Range:_ min = CG_brk1 and max = CG_brk3  
_Out-of-Range Action:_ error  


####  `CG_rt3`  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 2 and below threshold 3 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.2  
2014: 0.2  
2015: 0.2  
2016: 0.2  
2017: 0.2  
2018: 0.2  
2019: 0.2  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CG_brk3`  
_Description:_ The gains and dividends (stacked on top of regular income) below this and above top of bracket 2 are taxed at the capital gain rate 3; above this they are taxed at capital gain rate 4.  Default value is essentially infinity.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = CG_brk2 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CG_rt4`  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 3 are taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Tax All Capital Gains And Dividends The Same As Regular Taxable Income

####  `CG_nodiff`  
_Description:_ Specifies whether or not long term capital gains and qualified dividends are taxed like regular taxable income.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `CG_ec`  
_Description:_ Positive value used only if long term capital gains and qualified dividends taxed no differently than regular taxable income.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CG_reinvest_ec_rt`  
_Description:_ Positive value used only if long term capital gains and qualified dividends taxed no differently than regular taxable income.  To limit the exclusion to capital gains and dividends invested within one year, set to statutory exclusion rate times the fraction of capital gains and qualified dividends in excess of the exclusion that are assumed to be reinvested within the year.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


## Personal Income

### Alternative Minimum Tax

####  `AMT_em`  
_Description:_ The amount of AMT taxable income exempted from AMT.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [51900.0, 80800.0, 40400.0, 51900.0, 80800.0]  
2014: [52800.0, 82100.0, 41050.0, 52800.0, 82100.0]  
2015: [53600.0, 83400.0, 41700.0, 53600.0, 83400.0]  
2016: [53900.0, 83800.0, 41900.0, 53900.0, 83800.0]  
2017: [54300.0, 84500.0, 42250.0, 54300.0, 84500.0]  
2018: [70300.0, 109400.0, 54700.0, 70300.0, 109400.0]  
2019: [71700.0, 111700.0, 55850.0, 71700.0, 111700.0]  
2020: [72804.18, 113420.18, 56710.09, 72804.18, 113420.18]  
2021: [73335.65, 114248.15, 57124.07, 73335.65, 114248.15]  
2022: [74032.34, 115333.51, 57666.75, 74032.34, 115333.51]  
2023: [75202.05, 117155.78, 58577.88, 75202.05, 117155.78]  
2024: [76653.45, 119416.89, 59708.43, 76653.45, 119416.89]  
2025: [78186.52, 121805.23, 60902.6, 78186.52, 121805.23]  
2026: [62898.0, 97880.0, 48940.0, 62898.0, 97880.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMT_prt`  
_Description:_ AMT exemption will decrease at this rate for each dollar of AMT taxable income exceeding AMT phaseout start.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.25  
2019: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AMT_em_ps`  
_Description:_ AMT exemption starts to decrease when AMT taxable income goes beyond this threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [115400.0, 153900.0, 76950.0, 115400.0, 153900.0]  
2014: [117300.0, 156500.0, 78250.0, 117300.0, 156500.0]  
2015: [119200.0, 158900.0, 79450.0, 119200.0, 158900.0]  
2016: [119700.0, 159700.0, 79850.0, 119700.0, 159700.0]  
2017: [120700.0, 160900.0, 80450.0, 120700.0, 160900.0]  
2018: [500000.0, 1000000.0, 500000.0, 500000.0, 1000000.0]  
2019: [510300.0, 1020600.0, 510300.0, 510300.0, 1020600.0]  
2020: [518158.62, 1036317.24, 518158.62, 518158.62, 1036317.24]  
2021: [521941.18, 1043882.36, 521941.18, 521941.18, 1043882.36]  
2022: [526899.62, 1053799.24, 526899.62, 526899.62, 1053799.24]  
2023: [535224.63, 1070449.27, 535224.63, 535224.63, 1070449.27]  
2024: [545554.47, 1091108.94, 545554.47, 545554.47, 1091108.94]  
2025: [556465.56, 1112931.12, 556465.56, 556465.56, 1112931.12]  
2026: [139812.0, 186378.0, 93189.0, 139812.0, 186378.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMT_rt1`  
_Description:_ The tax rate applied to the portion of AMT taxable income below the surtax threshold, AMT bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.26  
2014: 0.26  
2015: 0.26  
2016: 0.26  
2017: 0.26  
2018: 0.26  
2019: 0.26  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AMT_brk1`  
_Description:_ AMT taxable income below this is subject to AMT rate 1 and above it is subject to AMT rate 1 + the additional AMT rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 179500.0  
2014: 182500.0  
2015: 185400.0  
2016: 186300.0  
2017: 187800.0  
2018: 191100.0  
2019: 194800.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMT_rt2`  
_Description:_ The additional tax rate applied to the portion of AMT income above the AMT bracket 1.  
_Notes:_ This is the additional tax rate (on top of AMT rate 1) for AMT income above AMT bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Pass-Through

####  `PT_rt1`  
_Description:_ The lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
2020: 0.1  
2021: 0.1  
2022: 0.1  
2023: 0.1  
2024: 0.1  
2025: 0.1  
2026: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk1`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold is taxed at tax rate 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [8925.0, 17850.0, 8925.0, 12750.0, 17850.0]  
2014: [9075.0, 18150.0, 9075.0, 12950.0, 18150.0]  
2015: [9225.0, 18450.0, 9225.0, 13150.0, 18450.0]  
2016: [9275.0, 18550.0, 9275.0, 13250.0, 18550.0]  
2017: [9325.0, 18650.0, 9325.0, 13350.0, 18650.0]  
2018: [9525.0, 19050.0, 9525.0, 13600.0, 19050.0]  
2019: [9700.0, 19400.0, 9700.0, 13850.0, 19400.0]  
2020: [9849.38, 19698.76, 9849.38, 14063.29, 19698.76]  
2021: [9921.28, 19842.56, 9921.28, 14165.95, 19842.56]  
2022: [10015.53, 20031.06, 10015.53, 14300.53, 20031.06]  
2023: [10173.78, 20347.55, 10173.78, 14526.48, 20347.55]  
2024: [10370.13, 20740.26, 10370.13, 14806.84, 20740.26]  
2025: [10577.53, 21155.07, 10577.53, 15102.98, 21155.07]  
2026: [10802.0, 21603.0, 10802.0, 15464.0, 21603.0]  
_Valid Range:_ min = 0 and max = PT_brk2  
_Out-of-Range Action:_ error  


####  `PT_rt2`  
_Description:_ The second lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 2 and above tax bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.12  
2019: 0.12  
2020: 0.12  
2021: 0.12  
2022: 0.12  
2023: 0.12  
2024: 0.12  
2025: 0.12  
2026: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk2`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 1 is taxed at tax rate 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38700.0, 77400.0, 38700.0, 51800.0, 77400.0]  
2019: [39475.0, 78950.0, 39475.0, 52850.0, 78950.0]  
2020: [40082.92, 80165.83, 40082.92, 53663.89, 80165.83]  
2021: [40375.53, 80751.04, 40375.53, 54055.64, 80751.04]  
2022: [40759.1, 81518.17, 40759.1, 54569.17, 81518.17]  
2023: [41403.09, 82806.16, 41403.09, 55431.36, 82806.16]  
2024: [42202.17, 84404.32, 42202.17, 56501.19, 84404.32]  
2025: [43046.21, 86092.41, 43046.21, 57631.21, 86092.41]  
2026: [43959.0, 87918.0, 43959.0, 58844.0, 87918.0]  
_Valid Range:_ min = PT_brk1 and max = PT_brk3  
_Out-of-Range Action:_ error  


####  `PT_rt3`  
_Description:_ The third lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 3 and above tax bracket 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.22  
2019: 0.22  
2020: 0.22  
2021: 0.22  
2022: 0.22  
2023: 0.22  
2024: 0.22  
2025: 0.22  
2026: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk3`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 2 is taxed at tax rate 3.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [87850.0, 146400.0, 73200.0, 125450.0, 146400.0]  
2014: [89350.0, 148850.0, 74425.0, 127550.0, 148850.0]  
2015: [90750.0, 151200.0, 75600.0, 129600.0, 151200.0]  
2016: [91150.0, 151900.0, 75950.0, 130150.0, 151900.0]  
2017: [91900.0, 153100.0, 76550.0, 131200.0, 153100.0]  
2018: [82500.0, 165000.0, 82500.0, 82500.0, 165000.0]  
2019: [84200.0, 168400.0, 84200.0, 84200.0, 168400.0]  
2020: [85496.68, 170993.36, 85496.68, 85496.68, 170993.36]  
2021: [86120.81, 172241.61, 86120.81, 86120.81, 172241.61]  
2022: [86938.96, 173877.91, 86938.96, 86938.96, 173877.91]  
2023: [88312.6, 176625.18, 88312.6, 88312.6, 176625.18]  
2024: [90017.03, 180034.05, 90017.03, 90017.03, 180034.05]  
2025: [91817.37, 183634.73, 91817.37, 91817.37, 183634.73]  
2026: [106452.0, 177343.0, 88671.0, 151975.0, 177343.0]  
_Valid Range:_ min = PT_brk2 and max = PT_brk4  
_Out-of-Range Action:_ error  


####  `PT_rt4`  
_Description:_ The tax rate applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 4 and above tax bracket 3.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.28  
2014: 0.28  
2015: 0.28  
2016: 0.28  
2017: 0.28  
2018: 0.24  
2019: 0.24  
2020: 0.24  
2021: 0.24  
2022: 0.24  
2023: 0.24  
2024: 0.24  
2025: 0.24  
2026: 0.28  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk4`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 3 is taxed at tax rate 4.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [183250.0, 223050.0, 111525.0, 203150.0, 223050.0]  
2014: [186350.0, 226850.0, 113425.0, 206600.0, 226850.0]  
2015: [189300.0, 230450.0, 115225.0, 209850.0, 230450.0]  
2016: [190150.0, 231450.0, 115725.0, 210800.0, 231450.0]  
2017: [191650.0, 233350.0, 116675.0, 212500.0, 233350.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160725.0, 321450.0, 160725.0, 160700.0, 321450.0]  
2020: [163200.16, 326400.33, 163200.16, 163174.78, 326400.33]  
2021: [164391.52, 328783.05, 164391.52, 164365.96, 328783.05]  
2022: [165953.24, 331906.49, 165953.24, 165927.44, 331906.49]  
2023: [168575.3, 337150.61, 168575.3, 168549.09, 337150.61]  
2024: [171828.8, 343657.62, 171828.8, 171802.09, 343657.62]  
2025: [175265.38, 350530.77, 175265.38, 175238.13, 350530.77]  
2026: [221997.0, 270300.0, 135150.0, 246148.0, 270300.0]  
_Valid Range:_ min = PT_brk3 and max = PT_brk5  
_Out-of-Range Action:_ error  


####  `PT_rt5`  
_Description:_ The third highest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 5 and above tax bracket 4.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.33  
2014: 0.33  
2015: 0.33  
2016: 0.33  
2017: 0.33  
2018: 0.32  
2019: 0.32  
2020: 0.32  
2021: 0.32  
2022: 0.32  
2023: 0.32  
2024: 0.32  
2025: 0.32  
2026: 0.33  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk5`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 4 is taxed at tax rate 5.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [398350.0, 398350.0, 199175.0, 398350.0, 398350.0]  
2014: [405100.0, 405100.0, 202550.0, 405100.0, 405100.0]  
2015: [411500.0, 411500.0, 205750.0, 411500.0, 411500.0]  
2016: [413350.0, 413350.0, 206675.0, 413350.0, 413350.0]  
2017: [416700.0, 416700.0, 208350.0, 416700.0, 416700.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [204100.0, 408200.0, 204100.0, 204100.0, 408200.0]  
2020: [207243.14, 414486.28, 207243.14, 207243.14, 414486.28]  
2021: [208756.01, 417512.03, 208756.01, 208756.01, 417512.03]  
2022: [210739.19, 421478.39, 210739.19, 210739.19, 421478.39]  
2023: [214068.87, 428137.75, 214068.87, 214068.87, 428137.75]  
2024: [218200.4, 436400.81, 218200.4, 218200.4, 436400.81]  
2025: [222564.41, 445128.83, 222564.41, 222564.41, 445128.83]  
2026: [482682.0, 482682.0, 241341.0, 482682.0, 482682.0]  
_Valid Range:_ min = PT_brk4 and max = PT_brk6  
_Out-of-Range Action:_ error  


####  `PT_rt6`  
_Description:_ The second higher tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 6 and above tax bracket 5.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.35  
2014: 0.35  
2015: 0.35  
2016: 0.35  
2017: 0.35  
2018: 0.35  
2019: 0.35  
2020: 0.35  
2021: 0.35  
2022: 0.35  
2023: 0.35  
2024: 0.35  
2025: 0.35  
2026: 0.35  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk6`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 5 is taxed at tax rate 6.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [500000.0, 600000.0, 300000.0, 500000.0, 600000.0]  
2019: [510300.0, 612350.0, 306175.0, 510300.0, 612350.0]  
2020: [518158.62, 621780.19, 310890.1, 518158.62, 621780.19]  
2021: [521941.18, 626319.19, 313159.6, 521941.18, 626319.19]  
2022: [526899.62, 632269.22, 316134.62, 526899.62, 632269.22]  
2023: [535224.63, 642259.07, 321129.55, 535224.63, 642259.07]  
2024: [545554.47, 654654.67, 327327.35, 545554.47, 654654.67]  
2025: [556465.56, 667747.76, 333873.9, 556465.56, 667747.76]  
2026: [484651.0, 545233.0, 272616.0, 514942.0, 545233.0]  
_Valid Range:_ min = PT_brk5 and max = PT_brk7  
_Out-of-Range Action:_ error  


####  `PT_rt7`  
_Description:_ The highest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 7 and above tax bracket 6.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.396  
2014: 0.396  
2015: 0.396  
2016: 0.396  
2017: 0.396  
2018: 0.37  
2019: 0.37  
2020: 0.37  
2021: 0.37  
2022: 0.37  
2023: 0.37  
2024: 0.37  
2025: 0.37  
2026: 0.396  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_brk7`  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 6 is taxed at tax rate 7. Default value is essentially infinity.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = PT_brk6 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `PT_rt8`  
_Description:_ The extra tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations above the tax bracket 7.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_EligibleRate_active`  
_Description:_ Eligibility rate of active business income for separate pass-through rates.  
_Notes:_ Active business income defined as e00900 + e26270  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_EligibleRate_passive`  
_Description:_ Eligibility rate of passive business income for mseparate pass-through rates.  
_Notes:_ Passive business income defined as e02000 - e26270  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_wages_active_income`  
_Description:_ Whether active business income eligibility base for PT schedule for includes wages.  
_Notes:_ Only applies if active business income is positive  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `PT_top_stacking`  
_Description:_ Whether taxable income eligible for PT rate schedule is stacked on top of regular taxable income.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: True  
2014: True  
2015: True  
2016: True  
2017: True  
2018: True  
2019: True  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `PT_qbid_rt`  
_Description:_ Fraction of pass-through business income that may be excluded from taxable income.  
_Notes:_ Applies to e00900 + e26270  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.2  
2019: 0.2  
2020: 0.2  
2021: 0.2  
2022: 0.2  
2023: 0.2  
2024: 0.2  
2025: 0.2  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_qbid_taxinc_thd`  
_Description:_ Pre-QBID taxable income above this lower threshold implies the QBID amount begins to be limited.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160700.0, 321400.0, 160725.0, 160700.0, 321400.0]  
2020: [163174.78, 326349.56, 163200.16, 163174.78, 326349.56]  
2021: [164365.96, 328731.91, 164391.52, 164365.96, 328731.91]  
2022: [165927.44, 331854.86, 165953.24, 165927.44, 331854.86]  
2023: [168549.09, 337098.17, 168575.3, 168549.09, 337098.17]  
2024: [171802.09, 343604.16, 171828.8, 171802.09, 343604.16]  
2025: [175238.13, 350476.24, 175265.38, 175238.13, 350476.24]  
2026: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `PT_qbid_taxinc_gap`  
_Description:_ Pre-QBID taxable income above this upper threshold implies the QBID amount is even more limited.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [1.0, 1.0, 1.0, 1.0, 1.0]  
2014: [1.0, 1.0, 1.0, 1.0, 1.0]  
2015: [1.0, 1.0, 1.0, 1.0, 1.0]  
2016: [1.0, 1.0, 1.0, 1.0, 1.0]  
2017: [1.0, 1.0, 1.0, 1.0, 1.0]  
2018: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2019: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2020: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2021: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2022: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2023: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2024: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2025: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2026: [1.0, 1.0, 1.0, 1.0, 1.0]  
_Valid Range:_ min = 1 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `PT_qbid_w2_wages_rt`  
_Description:_ QBID is capped at this fraction of W-2 wages paid by the pass-through business if pre-QBID taxable income is above the QBID thresholds.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.5  
2019: 0.5  
2020: 0.5  
2021: 0.5  
2022: 0.5  
2023: 0.5  
2024: 0.5  
2025: 0.5  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_qbid_alt_w2_wages_rt`  
_Description:_ QBID is capped at this fraction of W-2 wages paid by the pass-through business plus some fraction of business property if pre-QBID taxable income is above the QBID thresholds and the alternative cap is higher than the main wage-only cap.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.25  
2019: 0.25  
2020: 0.25  
2021: 0.25  
2022: 0.25  
2023: 0.25  
2024: 0.25  
2025: 0.25  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `PT_qbid_alt_property_rt`  
_Description:_ QBID is capped at this fraction of business property owned plus some fraction of W-2 wages paid by the pass-through business if pre-QBID taxable income is above the QBID thresholds and the alternative cap is higher than the main wage-only cap.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.025  
2019: 0.025  
2020: 0.025  
2021: 0.025  
2022: 0.025  
2023: 0.025  
2024: 0.025  
2025: 0.025  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Regular: Non-AMT, Non-Pass-Through

####  `II_rt1`  
_Description:_ The lowest tax rate, applied to the portion of taxable income below tax bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
2020: 0.1  
2021: 0.1  
2022: 0.1  
2023: 0.1  
2024: 0.1  
2025: 0.1  
2026: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk1`  
_Description:_ Taxable income below this threshold is taxed at tax rate 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [8925.0, 17850.0, 8925.0, 12750.0, 17850.0]  
2014: [9075.0, 18150.0, 9075.0, 12950.0, 18150.0]  
2015: [9225.0, 18450.0, 9225.0, 13150.0, 18450.0]  
2016: [9275.0, 18550.0, 9275.0, 13250.0, 18550.0]  
2017: [9325.0, 18650.0, 9325.0, 13350.0, 18650.0]  
2018: [9525.0, 19050.0, 9525.0, 13600.0, 19050.0]  
2019: [9700.0, 19400.0, 9700.0, 13850.0, 19400.0]  
2020: [9849.38, 19698.76, 9849.38, 14063.29, 19698.76]  
2021: [9921.28, 19842.56, 9921.28, 14165.95, 19842.56]  
2022: [10015.53, 20031.06, 10015.53, 14300.53, 20031.06]  
2023: [10173.78, 20347.55, 10173.78, 14526.48, 20347.55]  
2024: [10370.13, 20740.26, 10370.13, 14806.84, 20740.26]  
2025: [10577.53, 21155.07, 10577.53, 15102.98, 21155.07]  
2026: [10802.0, 21603.0, 10802.0, 15464.0, 21603.0]  
_Valid Range:_ min = 0 and max = II_brk2  
_Out-of-Range Action:_ error  


####  `II_rt2`  
_Description:_ The second lowest tax rate, applied to the portion of taxable income below tax bracket 2 and above tax bracket 1.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.12  
2019: 0.12  
2020: 0.12  
2021: 0.12  
2022: 0.12  
2023: 0.12  
2024: 0.12  
2025: 0.12  
2026: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk2`  
_Description:_ Income below this threshold and above tax bracket 1 is taxed at tax rate 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38700.0, 77400.0, 38700.0, 51800.0, 77400.0]  
2019: [39475.0, 78950.0, 39475.0, 52850.0, 78950.0]  
2020: [40082.92, 80165.83, 40082.92, 53663.89, 80165.83]  
2021: [40375.53, 80751.04, 40375.53, 54055.64, 80751.04]  
2022: [40759.1, 81518.17, 40759.1, 54569.17, 81518.17]  
2023: [41403.09, 82806.16, 41403.09, 55431.36, 82806.16]  
2024: [42202.17, 84404.32, 42202.17, 56501.19, 84404.32]  
2025: [43046.21, 86092.41, 43046.21, 57631.21, 86092.41]  
2026: [43959.0, 87918.0, 43959.0, 58844.0, 87918.0]  
_Valid Range:_ min = II_brk1 and max = II_brk3  
_Out-of-Range Action:_ error  


####  `II_rt3`  
_Description:_ The third lowest tax rate, applied to the portion of taxable income below tax bracket 3 and above tax bracket 2.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.22  
2019: 0.22  
2020: 0.22  
2021: 0.22  
2022: 0.22  
2023: 0.22  
2024: 0.22  
2025: 0.22  
2026: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk3`  
_Description:_ Income below this threshold and above tax bracket 2 is taxed at tax rate 3.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [87850.0, 146400.0, 73200.0, 125450.0, 146400.0]  
2014: [89350.0, 148850.0, 74425.0, 127550.0, 148850.0]  
2015: [90750.0, 151200.0, 75600.0, 129600.0, 151200.0]  
2016: [91150.0, 151900.0, 75950.0, 130150.0, 151900.0]  
2017: [91900.0, 153100.0, 76550.0, 131200.0, 153100.0]  
2018: [82500.0, 165000.0, 82500.0, 82500.0, 165000.0]  
2019: [84200.0, 168400.0, 84200.0, 84200.0, 168400.0]  
2020: [85496.68, 170993.36, 85496.68, 85496.68, 170993.36]  
2021: [86120.81, 172241.61, 86120.81, 86120.81, 172241.61]  
2022: [86938.96, 173877.91, 86938.96, 86938.96, 173877.91]  
2023: [88312.6, 176625.18, 88312.6, 88312.6, 176625.18]  
2024: [90017.03, 180034.05, 90017.03, 90017.03, 180034.05]  
2025: [91817.37, 183634.73, 91817.37, 91817.37, 183634.73]  
2026: [106452.0, 177343.0, 88671.0, 151975.0, 177343.0]  
_Valid Range:_ min = II_brk2 and max = II_brk4  
_Out-of-Range Action:_ error  


####  `II_rt4`  
_Description:_ The tax rate applied to the portion of taxable income below tax bracket 4 and above tax bracket 3.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.28  
2014: 0.28  
2015: 0.28  
2016: 0.28  
2017: 0.28  
2018: 0.24  
2019: 0.24  
2020: 0.24  
2021: 0.24  
2022: 0.24  
2023: 0.24  
2024: 0.24  
2025: 0.24  
2026: 0.28  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk4`  
_Description:_ Income below this threshold and above tax bracket 3 is taxed at tax rate 4.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [183250.0, 223050.0, 111525.0, 203150.0, 223050.0]  
2014: [186350.0, 226850.0, 113425.0, 206600.0, 226850.0]  
2015: [189300.0, 230450.0, 115225.0, 209850.0, 230450.0]  
2016: [190150.0, 231450.0, 115725.0, 210800.0, 231450.0]  
2017: [191650.0, 233350.0, 116675.0, 212500.0, 233350.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160725.0, 321450.0, 160725.0, 160700.0, 321450.0]  
2020: [163200.16, 326400.33, 163200.16, 163174.78, 326400.33]  
2021: [164391.52, 328783.05, 164391.52, 164365.96, 328783.05]  
2022: [165953.24, 331906.49, 165953.24, 165927.44, 331906.49]  
2023: [168575.3, 337150.61, 168575.3, 168549.09, 337150.61]  
2024: [171828.8, 343657.62, 171828.8, 171802.09, 343657.62]  
2025: [175265.38, 350530.77, 175265.38, 175238.13, 350530.77]  
2026: [221997.0, 270300.0, 135150.0, 246148.0, 270300.0]  
_Valid Range:_ min = II_brk3 and max = II_brk5  
_Out-of-Range Action:_ error  


####  `II_rt5`  
_Description:_ The third highest tax rate, applied to the portion of taxable income below tax bracket 5 and above tax bracket 4.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.33  
2014: 0.33  
2015: 0.33  
2016: 0.33  
2017: 0.33  
2018: 0.32  
2019: 0.32  
2020: 0.32  
2021: 0.32  
2022: 0.32  
2023: 0.32  
2024: 0.32  
2025: 0.32  
2026: 0.33  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk5`  
_Description:_ Income below this threshold and above tax bracket 4 is taxed at tax rate 5.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [398350.0, 398350.0, 199175.0, 398350.0, 398350.0]  
2014: [405100.0, 405100.0, 202550.0, 405100.0, 405100.0]  
2015: [411500.0, 411500.0, 205750.0, 411500.0, 411500.0]  
2016: [413350.0, 413350.0, 206675.0, 413350.0, 413350.0]  
2017: [416700.0, 416700.0, 208350.0, 416700.0, 416700.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [204100.0, 408200.0, 204100.0, 204100.0, 408200.0]  
2020: [207243.14, 414486.28, 207243.14, 207243.14, 414486.28]  
2021: [208756.01, 417512.03, 208756.01, 208756.01, 417512.03]  
2022: [210739.19, 421478.39, 210739.19, 210739.19, 421478.39]  
2023: [214068.87, 428137.75, 214068.87, 214068.87, 428137.75]  
2024: [218200.4, 436400.81, 218200.4, 218200.4, 436400.81]  
2025: [222564.41, 445128.83, 222564.41, 222564.41, 445128.83]  
2026: [482682.0, 482682.0, 241341.0, 482682.0, 482682.0]  
_Valid Range:_ min = II_brk4 and max = II_brk6  
_Out-of-Range Action:_ error  


####  `II_rt6`  
_Description:_ The second higher tax rate, applied to the portion of taxable income below tax bracket 6 and above tax bracket 5.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.35  
2014: 0.35  
2015: 0.35  
2016: 0.35  
2017: 0.35  
2018: 0.35  
2019: 0.35  
2020: 0.35  
2021: 0.35  
2022: 0.35  
2023: 0.35  
2024: 0.35  
2025: 0.35  
2026: 0.35  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk6`  
_Description:_ Income below this threshold and above tax bracket 5 is taxed at tax rate 6.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [500000.0, 600000.0, 300000.0, 500000.0, 600000.0]  
2019: [510300.0, 612350.0, 306175.0, 510300.0, 612350.0]  
2020: [518158.62, 621780.19, 310890.1, 518158.62, 621780.19]  
2021: [521941.18, 626319.19, 313159.6, 521941.18, 626319.19]  
2022: [526899.62, 632269.22, 316134.62, 526899.62, 632269.22]  
2023: [535224.63, 642259.07, 321129.55, 535224.63, 642259.07]  
2024: [545554.47, 654654.67, 327327.35, 545554.47, 654654.67]  
2025: [556465.56, 667747.76, 333873.9, 556465.56, 667747.76]  
2026: [484651.0, 545233.0, 272616.0, 514942.0, 545233.0]  
_Valid Range:_ min = II_brk5 and max = II_brk7  
_Out-of-Range Action:_ error  


####  `II_rt7`  
_Description:_ The tax rate applied to the portion of taxable income below tax bracket 7 and above tax bracket 6.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.396  
2014: 0.396  
2015: 0.396  
2016: 0.396  
2017: 0.396  
2018: 0.37  
2019: 0.37  
2020: 0.37  
2021: 0.37  
2022: 0.37  
2023: 0.37  
2024: 0.37  
2025: 0.37  
2026: 0.396  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_brk7`  
_Description:_ Income below this threshold and above tax bracket 6 is taxed at tax rate 7; income above this threshold is taxed at tax rate 8.  Default value is essentially infinity.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = II_brk6 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `II_rt8`  
_Description:_ The tax rate applied to the portion of taxable income above tax bracket 7.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


## Other Taxes

### Net Investment Income Tax

####  `NIIT_thd`  
_Description:_ If modified AGI is more than this threshold, filing unit is subject to the Net Investment Income Tax.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2014: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2015: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2016: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2017: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2018: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2019: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `NIIT_PT_taxed`  
_Description:_ false ==> partnership and S-corp income excluded from NIIT base; true ==> partnership and S-corp income is in NIIT base.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `NIIT_rt`  
_Description:_ If modified AGI exceeds NIIT_thd, all net investment income is taxed at this rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.038  
2014: 0.038  
2015: 0.038  
2016: 0.038  
2017: 0.038  
2018: 0.038  
2019: 0.038  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


## Refundable Credits

### Earned Income Tax Credit

####  `EITC_c`  
_Description:_ This is the maximum amount of earned income credit taxpayers are eligible for; it depends on how many kids they have.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [0kids, 1kid, 2kids, 3+kids]  
2013: [487.0, 3250.0, 5372.0, 6044.0]  
2014: [496.0, 3305.0, 5460.0, 6143.0]  
2015: [503.0, 3359.0, 5548.0, 6242.0]  
2016: [506.0, 3373.0, 5572.0, 6269.0]  
2017: [510.0, 3400.0, 5616.0, 6318.0]  
2018: [519.0, 3461.0, 5716.0, 6431.0]  
2019: [529.0, 3526.0, 5828.0, 6557.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_rt`  
_Description:_ Pre-phaseout credit is minimum of this rate times earnings and the maximum earned income credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [0kids, 1kid, 2kids, 3+kids]  
2013: [0.0765, 0.34, 0.4, 0.45]  
2014: [0.0765, 0.34, 0.4, 0.45]  
2015: [0.0765, 0.34, 0.4, 0.45]  
2016: [0.0765, 0.34, 0.4, 0.45]  
2017: [0.0765, 0.34, 0.4, 0.45]  
2018: [0.0765, 0.34, 0.4, 0.45]  
2019: [0.0765, 0.34, 0.4, 0.45]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_basic_frac`  
_Description:_ This fraction of EITC_c is always paid as a credit and one minus this fraction is applied to the phasein rate, EITC_rt.  This fraction is zero under current law.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0.0 and max = 1.0  
_Out-of-Range Action:_ error  


####  `EITC_prt`  
_Description:_ Earned income credit begins to decrease at the this rate when AGI is higher than earned income credit phaseout start AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [0kids, 1kid, 2kids, 3+kids]  
2013: [0.0765, 0.1598, 0.2106, 0.2106]  
2014: [0.0765, 0.1598, 0.2106, 0.2106]  
2015: [0.0765, 0.1598, 0.2106, 0.2106]  
2016: [0.0765, 0.1598, 0.2106, 0.2106]  
2017: [0.0765, 0.1598, 0.2106, 0.2106]  
2018: [0.0765, 0.1598, 0.2106, 0.2106]  
2019: [0.0765, 0.1598, 0.2106, 0.2106]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_ps`  
_Description:_ If AGI is higher than this threshold, the amount of EITC will start to decrease at the phaseout rate.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [0kids, 1kid, 2kids, 3+kids]  
2013: [7970.0, 17530.0, 17530.0, 17530.0]  
2014: [8110.0, 17830.0, 17830.0, 17830.0]  
2015: [8250.0, 18150.0, 18150.0, 18150.0]  
2016: [8270.0, 18190.0, 18190.0, 18190.0]  
2017: [8340.0, 18340.0, 18340.0, 18340.0]  
2018: [8490.0, 18660.0, 18660.0, 18660.0]  
2019: [8650.0, 19030.0, 19030.0, 19030.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_ps_MarriedJ`  
_Description:_ This is the additional amount added on the regular phaseout start amount for taxpayers with filling status of married filing jointly.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [0kids, 1kid, 2kids, 3+kids]  
2013: [5340.0, 5340.0, 5340.0, 5340.0]  
2014: [5430.0, 5430.0, 5430.0, 5430.0]  
2015: [5500.0, 5500.0, 5500.0, 5500.0]  
2016: [5550.0, 5550.0, 5550.0, 5550.0]  
2017: [5590.0, 5590.0, 5590.0, 5590.0]  
2018: [5680.0, 5690.0, 5690.0, 5690.0]  
2019: [5800.0, 5790.0, 5790.0, 5790.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_MinEligAge`  
_Description:_ For a childless filing unit, at least one individual's age needs to be no less than this age (but no greater than the EITC_MaxEligAge) in order to be eligible for an earned income tax credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 25  
2014: 25  
2015: 25  
2016: 25  
2017: 25  
2018: 25  
2019: 25  
_Valid Range:_ min = 0 and max = 125  
_Out-of-Range Action:_ error  


####  `EITC_MaxEligAge`  
_Description:_ For a childless filing unit, at least one individual's age needs to be no greater than this age (but no less than the EITC_MinEligAge) in order to be eligible for an earned income tax credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 64  
2014: 64  
2015: 64  
2016: 64  
2017: 64  
2018: 64  
2019: 64  
_Valid Range:_ min = 0 and max = 125  
_Out-of-Range Action:_ error  


####  `EITC_InvestIncome_c`  
_Description:_ The EITC amount is reduced when investment income exceeds this ceiling.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 3300.0  
2014: 3350.0  
2015: 3400.0  
2016: 3400.0  
2017: 3450.0  
2018: 3500.0  
2019: 3600.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_excess_InvestIncome_rt`  
_Description:_ The EITC amount is reduced at this rate per dollar of investment income exceeding the ceiling.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `EITC_indiv`  
_Description:_ Current-law value is false implying EITC is filing-unit based; a value of true implies EITC is computed for each individual wage earner.  The additional phaseout start for joint filers is not affected by this parameter, nor are investment income and age eligibilty rules.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `EITC_sep_filers_elig`  
_Description:_ Current-law value is false, implying ineligibility.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


### New Refundable Child Tax Credit

####  `CTC_new_c`  
_Description:_ In addition to all credits currently available for dependents, this parameter gives each qualifying child a new refundable credit with this maximum amount.  
_Notes:_ Child age qualification for the new child tax credit is the same as under current-law Child Tax Credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_c_under6_bonus`  
_Description:_ The maximum amount of the new refundable child tax credit allowed for each child is increased by this amount for qualifying children under 6 years old.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_for_all`  
_Description:_ The maximum amount of the new refundable child tax credit does not depend on AGI when true; otherwise, see CTC_new_rt.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `CTC_new_rt`  
_Description:_ The maximum amount of the new child tax credit is increased at this rate per dollar of positive AGI until CTC_new_c times the number of qualified children is reached if CTC_new_for_all is false; if CTC_new_for_all is true, there is no AGI limitation to the maximum amount.  
_Notes:_ Child age qualification for the new child tax credit is the same as under current-law Child Tax Credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_ps`  
_Description:_ The total amount of new child tax credit is reduced for taxpayers with AGI higher than this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_prt`  
_Description:_ The total amount of the new child tax credit is reduced at this rate per dollar exceeding the phaseout starting AGI, CTC_new_ps.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_refund_limited`  
_Description:_ Specifies whether the new child tax credit refund is limited by the new child tax credit refund limit rate (_CTC_new_refund_limit_payroll_rt).  
_Notes:_ Set this parameter to true to limit the refundability or false to allow full refundability for all taxpayers.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `CTC_new_refund_limit_payroll_rt`  
_Description:_ The fraction of payroll taxes (employee plus employer shares, but excluding all Medicare payroll taxes) that serves as a limit to the amount of new child tax credit that can be refunded.  
_Notes:_ Set this parameter to zero for no refundability; set it to 9e99 for unlimited refundability for taxpayers with payroll tax liabilities.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CTC_new_refund_limited_all_payroll`  
_Description:_ Specifies whether the new child tax credit refund limit rate (_CTC_new_refund_limit_payroll_rt) applies to all FICA taxes (true) or just OASDI taxes (false).  
_Notes:_ If the new CTC is limited, set this parameter to true to limit the refundability to all FICA taxes or false to limit refundabiity to OASDI taxes.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


### Personal Refundable Credit

####  `II_credit`  
_Description:_ This credit amount is fully refundable and is phased out based on AGI. It is available to tax units who would otherwise not file.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `II_credit_ps`  
_Description:_ The personal refundable credit amount will be reduced for taxpayers with AGI higher than this threshold level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `II_credit_prt`  
_Description:_ The personal refundable credit amount will be reduced at this rate for each dollar of AGI exceeding the II_credit_ps threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


### Refundable Child and Dependent Care Credit

####  `CDCC_new_c`  
_Description:_ The maximum refundable credit allowed for each qualifying dependent.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CDCC_new_deps_max`  
_Description:_ The refundable child & dependent care credit will be applied up to this many dependents.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 10  
2014: 10  
2015: 10  
2016: 10  
2017: 10  
2018: 10  
2019: 10  
_Valid Range:_ min = 0 and max = 10  
_Out-of-Range Action:_ error  


####  `CDCC_new_frac`  
_Description:_ Child care costs are multiplied by this fraction to calculate the refundable child & dependent care credit amount.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1.0  
_Out-of-Range Action:_ error  


####  `CDCC_new_ps`  
_Description:_ The total amount of the refundable child & dependent care credit is reduced for taxpayers with AGI higher than this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CDCC_new_prt`  
_Description:_ The total amount of the refundable child & dependent care credit is reduced at this rate per dollar exceeding the phaseout starting AGI, CDCC_new_ps.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### Refundable Payroll Tax Credit

####  `RPTC_c`  
_Description:_ This is the maximum amount of the refundable payroll tax credit for each taxpayer/spouse.  
_Notes:_ Positive values of RPTC_c and RPTC_rt can be used to emulate a payroll tax exemption, the implied value of which is RPTC_c divided by RPTC_rt.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `RPTC_rt`  
_Description:_ Pre-phaseout credit is minimum of this rate times earnings and the maximum refundable payroll tax credit, where earnings is defined as in FICA and SECA.  
_Notes:_ Positive values of RPTC_c and RPTC_rt can be used to emulate a payroll tax exemption, the implied value of which is RPTC_c divided by RPTC_rt.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


## Surtaxes

### Lump-Sum Tax

####  `LST`  
_Description:_ The lump-sum tax is levied on every member of a tax filing unit. The lump-sum tax is included only in combined taxes; it is not included in income or payroll taxes.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = -9e+99 and max = 9e+99  
_Out-of-Range Action:_ error  


### New AGI Surtax

####  `AGI_surtax_trt`  
_Description:_ The surtax rate is applied to the portion of Adjusted Gross Income above the AGI surtax threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `AGI_surtax_thd`  
_Description:_ The aggregate gross income above this AGI surtax threshold is taxed at surtax rate on AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### New Minimum Tax

####  `FST_AGI_trt`  
_Description:_ Individual income taxes and the employee share of payroll taxes are credited against this minimum tax, so the surtax is the difference between the tax rate times AGI and the credited taxes. The new minimum tax is similar to the Fair Share Tax, except that no credits are exempted from the base.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `FST_AGI_thd_lo`  
_Description:_ A taxpayer is only subject to the new minimum tax if they exceed this level of AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2014: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2015: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2016: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2017: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2018: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2019: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
_Valid Range:_ min = 0 and max = FST_AGI_thd_hi  
_Out-of-Range Action:_ error  


####  `FST_AGI_thd_hi`  
_Description:_ The new minimum tax will be fully phased in at this level of AGI. If there is no phase-in, this upper threshold should be set equal to the lower AGI threshold.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2014: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2015: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2016: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2017: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2018: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2019: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
_Valid Range:_ min = FST_AGI_thd_lo and max = 9e+99  
_Out-of-Range Action:_ error  


## Universal Basic Income

### UBI Benefits

####  `UBI_u18`  
_Description:_ UBI benefit provided to people under 18.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `UBI_1820`  
_Description:_ UBI benefit provided to people 18-20 years of age.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `UBI_21`  
_Description:_ UBI benefit provided to people 21 and over.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


### UBI Taxability

####  `UBI_ecrt`  
_Description:_ One minus this fraction of UBI benefits are taxable and will be added to AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


## Benefits

### Benefit Repeal

####  `BEN_ssi_repeal`  
_Description:_ SSI benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_housing_repeal`  
_Description:_ Housing benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_snap_repeal`  
_Description:_ SNAP benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_tanf_repeal`  
_Description:_ TANF benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_vet_repeal`  
_Description:_ Veterans benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_wic_repeal`  
_Description:_ WIC benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_mcare_repeal`  
_Description:_ Medicare benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_mcaid_repeal`  
_Description:_ Medicaid benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_oasdi_repeal`  
_Description:_ Social Security benefits (e02400) can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_ui_repeal`  
_Description:_ Unemployment insurance benefits (e02300) can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `BEN_other_repeal`  
_Description:_ Other benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_ _PUF data:_ False _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


## Other Parameters (not in Tax-Brain webapp)

####  `SS_percentage1`  
_Description:_ Under current law if their provisional income is above the first threshold for Social Security taxability but below the second threshold, taxpayers need to apply this fraction to both the excess of their provisional income over the first threshold and their Social Security benefits, and then include the smaller one in their AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.5  
2014: 0.5  
2015: 0.5  
2016: 0.5  
2017: 0.5  
2018: 0.5  
2019: 0.5  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `SS_percentage2`  
_Description:_ Under current law if their provisional income is above the second threshold for Social Security taxability, taxpayers need to apply this fraction to both the excess of their provisional income over the second threshold and their social security benefits, and then include the smaller one in their AGI.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.85  
2014: 0.85  
2015: 0.85  
2016: 0.85  
2017: 0.85  
2018: 0.85  
2019: 0.85  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `II_em_ps`  
_Description:_ If taxpayers' AGI is above this level, their personal exemption will start to decrease at the personal exemption phaseout rate (PEP provision).  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [250000.0, 300000.0, 150000.0, 275000.0, 300000.0]  
2014: [254200.0, 305050.0, 152525.0, 279650.0, 305050.0]  
2015: [258250.0, 309900.0, 154950.0, 284040.0, 309900.0]  
2016: [259400.0, 311300.0, 155650.0, 285350.0, 311300.0]  
2017: [261500.0, 313800.0, 156900.0, 287650.0, 313800.0]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `STD_Dep`  
_Description:_ This is the maximum standard deduction for dependents.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1050.0  
2016: 1050.0  
2017: 1050.0  
2018: 1050.0  
2019: 1100.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `STD_allow_charity_ded_nonitemizers`  
_Description:_ Extends the charitable contributions deduction to taxpayers who take the standard deduction. The same ceilings, floor, and haircuts applied to itemized deduction for charitable contributions also apply here.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error  


####  `AMT_child_em`  
_Description:_ The child's AMT exemption is capped by this amount plus the child's earned income.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 7150.0  
2014: 7250.0  
2015: 7400.0  
2016: 7400.0  
2017: 7500.0  
2018: 7600.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `AMT_child_em_c_age`  
_Description:_ Individuals under this age must use the child AMT exemption rules.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 18  
2014: 18  
2015: 18  
2016: 18  
2017: 18  
2018: 18  
2019: 18  
_Valid Range:_ min = 0 and max = 30  
_Out-of-Range Action:_ error  


####  `AMT_em_pe`  
_Description:_ The AMT exemption is entirely disallowed beyond this AMT taxable income level for individuals who are married but filing separately.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 238550.0  
2014: 242450.0  
2015: 246250.0  
2016: 247450.0  
2017: 249450.0  
2018: 718800.0  
2019: 733700.0  
2020: 744998.98  
2021: 750437.47  
2022: 757566.63  
2023: 769536.18  
2024: 784388.23  
2025: 800075.99  
2026: 288949.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `LLC_Expense_c`  
_Description:_ The maximum expense eligible for lifetime learning credit, per child.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 10000.0  
2014: 10000.0  
2015: 10000.0  
2016: 10000.0  
2017: 10000.0  
2018: 10000.0  
2019: 10000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ETC_pe_Single`  
_Description:_ The education tax credit will be zero for those taxpayers of single filing status with modified AGI (in thousands) higher than this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 63.0  
2014: 64.0  
2015: 65.0  
2016: 65.0  
2017: 66.0  
2018: 67.0  
2019: 68.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `ETC_pe_Married`  
_Description:_ The education tax credit will be zero for those taxpayers of married filing status with modified AGI level (in thousands) higher than this level.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ False  
_Can Be Inflation Indexed:_ True _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 127.0  
2014: 128.0  
2015: 130.0  
2016: 131.0  
2017: 132.0  
2018: 134.0  
2019: 136.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CR_Charity_rt`  
_Description:_ If greater than zero, this decimal fraction represents the portion of total charitable contributions provided as a nonrefundable tax credit.  
_Notes:_ Credit claimed will be (rt) * (e19800 + e20100)  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `CR_Charity_f`  
_Description:_ Only charitable giving in excess of this dollar amount is eligible for the charity credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
 for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error  


####  `CR_Charity_frt`  
_Description:_ Only charitable giving in excess of this decimal fraction of AGI is eligible for the charity credit.  
_Has An Effect When Using:_ _PUF data:_ True _CPS data:_ True  
_Can Be Inflation Indexed:_ False _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  
