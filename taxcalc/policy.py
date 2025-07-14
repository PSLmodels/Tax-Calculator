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
    # (1) specify which Policy parameters have been removed or renamed recently
    #     where "recently" means in the last major release
    REMOVED_PARAMS = {
        # following parameters were renamed in PR 2918
        'SS_thd50': 'was renamed SS_thd1 in Tax-Calculator 5.0.0',
        'SS_thd85': 'was renamed SS_thd2 in Tax-Calculator 5.0.0',
        # following parameters were removed in PR 2919
        'PT_rt1': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt2': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt3': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt4': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt5': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt6': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt7': 'was removed in Tax-Calculator 5.0.0',
        'PT_rt8': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk1': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk2': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk3': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk4': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk5': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk6': 'was removed in Tax-Calculator 5.0.0',
        'PT_brk7': 'was removed in Tax-Calculator 5.0.0',
        'PT_EligibleRate_active': 'was removed in Tax-Calculator 5.0.0',
        'PT_EligibleRate_passive': 'was removed in Tax-Calculator 5.0.0',
        'PT_wages_active_income': 'was removed in Tax-Calculator 5.0.0',
        'PT_top_stacking': 'was removed in Tax-Calculator 5.0.0',
        # following parameters were removed in PR 2920
        'ID_AmountCap_Switch': 'was removed in Tax-Calculator 5.0.0',
        'ID_AmountCap_rt': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitCap_Switch': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitCap_rt': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitSurtax_Switch': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitSurtax_crt': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitSurtax_trt': 'was removed in Tax-Calculator 5.0.0',
        'ID_BenefitSurtax_em': 'was removed in Tax-Calculator 5.0.0',
        # following parameters were renamed in PR 2928
        'CDCC_ps': 'was renamed CDCC_ps1 in Tax-Calculator 5.1.0',
        'CDCC_crt': 'was renamed CDCC_po1_rate_max in Tax-Calculator 5.1.0',
        'CDCC_frt': 'was renamed CDCC_po1_rate_min in Tax-Calculator 5.1.0',
        'CDCC_po_step_size': (
            'was renamed CDCC_po1_step_size in Tax-Calculator 5.1.0'
        ),
        # following parameter was renamed in PR 2929
        'II_prt': 'was renamed II_em_prt in Tax-Calculator 5.1.0',
        # following parameter was renamed in PR 2932
        'ID_Charity_crt_cash': (
            'was renamed ID_Charity_crt_all in Tax-Calculator 5.1.0'
        ),
    }
    # (2) specify which Policy parameters have been redefined recently
    #     where "recently" means in the last major release
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
        ]
        for param in reform.keys():
            if param in deprecated_parameters:
                print(  # pragma: no cover
                    f'DEPRECATION WARNING: the {param} policy parameter\n'
                    'is scheduled to be removed in Tax-Calculator 6.0.0;\n'
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
