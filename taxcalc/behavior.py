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


def update_ordinary_income(taxinc_change, calc_y):
    """
    Implement total taxable income change induced by behavioral responses.
    """
    delta_inc = np.where(calc_y.records.c00100 > 0, taxinc_change, 0.)

    # Allocate taxinc_change across itemized deductions, wages, other income
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
                                     calc_y.records.e19570 + delta_itemized,
                                     0.)
    # TODO, we should create a behavioral modification
    # variable instead of using e19570

    return calc_y


def update_cap_gain_income(cap_gain_change, calc_y):
    """
    Implement capital gain change induced by behavioral responses.
    """
    calc_y.records.p23250 = calc_y.records.p23250 + cap_gain_change
    return calc_y


def behavior(calc_x, calc_y):
    """
    Modify plan Y records to account for behavioral responses that arise
    from the policy reform that involves moving from plan X to plan Y.
    """

    # Calculate marginal tax rates for plan X and plan Y
    wage_mtr_x, wage_mtr_y = mtr_xy(calc_x, calc_y,
                                    mtr_of='e00200p',  # taxpayer's wage+salary
                                    liability_type='combined')
    ltcg_mtr_x, ltcg_mtr_y = mtr_xy(calc_x, calc_y,
                                    mtr_of='p23250',  # long-term capital gains
                                    liability_type='iitax')

    # Calculate proportional change (pch) in marginal net-of-tax rates
    wage_pch = ((1. - wage_mtr_y) - (1. - wage_mtr_x)) / (1. - wage_mtr_x)
    ltcg_pch = ((1. - ltcg_mtr_y) - (1. - ltcg_mtr_x)) / (1. - ltcg_mtr_x)

    # Calculate magnitude of substitution and income effects and their sum
    substitution_effect = (calc_y.behavior.BE_sub * wage_pch *
                           calc_x.records.c04800)  # c04800 is taxable income
    # pylint: disable=protected-access
    income_effect = (calc_y.behavior.BE_inc *
                     (calc_y.records._combined -
                      calc_x.records._combined))  # _combined is INC+FICA taxes
    combined_behavioral_effect = income_effect + substitution_effect

    # Calculate magnitude of behavioral response in long-term capital gains
    cap_gain_behavioral_effect = (calc_y.behavior.BE_cg * ltcg_pch *
                                  calc_x.records.p23250)  # p23250 is ltcg

    # Add the behavior changes to income sources
    calc_y_behavior = copy.deepcopy(calc_y)
    calc_y_behavior = update_ordinary_income(combined_behavioral_effect,
                                             calc_y_behavior)
    calc_y_behavior = update_cap_gain_income(cap_gain_behavioral_effect,
                                             calc_y_behavior)

    # Recalculate post-reform taxes taking behavioral responses into account
    calc_y_behavior.calc_all()
    return calc_y_behavior


def mtr_xy(calc_x, calc_y, mtr_of, liability_type):
    """
    Compute marginal tax rates for plan X and plan Y for
    specified mtr_of income type and liability_type.
    """
    payroll_x, iitax_x, combined_x = calc_x.mtr(mtr_of)
    payroll_y, iitax_y, combined_y = calc_y.mtr(mtr_of)
    if liability_type == 'combined':
        return (combined_x, combined_y)
    elif liability_type == 'payroll':
        return (payroll_x, payroll_y)
    elif liability_type == 'iitax':
        return (iitax_x, iitax_y)
    else:
        raise ValueError('Choose from combined, iitax, and payroll.')


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
        if behavior_dict:
            if not isinstance(behavior_dict, dict):
                raise ValueError('behavior_dict is not a dictionary')
            self._vals = behavior_dict
        elif behavior_dict is None:
            self._vals = self._params_dict_from_json_file()
        else:
            raise ValueError('illegal value of behavior_dict in Behavior ctor')
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
