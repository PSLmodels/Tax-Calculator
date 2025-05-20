"""
Tax-Calculator federal tax policy Policy class.
"""
# CODING-STYLE CHECKS:
# pycodestyle policy.py
# pylint --disable=locally-disabled policy.py

import os
import json
from pathlib import Path
import paramtools
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

    last_budget_year: integer
        user-defined last parameter extrapolation year

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
    LAST_KNOWN_YEAR = 2025  # last year for which indexed param vals are known
    # should increase LAST_KNOWN_YEAR by one every calendar year
    LAST_BUDGET_YEAR = 2035  # default value of last extrapolation year
    # should increase LAST_BUDGET_YEAR by one every calendar year

    @staticmethod
    def number_of_years(last_budget_year=LAST_BUDGET_YEAR):
        """
        Static method returns number of policy parameters years given
        user-defined last_budget_year.
        """
        return last_budget_year - Policy.JSON_START_YEAR + 1

    # NOTE: the following three data structures use internal parameter names:
    # (1) specify which Policy parameters have been removed or renamed
    REMOVED_PARAMS = {
        # following five parameters removed in PR 2223 merged on 2019-02-06
        'DependentCredit_Child_c': 'is a removed parameter name',
        'DependentCredit_Nonchild_c': 'is a removed parameter name',
        'DependentCredit_before_CTC': 'is a removed parameter name',
        'FilerCredit_c': 'is a removed parameter name',
        'ALD_InvInc_ec_base_RyanBrady': 'is a removed parameter name',
        # following parameters renamed in PR 2345 merged on 2019-06-24
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

    def __init__(self,
                 gfactors=None,
                 last_budget_year=LAST_BUDGET_YEAR,
                 **kwargs):
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
        nyrs = Policy.number_of_years(last_budget_year)
        self._inflation_rates = None
        self._wage_growth_rates = None
        self.initialize(syr, nyrs, Policy.LAST_KNOWN_YEAR,
                        Policy.REMOVED_PARAMS,
                        Policy.REDEFINED_PARAMS,
                        Policy.WAGE_INDEXED_PARAMS, **kwargs)

    @staticmethod
    def tmd_constructor(
            growfactors: Path | GrowFactors,
            last_budget_year=LAST_BUDGET_YEAR,
    ):  # pragma: no cover
        """
        Static method returns a Policy object instantiated with TMD
        input data.  This convenience method works in a analogous way
        to Policy(), which returns a Policy object instantiated with
        non-TMD input data.
        """
        if isinstance(growfactors, Path):
            growfactors = GrowFactors(growfactors_filename=str(growfactors))
        else:
            assert isinstance(growfactors, GrowFactors)
        return Policy(gfactors=growfactors, last_budget_year=last_budget_year)

    @staticmethod
    def read_json_reform(obj):
        """
        Return a reform dictionary suitable for use with implement_reform
        method generated from the specified JSON object, which can be None or
        a string containing a local filename, a URL beginning with 'http'
        pointing to a valid JSON file hosted online, or a valid JSON text.
        """
        return Parameters._read_json_revision(obj, 'policy')

    def implement_reform(self, reform: dict,
                         print_warnings=True, raise_errors=True):
        """
        Implement reform using a Tax-Calculator-style reform dictionary.
        """
        if not isinstance(reform, dict):
            raise paramtools.ValidationError(
                {'errors': {'schema': 'reform must be a dictionary'}},
                None
            )
        deprecated_parameters = [
            'ID_AmountCap_Switch',
            'ID_AmountCap_rt',
            'ID_BenefitCap_Switch',
            'ID_BenefitCap_rt',
            'ID_BenefitSurtax_Switch',
            'ID_BenefitSurtax_crt',
            'ID_BenefitSurtax_trt',
            'ID_BenefitSurtax_em',
        ]
        for param in reform.keys():
            if param in deprecated_parameters:
                print(
                    f'DEPRECATION WARNING: the {param} policy parameter\n'
                    'is scheduled to be removed in Tax-Calculator 5.0.0;\n'
                    'if you think this removal should not happen, open an\n'
                    'issue on GitHub to make your case for non-removal.'
                )
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
        with open(path, 'r', encoding='utf-8') as f:
            defaults = json.loads(f.read())  # pylint: disable=protected-access
        return [k for k in defaults if k != "schema"]

    def set_rates(self):
        """
        Initialize policy parameter indexing rates.
        """
        cpi_vals = [
            vo["value"] for
            vo in self._data["parameter_indexing_CPI_offset"]["value"]
        ]
        # parameter_indexing_CPI_offset parameter is no longer used, so check:
        assert any(cpi_vals) is False, \
            'obsolete parameter_indexing_CPI_offset values must all be zero'
        syr = max(self.start_year, self._gfactors.first_year)
        self._inflation_rates = self._gfactors.price_inflation_rates(
            syr, self.end_year
        )
        self._wage_growth_rates = self._gfactors.wage_growth_rates(
            syr, self.end_year
        )
