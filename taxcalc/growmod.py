"""
Tax-Calculator Growmod class that is used to modify GrowModel parameters.
"""
# CODING-STYLE CHECKS:
# pycodestyle growdiff.py
# pylint --disable=locally-disabled growdiff.py

import numpy as np
from taxcalc.parameters import ParametersBase


class Growmod(ParametersBase):
    """
    Growmod is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for Growmod class.

    Parameters
    ----------
    growmod_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of growth difference parameters; if None, default
        parameters are read from the growmod.json file.

    start_year: integer
        first calendar year for growth difference parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if growmod_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Growmod
    """

    JSON_START_YEAR = 2013  # must be same as Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growmod.json'
    DEFAULT_NUM_YEARS = 15  # must be same as Policy.DEFAULT_NUM_YEARS

    def __init__(self, growmod_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Growmod, self).__init__()
        if growmod_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(growmod_dict, dict):
            self._vals = growmod_dict
        else:
            raise ValueError('growmod_dict is neither None nor a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Growmod ctor')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_growmod(self, revision):
        """
        Update growmod default values using specified revision, which is
        a dictionary containing one or more year:modification dictionaries.
        For example: {2013: {'_active': [True]}}.
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

    def is_ever_active(self):
        """
        Returns true if _active parameter is True for any year;
        otherwise returns False.
        """
        return np.any(getattr(self, '_active'))

    def apply_to(self, growmodel):
        """
        Apply updated growmod values to specified GrowModel instance.
        """
        # pylint: disable=no-member
        for i in range(0, self.num_years):
            cyr = i + Growmod.JSON_START_YEAR
            growmodel.update('active', cyr, self._active[i])  # TODO: fix
