"""
Partial-equilibrium elasticity-based behavioral-responses logic.

This module contains two independent sets of functions that are not
used by each other:

(1) The response function, which conducts a complete partial-equilibrium
    analysis of a baseline-to-reform policy change: it computes the
    behavioral response implied by the assumed elasticities, adds that
    response to the reform filing units' input variables, recalculates
    reform taxes, and returns baseline and reform DataFrame objects.
    This is the function used by the tc CLI --behavior option and by
    cookbook recipe 2.

(2) The quantity_response and labor_response functions (and their
    pch_response helper), which are stand-alone array arithmetic that
    evaluate a log-log response equation for a caller-supplied quantity,
    elasticities, prices, and incomes.  They conduct no tax calculations
    and know nothing about Calculator objects; a caller must compute the
    marginal tax rates and incomes and apply the returned dollar change.

Beyond being unrelated in the code, the two sets of functions differ in
their economics: the response function scales its substitution effect by
taxable income (c04800), whereas labor_response and quantity_response
scale theirs by the quantity (for example, earnings) passed in by the
caller.  They also handle extreme values differently: the response
function caps nothing --- it applies no cap to marginal tax rates and no
floor to after-tax income --- whereas quantity_response forces after-tax
prices into the [0.01, inf] range and after-tax income into the
[1, inf] range.
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

    This function internally modifies a copy of the calc_2 records to
    account for behavioral responses that arise from the policy reform that
    involves moving from calc_1 policy to calc_2 policy.  Neither calc_1 nor
    calc_2 need to have had calc_all() executed before calling the response
    function.  And neither calc_1 nor calc_2 are affected by this response
    function.

    Parameters
    ----------
    calc_1: Calculator object
        represents baseline policy; must be advanced to the analysis year.

    calc_2: Calculator object
        represents reform policy; must be advanced to the same analysis
        year as calc_1 and must contain the same number of filing units.

    elasticities: dictionary
        contains the assumed response elasticities.  Omitting an
        elasticity key:value pair implies the omitted elasticity is
        assumed to be zero.  (Note that the tc CLI --behavior option is
        stricter: a JSON behavior file must contain all the keys.)
        Here is the full dictionary content and each elasticity's
        internal name:

        be_sub = elasticities['sub']
          Substitution elasticity of taxable income.
          Defined as proportional change in taxable income divided by
          proportional change in marginal net-of-tax rate (1-MTR) on
          taxpayer earnings caused by the reform.
          Must be zero or positive.

        be_inc = elasticities['inc']
          Income elasticity of taxable income.
          Defined as dollar change in taxable income divided by dollar
          change in after-tax income caused by the reform.
          Must be zero or negative.

        be_cg = elasticities['cg']
          Semi-elasticity of long-term capital gains.
          Defined as change in logarithm of long-term capital gains
          divided by change in marginal tax rate (MTR) on long-term
          capital gains caused by the reform.
          Must be zero or negative.
          See the capital-gains note below for a discussion of
          appropriate values; be_cg is NOT the tax-rate elasticity
          usually reported in the literature.

    dump: boolean
        controls the number of variables included in the two returned
        DataFrame objects.  When dump=False (its default value), the
        variables in the two returned DataFrame objects include just the
        variables in the Tax-Calculator DIST_VARIABLES list, which is
        sufficient for constructing the standard Tax-Calculator tables.
        When dump=True, the variables in the two returned DataFrame
        objects include all the Tax-Calculator input and calculated
        output variables, which is the same output as produced by the
        Tax-Calculator tc --dumpdb option except for one difference: the
        tc dump output provides two calculated variables, mtr_inctax and
        mtr_paytax, that are replaced in the dump output of this response
        function by mtr_combined, which is the sum of mtr_inctax and
        mtr_paytax.  Two cautions about the mtr_combined column: it is
        expressed in percentage points (that is, it is 100 times the
        rates returned by the Calculator.mtr method), and it contains all
        zeros when both be_sub and be_inc are zero, because in that case
        no earnings marginal tax rates are computed.

    Returns
    -------
    (df1, df2): tuple of two Pandas DataFrame objects
        df1 contains baseline-policy results extracted from a copy of
        calc_1, and df2 contains reform-policy results, incorporating
        the behavioral responses, extracted from a copy of calc_2.
        Both have one row per filing unit, in input-data order, and
        contain the columns described in the dump argument documentation.

    Notes
    -----
    Response equations:

      The substitution and income effects on taxable income are computed,
      in dollars per filing unit, as follows, where mtr1 and mtr2 are the
      baseline and reform combined (income plus payroll) marginal tax
      rates on the taxpayer's earnings (e00200p) computed with respect to
      full compensation (and not capped in any way), where c04800 is
      baseline taxable income, and where combined1 and combined2 are the
      baseline and reform combined income and payroll tax liabilities:

        sub = be_sub * (((1 - mtr2) / (1 - mtr1)) - 1) * c04800

        inc = be_inc * (combined1 - combined2)

      The long-term capital gains response is computed, in dollars per
      filing unit, as follows, where ltcg_mtr1 and ltcg_mtr2 are the
      baseline and reform income-tax marginal tax rates on long-term
      capital gains (p23250):

        new_p23250 = p23250 * exp(be_cg * (ltcg_mtr2 - ltcg_mtr1))

        ltcg_chg = new_p23250 - p23250

      Note that the substitution effect is scaled by taxable income,
      which includes long-term capital gains, so its magnitude is not
      independent of the filing unit's LTCG amount.

    How responses are applied to input variables:

      The sum of the substitution and income effects is a change in
      taxable income that must be mapped back onto the input variables
      used in the tax calculation.  The dollar change is allocated in
      proportion to three components --- wage and salary income (e00200),
      other AGI (c00100 minus e00200), and itemized deductions --- and
      the three parts are added to these input variables:

        the wage part is added to both e00200 and e00200p
        the other-income part is added to e00300 (taxable interest)
        the deduction part is added to e19200 (interest paid deduction)

      Two consequences are worth noting.  First, the spouse's earnings
      variable, e00200s, is not adjusted, so after a response e00200 is
      no longer the sum of e00200p and e00200s.  Second, a response shows
      up in dump output as changes in e00300 and e19200 even for filing
      units whose actual behavior would involve other income or deduction
      items.  The capital-gains response, by contrast, is applied
      directly to p23250.

      The denominator used to form the three allocation shares, called
      alloc_base in the code, is AGI minus itemized deductions, where
      itemized deductions (c04470) are counted only for filing units that
      actually itemize (that is, only when c04470 is no less than the
      standard deduction).  This is NOT an approximation of taxable
      income, and it must not be replaced by the calculated taxable
      income variable, c04800.  Because other AGI is defined as AGI minus
      wages, the three components sum to alloc_base by construction, so
      the three shares sum to one and the allocated parts sum to the
      intended dollar change.  Dividing by any other quantity --- c04800
      included --- would scale the delivered change by the ratio of
      alloc_base to that quantity.  Taxable income is used where taxable
      income is the concept called for: c04800 scales the substitution
      effect, as described in the response equations above.

      The mapping does assume that a dollar added to e00200, e00300, or
      e19200 moves taxable income by a dollar.  That is exact for a
      filing unit in the interior of the rate schedule, but not for one
      whose AGI change also moves an AGI-linked provision (taxable Social
      Security benefits, phase-outs such as the EITC, the qualified
      business income deduction, or the itemized deduction limitation).
      The realized change in aggregate taxable income therefore differs
      somewhat from the intended change: for a top-bracket rate reform
      applied to CPS data for 2026, with be_sub of 0.25 and be_inc of
      -0.1, the realized change exceeded the intended change by about
      four percent, with under one percent of responding filing units
      differing by more than ten dollars.

    Filing units excluded from the response:

      The substitution and income effects are applied only to filing
      units with positive alloc_base; all other filing units are assumed
      to have no ordinary-income response.  That condition is a guard on
      the allocation arithmetic rather than an economic screen: it keeps
      the denominator away from zero and prevents the negative shares
      that a negative alloc_base would produce.  It excludes no filing
      unit that has positive taxable income, because c04800 is positive
      only when alloc_base is positive.  Note that the converse does not
      hold: a filing unit with positive alloc_base and zero taxable
      income does respond, which is intended, because such a unit can
      still owe payroll tax and therefore can still have an income
      effect.  For that reason the condition must not be tightened to
      require positive c04800.  Within the responding group, filing
      units that do not itemize receive no change in e19200.  Aside from
      this positive alloc_base condition, the response function applies
      no adhoc limits: earnings marginal tax rates are used exactly as
      computed, with no cap, so a marginal tax rate at or above one
      generates a zero or negative baseline net-of-tax rate and hence an
      extreme substitution effect for that filing unit.  Likewise, there
      is no limit on the capital-gains response, whose exponential form
      can generate large proportional changes when the change in the
      capital-gains marginal tax rate is large.

    What is not modeled:

      Each analysis year is handled independently: this function contains
      no logic that carries a response in one year over into another
      year, so retiming behavior --- most notably the realization timing
      of capital gains --- is not modeled.  There are no response margins
      for the spouse's earnings, for short-term capital gains, for
      deduction items other than the mechanical e19200 adjustment
      described above, or for any margin not represented by the three
      elasticities.  Being a partial-equilibrium calculation, the
      analysis holds constant all prices, wages, and macroeconomic
      aggregates.

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
      Specifying be_cg equal to a published tax-rate elasticity such as
      -0.792 is therefore a common mistake that generates a much smaller
      capital-gains response than intended.
    """
    # pylint: disable=too-many-locals,too-many-statements,too-many-branches

    # Check function argument types and elasticity values
    assert isinstance(calc_1, Calculator)
    assert isinstance(calc_2, Calculator)
    assert isinstance(elasticities, dict)
    be_sub = elasticities['sub'] if 'sub' in elasticities else 0.0
    be_inc = elasticities['inc'] if 'inc' in elasticities else 0.0
    be_cg = elasticities['cg'] if 'cg' in elasticities else 0.0
    assert be_sub >= 0.0
    assert be_inc <= 0.0
    assert be_cg <= 0.0
    calc1 = copy.deepcopy(calc_1)
    calc2 = copy.deepcopy(calc_2)

    # Begin nested functions used only in this response function
    def _update_ordinary_income(taxinc_change, calc):
        """
        Implement total taxable income change induced by behavioral response.
        """
        # compute allocation base: AGI minus itemized deductions
        # Note: alloc_base is not an approximation of taxable income and
        # must not be replaced by the c04800 taxable income variable; it
        # is the sum of the three components being adjusted below, which
        # is what makes the three allocation shares sum to one.  See the
        # response function docstring for details.
        agi = calc.array('c00100')
        ided = np.where(calc.array('c04470') < calc.array('standard'),
                        0., calc.array('c04470'))
        alloc_base = agi - ided
        # apply response only where the allocation arithmetic is valid
        # Note: this guards against a zero denominator and against the
        # negative shares implied by a negative alloc_base.  It is not an
        # economic screen and must not be tightened to require positive
        # c04800: a filing unit with zero taxable income can still owe
        # payroll tax and therefore can still have an income effect.
        pos = np.array(alloc_base > 0., dtype=bool)
        # allocate change in taxable income into three parts
        # Note: because oinc is agi minus winc, the three parts always
        # satisfy delta_winc + delta_oinc - delta_ided == taxinc_change
        # for the pos filing units, so there is nothing to check here.
        # pylint: disable=unsupported-assignment-operation
        winc = calc.array('e00200')
        oinc = agi - winc
        share = np.zeros_like(agi)
        share[pos] = taxinc_change[pos] / alloc_base[pos]
        delta_winc = share * winc
        delta_oinc = share * oinc
        delta_ided = share * ided
        # add the three parts to different records variables embedded in calc
        calc.incarray('e00200', delta_winc)
        calc.incarray('e00200p', delta_winc)
        calc.incarray('e00300', delta_oinc)
        calc.incarray('e19200', delta_ided)
        return calc

    def _mtr12(calc__1, calc__2, mtr_of='e00200p', tax_type='combined'):
        """
        Computes marginal tax rates for Calculator objects calc__1 and calc__2
        for specified mtr_of income type and specified tax_type.

        Both calc__1 and calc__2 must already have had their calc_all
        method called, which allows the mtr method to skip one of the two
        calc_all calls it would otherwise make for each Calculator object.
        """
        assert tax_type in ('combined', 'iitax')
        _, iitax1, combined1 = calc__1.mtr(mtr_of,
                                           calc_all_already_called=True,
                                           wrt_full_compensation=True)
        _, iitax2, combined2 = calc__2.mtr(mtr_of,
                                           calc_all_already_called=True,
                                           wrt_full_compensation=True)
        if tax_type == 'combined':
            return (combined1, combined2)
        return (iitax1, iitax2)
    # End nested functions used only in this response function

    # Begin main logic of response function
    assert calc1.array_len == calc2.array_len
    assert calc1.current_year == calc2.current_year
    calc1.calc_all()
    calc2.calc_all()
    if dump:
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        dvars = sorted(recs_vinfo.USABLE_READ_VARS |
                       recs_vinfo.CALCULATED_VARS)
    # Calculate sum of substitution and income effects
    zero_sub_and_inc = be_sub == 0.0 and be_inc == 0.0
    # Note: the wage marginal tax rates are used only by the substitution
    # effect and by the dump output, so they are not computed when be_sub
    # is zero unless they are needed for the dump output
    if be_sub == 0.0 and (zero_sub_and_inc or not dump):
        wage_mtr1 = np.zeros(calc1.array_len)
        wage_mtr2 = np.zeros(calc2.array_len)
    else:
        # calculate marginal combined tax rates on taxpayer wages+salary
        # (e00200p is taxpayer's wages+salary)
        wage_mtr1, wage_mtr2 = _mtr12(calc1, calc2,
                                      mtr_of='e00200p',
                                      tax_type='combined')
    if zero_sub_and_inc:
        si_chg = None  # is not used when zero_sub_and_inc is True
    else:
        # calculate magnitude of substitution effect
        if be_sub == 0.0:
            sub = np.zeros(calc1.array_len)
        else:
            # proportional change in marginal net-of-tax rates on earnings
            pch = ((1. - wage_mtr2) / (1. - wage_mtr1)) - 1.
            # Note: c04800 is filing unit's taxable income
            # Scaling by taxable income (rather than by earnings, as the
            # labor_response and quantity_response functions do) is by
            # design; see the module docstring.
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
        df1.drop(['mtr_inctax', 'mtr_paytax'], axis='columns', inplace=True)
        df1['mtr_combined'] = wage_mtr1 * 100
    else:
        df1 = calc1.dataframe(DIST_VARIABLES)
    del calc1
    # Add behavioral-response changes to income sources
    # Note: calc2 is already a private deepcopy of the calc_2 argument,
    # so it can be modified without making another deepcopy of it
    calc2_behv = calc2
    del calc2
    if not zero_sub_and_inc:
        calc2_behv = _update_ordinary_income(si_chg, calc2_behv)
    calc2_behv.incarray('p23250', ltcg_chg)
    # Recalculate post-reform taxes incorporating behavioral responses
    calc2_behv.calc_all()
    # Extract dataframe from calc2_behv
    if dump:
        df2 = calc2_behv.dataframe(dvars)
        df2.drop(['mtr_inctax', 'mtr_paytax'], axis='columns', inplace=True)
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

    This is a helper function for the quantity_response function; it is
    not part of the public API of this module (it is not in __all__) and
    it is not used by the response function.

    A val1 element equal to zero implies an undefined proportional
    change, so this function returns a zero response for such elements
    rather than generating a divide-by-zero warning.

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
