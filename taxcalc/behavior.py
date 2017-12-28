"""
Tax-Calculator elasticity-based behavioral-response Behavior class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 behavior.py
# pylint --disable=locally-disabled behavior.py

from __future__ import print_function
import copy
import numpy as np
from taxcalc.policy import Policy
from taxcalc.parameters import ParametersBase


class Behavior(ParametersBase):
    """
    Behavior is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for elasticity-based behavioral-response class.

    Parameters
    ----------
    behavior_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of behavioral-response elasticities; if None, default
        elasticities are read from the behavior.json file.

    start_year: integer
        first calendar year for behavioral-response elasticities.

    num_years: integer
        number of calendar years for which to specify elasticity
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if behavior_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Behavior
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'behavior.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self, behavior_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Behavior, self).__init__()
        if behavior_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(behavior_dict, dict):
            self._vals = behavior_dict
        else:
            raise ValueError('behavior_dict is not None or a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Behavior ctor')
        self.initialize(start_year, num_years)
        self._validate_parameter_values()

    def update_behavior(self, revisions):
        """
        Update behavior for given revisions, a dictionary consisting
        of one or more year:modification dictionaries.
        For example: {2014: {'_BE_sub': [0.4, 0.3]}}
        Also checks for valid elasticity values in revisions dictionary.

        Note that this method uses the specified revisions to update the
        default elasticity values, so use this method just once
        rather than calling it sequentially in an attempt to update
        elasticities in several steps.
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            self._update({year: revisions[year]})
        self.set_year(precall_current_year)
        self._validate_parameter_values()

    def has_response(self):
        """
        Returns true if any behavioral-response elasticity is non-zero for
        the current_year; returns false if all elasticities are zero.
        """
        # pylint: disable=no-member
        all_zero = (self.BE_sub == 0.0 and
                    self.BE_inc == 0.0 and
                    self.BE_cg == 0.0 and
                    self.BE_charity.tolist() == [0.0, 0.0, 0.0])
        return not all_zero

    def has_any_response(self):
        """
        Returns true if any behavioral-response elasticity is non-zero in
        any year; returns false if all elasticities are zero in all years.
        """
        for elast in self._vals:
            values = getattr(self, elast)
            for year in np.ndindex(values.shape):
                val = values[year]
                if val != 0.0:
                    return True
        return False

    @staticmethod
    def response(calc1, calc2, trace=False):
        """
        Implements TaxBrain "Partial Equilibrium Simulation" dynamic analysis.

        Modify calc2 records to account for behavioral responses that arise
          from the policy reform that involves moving from calc1 policy to
          calc2 policy.  Neither calc1 nor calc2 need to have had calc_all()
          executed before calling the Behavior.response(calc1, calc2) method.
        Returns new Calculator object --- a deepcopy of calc2 --- that
          incorporates behavioral responses to the reform.
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
          into a much larger absolute value for the _BE_cg semi-elasticity
          used by Tax-Calculator.
          To calculate the elasticity from a semi-elasticity, we multiply by
          MTRs from TC and weight by shares of taxable gains. To avoid those
          with zero MTRs, we restrict this to the top 40% of tax units by AGI.
          Using this method, a semi-elasticity of -3.45 corresponds to a tax
          rate elasticity of -0.792.
        """
        # pylint: disable=too-many-statements,too-many-locals,too-many-branches

        # nested function used only in response
        def trace_output(varname, variable, histbins, pweight, dweight):
            """
            Print trace output for specified variable.
            """
            print('*** TRACE for variable {}'.format(varname))
            hist = np.histogram(variable, bins=histbins)
            print('*** Histogram:')
            print(hist[0])
            print(hist[1])
            if pweight.sum() != 0:
                out = '*** Person-weighted mean= {:.2f}'
                mean = (variable * pweight).sum() / pweight.sum()
                print(out.format(mean))
            if dweight.sum() != 0:
                out = '*** Dollar-weighted mean= {:.2f}'
                mean = (variable * dweight).sum() / dweight.sum()
                print(out.format(mean))

        # begin main logic of response
        assert calc1.array_len == calc2.array_len
        assert calc1.current_year == calc2.current_year
        # calculate sum of substitution and income effects
        if calc2.behavior('BE_sub') == 0.0 and calc2.behavior('BE_inc') == 0.0:
            zero_sub_and_inc = True
        else:
            zero_sub_and_inc = False
            # calculate marginal combined tax rates on taxpayer wages+salary
            # (e00200p is taxpayer's wages+salary)
            wage_mtr1, wage_mtr2 = Behavior._mtr12(calc1, calc2,
                                                   mtr_of='e00200p',
                                                   tax_type='combined')
            # calculate magnitude of substitution effect
            if calc2.behavior('BE_sub') == 0.0:
                sub = np.zeros(calc1.array_len)
            else:
                # proportional change in marginal net-of-tax rates on earnings
                nearone = 0.999999
                mtr1 = np.where(wage_mtr1 > nearone, nearone, wage_mtr1)
                mtr2 = np.where(wage_mtr2 > nearone, nearone, wage_mtr2)
                pch = ((1. - mtr2) / (1. - mtr1)) - 1.
                if calc2.behavior('BE_subinc_wrt_earnings'):
                    # Note: e00200 is filing unit's wages+salaries
                    sub = (calc2.behavior('BE_sub') *
                           pch * calc1.array('e00200'))
                else:
                    # Note: c04800 is filing unit's taxable income
                    sub = (calc2.behavior('BE_sub') *
                           pch * calc1.array('c04800'))
                    if trace:
                        trace_output('pch', pch,
                                     [-9e99, -1.00, -0.50, -0.20, -0.10,
                                      -0.00001, 0.00001,
                                      0.10, 0.20, 0.50, 1.00, 9e99],
                                     calc1.array('s006'),
                                     calc1.array('c04800'))
                        trace_output('sub', sub,
                                     [-9e99, -1e3,
                                      -0.1, 0.1,
                                      1e3, 1e4, 1e5, 1e6, 9e99],
                                     calc1.array('s006'),
                                     np.zeros(calc1.array_len))
            # calculate magnitude of income effect
            if calc2.behavior('BE_inc') == 0.0:
                inc = np.zeros(calc1.array_len)
            else:
                if calc2.behavior('BE_subinc_wrt_earnings'):
                    # proportional change in after-tax income
                    with np.errstate(invalid='ignore'):
                        pch = np.where(calc1.array('aftertax_income') > 0.,
                                       (calc2.array('aftertax_income') /
                                        calc1.array('aftertax_income')) - 1.,
                                       0.)
                    inc = (calc2.behavior('BE_inc') *
                           pch * calc1.array('e00200'))
                else:
                    # dollar change in after-tax income
                    # Note: combined is f.unit's income+payroll tax liability
                    dch = calc1.array('combined') - calc2.array('combined')
                    inc = calc2.behavior('BE_inc') * dch
            # calculate sum of substitution and income effects
            si_chg = sub + inc
        # calculate long-term capital-gains effect
        if calc2.behavior('BE_cg') == 0.0:
            ltcg_chg = np.zeros(calc1.array_len)
        else:
            # calculate marginal tax rates on long-term capital gains
            # (p23250 is filing units' long-term capital gains)
            ltcg_mtr1, ltcg_mtr2 = Behavior._mtr12(calc1, calc2,
                                                   mtr_of='p23250',
                                                   tax_type='iitax')
            rch = ltcg_mtr2 - ltcg_mtr1
            exp_term = np.exp(calc2.behavior('BE_cg') * rch)
            new_ltcg = calc1.array('p23250') * exp_term
            ltcg_chg = new_ltcg - calc1.array('p23250')
        # calculate charitable giving effect
        no_charity_response = (calc2.behavior('BE_charity').tolist() ==
                               [0.0, 0.0, 0.0])
        if no_charity_response:
            c_charity_chg = np.zeros(calc1.array_len)
            nc_charity_chg = np.zeros(calc1.array_len)
        else:
            # calculate marginal tax rate on charitable contributions
            # e19800 is filing units' cash charitable contributions
            # e20100 is filing units' non-cash charitable contributions
            # cash:
            c_charity_mtr1, c_charity_mtr2 = Behavior._mtr12(
                calc1, calc2, mtr_of='e19800', tax_type='combined')
            c_charity_price_pch = (((1. + c_charity_mtr2) /
                                    (1. + c_charity_mtr1)) - 1.)
            # non-cash:
            nc_charity_mtr1, nc_charity_mtr2 = Behavior._mtr12(
                calc1, calc2, mtr_of='e20100', tax_type='combined')
            nc_charity_price_pch = (((1. + nc_charity_mtr2) /
                                     (1. + nc_charity_mtr1)) - 1.)
            # identify income bin based on baseline income
            agi = calc1.array('c00100')
            low_income = (agi < 50000)
            mid_income = ((agi >= 50000) & (agi < 100000))
            high_income = (agi >= 100000)
            # calculate change in cash contributions
            c_charity_chg = np.zeros(calc1.array_len)
            # AGI < 50000
            c_charity_chg = np.where(low_income,
                                     (calc2.behavior('BE_charity')[0] *
                                      c_charity_price_pch *
                                      calc1.array('e19800')),
                                     c_charity_chg)
            # 50000 <= AGI < 1000000
            c_charity_chg = np.where(mid_income,
                                     (calc2.behavior('BE_charity')[1] *
                                      c_charity_price_pch *
                                      calc1.array('e19800')),
                                     c_charity_chg)
            # 1000000 < AGI
            c_charity_chg = np.where(high_income,
                                     (calc2.behavior('BE_charity')[2] *
                                      c_charity_price_pch *
                                      calc1.array('e19800')),
                                     c_charity_chg)
            # calculate change in non-cash contributions
            nc_charity_chg = np.zeros(calc1.array_len)
            # AGI < 50000
            nc_charity_chg = np.where(low_income,
                                      (calc2.behavior('BE_charity')[0] *
                                       nc_charity_price_pch *
                                       calc1.array('e20100')),
                                      nc_charity_chg)
            # 50000 <= AGI < 1000000
            nc_charity_chg = np.where(mid_income,
                                      (calc2.behavior('BE_charity')[1] *
                                       nc_charity_price_pch *
                                       calc1.array('e20100')),
                                      nc_charity_chg)
            # 1000000 < AGI
            nc_charity_chg = np.where(high_income,
                                      (calc2.behavior('BE_charity')[2] *
                                       nc_charity_price_pch *
                                       calc1.array('e20100')),
                                      nc_charity_chg)
        # Add behavioral-response changes to income sources
        calc2_behv = copy.deepcopy(calc2)
        if not zero_sub_and_inc:
            if calc2_behv.behavior('BE_subinc_wrt_earnings'):
                calc2_behv = Behavior._update_earnings(si_chg,
                                                       calc2_behv)
            else:
                calc2_behv = Behavior._update_ordinary_income(si_chg,
                                                              calc2_behv)
        calc2_behv = Behavior._update_cap_gain_income(ltcg_chg,
                                                      calc2_behv)
        calc2_behv = Behavior._update_charity(c_charity_chg, nc_charity_chg,
                                              calc2_behv)
        # Recalculate post-reform taxes incorporating behavioral responses
        calc2_behv.calc_all()
        return calc2_behv

    # ----- begin private methods of Behavior class -----

    def _validate_parameter_values(self):
        """
        Check that all behavioral-response parameters have valid values.
        """
        # pylint: disable=too-many-branches,too-many-locals
        # check for presence of required parameters
        expected_num_params = 5
        num_params = 0
        for param in self._vals:
            if param == '_BE_sub':
                num_params += 1
            elif param == '_BE_inc':
                num_params += 1
            elif param == '_BE_subinc_wrt_earnings':
                num_params += 1
            elif param == '_BE_cg':
                num_params += 1
            elif param == '_BE_charity':
                num_params += 1
        if num_params != expected_num_params:
            msg = 'num required Behavior parameters {} not expected number {}'
            raise ValueError(msg.format(num_params, expected_num_params))
        # check validity of parameter values
        msg = '{} elasticity cannot be {} in year {}; value is {}'
        pos = 'positive'
        neg = 'negative'
        nob = 'non-boolean'
        for param in self._vals:
            values = getattr(self, param)
            for year in np.ndindex(values.shape):
                val = values[year]
                cyr = year[0] + self.start_year
                if param == '_BE_sub':
                    if val < 0.0:
                        raise ValueError(msg.format(param, neg, cyr, val))
                elif param == '_BE_inc':
                    if val > 0.0:
                        raise ValueError(msg.format(param, pos, cyr, val))
                elif param == '_BE_subinc_wrt_earnings':
                    if val < 0 or val > 1:
                        raise ValueError(msg.format(param, nob, cyr, val))
                elif param == '_BE_cg':
                    if val > 0.0:
                        raise ValueError(msg.format(param, pos, cyr, val))
                elif param == '_BE_charity':
                    if val > 0.0:
                        raise ValueError(msg.format(param, neg, cyr, val))
        # check consistency of earnings-related parameters
        subinc_wrt_earnings = getattr(self, '_BE_subinc_wrt_earnings')
        sub_elasticity = getattr(self, '_BE_sub')
        inc_elasticity = getattr(self, '_BE_inc')
        msg = ('_BE_subinc_wrt_earnings is True in year {} '
               'when _BE_sub and _BE_inc are both zero')
        for year in range(self.num_years):
            if subinc_wrt_earnings[year]:
                zero_sub = sub_elasticity[year] == 0.0
                zero_inc = inc_elasticity[year] == 0.0
                if zero_sub and zero_inc:
                    raise ValueError(msg.format(year + self.start_year))

    @staticmethod
    def _update_earnings(change, calc):
        """
        Implement earnings change induced by earnings response.
        """
        calc.incarray('e00200', change)
        calc.incarray('e00200p', change)
        return calc

    @staticmethod
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

    @staticmethod
    def _update_cap_gain_income(cap_gain_change, calc):
        """
        Implement capital gain change induced by behavioral responses.
        """
        calc.incarray('p23250', cap_gain_change)
        return calc

    @staticmethod
    def _update_charity(cash_charity_change, non_cash_charity_change, calc):
        """
        Implement cash charitable contribution change induced
        by behavioral responses.
        """
        calc.incarray('e19800', cash_charity_change)
        calc.incarray('e20100', non_cash_charity_change)
        return calc

    @staticmethod
    def _mtr12(calc1, calc2, mtr_of='e00200p', tax_type='combined'):
        """
        Computes marginal tax rates for Calculator objects calc1 and calc2
        for specified mtr_of income type and specified tax_type.
        """
        _, iitax1, combined1 = calc1.mtr(mtr_of, wrt_full_compensation=True)
        _, iitax2, combined2 = calc2.mtr(mtr_of, wrt_full_compensation=True)
        if tax_type == 'combined':
            return (combined1, combined2)
        elif tax_type == 'iitax':
            return (iitax1, iitax2)
        else:
            raise ValueError('tax_type must be "combined" or "iitax"')
