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
    # specify complexity of reform assumed in the test
    reform_includes_2dim_parameters = False

    # summarize test results
    #
    # If reform_includes_2dim_parameters == False, then
    #   test produces NO ASSERT ERRORS
    #
    # If reform_includes_2dim_parameters == True, then
    #   test produces the following Python error:
    #   --------------------------------------------------------------------
    #   tax-calculator$ python reform_test.py
    #   Traceback (most recent call last):
    #     File "reform_test.py", line 177, in <module>
    #       exit(main())
    #     File "reform_test.py", line 100, in main
    #       ppo.update(year_provisions)
    #     File "/Users/mrh/work/OSPC/tax-calculator/taxcalc/parameters.py",
    #          line 125, in update
    #       cur_val[offset:] = nval[num_years_to_skip:]
    #   ValueError: could not broadcast input array from shape (7) into
    #               shape (7,4)
    #   --------------------------------------------------------------------

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
    assert_array_equal(ppo._II_em, #pylint: disable=no-member,protected-access
                       expand_array(np.array( #pylint: disable=no-member
                           [3900, 3950, 4000]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))
    assert_array_equal(ppo._EITC_c, #pylint: disable=no-member,protected-access
                       expand_array(np.array( #pylint: disable=no-member
                           [[487, 3250, 5372, 6044],
                            [496, 3305, 5460, 6143],
                            [503, 3359, 5548, 6242]]),
                                    inflate=True, inflation_rates=iratelist,
                                    num_years=nyrs))

    # specify multi-year reform using a dictionary of year_provisions dicts
    if reform_includes_2dim_parameters:
        reform = {
            2015: {
                '_AMT_thd_MarriedS': [60000]
            },
            2016: {
                '_EITC_c': [900, 5000, 8000, 9000],
                '_II_em': [7000],
                '_SS_Earnings_c': [300000]
            },
            2017: {
                '_AMT_thd_MarriedS': [80000],
                '_SS_Earnings_c': [500000]
            },
            2019: {
                '_EITC_c': [1200, 7000, 10000, 12000],
                '_II_em': [9000],
                '_SS_Earnings_c': [700000]
            }
        }
    else: # if reform includes only 1D parameters
        reform = {
            2015: {
                '_AMT_thd_MarriedS': [60000]
            },
            2016: {
                '_II_em': [7000],
                '_SS_Earnings_c': [300000]
            },
            2017: {
                '_AMT_thd_MarriedS': [80000],
                '_SS_Earnings_c': [500000]
            },
            2019: {
                '_II_em': [9000],
                '_SS_Earnings_c': [700000]
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
    check_ii_em(ppo, reform, ifactors)
    check_ss_earnings_c(ppo, reform, ifactors)

    # normal return
    return 0


def check_amt_thd_marrieds(ppo, reform, ifactors):
    """
    Compare actual and expected _AMT_thd_MarriedS parameter values.
    """
    actual = {}
    for i in range(0, ppo.budget_years):
        act = ppo._AMT_thd_MarriedS[i] #pylint: disable=no-member,protected-access
        actual[ppo.start_year + i] = act
    assert actual[2013] == 40400
    assert actual[2014] == 41050
    e2015 = reform[2015]['_AMT_thd_MarriedS'][0]
    assert actual[2015] == e2015
    e2016 = int(round(ifactors[2016] * actual[2015]))
    assert actual[2016] == e2016
    e2017 = reform[2017]['_AMT_thd_MarriedS'][0]
    assert actual[2017] == e2017
    e2018 = int(round(ifactors[2018] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = int(round(ifactors[2019] * actual[2018]))
    assert actual[2019] == e2019
    e2020 = int(round(ifactors[2020] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactors[2021] * actual[2020]))
    absdiff = abs(actual[2021] - e2021)
    if absdiff <= 1:
        pass # close enough for government work
    else:
        assert actual[2021] == e2021
    e2022 = int(round(ifactors[2022] * actual[2021]))
    assert actual[2022] == e2022


def check_ii_em(ppo, reform, ifactors):
    """
    Compare actual and expected _II_em parameter values.
    """
    actual = {}
    for i in range(0, ppo.budget_years):
        act = ppo._II_em[i] #pylint: disable=no-member,protected-access
        actual[ppo.start_year + i] = act
    assert actual[2013] == 3900
    assert actual[2014] == 3950
    assert actual[2015] == 4000
    e2016 = reform[2016]['_II_em'][0]
    assert actual[2016] == e2016
    e2017 = int(round(ifactors[2017] * actual[2016]))
    assert actual[2017] == e2017
    e2018 = int(round(ifactors[2018] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = reform[2019]['_II_em'][0]
    assert actual[2019] == e2019
    e2020 = int(round(ifactors[2020] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactors[2021] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(ifactors[2022] * actual[2021]))
    assert actual[2022] == e2022


def check_ss_earnings_c(ppo, reform, ifactors):
    """
    Compare actual and expected _SS_Earnings_c parameter values.
    """
    actual = {}
    for i in range(0, ppo.budget_years):
        act = ppo._SS_Earnings_c[i] #pylint: disable=no-member,protected-access
        actual[ppo.start_year + i] = act
    assert actual[2013] == 113700
    assert actual[2014] == 117000
    assert actual[2015] == 118500
    e2016 = reform[2016]['_SS_Earnings_c'][0]
    assert actual[2016] == e2016
    e2017 = reform[2017]['_SS_Earnings_c'][0]
    assert actual[2017] == e2017
    e2018 = int(round(ifactors[2018] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = reform[2019]['_SS_Earnings_c'][0]
    assert actual[2019] == e2019
    e2020 = int(round(ifactors[2020] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactors[2021] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(ifactors[2022] * actual[2021]))
    absdiff = abs(actual[2022] - e2022)
    if absdiff <= 1:
        pass # close enough for government work
    else:
        assert actual[2022] == e2022


if __name__ == '__main__':
    exit(main())
