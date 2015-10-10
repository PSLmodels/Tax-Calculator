"""
OSPC Tax-Calculator federal tax policy Parameters class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 parameters.py
# pylint --disable=locally-disabled parameters.py

from .utils import expand_array
import os
import json


class Parameters(object):
    """
    Constructor for the federal tax policy parameters class.

    Parameters
    ----------
    parameter_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of policy parameters; if None, default policy
        parameters are read from the params.json file.

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
    class instance: Parameters
    """

    PARAMS_FILENAME = 'params.json'
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
        return Parameters.__rates

    def __init__(self, parameter_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None):
        """
        Parameters class constructor.
        """
        if parameter_dict:
            if not isinstance(parameter_dict, dict):
                raise ValueError('parameter_dict is not a dictionary')
            self._vals = parameter_dict
        else:  # if None, read current-law parameters
            self._vals = self._params_dict_from_json_file()

        if parameter_dict is None and start_year < Parameters.JSON_START_YEAR:
            msg = 'start_year={} < JSON_START_YEAR={}'
            raise ValueError(msg.format(start_year,
                                        Parameters.JSON_START_YEAR))

        if num_years < 1:
            raise ValueError('num_years < 1')

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

        self._current_year = start_year
        self._start_year = start_year
        self._num_years = num_years
        self._end_year = start_year + num_years - 1

        # extend current-law parameter values into future with _inflation_rates
        for name, data in self._vals.items():
            cpi_inflated = data.get('cpi_inflated', False)
            values = data['value']
            setattr(self, name,
                    expand_array(values, inflate=cpi_inflated,
                                 inflation_rates=self._inflation_rates,
                                 num_years=self._num_years))
        self.set_year(self._start_year)

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
        Given a reform dictionary, typical usage of the Parameters class
        is as follows::

            ppo = Parameters()
            ppo.implement_reform(reform)

        In the above statements, the Parameters() call instantiates a
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

    @property
    def current_year(self):
        """
        Current policy parameter year property.
        """
        return self._current_year

    @property
    def start_year(self):
        """
        First policy parameter year property.
        """
        return self._start_year

    @property
    def num_years(self):
        """
        Number of policy parameter years property.
        """
        return self._num_years

    @property
    def end_year(self):
        """
        Last policy parameter year property.
        """
        return self._end_year

    def set_year(self, year):
        """
        Set policy parameters to values for specified calendar year.

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

            ppo.set_year(ppo.current_year + 1)

        where ppo is a policy Parameters object.
        """
        if year < self.start_year or year > self.end_year:
            msg = 'year passed to set_year() must be in [{},{}] range.'
            raise ValueError(msg.format(self.start_year, self.end_year))
        self._current_year = year
        year_zero_indexed = year - self._start_year
        for name in self._vals:
            arr = getattr(self, name)
            setattr(self, name[1:], arr[year_zero_indexed])

    @staticmethod
    def default_data(metadata=False, start_year=None):
        """
        Return current-law policy data read from params.json file.

        Parameters
        ----------
        metadata: boolean

        start_year: int

        Returns
        -------
        params: dictionary of params.json data
        """
        # extract different data from params.json depending on start_year
        if start_year:  # if start_year is not None
            nyrs = start_year - Parameters.JSON_START_YEAR + 1
            ppo = Parameters(num_years=nyrs)
            ppo.set_year(start_year)
            parms = getattr(ppo, '_vals')
            params = Parameters._revised_default_data(parms, start_year,
                                                      nyrs, ppo)
        else:  # if start_year is None
            params = Parameters._params_dict_from_json_file()
        # return different data from params dict depending on metadata value
        if metadata:
            return params
        else:
            return {name: data['value'] for name, data in params.items()}

    # ----- begin private methods of Parameters class -----

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

        ppo: Parameters object
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

    def params_to_json(self):
        return json.dumps(self._vals)

    @staticmethod
    def _params_dict_from_json_file():
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
        params_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   Parameters.PARAMS_FILENAME)
        if os.path.exists(params_path):
            with open(params_path) as pfile:
                params = json.load(pfile)
        else:
            from pkg_resources import resource_stream, Requirement
            path_in_egg = os.path.join('taxcalc', Parameters.PARAMS_FILENAME)
            buf = resource_stream(Requirement.parse('taxcalc'), path_in_egg)
            as_bytes = buf.read()
            as_string = as_bytes.decode("utf-8")
            params = json.loads(as_string)
        return params

    def _update(self, year_mods):
        """Private method used **only** by the public implement_reform method.

        Parameters
        ----------
        year_mods: dictionary containing a single YEAR:MODS pair
            see Notes below for details on dictionary structure.

        Raises
        ------
        ValueError:
            if year_mods is not a dictionary of the expected structure.

        Returns
        -------
        nothing: void

        Notes
        -----
        This is a private method that should **never** be used by clients
        of the Parameters class.  Instead, always use the public
        implement_reform method.  This is a private method that helps
        the public implement_reform method do its job.

        This private method implements a policy reform, the provisions of
        which are specified in the year_mods dictionary, that changes
        the values of some policy parameters in this Parameters
        object.  This year_mods dictionary contains exactly one
        YEAR:MODS pair, where the integer YEAR key indicates the
        calendar year for which the reform provisions in the MODS
        dictionary are implemented.  The MODS dictionary contains
        PARAM:VALUE pairs in which the PARAM is a string specifying
        the policy parameter (as used in the params.json default
        parameter file) and the VALUE is a Python list of post-reform
        values for that PARAM in that YEAR.  Beginning in the year
        following the implementation of a reform provision, the
        parameter whose value has been changed by the reform continues
        to be inflation indexed or not be inflation indexed according
        to that parameter's cpi_inflated value in the params.json
        file.  But a reform can change the indexing status of a
        parameter by including in the MODS dictionary a term that is a
        PARAM_cpi:BOOLEAN pair specifying the post-reform indexing
        status of the parameter.

        So, for example, to raise the OASDI (i.e., Old-Age, Survivors,
        and Disability Insurance) maximum taxable earnings beginning
        in 2018 to $500,000 and to continue indexing it in subsequent
        years as in current-law policy, the YEAR:MODS dictionary would
        be as follows::

            {2018: {"_SS_Earnings_c":[500000]}}

        But to raise the maximum taxable earnings in 2018 to $500,000
        without any indexing in subsequent years, the YEAR:MODS
        dictionary would be as follows::

            {2018: {"_SS_Earnings_c":[500000], "_SS_Earnings_c_cpi":False}}

        And to raise in 2019 the starting AGI for EITC phaseout for
        married filing jointly filing status (which is a two-dimensional
        policy parameter that varies by the number of children from zero
        to three or more and is inflation indexed), the YEAR:MODS dictionary
        would be as follows::

            {2019: {"_EITC_ps_MarriedJ":[[8000, 8500, 9000, 9500]]}}

        Notice the pair of double square brackets around the four values
        for 2019.  The one-dimensional parameters above require only a pair
        of single square brackets.
        """
        # check YEAR value in the single YEAR:MODS dictionary parameter
        if not isinstance(year_mods, dict):
            msg = 'year_mods is not a dictionary'
            raise ValueError(msg)
        if len(year_mods.keys()) != 1:
            msg = 'year_mods dictionary must contain a single YEAR:MODS pair'
            raise ValueError(msg)
        year = list(year_mods.keys())[0]
        if year != self.current_year:
            msg = 'YEAR={} in year_mods is not equal to current_year={}'
            raise ValueError(msg.format(year, self.current_year))

        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.num_years) - year
        inf_rates = [self._inflation_rates[(year - self.start_year) + i]
                     for i in range(0, num_years_to_expand)]
        paramvals = self._vals
        for name, values in year_mods[year].items():
            # determine inflation indexing status of parameter with name
            if name.endswith('_cpi'):
                continue
            if name in paramvals:
                default_cpi = paramvals[name].get('cpi_inflated', False)
            else:
                default_cpi = False
            cpi_inflated = year_mods[year].get(name + '_cpi', default_cpi)
            # set post-reform values of parameter with name
            cval = getattr(self, name, None)
            if cval is None:
                # it is a behavior parameter instead
                continue
            nval = expand_array(values,
                                inflate=cpi_inflated,
                                inflation_rates=inf_rates,
                                num_years=num_years_to_expand)
            cval[(self.current_year - self.start_year):] = nval
        self.set_year(self._current_year)

# end Parameters class
