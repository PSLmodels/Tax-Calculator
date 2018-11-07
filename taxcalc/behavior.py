"""
Tax-Calculator elasticity-based behavioral-response Behavior class.
"""
# CODING-STYLE CHECKS:
# pycodestyle behavior.py
# pylint --disable=locally-disabled behavior.py

import copy
import numpy as np
from taxcalc.policy import Policy
from taxcalc.parameters import Parameters


class Behavior(Parameters):
    """
    Behavior is a subclass of the abstract Parameters class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for elasticity-based behavioral-response class.

    WARNING: the Behavior class is deprecated and will be removed soon.
    FUTURE: use the Behavioral-Responses behresp package OR
            use the Tax-Calculator quantity_response function.

    Parameters
    ----------
    start_year: integer
        first calendar year for behavioral-response elasticities.

    num_years: integer
        number of calendar years for which to specify elasticity
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if start_year is less than Policy.JSON_START_YEAR
        if num_years is less than one.

    Returns
    -------
    class instance: Behavior
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'behavior.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        print(('WARNING: the Behavior class is deprecated '
               'and will be removed soon.'))
        print('FUTURE: use the Behavioral-Responses behresp package OR')
        print('        use the Tax-Calculator quantity_response function.')
        super(Behavior, self).__init__()
        self._vals = self._params_dict_from_json_file()
        if start_year < Policy.JSON_START_YEAR:
            raise ValueError('start_year < Policy.JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years < 1')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_behavior(self, revision):
        """
        Implement multi-year behavior revision leaving current_year unchanged.

        Parameters
        ----------
        revision: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        Raises
        ------
        ValueError:
            if revision is not a dictionary.
            if each YEAR in revision is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.
            if _validate_assump_parameter_names_types generates errors.
            if _validate_assump_parameter_values generates errors.

        Returns
        -------
        nothing: void

        Notes
        -----
        Given a revision dictionary, typical usage of the Policy class
        is as follows::

            behavior = Behavior()
            behavior.update_behavior(revision)

        In the above statements, the Behavior() call instantiates a
        behavior object (behavior) containing behavior baseline parameters,
        and the update_behavior(revision) call applies the (possibly
        multi-year) revision specified in revision and then sets the
        current_year to the value of current_year when update_behavior
        was called with parameters set for that pre-call year.

        An example of a multi-year, multi-parameter revision is as follows::

            revision = {
                2016: {
                    '_BE_inc': [-0.3]
                },
                2017: {
                    '_BE_sub': [0.2]
                }
            }

        Notice that each of the four YEAR:MODS pairs is specified as
        required by the private _update method, whose documentation
        provides several MODS dictionary examples.

        IMPORTANT NOTICE: when specifying a revision dictionary always group
        all revision provisions for a specified year into one YEAR:MODS pair.
        If you make the mistake of specifying two or more YEAR:MODS pairs
        with the same YEAR value, all but the last one will be overwritten,
        and therefore, not part of the revision.  This is because Python
        expects unique (not multiple) dictionary keys.  There is no way to
        catch this error, so be careful to specify revision dictionaries
        correctly.
        """
        # check that all revisions dictionary keys are integers
        if not isinstance(revision, dict):
            raise ValueError('ERROR: revision is not a dictionary')
        if not revision:
            return  # no revision to implement
        revision_years = sorted(list(revision.keys()))
        for year in revision_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in revision is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining revision_years
        first_revision_year = min(revision_years)
        if first_revision_year < self.start_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_revision_year, self.start_year))
        if first_revision_year < self.current_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < current_year={}'
            raise ValueError(
                msg.format(first_revision_year, self.current_year)
            )
        last_revision_year = max(revision_years)
        if last_revision_year > self.end_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_revision_year, self.end_year))
        # validate revision parameter names and types
        self._validate_assump_parameter_names_types(revision)
        if self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # implement the revision year by year
        precall_current_year = self.current_year
        revision_parameters = set()
        for year in revision_years:
            self.set_year(year)
            revision_parameters.update(revision[year].keys())
            self._update({year: revision[year]})
        self.set_year(precall_current_year)
        # validate revision parameter values
        self._validate_assump_parameter_values(revision_parameters)
        if self.parameter_errors:
            raise ValueError('\n' + self.parameter_errors)

    def has_response(self):
        """
        Returns true if any behavioral-response elasticity is non-zero for
        the current_year; returns false if all elasticities are zero.
        """
        # pylint: disable=no-member
        all_zero = (self.BE_sub == 0.0 and
                    self.BE_inc == 0.0 and
                    self.BE_cg == 0.0)
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
        mtr_cap = 0.99
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
                mtr1 = np.where(wage_mtr1 > mtr_cap, mtr_cap, wage_mtr1)
                mtr2 = np.where(wage_mtr2 > mtr_cap, mtr_cap, wage_mtr2)
                pch = ((1. - mtr2) / (1. - mtr1)) - 1.
                # Note: c04800 is filing unit's taxable income
                sub = (calc2.behavior('BE_sub') *
                       pch * calc1.array('c04800'))
                if trace:
                    trace_output('wmtr1', wage_mtr1,
                                 [-9e99, 0.00, 0.25, 0.50, 0.60,
                                  0.70, 0.80, 0.90, 0.999999, 1.1,
                                  1.2, 1.3, 9e99],
                                 calc1.array('s006'),
                                 np.zeros(calc1.array_len))
                    print('high wage_mtr1:',
                          wage_mtr1[wage_mtr1 > 0.999999])
                    print('wage_mtr2 them:',
                          wage_mtr2[wage_mtr1 > 0.999999])
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
            #  p23250 is filing units' long-term capital gains
            ltcg_mtr1, ltcg_mtr2 = Behavior._mtr12(calc1, calc2,
                                                   mtr_of='p23250',
                                                   tax_type='iitax')
            rch = ltcg_mtr2 - ltcg_mtr1
            exp_term = np.exp(calc2.behavior('BE_cg') * rch)
            new_ltcg = calc1.array('p23250') * exp_term
            ltcg_chg = new_ltcg - calc1.array('p23250')
        # Add behavioral-response changes to income sources
        calc2_behv = copy.deepcopy(calc2)
        if not zero_sub_and_inc:
            calc2_behv = Behavior._update_ordinary_income(si_chg,
                                                          calc2_behv)
        calc2_behv = Behavior._update_cap_gain_income(ltcg_chg,
                                                      calc2_behv)
        # Recalculate post-reform taxes incorporating behavioral responses
        calc2_behv.calc_all()
        calc2_behv.records_include_behavioral_responses()
        return calc2_behv

    # ----- begin private methods of Behavior class -----

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
    def _mtr12(calc1, calc2, mtr_of='e00200p', tax_type='combined'):
        """
        Computes marginal tax rates for Calculator objects calc1 and calc2
        for specified mtr_of income type and specified tax_type.
        """
        _, iitax1, combined1 = calc1.mtr(mtr_of, wrt_full_compensation=True)
        _, iitax2, combined2 = calc2.mtr(mtr_of, wrt_full_compensation=True)
        if tax_type == 'combined':
            return (combined1, combined2)
        if tax_type == 'iitax':
            return (iitax1, iitax2)
        raise ValueError('tax_type must be "combined" or "iitax"')
