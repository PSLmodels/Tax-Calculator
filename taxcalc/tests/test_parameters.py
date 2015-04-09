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

def test_update_Parameters_increment_until_mod_year():
    p = Parameters(start_year=2013)
    p.increment_year()
    p.increment_year()
    user_mods = {2015: { "_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]] }}
    p.update(user_mods)
    assert_array_equal(p.STD_Aged, np.array([1400, 1100, 1100, 1400, 1400, 1199]))


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


