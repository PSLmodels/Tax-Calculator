"""
Partial-equilibrium elasticity-based behavioral-responses logic.
"""
# CODING-STYLE CHECKS:
# pycodestyle behresp.py
# pylint --disable=locally-disabled behresp.py

import copy
import numpy as np
from taxcalc.calculator import Calculator
from taxcalc.records import Records
from taxcalc.utils import DIST_VARIABLES

__all__ = ['response', 'quantity_response', 'labor_response']


def response(calc_1, calc_2, elasticities, dump=False):
    """
    Implements "Partial Equilibrium Simulation" conventional analysis,
    returning results as a tuple of Pandas DataFrame objects (df1, df2)
    where df1 is extracted from a baseline-policy calc_1 copy, and df2 is
    extracted from a reform-policy calc_2 copy that incorporates the
    behavioral responses given by the nature of the baseline-to-reform
    change in policy and elasticities in the specified behavior dictionary.

    Note: this function internally modifies a copy of calc_2 records to
    account for behavioral responses that arise from the policy reform that
    involves moving from calc1 policy to calc2 policy.  Neither calc_1 nor
    calc_2 need to have had calc_all() executed before calling the response
    function.  And neither calc_1 nor calc_2 are affected by this response
    function.

    The elasticities argument is a dictionary containing the assumed response
    elasticities.  Omitting an elasticity key:value pair in the dictionary
    implies the omitted elasticity is assumed to be zero.  Here is the full
    dictionary content and each elasticity's internal name:

     be_sub = elasticities['sub']
       Substitution elasticity of taxable income.
       Defined as proportional change in taxable income divided by
       proportional change in marginal net-of-tax rate (1-MTR) on taxpayer
       earnings caused by the reform.  Must be zero or positive.

     be_inc = elasticities['inc']
       Income elasticity of taxable income.
       Defined as dollar change in taxable income divided by dollar change
       in after-tax income caused by the reform.  Must be zero or negative.

     be_cg = elasticities['cg']
       Semi-elasticity of long-term capital gains.
       Defined as change in logarithm of long-term capital gains divided by
       change in marginal tax rate (MTR) on long-term capital gains caused by
       the reform.  Must be zero or negative.
       Read response function documentation (see below) for discussion of
       appropriate values.

    The optional dump argument controls the number of variables included
    in the two returned DataFrame objects.  When dump=False (its default
    value), the variables in the two returned DataFrame objects include
    just the variables in the Tax-Calculator DIST_VARIABLES list, which
    is sufficient for constructing the standard Tax-Calculator tables.
    When dump=True, the variables in the two returned DataFrame objects
    include all the Tax-Calculator input and calculated output variables,
    which is the same output as produced by the Tax-Calculator tc --dump
    option except for one difference: the tc --dump option provides two
    calculated variables, mtr_inctax and mtr_paytax, that are replaced
    in the dump output of this response function by mtr_combined, which
    is the sum of mtr_inctax and mtr_paytax.

    Note: the use here of a dollar-change income elasticity (rather than
      a proportional-change elasticity) is consistent with Feldstein and
      Feenberg, "The Taxation of Two Earner Families", NBER Working Paper
      No. 5155 (June 1995).  A proportional-change elasticity was used by
      Gruber and Saez, "The elasticity of taxable income: evidence and
      implications", Journal of Public Economics 84:1-32 (2002) [see
      equation 2 on page 10].

    Note: the nature of the capital-gains elasticity used here is similar
      to that used in Joint Committee on Taxation, "New Evidence on the
      Tax Elasticity of Capital Gains: A Joint Working Paper of the Staff
      of the Joint Committee on Taxation and the Congressional Budget
      Office", (JCX-56-12), June 2012.  In particular, the elasticity
      use here is equivalent to the term inside the square brackets on
      the right-hand side of equation (4) on page 11 --- not the epsilon
      variable on the left-hand side of equation (4), which is equal to
      the elasticity used here times the weighted average marginal tax
      rate on long-term capital gains.  So, the JCT-CBO estimate of
      -0.792 for the epsilon elasticity (see JCT-CBO, Table 5) translates
      into a much larger absolute value for the be_cg semi-elasticity
      used by Tax-Calculator.
      To calculate the elasticity from a semi-elasticity, we multiply by
      MTRs from TC and weight by shares of taxable gains. To avoid those
      with zero MTRs, we restrict this to the top 40% of tax units by AGI.
      Using this function, a semi-elasticity of -3.45 corresponds to a tax
      rate elasticity of -0.792.

    """
    # pylint: disable=too-many-locals,too-many-statements,too-many-branches

    # Check function argument types and elasticity values
    calc1 = copy.deepcopy(calc_1)
    calc2 = copy.deepcopy(calc_2)
    assert isinstance(calc1, Calculator)
    assert isinstance(calc2, Calculator)
    assert isinstance(elasticities, dict)
    be_sub = elasticities['sub'] if 'sub' in elasticities else 0.0
    be_inc = elasticities['inc'] if 'inc' in elasticities else 0.0
    be_cg = elasticities['cg'] if 'cg' in elasticities else 0.0
    assert be_sub >= 0.0
    assert be_inc <= 0.0
    assert be_cg <= 0.0

    # Begin nested functions used only in this response function
    def _update_ordinary_income(taxinc_change, calc):
        """
        Implement total taxable income change induced by behavioral response.
        """
        # compute AGI minus itemized deductions, agi_m_ided
        agi = calc.array('c00100')
        ided = np.where(calc.array('c04470') < calc.array('standard'),
                        0., calc.array('c04470'))
        agi_m_ided = agi - ided
        # assume behv response only for filing units with positive agi_m_ided
        pos = np.array(agi_m_ided > 0., dtype=bool)
        delta_income = np.where(pos, taxinc_change, 0.)
        # allocate delta_income into three parts
        # pylint: disable=unsupported-assignment-operation
        winc = calc.array('e00200')
        delta_winc = np.zeros_like(agi)
        delta_winc[pos] = delta_income[pos] * winc[pos] / agi_m_ided[pos]
        oinc = agi - winc
        delta_oinc = np.zeros_like(agi)
        delta_oinc[pos] = delta_income[pos] * oinc[pos] / agi_m_ided[pos]
        delta_ided = np.zeros_like(agi)
        delta_ided[pos] = delta_income[pos] * ided[pos] / agi_m_ided[pos]
        # confirm that the three parts are consistent with delta_income
        assert np.allclose(delta_income, delta_winc + delta_oinc - delta_ided)
        # add the three parts to different records variables embedded in calc
        calc.incarray('e00200', delta_winc)
        calc.incarray('e00200p', delta_winc)
        calc.incarray('e00300', delta_oinc)
        calc.incarray('e19200', delta_ided)
        return calc

    def _update_cap_gain_income(cap_gain_change, calc):
        """
        Implement capital gain change induced by behavioral responses.
        """
        calc.incarray('p23250', cap_gain_change)
        return calc

    def _mtr12(calc__1, calc__2, mtr_of='e00200p', tax_type='combined'):
        """
        Computes marginal tax rates for Calculator objects calc__1 and calc__2
        for specified mtr_of income type and specified tax_type.
        """
        assert tax_type in ('combined', 'iitax')
        _, iitax1, combined1 = calc__1.mtr(mtr_of, wrt_full_compensation=True)
        _, iitax2, combined2 = calc__2.mtr(mtr_of, wrt_full_compensation=True)
        if tax_type == 'combined':
            return (combined1, combined2)
        return (iitax1, iitax2)
    # End nested functions used only in this response function

    # Begin main logic of response function
    calc1.calc_all()
    calc2.calc_all()
    assert calc1.array_len == calc2.array_len
    assert calc1.current_year == calc2.current_year
    mtr_cap = 0.99
    if dump:
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        dvars = list(recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS)
    # Calculate sum of substitution and income effects
    if be_sub == 0.0 and be_inc == 0.0:
        zero_sub_and_inc = True
        si_chg = None  # is not used when zero_sub_and_inc is True
        if dump:
            wage_mtr1 = np.zeros(calc1.array_len)
            wage_mtr2 = np.zeros(calc2.array_len)
    else:
        zero_sub_and_inc = False
        # calculate marginal combined tax rates on taxpayer wages+salary
        # (e00200p is taxpayer's wages+salary)
        wage_mtr1, wage_mtr2 = _mtr12(calc1, calc2,
                                      mtr_of='e00200p',
                                      tax_type='combined')
        # calculate magnitude of substitution effect
        if be_sub == 0.0:
            sub = np.zeros(calc1.array_len)
        else:
            # proportional change in marginal net-of-tax rates on earnings
            mtr1 = np.where(wage_mtr1 > mtr_cap, mtr_cap, wage_mtr1)
            mtr2 = np.where(wage_mtr2 > mtr_cap, mtr_cap, wage_mtr2)
            pch = ((1. - mtr2) / (1. - mtr1)) - 1.
            # Note: c04800 is filing unit's taxable income
            # The substitution effect is scaled by taxable income, which
            # includes long-term capital gains, so its magnitude is not
            # independent of the filing unit's LTCG amount.  This is by
            # design, but note that it differs from the labor_response
            # and quantity_response functions below, which scale the
            # substitution effect by earnings (that is, by quantity).
            sub = be_sub * pch * calc1.array('c04800')
        # calculate magnitude of income effect
        if be_inc == 0.0:
            inc = np.zeros(calc1.array_len)
        else:
            # dollar change in after-tax income
            # Note: combined is f.unit's income+payroll tax liability
            dch = calc1.array('combined') - calc2.array('combined')
            inc = be_inc * dch
        # calculate sum of substitution and income effects
        si_chg = sub + inc
    # Calculate long-term capital-gains effect
    if be_cg == 0.0:
        ltcg_chg = np.zeros(calc1.array_len)
    else:
        # calculate marginal tax rates on long-term capital gains
        #  p23250 is filing units' long-term capital gains
        ltcg_mtr1, ltcg_mtr2 = _mtr12(calc1, calc2,
                                      mtr_of='p23250',
                                      tax_type='iitax')
        rch = ltcg_mtr2 - ltcg_mtr1
        exp_term = np.exp(be_cg * rch)
        new_ltcg = calc1.array('p23250') * exp_term
        ltcg_chg = new_ltcg - calc1.array('p23250')
    # Extract dataframe from calc1
    if dump:
        df1 = calc1.dataframe(dvars)
        df1.drop('mtr_inctax', axis='columns', inplace=True)
        df1.drop('mtr_paytax', axis='columns', inplace=True)
        df1['mtr_combined'] = wage_mtr1 * 100
    else:
        df1 = calc1.dataframe(DIST_VARIABLES)
    del calc1
    # Add behavioral-response changes to income sources
    calc2_behv = copy.deepcopy(calc2)
    del calc2
    if not zero_sub_and_inc:
        calc2_behv = _update_ordinary_income(si_chg, calc2_behv)
    calc2_behv = _update_cap_gain_income(ltcg_chg, calc2_behv)
    # Recalculate post-reform taxes incorporating behavioral responses
    calc2_behv.calc_all()
    # Extract dataframe from calc2_behv
    if dump:
        df2 = calc2_behv.dataframe(dvars)
        df2.drop('mtr_inctax', axis='columns', inplace=True)
        df2.drop('mtr_paytax', axis='columns', inplace=True)
        df2['mtr_combined'] = wage_mtr2 * 100
    else:
        df2 = calc2_behv.dataframe(DIST_VARIABLES)
    del calc2_behv
    # Return the two dataframes
    return (df1, df2)


def pch_response(elasticity=np.zeros(1),
                 val1=np.zeros(1),
                 val2=np.zeros(1)):
    """
    Calculate the percentage change response, given an elasticity and
    original/new values. Can be used to calculate substitution or
    income effects.

    Parameters
    ----------
    elasticity: value or numpy array representing elasticity(ies).
        Defaults to zero.

    val1: value or numpy array representing original value(s).
        Defaults to zero.

    val2: value or numpy array representing new value(s).
        Defaults to zero.

    Returns
    -------
    pch_response: numpy array
        Percentage change in the response, calculated essentially as:
        elasticity * (val2 / val1 - 1).
    """
    val1 = np.where(val1 == 0, np.nan, val1)  # Avoids a warning.
    pch = np.where(np.isnan(val1), 0, val2 / val1 - 1.)
    return elasticity * pch


def quantity_response(quantity=np.array([1]),
                      price_elasticity=np.zeros(1),
                      aftertax_price1=np.zeros(1),
                      aftertax_price2=np.zeros(1),
                      income_elasticity=np.zeros(1),
                      aftertax_income1=np.zeros(1),
                      aftertax_income2=np.zeros(1)):
    """
    Calculate dollar change in quantity using a log-log response equation,
    which assumes that the proportional change in the quantity is equal to
    the sum of two terms:

    (1) the proportional change in the quantity's marginal aftertax price
        times an assumed price elasticity, and

    (2) the proportional change in aftertax income
        times an assumed income elasticity.

    Not all inputs are required, so it's possible to calculate only the price
    or income effects by providing a subset of arguments. Accepts arrays.

    Parameters
    ----------
    quantity: numpy array
        pre-response quantity whose response is being calculated.
        Defaults to 1.

    price_elasticity: float
        coefficient of the percentage change in aftertax price of
        the quantity in the log-log response equation. Defaults to 0.

    aftertax_price1: numpy array
        marginal aftertax price of the quantity under baseline policy.

        Note that this function forces prices to be in [0.01, inf] range,
        but the caller of this function may want to constrain negative
        or very small prices to be somewhat larger in order to avoid extreme
        proportional changes in price. Defaults to 0.

        Note this is NOT an array of marginal tax rates (MTR), but rather
        usually 1-MTR (or in the case of quantities, like charitable
        giving, whose MTR values are non-positive, 1+MTR).

    aftertax_price2: numpy array
        marginal aftertax price of the quantity under reform policy.

        Note that this function forces prices to be in [0.01, inf] range,
        but the caller of this function may want to constrain negative
        or very small prices to be somewhat larger in order to avoid extreme
        proportional changes in price. Defaults to 0.

        Note this is NOT an array of marginal tax rates (MTR), but rather
        usually 1-MTR (or in the case of quantities, like charitable
        giving, whose MTR values are non-positive, 1+MTR).

    income_elasticity: float
        coefficient of the percentage change in aftertax income in the
        log-log response equation. Defaults to 0.

    aftertax_income1: numpy array
        aftertax income under baseline policy.

        Note that this function forces income to be in [1, inf] range,
        but the caller of this function may want to constrain negative
        or small incomes to be somewhat larger in order to avoid extreme
        proportional changes in aftertax income. Defaults to 0.

    aftertax_income2: numpy array
        aftertax income under reform policy.

        Note that this function forces income to be in [1, inf] range,
        but the caller of this function may want to constrain negative
        or small incomes to be somewhat larger in order to avoid extreme
        proportional changes in aftertax income. Defaults to 0.

    Returns
    -------
    response: numpy array
        dollar change in quantity calculated from log-log response equation
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    substitution_effect = pch_response(
        price_elasticity,
        np.maximum(aftertax_price1, 0.01),
        np.maximum(aftertax_price2, 0.01))
    income_effect = pch_response(
        income_elasticity,
        np.maximum(aftertax_income1, 1.0),
        np.maximum(aftertax_income2, 1.0))
    return quantity * (substitution_effect + income_effect)


def labor_response(earnings=np.array([1]),
                   substitution_eti=np.zeros(1),
                   mtr1=np.zeros(1),
                   mtr2=np.zeros(1),
                   income_elasticity=np.zeros(1),
                   aftertax_income1=np.zeros(1),
                   aftertax_income2=np.zeros(1)):
    """
    Calculate labor response given earnings, substitution elasticity of taxable
    income, initial and new marginal tax rates, income elasticity, and initial
    and new after-tax income. Accepts arrays.

    Parameters
    ----------
    earnings: numpy array
        pre-response earnings whose response is being calculated.
        Defaults to 1.

    substitution_eti: float or numpy array
        coefficient of the substitution elasticity of taxable income.
        Defaults to 0.

    mtr1: numpy array
        marginal tax rate of earnings under baseline policy.

        Note that this function forces MTRs to be in [-inf, 0.99] range,
        but the caller of this function may want to constrain large MTRs
        to be somewhat smaller in order to avoid extreme
        proportional changes in earnings. Defaults to 0.

    mtr2: numpy array
        marginal tax rate of earnings under reform policy.

        Note that this function forces MTRs to be in [-inf, 0.99] range,
        but the caller of this function may want to constrain large MTRs
        to be somewhat smaller in order to avoid extreme
        proportional changes in earnings. Defaults to 0.

    income_elasticity: float
        coefficient of the percentage change in aftertax income in the
        log-log response equation. Defaults to 0.

    aftertax_income1: numpy array
        aftertax income under baseline policy.

        Note that this function forces income to be in [1, inf] range,
        but the caller of this function may want to constrain negative
        or small incomes to be somewhat larger in order to avoid extreme
        proportional changes in aftertax income. Defaults to 0.

    aftertax_income2: numpy array
        aftertax income under reform policy.

        Note that this function forces income to be in [1, inf] range,
        but the caller of this function may want to constrain negative
        or small incomes to be somewhat larger in order to avoid extreme
        proportional changes in aftertax income. Defaults to 0.

    Returns
    -------
    response: numpy array
        dollar change in earnings calculated from log-log response equation
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    return quantity_response(
        quantity=earnings,
        price_elasticity=substitution_eti,
        aftertax_price1=1 - mtr1,
        aftertax_price2=1 - mtr2,
        income_elasticity=income_elasticity,
        aftertax_income1=aftertax_income1,
        aftertax_income2=aftertax_income2
    )
