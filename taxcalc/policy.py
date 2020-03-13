"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

import os
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
    LAST_KNOWN_YEAR = 2019  # last year for which indexed param vals are known
    # should increase LAST_KNOWN_YEAR by one every calendar year
    LAST_BUDGET_YEAR = 2030  # last extrapolation year
    # should increase LAST_BUDGET_YEAR by one every calendar year
    DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

    # NOTE: the following three data structures use internal parameter names:
    # (1) specify which Policy parameters have been removed or renamed
    REMOVED_PARAMS = {
        # following five parameters removed in PR 2223 merged on 2019-02-06
        '_DependentCredit_Child_c': 'is a removed parameter name',
        '_DependentCredit_Nonchild_c': 'is a removed parameter name',
        '_DependentCredit_before_CTC': 'is a removed parameter name',
        '_FilerCredit_c': 'is a removed parameter name',
        '_ALD_InvInc_ec_base_RyanBrady': 'is a removed parameter name',
        # TODO: following parameter renamed in PR 2292 merged on 2019-04-15
        '_cpi_offset': 'was renamed CPI_offset in release 2.0.0',
        # TODO: following parameters renamed in PR 2345 merged on 2019-06-24
        '_PT_excl_rt':
        'was renamed PT_qbid_rt in release 2.4.0',
        '_PT_excl_wagelim_thd':
        'was renamed PT_qbid_taxinc_thd in release 2.4.0',
        '_PT_excl_wagelim_prt':
        'was renamed PT_qbid_taxinc_gap in release 2.4.0',
        '_PT_excl_wagelim_rt':
        'was renamed PT_qbid_w2_wages_rt in release 2.4.0'
    }
    # (2) specify which Policy parameters have been redefined recently
    REDEFINED_PARAMS = {
        # TODO: remove the CTC_c name:message pair sometime later in 2019
        '_CTC_c': 'CTC_c was redefined in release 1.0.0'
    }
    # (3) specify which Policy parameters are wage (rather than price) indexed
    WAGE_INDEXED_PARAMS = [
        '_SS_Earnings_c',
        '_SS_Earnings_thd'
    ]

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
        self._wage_growth_rates = self._gfactors.wage_growth_rates(syr, lyr)
        self.initialize(syr, nyrs, Policy.LAST_KNOWN_YEAR,
                        Policy.REMOVED_PARAMS,
                        Policy.REDEFINED_PARAMS,
                        Policy.WAGE_INDEXED_PARAMS)

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
        Implement specified policy reform and leave current_year unchanged.
        See Parameters._update for argument documentation and details about
        the expected structure of the reform dictionary.
        """
        self._update(reform, print_warnings, raise_errors)

    @staticmethod
    def parameter_list():
        """
        Returns list of parameter names in the policy_current_law.json file.
        """
        policy = Policy(only_reading_defaults=True)
        plist = list(policy._vals.keys())  # pylint: disable=protected-access
        del policy
        return plist
