"""
Tax-Calculator Consumption class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 consumption.py
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
    consumption_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of marginal propensity to consume (MPC) parameters and
        benefit (BEN) value-of-in-kind-benefit parameters;
        if None, all parameters are read from DEFAULTS_FILENAME file.

    start_year: integer
        first calendar year for consumption parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if consumption_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Consumption
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'consumption.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self, consumption_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Consumption, self).__init__()
        if consumption_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(consumption_dict, dict):
            self._vals = consumption_dict
        else:
            raise ValueError('consumption_dict is not None or a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Consumption ctor')
        self.initialize(start_year, num_years)

    def update_consumption(self, revisions):
        """
        Update consumption for given revisions, a dictionary consisting
        of one or more year:modification dictionaries.
        For example: {2014: {'_MPC_xxx': [0.2, 0.1]}}

        Note that this method uses the specified revisions to update the
        default MPC parameter values and the default BEN parameter values,
        so use this method just once rather than calling it sequentially
        in an attempt to update the parameters in several steps.
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        # specify revisions ordered by year
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            self._update({year: revisions[year]})
        self.set_year(precall_current_year)

    RESPONSE_VARS = set(['e17500', 'e18400', 'e19800', 'e20400'])
    BENEFIT_VARS = set(['snap', 'vet', 'mcare', 'mcaid', 'other'])

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
