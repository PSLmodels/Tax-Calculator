"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 policy.py
# pylint --disable=locally-disabled policy.py

from taxcalc.parameters import ParametersBase
from taxcalc.growfactors import Growfactors


class Policy(ParametersBase):

    """
    Constructor for the federal tax policy class.

    Parameters
    ----------
    gfactors: Growfactors class instance
        containing price inflation rates and wage growth rates

    parameter_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of policy parameters; if None, default policy
        parameters are read from the current_law_policy.json file.

    start_year: integer
        first calendar year for historical policy parameters.

    num_years: integer
        number of calendar years for which to specify policy parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if gfactors is not a Growfactors class instance.
        if parameter_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILENAME = 'current_law_policy.json'
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    LAST_KNOWN_YEAR = 2017  # last year for which indexed param vals are known
    LAST_BUDGET_YEAR = 2026  # increases by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    def __init__(self,
                 gfactors=Growfactors(),
                 parameter_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        """
        Policy class constructor.
        """
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-branches
        super(Policy, self).__init__()

        if not isinstance(gfactors, Growfactors):
            raise ValueError('gfactors is not a Growfactors instance')
        self._gfactors = gfactors

        if parameter_dict is None:  # read default parameters
            self._vals = self._params_dict_from_json_file()
        elif isinstance(parameter_dict, dict):
            self._vals = parameter_dict
        else:
            raise ValueError('parameter_dict is not None or a dictionary')

        if num_years < 1:
            raise ValueError('num_years cannot be less than one')

        syr = start_year
        lyr = start_year + num_years - 1
        self._inflation_rates = gfactors.price_inflation_rates(syr, lyr)
        self._wage_growth_rates = gfactors.wage_growth_rates(syr, lyr)

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
                2016: {
                    '_EITC_c': [[900, 5000, 8000, 9000]],
                    '_II_em': [7000],
                    '_SS_Earnings_c': [300000]
                },
                2017: {
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

    def current_law_version(self):
        """
        Return Policy object same as self except with current-law policy.
        """
        startyear = self.start_year
        numyears = self.num_years
        clv = Policy(self._gfactors,
                     parameter_dict=None,
                     start_year=startyear,
                     num_years=numyears)
        clv.set_year(self.current_year)
        return clv
