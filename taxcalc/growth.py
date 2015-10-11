import copy
import json
import os
import numpy as np
from .policy import Policy
from .parameters_base import ParametersBase

class Growth(ParametersBase):

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'growth.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS
    DEFAULT_INFLATION_RATES =  {2013: 0.015, 2014: 0.020, 2015: 0.022, 2016: 0.020, 2017: 0.021,
               2018: 0.022, 2019: 0.023, 2020: 0.024, 2021: 0.024, 2022: 0.024,
               2023: 0.024, 2024: 0.024}

    def __init__(self, growth_dict=None,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS,
                 inflation_rates=DEFAULT_INFLATION_RATES):
        if growth_dict:
            if not isinstance(growth_dict, dict):
                raise ValueError('growth_dict is not a dictionary')
            self._vals = growth_dict
        else:  # if None, read defaults
            self._vals = self._params_dict_from_json_file()

        self.initialize(start_year, num_years)

    def update_economic_growth(self, reform):
        '''Update economic growth rates/targets
        for a reform, a dictionary
        consisting of year: modification dictionaries. For example:
        {2014: {'_BE_inc': [0.4, 0.3]}}'''
        self.set_default_vals()
        if self.current_year != self.start_year:
            self.set_year(self.start_year)

        for year in reform:
            if year != self.start_year:
                self.set_year(year)
            self._update({year: reform[year]})
            
            
def growth(calc_x, calc_y):
    calc_x_growth = copy.deepcopy(calc_x)
    calc_y_growth = copy.deepcopy(calc_y)
    
    if calc_y_growth.growth.factor_adjustment != 0:
        percentage = calc_y_growth.growth.factor_adjustment
        year = calc_y_growth.growth.current_year + 1
        factor_adjustment(calc_x_growth, percentage, year)
        factor_adjustment(calc_y_growth, percentage, year)
    elif calc_y_growth.growth.factor_target != 0:
        target = calc_y_growth.growth._target
        year = calc_y_growth.growth.current_year + 1
        inflation = inflation_rates
        factor_target(calc_x_growth, target, inflation, year)
        factor_target(calc_y_growth, target, inflation, year)
    
    calc_x_growth.calc_all()
    calc_y_growth.calc_all()
    
    return (calc_x_growth, calc_y_growth)

def factor_adjustment(calc, percentage, year):
    records = calc.records
    records.BF.AGDPN[year] += percentage * abs(records.BF.AGDPN[year] - 1)
    records.BF.ATXPY[year] += percentage * abs(records.BF.ATXPY[year] - 1)
    records.BF.AWAGE[year] += percentage * abs(records.BF.AWAGE[year] - 1)
    records.BF.ASCHCI[year] += percentage * abs(records.BF.ASCHCI[year] - 1)
    records.BF.ASCHCL[year] += percentage * abs(records.BF.ASCHCL[year] - 1)
    records.BF.ASCHF[year] += percentage * abs(records.BF.ASCHF[year] - 1)
    records.BF.AINTS[year] += percentage * abs(records.BF.AINTS[year] - 1)
    records.BF.ADIVS[year] += percentage * abs(records.BF.ADIVS[year] - 1)
    records.BF.ACGNS[year] += percentage * abs(records.BF.ACGNS[year] - 1)
    records.BF.ASCHEI[year] += percentage * abs(records.BF.ASCHEI[year] - 1)
    records.BF.ASCHEL[year] += percentage * abs(records.BF.ASCHEL[year] - 1)
    records.BF.ABOOK[year] += percentage * abs(records.BF.ABOOK[year] - 1)
    records.BF.ACPIU[year] += percentage * abs(records.BF.ACPIU[year] - 1)
    records.BF.ACPIM[year] += percentage * abs(records.BF.ACPIM[year] - 1)
    records.BF.ASOCSEC[year] += percentage * abs(records.BF.ASOCSEC[year] - 1)
    records.BF.AUCOMP[year] += percentage * abs(records.BF.AUCOMP[year] - 1)
    records.BF.AIPD[year] += percentage * abs(records.BF.AIPD[year] - 1)

def factor_target(calc, target, inflation, year):
    # 2013 is the start year of all parameter arrays. Hard coded for now.
    # Need to be fixed later
    if year >= 2013 and target[year - 2013] != 0:
        # user inputs theoretically should be based on GDP
        g = abs(records.BF.AGDPN[year] - 1)
        ratio = (target[year - 2013] + inflation[year]) / g

        # apply this ratio to all the dollar amount factors
        records.BF.AGDPN[year] = ratio * abs(records.BF.AGDPN[year] - 1) + 1
        records.BF.ATXPY[year] = ratio * abs(records.BF.ATXPY[year] - 1) + 1
        records.BF.AWAGE[year] = ratio * abs(records.BF.AWAGE[year] - 1) + 1
        records.BF.ASCHCI[year] = ratio * abs(records.BF.ASCHCI[year] - 1) + 1
        records.BF.ASCHCL[year] = ratio * abs(records.BF.ASCHCL[year] - 1) + 1
        records.BF.ASCHF[year] = ratio * abs(records.BF.ASCHF[year] - 1) + 1
        records.BF.AINTS[year] = ratio * abs(records.BF.AINTS[year] - 1) + 1
        records.BF.ADIVS[year] = ratio * abs(records.BF.ADIVS[year] - 1) + 1
        records.BF.ACGNS[year] = ratio * abs(records.BF.ACGNS[year] - 1) + 1
        records.BF.ASCHEI[year] = ratio * abs(records.BF.ASCHEI[year] - 1) + 1
        records.BF.ASCHEL[year] = ratio * abs(records.BF.ASCHEL[year] - 1) + 1
        records.BF.ABOOK[year] = ratio * abs(records.BF.ABOOK[year] - 1) + 1
        records.BF.ACPIU[year] = ratio * abs(records.BF.ACPIU[year] - 1) + 1
        records.BF.ACPIM[year] = ratio * abs(records.BF.ACPIM[year] - 1) + 1
        records.BF.ASOCSEC[year] = ratio * abs(records.BF.ASOCSEC[year] - 1) + 1
        records.BF.AUCOMP[year] = ratio * abs(records.BF.AUCOMP[year] - 1) + 1
        records.BF.AIPD[year] = ratio * abs(records.BF.AIPD[year] - 1) + 1

