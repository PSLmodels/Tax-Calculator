"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

import os
import collections
import numpy as np
from taxcalc.parameters import Parameters
from taxcalc.growfactors import GrowFactors


class Policy(Parameters):
    """
    Policy is a subclass of the abstract Parameters class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for the federal tax policy class.

    Parameters
    ----------
    gfactors: GrowFactors class instance
        containing price inflation rates and wage growth rates

    Raises
    ------
    ValueError:
        if gfactors is not a GrowFactors class instance or None.

    Returns
    -------
    class instance: Policy
    """

    DEFAULTS_FILE_NAME = 'policy_current_law.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
    JSON_START_YEAR = 2013  # remains the same unless earlier data added
    LAST_KNOWN_YEAR = 2018  # last year for which indexed param vals are known
    # should increase LAST_KNOWN_YEAR by one every calendar year
    LAST_BUDGET_YEAR = 2029  # last extrapolation year
    # should increase LAST_BUDGET_YEAR by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    # NOTE: the following three data structures use internal parameter names:
    # (1) specify which Policy parameters are wage (rather than price) indexed
    WAGE_INDEXED_PARAMS = [
        '_SS_Earnings_c',
        '_SS_Earnings_thd'
    ]
    # (2) specify which Policy parameters have been removed
    REMOVED_PARAMS = [
        # following five parameters removed in PR 2223 merged on 2019-02-06
        '_DependentCredit_Child_c',
        '_DependentCredit_Nonchild_c',
        '_DependentCredit_before_CTC',
        '_FilerCredit_c',
        '_ALD_InvInc_ec_base_RyanBrady'
    ]
    # (3) specify which Policy parameters havve been redefined recently
    REDEFINED_PARAMS = {
        # TODO: remove the CTC_c name:message pair sometime later in 2019
        '_CTC_c': 'CTC_c was redefined in release 1.0.0 (2019-02-22)'
    }

    def __init__(self, gfactors=None, only_reading_defaults=False):
        # put JSON contents of DEFAULTS_FILE_NAME into self._vals dictionary
        super().__init__()
        if only_reading_defaults:
            return
        # handle gfactors argument
        if gfactors is None:
            self._gfactors = GrowFactors()
        elif isinstance(gfactors, GrowFactors):
            self._gfactors = gfactors
        else:
            raise ValueError('gfactors is not None or a GrowFactors instance')
        # read default parameters and initialize
        syr = Policy.JSON_START_YEAR
        lyr = Policy.LAST_BUDGET_YEAR
        nyrs = Policy.DEFAULT_NUM_YEARS
        self._inflation_rates = self._gfactors.price_inflation_rates(syr, lyr)
        self._apply_clp_cpi_offset(self._vals['_cpi_offset'], nyrs)
        self._wage_growth_rates = self._gfactors.wage_growth_rates(syr, lyr)
        self.initialize(syr, nyrs, Policy.WAGE_INDEXED_PARAMS)
        # initialize parameter warning/error variables
        self.parameter_warnings = ''
        self.parameter_errors = ''

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

    def implement_reform(self, reform,
                         print_warnings=True, raise_errors=True):
        """
        Implement multi-year policy reform and leave current_year unchanged.

        Parameters
        ----------
        reform: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        print_warnings: boolean
            if True, prints warnings when parameter_warnings exists;
            if False, does not print warnings when parameter_warnings exists
                    and leaves warning handling to caller of implement_reform.

        raise_errors: boolean
            if True, raises ValueError when parameter_errors exists;
            if False, does not raise ValueError when parameter_errors exists
                    and leaves error handling to caller of implement_reform.

        Raises
        ------
        ValueError:
            if reform is not a dictionary.
            if each YEAR in reform is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.
            if raise_errors is True AND
              _validate_names_types generates errors OR
              _validate_values generates errors.

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

        An example of a multi-year, multi-parameter reform is as follows:

            reform = {
                2016: {
                    'EITC_c': [900, 5000, 8000, 9000],
                    'II_em': 7000,
                    'SS_Earnings_c': 300000
                },
                2017: {
                    'SS_Earnings_c': 500000, 'SS_Earnings_c-indexed': False
                },
                2019: {
                    'EITC_c': [1200, 7000, 10000, 12000],
                    'II_em': 9000,
                    'SS_Earnings_c': 700000, 'SS_Earnings_c-indexed': True
                }
            }

        IMPORTANT NOTICE: when specifying a reform dictionary always group
        all reform provisions for a specified year into one YEAR:MODS pair.
        If you make the mistake of specifying two or more YEAR:MODS pairs
        with the same YEAR value, all but the last one will be overwritten,
        and therefore, not part of the reform.  This is because Python
        expects unique (not multiple) dictionary keys.  There is no way to
        catch this error, so be careful to specify reform dictionaries
        correctly.
        """
        # pylint: disable=too-many-locals
        # check that all reform dictionary keys are integers
        if not isinstance(reform, dict):
            raise ValueError('ERROR: YYYY PARAM reform is not a dictionary')
        if not reform:
            return  # no reform to implement
        reform_years = sorted(list(reform.keys()))
        for year in reform_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in reform is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining reform_years
        first_reform_year = min(reform_years)
        if first_reform_year < self.start_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_reform_year, self.start_year))
        if first_reform_year < self.current_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR < current_year={}'
            raise ValueError(msg.format(first_reform_year, self.current_year))
        last_reform_year = max(reform_years)
        if last_reform_year > self.end_year:
            msg = 'ERROR: {} YEAR reform provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_reform_year, self.end_year))
        # add leading underscore character to each parameter name in reform
        reform = Parameters._add_underscores(reform)
        # add brackets around each data element in reform
        reform = Parameters._add_brackets(reform)
        # validate reform parameter names and types
        self.parameter_warnings = ''
        self.parameter_errors = ''
        self._validate_names_types(reform,
                                   removed_names=Policy.REMOVED_PARAMS)
        if self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # optionally apply cpi_offset to inflation_rates and re-initialize
        if Policy._cpi_offset_in_reform(reform):
            known_years = self._apply_reform_cpi_offset(reform)
            self._set_default_vals(
                wage_indexed_params=Policy.WAGE_INDEXED_PARAMS,
                known_years=known_years
            )
        # implement the reform year by year
        precall_current_year = self.current_year
        reform_parameters = set()
        for year in reform_years:
            self.set_year(year)
            reform_parameters.update(reform[year].keys())
            self._update({year: reform[year]}, Policy.WAGE_INDEXED_PARAMS)
        self.set_year(precall_current_year)
        # validate reform parameter values
        self._validate_values(reform_parameters,
                              redefined_info=Policy.REDEFINED_PARAMS)
        if self.parameter_warnings and print_warnings:
            print(self.parameter_warnings)
        if self.parameter_errors and raise_errors:
            raise ValueError('\n' + self.parameter_errors)

    def metadata(self):
        """
        Returns ordered dictionary of parameter information based on
        the contents of the policy_current_law.json file with updates
        to each parameter's 'start_year', 'row_label', and 'value' key
        values so that the updated values contain just the current_year
        information for this instance of the Policy class.
        """
        mdata = collections.OrderedDict()
        for pname, pdata in self._vals.items():
            name = pname[1:]
            mdata[name] = pdata
            mdata[name]['row_label'] = ['{}'.format(self.current_year)]
            mdata[name]['start_year'] = '{}'.format(self.current_year)
            valraw = getattr(self, name)
            if isinstance(valraw, np.ndarray):
                val = valraw.tolist()
            else:
                val = valraw
            mdata[name]['value'] = val
        return mdata

    @staticmethod
    def parameter_list():
        """
        Returns list of parameter names in the policy_current_law.json file.
        """
        policy = Policy(only_reading_defaults=True)
        plist = list(policy._vals.keys())  # pylint: disable=protected-access
        del policy
        return plist

    # ----- begin private methods of Policy class -----

    def _apply_clp_cpi_offset(self, cpi_offset_clp_data, num_years):
        """
        Call this method from Policy constructor
        after self._inflation_rates has been set and
        before base class initialize method is called.
        (num_years is number of years for which inflation rates are specified)
        """
        ovalues = cpi_offset_clp_data['value']
        if len(ovalues) < num_years:  # extrapolate last known value
            ovalues = ovalues + ovalues[-1:] * (num_years - len(ovalues))
        for idx in range(0, num_years):
            infrate = round(self._inflation_rates[idx] + ovalues[idx], 6)
            self._inflation_rates[idx] = infrate

    @staticmethod
    def _cpi_offset_in_reform(reform):
        """
        Return true if cpi_offset is in reform; otherwise return false.
        """
        for year in reform:
            for name in reform[year]:
                if name == '_cpi_offset':
                    return True
        return False

    def _apply_reform_cpi_offset(self, reform):
        """
        Call this method ONLY if _cpi_offset_in_reform returns True.
        Apply CPI offset to inflation rates and
        revert indexed parameter values in preparation for re-indexing.
        Also, return known_years which is dictionary with indexed policy
        parameter names as keys and known_years as values.  For indexed
        parameters included in reform, the known_years value is equal to:
        (first_cpi_offset_year - start_year + 1).  For indexed parameters
        not included in reform, the known_years value is equal to:
        (max(first_cpi_offset_year, Policy.LAST_KNOWN_YEAR) - start_year + 1).
        """
        # pylint: disable=too-many-branches
        # extrapolate cpi_offset reform
        self.set_year(self.start_year)
        first_cpi_offset_year = 0
        for year in sorted(reform.keys()):
            self.set_year(year)
            if '_cpi_offset' in reform[year]:
                if first_cpi_offset_year == 0:
                    first_cpi_offset_year = year
                oreform = {'_cpi_offset': reform[year]['_cpi_offset']}
                self._update({year: oreform}, Policy.WAGE_INDEXED_PARAMS)
        self.set_year(self.start_year)
        assert first_cpi_offset_year > 0
        # adjust inflation rates
        cpi_offset = getattr(self, '_cpi_offset')
        for idx in range(0, self.num_years):
            infrate = round(self._inflation_rates[idx] + cpi_offset[idx], 6)
            self._inflation_rates[idx] = infrate
        # revert indexed parameter values to policy_current_law.json values
        for name in self._vals.keys():
            if self._vals[name]['indexed']:
                setattr(self, name, self._vals[name]['value'])
        # construct and return known_years dictionary
        known_years = dict()
        kyrs_in_reform = (first_cpi_offset_year -
                          self.start_year + 1)
        kyrs_not_in_reform = (max(first_cpi_offset_year,
                                  Policy.LAST_KNOWN_YEAR) -
                              self.start_year + 1)
        for year in sorted(reform.keys()):
            for name in reform[year]:
                if self._vals[name]['indexed']:
                    if name not in known_years:
                        known_years[name] = kyrs_in_reform
        for name in self._vals.keys():
            if self._vals[name]['indexed']:
                if name not in known_years:
                    known_years[name] = kyrs_not_in_reform
        return known_years
