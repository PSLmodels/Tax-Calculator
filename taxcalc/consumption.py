"""
Tax-Calculator marginal Consumption class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 consumption.py
# pylint --disable=locally-disabled consumption.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

from .policy import Policy
from .parameters import ParametersBase


class Consumption(ParametersBase):
    """
    Constructor for marginal Consumption class.

    Parameters
    ----------
    consumption_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of marginal propensity to consume (MPC) parameters;
        if None, all MPC parameters are read from DEFAULTS_FILENAME file.

    start_year: integer
        first calendar year for MPC parameters.

    num_years: integer
        number of calendar years for which to specify MPC parameter
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
        if consumption_dict is not None:
            self._validate_mpc_values()

    def update_consumption(self, revisions):
        """
        Update consumption for given revisions, a dictionary consisting
        of one or more year:modification dictionaries.
        For example: {2014: {'_MPC_xxx': [0.2, 0.1]}}
        Also checks for valid MPC parameter values in revisions dictionary.
        NOTE: this method uses the specified revisions to update the
              DEFAULT MPC parameter values, so use this method just once
              rather than calling it sequentially in an attempt to update
              MPC parameters in several steps.
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        # specify revisions
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            self._update({year: revisions[year]})
        self.set_year(precall_current_year)
        self._validate_mpc_values()

    def has_response(self):
        """
        Returns true if any MPC parameters are positive for current_year;
        returns false if all MPC parameters are zero.
        """
        # pylint: disable=no-member
        if self.MPC_xxx > 0.0 or self.MPC_yyy > 0.0:
            return True
        else:
            return False

    # ----- begin private methods of Consumption class -----

    def _validate_mpc_values(self):
        """
        Check that each MPC parameter is in [0,1] range and that
        sum of all MPC parameters in a year is no more than one.
        """
        for iyr in range(0, self.num_years):
            sum_mpc = 0.0
            for mpc in self._vals:
                val = getattr(self, mpc)[iyr]
                sum_mpc += val
                if val < 0.0 or val > 1.0:
                    msg = '{} is outside [0,1] range in year {}; value is {}'
                    cyr = iyr + self.start_year
                    raise ValueError(msg.format(mpc, cyr, val))
            if sum_mpc > 1.0:
                msg = 'sum of MPC = {} is greater than one for year {}'
                raise ValueError(msg.format(sum_mpc, iyr + self.start_year))

# end Consumption class
