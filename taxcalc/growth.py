from .policy import Policy
from .parameters_base import ParametersBase


class Growth(ParametersBase):

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growth.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS
    # REAL_GDP_GROWTH_RATES is a list indexed starting with JSON_START_YEAR
    REAL_GDP_GROWTH_RATES = [0.0244, 0.0118, 0.0291, 0.0331,
                             0.0285, 0.0223, 0.0202, 0.0188,
                             0.0183, 0.0178, 0.0171, 0.0166,
                             0.0165, 0.0166]

    def __init__(self, growth_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        if growth_dict:
            if not isinstance(growth_dict, dict):
                raise ValueError('growth_dict is not a dictionary')
            self._vals = growth_dict
        else:  # if None, read defaults
            self._vals = self._params_dict_from_json_file()
        self.initialize(start_year, num_years)

    def update_economic_growth(self, revisions):
        """
        Update economic growth rates/targets given the revisions, a dictionary
        consisting of year:modification dictionaries.
        For example: {2014: {'_BE_inc': [0.4, 0.3]}}
        """
        self.set_default_vals()
        if self.current_year != self.start_year:
            self.set_year(self.start_year)
        for year in revisions:
            if year != self.start_year:
                self.set_year(year)
            self._update({year: revisions[year]})

    @staticmethod
    def default_real_GDP_growth_rate(list_index):
        return Growth.REAL_GDP_GROWTH_RATES[list_index]


def adjustment(calc, percentage, year):
    records = calc.records
    records.BF.AGDPN[year] += percentage
    records.BF.ATXPY[year] += percentage
    records.BF.AWAGE[year] += percentage
    records.BF.ASCHCI[year] += percentage
    records.BF.ASCHCL[year] += percentage
    records.BF.ASCHF[year] += percentage
    records.BF.AINTS[year] += percentage
    records.BF.ADIVS[year] += percentage
    records.BF.ACGNS[year] += percentage
    records.BF.ASCHEI[year] += percentage
    records.BF.ASCHEL[year] += percentage
    records.BF.ABOOK[year] += percentage
    records.BF.ACPIU[year] += percentage
    records.BF.ACPIM[year] += percentage
    records.BF.ASOCSEC[year] += percentage
    records.BF.AUCOMP[year] += percentage
    records.BF.AIPD[year] += percentage


def target(calc, target_list, year):
    records = calc.records
    pgr = records.BF.APOPN[year]
    syr = Growth.JSON_START_YEAR
    dgr = Growth.default_real_GDP_growth_rate(year - syr)
    if year >= syr and target_list[year - syr] != dgr:
        # user inputs theoretically should be based on GDP
        distance = (target_list[year - syr] - dgr) / pgr
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
