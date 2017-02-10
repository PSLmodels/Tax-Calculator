"""
Tax-Calculator Growdiff class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 growdiff.py
# pylint --disable=locally-disabled growdiff.py

from .policy import Policy
from .parameters import ParametersBase


class Growdiff(ParametersBase):
    """
    Constructor for growth difference class.

    Parameters
    ----------
    growdiff_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of growth difference parameters; if None, default
        parameters are read from the growdiff.json file.

    start_year: integer
        first calendar year for growth difference parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if growdiff_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Growdiff
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growdiff.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self, growdiff_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Growdiff, self).__init__()
        if growdiff_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(growdiff_dict, dict):
            self._vals = growdiff_dict
        else:
            raise ValueError('growdiff_dict is neither None nor a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Growdiff ctor')
        self.initialize(start_year, num_years)

    def update_growdiff(self, revisions):
        """
        Update growdiff default values using specified revisions, which is
        a dictionary containing one or more year:modification dictionaries.
        For example: {2014: {'_AWAGE': [0.01]}}.
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            self._update({year: revisions[year]})
        self.set_year(precall_current_year)

    def apply_growdiff(self, gfactors):
        """
        Apply updated growdiff values to specified Growfactors instance.
        """
        # pylint: disable=no-member
        for i in range(0, self.num_years):
            cyr = i + Growdiff.JSON_START_YEAR
            gfactors.update('ABOOK', cyr, self._ABOOK[i])
            gfactors.update('ACGNS', cyr, self._ACGNS[i])
            gfactors.update('ACPIM', cyr, self._ACPIM[i])
            gfactors.update('ACPIU', cyr, self._ACPIU[i])
            gfactors.update('ADIVS', cyr, self._ADIVS[i])
            gfactors.update('AGDPN', cyr, self._AGDPN[i])
            gfactors.update('AINTS', cyr, self._AINTS[i])
            gfactors.update('AIPD', cyr, self._AIPD[i])
            gfactors.update('ASCHCI', cyr, self._ASCHCI[i])
            gfactors.update('ASCHCL', cyr, self._ASCHCL[i])
            gfactors.update('ASCHEI', cyr, self._ASCHEI[i])
            gfactors.update('ASCHEL', cyr, self._ASCHEL[i])
            gfactors.update('ASCHF', cyr, self._ASCHF[i])
            gfactors.update('ASOCSEC', cyr, self._ASOCSEC[i])
            gfactors.update('ATXPY', cyr, self._ATXPY[i])
            gfactors.update('AUCOMP', cyr, self._AUCOMP[i])
            gfactors.update('AWAGE', cyr, self._AWAGE[i])
