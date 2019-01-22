# CODING-STYLE CHECKS:
# pycodestyle test_policy.py

import os
import sys
import json
import tempfile
import numpy as np
import pytest
from taxcalc import Policy, Calculator


def test_incorrect_Policy_instantiation():
    with pytest.raises(ValueError):
        Policy(gfactors=list())


def test_correct_Policy_instantiation():
    pol = Policy()
    assert pol
    pol.implement_reform({})
    with pytest.raises(ValueError):
        pol.implement_reform(list())
    with pytest.raises(ValueError):
        pol.implement_reform({2099: {'_II_em': [99000]}})
    pol.set_year(2019)
    with pytest.raises(ValueError):
        pol.implement_reform({2018: {'_II_em': [99000]}})
    with pytest.raises(ValueError):
        pol.implement_reform({2020: {'_II_em': [-1000]}})


def test_policy_json_content():
    ppo = Policy()
    policy = getattr(ppo, '_vals')
    for _, data in policy.items():
        start_year = data.get('start_year')
        assert isinstance(start_year, int)
        assert start_year == Policy.JSON_START_YEAR
        row_label = data.get('row_label')
        assert isinstance(row_label, list)
        value = data.get('value')
        expected_row_label = [str(start_year + i) for i in range(len(value))]
        if row_label != expected_row_label:
            msg = 'name,row_label,expected_row_label: {}\n{}\n{}'
            raise ValueError(msg.format(data.get('long_name')), row_label,
                             expected_row_label)


def test_constant_inflation_rate_with_reform():
    pol = Policy()
    # implement reform in year before final year
    fyr = Policy.LAST_BUDGET_YEAR
    ryr = fyr - 1
    reform = {
        (ryr - 3): {'_II_em': [1000]},  # to avoid divide-by-zero under TCJA
        ryr: {'_II_em': [20000]}
    }
    pol.implement_reform(reform)
    # extract price inflation rates
    pirates = pol.inflation_rates()
    syr = Policy.JSON_START_YEAR
    irate_b = pirates[ryr - 2 - syr]
    irate_a = pirates[ryr - syr]
    # check implied inflation rate just before reform
    grate = float(pol._II_em[ryr - 1 - syr]) / float(pol._II_em[ryr - 2 - syr])
    assert round(grate - 1.0, 4) == round(irate_b, 4)
    # check implied inflation rate just after reform
    grate = float(pol._II_em[ryr + 1 - syr]) / float(pol._II_em[ryr - syr])
    assert round(grate - 1.0, 6) == round(irate_a, 6)


def test_variable_inflation_rate_with_reform():
    pol = Policy()
    syr = Policy.JSON_START_YEAR
    assert pol._II_em[2013 - syr] == 3900
    # implement reform in 2020 which is two years before the last year, 2022
    reform = {
        2018: {'_II_em': [1000]},  # to avoid divide-by-zero under TCJA
        2020: {'_II_em': [20000]}
    }
    pol.implement_reform(reform)
    pol.set_year(2020)
    assert pol.current_year == 2020
    # extract price inflation rates
    pirates = pol.inflation_rates()
    irate2018 = pirates[2018 - syr]
    irate2020 = pirates[2020 - syr]
    irate2021 = pirates[2021 - syr]
    # check implied inflation rate between 2018 and 2019 (before the reform)
    grate = float(pol._II_em[2019 - syr]) / float(pol._II_em[2018 - syr])
    assert round(grate - 1.0, 5) == round(irate2018, 5)
    # check implied inflation rate between 2020 and 2021 (after the reform)
    grate = float(pol._II_em[2021 - syr]) / float(pol._II_em[2020 - syr])
    assert round(grate - 1.0, 5) == round(irate2020, 5)
    # check implied inflation rate between 2021 and 2022 (after the reform)
    grate = float(pol._II_em[2022 - syr]) / float(pol._II_em[2021 - syr])
    assert round(grate - 1.0, 5) == round(irate2021, 5)


def test_multi_year_reform():
    """
    Test multi-year reform involving 1D and 2D parameters.
    """
    # specify dimensions of policy Policy object
    syr = Policy.JSON_START_YEAR
    nyrs = Policy.DEFAULT_NUM_YEARS
    pol = Policy()
    iratelist = pol.inflation_rates()
    ifactor = {}
    for i in range(0, nyrs):
        ifactor[syr + i] = 1.0 + iratelist[i]
    wratelist = pol.wage_growth_rates()
    wfactor = {}
    for i in range(0, nyrs):
        wfactor[syr + i] = 1.0 + wratelist[i]
    # confirm that parameters have current-law values
    assert np.allclose(getattr(pol, '_EITC_c'),
                       Policy._expand_array(
                           np.array([[487, 3250, 5372, 6044],
                                     [496, 3305, 5460, 6143],
                                     [503, 3359, 5548, 6242],
                                     [506, 3373, 5572, 6269],
                                     [510, 3400, 5616, 6318]],
                                    dtype=np.float64),
                           False, False,
                           inflate=True,
                           inflation_rates=iratelist,
                           num_years=nyrs),
                       atol=0.01, rtol=0.0)
    assert np.allclose(getattr(pol, '_STD_Dep'),
                       Policy._expand_array(
                           np.array([1000, 1000, 1050, 1050, 1050],
                                    dtype=np.float64),
                           False, False,
                           inflate=True,
                           inflation_rates=iratelist,
                           num_years=nyrs),
                       atol=0.01, rtol=0.0)
    assert np.allclose(getattr(pol, '_CTC_c'),
                       Policy._expand_array(
                           np.array([1000] * 5 + [1400] * 4 +
                                    [1500] * 3 + [1600] + [1000],
                                    dtype=np.float64),
                           False, False,
                           inflate=False,
                           inflation_rates=iratelist,
                           num_years=nyrs),
                       atol=0.01, rtol=0.0)
    # this parameter uses a different indexing rate
    assert np.allclose(getattr(pol, '_SS_Earnings_c'),
                       Policy._expand_array(
                           np.array([113700, 117000, 118500, 118500, 127200,
                                     128400, 132900],
                                    dtype=np.float64),
                           False, False,
                           inflate=True,
                           inflation_rates=wratelist,
                           num_years=nyrs),
                       atol=0.01, rtol=0.0)
    # specify multi-year reform using a dictionary of year_provisions dicts
    reform = {
        2015: {
            '_CTC_c': [2000]
        },
        2016: {
            '_EITC_c': [[900, 5000, 8000, 9000]],
            '_II_em': [7000],
            '_SS_Earnings_c': [300000]
        },
        2017: {
            '_SS_Earnings_c': [500000], '_SS_Earnings_c_cpi': False
        },
        2019: {
            '_EITC_c': [[1200, 7000, 10000, 12000]],
            '_II_em': [9000],
            '_SS_Earnings_c': [700000], '_SS_Earnings_c_cpi': True
        }
    }
    # implement multi-year reform
    pol.implement_reform(reform)
    assert pol.current_year == syr
    # move policy Policy object forward in time so current_year is syr+2
    #   Note: this would be typical usage because the first budget year
    #         is greater than Policy start_year.
    pol.set_year(pol.start_year + 2)
    assert pol.current_year == syr + 2
    # confirm that actual parameters have expected post-reform values
    check_eitc_c(pol, reform, ifactor)
    check_ii_em(pol, reform, ifactor)
    check_ss_earnings_c(pol, reform, wfactor)
    check_ctc_c(pol, reform)
    # end of test_multi_year_reform with the check_* functions below:


def check_ctc_c(ppo, reform):
    """
    Compare actual and expected _CTC_c parameter values
    generated by the test_multi_year_reform() function above.
    Ensure that future-year values in policy_current_law.json
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
    assert np.allclose(actual[2013], [487, 3250, 5372, 6044],
                       atol=0.01, rtol=0.0)
    assert np.allclose(actual[2014], [496, 3305, 5460, 6143],
                       atol=0.01, rtol=0.0)
    assert np.allclose(actual[2015], [503, 3359, 5548, 6242],
                       atol=0.01, rtol=0.0)
    e2016 = reform[2016]['_EITC_c'][0]
    assert np.allclose(actual[2016], e2016, atol=0.01, rtol=0.0)
    e2017 = [ifactor[2016] * actual[2016][j] for j in range(0, alen)]
    assert np.allclose(actual[2017], e2017, atol=0.01, rtol=0.0)
    e2018 = [ifactor[2017] * actual[2017][j] for j in range(0, alen)]
    assert np.allclose(actual[2018], e2018, atol=0.01, rtol=0.0)
    e2019 = reform[2019]['_EITC_c'][0]
    assert np.allclose(actual[2019], e2019, atol=0.01, rtol=0.0)
    e2020 = [ifactor[2019] * actual[2019][j] for j in range(0, alen)]
    assert np.allclose(actual[2020], e2020, atol=0.01, rtol=0.0)
    e2021 = [ifactor[2020] * actual[2020][j] for j in range(0, alen)]
    assert np.allclose(actual[2021], e2021, atol=0.01, rtol=0.0)
    e2022 = [ifactor[2021] * actual[2021][j] for j in range(0, alen)]
    assert np.allclose(actual[2022], e2022, atol=0.01, rtol=0.0)


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
    e2017 = ifactor[2016] * actual[2016]
    assert np.allclose([actual[2017]], [e2017], atol=0.01, rtol=0.0)
    e2018 = ifactor[2017] * actual[2017]
    assert np.allclose([actual[2018]], [e2018], atol=0.01, rtol=0.0)
    e2019 = reform[2019]['_II_em'][0]
    assert actual[2019] == e2019
    e2020 = ifactor[2019] * actual[2019]
    assert np.allclose([actual[2020]], [e2020], atol=0.01, rtol=0.0)
    e2021 = ifactor[2020] * actual[2020]
    assert np.allclose([actual[2021]], [e2021], atol=0.01, rtol=0.0)
    e2022 = ifactor[2021] * actual[2021]
    assert np.allclose([actual[2022]], [e2022], atol=0.01, rtol=0.0)


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
    e2020 = wfactor[2019] * actual[2019]  # indexing after 2019
    assert actual[2020] == e2020
    e2021 = wfactor[2020] * actual[2020]
    assert np.allclose([actual[2021]], [e2021], atol=0.01, rtol=0.0)
    e2022 = wfactor[2021] * actual[2021]
    assert np.allclose([actual[2022]], [e2022], atol=0.01, rtol=0.0)


@pytest.fixture(scope='module', name='defaultpolicyfile')
def fixture_defaultpolicyfile():
    # specify JSON text for alternative to policy_current_law.json file
    txt = """{"_almdep": {"value": [7150, 7250, 7400],
                          "cpi_inflated": true},
              "_cpi_offset": {"value": [0]},
              "_almsep": {"value": [40400, 41050],
                          "cpi_inflated": true},
              "_rt5": {"value": [0.33 ],
                       "cpi_inflated": false},
              "_rt7": {"value": [0.396],
                       "cpi_inflated": false}}"""
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as f:
        f.write(txt + '\n')
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_create_parameters_from_file(monkeypatch, defaultpolicyfile):
    # pytest monkeypatch sets the temporary file path as the default path;
    # after the test completes, monkeypatch restores the default settings.
    monkeypatch.setattr(Policy, 'DEFAULTS_FILENAME', defaultpolicyfile.name)
    ppo = Policy()
    inf_rates = ppo.inflation_rates()
    assert np.allclose(ppo._almdep,
                       Policy._expand_array(
                           np.array([7150, 7250, 7400],
                                    dtype=np.float64),
                           False, False,
                           inflate=True,
                           inflation_rates=inf_rates,
                           num_years=ppo.num_years),
                       atol=0.01, rtol=0.0)
    assert np.allclose(ppo._almsep,
                       Policy._expand_array(
                           np.array([40400, 41050],
                                    dtype=np.float64),
                           False, False,
                           inflate=True,
                           inflation_rates=inf_rates,
                           num_years=ppo.num_years),
                       atol=0.01, rtol=0.0)
    assert np.allclose(ppo._rt5,
                       Policy._expand_array(
                           np.array([0.33]),
                           False, False,
                           inflate=False,
                           inflation_rates=inf_rates,
                           num_years=ppo.num_years),
                       atol=0.01, rtol=0.0)
    assert np.allclose(ppo._rt7,
                       Policy._expand_array(
                           np.array([0.396]),
                           False, False,
                           inflate=False,
                           inflation_rates=inf_rates,
                           num_years=ppo.num_years),
                       atol=0.01, rtol=0.0)


def test_policy_metadata():
    clp = Policy()
    mdata = clp.metadata()
    assert mdata['_CDCC_ps']['value'] == [15000]


def test_implement_reform_Policy_raises_on_no_year():
    reform = {'_STD_Aged': [[1400, 1200]]}
    ppo = Policy()
    with pytest.raises(ValueError):
        ppo.implement_reform(reform)


def test_Policy_reform_in_start_year():
    ppo = Policy()
    reform = {2013: {'_STD': [[16000, 13000, 13000, 16000, 16000]]}}
    ppo.implement_reform(reform)
    assert np.allclose(ppo.STD,
                       np.array([16000, 13000, 13000, 16000, 16000]),
                       atol=0.01, rtol=0.0)


def test_implement_reform_Policy_raises_on_early_year():
    ppo = Policy()
    reform = {2010: {'_STD_Aged': [[1400, 1100, 1100, 1400, 1400]]}}
    with pytest.raises(ValueError):
        ppo.implement_reform(reform)


def test_Policy_reform_with_default_cpi_flags():
    ppo = Policy()
    reform = {2015: {'_II_em': [4300]}}
    ppo.implement_reform(reform)
    # '_II_em' has a default cpi_flag of True, so
    # in 2016 its value should be greater than 4300
    ppo.set_year(2016)
    assert ppo.II_em > 4300


def test_Policy_reform_after_start_year():
    ppo = Policy()
    reform = {2015: {'_STD_Aged': [[1400, 1100, 1100, 1400, 1400]]}}
    ppo.implement_reform(reform)
    ppo.set_year(2015)
    assert np.allclose(ppo.STD_Aged,
                       np.array([1400, 1100, 1100, 1400, 1400]),
                       atol=0.01, rtol=0.0)


def test_Policy_reform_makes_no_changes_before_year():
    ppo = Policy()
    reform = {2015: {'_II_em': [4400], '_II_em_cpi': True}}
    ppo.implement_reform(reform)
    ppo.set_year(2015)
    assert np.allclose(ppo._II_em[:3], np.array([3900, 3950, 4400]),
                       atol=0.01, rtol=0.0)
    assert ppo.II_em == 4400


REFORM_CONTENTS = """
// Example of reform file suitable for Calculator read_json_param_objects().
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// The primary keys are policy parameters and secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
// Parameter code in the policy object is enclosed inside a pair of double
// pipe characters (||).
{
"policy": {
    "_AMT_brk1": // top of first AMT tax bracket
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
}
"""


@pytest.fixture(scope='module', name='reform_file')
def fixture_reform_file():
    """
    Temporary reform file for Calculator read_json_param_objects() function.
    """
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as rfile:
        rfile.write(REFORM_CONTENTS)
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.mark.parametrize("set_year", [False, True])
def test_read_json_param_and_implement_reform(reform_file, set_year):
    """
    Test reading and translation of reform file into a reform dictionary
    that is then used to call implement_reform method.
    NOTE: implement_reform called when policy.current_year == policy.start_year
    """
    policy = Policy()
    if set_year:
        policy.set_year(2015)
    param_dict = Calculator.read_json_param_objects(reform_file.name, None)
    policy.implement_reform(param_dict['policy'])
    syr = policy.start_year
    amt_brk1 = policy._AMT_brk1
    assert amt_brk1[2015 - syr] == 200000
    assert amt_brk1[2016 - syr] > 200000
    assert amt_brk1[2017 - syr] == 300000
    assert amt_brk1[2018 - syr] > 300000
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
    add4aged = policy._ID_Medical_frt_add4aged
    assert add4aged[2015 - syr] == -0.025
    assert add4aged[2016 - syr] == -0.025
    assert add4aged[2017 - syr] == 0.0
    assert add4aged[2022 - syr] == 0.0


def test_pop_the_cap_reform():
    """
    Test eliminating the maximum taxable earnings (MTE)
    used in the calculation of the OASDI payroll tax.
    """
    # create Policy parameters object
    ppo = Policy()
    assert ppo.current_year == Policy.JSON_START_YEAR
    # confirm that MTE has current-law values in 2015 and 2016
    mte = ppo._SS_Earnings_c
    syr = Policy.JSON_START_YEAR
    assert mte[2015 - syr] == 118500
    assert mte[2016 - syr] == 118500
    # specify a "pop the cap" reform that eliminates MTE cap in 2016
    reform = {2016: {'_SS_Earnings_c': [9e99]}}
    ppo.implement_reform(reform)
    assert mte[2015 - syr] == 118500
    assert mte[2016 - syr] == 9e99
    assert mte[ppo.end_year - syr] == 9e99


def test_order_of_cpi_and_level_reforms():
    """
    Test that the order of the two reform provisions for the same parameter
    make no difference to the post-reform policy parameter values.
    """
    # specify two reforms that raises the MTE and stops its indexing in 2015
    reform = [{2015: {'_SS_Earnings_c': [500000],
                      '_SS_Earnings_c_cpi': False}},
              # now reverse the order of the two reform provisions
              {2015: {'_SS_Earnings_c_cpi': False,
                      '_SS_Earnings_c': [500000]}}]
    # specify two Policy objects
    ppo = [Policy(), Policy()]
    # apply reforms to corresponding Policy object & check post-reform values
    syr = Policy.JSON_START_YEAR
    for ref in range(len(reform)):
        # confirm pre-reform MTE values in 2014-17
        mte = ppo[ref]._SS_Earnings_c
        assert mte[2014 - syr] == 117000
        assert mte[2015 - syr] == 118500
        assert mte[2016 - syr] == 118500
        assert mte[2017 - syr] < 500000
        # implement reform in 2015
        ppo[ref].implement_reform(reform[ref])
        # confirm post-reform MTE values in 2014-17
        mte = ppo[ref]._SS_Earnings_c
        assert mte[2014 - syr] == 117000
        assert mte[2015 - syr] == 500000
        assert mte[2016 - syr] == 500000
        assert mte[2017 - syr] == 500000


def test_misspecified_reforms():
    """
    Demonstrate pitfalls of careless specification of policy reforms.
    """
    # specify apparently the same reform in two different ways, forgetting
    # that Python dictionaries have unique keys
    reform1 = {2016: {'_SS_Earnings_c': [500000],
                      '_II_em': [9000]}}
    reform2 = {2016: {'_SS_Earnings_c': [500000]},
               2016: {'_II_em': [9000]}}
    # these two reform dictionaries are not the same: the second
    # 2016 key:value pair in reform2 (2016:{'_II_em...}) overwrites and
    # replaces the first 2016 key:value pair in reform2 (2016:{'_SS_E...})
    assert not reform1 == reform2


def test_section_titles(tests_path):
    """
    Check section titles in policy_current_law.json and index.htmx files.
    """
    def generate_section_dictionary(html_text):
        """
        Returns dictionary of section titles that is
        structured like the VALID_SECTION dictionary (see below) and
        extracted from the specified html_text.
        """
        sdict = dict()
        for line in html_text.splitlines():
            if line == '<!--  @  -->':  # the last policy parameter line
                sdict[''] = {'': 0}
                break  # out of line loop
            secline = (line.startswith('<!--') and
                       line.endswith('-->') and
                       '@' in line)
            if secline:
                info = line.replace('<!--', '', 1).replace('-->', '', 1)
                seclist = info.split('@', 1)
                sec1 = seclist[0].strip()
                sec2 = seclist[1].strip()
                if sec1 not in sdict:
                    sdict[sec1] = {}
                sdict[sec1][sec2] = 0
        return sdict
    # begin main logic of test_section_titles
    # specify expected section titles ordered as on TaxBrain
    ided_ceiling_pct = ('Ceiling On The Benefit Of Itemized Deductions '
                        'As A Percent Of Deductible Expenses')
    cgqd_tax_same = ('Tax All Capital Gains And Dividends The Same '
                     'As Regular Taxable Income')
    VALID = {
        '': {  # empty section_1 implies parameter is not displayed in TaxBrain
            '': 0
        },
        'Parameter Indexing': {
            'Offsets': 0
        },
        'Payroll Taxes': {
            'Social Security FICA': 0,
            'Medicare FICA': 0,
            'Additional Medicare FICA': 0
        },
        'Social Security Taxability': {
            'Threshold For Social Security Benefit Taxability 1': 0,
            # 'Social Security Taxable Income Decimal Fraction 1': 0,
            'Threshold For Social Security Benefit Taxability 2': 0
            # 'Social Security Taxable Income Decimal Fraction 2': 0
        },
        'Above The Line Deductions': {
            'Misc. Adjustment Haircuts': 0,
            'Misc. Exclusions': 0,
            'Child And Elderly Care': 0
        },
        'Personal Exemptions': {
            'Personal And Dependent Exemption Amount': 0,
            # 'Personal Exemption Phaseout Starting Income': 0,
            'Personal Exemption Phaseout Rate': 0,
            'Repeal for Dependents Under Age 18': 0
        },
        'Standard Deduction': {
            'Standard Deduction Amount': 0,
            'Additional Standard Deduction For Blind And Aged': 0
            # 'Standard Deduction For Dependents': 0
        },
        'Nonrefundable Credits': {
            'Misc. Credit Limits': 0,
            'Child And Dependent Care': 0,
            'Child Tax Credit': 0,
            'Personal Nonrefundable Credit': 0
        },
        'Itemized Deductions': {
            'Medical Expenses': 0,
            'State And Local Income And Sales Taxes': 0,
            'State, Local, And Foreign Real Estate Taxes': 0,
            'Interest Paid': 0,
            'Charity': 0,
            'Casualty': 0,
            'Miscellaneous': 0,
            'Itemized Deduction Limitation': 0,
            'Surtax On Itemized Deduction Benefits Above An AGI Threshold': 0,
            ided_ceiling_pct: 0,
            'Ceiling On The Amount Of Itemized Deductions Allowed': 0
        },
        'Capital Gains And Dividends': {
            'Regular - Long Term Capital Gains And Qualified Dividends': 0,
            'AMT - Long Term Capital Gains And Qualified Dividends': 0,
            cgqd_tax_same: 0
        },
        'Personal Income': {
            'Regular: Non-AMT, Non-Pass-Through': 0,
            'Pass-Through': 0,
            'Alternative Minimum Tax': 0
        },
        'Other Taxes': {
            'Net Investment Income Tax': 0
        },
        'Refundable Credits': {
            'Earned Income Tax Credit': 0,
            'Additional Child Tax Credit': 0,
            'New Refundable Child Tax Credit': 0,
            'Personal Refundable Credit': 0
        },
        'Surtaxes': {
            'New Minimum Tax': 0,
            'New AGI Surtax': 0,
            'Lump-Sum Tax': 0
        },
        'Universal Basic Income': {
            'UBI Benefits': 0,
            'UBI Taxability': 0
        },
        'Benefits': {
            'Benefit Repeal': 0,
        }
    }
    # check validity of parameter section titles in policy_current_law.json
    path = os.path.join(tests_path, '..', 'policy_current_law.json')
    with open(path, 'r') as clpfile:
        clpdict = json.load(clpfile)
    # ... make sure ever clpdict section title is in VALID dict
    CLP = dict()  # dictionary of clp section titles structured like VALID
    for pname in clpdict:
        param = clpdict[pname]
        assert isinstance(param, dict)
        sec1title = param['section_1']
        assert sec1title in VALID
        sec2title = param['section_2']
        assert sec2title in VALID[sec1title]
        if sec1title not in CLP:
            CLP[sec1title] = {}
        if sec2title not in CLP[sec1title]:
            CLP[sec1title][sec2title] = 0
    # ... make sure every VALID section title is in clpdict
    for sec1title in VALID:
        assert isinstance(VALID[sec1title], dict)
        assert sec1title in CLP
        for sec2title in VALID[sec1title]:
            assert sec2title in CLP[sec1title]
    # check validity of parameter section titles in docs/index.htmx skeleton
    path = os.path.join(tests_path, '..', '..', 'docs', 'index.htmx')
    with open(path, 'r') as htmxfile:
        htmx_text = htmxfile.read()
    htmxdict = generate_section_dictionary(htmx_text)
    # ... make sure every htmxdict section title is in VALID dict
    for sec1title in htmxdict:
        assert isinstance(htmxdict[sec1title], dict)
        assert sec1title in VALID
        for sec2title in htmxdict[sec1title]:
            assert sec2title in VALID[sec1title]
    # ... make sure every VALID section title is in htmxdict
    for sec1title in VALID:
        assert isinstance(VALID[sec1title], dict)
        assert sec1title in htmxdict
        for sec2title in VALID[sec1title]:
            assert sec2title in htmxdict[sec1title]


def test_json_reform_suffixes(tests_path):
    """
    Check "var_label" values versus Policy.JSON_REFORM_SUFFIXES set
    """
    # read policy_current_law.json file into a dictionary
    path = os.path.join(tests_path, '..', 'policy_current_law.json')
    with open(path, 'r') as clpfile:
        clpdict = json.load(clpfile)
    # create set of suffixes in the clpdict "col_label" lists
    json_suffixes = Policy.JSON_REFORM_SUFFIXES.keys()
    clp_suffixes = set()
    for param in clpdict:
        suffix = param.split('_')[-1]
        assert suffix not in json_suffixes
        col_var = clpdict[param]['col_var']
        col_label = clpdict[param]['col_label']
        if col_var == '':
            assert col_label == ''
            continue
        assert isinstance(col_label, list)
        clp_suffixes.update(col_label)
    # check that suffixes set is same as Policy.JSON_REFORM_SUFFIXES set
    unmatched = clp_suffixes ^ set(json_suffixes)
    if len(unmatched) != 0:
        assert unmatched == 'UNMATCHED SUFFIXES'


def test_description_punctuation(tests_path):
    """
    Check that each description ends in a period.
    """
    # read JSON file into a dictionary
    path = os.path.join(tests_path, '..', 'policy_current_law.json')
    with open(path, 'r') as jsonfile:
        dct = json.load(jsonfile)
    all_desc_ok = True
    for param in dct.keys():
        if not dct[param]['description'].endswith('.'):
            all_desc_ok = False
            print('param,description=',
                  str(param),
                  dct[param]['description'])
    assert all_desc_ok


def test_range_infomation(tests_path):
    """
    Check consistency of range-related info in policy_current_law.json file.
    """
    # read policy_current_law.json file into a dictionary
    path = os.path.join(tests_path, '..', 'policy_current_law.json')
    with open(path, 'r') as clpfile:
        clpdict = json.load(clpfile)
    parameters = set(clpdict.keys())
    # construct set of parameter names with "range" field in clpdict
    min_max_list = ['min', 'max']
    warn_stop_list = ['warn', 'stop']
    json_range_params = set()
    for pname in parameters:
        param = clpdict[pname]
        assert isinstance(param, dict)
        range = param.get('range', None)
        if range:
            json_range_params.add(pname)
            oor_action = param['out_of_range_action']
            assert oor_action in warn_stop_list
            range_items = range.items()
            assert len(range_items) == 2
            for vop, vval in range_items:
                assert vop in min_max_list
                if isinstance(vval, str):
                    if vval == 'default':
                        if vop != 'min' or oor_action != 'warn':
                            msg = 'USES DEFAULT FOR min OR FOR error'
                            assert pname == msg
                        continue
                    elif vval in clpdict:
                        if vop == 'min':
                            extra_msg = param['out_of_range_minmsg']
                        if vop == 'max':
                            extra_msg = param['out_of_range_maxmsg']
                        assert vval in extra_msg
                    else:
                        assert vval == 'ILLEGAL RANGE STRING VALUE'
                else:  # if vval is not a str
                    if isinstance(vval, int):
                        continue
                    elif isinstance(vval, float):
                        continue
                    elif isinstance(vval, bool):
                        continue
                    else:
                        assert vval == 'ILLEGAL RANGE NUMERIC VALUE'
    # compare contents of c_l_p.json parameters and json_range_params
    unmatched = parameters ^ json_range_params
    if len(unmatched) != 0:
        assert unmatched == 'UNMATCHED RANGE PARAMETERS'
    # check all current-law-policy parameters for range validity
    clp = Policy()
    clp._validate_parameter_values(parameters)
    assert len(clp.parameter_warnings) == 0
    assert len(clp.parameter_errors) == 0


def test_validate_param_names_types_errors():
    """
    Check detection of invalid policy parameter names and types in reforms.
    """
    pol0 = Policy()
    ref0 = {2020: {'_STD_cpi': 2}}
    with pytest.raises(ValueError):
        pol0.implement_reform(ref0)
    pol1 = Policy()
    ref1 = {2020: {'_badname_cpi': True}}
    with pytest.raises(ValueError):
        pol1.implement_reform(ref1)
    pol2 = Policy()
    ref2 = {2020: {'_II_em_cpi': 5}}
    with pytest.raises(ValueError):
        pol2.implement_reform(ref2)
    pol3 = Policy()
    ref3 = {2020: {'_badname': [0.4]}}
    with pytest.raises(ValueError):
        pol3.implement_reform(ref3)
    pol4 = Policy()
    ref4 = {2020: {'_EITC_MinEligAge': [21.4]}}
    with pytest.raises(ValueError):
        pol4.implement_reform(ref4)
    pol5 = Policy()
    ref5 = {2025: {'_ID_BenefitSurtax_Switch': [[False, True, 0, 1, 0, 1, 0]]}}
    with pytest.raises(ValueError):
        pol5.implement_reform(ref5)
    pol6 = Policy()
    ref6 = {2021: {'_II_em': ['not-a-number']}}
    with pytest.raises(ValueError):
        pol6.implement_reform(ref6)
    pol7 = Policy()
    ref7 = {2019: {'_FICA_ss_trt_cpi': True}}
    with pytest.raises(ValueError):
        pol7.implement_reform(ref7)
    # test 8 was contributed by Hank Doupe in bug report #1956
    pol8 = Policy()
    ref8 = {2019: {'_AMEDT_rt': [True]}}
    with pytest.raises(ValueError):
        pol8.implement_reform(ref8)
    # test 9 extends test 8 to integer parameters
    pol9 = Policy()
    ref9 = {2019: {'_AMT_KT_c_Age': [True]}}
    with pytest.raises(ValueError):
        pol9.implement_reform(ref9)
    # test 10 was contributed by Hank Doupe in bug report #1980
    json_reform = """
    {"policy": {"_ID_BenefitSurtax_Switch_medical": {"2018": [true]}}}
    """
    pdict = Calculator.read_json_param_objects(json_reform, None)
    pol = Policy()
    pol.implement_reform(pdict["policy"], raise_errors=False)
    assert pol.parameter_errors == ''


def test_validate_param_values_warnings_errors():
    """
    Check detection of out_of_range policy parameters in reforms.
    """
    pol1 = Policy()
    ref1 = {2020: {'_ID_Medical_frt': [0.05]}}
    pol1.implement_reform(ref1, print_warnings=True, raise_errors=False)
    assert len(pol1.parameter_warnings) > 0
    pol2 = Policy()
    ref2 = {2021: {'_ID_Charity_crt_all': [0.61]}}
    pol2.implement_reform(ref2, print_warnings=False, raise_errors=False)
    assert len(pol2.parameter_warnings) > 0
    pol3 = Policy()
    ref3 = {2024: {'_II_brk4': [[0, 0, 0, 0, 0]]}}
    pol3.implement_reform(ref3, print_warnings=False, raise_errors=False)
    assert len(pol3.parameter_errors) > 0
    pol4 = Policy()
    ref4 = {2024: {'_II_brk4': [[0, 9e9, 0, 0, 0]]}}
    pol4.implement_reform(ref4, print_warnings=False, raise_errors=False)
    assert len(pol4.parameter_errors) > 0
    pol5 = Policy()
    pol5.ignore_reform_errors()
    ref5 = {2025: {'_ID_BenefitSurtax_Switch': [[False, True, 0, 1, 0, 1, 0]]}}
    pol5.implement_reform(ref5, print_warnings=False, raise_errors=False)
    assert len(pol5.parameter_errors) > 0
    pol6 = Policy()
    ref6 = {2013: {'_STD': [[20000, 25000, 20000, 20000, 25000]]}}
    pol6.implement_reform(ref6, print_warnings=False, raise_errors=False)
    assert pol6.parameter_errors == ''
    assert pol6.parameter_warnings == ''


def test_indexing_rates_for_update():
    """
    Check private _indexing_rates_for_update method.
    """
    pol = Policy()
    wgrates = pol._indexing_rates_for_update('_SS_Earnings_c', 2017, 10)
    pirates = pol._indexing_rates_for_update('_II_em', 2017, 10)
    assert len(wgrates) == len(pirates)
