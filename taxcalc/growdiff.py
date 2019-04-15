"""
Tax-Calculator GrowDiff class that is used to modify GrowFactors.
"""
# CODING-STYLE CHECKS:
# pycodestyle growdiff.py
# pylint --disable=locally-disabled growdiff.py
import os
import numpy as np
from taxcalc.parameters import Parameters


class GrowDiff(Parameters):
    """
    GrowDiff is a subclass of the abstract Parameters class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for GrowDiff class.

    Parameters
    ----------
    none

    Returns
    -------
    class instance: GrowDiff
    """

    JSON_START_YEAR = 2013  # must be same as Policy.JSON_START_YEAR
    DEFAULT_NUM_YEARS = 17  # must be same as Policy.DEFAULT_NUM_YEARS
    DEFAULTS_FILE_NAME = 'growdiff.json'
    DEFAULTS_FILE_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        super().__init__()
        self.initialize(GrowDiff.JSON_START_YEAR,
                        GrowDiff.DEFAULT_NUM_YEARS)

    def update_growdiff(self, revision,
                        print_warnings=True, raise_errors=True):
        """
        Update growdiff default values using specified revision dictionary.
        (see Parameters._update for argument documentation.)
        """
        self._update(revision, print_warnings, raise_errors)

    def has_any_response(self):
        """
        Returns true if any parameter is non-zero for any year;
        returns false if all parameters are zero in all years.
        """
        for param in self._vals:
            values = getattr(self, param)
            for year in np.ndindex(values.shape):
                val = values[year]
                if val != 0.0:
                    return True
        return False

    def apply_to(self, growfactors):
        """
        Apply updated GrowDiff values to specified GrowFactors instance.
        """
        # pylint: disable=no-member
        for i in range(0, self.num_years):
            cyr = i + self.start_year
            growfactors.update('ABOOK', cyr, self._ABOOK[i])
            growfactors.update('ACGNS', cyr, self._ACGNS[i])
            growfactors.update('ACPIM', cyr, self._ACPIM[i])
            growfactors.update('ACPIU', cyr, self._ACPIU[i])
            growfactors.update('ADIVS', cyr, self._ADIVS[i])
            growfactors.update('AINTS', cyr, self._AINTS[i])
            growfactors.update('AIPD', cyr, self._AIPD[i])
            growfactors.update('ASCHCI', cyr, self._ASCHCI[i])
            growfactors.update('ASCHCL', cyr, self._ASCHCL[i])
            growfactors.update('ASCHEI', cyr, self._ASCHEI[i])
            growfactors.update('ASCHEL', cyr, self._ASCHEL[i])
            growfactors.update('ASCHF', cyr, self._ASCHF[i])
            growfactors.update('ASOCSEC', cyr, self._ASOCSEC[i])
            growfactors.update('ATXPY', cyr, self._ATXPY[i])
            growfactors.update('AUCOMP', cyr, self._AUCOMP[i])
            growfactors.update('AWAGE', cyr, self._AWAGE[i])
            growfactors.update('ABENOTHER', cyr, self._ABENOTHER[i])
            growfactors.update('ABENMCARE', cyr, self._ABENMCARE[i])
            growfactors.update('ABENMCAID', cyr, self._ABENMCAID[i])
            growfactors.update('ABENSSI', cyr, self._ABENSSI[i])
            growfactors.update('ABENSNAP', cyr, self._ABENSNAP[i])
            growfactors.update('ABENWIC', cyr, self._ABENWIC[i])
            growfactors.update('ABENHOUSING', cyr, self._ABENHOUSING[i])
            growfactors.update('ABENTANF', cyr, self._ABENTANF[i])
            growfactors.update('ABENVET', cyr, self._ABENVET[i])
