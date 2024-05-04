"""
Tax-Calculator GrowDiff class that is used to modify GrowFactors.
"""
# CODING-STYLE CHECKS:
# pycodestyle growdiff.py
# pylint --disable=locally-disabled growdiff.py
import os
import numpy as np
from taxcalc.parameters import Parameters
from taxcalc.growfactors import GrowFactors
from taxcalc.policy import Policy
from taxcalc.records import Records


class GrowDiff(Parameters):
    """
    GrowDiff is a subclass of the abstract Parameters class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for GrowDiff class.

    Parameters
    ----------
    using_tmd: bool

    Returns
    -------
    class instance: GrowDiff
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS
    TMD_START_YEAR = Records.TMDCSV_YEAR
    DEFAULTS_FILE_NAME = 'growdiff.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, using_tmd=False):
        super().__init__()
        self.initialize(GrowDiff.JSON_START_YEAR,
                        GrowDiff.DEFAULT_NUM_YEARS)
        self.firstyear = GrowDiff.TMD_START_YEAR if using_tmd \
                         else GrowDiff.JSON_START_YEAR
        syrdiff = GrowDiff.TMD_START_YEAR - GrowDiff.JSON_START_YEAR
        self.numbyears = GrowDiff.DEFAULT_NUM_YEARS - syrdiff if using_tmd \
                         else GrowDiff.DEFAULT_NUM_YEARS

    @staticmethod
    def read_json_update(obj, topkey):
        """
        Return a revision dictionary suitable for use with update_growdiff
        method generated from the specified JSON object, which can be None or
        a string containing a local filename, a URL beginning with 'http'
        pointing to a valid JSON file hosted online, or a valid JSON text.
        """
        assert topkey in ('growdiff_baseline', 'growdiff_response')
        return Parameters._read_json_revision(obj, topkey)

    def update_growdiff(self, revision,
                        print_warnings=True, raise_errors=True):
        """
        Update growdiff default values using specified revision dictionary.
        See Parameters._update for argument documentation and details about
        the expected structure of the revision dictionary.
        """
        self._update(revision, print_warnings, raise_errors)

    def has_any_response(self):
        """
        Returns true if any parameter is non-zero for any year;
        returns false if all parameters are zero in all years.
        """
        for param in self:
            values = getattr(self, f"_{param}")
            for year in np.ndindex(values.shape):
                val = values[year]
                if val != 0.0:
                    return True
        return False

    def apply_to(self, growfactors):
        """
        Apply updated GrowDiff values to specified GrowFactors instance.
        """
        assert isinstance(growfactors, GrowFactors)
        for gfvn in GrowFactors.VALID_NAMES:
            _gfvn = f'_{gfvn}'
            for i in range(0, self.numbyears):
                cyr = i + self.firstyear
                diff_array = getattr(self, _gfvn)
                growfactors.update(gfvn, cyr, diff_array[i])

    def set_rates(self):
        """
        Unimplemented base class method that is not used here.
        """
