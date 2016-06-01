"""
Tax-Calculator elasticity-based behavioral-response Behavior class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 behavior.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy behavior.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import copy
import numpy as np
from .policy import Policy
from .parameters_base import ParametersBase


class Behavior(ParametersBase):
    """
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

    inflation_rates: must be equal to None.

    Raises
    ------
    ValueError:
        if behavior_dict is neither None nor a dictionary.
        if num_years is less than one.
        if inflation_rates is not equal to None.

    Returns
    -------
    class instance: Behavior
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'behavior.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self, behavior_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None):
        # pylint: disable=super-init-not-called
        if behavior_dict is None:
            self._vals = self._params_dict_from_json_file()
        else:
            if isinstance(behavior_dict, dict):
                self._vals = behavior_dict
            else:
                raise ValueError('specified behavior_dict is not a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Behavior ctor')
        if inflation_rates is not None:
            raise ValueError('inflation_rates != None in Behavior ctor')
        self.initialize(start_year, num_years)

    def update_behavior(self, revisions):
        """
        Update behavior for given revisions, a dictionary consisting
        of one or more year:modification dictionaries.
        For example: {2014: {'_BE_sub': [0.4, 0.3]}}
        Also checks for valid elasticity values in revisions dictionary.
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        if self.current_year != self.start_year:
            self.set_year(self.start_year)
        msg = '{} elasticity cannot be {}; value is {}'
        pos = 'positive'
        neg = 'negative'
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            # enforce valid elasticity values in each revisons[year] dictionary
            for elast in revisions[year]:
                for idx in range(len(revisions[year][elast])):
                    val = revisions[year][elast][idx]
                    if elast == '_BE_inc':
                        if val > 0.0:
                            raise ValueError(msg.format(elast, pos, val))
                    elif elast == '_BE_sub':
                        if val < 0.0:
                            raise ValueError(msg.format(elast, neg, val))
                    elif elast == '_BE_cg':
                        if val < 0.0:
                            raise ValueError(msg.format(elast, neg, val))
                    else:
                        raise ValueError('illegal elasticity {}'.format(elast))
            # update valid elasticity values for year
            self._update({year: revisions[year]})
        self.set_year(precall_current_year)

    def has_response(self):
        """
        Returns true if any behavioral-response elasticity is non-zero for
        the current_year; returns false if all elasticities are zero.
        """
        # pylint: disable=no-member
        if self.BE_inc or self.BE_sub or self.BE_cg:
            return True
        else:
            return False

    def response(self, calc_x, calc_y):
        """
        Modify calc_y records to account for behavioral responses that arise
        from the policy reform that involves moving from calc_x.policy to
        calc_y.policy.
        Returns new Calculator object --- a deepcopy of calc_y --- that
        incorporates behavioral responses to the reform.
        """
        # pylint: disable=too-many-locals
        assert calc_x.records.dim == calc_y.records.dim
        # Calculate marginal tax rates and the corresponding
        # proportional changes (pch) in marginal net-of-tax rates
        if calc_y.behavior.BE_sub:
            # e00200p is taxpayer's wages+salary
            wage_mtr_x, wage_mtr_y = self._mtr_xy(calc_x, calc_y,
                                                  mtr_of='e00200p',
                                                  liability_type='combined')
            wage_pch = ((1. - wage_mtr_y) / (1. - wage_mtr_x)) - 1.
        if calc_y.behavior.BE_cg:
            # p23250 is filing unit's long-term capital gains
            ltcg_mtr_x, ltcg_mtr_y = self._mtr_xy(calc_x, calc_y,
                                                  mtr_of='p23250',
                                                  liability_type='iitax')
            ltcg_pch = ((1. - ltcg_mtr_y) / (1. - ltcg_mtr_x)) - 1.
        # Calculate proportional change (pch) in after-tax income, ati
        if calc_y.behavior.BE_inc:
            # c00100 is filing unit's adjusted gross income, AGI
            # _combined is filing unit's income+payroll tax liability
            # pylint: disable=protected-access
            ati_x = calc_x.records.c00100 - calc_x.records._combined
            ati_y = calc_y.records.c00100 - calc_y.records._combined
            ati_pch = (ati_y / ati_x) - 1.
        # Calculate magnitude of substitution and income effects and their sum
        #   c04800 is filing unit's taxable income
        if calc_y.behavior.BE_sub:
            sub = calc_y.behavior.BE_sub * wage_pch * calc_x.records.c04800
        else:
            sub = np.zeros(calc_x.records.dim)
        if calc_y.behavior.BE_inc:
            inc = calc_y.behavior.BE_inc * ati_pch * ati_x
        else:
            inc = np.zeros(calc_x.records.dim)
        taxinc_chg = sub + inc
        # Calculate magnitude of behavioral response in long-term capital gains
        if calc_y.behavior.BE_cg:
            ltcg_chg = calc_y.behavior.BE_cg * ltcg_pch * calc_x.records.p23250
        else:
            ltcg_chg = np.zeros(calc_x.records.dim)
        # Add behavioral-response changes to income sources
        calc_y_behv = copy.deepcopy(calc_y)
        calc_y_behv = self._update_ordinary_income(taxinc_chg, calc_y_behv)
        calc_y_behv = self._update_cap_gain_income(ltcg_chg, calc_y_behv)
        # Recalculate post-reform taxes incorporating behavioral responses
        calc_y_behv.calc_all()
        return calc_y_behv

    # ----- begin private methods of Behavior class -----

    def _update_ordinary_income(self, taxinc_change, calc):
        """
        Implement total taxable income change induced by behavioral response.
        """
        # pylint: disable=no-self-use,protected-access
        # Assume no behv response for filing units with no, or negative, AGI
        delta_income = np.where(calc.records.c00100 > 0., taxinc_change, 0.)
        # Compute itemized deductions, ided
        ided = np.where(calc.records.c04470 < calc.records._standard,
                        0.,
                        calc.records.c04470)
        # Compute AGI plus itemized deductions, agi_ided
        agi_ided = calc.records.c00100 + ided
        # Allocate delta_income
        delta_wage = np.where(agi_ided > 0.,
                              delta_income * calc.records.e00200 / agi_ided,
                              0.)
        oinc = calc.records.c00100 - calc.records.e00200
        delta_oinc = np.where(agi_ided > 0.,
                              delta_income * oinc / agi_ided,
                              0.)
        delta_ided = np.where(agi_ided > 0.,
                              delta_income * ided / agi_ided,
                              0.)
        calc.records.e00200 = calc.records.e00200 + delta_wage
        calc.records.e00200p = calc.records.e00200p + delta_wage
        calc.records.e00300 = calc.records.e00300 + delta_oinc
        calc.records.e19570 = np.where(ided > 0.,
                                       calc.records.e19570 + delta_ided,
                                       0.)
        # TODO, we should create a behavioral modification
        # variable instead of using e19570
        return calc

    def _update_cap_gain_income(self, cap_gain_change, calc):
        """
        Implement capital gain change induced by behavioral responses.
        """
        # pylint: disable=no-self-use
        calc.records.p23250 = calc.records.p23250 + cap_gain_change
        return calc

    def _mtr_xy(self, calc_x, calc_y, mtr_of, liability_type):
        """
        Computes marginal tax rates for Calculator objects calc_x and calc_y
        for specified mtr_of income type and specified liability_type.
        """
        # pylint: disable=no-self-use
        _, iitax_x, combined_x = calc_x.mtr(mtr_of)
        _, iitax_y, combined_y = calc_y.mtr(mtr_of)
        if liability_type == 'combined':
            return (combined_x, combined_y)
        elif liability_type == 'iitax':
            return (iitax_x, iitax_y)
        else:
            raise ValueError('liability_type must be "combined" or "iitax"')

# end Behavior class
