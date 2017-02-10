"""
Tax-Calculator economic Growth adjustment class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 growth.py
# pylint --disable=locally-disabled growth.py

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
    REAL_GDP_GROWTH_RATES = [0.0243, 0.0113, 0.0159, 0.0093, 0.0191,
                             0.0172, 0.0130, 0.0123, 0.0155, 0.0161,
                             0.0165, 0.0165, 0.0166, 0.0164]

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

    def default_real_gdp_growth_rate(self):
        """
        Return REAL_GDP_GROWTH_RATES array element for current_year.
        """
        iyr = self.current_year - Growth.JSON_START_YEAR
        return Growth.REAL_GDP_GROWTH_RATES[iyr]

    def update_growth(self, revisions):
        """
        Update economic growth rates/targets as specified in revisions, which
        is a dictionary containing one or more year:modification dictionaries.
        For example: {2014: {'_factor_adjustment': [0.04, 0.03]}}
        Also, checks that at least one of these two relationships is true
        (a) _factor_adjustment[iyr] == 0.0
        (b) _factor_target[iyr] = Growth.REAL_GDP_GROWTH_RATES[iyr]
        for each index year iyr.
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

    def apply_change(self, records):
        """
        Apply either factor_adjustment or factor_target change to
        specified records object's blowup factors for current_year.
        """
        # pylint: disable=no-member
        if self.factor_adjustment != 0.0:
            self._adjustment_change(records)
        else:
            if self.factor_target != self.default_real_gdp_growth_rate():
                self._target_change(records)

    # ----- begin private methods of Growth class -----

    def _adjustment_change(self, records):
        """
        Add factor_adjustment to specified records object's
        blowup factors for current_year.
        """
        diff = self.factor_adjustment  # pylint: disable=no-member
        year = self.current_year
        """
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
        records.BF.ACPIM[year] += diff
        records.BF.ASOCSEC[year] += diff
        records.BF.AUCOMP[year] += diff
        records.BF.AIPD[year] += diff
        """

    def _target_change(self, records):
        """
        Add distance to records object's blowup factors for current_year.
        """
        year = self.current_year
        """
        pgr = records.BF.APOPN[year]
        """
        dgr = self.default_real_gdp_growth_rate()
        # pylint: disable=no-member
        if self.factor_target != dgr:
            """
            # user inputs theoretically should be based on GDP
            distance = (self.factor_target - dgr) / pgr
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
            records.BF.ACPIM[year] += distance
            records.BF.ASOCSEC[year] += distance
            records.BF.AUCOMP[year] += distance
            records.BF.AIPD[year] += distance
            """
