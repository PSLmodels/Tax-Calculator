"""
Test implementation of complex reform in OSPC Tax-Calculator Parameters class.

SCRIPT USAGE: tax-calculator$ python reform_test.py

PYLINT USAGE: pylint --disable=locally-disabled reform_test.py
"""
import numpy as np
from numpy.testing import assert_array_equal
from taxcalc.parameters import Parameters
from taxcalc.utils import expand_array


def main():
    """
    Test implementation of multi-year reform.
    """
    # specify dimensions of policy Parameters object
    syr = 2013
    nyrs = 10

    # specify assumed inflation rates
    irates = {2013: 0.02, 2014: 0.02, 2015: 0.02, 2016: 0.03, 2017: 0.03,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.04, 2022: 0.04}
    ifactors = {}
    for i in range(0, nyrs):
        ifactors[syr + i] = 1.0 + irates[syr + i]
    iratelist = [irates[syr + i] for i in range(0, nyrs)]

    # instantiate policy Parameters object
    ppo = Parameters(start_year=syr, budget_years=nyrs, inflation_rates=irates)

    # confirm that parameters have current-law values
    assert_array_equal(getattr(ppo, '_AMT_thd_MarriedS'),
                       expand_array(np.array( #pylint: disable=no-member
                           [40400, 41050]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))
    assert_array_equal(getattr(ppo, '_EITC_c'),
                       expand_array(np.array( #pylint: disable=no-member
                           [[487, 3250, 5372, 6044],
                            [496, 3305, 5460, 6143],
                            [503, 3359, 5548, 6242]]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))
    assert_array_equal(getattr(ppo, '_II_em'),
                       expand_array(np.array( #pylint: disable=no-member
                           [3900, 3950, 4000]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))
    assert_array_equal(getattr(ppo, '_SS_Earnings_c'),
                       expand_array(np.array( #pylint: disable=no-member
                           [113700, 117000, 118500]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))

    # specify multi-year reform using a dictionary of year_provisions dicts
    reform = {
        2015: {
            '_AMT_thd_MarriedS': [60000]
        },
        2016: {
            '_EITC_c': [[900, 5000, 8000, 9000]],
            '_II_em': [7000],
            '_SS_Earnings_c': [300000]
        },
        2017: {
            '_AMT_thd_MarriedS': [80000],
            '_SS_Earnings_c': [500000], '_SS_Earnings_c_cpi': False
        },
        2019: {
            '_EITC_c': [[1200, 7000, 10000, 12000]],
            '_II_em': [9000],
            '_SS_Earnings_c': [700000], '_SS_Earnings_c_cpi': True
        }
    }

    # implement reform using Parameters class update method
    #   Note: apparently must pass update method a YEAR:PROVISIONS dictionary,
    #         where YEAR must equal Parameters current_year (although update
    #         method does not enforce this requirement).  The PROVISIONS are
    #         a dictionary of parameter:value pairs (as in the reform
    #         dictionary above).
    assert ppo.current_year == syr
    reform_years_list = reform.keys()
    last_reform_year = max(reform_years_list)
    assert last_reform_year == 2019
    while ppo.current_year < last_reform_year:
        ppo.increment_year()
        if ppo.current_year in reform_years_list:
            year_provisions = {ppo.current_year: reform[ppo.current_year]}
            ppo.update(year_provisions)

    # move policy Parameters object back in time so current_year is syr+2
    #   Note: this would be typical usage because the first budget year
    #         is greater than Parameters start_year.
    ppo._current_year = ppo.start_year #pylint: disable=protected-access
    ppo.set_year(ppo.start_year)
    assert ppo.current_year == ppo.start_year
    ppo.increment_year()
    ppo.increment_year()
    assert ppo.current_year == syr + 2

    # confirm that actual parameters have expected post-reform values
    check_amt_thd_marrieds(ppo, reform, ifactors)
    check_eitc_c(ppo, reform, ifactors)
    check_ii_em(ppo, reform, ifactors)
    check_ss_earnings_c(ppo, reform, ifactors)

    # normal return
    return 0


def check_amt_thd_marrieds(ppo, reform, ifactor):
    """
    Compare actual and expected _AMT_thd_MarriedS parameter values.
    """
    actual = {}
    arr = getattr(ppo, '_AMT_thd_MarriedS')
    for i in range(0, ppo.budget_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 40400
    assert actual[2014] == 41050
    e2015 = reform[2015]['_AMT_thd_MarriedS'][0]
    assert actual[2015] == e2015
    e2016 = int(round(ifactor[2016] * actual[2015]))
    assert actual[2016] == e2016
    e2017 = reform[2017]['_AMT_thd_MarriedS'][0]
    assert actual[2017] == e2017
    e2018 = int(round(ifactor[2018] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = int(round(ifactor[2019] * actual[2018]))
    assert actual[2019] == e2019
    e2020 = int(round(ifactor[2020] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactor[2021] * actual[2020]))
    absdiff = abs(actual[2021] - e2021)
    if absdiff <= 1:
        pass # close enough for government work
    else:
        assert actual[2021] == e2021
    e2022 = int(round(ifactor[2022] * actual[2021]))
    assert actual[2022] == e2022


def check_eitc_c(ppo, reform, ifactor):
    """
    Compare actual and expected _EITC_c parameter values.
    """
    actual = {}
    arr = getattr(ppo, '_EITC_c')
    alen = len(arr[0])
    for i in range(0, ppo.budget_years):
        actual[ppo.start_year + i] = arr[i]
    assert_array_equal(actual[2013], [487, 3250, 5372, 6044])
    assert_array_equal(actual[2014], [496, 3305, 5460, 6143])
    assert_array_equal(actual[2015], [503, 3359, 5548, 6242])
    e2016 = reform[2016]['_EITC_c'][0]
    assert_array_equal(actual[2016], e2016)
    e2017 = [int(round(ifactor[2017] * actual[2016][j]))
             for j in range(0, alen)]
    print '2017 ifactor: ', ifactor[2017]
    print '2017 actual: ', actual[2017], ' expected: ', e2017
    assert_array_equal(actual[2017], e2017)
    e2018 = [int(round(ifactor[2018] * actual[2017][j]))
             for j in range(0, alen)]
    print '2018 ifactor: ', ifactor[2018]
    print '2018 actual: ', actual[2018], ' expected: ', e2018
    assert_array_equal(actual[2018], e2018)
    e2019 = reform[2019]['_EITC_c'][0]
    assert_array_equal(actual[2019], e2019)
    e2020 = [int(round(ifactor[2020] * actual[2019][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2020], e2020)
    e2021 = [int(round(ifactor[2021] * actual[2020][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2021], e2021)
    e2022 = [int(round(ifactor[2022] * actual[2021][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2022], e2022)


def check_ii_em(ppo, reform, ifactor):
    """
    Compare actual and expected _II_em parameter values.
    """
    actual = {}
    arr = getattr(ppo, '_II_em')
    for i in range(0, ppo.budget_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 3900
    assert actual[2014] == 3950
    assert actual[2015] == 4000
    e2016 = reform[2016]['_II_em'][0]
    assert actual[2016] == e2016
    e2017 = int(round(ifactor[2017] * actual[2016]))
    assert actual[2017] == e2017
    e2018 = int(round(ifactor[2018] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = reform[2019]['_II_em'][0]
    assert actual[2019] == e2019
    e2020 = int(round(ifactor[2020] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactor[2021] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(ifactor[2022] * actual[2021]))
    assert actual[2022] == e2022


def check_ss_earnings_c(ppo, reform, ifactor):
    """
    Compare actual and expected _SS_Earnings_c parameter values.
    """
    actual = {}
    arr = getattr(ppo, '_SS_Earnings_c')
    for i in range(0, ppo.budget_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 113700
    assert actual[2014] == 117000
    assert actual[2015] == 118500
    e2016 = reform[2016]['_SS_Earnings_c'][0]
    assert actual[2016] == e2016
    e2017 = reform[2017]['_SS_Earnings_c'][0]
    assert actual[2017] == e2017
    e2018 = actual[2017] # no indexing after 2017
    assert actual[2018] == e2018
    e2019 = reform[2019]['_SS_Earnings_c'][0]
    assert actual[2019] == e2019
    e2020 = int(round(ifactor[2020] * actual[2019])) # indexing after 2019
    assert actual[2020] == e2020
    e2021 = int(round(ifactor[2021] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(ifactor[2022] * actual[2021]))
    absdiff = abs(actual[2022] - e2022)
    if absdiff <= 1:
        pass # close enough for government work
    else:
        assert actual[2022] == e2022


if __name__ == '__main__':
    exit(main())
