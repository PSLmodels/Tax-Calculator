"""
Simple macroeconomic growth model embedded in Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pycodestyle growmodel.py
# pylint --disable=locally-disabled growmodel.py

import numpy as np
from taxcalc.policy import Policy
from taxcalc.parameters import ParametersBase


class GrowModel(ParametersBase):
    """
    GrowModel is a subclass of the abstract ParametersBase class, and
    therefore, inherits its methods (none of which are shown here).

    Constructor for simple macroeconomic growth model.

    Parameters
    ----------
    start_year: integer
        first calendar year for GrowModel parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if start_year is less than Policy.JSON_START_YEAR
        if num_years is less than one.

    Returns
    -------
    class instance: GrowModel
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growmodel.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(GrowModel, self).__init__()
        self._vals = self._params_dict_from_json_file()
        if start_year < Policy.JSON_START_YEAR:
            raise ValueError('start_year < Policy.JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years < 1')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_growmodel(self, revision):
        """
        Implement multi-year parameter revision leaving current_year unchanged.

        Parameters
        ----------
        revision: dictionary of one or more YEAR:MODS pairs
            see Notes to Parameters _update method for info on MODS structure

        Raises
        ------
        ValueError:
            if revision is not a dictionary.
            if each YEAR in revision is not an integer.
            if minimum YEAR in the YEAR:MODS pairs is less than start_year.
            if minimum YEAR in the YEAR:MODS pairs is less than current_year.
            if maximum YEAR in the YEAR:MODS pairs is greater than end_year.
            if _validate_assump_parameter_names_types generates errors.
            if _validate_assump_parameter_values generates errors.

        Returns
        -------
        nothing: void

        Notes
        -----
        Given a revision dictionary, typical usage of the GrowModel class
        is as follows::

            gmodel = GrowModel()
            gmodel.update_growmodel(revision)

        In the above statements, the GrowModel() call instantiates a
        GrowModel object (gmodel) containing default parameter values,
        and the update_growmodel(revision) call applies the (possibly
        multi-year) revision specified in revision and then sets the
        current_year to the value of current_year when update_growmodel
        was called with parameters set for that pre-call year.

        An example of a multi-year, multi-parameter revision is as follows::

            revision = {
                2018: {
                    '_active': [True]
                },
                2019: {
                    '_active': [False]
                }
            }

        Notice that each of the YEAR:MODS pairs is specified as
        required by the private _update method, whose documentation
        provides several MODS dictionary examples.

        IMPORTANT NOTICE: when specifying a revision dictionary always group
        all revision provisions for a specified year into one YEAR:MODS pair.
        If you make the mistake of specifying two or more YEAR:MODS pairs
        with the same YEAR value, all but the last one will be overwritten,
        and therefore, not part of the revision.  This is because Python
        expects unique (not multiple) dictionary keys.  There is no way to
        catch this error, so be careful to specify revision dictionaries
        correctly.
        """
        # check that all revisions dictionary keys are integers
        if not isinstance(revision, dict):
            raise ValueError('ERROR: revision is not a dictionary')
        if not revision:
            return  # no revision to implement
        revision_years = sorted(list(revision.keys()))
        for year in revision_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in revision is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining revision_years
        first_revision_year = min(revision_years)
        if first_revision_year < self.start_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_revision_year, self.start_year))
        if first_revision_year < self.current_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < current_year={}'
            raise ValueError(
                msg.format(first_revision_year, self.current_year)
            )
        last_revision_year = max(revision_years)
        if last_revision_year > self.end_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_revision_year, self.end_year))
        # validate revision parameter names and types
        self._validate_assump_parameter_names_types(revision)
        if self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # implement the revision year by year
        precall_current_year = self.current_year
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

    def is_active(self):
        """
        Returns true if GrowModel is active in the current_year;
        returns false if GrowModel is inactive in the current_year.
        """
        return self.active  # pylint: disable=no-member

    def is_ever_active(self):
        """
        Returns true if GrowModel is active in any year;
        returns false if GrowModel is inactive in all years.
        """
        return np.any(getattr(self, '_active'))

    # ----- begin private methods of GrowModel class -----
