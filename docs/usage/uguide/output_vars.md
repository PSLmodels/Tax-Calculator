Output variables
================

This section contains documentation of output variables in a format that is easy to search and print.
The output variables are ordered alphabetically by name.
There are no subsections, just a long list of output variables that Tax-Calculator is programmed to calculate.

_Output Variable Name:_ **aftertax_income**  
_Description:_ After tax income is equal to expanded_income minus combined  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **benefit_cost_total**  
_Description:_ Government cost of all benefits received by tax unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **benefit_value_total**  
_Description:_ Consumption value of all benefits received by tax unit, which is included in expanded_income  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c00100**  
_Description:_ Adjusted Gross Income (AGI)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 37  
2018-20??: 1040 line 7

_Output Variable Name:_ **c01000**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c02500**  
_Description:_ Social security (OASDI) benefits included in AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 20b

_Output Variable Name:_ **c02900**  
_Description:_ Total of all 'above the line' income adjustments to get AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 36

_Output Variable Name:_ **c03260**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c04470**  
_Description:_ Itemized deductions after phase-out (zero for non-itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8

_Output Variable Name:_ **c04600**  
_Description:_ Personal exemptions after phase-out  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 42  
2018-20??:

_Output Variable Name:_ **c04800**  
_Description:_ Regular taxable income  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 43  
2018-20??: 1040 line 10

_Output Variable Name:_ **c05200**  
_Description:_ Tax amount from Sch X,Y,X tables  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c05700**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c05800**  
_Description:_ Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 46  
2014-2016: 1040 line 47

_Output Variable Name:_ **c07100**  
_Description:_ Total non-refundable credits used to reduce positive tax liability  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 46 minus 1040 line 55  
2014-2016: 1040 line 47 minus 1040 line 56

_Output Variable Name:_ **c07180**  
_Description:_ Credit for child and dependent care expenses from Form 2441  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 48  
2014-2016: 1040 line 49

_Output Variable Name:_ **c07200**  
_Description:_ Schedule R credit for the elderly and the disabled  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07220**  
_Description:_ Child tax credit (adjusted) from Form 8812  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 51  
2014-2016: 1040 line 52

_Output Variable Name:_ **c07230**  
_Description:_ Education tax credits non-refundable amount from Form 8863 (includes c87668)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 8863 line 19 and 1040 line 49  
2014-2016: 8863 line 19 and 1040 line 50

_Output Variable Name:_ **c07240**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07260**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07300**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07400**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07600**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c08000**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c09200**  
_Description:_ Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 61  
2014-2016: 1040 line 63

_Output Variable Name:_ **c09600**  
_Description:_ Alternative Minimum Tax (AMT) liability  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 45

_Output Variable Name:_ **c10960**  
_Description:_ American Opportunity Credit refundable amount from Form 8863  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 8863 line 8 and 1040 line 66  
2014-2016: 8863 line 8 and 1040 line 68

_Output Variable Name:_ **c11070**  
_Description:_ Child tax credit (refunded) from Form 8812  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 65  
2014-2016: 1040 line 67

_Output Variable Name:_ **c17000**  
_Description:_ Sch A: Medical expenses deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c18300**  
_Description:_ Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c19200**  
_Description:_ Sch A: Interest deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c19700**  
_Description:_ Sch A: Charity contributions deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c20500**  
_Description:_ Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c20800**  
_Description:_ Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c21040**  
_Description:_ Itemized deductions that are phased out  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c21060**  
_Description:_ Itemized deductions before phase-out (zero for non-itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c23650**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c59660**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c62100**  
_Description:_ Alternative Minimum Tax (AMT) taxable income  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 6251 line 28

_Output Variable Name:_ **c87668**  
_Description:_ American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **care_deduction**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **charity_credit**  
_Description:_ Credit for charitable giving  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **codtc_limited**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **combined**  
_Description:_ Sum of iitax and payrolltax and lumpsum_tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ctc_new**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks10**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks13**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks14**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks19**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e17500_capped**  
_Description:_ Sch A: Medical expenses, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e18400_capped**  
_Description:_ Sch A: State and local income taxes deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e18500_capped**  
_Description:_ Sch A: State and local real estate taxes deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e19200_capped**  
_Description:_ Sch A: Interest deduction deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e19800_capped**  
_Description:_ Sch A: Charity cash contributions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e20100_capped**  
_Description:_ Sch A: Charity noncash contributions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e20400_capped**  
_Description:_ Sch A: Gross miscellaneous deductions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned_p**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned_s**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **eitc**  
_Description:_ Earned Income Credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 64a  
2014-2016: 1040 line 66a

_Output Variable Name:_ **exact**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ integer  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **expanded_income**  
_Description:_ Broad income measure that includes benefit_value_total  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **fstax**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **g20500_capped**  
_Description:_ Sch A: Gross casualty or theft loss deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **iitax**  
_Description:_ Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 61 minus line 56 minus line 60a  
2014-2016: 1040 line 63 minus line 57 minus line 62a

_Output Variable Name:_ **invinc_agi_ec**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **invinc_ec_base**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **lumpsum_tax**  
_Description:_ Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **mtr_inctax**  
_Description:_ Marginal income tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **mtr_paytax**  
_Description:_ Marginal payroll tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **niit**  
_Description:_ Net Investment Income Tax from Form 8960  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 60b  
2014-2016: 1040 line 62b

_Output Variable Name:_ **nontaxable_ubi**  
_Description:_ Amount of UBI benefit excluded from AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **num**  
_Description:_ 2 when MARS is 2 (married filing jointly); otherwise 1  
_Datatype:_ integer  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Output Variable Name:_ **odc**  
_Description:_ Other Dependent Credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **othertaxes**  
_Description:_ Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: sum of 1040 lines 57 through 60  
2014-2016: sum of 1040 lines 58 through 62

_Output Variable Name:_ **payrolltax**  
_Description:_ Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDI+HI FICA plus 1040 lines 56 and 60a  
2014-2016: OASDI+HI FICA plus 1040 lines 57 and 62a

_Output Variable Name:_ **personal_nonrefundable_credit**  
_Description:_ Personal nonrefundable credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **personal_refundable_credit**  
_Description:_ Personal refundable credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **pre_c04600**  
_Description:_ Personal exemption before phase-out  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ptax_amc**  
_Description:_ Additional Medicare Tax from Form 8959 (included in payrolltax)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 60a  
2014-2016: 1040 line 62a

_Output Variable Name:_ **ptax_oasdi**  
_Description:_ Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDI FICA plus 1040 line 56  
2014-2016: OASDI FICA plus 1040 line 57

_Output Variable Name:_ **ptax_was**  
_Description:_ Employee + employer OASDI + HI FICA tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDHI FICA  
2014-2016: OASDHI FICA

_Output Variable Name:_ **qbided**  
_Description:_ Qualified Business Income (QBI) deduction  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017:  
2018-20??: 1040 line 9

_Output Variable Name:_ **refund**  
_Description:_ Total refundable income tax credits  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc**  
_Description:_ Refundable Payroll Tax Credit for filing unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc_p**  
_Description:_ Refundable Payroll Tax Credit for taxpayer  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc_s**  
_Description:_ Refundable Payroll Tax Credit for spouse  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **sep**  
_Description:_ 2 when MARS is 3 (married filing separately); otherwise 1  
_Datatype:_ integer  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Output Variable Name:_ **setax**  
_Description:_ Self-employment tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 56  
2014-2016: 1040 line 57

_Output Variable Name:_ **sey**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **standard**  
_Description:_ Standard deduction (zero for itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8

_Output Variable Name:_ **surtax**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **taxable_ubi**  
_Description:_ Amount of UBI benefit included in AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **taxbc**  
_Description:_ Regular tax on regular taxable income before credits  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 44

_Output Variable Name:_ **ubi**  
_Description:_ Universal Basic Income benefit for filing unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **was_plus_sey_p**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **was_plus_sey_s**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ymod**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ymod1**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable