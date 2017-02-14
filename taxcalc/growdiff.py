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

    def apply_to(self, growfactors):
        """
        Apply updated growdiff values to specified Growfactors instance.
        """
        # pylint: disable=no-member
        for i in range(0, self.num_years):
            cyr = i + Growdiff.JSON_START_YEAR
            growfactors.update('ABOOK', cyr, self._ABOOK[i])
            growfactors.update('ACGNS', cyr, self._ACGNS[i])
            growfactors.update('ACPIM', cyr, self._ACPIM[i])
            growfactors.update('ACPIU', cyr, self._ACPIU[i])
            growfactors.update('ADIVS', cyr, self._ADIVS[i])
            growfactors.update('AGDPN', cyr, self._AGDPN[i])
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
