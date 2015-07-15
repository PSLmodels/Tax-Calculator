import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
import tempfile
from numba import jit, vectorize, guvectorize
import taxcalc
from taxcalc import *
from taxcalc.utils import expand_array


@pytest.yield_fixture
def paramsfile():

    txt = """{"_almdep": {"value": [7150, 7250, 7400],
                          "cpi_inflated": true},

             "_almsep": {"value": [40400, 41050],
                         "cpi_inflated": true},

             "_rt5": {"value": [0.33 ],
                      "cpi_inflated": false},

             "_rt7": {"value": [0.396],
                      "cpi_inflated": false}}"""

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(txt + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_create_parameters():
    p = Parameters()
    assert p


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
    for yr in range(0, 8):
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
    assert round(grate, 3) == round(0.08, 3)
    # Note: above assert shows that inflation indexing of policy parameters
    # works like this:  param(t) = param(t-1) * ( 1 + inflation_rate(t) ).


def test_variable_inflation_rate_with_reform():
    irates = {2013: 0.04, 2014: 0.04, 2015: 0.04, 2016: 0.04, 2017: 0.04,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.04, 2022: 0.08}
    syr = 2013
    p = Parameters(start_year=syr, budget_years=10, inflation_rates=irates)
    assert p._II_em[2013 - syr] == 3900
    # implement reform in 2020 which is two years before the last year, 2022
    for yr in range(0, 2020 - syr):
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
    assert round(grate, 3) == round(0.08, 3)


def test_create_parameters_from_file(paramsfile):
    p = Parameters.from_file(paramsfile.name)
    irates = Parameters._Parameters__rates
    inf_rates = [irates[2013 + i] for i in range(0, 12)]

    assert_array_equal(p._almdep,
                       expand_array(np.array([7150, 7250, 7400]), inflate=True,
                                    inflation_rates=inf_rates, num_years=12))
    assert_array_equal(p._almsep,
                       expand_array(np.array([40400, 41050]), inflate=True,
                                    inflation_rates=inf_rates, num_years=12))
    assert_array_equal(p._rt5,
                       expand_array(np.array([0.33]), inflate=False,
                                    inflation_rates=inf_rates, num_years=12))
    assert_array_equal(p._rt7,
                       expand_array(np.array([0.396]), inflate=False,
                                    inflation_rates=inf_rates, num_years=12))


def test_parameters_get_default(paramsfile):
    paramdata = taxcalc.parameters.default_data()
    assert paramdata['_CDCC_ps'] == [15000]


def test_update_Parameters_raises_on_no_year(paramsfile):
    p = Parameters.from_file(paramsfile.name)
    user_mods = { "_STD_Aged": [[1400, 1200]] }
    with pytest.raises(ValueError):
        p.update(user_mods)


def test_update_Parameters_update_current_year():
    p = Parameters(start_year=2013)
    user_mods = {2013: { "_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]] }}
    p.update(user_mods)
    assert_array_equal(p.STD_Aged, np.array([1400, 1100, 1100, 1400, 1400, 1199]))


def test_update_Parameters_raises_on_future_year():
    p = Parameters(start_year=2013)
    with pytest.raises(ValueError):
        user_mods = {2015: { "_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]] }}
        p.update(user_mods)

def test_update_Parameters_maintains_default_cpi_flags():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: { "_II_em": [4300]}}
    p.update(user_mods)
    #_II_em has a default cpi_flag of True, so by incrementing the year,
    #the current year value should increase, and therefore not be 4300
    p.increment_year()
    assert p.II_em != 4300


def test_update_Parameters_increment_until_mod_year():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: { "_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]] }}
    p.update(user_mods)
    assert_array_equal(p.STD_Aged, np.array([1400, 1100, 1100, 1400, 1400, 1199]))

def test_increment_Parameters_increment_and_then_update():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: { "_II_em": [4400], "_II_em_cpi": True}}
    p.update(user_mods)
    assert_array_equal(p._II_em[:3], np.array([3900, 3950, 4400]))
    assert p.II_em == 4400

def test_parameters_get_default_start_year():
    paramdata = taxcalc.parameters.default_data(start_year=2015, metadata=True)
    #1D data, has 2015 values
    meta_II_em = paramdata['_II_em']
    assert meta_II_em['start_year'] == 2015
    assert meta_II_em['row_label'] == ["2015"]
    assert meta_II_em['value'] == [4000]

    #2D data, has 2015 values
    meta_std_aged = paramdata['_STD_Aged']
    assert meta_std_aged['start_year'] == 2015
    assert meta_std_aged['row_label'] == ["2015"]
    assert meta_std_aged['value'] == [[1550, 1250, 1250, 1550, 1550, 1250]]

    #1D data, doesn't have 2015 values, is CPI inflated
    meta_amt_thd_marrieds = paramdata['_AMT_thd_MarriedS']
    assert meta_amt_thd_marrieds['start_year'] == 2015
    assert meta_amt_thd_marrieds['row_label'] == ["2015"]
    #Take the 2014 rate and multiply by inflation for that year
    assert meta_amt_thd_marrieds['value'] == [41050 * (1.0 + Parameters._Parameters__rates[2014])]

    #1D data, doesn't have 2015 values, is not CPI inflated
    meta_kt_c_age = paramdata['_KT_c_Age']
    assert meta_kt_c_age['start_year'] == 2015
    assert meta_kt_c_age['row_label'] == ""
    assert meta_kt_c_age['value'] == [24]

    #1D data, does have 2015 values, goes up to 2018
    meta_ctc_c = paramdata['_CTC_c']
    assert meta_ctc_c['start_year'] == 2015
    assert meta_ctc_c['row_label'] == ["2015", "2016", "2017", "2018"]
    assert meta_ctc_c['value'] == [1000, 1000, 1000, 500]


