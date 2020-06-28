Input variables
===============

This section contains documentation of input variables in a format that is easy to search and print.
The input variables are ordered alphabetically by name.
There are no subsections, just a long list of input variables that Tax-Calculator is programmed to use in its calculations.
The Availability information indicates which input data files contain the variable.

_Input Variable Name:_ **DSI**  
_Description:_ 1 if claimed as dependent on another return; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 6a

_Input Variable Name:_ **EIC**  
_Description:_ number of EIC qualifying children (range: 0 to 3)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch EIC

_Input Variable Name:_ **FLPDYR**  
_Description:_ Calendar year for which taxes are calculated  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040

_Input Variable Name:_ **MARS**  
**_Required Input Variable_**  
_Description:_ Filing (marital) status: line number of the checked box [1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er)]  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Input Variable Name:_ **MIDR**  
_Description:_ 1 if separately filing spouse itemizes; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 39b

_Input Variable Name:_ **PT_SSTB_income**  
_Description:_ Value of one implies business income is from a specified service trade or business (SSTB); value of zero implies business income is from a qualified trade or business  
_Datatype:_ integer  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **PT_binc_w2_wages**  
_Description:_ Filing unit's share of total W-2 wages paid by the pass-through business  
_Datatype:_ real  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **PT_ubia_property**  
_Description:_ Filing unit's share of total business property owned by the pass-through business  
_Datatype:_ real  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **RECID**  
**_Required Input Variable_**  
_Description:_ Unique numeric identifier for filing unit; appears as RECID variable in tc CLI minimal output  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: private info

_Input Variable Name:_ **XTOT**  
_Description:_ Total number of exemptions for filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 6d

_Input Variable Name:_ **a_lineno**  
_Description:_ CPS line number for the person record of the head of the tax filing unit (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **age_head**  
_Description:_ Age in years of taxpayer (i.e. primary adult)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **age_spouse**  
_Description:_ Age in years of spouse (i.e. secondary adult if present)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **agi_bin**  
_Description:_ Historical AGI category used in data extrapolation  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: not used in tax calculations

_Input Variable Name:_ **blind_head**  
_Description:_ 1 if taxpayer is blind; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 39a

_Input Variable Name:_ **blind_spouse**  
_Description:_ 1 if spouse is blind; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 39a

_Input Variable Name:_ **cmbtp**  
_Description:_ Estimate of income on (AMT) Form 6251 but not in AGI  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251 and 1040

_Input Variable Name:_ **data_source**  
_Description:_ 1 if unit is created primarily from IRS-SOI PUF data; 0 if created primarily from CPS data (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **e00200**  
_Description:_ Wages, salaries, and tips for filing unit net of pension contributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7

_Input Variable Name:_ **e00200p**  
_Description:_ Wages, salaries, and tips for taxpayer net of pension contributions (pencon_p)  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7 component

_Input Variable Name:_ **e00200s**  
_Description:_ Wages, salaries, and tips for spouse net of pension contributions (pencon_s)  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7 component

_Input Variable Name:_ **e00300**  
_Description:_ Taxable interest income  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 8a

_Input Variable Name:_ **e00400**  
_Description:_ Tax-exempt interest income  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 8b

_Input Variable Name:_ **e00600**  
_Description:_ Ordinary dividends included in AGI  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 9a

_Input Variable Name:_ **e00650**  
_Description:_ Qualified dividends included in ordinary dividends  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 9b

_Input Variable Name:_ **e00700**  
_Description:_ Taxable refunds of state and local income taxes  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 10

_Input Variable Name:_ **e00800**  
_Description:_ Alimony received  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 11

_Input Variable Name:_ **e00900**  
_Description:_ Sch C business net profit/loss for filing unit  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12

_Input Variable Name:_ **e00900p**  
_Description:_ Sch C business net profit/loss for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12 component

_Input Variable Name:_ **e00900s**  
_Description:_ Sch C business net profit/loss for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12 component

_Input Variable Name:_ **e01100**  
_Description:_ Capital gain distributions not reported on Sch D  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 13

_Input Variable Name:_ **e01200**  
_Description:_ Other net gain/loss from Form 4797  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 14

_Input Variable Name:_ **e01400**  
_Description:_ Taxable IRA distributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 15b

_Input Variable Name:_ **e01500**  
_Description:_ Total pensions and annuities  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 16a

_Input Variable Name:_ **e01700**  
_Description:_ Taxable pensions and annuities  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 16b

_Input Variable Name:_ **e02000**  
_Description:_ Sch E total rental, royalty, partnership, S-corporation, etc, income/loss (includes e26270 and e27200)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 17

_Input Variable Name:_ **e02100**  
_Description:_ Farm net income/loss for filing unit from Sch F  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18

_Input Variable Name:_ **e02100p**  
_Description:_ Farm net income/loss for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18 component

_Input Variable Name:_ **e02100s**  
_Description:_ Farm net income/loss for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18 component

_Input Variable Name:_ **e02300**  
_Description:_ Unemployment insurance benefits  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 19

_Input Variable Name:_ **e02400**  
_Description:_ Total social security (OASDI) benefits  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 20a

_Input Variable Name:_ **e03150**  
_Description:_ Total deductible IRA contributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 32

_Input Variable Name:_ **e03210**  
_Description:_ Student loan interest  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 33

_Input Variable Name:_ **e03220**  
_Description:_ Educator expenses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 23

_Input Variable Name:_ **e03230**  
_Description:_ Tuition and fees from Form 8917  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 34

_Input Variable Name:_ **e03240**  
_Description:_ Domestic production activities from Form 8903  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 35

_Input Variable Name:_ **e03270**  
_Description:_ Self-employed health insurance deduction  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 29

_Input Variable Name:_ **e03290**  
_Description:_ Health savings account deduction from Form 8889  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 25

_Input Variable Name:_ **e03300**  
_Description:_ Contributions to SEP, SIMPLE and qualified plans  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 28

_Input Variable Name:_ **e03400**  
_Description:_ Penalty on early withdrawal of savings  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 30

_Input Variable Name:_ **e03500**  
_Description:_ Alimony paid  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 31a

_Input Variable Name:_ **e07240**  
_Description:_ Retirement savings contributions credit from Form 8880  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 50  
2014-2016: 1040 line 51

_Input Variable Name:_ **e07260**  
_Description:_ Residential energy credit from Form 5695  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 52  
2014-2016: 1040 line 53

_Input Variable Name:_ **e07300**  
_Description:_ Foreign tax credit from Form 1116  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 47  
2014-2016: 1040 line 48

_Input Variable Name:_ **e07400**  
_Description:_ General business credit from Form 3800  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53a  
2014-2016: 1040 line 54a

_Input Variable Name:_ **e07600**  
_Description:_ Prior year minimum tax credit from Form 8801  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53b  
2014-2016: 1040 line 54b

_Input Variable Name:_ **e09700**  
_Description:_ Recapture of Investment Credit  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2015: 4255 line 15  
2016-2016: 4255 line 20

_Input Variable Name:_ **e09800**  
_Description:_ Unreported payroll taxes from Form 4137 or 8919  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 57  
2014-2016: 1040 line 58

_Input Variable Name:_ **e09900**  
_Description:_ Penalty tax on qualified retirement plans  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 58  
2014-2016: 1040 line 59

_Input Variable Name:_ **e11200**  
_Description:_ Excess payroll (FICA/RRTA) tax withheld  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 69  
2014-2016: 1040 line 71

_Input Variable Name:_ **e17500**  
_Description:_ Itemizable medical and dental expenses. WARNING: this variable is zero below the floor in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 1

_Input Variable Name:_ **e18400**  
_Description:_ Itemizable state and local income/sales taxes  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 5

_Input Variable Name:_ **e18500**  
_Description:_ Itemizable real-estate taxes paid  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 6

_Input Variable Name:_ **e19200**  
_Description:_ Itemizable interest paid  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 15

_Input Variable Name:_ **e19800**  
_Description:_ Itemizable charitable giving: cash/check contributions. WARNING: this variable is already capped in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 16

_Input Variable Name:_ **e20100**  
_Description:_ Itemizable charitable giving: other than cash/check contributions. WARNING: this variable is already capped in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 17

_Input Variable Name:_ **e20400**  
_Description:_ Itemizable miscellaneous deductions. WARNING: this variable is zero below the floor in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 24

_Input Variable Name:_ **e24515**  
_Description:_ Sch D: Un-Recaptured Section 1250 Gain  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 19

_Input Variable Name:_ **e24518**  
_Description:_ Sch D: 28% Rate Gain or Loss  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 18

_Input Variable Name:_ **e26270**  
_Description:_ Sch E: Combined partnership and S-corporation net income/loss (includes k1bx14p and k1bx14s amounts and is included in e02000)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch E line 32

_Input Variable Name:_ **e27200**  
_Description:_ Sch E: Farm rent net income or loss (included in e02000)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch E line 40

_Input Variable Name:_ **e32800**  
_Description:_ Child/dependent-care expenses for qualifying persons from Form 2441  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 2441 line 3

_Input Variable Name:_ **e58990**  
_Description:_ Investment income elected amount from Form 4952  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 4952 line 4g

_Input Variable Name:_ **e62900**  
_Description:_ Alternative Minimum Tax foreign tax credit from Form 6251  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251 line 32

_Input Variable Name:_ **e87521**  
_Description:_ Total tentative AmOppCredit amount for all students  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 8863 Part I line 1 and 8863 Part III line 30

_Input Variable Name:_ **e87530**  
_Description:_ Adjusted qualified lifetime learning expenses for all students  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 8863 Part I line 10 and 8863 Part III line 31

_Input Variable Name:_ **elderly_dependents**  
_Description:_ number of dependents age 65+ in filing unit excluding taxpayer and spouse  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data; not used in tax law

_Input Variable Name:_ **f2441**  
_Description:_ number of child/dependent-care qualifying persons  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 2441 line 2b

_Input Variable Name:_ **f6251**  
_Description:_ 1 if Form 6251 (AMT) attached to return; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251

_Input Variable Name:_ **ffpos**  
_Description:_ CPS family identifier within household (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **fips**  
_Description:_ FIPS state code (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **g20500**  
_Description:_ Itemizable gross (before 10% AGI disregard) casualty or theft loss  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 20 before disregard subtracted

_Input Variable Name:_ **h_seq**  
_Description:_ CPS household sequence number (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **housing_ben**  
_Description:_ Imputed housing benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **k1bx14p**  
_Description:_ Partner self-employment earnings/loss for taxpayer (included in e26270 total)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1065 (Schedule K-1) box 14

_Input Variable Name:_ **k1bx14s**  
_Description:_ Partner self-employment earnings/loss for spouse (included in e26270 total)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1065 (Schedule K-1) box 14

_Input Variable Name:_ **mcaid_ben**  
_Description:_ Imputed Medicaid benefits expressed as the actuarial value of Medicaid health insurance  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **mcare_ben**  
_Description:_ Imputed Medicare benefits expressed as the actuarial value of Medicare health insurance  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **n1820**  
_Description:_ Number of people age 18-20 years old in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **n21**  
_Description:_ Number of people 21 years old or older in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **n24**  
_Description:_ Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu05**  
_Description:_ Number of dependents under 5 years old  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu13**  
_Description:_ Number of dependents under 13 years old  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu18**  
_Description:_ Number of people under 18 years old in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **other_ben**  
_Description:_ Non-imputed benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: determined using government benefit program data

_Input Variable Name:_ **p08000**  
_Description:_ Other tax credits (but not including Sch R credit)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53  
2014-2016: 1040 line 54

_Input Variable Name:_ **p22250**  
_Description:_ Sch D: Net short-term capital gains/losses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 7

_Input Variable Name:_ **p23250**  
_Description:_ Sch D: Net long-term capital gains/losses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 15

_Input Variable Name:_ **pencon_p**  
_Description:_ Contributions to defined-contribution pension plans for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: Imputed using IRS tabulations of Form W-2 sample

_Input Variable Name:_ **pencon_s**  
_Description:_ Contributions to defined-contribution pension plans for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: Imputed using IRS tabulations of Form W-2 sample

_Input Variable Name:_ **s006**  
_Description:_ Filing unit sampling weight; appears as WEIGHT variable in tc CLI minimal output  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: not used in filing unit tax calculations

_Input Variable Name:_ **snap_ben**  
_Description:_ Imputed SNAP benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **ssi_ben**  
_Description:_ Imputed SSI benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **tanf_ben**  
_Description:_ Imputed TANF benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **vet_ben**  
_Description:_ Imputed Veteran's benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **wic_ben**  
_Description:_ Imputed WIC benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model