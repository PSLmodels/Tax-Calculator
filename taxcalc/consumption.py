"""
Tax-Calculator Consumption class.
"""
# CODING-STYLE CHECKS:
# pycodestyle consumption.py
# pylint --disable=locally-disabled consumption.py

import os
from taxcalc.parameters import Parameters
from taxcalc.policy import Policy
from taxcalc.records import Records


class Consumption(Parameters):
    """
    Consumption is a subclass of the abstract Parameters class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for Consumption class.

    Parameters
    ----------
    last_budget_year: integer
        user-defined last parameter extrapolation year

    Returns
    -------
    class instance: Consumption
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILE_NAME = 'consumption.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, last_budget_year=Policy.LAST_BUDGET_YEAR):
        super().__init__()
        nyrs = Policy.number_of_years(last_budget_year)
        self.initialize(Consumption.JSON_START_YEAR, nyrs)

    @staticmethod
    def read_json_update(obj):
        """
        Return a revision dictionary suitable for use with update_consumption
        method derived from the specified JSON object, which can be None or
        a string containing a local filename, a URL beginning with 'http'
        pointing to a valid JSON file hosted online, or a valid JSON text.
        """
        return Parameters._read_json_revision(obj, 'consumption')

    def update_consumption(self, revision,
                           print_warnings=True, raise_errors=True):
        """
        Update consumption default values using specified revision dictionary.
        See Parameters._update for argument documentation and details about
        the expected structure of the revision dictionary.
        """
        self._update(revision, print_warnings, raise_errors)

    RESPONSE_VARS = set(['e17500', 'e18400', 'e19800', 'e20400'])
    BENEFIT_VARS = set(['housing', 'snap', 'tanf', 'vet', 'wic',
                        'mcare', 'mcaid', 'other'])

    def has_response(self):
        """
        Return true if any MPC parameters are positive for current_year or
        if any BEN value parameters are less than one for current_year;
        return false if all MPC parameters are zero and all BEN value
        parameters are one
        """
        for var in Consumption.RESPONSE_VARS:
            if getattr(self, f'MPC_{var}') > 0.0:
                return True
        for var in Consumption.BENEFIT_VARS:
            if getattr(self, f'BEN_{var}_value') < 1.0:
                return True
        return False

    def response(self, records, income_change):
        """
        Changes consumption-related records variables given income_change
        and the current values of the MPC consumption parameters
        """
        if not isinstance(records, Records):
            raise ValueError('records is not a Records object')
        for var in Consumption.RESPONSE_VARS:
            records_var = getattr(records, var)
            mpc_var = getattr(self, f'MPC_{var}')
            records_var[:] += mpc_var * income_change

    def benval_params(self):
        """
        Returns list of BEN_*_value parameter values
        """
        return [getattr(self, f'BEN_{var}_value')
                for var in Consumption.BENEFIT_VARS]

    def set_rates(self):
        """
        Consumption class has no parameter indexing rates.
        """
