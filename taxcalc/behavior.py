import copy
import numpy as np
from .policy import Policy
from .parameters_base import ParametersBase


def update_income(behavioral_effect, calc_y):
    delta_inc = np.where(calc_y.records.c00100 > 0, behavioral_effect, 0)

    # Attribute the behavioral effects across itemized deductions,
    # wages, and other income.

    _itemized = np.where(calc_y.records.c04470 < calc_y.records._standard,
                         0,
                         calc_y.records.c04470)

    delta_wages = np.where(calc_y.records.c00100 + _itemized > 0,
                           (delta_inc * calc_y.records.e00200 /
                            (calc_y.records.c00100 + _itemized)),
                           0)

    other_inc = calc_y.records.c00100 - calc_y.records.e00200

    delta_other_inc = np.where(calc_y.records.c00100 + _itemized > 0,
                               (delta_inc * other_inc /
                                (calc_y.records.c00100 + _itemized)),
                               0)

    delta_itemized = np.where(calc_y.records.c00100 + _itemized > 0,
                              (delta_inc * _itemized /
                               (calc_y.records.c00100 + _itemized)),
                              0)

    calc_y.records.e00200 = calc_y.records.e00200 + delta_wages

    calc_y.records.e00300 = calc_y.records.e00300 + delta_other_inc

    calc_y.records.e19570 = np.where(_itemized > 0,
                                     calc_y.records.e19570 + delta_itemized, 0)
    # TODO, we should create a behavioral modification
    # variable instead of using e19570

    calc_y.calc_all()

    return calc_y


def behavior(calc_x, calc_y, update_income=update_income):
    """
    Modify plan Y records to account for micro-feedback effect that arrise
    from moving from plan X to plan Y.
    """

    # Calculate marginal tax rates for plan x and plan y.
    _, _, combined_mtr_x = calc_x.mtr()
    mtr_x = combined_mtr_x

    _, _, combined_mtr_y = calc_y.mtr()
    mtr_y = combined_mtr_y

    # Calculate the percent change in after-tax rate.
    pct_diff_atr = ((1 - mtr_y) - (1 - mtr_x)) / (1 - mtr_x)

    # Calculate the magnitude of the substitution and income effects.
    substitution_effect = (calc_y.behavior.BE_sub * pct_diff_atr *
                           (calc_x.records.c04800))

    income_effect = calc_y.behavior.BE_inc * (calc_y.records._combined -
                                              calc_x.records._combined)
    calc_y_behavior = copy.deepcopy(calc_y)

    combined_behavioral_effect = income_effect + substitution_effect

    calc_y_behavior = update_income(combined_behavioral_effect,
                                    calc_y_behavior)

    return calc_y_behavior


class Behavior(ParametersBase):

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'behavior.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self, behavior_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None):
        if behavior_dict:
            if not isinstance(behavior_dict, dict):
                raise ValueError('behavior_dict is not a dictionary')
            self._vals = behavior_dict
        else:  # if None, read defaults
            self._vals = self._params_dict_from_json_file()
        if inflation_rates is not None:
            raise ValueError('inflation_rates != None in Behavior.__init__')
        self.initialize(start_year, num_years)

    def update_behavior(self, revisions):
        """
        Update behavior for given revisions, a dictionary consisting
        of year:modification dictionaries.
        For example: {2014: {'_BE_inc': [0.4, 0.3]}}
        """
        self.set_default_vals()
        if self.current_year != self.start_year:
            self.set_year(self.start_year)
        for year in revisions:
            if year != self.start_year:
                self.set_year(year)
            self._update({year: revisions[year]})
