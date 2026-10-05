Input variables
===============

This section contains documentation of input variables in a format that is easy to search and print.
The input variables are ordered alphabetically by name.
There are no subsections, just a long list of input variables that Tax-Calculator is programmed to use in its calculations.
The Availability information indicates which input data files contain the variable.


##  `DSI`  
_Description_: 1 if claimed as dependent on another return; otherwise 0  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `EIC`  
_Description_: number of EIC qualifying children (range: 0 to 3)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `FLPDYR`  
_Description_: Calendar year for which taxes are calculated  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `MARS`  
**_Required Input Variable_**  
_Description_: Filing (marital) status: line number of the checked box [1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er)]  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `MIDR`  
_Description_: 1 if separately filing spouse itemizes; otherwise 0  
_Datatype_: int  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `RECID`  
**_Required Input Variable_**  
_Description_: Unique numeric identifier for filing unit; appears as RECID variable in tc CLI minimal output  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `XTOT`  
_Description_: Total number of exemptions for filing unit  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `age_head`  
_Description_: Age in years of taxpayer (i.e. primary adult)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `age_spouse`  
_Description_: Age in years of spouse (i.e. secondary adult if present)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `agi_bin`  
_Description_: Historical AGI category used in data extrapolation  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `blind_head`  
_Description_: 1 if taxpayer is blind; otherwise 0  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `blind_spouse`  
_Description_: 1 if spouse is blind; otherwise 0  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `cmbtp`  
_Description_: Estimate of income on (AMT) Form 6251 but not in AGI  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e00200`  
_Description_: Wages, salaries, tips/otime for filing unit net of pension contributions  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00200p`  
_Description_: Wages, salaries, tips/otime for taxpayer net of pension contributions (pencon_p)  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00200s`  
_Description_: Wages, salaries, tips/otime for spouse net of pension contributions (pencon_s)  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `pencon_p`  
_Description_: Contributions to defined-contribution pension plans for taxpayer  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `pencon_s`  
_Description_: Contributions to defined-contribution pension plans for spouse  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00300`  
_Description_: Taxable interest income  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00400`  
_Description_: Tax-exempt interest income  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00600`  
_Description_: Ordinary dividends included in AGI  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00650`  
_Description_: Qualified dividends included in ordinary dividends  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00700`  
_Description_: Taxable refunds of state and local income taxes  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e00800`  
_Description_: Alimony received  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00900`  
_Description_: Sch C business net profit/loss for filing unit  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00900p`  
_Description_: Sch C business net profit/loss for taxpayer  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e00900s`  
_Description_: Sch C business net profit/loss for spouse  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e01100`  
_Description_: Capital gain distributions not reported on Sch D  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e01200`  
_Description_: Other net gain/loss from Form 4797  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e01400`  
_Description_: Taxable IRA distributions  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e01500`  
_Description_: Total pensions and annuities  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e01700`  
_Description_: Taxable pensions and annuities  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e02000`  
_Description_: Sch E total rental, royalty, partnership, S-corporation, etc, income/loss (includes e26270 and e27200)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e02100`  
_Description_: Farm net income/loss for filing unit from Sch F  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e02100p`  
_Description_: Farm net income/loss for taxpayer  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e02100s`  
_Description_: Farm net income/loss for spouse  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e02300`  
_Description_: Unemployment insurance benefits  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e02400`  
_Description_: Total social security (OASDI) benefits  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03150`  
_Description_: Total deductible IRA contributions  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03210`  
_Description_: Student loan interest  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03220`  
_Description_: Educator expenses  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e03230`  
_Description_: Tuition and fees from Form 8917  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e03240`  
_Description_: Domestic production activities from Form 8903  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03270`  
_Description_: Self-employed health insurance deduction  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03290`  
_Description_: Health savings account deduction from Form 8889  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e03300`  
_Description_: Contributions to SEP, SIMPLE and qualified plans  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e03400`  
_Description_: Penalty on early withdrawal of savings  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e03500`  
_Description_: Alimony paid  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e07240`  
_Description_: Retirement savings contributions credit from Form 8880  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e07260`  
_Description_: Residential energy credit from Form 5695  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e07300`  
_Description_: Foreign tax credit from Form 1116  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e07400`  
_Description_: General business credit from Form 3800  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e07600`  
_Description_: Prior year minimum tax credit from Form 8801  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e09700`  
_Description_: Recapture of Investment Credit  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e09800`  
_Description_: Unreported payroll taxes from Form 4137 or 8919  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e09900`  
_Description_: Penalty tax on qualified retirement plans  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e11200`  
_Description_: Excess payroll (FICA/RRTA) tax withheld  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e17500`  
_Description_: Itemizable medical and dental expenses.  WARNING: this variable is zero below the floor in PUF data.  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e18400`  
_Description_: Itemizable state and local income/sales taxes  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e18500`  
_Description_: Itemizable real-estate taxes paid  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e19200`  
_Description_: Itemizable interest paid  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e19800`  
_Description_: Itemizable charitable giving: cash/check contributions.  WARNING: this variable is already capped in PUF data.  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e20100`  
_Description_: Itemizable charitable giving: other than cash/check contributions.  WARNING: this variable is already capped in PUF data.  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e20400`  
_Description_: Itemizable miscellaneous deductions.  WARNING: this variable is zero below the floor in PUF data.  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `g20500`  
_Description_: Itemizable gross (before 10% AGI disregard) casualty or theft loss  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e24515`  
_Description_: Sch D: Un-Recaptured Section 1250 Gain  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e24518`  
_Description_: Sch D: 28% Rate Gain or Loss  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e26270`  
_Description_: Sch E: Combined partnership and S-corporation net income/loss (includes k1bx14p and k1bx14s amounts and is included in e02000)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e27200`  
_Description_: Sch E: Farm rent net income or loss (included in e02000)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e32800`  
_Description_: Child/dependent-care expenses for qualifying persons from Form 2441  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `e58990`  
_Description_: Investment income elected amount from Form 4952  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e62900`  
_Description_: Alternative Minimum Tax foreign tax credit from Form 6251  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e87530`  
_Description_: Adjusted qualified lifetime learning expenses for all students  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `elderly_dependents`  
_Description_: number of dependents age 65+ in filing unit excluding taxpayer and spouse  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `f2441`  
_Description_: number of child/dependent-care qualifying persons  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `f6251`  
_Description_: 1 if Form 6251 (AMT) attached to return; otherwise 0  
_Datatype_: int  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `a_lineno`  
_Description_: CPS line number for the person record of the head of the tax filing unit (not used in tax-calculation logic)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `ffpos`  
_Description_: CPS family identifier within household (not used in tax-calculation logic)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `fips`  
_Description_: FIPS state code (not used in tax-calculation logic)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `h_seq`  
_Description_: CPS household sequence number (not used in tax-calculation logic)  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `data_source`  
_Description_: 1 if unit is created primarily from IRS-SOI PUF data; 0 if created primarily from CPS data (not used in tax-calculation logic)  
_Datatype_: int  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `k1bx14p`  
_Description_: Partner self-employment earnings/loss for taxpayer (included in e26270 total)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `k1bx14s`  
_Description_: Partner self-employment earnings/loss for spouse (included in e26270 total)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `mcaid_ben`  
_Description_: Imputed Medicaid benefits expressed as the actuarial value of Medicaid health insurance  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `mcare_ben`  
_Description_: Imputed Medicare benefits expressed as the actuarial value of Medicare health insurance  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `n24`  
_Description_: Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `nu06`  
_Description_: Number of dependents under 6 years old  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `nu13`  
_Description_: Number of dependents under 13 years old  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `nu18`  
_Description_: Number of people under 18 years old in the filing unit  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `n1820`  
_Description_: Number of people age 18-20 years old in the filing unit  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `n21`  
_Description_: Number of people 21 years old or older in the filing unit  
_Datatype_: int  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `other_ben`  
_Description_: Non-imputed benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `p08000`  
_Description_: Other tax credits (but not including Sch R credit)  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `p22250`  
_Description_: Sch D: Net short-term capital gains/losses  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `p23250`  
_Description_: Sch D: Net long-term capital gains/losses  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `e87521`  
_Description_: Total tentative AmOppCredit amount for all students  
_Datatype_: float  
_Availability_: taxdata_puf, taxmicrodata_tmd  


##  `s006`  
_Description_: Filing unit sampling weight; appears as WEIGHT variable in tc CLI minimal output  
_Datatype_: float  
_Availability_: taxdata_puf, taxdata_cps, taxmicrodata_tmd  


##  `snap_ben`  
_Description_: Imputed SNAP benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `housing_ben`  
_Description_: Imputed housing benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `ssi_ben`  
_Description_: Imputed SSI benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `tanf_ben`  
_Description_: Imputed TANF benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `vet_ben`  
_Description_: Imputed Veteran's benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `wic_ben`  
_Description_: Imputed WIC benefits  
_Datatype_: float  
_Availability_: taxdata_cps, taxmicrodata_tmd  


##  `PT_SSTB_income`  
_Description_: Value of one implies business income is from a specified service trade or business (SSTB); value of zero implies business income is from a qualified trade or business  
_Datatype_: int  
_Availability_: taxmicrodata_tmd  


##  `PT_binc_w2_wages`  
_Description_: Filing unit's share of total W-2 wages paid by the pass-through business  
_Datatype_: float  
_Availability_: taxmicrodata_tmd  


##  `PT_ubia_property`  
_Description_: Filing unit's share of total business property owned by the pass-through business  
_Datatype_: float  
_Availability_: taxmicrodata_tmd  


##  `auto_loan_interest`  
_Description_: Filing unit's interest payments on OBBBA-qualified auto loans  
_Datatype_: float  
_Availability_: taxmicrodata_tmd  


##  `overtime_income`  
_Description_: Filing unit's OBBBA-qualified overtime income  
_Datatype_: float  
_Availability_: taxmicrodata_tmd  


##  `tip_income`  
_Description_: Filing unit's OBBBA-qualified tip income  
_Datatype_: float  
_Availability_: taxmicrodata_tmd  
