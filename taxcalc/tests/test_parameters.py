""" Part of taxcalc pytest suite that tests parameters.py logic.
"""
import os
import numpy as np
from numpy.testing import assert_array_equal
import pytest
import tempfile
from taxcalc.parameters import Parameters, default_data
from taxcalc.utils import expand_array


@pytest.yield_fixture
def paramsfile():
    txt = """
          {
          "_almdep": {"value": [7150, 7250, 7400], "cpi_inflated": true},
          "_almsep": {"value": [40400, 41050], "cpi_inflated": true},
          "_rt5": {"value": [0.330], "cpi_inflated": false},
          "_rt7": {"value": [0.396], "cpi_inflated": false}
          }
          """
    pfile = tempfile.NamedTemporaryFile(mode="a", delete=False)
    pfile.write(txt)
    pfile.close()
    # must close and then yield for Windows platform
    yield pfile
    os.remove(pfile.name)


def test_create_parameters():
    p = Parameters()
    assert p


def test_multi_year_reform():
    """
    Test implementation of multi-year reform involving 1D and 2D parameters.
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

    # implement multi-year reform using Parameters class update method
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

    # end of test_multi_year_reform with the check_* functions below:

def check_amt_thd_marrieds(ppo, reform, ifactor):
    """
    Compare actual and expected _AMT_thd_MarriedS parameter values generated
    by the test_multi_year_reform() function above.
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
    Compare actual and expected _EITC_c parameter values generated
    by the test_multi_year_reform() function above.
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
    assert_array_equal(actual[2017], e2017)
    e2018 = [int(round(ifactor[2018] * actual[2017][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2018], e2018, #pylint: disable=no-member
                       rtol=0.0, atol=1.0)
    e2019 = reform[2019]['_EITC_c'][0]
    assert_array_equal(actual[2019], e2019)
    e2020 = [int(round(ifactor[2020] * actual[2019][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2020], e2020)
    e2021 = [int(round(ifactor[2021] * actual[2020][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2021], e2021, #pylint: disable=no-member
                       rtol=0.0, atol=1.0)
    e2022 = [int(round(ifactor[2022] * actual[2021][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2022], e2022, #pylint: disable=no-member
                       rtol=0.0, atol=1.0)

def check_ii_em(ppo, reform, ifactor):
    """
    Compare actual and expected _II_em parameter values generated
    by the test_multi_year_reform() function above.
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
    Compare actual and expected _SS_Earnings_c parameter values generated
    by the test_multi_year_reform() function above.
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


def test_constant_inflation_rate_without_reform():
    irate = 0.08
    syr = 2013
    p = Parameters(start_year=syr, budget_years=10, inflation_rate=irate)
    assert p._II_em[2013 - syr] == 3900
    # no reform
    # check implied inflation rate at end of budget years that end in 2022
    grate = float(p._II_em[2022 - syr]) / float(p._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)


def test_constant_inflation_rate_with_reform():
    irate = 0.08
    syr = 2013
    p = Parameters(start_year=syr, budget_years=10, inflation_rate=irate)
    # implement reform in 2021 which is the year before the last year = 2022
    for year in range(0, 8):
        p.increment_year()
    assert p.current_year == 2021
    reform = {2021: {"_II_em": [20000]}}
    p.update(reform)
    # check implied inflation rate just before reform
    grate = float(p._II_em[2020 - syr]) / float(p._II_em[2019 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)
    # check implied inflation rate just after reform
    grate = float(p._II_em[2022 - syr]) / float(p._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)


def test_variable_inflation_rate_without_reform():
    irates = {2013: 0.04, 2014: 0.04, 2015: 0.04, 2016: 0.04, 2017: 0.04,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.04, 2022: 0.08}
    syr = 2013
    p = Parameters(start_year=syr, budget_years=10, inflation_rates=irates)
    assert p._II_em[2013 - syr] == 3900
    # no reform
    # check implied inflation rate between 2020 and 2021
    grate = float(p._II_em[2021 - syr]) / float(p._II_em[2020 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2021 and 2022
    grate = float(p._II_em[2022 - syr]) / float(p._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)


def test_variable_inflation_rate_with_reform():
    irates = {2013: 0.04, 2014: 0.04, 2015: 0.04, 2016: 0.04, 2017: 0.04,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.04, 2022: 0.08}
    syr = 2013
    p = Parameters(start_year=syr, budget_years=10, inflation_rates=irates)
    assert p._II_em[2013 - syr] == 3900
    # implement reform in 2020 which is two years before the last year, 2022
    for year in range(0, 2020 - syr):
        p.increment_year()
    assert p.current_year == 2020
    reform = {2020: {"_II_em": [20000]}}
    p.update(reform)
    # check implied inflation rate between 2018 and 2019 (before the reform)
    grate = float(p._II_em[2019 - syr]) / float(p._II_em[2018 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2020 and 2021 (after then reform)
    grate = float(p._II_em[2021 - syr]) / float(p._II_em[2020 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2021 and 2022 (after then reform)
    grate = float(p._II_em[2022 - syr]) / float(p._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)


def test_create_parameters_from_file(paramsfile):
    p = Parameters.from_file(paramsfile.name)
    inf_rates = [Parameters.default_inflation_rate(p.start_year + i)
                 for i in range(0, p.budget_years)]
    assert_array_equal(p._almdep,
                       expand_array(np.array([7150, 7250, 7400]),
                                    inflate=True,
                                    inflation_rates=inf_rates,
                                    num_years=p.budget_years))
    assert_array_equal(p._almsep,
                       expand_array(np.array([40400, 41050]),
                                    inflate=True,
                                    inflation_rates=inf_rates,
                                    num_years=p.budget_years))
    assert_array_equal(p._rt5,
                       expand_array(np.array([0.33]),
                                    inflate=False,
                                    inflation_rates=inf_rates,
                                    num_years=p.budget_years))
    assert_array_equal(p._rt7,
                       expand_array(np.array([0.396]),
                                    inflate=False,
                                    inflation_rates=inf_rates,
                                    num_years=p.budget_years))


def test_parameters_get_default():
    paramdata = default_data()
    assert paramdata['_CDCC_ps'] == [15000]


def test_update_Parameters_raises_on_no_year(paramsfile):
    p = Parameters.from_file(paramsfile.name)
    user_mods = {"_STD_Aged": [[1400, 1200]]}
    with pytest.raises(ValueError):
        p.update(user_mods)


def test_update_Parameters_update_current_year():
    p = Parameters(start_year=2013)
    user_mods = {2013:
                 {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
    p.update(user_mods)
    assert_array_equal(p.STD_Aged,
                       np.array([1400, 1100, 1100, 1400, 1400, 1199]))


def test_update_Parameters_raises_on_future_year():
    p = Parameters(start_year=2013)
    with pytest.raises(ValueError):
        user_mods = {2015:
                     {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
        p.update(user_mods)


def test_update_Parameters_maintains_default_cpi_flags():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: {"_II_em": [4300]}}
    p.update(user_mods)
    # _II_em has a default cpi_flag of True, so by incrementing the year,
    # the current year value should increase, and therefore not be 4300
    p.increment_year()
    assert p.II_em != 4300


def test_update_Parameters_increment_until_mod_year():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015:
                 {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
    p.update(user_mods)
    assert_array_equal(p.STD_Aged,
                       np.array([1400, 1100, 1100, 1400, 1400, 1199]))


def test_increment_Parameters_increment_and_then_update():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: {"_II_em": [4400], "_II_em_cpi": True}}
    p.update(user_mods)
    assert_array_equal(p._II_em[:3], np.array([3900, 3950, 4400]))
    assert p.II_em == 4400


def test_parameters_get_default_start_year():
    paramdata = default_data(start_year=2015, metadata=True)
    # 1D data, has 2015 values
    meta_II_em = paramdata['_II_em']
    assert meta_II_em['start_year'] == 2015
    assert meta_II_em['row_label'] == ["2015"]
    assert meta_II_em['value'] == [4000]

    # 2D data, has 2015 values
    meta_std_aged = paramdata['_STD_Aged']
    assert meta_std_aged['start_year'] == 2015
    assert meta_std_aged['row_label'] == ["2015"]
    assert meta_std_aged['value'] == [[1550, 1250, 1250, 1550, 1550, 1250]]

    # 1D data, doesn't have 2015 values, is CPI inflated
    meta_amt_thd_marrieds = paramdata['_AMT_thd_MarriedS']
    assert meta_amt_thd_marrieds['start_year'] == 2015
    assert meta_amt_thd_marrieds['row_label'] == ["2015"]
    # multiply 2014 value by 2015 default inflation rate to get 2015 value
    v2014 = 41050
    v2015 = v2014 * (1.0 + Parameters.default_inflation_rate(2014))
    assert meta_amt_thd_marrieds['value'] == [v2015]

    # 1D data, doesn't have 2015 values, is not CPI inflated
    meta_kt_c_age = paramdata['_KT_c_Age']
    assert meta_kt_c_age['start_year'] == 2015
    assert meta_kt_c_age['row_label'] == ""
    assert meta_kt_c_age['value'] == [24]

    # 1D data, does have 2015 values, goes up to 2018
    meta_ctc_c = paramdata['_CTC_c']
    assert meta_ctc_c['start_year'] == 2015
    assert meta_ctc_c['row_label'] == ["2015", "2016", "2017", "2018"]
    assert meta_ctc_c['value'] == [1000, 1000, 1000, 500]
