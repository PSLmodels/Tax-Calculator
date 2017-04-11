"""
Implements TaxBrain "Macroeconomic Elasticities Simulation" dynamic analysis.
"""


def proportional_change_gdp(calc1, calc2, elasticity=0.0):
    '''
    This function harnesses econometric estimates of the historic relationship
    between tax policy and the macroeconomy to predict the effect of tax
    reforms on growth.

    In particular, this model relies on estimates of how GDP responds to
    changes in the average after tax rate on wage income across all taxpayers
    (one minus the average marginal tax rate, or 1-AMTR). These estimates are
    derived from calculations of income-weighted marginal tax rates under the
    baseline and reform.

    Evidence for this parameter can be found in Barro and Redlick's
    "Macroeconomic Effects from Government Purchases and Taxes." In particular,
    Barro and Redlick find that from a 1 percentage point increase in the AMTR
    leads to a 0.54 percent increase in GDP. Evaluated at the sample mean,
    this translates to an elasticity of GDP with respect to the average after
    tax rate of 0.36.

    Karel Mertens' "Marginal Tax Rates and Income: New Time Series Evidence"
    contains additional evidence, focussed on tax cuts affecting the upper part
    of the income distribution.

    Both Mertens and Karel tentatively conclude that the effect stems from
    marginal rather than average tax rates.

    Parameters
    ----------
    calc1 : Calculator object for the pre-reform baseline
    calc2 : Calculator object for the policy reform
    elasticity: Float estimate of elasticity of GDP wrt 1-AMTR

    Returns
    -------
    Float estimate of proportional GDP impact of the reform.
    '''
    _, _, mtr_combined1 = calc1.mtr()
    _, _, mtr_combined2 = calc2.mtr()
    avg_one_mtr1 = (1.0 - (mtr_combined1 * calc1.records.c00100 *
                           calc1.records.s006).sum() /
                    (calc1.records.c00100 * calc1.records.s006).sum())
    avg_one_mtr2 = (1.0 - (mtr_combined2 * calc2.records.c00100 *
                           calc2.records.s006).sum() /
                    (calc2.records.c00100 * calc2.records.s006).sum())
    diff_avg_one_mtr = avg_one_mtr2 - avg_one_mtr1
    proportional_diff_mtr = diff_avg_one_mtr / avg_one_mtr1
    gdp_effect_of_reform = proportional_diff_mtr * elasticity
    print('{:.5f}'.format(gdp_effect_of_reform))
    return gdp_effect_of_reform
