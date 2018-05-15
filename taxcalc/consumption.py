"""
Tax-Calculator Consumption class.
"""
# CODING-STYLE CHECKS:
# pycodestyle consumption.py
# pylint --disable=locally-disabled consumption.py

from taxcalc.parameters import ParametersBase
from taxcalc.policy import Policy
from taxcalc.records import Records


class Consumption(ParametersBase):
    """
    Consumption is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for Consumption class.

    Parameters
    ----------
    start_year: integer
        first calendar year for consumption parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if start_year is less than Policy.JSON_START_YEAR.
        if num_years is less than one.

    Returns
    -------
    class instance: Consumption
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'consumption.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Consumption, self).__init__()
        self._vals = self._params_dict_from_json_file()
        if start_year < Policy.JSON_START_YEAR:
            raise ValueError('start_year < Policy.JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years < 1')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_consumption(self, revision):
        """
        Update consumption for given revision, a dictionary consisting
        of one or more year:modification dictionaries.
        For example: {2014: {'_MPC_xxx': [0.2, 0.1]}}

        Note that this method uses the specified revision to update the
        default MPC parameter values and the default BEN parameter values,
        so use this method just once rather than calling it sequentially
        in an attempt to update the parameters in several steps.
        """
        if not isinstance(revision, dict):
            raise ValueError('ERROR: revision is not a dictionary')
        if not revision:
            return  # no revision to update
        precall_current_year = self.current_year
        self.set_default_vals()
        # check that revisions keys are integers
        revision_years = sorted(list(revision.keys()))
        for year in revision_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in revision is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of revision_years
        first_revision_year = min(revision_years)
        if first_revision_year < self.start_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_revision_year, self.start_year))
        last_revision_year = max(revision_years)
        if last_revision_year > self.end_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_revision_year, self.end_year))
        # validate revision parameter names and types
        self._validate_assump_parameter_names_types(revision)
        if self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # implement the revision year by year
        revision_parameters = set()
        for year in revision_years:
            self.set_year(year)
            revision_parameters.update(revision[year].keys())
            self._update({year: revision[year]})
        self.set_year(precall_current_year)
        # validate revision parameter values
        self._validate_assump_parameter_values(revision_parameters)
        if self.parameter_errors:
            raise ValueError('\n' + self.parameter_errors)

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
            if getattr(self, 'MPC_{}'.format(var)) > 0.0:
                return True
        for var in Consumption.BENEFIT_VARS:
            if getattr(self, 'BEN_{}_value'.format(var)) < 1.0:
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
            mpc_var = getattr(self, 'MPC_{}'.format(var))
            records_var[:] += mpc_var * income_change

    def benval_params(self):
        """
        Returns list of BEN_*_value parameter values
        """
        return [getattr(self, 'BEN_{}_value'.format(var))
                for var in Consumption.BENEFIT_VARS]
