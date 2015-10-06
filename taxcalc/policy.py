"""
OSPC Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 parameters.py
# pylint --disable=locally-disabled parameters.py


import os
import json
from .utils import expand_array
from .parameters_base import ParametersBase


class Policy(ParametersBase):

    """
    Constructor for the federal tax policy parameters class.

    Parameters
    ----------
    parameter_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of policy parameters; if None, default policy
        parameters are read from the current_law_policy.json file.

    start_year: integer
        first calendar year for historical policy parameters.

    num_years: integer
        number of calendar years for which to specify policy parameter
        values beginning with start_year.

    inflation_rates: dictionary of YEAR:RATE pairs
        variable inflation rates used to project future policy parameter
        values; if None, default inflation rates (specified below) are used.

    Raises
    ------
    ValueError:
        if parameter_dict is neither None nor a dictionary.
        if num_years is less than one.
        if len(inflation_rates) is not equal to num_years.
        if min(inflation_rates.keys()) is not equal to start_year.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILENAME = 'current_law_policy.json'
    IRATES_FILENAME = 'irates.json'  # TODO: move __rates there & add wages
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    FIRST_BUDGET_YEAR = 2015  # increases by one every calendar year
    NUM_BUDGET_YEARS = 10  # fixed by federal government budgeting rules
    DEFAULT_NUM_YEARS = NUM_BUDGET_YEARS + FIRST_BUDGET_YEAR - JSON_START_YEAR

    # default inflation rates by year
    __rates = {2013: 0.015, 2014: 0.020, 2015: 0.022, 2016: 0.020, 2017: 0.021,
               2018: 0.022, 2019: 0.023, 2020: 0.024, 2021: 0.024, 2022: 0.024,
               2023: 0.024, 2024: 0.024}

    @staticmethod
    def default_inflation_rates():
        """
        Return complete default inflation rate dictionary.

        Parameters
        ----------
        none

        Returns
        -------
        default inflation rates: dict
            decimal (not percentage) annual inflation rate by calyear.
        """
        return Policy.__rates

    def __init__(self, parameter_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None):
        """
        Policy class constructor.
        """
        if parameter_dict:
            if not isinstance(parameter_dict, dict):
                raise ValueError('parameter_dict is not a dictionary')
            self._vals = parameter_dict
        else:  # if None, read current-law parameters
            self._vals = self._params_dict_from_json_file()

        if parameter_dict is None and start_year < Policy.JSON_START_YEAR:
            msg = 'start_year={} < JSON_START_YEAR={}'
            raise ValueError(msg.format(start_year,
                                        Policy.JSON_START_YEAR))

        if inflation_rates:
            if len(inflation_rates) != num_years:
                raise ValueError('len(inflation_rates) != num_years')
            if min(list(inflation_rates.keys())) != start_year:
                raise ValueError('min(inflation_rates.keys()) != start_year')
            self._inflation_rates = [inflation_rates[start_year + i]
                                     for i in range(0, num_years)]
        else:  # if None, read default rates
            self._inflation_rates = [self.__rates[start_year + i]
                                     for i in range(0, num_years)]
        self.initialize(start_year, num_years)

    def implement_reform(self, reform):
        """
        Implement multi-year parameters reform and set current_year=start_year.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to _update function for details on MODS structure.

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.

        Returns
        -------
        nothing: void

        Notes
        -----
        Given a reform dictionary, typical usage of the Policy class
        is as follows::

            ppo = Policy()
            ppo.implement_reform(reform)

        In the above statements, the Policy() call instantiates a
        policy parameters object (ppo) containing current-law policy
        parameters, and the implement_reform(reform) call applies the
        (possibly multi-year) reform specified in reform and then sets
        the current_year to start_year with parameters set for that year.

        An example of a multi-year, multi-parameter reform is as follows::

            reform = {
                2015: {
                    '_AMT_thd_MarriedS': [60000]
                },
                2016: {
                    '_EITC_c': [[900, 5000, 8000, 9000]],
                    '_II_em': [7000],
                    '_SS_Earnings_c': [300000]
                },
                2017: {
                    '_AMT_thd_MarriedS': [80000],
                    '_SS_Earnings_c': [500000], '_SS_Earnings_c_cpi': False
                },
                2019: {
                    '_EITC_c': [[1200, 7000, 10000, 12000]],
                    '_II_em': [9000],
                    '_SS_Earnings_c': [700000], '_SS_Earnings_c_cpi': True
                }
            }

        Notice that each of the four YEAR:MODS pairs is specified as
        required by the private _update method, whose documentation
        provides several MODS dictionary examples.
        """
        if self.current_year != self.start_year:
            self.set_year(self.start_year)
        if not isinstance(reform, dict):
            msg = 'reform passed to implement_reform is not a dictionary'
            ValueError(msg)
        if not reform:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'key={} in reform is not an integer calendar year'
                raise ValueError(msg.format(year))
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'reform provision in year={} < start_year={}'
            ValueError(msg.format(first_reform_year, self.start_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'reform provision in year={} > end_year={}'
            ValueError(msg.format(last_reform_year, self.end_year))
        for year in reform_years:
            if year != self.start_year:
                self.set_year(year)
            self._update({year: reform[year]})
        self.set_year(self.start_year)

    @staticmethod
    def default_data(metadata=False, start_year=None):
        """
        Return current-law policy data read from current_law_policy.json file.

        Parameters
        ----------
        metadata: boolean

        start_year: int

        Returns
        -------
        params: dictionary of current_law_policy.json data
        """
        # extract different data from current_law_policy.json depending on
        # start_year
        if start_year:  # if start_year is not None
            nyrs = start_year - Policy.JSON_START_YEAR + 1
            ppo = Policy(num_years=nyrs)
            ppo.set_year(start_year)
            parms = getattr(ppo, '_vals')
            params = Policy._revised_default_data(parms, start_year,
                                                      nyrs, ppo)
        else:  # if start_year is None
            params = Policy._params_dict_from_json_file()
        # return different data from params dict depending on metadata value
        if metadata:
            return params
        else:
            return {name: data['value'] for name, data in params.items()}

    # ----- begin private methods of Policy class -----

    @staticmethod
    def _revised_default_data(params, start_year, nyrs, ppo):
        """
        Return revised default parameter data.

        Parameters
        ----------
        params: dictionary of NAME:DATA pairs for each parameter
            as defined in calling default_data staticmethod.

        start_year: int
            as defined in calling default_data staticmethod.

        nyrs: int
            as defined in calling default_data staticmethod.

        ppo: Policy object
            as defined in calling default_data staticmethod.

        Returns
        -------
        params: dictionary of revised parameter data

        Notes
        -----
        This staticmethod is called from default_data staticmethod in
        order to reduce the complexity of the default_data staticmethod.
        """
        import numpy.core as np
        start_year_str = '{}'.format(start_year)
        for name, data in params.items():
            data['start_year'] = start_year
            values = data['value']
            num_values = len(values)
            if num_values <= nyrs:
                # val should be the single start_year value
                rawval = getattr(ppo, name[1:])
                if isinstance(rawval, np.ndarray):
                    val = rawval.tolist()
                else:
                    val = rawval
                data['value'] = [val]
                data['row_label'] = [start_year_str]
            else:  # if num_values > nyrs
                # val should extend beyond the start_year value
                data['value'] = data['value'][(nyrs - 1):]
                data['row_label'] = data['row_label'][(nyrs - 1):]
        return params
