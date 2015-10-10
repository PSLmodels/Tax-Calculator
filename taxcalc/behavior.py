import copy
import json
import os
import numpy as np
from .parameters import Parameters
from .utils import expand_array


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
    mtrX = calc_x.mtr('e00200')[2]

    mtrY = calc_y.mtr('e00200')[2]

    # Calculate the percent change in after-tax rate.
    pct_diff_atr = ((1 - mtrY) - (1 - mtrX)) / (1 - mtrX)

    # Calculate the magnitude of the substitution and income effects.
    substitution_effect = (calc_y.behavior.BE_sub * pct_diff_atr *
                           (calc_x.records.c04800))

    income_effect = calc_y.behavior.BE_inc * (calc_y.records._ospctax -
                                              calc_x.records._ospctax)
    calc_y_behavior = copy.deepcopy(calc_y)

    combined_behavioral_effect = income_effect + substitution_effect

    calc_y_behavior = update_income(combined_behavioral_effect,
                                    calc_y_behavior)

    return calc_y_behavior


class Behavior(object):

    JSON_START_YEAR = Parameters.JSON_START_YEAR
    BEHAVIOR_FILENAME = 'behavior.json'
    DEFAULT_NUM_YEARS = Parameters.DEFAULT_NUM_YEARS

    def __init__(self, behavior_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None):
        if behavior_dict:
            if not isinstance(behavior_dict, dict):
                raise ValueError('behavior_dict is not a dictionary')
            self._vals = behavior_dict
        else:  # if None, read current-law parameters
            self._vals = self._behavior_dict_from_json_file()

        if num_years < 1:
            raise ValueError('num_years < 1')

        self._current_year = start_year
        self._start_year = start_year
        self._num_years = num_years
        self._end_year = start_year + num_years - 1
        self.set_default_vals()

    def set_default_vals(self):
        # extend current-law parameter values into future with _inflation_rates
        for name, data in self._vals.items():
            values = data['value']
            setattr(self, name,
                    expand_array(values, inflate=False,
                                 inflation_rates=None,
                                 num_years=self._num_years))
        self.set_year(self._start_year)

    @property
    def num_years(self):
        return self._num_years

    @property
    def current_year(self):
        return self._current_year

    @property
    def end_year(self):
        return self._end_year

    @property
    def start_year(self):
        return self._start_year

    @staticmethod
    def _behavior_dict_from_json_file():
        """
        Read params.json file and return complete params dictionary.

        Parameters
        ----------
        nothing: void

        Returns
        -------
        params: dictionary
            containing complete contents of params.json file.
        """
        behavior_path = os.path.join(os.path.abspath(
                                     os.path.dirname(__file__)),
                                     Behavior.BEHAVIOR_FILENAME)
        if os.path.exists(behavior_path):
            with open(behavior_path) as pfile:
                behavior = json.load(pfile)
        else:
            from pkg_resources import resource_stream, Requirement
            path_in_egg = os.path.join('taxcalc', Behavior.BEHAVIOR_FILENAME)
            buf = resource_stream(Requirement.parse('taxcalc'), path_in_egg)
            as_bytes = buf.read()
            as_string = as_bytes.decode("utf-8")
            behavior = json.loads(as_string)
        return behavior

    def update_behavior(self, reform):
        self.set_default_vals()
        if self.current_year != self.start_year:
            self.set_year(self.start_year)

        for year in reform:
            if year != self.start_year:
                self.set_year(year)
            num_years_to_expand = (self.start_year + self.num_years) - year
            for name, values in reform[year].items():
                # determine inflation indexing status of parameter with name
                cval = getattr(self, name, None)
                if cval is None:
                    # it is a tax law parameter not behavior
                    continue
                nval = expand_array(values,
                                    inflate=False,
                                    inflation_rates=None,
                                    num_years=num_years_to_expand)

                cval[(self.current_year - self.start_year):] = nval
        self.set_year(self.start_year)

    def set_year(self, year):
        """
        Set behavior parameters to values for specified calendar year.

        Parameters
        ----------
        year: int
            calendar year for which to current_year and parameter values

        Raises
        ------
        ValueError:
            if year is not in [start_year, end_year] range.

        Returns
        -------
        nothing: void

        Notes
        -----
        To increment the current year, use the following statement::

            behavior.set_year(behavior.current_year + 1)

        where behavior is a policy Behavior object.
        """
        if year < self.start_year or year > self.end_year:
            msg = 'year passed to set_year() must be in [{},{}] range.'
            raise ValueError(msg.format(self.start_year, self.end_year))
        self._current_year = year
        year_zero_indexed = year - self._start_year
        for name in self._vals:
            arr = getattr(self, name)
            setattr(self, name[1:], arr[year_zero_indexed])
