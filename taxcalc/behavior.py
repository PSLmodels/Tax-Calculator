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
from .parameters import ParametersBase


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
        super(Behavior, self).__init__()
        if behavior_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(behavior_dict, dict):
            self._vals = behavior_dict
        else:
            raise ValueError('behavior_dict is not None or a dictionary')
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

    @staticmethod
    def response(calc_x, calc_y):
        """
        Modify calc_y records to account for behavioral responses that arise
        from the policy reform that involves moving from calc_x.policy to
        calc_y.policy.
        Returns new Calculator object --- a deepcopy of calc_y --- that
        incorporates behavioral responses to the reform.
        """
        # Calculate marginal tax rates
        #   e00200p is taxpayer's wages+salary
        #   p23250 is filing unit's long-term capital gains
        wage_mtr_x, wage_mtr_y = Behavior._mtr_xy(calc_x, calc_y,
                                                  mtr_of='e00200p',
                                                  liability_type='combined')
        ltcg_mtr_x, ltcg_mtr_y = Behavior._mtr_xy(calc_x, calc_y,
                                                  mtr_of='p23250',
                                                  liability_type='iitax')
        # Calculate proportional change (pch) in marginal net-of-tax rates
        wage_pch = ((1. - wage_mtr_y) - (1. - wage_mtr_x)) / (1. - wage_mtr_x)
        ltcg_pch = ((1. - ltcg_mtr_y) - (1. - ltcg_mtr_x)) / (1. - ltcg_mtr_x)
        # Calculate magnitude of substitution and income effects and their sum
        #   c04800 is filing unit's taxable income
        #   _combined is filing unit's income+payroll tax liability
        substitution_effect = (calc_y.behavior.BE_sub * wage_pch *
                               calc_x.records.c04800)
        # pylint: disable=protected-access
        income_effect = (calc_y.behavior.BE_inc *
                         (calc_y.records._combined -
                          calc_x.records._combined))
        tax_inc_change = income_effect + substitution_effect
        # Calculate magnitude of behavioral response in long-term capital gains
        cap_gain_change = (calc_y.behavior.BE_cg * ltcg_pch *
                           calc_x.records.p23250)
        # Add behavioral-response changes to income sources
        calc_y_behavior = copy.deepcopy(calc_y)
        calc_y_behavior = Behavior._update_ordinary_income(tax_inc_change,
                                                           calc_y_behavior)
        calc_y_behavior = Behavior._update_cap_gain_income(cap_gain_change,
                                                           calc_y_behavior)
        # Recalculate post-reform taxes incorporating behavioral responses
        calc_y_behavior.calc_all()
        return calc_y_behavior

    # ----- begin private methods of Behavior class -----

    @staticmethod
    def _update_ordinary_income(taxinc_change, calc_y):
        """
        Implement total taxable income change induced by behavioral responses.
        """
        delta_inc = np.where(calc_y.records.c00100 > 0, taxinc_change, 0.)
        # Allocate taxinc_change across different income sources
        # pylint: disable=protected-access
        itemized = np.where(calc_y.records.c04470 < calc_y.records._standard,
                            0.,
                            calc_y.records.c04470)
        delta_wages = np.where(calc_y.records.c00100 + itemized > 0.,
                               (delta_inc * calc_y.records.e00200 /
                                (calc_y.records.c00100 + itemized)),
                               0.)
        other_inc = calc_y.records.c00100 - calc_y.records.e00200
        delta_other_inc = np.where(calc_y.records.c00100 + itemized > 0.,
                                   (delta_inc * other_inc /
                                    (calc_y.records.c00100 + itemized)),
                                   0.)
        delta_itemized = np.where(calc_y.records.c00100 + itemized > 0.,
                                  (delta_inc * itemized /
                                   (calc_y.records.c00100 + itemized)),
                                  0.)
        calc_y.records.e00200 = calc_y.records.e00200 + delta_wages
        calc_y.records.e00200p = calc_y.records.e00200p + delta_wages
        calc_y.records.e00300 = calc_y.records.e00300 + delta_other_inc
        calc_y.records.e19570 = np.where(itemized > 0.,
                                         (calc_y.records.e19570 +
                                          delta_itemized),
                                         0.)
        # TODO, we should create a behavioral modification
        # variable instead of using e19570
        return calc_y

    @staticmethod
    def _update_cap_gain_income(cap_gain_change, calc_y):
        """
        Implement capital gain change induced by behavioral responses.
        """
        # pylint: disable=no-self-use
        calc_y.records.p23250 = calc_y.records.p23250 + cap_gain_change
        return calc_y

    @staticmethod
    def _mtr_xy(calc_x, calc_y, mtr_of, liability_type):
        """
        Computes marginal tax rates for Calculator objects calc_x and calc_y
        for specified mtr_of income type and specified liability_type.
        """
        _, iitax_x, combined_x = calc_x.mtr(mtr_of)
        _, iitax_y, combined_y = calc_y.mtr(mtr_of)
        if liability_type == 'combined':
            return (combined_x, combined_y)
        elif liability_type == 'iitax':
            return (iitax_x, iitax_y)
        else:
            raise ValueError('liability_type must be "combined" or "iitax"')

# end Behavior class
