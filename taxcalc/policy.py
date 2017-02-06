"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 policy.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy policy.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import re
from .parameters import ParametersBase


class Policy(ParametersBase):

    """
    Constructor for the federal tax policy class.

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

    wage_growth_rates: dictionary of YEAR:RATE pairs
        variable wage growth rates used to project future policy parameter
        values; if None, default wage growth rates (specified below) are used.

    Raises
    ------
    ValueError:
        if parameter_dict is neither None nor a dictionary.
        if num_years is less than one.
        if inflation_rates is neither None nor a dictionary.
        if len(inflation_rates) is not equal to num_years.
        if min(inflation_rates.keys()) is not equal to start_year.
        if wage_growth_rates is neither None nor a dictionary.
        if len(wage_growth_rates) is not equal to num_years.
        if min(wage_growth_rates.keys()) is not equal to start_year.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILENAME = 'current_law_policy.json'
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    LAST_BUDGET_YEAR = 2026  # increases by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    # default price inflation rates by year
    __pirates = {2013: 0.0148, 2014: 0.0211, 2015: 0.0183, 2016: 0.0228,
                 2017: 0.0222, 2018: 0.0229, 2019: 0.0233, 2020: 0.0233,
                 2021: 0.0232, 2022: 0.0233, 2023: 0.0233, 2024: 0.0234,
                 2025: 0.0235, 2026: 0.0235}

    # default wage growth rates by year
    __wgrates = {2013: 0.0199, 2014: 0.0401, 2015: 0.0395, 2016: 0.0388,
                 2017: 0.0352, 2018: 0.0324, 2019: 0.0281, 2020: 0.0281,
                 2021: 0.0306, 2022: 0.0315, 2023: 0.0317, 2024: 0.0317,
                 2025: 0.0319, 2026: 0.0319}

    VALID_PARAM_CODE_NAMES = set(['ALD_InvInc_ec_base_code',
                                  'CTC_new_code'])

    PROHIBIT_PARAM_CODE = False

    @staticmethod
    def default_inflation_rates():
        """
        Return complete default price inflation rate dictionary.

        Parameters
        ----------
        none

        Returns
        -------
        default inflation rates: dict
            decimal (not percentage) annual inflation rate by calendar year.
        """
        return Policy.__pirates

    @staticmethod
    def default_wage_growth_rates():
        """
        Return complete default wage growth rate dictionary.

        Parameters
        ----------
        none

        Returns
        -------
        default growth rates: dict
            decimal (not percentage) annual growth rate by calyear.
        """
        return Policy.__wgrates

    def __init__(self, parameter_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=None,
                 wage_growth_rates=None):
        """
        Policy class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-branches
        super(Policy, self).__init__()
        if parameter_dict is None:  # read default parameters
            self._vals = self._params_dict_from_json_file()
        elif isinstance(parameter_dict, dict):
            self._vals = parameter_dict
        else:
            raise ValueError('parameter_dict is not None or a dictionary')

        if num_years < 1:
            raise ValueError('num_years cannot be less than one')

        if inflation_rates is None:  # read default rates
            self._inflation_rates = [Policy.__pirates[start_year + i]
                                     for i in range(0, num_years)]
        elif isinstance(inflation_rates, dict):
            if len(inflation_rates) != num_years:
                raise ValueError('len(inflation_rates) != num_years')
            if min(list(inflation_rates.keys())) != start_year:
                msg = 'min(inflation_rates.keys()) != start_year'
                raise ValueError(msg)
            self._inflation_rates = [inflation_rates[start_year + i]
                                     for i in range(0, num_years)]
        else:
            raise ValueError('inflation_rates is not None or a dictionary')

        cpi = 1.0
        self._inflation_index = [cpi]
        for idx in range(0, num_years):
            cpi *= (1.0 + self._inflation_rates[idx])
            self._inflation_index.append(cpi)

        if wage_growth_rates is None:  # read default rates
            self._wage_growth_rates = [Policy.__wgrates[start_year + i]
                                       for i in range(0, num_years)]
        elif isinstance(wage_growth_rates, dict):
            if len(wage_growth_rates) != num_years:
                raise ValueError('len(wage_growth_rates) != num_years')
            if min(list(wage_growth_rates.keys())) != start_year:
                msg = 'min(wage_growth_rates.keys()) != start_year'
                raise ValueError(msg)
            self._wage_growth_rates = [wage_growth_rates[start_year + i]
                                       for i in range(0, num_years)]
        else:
            raise ValueError('wage_growth_rates is not None or a dictionary')

        self.param_code = dict()
        for param in Policy.VALID_PARAM_CODE_NAMES:
            self.param_code[param] = ''

        self.initialize(start_year, num_years)

    def inflation_rates(self):
        """
        Returns list of price inflation rates starting with JSON_START_YEAR.
        """
        return self._inflation_rates

    def wage_growth_rates(self):
        """
        Returns list of wage growth rates starting with JSON_START_YEAR.
        """
        return self._wage_growth_rates

    def implement_reform(self, reform):
        """
        Implement multi-year policy reform and leave current_year unchanged.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.

        Returns
        -------
        nothing: void

        Notes
        -----
        Given a reform dictionary, typical usage of the Policy class
        is as follows::

            policy = Policy()
            policy.implement_reform(reform)

        In the above statements, the Policy() call instantiates a
        policy object (policy) containing current-law policy parameters,
        and the implement_reform(reform) call applies the (possibly
        multi-year) reform specified in reform and then sets the
        current_year to the value of current_year when implement_reform
        was called with parameters set for that pre-call year.

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

        IMPORTANT NOTICE: when specifying a reform dictionary always group
        all reform provisions for a specified year into one YEAR:MODS pair.
        If you make the mistake of specifying two or more YEAR:MODS pairs
        with the same YEAR value, all but the last one will be overwritten,
        and therefore, not part of the reform.  This is because Python
        expects unique (not multiple) dictionary keys.  There is no way to
        catch this error, so be careful to specify reform dictionaries
        correctly.
        """
        # check that all reform dictionary keys are integers
        if not isinstance(reform, dict):
            raise ValueError('reform is not a dictionary')
        if len(reform) == 0:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'key={} in reform is not an integer calendar year'
                raise ValueError(msg.format(year))
        # remove and process param_code information
        zero = 0  # param_code information is marked with year equal to 0
        param_code_dict = reform.pop(zero, None)
        if param_code_dict:
            reform_years.remove(zero)
            for param, code in param_code_dict.items():
                Policy.scan_param_code(code)
                self.param_code[param] = code
        # check range of remaining reform_years
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'reform provision in year={} < start_year={}'
            raise ValueError(msg.format(first_reform_year, self.start_year))
        if first_reform_year < self.current_year:
            msg = 'reform provision in year={} < current_year={}'
            raise ValueError(msg.format(first_reform_year, self.current_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'reform provision in year={} > end_year={}'
            raise ValueError(msg.format(last_reform_year, self.end_year))
        # implement the reform year by year
        precall_current_year = self.current_year
        for year in reform_years:
            self.set_year(year)
            self._update({year: reform[year]})
        self.set_year(precall_current_year)

    @staticmethod
    def scan_param_code(code):
        """
        Raise ValueError if certain character strings found in specified code.
        """
        if re.search(r'__', code) is not None:
            msg = 'Following param_code includes illegal "__":\n'
            msg += code
            raise ValueError(msg)
        if re.search(r'lambda', code) is not None:
            msg = 'Following param_code includes illegal "lambda":\n'
            msg += code
            raise ValueError(msg)
        if re.search(r'\[', code) is not None:
            msg = 'Following param_code includes illegal "[":\n'
            msg += code
            raise ValueError(msg)
        if re.search(r'\*\*', code) is not None:
            msg = 'Following param_code includes illegal "**":\n'
            msg += code
            raise ValueError(msg)

    def cpi_for_param_code(self, param_code_name):
        """
        Return inflation index for current_year that has a base value
        of one in the first year the named param_code is active.

        Note that a ValueError is raised if the specified
        param_code_name is not a valid parameter code name or
        if the specified parameter code is not active in the range of
        years from Policy.JSON_START_YEAR through Policy.LAST_BUDGET_YEAR.
        """
        if param_code_name not in Policy.VALID_PARAM_CODE_NAMES:
            msg = '{} is not in Policy.VALID_PARAM_CODE_NAMES'
            raise ValueError(msg.format(param_code_name))
        active_name = '_{}_active'.format(param_code_name)
        active_param = getattr(self, active_name, None)
        zero_year = Policy.JSON_START_YEAR
        first_active_year = 9999
        for idx in range(0, len(active_param)):
            if active_param[idx]:
                first_active_year = idx + zero_year
                break
        if self.current_year < first_active_year:
            msg = 'current_year={} < {} first active year {}'
            raise ValueError(msg.format(self.current_year,
                                        param_code_name, first_active_year))
        cpi_current_year = self._inflation_index[self.current_year - zero_year]
        cpi_active_year = self._inflation_index[first_active_year - zero_year]
        cpi_rebased = cpi_current_year / cpi_active_year
        return cpi_rebased

    def current_law_version(self):
        """
        Return Policy object same as self except with current-law policy.
        """
        startyear = self.start_year
        numyears = self.num_years
        year_list = [startyear + i for i in range(0, numyears)]
        irate_dict = dict(zip(year_list, self._inflation_rates))
        wrate_dict = dict(zip(year_list, self._wage_growth_rates))
        clv = Policy(parameter_dict=None,
                     start_year=startyear,
                     num_years=numyears,
                     inflation_rates=irate_dict,
                     wage_growth_rates=wrate_dict)
        clv.set_year(self.current_year)
        return clv
