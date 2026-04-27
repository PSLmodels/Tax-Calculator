Assumption parameters
=====================

This section contains documentation of several sets of parameters that
characterize responses to a tax reform. Consumption parameters are
used to compute marginal tax rates and to compute the consumption
value of in-kind benefits. Growdiff parameters are used to specify
baseline differences and/or reform responses in the annual rate of
growth in economic variables. (Note that behavior parameters used to
compute changes in input variables caused by a tax reform in a
partial-equilibrium setting are not part of Tax-Calculator, but can be
used via the Behavioral-Response `behresp` package in a Python
program.)

The assumption parameters control advanced features of Tax-Calculator,
so understanding the source code that uses them is essential. Default
values of many assumption parameters are zero and are projected into
the future at that value, which implies no response to the reform. The
benefit value consumption parameters have a default value of one,
which implies the consumption value of the in-kind benefits is equal
to the government cost of providing the benefits.


## Growdiff

####  `ABOOK`  
_Long Name:_ ABOOK additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABOOK extrapolates input variables: e07300 and e07400.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ACGNS`  
_Long Name:_ ACGNS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ACGNS extrapolates input variables: e01200, p22250, p23250, e24515 and e24518.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ACPIM`  
_Long Name:_ ACPIM additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ACPIM extrapolates input variables: e03270, e03290 and e17500.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ACPIU`  
_Long Name:_ ACPIU additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ACPIU is the price inflation rate used to inflate many policy parameters.  Note that non-zero values of this parameter will not affect historically known values of policy parameters.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ADIVS`  
_Long Name:_ ADIVS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ADIVS extrapolates input variables: e00600 and e00650.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `AINTS`  
_Long Name:_ AINTS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  AINTS extrapolates input variables: e00300 and e00400.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `AIPD`  
_Long Name:_ AIPD additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  AIPD extrapolates input variables: e19200.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASCHCI`  
_Long Name:_ ASCHCI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASCHCI extrapolates input variables: e00900, e00900p and e00900s when they are positive.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASCHCL`  
_Long Name:_ ASCHCL additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASCHCL extrapolates input variables: e00900, e00900p and e00900s when they are negative.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASCHEI`  
_Long Name:_ ASCHEI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASCHEI extrapolates input variables: e02000 when positive, and e26270, k1bx14p, k1bx14s and e27200 for all values.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASCHEL`  
_Long Name:_ ASCHEL additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASCHEL extrapolates input variable: e02000 when negative.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASCHF`  
_Long Name:_ ASCHF additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASCHF extrapolates input variables: e02100, e02100p and e02100s.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ASOCSEC`  
_Long Name:_ ASOCSEC additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ASOCSEC extrapolates input variable: e02400.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ATXPY`  
_Long Name:_ ATXPY additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ATXPY extrapolates input variables: e00700, e00800, e01400, e01500, e01700, e03150, e03210, e03220, e03230, e03300, e03400, e03500, e07240, e07260, p08000, e09700, e09800, e09900, e11200, e18400, e18500, e19800, e20100, e20400, g20500, e07600, e32800, e58990, e62900, e87530, e87521 and cmbtp.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `AUCOMP`  
_Long Name:_ AUCOMP additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  AUCOMP extrapolates input variable: e02300.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `AWAGE`  
_Long Name:_ AWAGE additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  AWAGE extrapolates input variables: e00200, e00200p and e00200s.  Also, AWAGE is the wage growth rate used to inflate the OASDI maximum taxable earnings policy parameter, _SS_Earnings_c.  Note that non-zero values of this parameter will not affect historically known values of _SS_Earnings_c.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENOTHER`  
_Long Name:_ ABENOTHER additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENOTHER extrapolates input variable other_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENMCARE`  
_Long Name:_ ABENMCARE additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENMCARE extrapolates input variable mcare_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENMCAID`  
_Long Name:_ ABENMCAID additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENMCAID extrapolates input variable mcaid_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENSSI`  
_Long Name:_ ABENSSI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENSSI extrapolates input variable ssi_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENSNAP`  
_Long Name:_ ABENSNAP additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENSNAP extrapolates input variable snap_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENWIC`  
_Long Name:_ ABENWIC additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENWIC extrapolates input variable wic_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENHOUSING`  
_Long Name:_ ABENHOUSING additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENHOUSING extrapolates input variable housing_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENTANF`  
_Long Name:_ ABENTANF additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENTANF extrapolates input variable tanf_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


####  `ABENVET`  
_Long Name:_ ABENVET additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file.  ABENVET extrapolates input variable vet_ben.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error  


## Consumption

####  `MPC_e17500`  
_Long Name:_ Marginal propensity to consume medical expenses  
_Description:_ Defined as dollar change in medical-expense consumption divided by dollar change in income.  Typical value is in [0,1] range.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `MPC_e18400`  
_Long Name:_ Marginal propensity to consume state-and-local taxes  
_Description:_ Defined as dollar change in state-and-local-taxes consumption divided by dollar change in income.  Typical value is in [0,1] range.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `MPC_e19800`  
_Long Name:_ Marginal propensity to consume charity cash contributions  
_Description:_ Defined as dollar change in charity-cash-contribution consumption divided by dollar change in income.  Typical value is in [0,1] range.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `MPC_e20400`  
_Long Name:_ Marginal propensity to consume miscellaneous deduction expenses  
_Description:_ Defined as dollar change in miscellaneous-deduction-expense consumption divided by dollar change in income.  Typical value is in [0,1] range.  
_Value Type:_ float  
_Default Value:_ 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `BEN_housing_value`  
_Long Name:_ Consumption value of housing benefits  
_Description:_ Consumption value per dollar of housing benefits, all of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `BEN_snap_value`  
_Long Name:_ Consumption value of SNAP benefits  
_Description:_ Consumption value per dollar of SNAP benefits, all of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `BEN_tanf_value`  
_Long Name:_ Consumption value of TANF benefits  
_Description:_ Consumption value per dollar of TANF benefits, some of which are cash benefits and some of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `BEN_vet_value`  
_Long Name:_ Consumption value of veterans benefits  
_Description:_ Consumption value per dollar of veterans benefits, some of which are in-kind benefits (only about 48% are cash benefits).  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error  


####  `BEN_wic_value`  
_Long Name:_ Consumption value of WIC benefits  
_Description:_ Consumption value per dollar of WIC benefits, all of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  


####  `BEN_mcare_value`  
_Long Name:_ Consumption value of Medicare benefits  
_Description:_ Consumption value per dollar of Medicare benefits, all of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error  


####  `BEN_mcaid_value`  
_Long Name:_ Consumption value of Medicaid benefits  
_Description:_ Consumption value per dollar of Medicaid benefits, all of which are in-kind benefits.  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error  


####  `BEN_other_value`  
_Long Name:_ Consumption value of other benefits  
_Description:_ Consumption value per dollar of other benefits, some of which are in-kind benefits (somewhere between 52% and 76% are in-kind benefits).  
_Value Type:_ float  
_Default Value:_ 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error  
