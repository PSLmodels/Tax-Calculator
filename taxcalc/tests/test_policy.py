import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import json
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
import tempfile
from numba import jit, vectorize, guvectorize
import taxcalc
from taxcalc import *


@pytest.yield_fixture
def policyfile():

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
    p = Policy()
    assert p


def test_policy_json_content():
    ppo = Policy()
    policy = getattr(ppo, '_vals')
    for name, data in policy.items():
        start_year = data.get('start_year')
        assert isinstance(start_year, int)
        assert start_year == Policy.JSON_START_YEAR
        row_label = data.get('row_label')
        assert isinstance(row_label, list)
        value = data.get('value')
        expected_row_label = [str(start_year + i) for i in range(len(value))]
        assert row_label == expected_row_label


def test_constant_inflation_rate_without_reform():
    syr = 2013
    nyrs = 10
    irate = 0.08
    irates = {(syr + i): irate for i in range(0, nyrs)}
    ppo = Policy(start_year=syr, num_years=nyrs, inflation_rates=irates)
    assert ppo._II_em[2013 - syr] == 3900
    # no reform
    # check implied inflation rate at end of years
    grate = float(ppo._II_em[2022 - syr]) / float(ppo._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)


def test_constant_inflation_rate_with_reform():
    syr = 2013
    nyrs = 10
    irate = 0.08
    irates = {(syr + i): irate for i in range(0, nyrs)}
    ppo = Policy(start_year=syr, num_years=nyrs, inflation_rates=irates)
    # implement reform in 2021 which is the year before the last year = 2022
    reform = {2021: {"_II_em": [20000]}}
    ppo.implement_reform(reform)
    # check implied inflation rate just before reform
    grate = float(ppo._II_em[2020 - syr]) / float(ppo._II_em[2019 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)
    # check implied inflation rate just after reform
    grate = float(ppo._II_em[2022 - syr]) / float(ppo._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(irate, 3)


def test_variable_inflation_rate_without_reform():
    syr = 2013
    irates = {2013: 0.04, 2014: 0.04, 2015: 0.04, 2016: 0.04, 2017: 0.04,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.08, 2022: 0.08}
    ppo = Policy(start_year=syr, num_years=10, inflation_rates=irates)
    assert ppo._II_em[2013 - syr] == 3900
    # no reform
    # check implied inflation rate between 2020 and 2021
    grate = float(ppo._II_em[2021 - syr]) / float(ppo._II_em[2020 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2021 and 2022
    grate = float(ppo._II_em[2022 - syr]) / float(ppo._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(0.08, 3)


def test_variable_inflation_rate_with_reform():
    syr = 2013
    irates = {2013: 0.04, 2014: 0.04, 2015: 0.04, 2016: 0.04, 2017: 0.04,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.08, 2022: 0.08}
    ppo = Policy(start_year=syr, num_years=10, inflation_rates=irates)
    assert ppo._II_em[2013 - syr] == 3900
    # implement reform in 2020 which is two years before the last year, 2022
    reform = {2020: {"_II_em": [20000]}}
    ppo.implement_reform(reform)
    ppo.set_year(2020)
    assert ppo.current_year == 2020
    # check implied inflation rate between 2018 and 2019 (before the reform)
    grate = float(ppo._II_em[2019 - syr]) / float(ppo._II_em[2018 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2020 and 2021 (after the reform)
    grate = float(ppo._II_em[2021 - syr]) / float(ppo._II_em[2020 - syr]) - 1.0
    assert round(grate, 3) == round(0.04, 3)
    # check implied inflation rate between 2021 and 2022 (after the reform)
    grate = float(ppo._II_em[2022 - syr]) / float(ppo._II_em[2021 - syr]) - 1.0
    assert round(grate, 3) == round(0.08, 3)


def test_multi_year_reform():
    """
    Test multi-year reform involving 1D and 2D parameters.
    """
    # specify dimensions of policy Policy object
    syr = 2013
    nyrs = 10

    # specify assumed inflation rates
    irates = {2013: 0.02, 2014: 0.02, 2015: 0.02, 2016: 0.03, 2017: 0.03,
              2018: 0.04, 2019: 0.04, 2020: 0.04, 2021: 0.04, 2022: 0.04}
    ifactor = {}
    for i in range(0, nyrs):
        ifactor[syr + i] = 1.0 + irates[syr + i]
    iratelist = [irates[syr + i] for i in range(0, nyrs)]

    # specify assumed inflation rates
    wrates = {2013: 0.0276, 2014: 0.0419, 2015: 0.0465, 2016: 0.0498,
              2017: 0.0507, 2018: 0.0481, 2019: 0.0451, 2020: 0.0441,
              2021: 0.0437, 2022: 0.0435}
    wfactor = {}
    for i in range(0, nyrs):
        wfactor[syr + i] = 1.0 + wrates[syr + i]
    wratelist = [wrates[syr + i] for i in range(0, nyrs)]

    # instantiate policy Policy object
    ppo = Policy(start_year=syr, num_years=nyrs, inflation_rates=irates,
                 wage_growth_rates=wrates)

    # confirm that parameters have current-law values
    assert_array_equal(getattr(ppo, '_AMT_thd_MarriedS'),
                       Policy.expand_array(np.array([40400, 41050]),
                                           inflate=True,
                                           inflation_rates=iratelist,
                                           num_years=nyrs))
    assert_array_equal(getattr(ppo, '_EITC_c'),
                       Policy.expand_array(np.array([[487, 3250, 5372, 6044],
                                                     [496, 3305, 5460, 6143],
                                                     [503, 3359, 5548, 6242],
                                                     [506, 3373, 5572, 6269]]),
                                           inflate=True,
                                           inflation_rates=iratelist,
                                           num_years=nyrs))
    assert_array_equal(getattr(ppo, '_II_em'),
                       Policy.expand_array(np.array([3900, 3950, 4000, 4050]),
                                           inflate=True,
                                           inflation_rates=iratelist,
                                           num_years=nyrs))
    assert_array_equal(getattr(ppo, '_CTC_c'),
                       Policy.expand_array(np.array([1000]),
                                           inflate=False,
                                           inflation_rates=iratelist,
                                           num_years=nyrs))

    # this parameter uses a different inflating rate
    assert_array_equal(getattr(ppo, '_SS_Earnings_c'),
                       Policy.expand_array(np.array([113700, 117000,
                                                     118500, 118500]),
                                           inflate=True,
                                           inflation_rates=wratelist,
                                           num_years=nyrs))

    # specify multi-year reform using a dictionary of year_provisions dicts
    reform = {
        2015: {
            '_AMT_thd_MarriedS': [60000],
            '_CTC_c': [2000]
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

    # implement multi-year reform
    ppo.implement_reform(reform)
    assert ppo.current_year == syr

    # move policy Policy object forward in time so current_year is syr+2
    #   Note: this would be typical usage because the first budget year
    #         is greater than Policy start_year.
    ppo.set_year(ppo.start_year + 2)
    assert ppo.current_year == syr + 2

    # confirm that actual parameters have expected post-reform values
    check_amt_thd_marrieds(ppo, reform, ifactor)
    check_eitc_c(ppo, reform, ifactor)
    check_ii_em(ppo, reform, ifactor)
    check_ss_earnings_c(ppo, reform, wfactor)
    check_ctc_c(ppo, reform)

    # end of test_multi_year_reform with the check_* functions below:


def check_ctc_c(ppo, reform):
    """
    Compare actual and expected _CTC_c parameter values
    generated by the test_multi_year_reform() function above.
    Ensure that future-year values in current_law_policy.json
    are overwritten by reform.
    """
    actual = {}
    arr = getattr(ppo, '_CTC_c')
    for i in range(0, ppo.num_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 1000
    assert actual[2014] == 1000
    e2015 = reform[2015]['_CTC_c'][0]
    assert actual[2015] == e2015
    e2016 = actual[2015]
    assert actual[2016] == e2016
    e2017 = actual[2016]
    assert actual[2017] == e2017
    e2018 = actual[2017]
    assert actual[2018] == e2018
    e2019 = actual[2018]
    assert actual[2019] == e2019


def check_amt_thd_marrieds(ppo, reform, ifactor):
    """
    Compare actual and expected _AMT_thd_MarriedS parameter values
    generated by the test_multi_year_reform() function above.
    """
    actual = {}
    arr = getattr(ppo, '_AMT_thd_MarriedS')
    for i in range(0, ppo.num_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 40400
    assert actual[2014] == 41050
    e2015 = reform[2015]['_AMT_thd_MarriedS'][0]
    assert actual[2015] == e2015
    e2016 = int(round(ifactor[2015] * actual[2015]))
    assert actual[2016] == e2016
    e2017 = reform[2017]['_AMT_thd_MarriedS'][0]
    assert actual[2017] == e2017
    e2018 = int(round(ifactor[2017] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = int(round(ifactor[2018] * actual[2018]))
    assert actual[2019] == e2019
    e2020 = int(round(ifactor[2019] * actual[2019]))
    absdiff = abs(actual[2020] - e2020)
    if absdiff <= 1:
        pass  # ignore one dollar rounding error
    else:
        assert actual[2020] == e2020
    e2021 = int(round(ifactor[2020] * actual[2020]))
    absdiff = abs(actual[2021] - e2021)
    if absdiff <= 1:
        pass  # ignore one dollar rounding error
    else:
        assert actual[2021] == e2021
    e2022 = int(round(ifactor[2021] * actual[2021]))
    assert actual[2022] == e2022


def check_eitc_c(ppo, reform, ifactor):
    """
    Compare actual and expected _EITC_c parameter values
    generated by the test_multi_year_reform() function above.
    """
    actual = {}
    arr = getattr(ppo, '_EITC_c')
    alen = len(arr[0])
    for i in range(0, ppo.num_years):
        actual[ppo.start_year + i] = arr[i]
    assert_array_equal(actual[2013], [487, 3250, 5372, 6044])
    assert_array_equal(actual[2014], [496, 3305, 5460, 6143])
    assert_array_equal(actual[2015], [503, 3359, 5548, 6242])
    e2016 = reform[2016]['_EITC_c'][0]
    assert_array_equal(actual[2016], e2016)
    e2017 = [int(round(ifactor[2016] * actual[2016][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2017], e2017)
    e2018 = [int(round(ifactor[2017] * actual[2017][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2018], e2018, rtol=0.0, atol=1.0)
    e2019 = reform[2019]['_EITC_c'][0]
    assert_array_equal(actual[2019], e2019)
    e2020 = [int(round(ifactor[2019] * actual[2019][j]))
             for j in range(0, alen)]
    assert_array_equal(actual[2020], e2020)
    e2021 = [int(round(ifactor[2020] * actual[2020][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2021], e2021, rtol=0.0, atol=1.0)
    e2022 = [int(round(ifactor[2021] * actual[2021][j]))
             for j in range(0, alen)]
    assert np.allclose(actual[2022], e2022, rtol=0.0, atol=1.0)


def check_ii_em(ppo, reform, ifactor):
    """
    Compare actual and expected _II_em parameter values
    generated by the test_multi_year_reform() function above.
    """
    actual = {}
    arr = getattr(ppo, '_II_em')
    for i in range(0, ppo.num_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 3900
    assert actual[2014] == 3950
    assert actual[2015] == 4000
    e2016 = reform[2016]['_II_em'][0]
    assert actual[2016] == e2016
    e2017 = int(round(ifactor[2016] * actual[2016]))
    assert actual[2017] == e2017
    e2018 = int(round(ifactor[2017] * actual[2017]))
    assert actual[2018] == e2018
    e2019 = reform[2019]['_II_em'][0]
    assert actual[2019] == e2019
    e2020 = int(round(ifactor[2019] * actual[2019]))
    assert actual[2020] == e2020
    e2021 = int(round(ifactor[2020] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(ifactor[2021] * actual[2021]))
    assert actual[2022] == e2022


def check_ss_earnings_c(ppo, reform, wfactor):
    """
    Compare actual and expected _SS_Earnings_c parameter values
    generated by the test_multi_year_reform() function above.
    """
    actual = {}
    arr = getattr(ppo, '_SS_Earnings_c')
    for i in range(0, ppo.num_years):
        actual[ppo.start_year + i] = arr[i]
    assert actual[2013] == 113700
    assert actual[2014] == 117000
    assert actual[2015] == 118500
    e2016 = reform[2016]['_SS_Earnings_c'][0]
    assert actual[2016] == e2016
    e2017 = reform[2017]['_SS_Earnings_c'][0]
    assert actual[2017] == e2017
    e2018 = actual[2017]  # no indexing after 2017
    assert actual[2018] == e2018
    e2019 = reform[2019]['_SS_Earnings_c'][0]
    assert actual[2019] == e2019
    e2020 = int(round(wfactor[2019] * actual[2019]))  # indexing after 2019
    assert actual[2020] == e2020
    e2021 = int(round(wfactor[2020] * actual[2020]))
    assert actual[2021] == e2021
    e2022 = int(round(wfactor[2021] * actual[2021]))
    absdiff = abs(actual[2022] - e2022)
    if absdiff <= 1:
        pass  # ignore one dollar rounding error
    else:
        assert actual[2022] == e2022


def test_create_parameters_from_file(policyfile):
    with open(policyfile.name) as pfile:
        policy = json.load(pfile)
    ppo = Policy(parameter_dict=policy)
    irates = Policy.default_inflation_rates()
    inf_rates = [irates[ppo.start_year + i] for i in range(0, ppo.num_years)]

    assert_array_equal(ppo._almdep,
                       Policy.expand_array(np.array([7150, 7250, 7400]),
                                           inflate=True,
                                           inflation_rates=inf_rates,
                                           num_years=ppo.num_years))
    assert_array_equal(ppo._almsep,
                       Policy.expand_array(np.array([40400, 41050]),
                                           inflate=True,
                                           inflation_rates=inf_rates,
                                           num_years=ppo.num_years))
    assert_array_equal(ppo._rt5,
                       Policy.expand_array(np.array([0.33]),
                                           inflate=False,
                                           inflation_rates=inf_rates,
                                           num_years=ppo.num_years))
    assert_array_equal(ppo._rt7,
                       Policy.expand_array(np.array([0.396]),
                                           inflate=False,
                                           inflation_rates=inf_rates,
                                           num_years=ppo.num_years))


def test_parameters_get_default():
    paramdata = Policy.default_data()
    assert paramdata['_CDCC_ps'] == [15000]


def test_implement_reform_Policy_raises_on_no_year():
    reform = {"_STD_Aged": [[1400, 1200]]}
    ppo = Policy()
    with pytest.raises(ValueError):
        ppo.implement_reform(reform)


def test_Policy_reform_in_start_year():
    ppo = Policy(start_year=2013)
    reform = {2013: {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
    ppo.implement_reform(reform)
    assert_array_equal(ppo.STD_Aged,
                       np.array([1400, 1100, 1100, 1400, 1400, 1199]))


def test_implement_reform_Policy_raises_on_future_year():
    ppo = Policy(start_year=2013)
    with pytest.raises(ValueError):
        reform = {2010: {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
        ppo.implement_reform(reform)


def test_Policy_reform_with_default_cpi_flags():
    ppo = Policy(start_year=2013)
    reform = {2015: {"_II_em": [4300]}}
    ppo.implement_reform(reform)
    # '_II_em' has a default cpi_flag of True, so
    # in 2016 its value should be greater than 4300
    ppo.set_year(2016)
    assert ppo.II_em > 4300


def test_Policy_reform_after_start_year():
    ppo = Policy(start_year=2013)
    reform = {2015: {"_STD_Aged": [[1400, 1100, 1100, 1400, 1400, 1199]]}}
    ppo.implement_reform(reform)
    ppo.set_year(2015)
    assert_array_equal(ppo.STD_Aged,
                       np.array([1400, 1100, 1100, 1400, 1400, 1199]))


def test_Policy_reform_makes_no_changes_before_year():
    ppo = Policy(start_year=2013)
    reform = {2015: {"_II_em": [4400], "_II_em_cpi": True}}
    ppo.implement_reform(reform)
    ppo.set_year(2015)
    assert_array_equal(ppo._II_em[:3], np.array([3900, 3950, 4400]))
    assert ppo.II_em == 4400


def test_parameters_get_default_start_year():
    paramdata = Policy.default_data(metadata=True, start_year=2015)

    # 1D data, has 2015 values
    meta_II_em = paramdata['_II_em']
    assert meta_II_em['start_year'] == 2015
    assert meta_II_em['row_label'] == ["2015", "2016"]
    assert meta_II_em['value'] == [4000, 4050]

    # 2D data, has 2015 values
    meta_std_aged = paramdata['_STD_Aged']
    assert meta_std_aged['start_year'] == 2015
    assert meta_std_aged['row_label'] == ["2015", "2016"]
    assert meta_std_aged['value'] == [[1550, 1250, 1250, 1550, 1550, 1250],
                                      [1550, 1250, 1250, 1550, 1550, 1250]]

    # 1D data, doesn't have 2015 values, is CPI inflated
    meta_amt_thd_marrieds = paramdata['_AMT_thd_MarriedS']
    assert meta_amt_thd_marrieds['start_year'] == 2015
    assert meta_amt_thd_marrieds['row_label'] == ["2015"]
    # Take the 2014 parameter value and multiply by inflation for that year
    should_be = [int(41050 * (1 + Policy.default_inflation_rates()[2014]))]
    assert meta_amt_thd_marrieds['value'] == should_be

    # 1D data, doesn't have 2015 values, is not CPI inflated
    meta_kt_c_age = paramdata['_KT_c_Age']
    assert meta_kt_c_age['start_year'] == 2015
    assert meta_kt_c_age['row_label'] == ["2015"]
    assert meta_kt_c_age['value'] == [24]


REFORM_CONTENTS = """
// Example of a reform file suitable for Policy read_json_reform_file function.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// The primary keys are policy parameters and secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
    "_AMT_tthd": // AMT taxinc threshold separating the two AMT tax brackets
    {"2015": [200000],
     "2017": [300000]
    },
    "_EITC_c": // maximum EITC amount by number of qualifying kids (0,1,2,3+)
    {"2016": [[ 900, 5000,  8000,  9000]],
     "2019": [[1200, 7000, 10000, 12000]]
    },
    "_II_em": // personal exemption amount (see indexing changes below)
    {"2016": [6000],
     "2018": [7500],
     "2020": [9000]
    },
    "_II_em_cpi": // personal exemption amount indexing status
    {"2016": false, // values in future years are same as this year value
     "2018": true   // values in future years indexed with this year as base
    },
    "_SS_Earnings_c": // social security (OASDI) maximum taxable earnings
    {"2016": [300000],
     "2018": [500000],
     "2020": [700000]
    },
    "_AMT_em_cpi": // AMT exemption amount indexing status
    {"2017": false, // values in future years are same as this year value
     "2020": true   // values in future years indexed with this year as base
    }
}
"""


@pytest.yield_fixture
def reform_file():
    """
    Temporary reform file for Policy read_json_reform_file function.
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_read_json_reform_file_and_implement_reform_a(reform_file):
    """
    Test reading and translation of reform file into a reform dictionary
    that is then used to call implement_reform method.
    NOTE: implement_reform called when policy.current_year == policy.start_year
    """
    reform = Policy.read_json_reform_file(reform_file.name)
    policy = Policy()
    policy.implement_reform(reform)
    syr = policy.start_year
    amt_tthd = policy._AMT_tthd
    assert amt_tthd[2015 - syr] == 200000
    assert amt_tthd[2016 - syr] > 200000
    assert amt_tthd[2017 - syr] == 300000
    assert amt_tthd[2018 - syr] > 300000
    ii_em = policy._II_em
    assert ii_em[2016 - syr] == 6000
    assert ii_em[2017 - syr] == 6000
    assert ii_em[2018 - syr] == 7500
    assert ii_em[2019 - syr] > 7500
    assert ii_em[2020 - syr] == 9000
    assert ii_em[2021 - syr] > 9000
    amt_em = policy._AMT_em
    assert amt_em[2016 - syr, 0] > amt_em[2015 - syr, 0]
    assert amt_em[2017 - syr, 0] > amt_em[2016 - syr, 0]
    assert amt_em[2018 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2019 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2020 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2021 - syr, 0] > amt_em[2020 - syr, 0]
    assert amt_em[2022 - syr, 0] > amt_em[2021 - syr, 0]


def test_read_json_reform_file_and_implement_reform_b(reform_file):
    """
    Test reading and translation of reform file into a reform dictionary
    that is then used to call implement_reform method.
    NOTE: implement_reform called when policy.current_year > policy.start_year
    """
    reform = Policy.read_json_reform_file(reform_file.name)
    policy = Policy()
    policy.set_year(2015)  # the only difference between this and prior test
    policy.implement_reform(reform)
    syr = policy.start_year
    amt_tthd = policy._AMT_tthd
    assert amt_tthd[2015 - syr] == 200000
    assert amt_tthd[2016 - syr] > 200000
    assert amt_tthd[2017 - syr] == 300000
    assert amt_tthd[2018 - syr] > 300000
    ii_em = policy._II_em
    assert ii_em[2016 - syr] == 6000
    assert ii_em[2017 - syr] == 6000
    assert ii_em[2018 - syr] == 7500
    assert ii_em[2019 - syr] > 7500
    assert ii_em[2020 - syr] == 9000
    assert ii_em[2021 - syr] > 9000
    amt_em = policy._AMT_em
    assert amt_em[2016 - syr, 0] > amt_em[2015 - syr, 0]
    assert amt_em[2017 - syr, 0] > amt_em[2016 - syr, 0]
    assert amt_em[2018 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2019 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2020 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2021 - syr, 0] > amt_em[2020 - syr, 0]
    assert amt_em[2022 - syr, 0] > amt_em[2021 - syr, 0]
