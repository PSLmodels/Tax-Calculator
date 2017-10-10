"""
Implements TaxBrain "Macroeconomic Elasticities Simulation" dynamic analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 macro_elasticity.py
# pylint --disable=locally-disabled macro_elasticity.py


def proportional_change_gdp(calc1, calc2, elasticity):
    '''
    This function harnesses econometric estimates of the historic relationship
    between tax policy and the macroeconomy to predict the effect of tax
    reforms on growth.

    In particular, this model relies on estimates of how GDP responds to
    changes in the average after tax rate on wage income across all taxpayers
    (one minus the average marginal tax rate, or 1-AMTR). These estimates are
    derived from calculations of income-weighted marginal tax rates under the
    baseline and reform.

    Empirical evidence on this elasticity can be found in Robert Barro
    and Charles Redlick, "Macroeconomic Effects from Government Purchases
    and Taxes" (2011 Quarterly Journal of Economics).  In particular,
    Barro and Redlick find that a 1 percentage point decrease in the AMTR
    leads to a 0.54 percent increase in GDP.  Evaluated at the sample mean,
    this translates to an elasticity of GDP with respect to the average
    after-tax marginal rate of about 0.36.

    A more recent paper by Karel Mertens and Jose L. Montiel Olea,
    entitled "Marginal Tax Rates and Income: New Time Series Evidence",
    NBER working paper 19171 (June 2013 with September 2017 revisions)
    <http://www.nber.org/papers/w19171.pdf>,
    contains additional empirical evidence suggesting the elasticity is
    no less than the 0.36 Barro-Redlick estimate and perhaps somewhat
    higher (see section 4.6).

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
    return gdp_effect_of_reform
