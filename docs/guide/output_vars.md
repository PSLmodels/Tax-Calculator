Output variables
================

This section contains documentation of output variables in a format that is easy to search and print.
The output variables are ordered alphabetically by name.
There are no subsections, just a long list of output variables that Tax-Calculator is programmed to calculate.


##  `niit`  
_Description_: Net Investment Income Tax from Form 8960  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 60b  
2014-2016: 1040 line 62b  


##  `combined`  
_Description_: Sum of iitax and payrolltax and lumpsum_tax  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `earned`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `earned_p`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `earned_s`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `was_plus_sey_p`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `was_plus_sey_s`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `eitc`  
_Description_: Earned Income Credit  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 64a  
2014-2016: 1040 line 66a  


##  `rptc`  
_Description_: Refundable Payroll Tax Credit for filing unit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `rptc_p`  
_Description_: Refundable Payroll Tax Credit for taxpayer  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `rptc_s`  
_Description_: Refundable Payroll Tax Credit for spouse  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `exact`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: int  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `expanded_income`  
_Description_: Broad income measure that includes benefit_value_total  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `iitax`  
_Description_: Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 61 minus line 56 minus line 60a  
2014-2016: 1040 line 63 minus line 57 minus line 62a  


##  `num`  
_Description_: 2 when MARS is 2 (married filing jointly); otherwise 1  
_Datatype_: int  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5  


##  `othertaxes`  
_Description_: Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: sum of 1040 lines 57 through 60  
2014-2016: sum of 1040 lines 58 through 62  


##  `payrolltax`  
_Description_: Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: OASDI+HI FICA plus 1040 lines 56 and 60a  
2014-2016: OASDI+HI FICA plus 1040 lines 57 and 62a  


##  `refund`  
_Description_: Total refundable income tax credits  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `sep`  
_Description_: 2 when MARS is 3 (married filing separately); otherwise 1  
_Datatype_: int  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5  


##  `sey`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `standard`  
_Description_: Standard deduction (zero for itemizers)  
_Datatype_: float  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8  


##  `surtax`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `taxbc`  
_Description_: Regular tax on regular taxable income before credits  
_Datatype_: float  
_IRS Form Location:_  
2013-2016: 1040 line 44  


##  `c00100`  
_Description_: Adjusted Gross Income (AGI)  
_Datatype_: float  
_IRS Form Location:_  
2013-2017: 1040 line 37  
2018-20??: 1040 line 7  


##  `c01000`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c02500`  
_Description_: Social security (OASDI) benefits included in AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-2016: 1040 line 20b  


##  `c02900`  
_Description_: Total of all 'above the line' income adjustments to get AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-2016: 1040 line 36  


##  `c03260`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c04470`  
_Description_: Itemized deductions after phase-out (zero for non-itemizers)  
_Datatype_: float  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8  


##  `c04600`  
_Description_: Personal exemptions after phase-out  
_Datatype_: float  
_IRS Form Location:_  
2013-2017: 1040 line 42  
2018-20??:   


##  `qbided`  
_Description_: Qualified Business Income (QBI) deduction  
_Datatype_: float  
_IRS Form Location:_  
2013-2017:   
2018-20??: 1040 line 9  


##  `c04800`  
_Description_: Regular taxable income  
_Datatype_: float  
_IRS Form Location:_  
2013-2017: 1040 line 43  
2018-20??: 1040 line 10  


##  `c05200`  
_Description_: Tax amount from Sch X,Y,X tables  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c05700`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c05800`  
_Description_: Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 46  
2014-2016: 1040 line 47  


##  `c07100`  
_Description_: Total non-refundable credits used to reduce positive tax liability  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 46 minus 1040 line 55  
2014-2016: 1040 line 47 minus 1040 line 56  


##  `c07180`  
_Description_: Credit for child and dependent care expenses from Form 2441  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 48  
2014-2016: 1040 line 49  


##  `c07200`  
_Description_: Schedule R credit for the elderly and the disabled  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c07220`  
_Description_: Child tax credit (adjusted) from Form 8812  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 51  
2014-2016: 1040 line 52  


##  `c07230`  
_Description_: Education tax credits non-refundable amount from Form 8863 (includes c87668)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 8863 line 19 and 1040 line 49  
2014-2016: 8863 line 19 and 1040 line 50  


##  `c07240`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c07260`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c07300`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c07400`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c07600`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c08000`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c09200`  
_Description_: Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 61  
2014-2016: 1040 line 63  


##  `c09600`  
_Description_: Alternative Minimum Tax (AMT) liability  
_Datatype_: float  
_IRS Form Location:_  
2013-2016: 1040 line 45  


##  `c10960`  
_Description_: American Opportunity Credit refundable amount from Form 8863  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 8863 line 8 and 1040 line 66  
2014-2016: 8863 line 8 and 1040 line 68  


##  `c11070`  
_Description_: Child tax credit (refunded) from Form 8812  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 65  
2014-2016: 1040 line 67  


##  `c17000`  
_Description_: Sch A: Medical expenses deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e17500_capped`  
_Description_: Sch A: Medical expenses, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c18300`  
_Description_: Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e18400_capped`  
_Description_: Sch A: State and local income taxes deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e18500_capped`  
_Description_: Sch A: State and local real estate taxes deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c19200`  
_Description_: Sch A: Interest deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e19200_capped`  
_Description_: Sch A: Interest deduction deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c19700`  
_Description_: Sch A: Charity contributions deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e19800_capped`  
_Description_: Sch A: Charity cash contributions deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e20100_capped`  
_Description_: Sch A: Charity noncash contributions deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c20500`  
_Description_: Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `g20500_capped`  
_Description_: Sch A: Gross casualty or theft loss deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c20800`  
_Description_: Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `e20400_capped`  
_Description_: Sch A: Gross miscellaneous deductions deductible, capped as a decimal fraction of AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c21040`  
_Description_: Itemized deductions that are phased out  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c21060`  
_Description_: Itemized deductions before phase-out (zero for non-itemizers)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c23650`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c59660`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `c62100`  
_Description_: Alternative Minimum Tax (AMT) taxable income  
_Datatype_: float  
_IRS Form Location:_  
2013-2016: 6251 line 28  


##  `c87668`  
_Description_: American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `care_deduction`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `ctc_new`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `cdcc_new`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `odc`  
_Description_: Other Dependent Credit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `personal_refundable_credit`  
_Description_: Personal refundable credit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `personal_nonrefundable_credit`  
_Description_: Personal nonrefundable credit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `charity_credit`  
_Description_: Credit for charitable giving  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `dwks10`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `dwks13`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `dwks14`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `dwks19`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `fstax`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `invinc_agi_ec`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `invinc_ec_base`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `lumpsum_tax`  
_Description_: Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `pre_c04600`  
_Description_: Personal exemption before phase-out  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `codtc_limited`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `ptax_amc`  
_Description_: Additional Medicare Tax from Form 8959 (included in payrolltax)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 60a  
2014-2016: 1040 line 62a  


##  `ptax_oasdi`  
_Description_: Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: OASDI FICA plus 1040 line 56  
2014-2016: OASDI FICA plus 1040 line 57  


##  `ptax_was`  
_Description_: Employee + employer OASDI + HI FICA tax  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: OASDHI FICA  
2014-2016: OASDHI FICA  


##  `setax`  
_Description_: Self-employment tax  
_Datatype_: float  
_IRS Form Location:_  
2013-2013: 1040 line 56  
2014-2016: 1040 line 57  


##  `ymod`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `ymod1`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `ubi`  
_Description_: Universal Basic Income benefit for filing unit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `taxable_ubi`  
_Description_: Amount of UBI benefit included in AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `nontaxable_ubi`  
_Description_: Amount of UBI benefit excluded from AGI  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `mtr_paytax`  
_Description_: Marginal payroll tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `mtr_inctax`  
_Description_: Marginal income tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `aftertax_income`  
_Description_: After tax income is equal to expanded_income minus combined  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `benefit_cost_total`  
_Description_: Government cost of all benefits received by tax unit  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  


##  `benefit_value_total`  
_Description_: Consumption value of all benefits received by tax unit, which is included in expanded_income  
_Datatype_: float  
_IRS Form Location:_  
2013-20??: calculated variable  
