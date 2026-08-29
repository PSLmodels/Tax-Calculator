"""
Partial-equilibrium elasticity-based behavioral-responses logic.

This module contains two independent sets of functions that are not
used by each other:

(1) The response function, which conducts partial-equilibrium
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

# Number of bisection steps used to solve the earnings-shift fixed-point
# equation in the response function.  The equation is solved by bisection
# on a bracket that is guaranteed to contain the solution, so this count
# is a precision setting rather than a convergence risk: each step halves
# the bracket, making sixty steps enough to locate the shifted wage to
# far less than a cent for any wage representable in the input data.
ESF_BISECTION_STEPS = 60


def response(calc_1, calc_2, elasticities, dump=False):
    """
    Implements conventional analysis (that is, static reform analysis
    plus partial-equilibrium behavior responses to a reform),
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
        contains the assumed response parameters/elasticities.  Omitting an
        key:value pair implies the omitted parameter/elasticity is
        assumed to be zero.  (Note that the tc CLI --behavior option is
        stricter: a JSON behavior file must contain all the keys.)
        Here is the full dictionary content and each parameter/elasticity's
        internal name:

        be_esf = elasticities['esf']
          Earnings shift factor.
          Defined as the fraction of the reform-induced change in employer
          payroll tax liability that is shifted to wages rather than to
          nontaxable employee fringe benefits such as employer-provided
          health insurance.  The shift is sign-symmetric: an increase in
          employer payroll tax liability decreases wages and a decrease
          increases them, although the two shifts are not equal in size
          because the employer tax rate that feeds back into the shifted
          wage differs between the two reforms.  It is calculated per
          earner, and it is applied before the elasticities below are
          evaluated.
          Must be in the [0,1] range.

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

      The earnings shift is computed first, and separately for the
      taxpayer and the spouse, because the OASDI cap (SS_Earnings_c) and
      the reform-only extra OASDI threshold (SS_Earnings_thd) apply per
      person rather than per filing unit, so a couple with two earners
      just below the cap and a couple with one earner well above it have
      different employer payroll tax exposure at the same filing-unit
      earnings.  Writing ptax_er(wage) for an earner's employer payroll
      tax liability on wages under reform policy as a function of that
      earner's wages, ptax_er_1 for the same earner's baseline employer
      payroll tax liability on wages, and wage2 for the earner's
      pre-shift reform wages, the shifted wage is the solution of

        wage = wage2 - be_esf * (ptax_er(wage) - ptax_er_1)

      This holds the be_esf fraction of the earner's gross compensation
      --- wages plus employer payroll tax --- fixed, and it is
      sign-symmetric: an increase in employer payroll tax liability
      lowers wages and a decrease raises them.  The remaining
      (1 - be_esf) fraction is absorbed by nontaxable fringe benefits,
      which are not represented in the input data.

      The equation is implicit in wage because ptax_er is a function of
      the wage being solved for, and it has no single closed-form
      solution because that function is piecewise linear.  Writing s0 and
      s1 for the baseline and reform employer OASDI rates, h for the
      employer HI rate, and cap for SS_Earnings_c, the two interior
      regimes are:

        wages below the cap under both policies, where the employer
        payroll tax is proportional to the wage in both its OASDI and its
        HI part, so the shift is proportional:

          wage = wage2 * (1 + be_esf * (s0 + h)) / (1 + be_esf * (s1 + h))

        wages above the cap under both policies, where the OASDI part is
        the flat amount s * cap and only the uncapped HI part varies with
        the wage, so the OASDI portion of the shift is a lump sum:

          wage = wage2 - be_esf * (s1 - s0) * cap / (1 + be_esf * h)

      In the second regime the earner's marginal wage is unchanged by an
      OASDI rate reform, so the shift is a pure income effect there,
      whereas in the first regime the marginal wage falls as well.  An
      earner whose wage cut carries them from above the cap to below it
      is in neither regime; such an earner is on the kink, where the
      wage cut shrinks their own employer OASDI liability, which in turn
      feeds back into the wage.  Because of these earners --- and of the
      band between the old and new caps under a reform to SS_Earnings_c
      itself --- the shift cannot be computed as a single average rate
      applied to all earners.  The implementation therefore solves the
      fixed-point equation numerically, by bisection on a bracket that is
      guaranteed to contain the solution, which handles all three cases
      without special-casing any of them and which cannot fail to
      converge at any employer payroll tax rate.

      The ptax_er function used here is the employer payroll tax on
      wages: the employer share of the OASDI tax on wages up to the
      SS_Earnings_c cap, plus the employer share of the reform-only extra
      OASDI tax on wages above the SS_Earnings_thd threshold, plus the
      employer share of the uncapped HI tax on wages, all of them
      evaluated on gross wages, which are wages plus employer pension
      contributions.  It is NOT the ptax_er_p and ptax_er_s output
      variables, whose extra-OASDI part is computed on a base that blends
      wage and self-employment earnings, as the EI_PayrollTax function
      documents.  Using those variables would shift onto wages an
      employer share of a tax on self-employment earnings, for which
      there is no employer, and that would be a large error under an
      SS_Earnings_thd reform for an earner whose self-employment earnings
      are much larger than their wages.  The cost of computing the wage
      part here is that the employer payroll tax rules are stated in this
      module as well as in the EI_PayrollTax function.

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

      The earnings shift is applied directly to the earnings variables of
      the two earners it is computed for: the taxpayer part is added to
      e00200p and the spouse part to e00200s, with e00200 incremented by
      their sum.  Nothing else is adjusted.  In particular, the pension
      contribution variables, pencon_p and pencon_s, are held fixed even
      though they are part of the employer payroll tax base, because
      nontaxable benefits are what the (1 - be_esf) fraction of the shift
      is defined to absorb.

      The shift is applied to a copy of calc_2 before the elasticities
      below are evaluated, and that copy is recalculated, so the reform
      marginal tax rates and tax liabilities that enter the substitution,
      income, and capital-gains responses are all measured at post-shift
      earnings.  The ordering matters because the shift is an accounting
      adjustment that defines the reform being analyzed --- it holds gross
      compensation fixed --- rather than a behavioral response to it, so
      the elasticity-driven responses are layered on top of it.  There is
      no double counting of the employer payroll tax: the substitution
      effect prices earnings using marginal tax rates computed with
      respect to full compensation, which is a different concept from the
      wage shift itself.

      The sum of the substitution and income effects is a change in
      taxable income that must be mapped back onto the input variables
      used in the tax calculation.  The dollar change is allocated in
      proportion to three components --- wage and salary income (e00200),
      other AGI (c00100 minus e00200), and itemized deductions --- and
      the three parts are added to these input variables:

        - the wage part is added to both e00200 and e00200p
        - the other-income part is added to e00300 (taxable interest)
        - the deduction part is added to e19200 (interest paid deduction)

      Two consequences are worth noting.  First, the spouse's earnings
      variable, e00200s, is not adjusted by this part of the response,
      so the substitution and income effects adjust e00200 and e00200p by
      the same amount.  (The earnings shift, in contrast, is calculated
      per earner and does adjust e00200s.)  Second, a
      response shows up in dump output as changes in e00300 and e19200 even
      for filing units whose actual behavior would involve other income or
      deduction items.  The capital-gains response, by contrast, is applied
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

      The earnings shift is skipped entirely when be_esf is zero and when
      the reform alters none of the four parameters of the employer
      payroll tax on wages: FICA_ss_trt_employer, FICA_mc_trt_employer,
      SS_Earnings_c, and SS_Earnings_thd.  That test is on the parameters
      themselves rather than on calculated tax amounts, so it is exact.
      Note that the employee-share rates are not among the four: they
      affect the ptax_er_p and ptax_er_s output variables under an
      SS_Earnings_thd reform, through the self-employment part of the
      extra OASDI bracket base, but they do not affect the employer
      payroll tax on wages that generates the shift.

      Within a reform that does change one of the four parameters, the
      shift is applied only to earners with positive wages.  That
      excludes the self-employed, who have no employer to shift a payroll
      tax to.  It also excludes an earner whose gross wages are entirely
      employer pension contributions: such an earner does generate an
      employer payroll tax liability, but has no wages to shift it onto,
      and shifting it onto an e00200p or e00200s of zero would make that
      variable negative.  Note that the employer payroll tax used for an
      included earner is nevertheless computed on gross wages, so it
      includes the part generated by that earner's pension
      contributions.

      The shifted wage is not floored at zero, consistent with the
      treatment of the responses below.  The shift is bounded by be_esf
      times the employer payroll tax rate times the gross wage, so under
      any plausible reform it is a small fraction of the wage, but a
      reform that sets an extreme employer rate, or an earner whose gross
      wages are mostly pension contributions, can drive a wage
      negative.

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
      described above, or for any margin not represented by the
      elasticities.  The earnings shift assumes full backward shifting of
      the be_esf fraction onto the individual earner who generated the
      employer payroll tax liability, so it models neither shifting across
      workers within an employer nor any forward shifting to consumers or
      to capital.  Being a partial-equilibrium calculation, the
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
      MTRs from T-C and weight by shares of taxable gains. To avoid those
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
    be_esf = elasticities['esf'] if 'esf' in elasticities else 0.0
    be_sub = elasticities['sub'] if 'sub' in elasticities else 0.0
    be_inc = elasticities['inc'] if 'inc' in elasticities else 0.0
    be_cg = elasticities['cg'] if 'cg' in elasticities else 0.0
    assert 0.0 <= be_esf <= 1.0
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

    def _employer_ptax_on_wages(calc, gross_ws):
        """
        Returns array of employer payroll tax liability on the specified
        array of one earner's gross wages (wages plus employer pension
        contributions) under the policy embedded in the specified
        Calculator object.

        Note: this duplicates the wage-and-salary part of the ptax_er_p
        and ptax_er_s logic in the EI_PayrollTax function, which cannot
        be used here because those two variables also contain an
        employer-rate share of the reform-only extra OASDI bracket on
        self-employment earnings, for which there is no employer.  See
        the response function docstring.
        """
        ss_rate = calc.policy_param('FICA_ss_trt_employer')
        mc_rate = calc.policy_param('FICA_mc_trt_employer')
        cap = calc.policy_param('SS_Earnings_c')
        thd = calc.policy_param('SS_Earnings_thd')
        return (ss_rate * (np.minimum(cap, gross_ws) +
                           np.maximum(0., gross_ws - thd)) +
                mc_rate * gross_ws)

    def _shifted_wage(calc, wage, pencon, ptax_er_1, esf):
        """
        Returns array of post-shift wages, which are the solution of the
        fixed-point equation described in the response function
        docstring, where wage is the array of pre-shift reform wages,
        pencon is the array of employer pension contributions, ptax_er_1
        is the array of baseline employer payroll tax liability on wages,
        and esf is the earnings shift factor.
        """
        def residual(wag):
            """
            Amount by which wag falls short of solving the fixed-point
            equation; it is increasing in wag with a slope of at least
            one, because employer payroll tax rates are nonnegative.
            """
            return wag - wage + esf * (
                _employer_ptax_on_wages(calc, wag + pencon) - ptax_er_1
            )
        # bracket the solution: because the residual has a slope of at
        # least one and is zero at the solution, the solution is no
        # farther from the pre-shift wage than the residual there
        offset = residual(wage)
        low = np.minimum(wage, wage - offset)
        high = np.maximum(wage, wage - offset)
        for _ in range(ESF_BISECTION_STEPS):
            mid = 0.5 * (low + high)
            below = residual(mid) < 0.
            low = np.where(below, mid, low)
            high = np.where(below, high, mid)
        return 0.5 * (low + high)

    # End nested functions used only in this response function

    # Begin main logic of response function
    assert calc1.array_len == calc2.array_len
    assert calc1.current_year == calc2.current_year
    calc1.calc_all()
    calc2.calc_all()
    # Calculate earnings shift caused by employer payroll tax liability change
    # Note: the shift depends on the wage-based part of the employer
    # payroll tax alone, so it can be skipped whenever the reform leaves
    # every parameter of that tax unchanged, which is an exact test that
    # requires no comparison of calculated tax amounts.
    esf_params = ('FICA_ss_trt_employer', 'FICA_mc_trt_employer',
                  'SS_Earnings_c', 'SS_Earnings_thd')
    earnings_shift = be_esf > 0. and any(
        calc1.policy_param(pname) != calc2.policy_param(pname)
        for pname in esf_params
    )
    if earnings_shift:
        # Hold each earner's gross compensation (wages plus employer
        # payroll tax) fixed by shifting the be_esf fraction of the
        # reform-induced change in employer payroll tax liability onto
        # wages, with the remaining fraction absorbed by nontaxable
        # fringe benefits, which are not represented in the input data
        # and therefore require no adjustment.
        # Note: the employer payroll tax is itself a piecewise-linear
        # function of the wage --- proportional in the uncapped HI tax and
        # in the OASDI tax below the SS_Earnings_c cap, but flat in the
        # OASDI tax above that cap --- so the shifted wage is the solution
        # of the fixed-point equation
        #   wage = wage2 - be_esf * (ptax_er(wage) - ptax_er_1)
        # rather than a quantity available in closed form.  The nested
        # _shifted_wage function solves that equation by bisection, which
        # handles the OASDI cap, the uncapped HI rate, and the reform-only
        # extra OASDI bracket without special-casing any of them, and
        # which finds the correct kink for an earner whose wage cut
        # carries them from above the OASDI cap to below it.
        # Note: the shift is calculated separately for the taxpayer and the
        # spouse because the OASDI cap and threshold apply per person, so
        # the filing-unit shift cannot be derived from filing-unit wages.
        # Earners with no wages are excluded: the self-employed, who have
        # no employer to shift a payroll tax to, and the rare earner whose
        # only gross wages are employer pension contributions, who has no
        # wages to shift onto.
        shift = {}
        for who in ('p', 's'):
            gross_ws_1 = (calc1.array(f'e00200{who}') +
                          calc1.array(f'pencon_{who}'))
            ptax_er_1 = _employer_ptax_on_wages(calc1, gross_ws_1)
            pencon_2 = calc2.array(f'pencon_{who}')
            wage_2 = calc2.array(f'e00200{who}')
            wage_shifted = _shifted_wage(calc2, wage_2, pencon_2,
                                         ptax_er_1, be_esf)
            shift[who] = np.where(wage_2 > 0., wage_shifted - wage_2, 0.)
        calc2.incarray('e00200p', shift['p'])
        calc2.incarray('e00200s', shift['s'])
        calc2.incarray('e00200', shift['p'] + shift['s'])
        calc2.calc_all()
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
        recs_vinfo = Records(data=None)  # contains records VARINFO only
        dvars = sorted(recs_vinfo.USABLE_READ_VARS |
                       recs_vinfo.CALCULATED_VARS)
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
