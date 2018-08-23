"""
Tax-Calculator GrowDiff class that is used to modify GrowFactors.
"""
# CODING-STYLE CHECKS:
# pycodestyle growdiff.py
# pylint --disable=locally-disabled growdiff.py

import numpy as np
from taxcalc.parameters import ParametersBase


class GrowDiff(ParametersBase):
    """
    GrowDiff is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for GrowDiff class.

    Parameters
    ----------
    start_year: integer
        first calendar year for growth difference parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if start_year is less than 2013
        if num_years is less than one.

    Returns
    -------
    class instance: GrowDiff
    """

    JSON_START_YEAR = 2013  # must be same as Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growdiff.json'
    DEFAULT_NUM_YEARS = 15  # must be same as Policy.DEFAULT_NUM_YEARS

    def __init__(self,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(GrowDiff, self).__init__()
        self._vals = self._params_dict_from_json_file()
        if start_year < GrowDiff.JSON_START_YEAR:
            raise ValueError('start_year < GrowDiff.JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years < 1')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_growdiff(self, revision):
        """
        Update growdiff default values using specified revision, which is
        a dictionary containing one or more year:modification dictionaries.
        For example: {2014: {'_AWAGE': [0.01]}}.
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
