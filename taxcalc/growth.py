"""
Tax-Calculator economic Growth adjustment class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 growth.py
# pylint --disable=locally-disabled growth.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

from .policy import Policy
from .parameters import ParametersBase


class Growth(ParametersBase):
    """
    Constructor for economic growth adjustment class.

    Parameters
    ----------
    growth_dict: dictionary of PARAM:DESCRIPTION pairs
        dictionary of economic-growth parameters; if None, default
        parameters are read from the growth.json file.

    start_year: integer
        first calendar year for economic-growth parameters.

    num_years: integer
        number of calendar years for which to specify parameter
        values beginning with start_year.

    Raises
    ------
    ValueError:
        if growth_dict is neither None nor a dictionary.
        if num_years is less than one.

    Returns
    -------
    class instance: Growth
    """

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growth.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS
    # REAL_GDP_GROWTH_RATES is a list indexed starting with JSON_START_YEAR
    REAL_GDP_GROWTH_RATES = [0.0226, 0.0241, 0.0285, 0.0273, 0.0204,
                             0.0185, 0.0144, 0.0144, 0.0168, 0.0173,
                             0.0173, 0.0171, 0.0169, 0.0172]

    def __init__(self, growth_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(Growth, self).__init__()
        if growth_dict is None:
            self._vals = self._params_dict_from_json_file()
        elif isinstance(growth_dict, dict):
            self._vals = growth_dict
        else:
            raise ValueError('growth_dict is neither None nor a dictionary')
        if num_years < 1:
            raise ValueError('num_years < 1 in Growth ctor')
        self.initialize(start_year, num_years)

    def update_economic_growth(self, revisions):
        """
        Update economic growth rates/targets as specified in revisions, which
        is a dictionary containing one or more year:modification dictionaries.
        For example: {2014: {'_factor_adjustment': [0.04, 0.03]}}
        Also, checks that at least one of these two relationships is true:
        (a) _factor_adjustment[yr] == 0.0
        (b) _factor_target[yr] = Growth.REAL_GDP_GROWTH_RATES[yr-start_year].
        """
        precall_current_year = self.current_year
        self.set_default_vals()
        revision_years = sorted(list(revisions.keys()))
        for year in revision_years:
            self.set_year(year)
            # update valid parameter values for year
            self._update({year: revisions[year]})
        # check for valid parameters in each year
        # pylint: disable=no-member
        for iyr in range(0, self.num_years):
            if self._factor_adjustment[iyr] == 0.0:
                continue
            if self._factor_target[iyr] == Growth.REAL_GDP_GROWTH_RATES[iyr]:
                continue
            msg = 'both growth parameters have non-default values for year {}'
            raise ValueError(msg.format(iyr + self.start_year))
        # set year to year value before this method was called
        self.set_year(precall_current_year)

    @staticmethod
    def default_real_gdp_growth_rate(year_index):
        """
        Return REAL_GDP_GROWTH_RATE for year_index = (year - start_year).
        """
        return Growth.REAL_GDP_GROWTH_RATES[year_index]

    def apply_change(self, records, year):
        """
        Apply either _factor_adjustment or _factor_target change to
        specified records object's blowup_factors for specified calendar year.
        """
        # pylint: disable=no-member
        iyr = year - self.start_year
        if self._factor_adjustment[iyr] != 0.0:
            self._adjustment_change(records, year)
        elif self._factor_target[iyr] != Growth.REAL_GDP_GROWTH_RATES[iyr]:
            self._target_change(records, year)

    # ----- begin private methods of Growth class -----

    def _adjustment_change(self, records, year):
        """
        Add _factor_adjustment to specified records object's
        blowup_factors for specified calendar year.
        """
        # pylint: disable=no-member
        diff = self._factor_adjustment[year - self.start_year]
        records.BF.AGDPN[year] += diff
        records.BF.ATXPY[year] += diff
        records.BF.AWAGE[year] += diff
        records.BF.ASCHCI[year] += diff
        records.BF.ASCHCL[year] += diff
        records.BF.ASCHF[year] += diff
        records.BF.AINTS[year] += diff
        records.BF.ADIVS[year] += diff
        records.BF.ACGNS[year] += diff
        records.BF.ASCHEI[year] += diff
        records.BF.ASCHEL[year] += diff
        records.BF.ABOOK[year] += diff
        records.BF.ACPIU[year] += diff
        records.BF.ACPIM[year] += diff
        records.BF.ASOCSEC[year] += diff
        records.BF.AUCOMP[year] += diff
        records.BF.AIPD[year] += diff

    def _target_change(self, records, year):
        """
        Add distance to records object's blowup_factors for
        specified calendar year.
        """
        pgr = records.BF.APOPN[year]
        syr = self.start_year
        dgr = Growth.default_real_gdp_growth_rate(year - syr)
        # pylint: disable=no-member
        if year >= syr and self._factor_target[year - syr] != dgr:
            # user inputs theoretically should be based on GDP
            distance = (self._factor_target[year - syr] - dgr) / pgr
            # add this distance to all the dollar amount factors
            records.BF.AGDPN[year] += distance
            records.BF.ATXPY[year] += distance
            records.BF.AWAGE[year] += distance
            records.BF.ASCHCI[year] += distance
            records.BF.ASCHCL[year] += distance
            records.BF.ASCHF[year] += distance
            records.BF.AINTS[year] += distance
            records.BF.ADIVS[year] += distance
            records.BF.ACGNS[year] += distance
            records.BF.ASCHEI[year] += distance
            records.BF.ASCHEL[year] += distance
            records.BF.ABOOK[year] += distance
            records.BF.ACPIU[year] += distance
            records.BF.ACPIM[year] += distance
            records.BF.ASOCSEC[year] += distance
            records.BF.AUCOMP[year] += distance
            records.BF.AIPD[year] += distance
