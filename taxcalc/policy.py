"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

import os
import json
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
    JSON_START_YEAR = 2011  # remains the same unless earlier data added
    LAST_KNOWN_YEAR = 2019  # last year for which indexed param vals are known
    # should increase LAST_KNOWN_YEAR by one every calendar year
    LAST_BUDGET_YEAR = 2030  # last extrapolation year
    # should increase LAST_BUDGET_YEAR by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    # NOTE: the following three data structures use internal parameter names:
    # (1) specify which Policy parameters have been removed or renamed
    REMOVED_PARAMS = {
        # following five parameters removed in PR 2223 merged on 2019-02-06
        'DependentCredit_Child_c': 'is a removed parameter name',
        'DependentCredit_Nonchild_c': 'is a removed parameter name',
        'DependentCredit_before_CTC': 'is a removed parameter name',
        'FilerCredit_c': 'is a removed parameter name',
        'ALD_InvInc_ec_base_RyanBrady': 'is a removed parameter name',
        # TODO: following parameter renamed in PR 2292 merged on 2019-04-15
        "cpi_offset": (
            "was renamed parameter_indexing_CPI_offset. "
            "See documentation for change in usage."
        ),
        "CPI_offset": (
            "was renamed parameter_indexing_CPI_offset. "
            "See documentation for change in usage."
        ),
        # TODO: following parameters renamed in PR 2345 merged on 2019-06-24
        'PT_excl_rt':
        'was renamed PT_qbid_rt in release 2.4.0',
        'PT_excl_wagelim_thd':
        'was renamed PT_qbid_taxinc_thd in release 2.4.0',
        'PT_excl_wagelim_prt':
        'was renamed PT_qbid_taxinc_gap in release 2.4.0',
        'PT_excl_wagelim_rt':
        'was renamed PT_qbid_w2_wages_rt in release 2.4.0',
        'CTC_c_under5_bonus': 'was renamed CTC_c_under6_bonus.',
        'ACTC_rt_bonus_under5family':
        'was renamed ACTC_rt_bonus_under6family.',
        'CTC_new_c_under5_bonus': 'was renamed CTC_new_c_under6_bonus.'
    }
    # (2) specify which Policy parameters have been redefined recently
    REDEFINED_PARAMS = {}
    # (3) specify which Policy parameters are wage (rather than price) indexed
    WAGE_INDEXED_PARAMS = ['SS_Earnings_c', 'SS_Earnings_thd']

    def __init__(self, gfactors=None, only_reading_defaults=False, **kwargs):
        # put JSON contents of DEFAULTS_FILE_NAME into self._vals dictionary
        super().__init__()
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
        self._inflation_rates = None
        self._wage_growth_rates = None
        self.initialize(syr, nyrs, Policy.LAST_KNOWN_YEAR,
                        Policy.REMOVED_PARAMS,
                        Policy.REDEFINED_PARAMS,
                        Policy.WAGE_INDEXED_PARAMS, **kwargs)

    @staticmethod
    def read_json_reform(obj):
        """
        Return a reform dictionary suitable for use with implement_reform
        method generated from the specified JSON object, which can be None or
        a string containing a local filename, a URL beginning with 'http'
        pointing to a valid JSON file hosted online, or a valid JSON text.
        """
        return Parameters._read_json_revision(obj, 'policy')

    def implement_reform(self, reform,
                         print_warnings=True, raise_errors=True):
        """
        Implement reform using Tax-Calculator syled reforms/adjustments. Users
        may also use the adjust method with ParamTools styled reforms.
        """
        # need to do conversion:
        return self._update(reform, print_warnings, raise_errors)

    @staticmethod
    def parameter_list():
        """
        Returns list of parameter names in the policy_current_law.json file.
        """
        path = os.path.join(
            Policy.DEFAULTS_FILE_PATH,
            Policy.DEFAULTS_FILE_NAME
        )
        with open(path) as f:
            defaults = json.loads(f.read())  # pylint: disable=protected-access
        return [k for k in defaults if k != "schema"]

    def set_rates(self):
        """Initialize taxcalc indexing data."""
        cpi_vals = [
            vo["value"] for
            vo in self._data["parameter_indexing_CPI_offset"]["value"]
        ]
        # extend parameter_indexing_CPI_offset values through budget window
        # if they have not been extended already.
        cpi_vals = cpi_vals + cpi_vals[-1:] * (
            self.end_year - self.start_year + 1 - len(cpi_vals)
        )
        cpi_offset = {
            (self.start_year + ix): val
            for ix, val in enumerate(cpi_vals)
        }

        self._gfactors = GrowFactors()

        self._inflation_rates = [
            np.round(rate + cpi_offset[self.start_year + ix], 4)
            for ix, rate in enumerate(
                self._gfactors.price_inflation_rates(
                    self.start_year, self.end_year
                )
            )
        ]

        self._wage_growth_rates = self._gfactors.wage_growth_rates(
            self.start_year, self.end_year
        )
