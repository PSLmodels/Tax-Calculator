Output variables
================

This section contains documentation of output variables in a format that is easy to search and print.
The output variables are ordered alphabetically by name.
There are no subsections, just a long list of output variables that Tax-Calculator is programmed to calculate.


##  `credit_claim_urn`  
_Description_: Uniform random number used in EITC/ACTC claiming logic, which implies correlated claimning behavior across different credits  
_Datatype_: unchanging_float  


##  `niit`  
_Description_: Net Investment Income Tax from Form 8960  
_Datatype_: float  


##  `combined`  
_Description_: Sum of iitax and payrolltax and lumpsum_tax  
_Datatype_: float  


##  `earned`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `earned_p`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `earned_s`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `eitc`  
_Description_: Earned Income Credit  
_Datatype_: float  


##  `exact`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: int  


##  `expanded_income`  
_Description_: Broad income measure that includes benefit_value_total  
_Datatype_: float  


##  `iitax`  
_Description_: Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output  
_Datatype_: float  


##  `num`  
_Description_: 2 when MARS is 2 (married filing jointly); otherwise 1  
_Datatype_: int  


##  `othertaxes`  
_Description_: Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)  
_Datatype_: float  


##  `payrolltax`  
_Description_: Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was)  
_Datatype_: float  


##  `refund`  
_Description_: Total refundable income tax credits  
_Datatype_: float  


##  `sey`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `standard`  
_Description_: Standard deduction (zero for itemizers)  
_Datatype_: float  


##  `surtax`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `taxbc`  
_Description_: Regular tax on regular taxable income before credits  
_Datatype_: float  


##  `c00100`  
_Description_: Adjusted Gross Income (AGI)  
_Datatype_: float  


##  `c01000`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c02500`  
_Description_: Social security (OASDI) benefits included in AGI  
_Datatype_: float  


##  `c02900`  
_Description_: Total of all 'above the line' income adjustments to get AGI  
_Datatype_: float  


##  `c03260`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c04470`  
_Description_: Itemized deductions after limitations (zero for non-itemizers)  
_Datatype_: float  


##  `c04600`  
_Description_: Personal exemptions after phase-out  
_Datatype_: float  


##  `qbided`  
_Description_: Qualified Business Income (QBI) deduction  
_Datatype_: float  


##  `c04800`  
_Description_: Regular taxable income  
_Datatype_: float  


##  `c05200`  
_Description_: Tax amount from Sch X,Y,Z tables  
_Datatype_: float  


##  `c05700`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c05800`  
_Description_: Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)  
_Datatype_: float  


##  `c07100`  
_Description_: Total non-refundable credits used to reduce positive tax liability  
_Datatype_: float  


##  `c32800`  
_Description_: Child and dependent care expenses capped by policy (not by earnings)  
_Datatype_: float  


##  `c07180`  
_Description_: Nonrefundable credit for child and dependent care expenses from Form 2441  
_Datatype_: float  


##  `CDCC_refund`  
_Description_: Refundable credit for child and dependent care expenses from Form 2441  
_Datatype_: float  


##  `c07200`  
_Description_: Schedule R credit for the elderly and the disabled  
_Datatype_: float  


##  `c07220`  
_Description_: Child tax credit (adjusted) from Form 8812  
_Datatype_: float  


##  `c07230`  
_Description_: Education tax credits non-refundable amount from Form 8863 (includes c87668)  
_Datatype_: float  


##  `c07240`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c07260`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c07300`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c07400`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c07600`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c08000`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c09200`  
_Description_: Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied  
_Datatype_: float  


##  `c09600`  
_Description_: Alternative Minimum Tax (AMT) liability  
_Datatype_: float  


##  `c10960`  
_Description_: American Opportunity Credit refundable amount from Form 8863  
_Datatype_: float  


##  `c11070`  
_Description_: Child tax credit (refunded) from Form 8812  
_Datatype_: float  


##  `c17000`  
_Description_: Sch A: Medical expenses deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c18300`  
_Description_: Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c19200`  
_Description_: Sch A: Interest deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c19700`  
_Description_: Sch A: Charity contributions deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c20500`  
_Description_: Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c20800`  
_Description_: Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)  
_Datatype_: float  


##  `c21040`  
_Description_: Itemized deductions that are phased out  
_Datatype_: float  


##  `c21060`  
_Description_: Itemized deductions before phase-out (zero for non-itemizers)  
_Datatype_: float  


##  `c23650`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c59660`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `c62100`  
_Description_: Alternative Minimum Tax (AMT) taxable income  
_Datatype_: float  


##  `c87668`  
_Description_: American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)  
_Datatype_: float  


##  `care_deduction`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `ctc_new`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `odc`  
_Description_: Other Dependent Credit  
_Datatype_: float  


##  `ctc_total`  
_Description_: Total CTC amount (c07220 + c11070 + odc + ctc_new)  
_Datatype_: float  


##  `ctc_nonrefundable`  
_Description_: Portion of total CTC amount that is nonrefundable  
_Datatype_: float  


##  `ctc_refundable`  
_Description_: Portion of total CTC amount that is refundable  
_Datatype_: float  


##  `personal_refundable_credit`  
_Description_: Personal refundable credit  
_Datatype_: float  


##  `recovery_rebate_credit`  
_Description_: Recovery Rebate Credit, from American Rescue Plan Act of 2021  
_Datatype_: float  


##  `personal_nonrefundable_credit`  
_Description_: Personal nonrefundable credit  
_Datatype_: float  


##  `charity_credit`  
_Description_: Credit for charitable giving  
_Datatype_: float  


##  `dwks10`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `dwks13`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `dwks14`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `dwks18`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `dwks43`  
_Description_: separate tax on long-term capital gains and qualified dividends  
_Datatype_: float  


##  `fstax`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `invinc_agi_ec`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `invinc_ec_base`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `lumpsum_tax`  
_Description_: Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output  
_Datatype_: float  


##  `pre_c04600`  
_Description_: Personal exemption before phase-out  
_Datatype_: float  


##  `codtc_limited`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `ptax_amc`  
_Description_: Additional Medicare Tax from Form 8959 (included in othertaxes and iitax)  
_Datatype_: float  


##  `ptax_er_p`  
_Description_: Taxpayer's employer share of OASDI+HI FICA payroll tax on wages and salaries; excludes self-employment tax (which has no employer share) and is therefore invariant under the soi_iitax bucketing switch  
_Datatype_: float  


##  `ptax_er_s`  
_Description_: Spouse's employer share of OASDI+HI FICA payroll tax on wages and salaries; excludes self-employment tax (which has no employer share) and is therefore invariant under the soi_iitax bucketing switch  
_Datatype_: float  


##  `ptax_oasdi`  
_Description_: Employee + employer OASDI FICA tax plus self-employment tax  
_Datatype_: float  


##  `ptax_was`  
_Description_: Employee + employer OASDI + HI FICA tax  
_Datatype_: float  


##  `setax`  
_Description_: Self-employment tax (included in othertaxes and iitax)  
_Datatype_: float  


##  `ymod`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `ymod1`  
_Description_: search taxcalc/calcfunctions.py for how calculated and used  
_Datatype_: float  


##  `senior_deduction`  
_Description_: Deduction for elderly head and/or spouse  
_Datatype_: float  


##  `auto_loan_interest_deduction`  
_Description_: Deduction for payment of qualified auto loan interest  
_Datatype_: float  


##  `overtime_income_deduction`  
_Description_: Deduction for qualified overtime income  
_Datatype_: float  


##  `tip_income_deduction`  
_Description_: Deduction for qualified tip income  
_Datatype_: float  


##  `ubi`  
_Description_: Universal Basic Income benefit for filing unit  
_Datatype_: float  


##  `taxable_ubi`  
_Description_: Amount of UBI benefit included in AGI  
_Datatype_: float  


##  `nontaxable_ubi`  
_Description_: Amount of UBI benefit excluded from AGI  
_Datatype_: float  


##  `mtr_paytax`  
_Description_: Marginal payroll tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype_: float  


##  `mtr_inctax`  
_Description_: Marginal income tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype_: float  


##  `aftertax_income`  
_Description_: After tax income is equal to expanded_income minus combined  
_Datatype_: float  


##  `benefit_cost_total`  
_Description_: Government cost of all benefits received by tax unit  
_Datatype_: float  


##  `benefit_value_total`  
_Description_: Consumption value of all benefits received by tax unit, which is included in expanded_income  
_Datatype_: float  
