import pandas as pd


def percentage_change_gdp(calc1, calc2, elasticity=0.0):
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
    calc1 : Calculator object for the baseline
    calc2 : Calculator object for the reform
    elasticity: Float estimate of elasticity of GDP wrt 1-AMTR

    Returns
    -------
    Float estimate of the GDP impact of the reform.
    '''
    mtr_fica_x, mtr_iit_x, mtr_combined_x = calc1.mtr()
    mtr_fica_y, mtr_iit_y, mtr_combined_y = calc2.mtr()

    after_tax_mtr_x = (1 - ((mtr_combined_x) * calc1.records.c00100 *
                       calc1.records.s006).sum() /
                       (calc1.records.c00100 * calc1.records.s006).sum())

    after_tax_mtr_y = (1 - ((mtr_combined_y) * calc2.records.c00100 *
                       calc2.records.s006).sum() /
                       (calc2.records.c00100 * calc2.records.s006).sum())

    diff_avg_mtr_combined_y = after_tax_mtr_y - after_tax_mtr_x
    percent_diff_mtr = diff_avg_mtr_combined_y / after_tax_mtr_x

    gdp_effect_y = percent_diff_mtr * elasticity

    print(("%.5f" % gdp_effect_y))

    return gdp_effect_y
