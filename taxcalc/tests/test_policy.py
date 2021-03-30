"""
Test Policy class and its methods.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_policy.py
# pylint --disable=locally-disabled test_policy.py
#
# pylint: disable=too-many-lines

import copy
import os
import json
import numpy as np
import pytest
import paramtools as pt
# pylint: disable=import-error
from taxcalc import Policy


def cmp_policy_objs(pol1, pol2, year_range=None, exclude=None):
    """
    Compare parameter values two policy objects.

    year_range: years over which to compare values.
    exclude: list of parameters to exclude from comparison.
    """
    if year_range is not None:
        pol1.set_state(year=list(year_range))
        pol2.set_state(year=list(year_range))
    else:
        pol1.clear_state()
        pol2.clear_state()
    for param in pol1._data:
        if exclude and param in exclude:
            continue
        v1 = getattr(pol1, param)
        v2 = getattr(pol2, param)
        np.testing.assert_allclose(v1, v2)


def test_incorrect_class_instantiation():
    """
    Test incorrect instantiation of Policy class object.
    """
    with pytest.raises(ValueError):
        Policy(gfactors=list())


def test_correct_class_instantiation():
    """
    Test correct instantiation of Policy class object.
    """
    pol = Policy()
    assert pol
    pol.implement_reform({})
    with pytest.raises(pt.ValidationError):
        pol.implement_reform(list())
    with pytest.raises(pt.ValidationError):
        pol.implement_reform({2099: {'II_em': 99000}})
    pol.set_year(2019)
    with pytest.raises(pt.ValidationError):
        pol.implement_reform({2018: {'II_em': 99000}})
    with pytest.raises(pt.ValidationError):
        pol.implement_reform({2020: {'II_em': -1000}})


def test_json_reform_url():
    """
    Test reading a JSON reform from a URL. Results from the URL are expected
    to match the results from the string.
    """
    reform_str = """
    {
        // raise FICA payroll tax rate in 2018 and 2020
        "FICA_ss_trt": {
            "2018": 0.130,
            "2020": 0.140
        },
        // raise Medicare payroll tax rate in 2019 and 2021
        "FICA_mc_trt": {
            "2019": 0.030,
            "2021": 0.032
        }
    }
    """
    reform_url = ('https://raw.githubusercontent.com/PSLmodels/'
                  'Tax-Calculator/master/taxcalc/reforms/ptaxes0.json')
    params_str = Policy.read_json_reform(reform_str)
    params_url = Policy.read_json_reform(reform_url)
    assert params_str == params_url

    reform_gh_url = (
        "github://PSLmodels:Tax-Calculator@master/taxcalc/reforms/ptaxes0.json"
    )
    params_gh_url = Policy.read_json_reform(reform_gh_url)
    assert params_gh_url
    assert params_gh_url == params_str


REFORM_JSON = """
// Example of a reform file suitable for Policy.read_json_reform().
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// The primary keys are parameters and the secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
    "AMT_brk1": // top of first AMT tax bracket
    {"2015": 200000,
     "2017": 300000
    },
    "EITC_c": // maximum EITC amount by number of qualifying kids (0,1,2,3+)
    {"2016": [ 900, 5000,  8000,  9000],
     "2019": [1200, 7000, 10000, 12000]
    },
    "II_em": // personal exemption amount (see indexing changes below)
    {"2016": 6000,
     "2018": 7500,
     "2020": 9000
    },
    "II_em-indexed": // personal exemption amount indexing status
    {"2016": false, // values in future years are same as this year value
     "2018": true   // values in future years indexed with this year as base
    },
    "SS_Earnings_c": // social security (OASDI) maximum taxable earnings
    {"2016": 300000,
     "2018": 500000,
     "2020": 700000
    },
    "AMT_em-indexed": // AMT exemption amount indexing status
    {"2017": false, // values in future years are same as this year value
     "2020": true   // values in future years indexed with this year as base
    }
}
"""


# pylint: disable=protected-access,no-member


@pytest.mark.parametrize("set_year", [False, True])
def test_read_json_reform_file_and_implement_reform(set_year):
    """
    Test reading and translation of reform JSON into a reform dictionary
    and then using that reform dictionary to implement reform.
    """
    pol = Policy()
    if set_year:
        pol.set_year(2015)
    pol.implement_reform(Policy.read_json_reform(REFORM_JSON))
    syr = pol.start_year
    # pylint: disable=protected-access
    amt_brk1 = pol._AMT_brk1
    assert amt_brk1[2015 - syr] == 200000
    assert amt_brk1[2016 - syr] > 200000
    assert amt_brk1[2017 - syr] == 300000
    assert amt_brk1[2018 - syr] > 300000
    ii_em = pol._II_em
    assert ii_em[2016 - syr] == 6000
    assert ii_em[2017 - syr] == 6000
    assert ii_em[2018 - syr] == 7500
    assert ii_em[2019 - syr] > 7500
    assert ii_em[2020 - syr] == 9000
    assert ii_em[2021 - syr] > 9000
    amt_em = pol._AMT_em
    assert amt_em[2016 - syr, 0] > amt_em[2015 - syr, 0]
    assert amt_em[2017 - syr, 0] > amt_em[2016 - syr, 0]
    assert amt_em[2018 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2019 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2020 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2021 - syr, 0] > amt_em[2020 - syr, 0]
    assert amt_em[2022 - syr, 0] > amt_em[2021 - syr, 0]
    add4aged = pol._ID_Medical_frt_add4aged
    assert add4aged[2015 - syr] == -0.025
    assert add4aged[2016 - syr] == -0.025
    assert add4aged[2017 - syr] == 0.0
    assert add4aged[2022 - syr] == 0.0


def test_constant_inflation_rate_with_reform():
    """
    Test indexing of policy parameters involved in a reform.
    """
    pol = Policy()
    # implement reform in year before final year
    fyr = Policy.LAST_BUDGET_YEAR
    ryr = fyr - 1
    reform = {
        'II_em': {(ryr - 3): 1000,  # to avoid divide-by-zero under TCJA
                  ryr: 20000}
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
    """
    Test indexing of policy parameters involved in a reform.
    """
    pol = Policy()
    syr = Policy.JSON_START_YEAR
    assert pol._II_em[2013 - syr] == 3900
    # implement reform in 2020 which is two years before the last year, 2022
    reform = {
        'II_em': {2018: 1000,  # to avoid divide-by-zero under TCJA
                  2020: 20000}
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
    # specify multi-year reform using a param:year:value-fomatted dictionary
    reform = {
        'SS_Earnings_c': {2016: 300000,
                          2017: 500000,
                          2019: 700000},
        'SS_Earnings_c-indexed': {2017: False,
                                  2019: True},
        'CTC_c': {2015: 2000},
        'EITC_c': {2016: [900, 5000, 8000, 9000],
                   2019: [1200, 7000, 10000, 12000]},
        'II_em': {2016: 7000,
                  2019: 9000}
    }
    # implement multi-year reform
    pol.implement_reform(reform)
    assert pol.current_year == syr
    # move policy Policy object forward in time so current_year is syr+2
    #   Note: this would be typical usage because the first budget year
    #         is typically greater than Policy start_year.
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
    e2015 = reform['CTC_c'][2015]
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
    e2016 = reform['EITC_c'][2016]
    assert np.allclose(actual[2016], e2016, atol=0.01, rtol=0.0)
    e2017 = [ifactor[2016] * actual[2016][j] for j in range(0, alen)]
    assert np.allclose(actual[2017], e2017, atol=0.01, rtol=0.0)
    e2018 = [ifactor[2017] * actual[2017][j] for j in range(0, alen)]
    assert np.allclose(actual[2018], e2018, atol=0.01, rtol=0.0)
    e2019 = reform['EITC_c'][2019]
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
    e2016 = reform['II_em'][2016]
    assert actual[2016] == e2016
    e2017 = ifactor[2016] * actual[2016]
    assert np.allclose([actual[2017]], [e2017], atol=0.01, rtol=0.0)
    e2018 = ifactor[2017] * actual[2017]
    assert np.allclose([actual[2018]], [e2018], atol=0.01, rtol=0.0)
    e2019 = reform['II_em'][2019]
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
    e2016 = reform['SS_Earnings_c'][2016]
    assert actual[2016] == e2016
    e2017 = reform['SS_Earnings_c'][2017]
    assert actual[2017] == e2017
    e2018 = actual[2017]  # no indexing after 2017
    assert actual[2018] == e2018
    e2019 = reform['SS_Earnings_c'][2019]
    assert actual[2019] == e2019
    e2020 = wfactor[2019] * actual[2019]  # indexing after 2019
    assert actual[2020] == e2020
    e2021 = wfactor[2020] * actual[2020]
    assert np.allclose([actual[2021]], [e2021], atol=0.01, rtol=0.0)
    e2022 = wfactor[2021] * actual[2021]
    assert np.allclose([actual[2022]], [e2022], atol=0.01, rtol=0.0)


def test_policy_metadata():
    """
    Test that metadata() method returns expected dictionary.
    """
    clp = Policy()
    mdata = clp.metadata()
    assert mdata


def test_implement_reform_raises_on_no_year():
    """
    Test that implement_reform raises error for missing year.
    """
    reform = {'STD_Aged': [1400, 1200, 1400, 1400, 1400]}
    ppo = Policy()
    with pytest.raises(pt.ValidationError):
        ppo.implement_reform(reform)


def test_implement_reform_raises_on_early_year():
    """
    Test that implement_reform raises error for early year.
    """
    ppo = Policy()
    reform = {'STD_Aged': {2010: [1400, 1100, 1100, 1400, 1400]}}
    with pytest.raises(pt.ValidationError):
        ppo.implement_reform(reform)


def test_reform_with_default_indexed():
    """
    Test that implement_reform indexes after first reform year.
    """
    ppo = Policy()
    reform = {'II_em': {2015: 4300}}
    ppo.implement_reform(reform)
    # II_em has a default indexing status of true, so
    # in 2016 its value should be greater than 4300
    ppo.set_year(2016)
    assert ppo.II_em > 4300


def test_reform_makes_no_changes_before_year():
    """
    Test that implement_reform makes no changes before first reform year.
    """
    ppo = Policy()
    reform = {'II_em': {2015: 4400}, 'II_em-indexed': {2015: True}}
    ppo.implement_reform(reform)
    ppo.set_year(2015)
    assert np.allclose(ppo._II_em[2:5], np.array([3900, 3950, 4400]),
                       atol=0.01, rtol=0.0)
    assert ppo.II_em == 4400


@pytest.mark.parametrize("set_year", [False, True])
def test_read_json_reform_and_implement_reform(set_year):
    """
    Test reading and translation of reform file into a reform dictionary
    that is then used to call implement_reform method.
    NOTE: implement_reform called when policy.current_year == policy.start_year
    """
    reform_json = """
    // Example of JSON reform text suitable for the
    // Policy.read_json_reform() method.
    // This JSON text can contain any number of trailing //-style comments,
    // which will be removed before the contents are converted from JSON to
    // a dictionary.
    // The primary keys are policy parameters and secondary keys are years.
    // Both the primary & secondary key values must be enclosed in quotes (").
    // Boolean variables are specified as true or false with no quotes and all
    // lowercase characters.
    {
        "AMT_brk1": // top of first AMT tax bracket
        {"2015": 200000,
         "2017": 300000
        },
        "EITC_c": // max EITC amount by number of qualifying kids (0,1,2,3+)
        {"2016": [ 900, 5000,  8000,  9000],
         "2019": [1200, 7000, 10000, 12000]
        },
        "II_em": // personal exemption amount (see indexing changes below)
        {"2016": 6000,
         "2018": 7500,
         "2020": 9000
        },
        "II_em-indexed": // personal exemption amount indexing status
        {"2016": false, // values in future years are same as this year value
         "2018": true   // vals in future years indexed with this year as base
        },
        "SS_Earnings_c": // Social Security (OASDI) maximum taxable earnings
        {"2016": 300000,
         "2018": 500000,
         "2020": 700000
        },
        "AMT_em-indexed": // AMT exemption amount indexing status
        {"2017": false, // values in future years are same as this year value
         "2020": true   // vals in future years indexed with this year as base
        }
    }
    """
    policy = Policy()
    if set_year:
        policy.set_year(2015)
    reform_dict = Policy.read_json_reform(reform_json)
    policy.implement_reform(reform_dict)
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
    reform = {'SS_Earnings_c': {2016: 9e99}}
    ppo.implement_reform(reform)
    mte = ppo._SS_Earnings_c
    assert mte[2015 - syr] == 118500
    assert mte[2016 - syr] == 9e99
    assert mte[ppo.end_year - syr] == 9e99


def test_order_of_indexing_and_level_reforms():
    """
    Test that the order of the two reform provisions for the same parameter
    make no difference to the post-reform policy parameter values.
    """
    # specify two reforms that raises the MTE and stops its indexing in 2015
    reform = [
        {
            'SS_Earnings_c': {2015: 500000},
            'SS_Earnings_c-indexed': {2015: False}
        },
        # now reverse the order of the two reform provisions
        {
            'SS_Earnings_c-indexed': {2015: False},
            'SS_Earnings_c': {2015: 500000}
        }
    ]
    # specify two Policy objects
    ppo = [Policy(), Policy()]
    # apply reforms to corresponding Policy object & check post-reform values
    syr = Policy.JSON_START_YEAR
    for ref in range(len(reform)):  # pylint: disable=consider-using-enumerate
        # confirm pre-reform MTE values in 2014-2017
        mte = ppo[ref]._SS_Earnings_c
        assert mte[2014 - syr] == 117000
        assert mte[2015 - syr] == 118500
        assert mte[2016 - syr] == 118500
        assert mte[2017 - syr] < 500000
        # implement reform in 2015
        ppo[ref].implement_reform(reform[ref])
        # confirm post-reform MTE values in 2014-2017
        mte = ppo[ref]._SS_Earnings_c
        assert mte[2014 - syr] == 117000
        assert mte[2015 - syr] == 500000
        assert mte[2016 - syr] == 500000
        assert mte[2017 - syr] == 500000


def test_misspecified_reform_dictionary():
    """
    Demonstrate pitfalls of careless specification of policy reform
    dictionaries involving non-unique dictionary keys.
    """
    # specify apparently the same reform in two different ways, forgetting
    # that Python dictionaries have unique keys
    reform1 = {'II_em': {2019: 1000, 2020: 2000}}
    # pylint: disable=duplicate-key
    reform2 = {'II_em': {2019: 1000}, 'II_em': {2020: 2000}}
    # these two reform dictionaries are not the same: the second
    # 'II_em' key value for 2020 in reform2 OVERWRITES and REPLACES
    # the first 'II_em' key value for 2019 in reform2
    assert reform1 != reform2


def test_section_titles(tests_path):
    """
    Check section titles in policy_current_law.json and uguide.htmx files.
    """
    # pylint: disable=too-many-locals
    def generate_section_dictionary(md_text):
        """
        Returns dictionary of section titles that is
        structured like the VALID_SECTION dictionary (see below) and
        extracted from the specified html_text.
        """
        sdict = dict()
        for line in md_text.splitlines():
            # This is shown as an empty case in current law policy and
            # validation.
            if line.startswith('## Other Parameters (not in Tax-Brain webapp'):
                sdict[''] = {}
                sdict[''][''] = 0
                continue
            sec2line = line.startswith('### ')
            sec1line = line.startswith('## ')
            # Create outer-layer dictionary entry for sec1.
            if sec1line:
                sec1 = line.replace('##', '', 1).strip()
                sdict[sec1] = {}
            # Create inner dictionary entry for sec1-sec2.
            # Note that sec1 will have been defined from a previous loop.
            if sec2line:
                sec2 = line.replace('###', '', 1).strip()
                sdict[sec1][sec2] = 0
        return sdict
    # begin main logic of test_section_titles
    # specify expected section titles ordered as on the Tax-Brain webapp
    ided_ceiling_pct = ('Ceiling On The Benefit Of Itemized Deductions '
                        'As A Percent Of Deductible Expenses')
    cgqd_tax_same = ('Tax All Capital Gains And Dividends The Same '
                     'As Regular Taxable Income')
    # pylint: disable=bad-continuation
    valid_dict = {
        '': {  # empty section_1 implies parameter not displayed in Tax-Brain
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
            'Personal Nonrefundable Credit': 0
        },
        'Child/Dependent Credits': {
            'Child Tax Credit': 0,
            'Additional Child Tax Credit': 0,
            'Other Dependent Tax Credit': 0
        },
        'Itemized Deductions': {
            'Medical Expenses': 0,
            'State And Local Income And Sales Taxes': 0,
            'State, Local, And Foreign Real Estate Taxes': 0,
            'State And Local Taxes And Real Estate Taxes': 0,
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
            'New Refundable Child Tax Credit': 0,
            'Personal Refundable Credit': 0,
            'Refundable Payroll Tax Credit': 0
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
        clpdict.pop("schema", None)
    # ... make sure ever clpdict section title is in valid_dict
    clp_dict = dict()  # dictionary of clp section titles structured like valid
    for pname in clpdict:
        param = clpdict[pname]
        assert isinstance(param, dict)
        sec1title = param['section_1']
        assert sec1title in valid_dict
        sec2title = param['section_2']
        assert sec2title in valid_dict[sec1title]
        if sec1title not in clp_dict:
            clp_dict[sec1title] = {}
        if sec2title not in clp_dict[sec1title]:
            clp_dict[sec1title][sec2title] = 0
    # ... make sure every valid_dict section title is in clpdict
    for sec1title in valid_dict:
        assert isinstance(valid_dict[sec1title], dict)
        assert sec1title in clp_dict
        for sec2title in valid_dict[sec1title]:
            assert sec2title in clp_dict[sec1title]
    # check validity of parameter section titles in docs/uguide.htmx skeleton
    path = os.path.join(tests_path, '..', '..', 'docs', 'guide',
                        'policy_params.md')
    with open(path, 'r') as md_file:
        md_text = md_file.read()
    md_dict = generate_section_dictionary(md_text)
    # ... make sure every md_dict section title is in valid_dict
    for sec1title in md_dict:
        assert isinstance(md_dict[sec1title], dict)
        assert sec1title in valid_dict
        for sec2title in md_dict[sec1title]:
            assert sec2title in valid_dict[sec1title]
    # ... make sure every valid_dict section title is in md_dict
    for sec1title in valid_dict:
        assert isinstance(valid_dict[sec1title], dict)
        assert sec1title in md_dict
        for sec2title in valid_dict[sec1title]:
            assert sec2title in md_dict[sec1title]


def test_description_punctuation(tests_path):
    """
    Check that each description ends in a period.
    """
    # read JSON file into a dictionary
    path = os.path.join(tests_path, '..', 'policy_current_law.json')
    with open(path, 'r') as jsonfile:
        dct = json.load(jsonfile)
        dct.pop("schema", None)
    all_desc_ok = True
    for param in dct.keys():
        if not dct[param]['description'].endswith('.'):
            all_desc_ok = False
            print('param,description=',
                  str(param),
                  dct[param]['description'])
    assert all_desc_ok


def test_get_index_rate():
    """
    Test Parameters.get_index_rate.
    """
    pol = Policy()
    wgrates = pol.get_index_rate('SS_Earnings_c', 2017)
    pirates = pol.get_index_rate('II_em', 2017)
    assert isinstance(wgrates, np.float64)
    assert wgrates == pol.wage_growth_rates(2017)
    assert pirates == pol.inflation_rates(2017)
    assert isinstance(pirates, np.float64)
    assert pol.inflation_rates() == pol._inflation_rates
    assert pol.wage_growth_rates() == pol._wage_growth_rates


def test_reform_with_bad_ctc_levels():
    """
    Implement a reform with _ACTC > _CTC_c values.
    """
    pol = Policy()
    child_credit_reform = {
        'CTC_c': {2020: 2200},
        'ACTC_c': {2020: 2500}
    }
    with pytest.raises(pt.ValidationError):
        pol.implement_reform(child_credit_reform)


def test_reform_with_removed_parameter(monkeypatch):
    """
    Try to use removed parameter in a reform.
    """
    policy1 = Policy()
    reform1 = {'FilerCredit_c': {2020: 1000}}
    with pytest.raises(pt.ValidationError):
        policy1.implement_reform(reform1)
    policy2 = Policy()
    reform2 = {'FilerCredit_c-indexed': {2020: True}}
    with pytest.raises(pt.ValidationError):
        policy2.implement_reform(reform2)

    redefined_msg = {"some_redefined": "some_redefined was redefined."}
    monkeypatch.setattr(Policy, "REDEFINED_PARAMS", redefined_msg)

    pol = Policy()
    with pytest.raises(pt.ValidationError):
        pol.implement_reform({"some_redefined": "hello world"})


def test_reform_with_out_of_range_error():
    """
    Try to use out-of-range values versus other parameter values in a reform.
    """
    pol = Policy()
    reform = {'SS_thd85': {2020: [20000, 20000, 20000, 20000, 20000]}}
    pol.implement_reform(reform, raise_errors=False)
    assert pol.parameter_errors


def test_reform_with_warning():
    """
    Try to use warned out-of-range parameter value in reform.
    """
    exp_warnings = {
        'ID_Medical_frt': [
            'ID_Medical_frt[year=2020] 0.05 < min 0.075 '
        ]
    }
    pol = Policy()
    reform = {'ID_Medical_frt': {2020: 0.05}}

    pol.implement_reform(reform, print_warnings=True)
    assert pol.warnings == exp_warnings
    pol.set_state(year=2020)
    assert pol.ID_Medical_frt == np.array([0.05])

    pol.implement_reform(reform, print_warnings=False)
    assert pol.warnings == {}
    pol.set_state(year=2020)
    assert pol.ID_Medical_frt == np.array([0.05])


def test_reform_with_scalar_vector_errors():
    """
    Test catching scalar-vector confusion.
    """
    policy1 = Policy()
    reform1 = {'SS_thd85': {2020: 30000}}
    with pytest.raises(pt.ValidationError):
        policy1.implement_reform(reform1)

    policy2 = Policy()
    reform2 = {'ID_Medical_frt': {2020: [0.08]}}
    with pytest.raises(pt.ValidationError):
        policy2.implement_reform(reform2)

    policy3 = Policy()
    reform3 = {'ID_Medical_frt': [{"year": 2020, "value": [0.08]}]}
    with pytest.raises(pt.ValidationError):
        policy3.adjust(reform3)

    # Check that error is thrown if there are extra elements in array.
    policy4 = Policy()
    ref4 = {"II_brk1": {2020: [9700, 19400, 9700, 13850, 19400, 19400]}}
    with pytest.raises(pt.ValidationError):
        policy4.implement_reform(ref4)

    policy5 = Policy()
    ref5 = {"II_rt1": {2029: [.2, .3]}}
    with pytest.raises(pt.ValidationError):
        policy5.implement_reform(ref5)


def test_index_offset_reform():
    """
    Test a reform that includes both a change in parameter_indexing_CPI_offset
    and a change in a variable's indexed status in the same year.
    """
    # create policy0 to extract inflation rates before any
    # parameter_indexing_CPI_offset
    policy0 = Policy()
    policy0.implement_reform({'parameter_indexing_CPI_offset': {2017: 0}})
    cpiu_rates = policy0.inflation_rates()

    reform1 = {'CTC_c-indexed': {2020: True}}
    policy1 = Policy()
    policy1.implement_reform(reform1)
    offset = -0.005
    reform2 = {'CTC_c-indexed': {2020: True},
               'parameter_indexing_CPI_offset': {2020: offset}}
    policy2 = Policy()
    policy2.implement_reform(reform2)  # caused T-C crash before PR#2364
    # extract from policy1 and policy2 the parameter values of CTC_c
    pvalue1 = dict()
    pvalue2 = dict()
    for cyr in [2019, 2020, 2021]:
        policy1.set_year(cyr)
        pvalue1[cyr] = policy1.CTC_c[0]
        policy2.set_year(cyr)
        pvalue2[cyr] = policy2.CTC_c[0]
    # check that pvalue1 and pvalue2 dictionaries contain the expected values
    assert pvalue2[2019] == pvalue1[2019]
    assert pvalue2[2020] == pvalue1[2020]
    assert pvalue2[2020] == pvalue2[2019]
    # ... indexing of CTC_c begins shows up first in 2021 parameter values
    assert pvalue1[2021] > pvalue1[2020]
    assert pvalue2[2021] > pvalue2[2020]
    # ... calculate expected pvalue2[2021] from offset and pvalue1 values
    indexrate1 = pvalue1[2021] / pvalue1[2020] - 1.
    syear = Policy.JSON_START_YEAR
    expindexrate = cpiu_rates[2020 - syear] + offset
    expvalue = round(pvalue2[2020] * (1. + expindexrate), 2)
    # ... compare expected value with actual value of pvalue2 for 2021
    assert np.allclose([expvalue], [pvalue2[2021]])


def test_cpi_offset_affect_on_prior_years():
    """
    Test that parameter_indexing_CPI_offset does not have affect
    on inflation rates in earlier years.
    """
    reform1 = {'parameter_indexing_CPI_offset': {2022: 0}}
    reform2 = {'parameter_indexing_CPI_offset': {2022: -0.005}}
    p1 = Policy()
    p2 = Policy()
    p1.implement_reform(reform1)
    p2.implement_reform(reform2)

    start_year = p1.start_year
    p1_rates = np.array(p1.inflation_rates())
    p2_rates = np.array(p2.inflation_rates())

    # Inflation rates prior to 2022 are the same.
    np.testing.assert_allclose(
        p1_rates[:2022 - start_year],
        p2_rates[:2022 - start_year]
    )

    # Inflation rate in 2022 was updated.
    np.testing.assert_allclose(
        p1_rates[2022 - start_year],
        p2_rates[2022 - start_year] - (-0.005)
    )


def test_cpi_offset_on_reverting_params():
    """
    Test that params that revert to their pre-TCJA values
    in 2026 revert if a parameter_indexing_CPI_offset is specified.
    """
    reform0 = {'parameter_indexing_CPI_offset': {2020: -0.001}}
    reform1 = {'STD': {2017: [6350, 12700, 6350, 9350, 12700]},
               'parameter_indexing_CPI_offset': {2020: -0.001}}
    reform2 = {'STD': {2020: [10000, 20000, 10000, 10000, 20000]},
               'parameter_indexing_CPI_offset': {2020: -0.001}}

    p0 = Policy()
    p1 = Policy()
    p2 = Policy()
    p0.implement_reform(reform0)
    p1.implement_reform(reform1)
    p2.implement_reform(reform2)

    ryear = 2026
    syear = Policy.JSON_START_YEAR

    # STD was reverted in 2026
    # atol=0.5 because ppp.py rounds params to nearest int
    assert np.allclose(
        p0._STD[ryear - syear],
        p1._STD[ryear - syear], atol=0.5)

    # STD was not reverted in 2026 if included in revision
    assert not np.allclose(
        p1._STD[ryear - syear],
        p2._STD[ryear - syear], atol=0.5)


def test_raise_errors_regression():
    """
    This tests that raise_errors prevents the error from being thrown. The
    correct behavior is to exit the `adjust` function and store the errors.
    """
    ref = {
        "II_brk7-indexed": [{"value": True}],
        "II_brk6": [{"value": 316700, "MARS": "single", "year": 2020}],
        "II_brk7": [{"value": 445400, "MARS": "single", "year": 2020}],

    }
    pol = Policy()
    pol.adjust(ref, raise_errors=False)
    assert pol.errors


class TestAdjust:
    """
    Test update and indexing rules as defined in the Parameters docstring.

    Each test implements a Tax-Calculator style reform and a pt styled
    reform, checks that the updated values are equal, and then, tests that
    values were extended and indexed (or not indexed) correctly.
    """

    def test_simple_adj(self):
        """
        Test updating a 2D parameter that is indexed to inflation.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {
                "EITC_c": {
                    2020: [10000, 10001, 10002, 10003],
                    2023: [20000, 20001, 20002, 20003],
                }
            }
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "EITC_c": [
                    {"year": 2020, "EIC": "0kids", "value": 10000},
                    {"year": 2020, "EIC": "1kid", "value": 10001},
                    {"year": 2020, "EIC": "2kids", "value": 10002},
                    {"year": 2020, "EIC": "3+kids", "value": 10003},
                    {"year": 2023, "EIC": "0kids", "value": 20000},
                    {"year": 2023, "EIC": "1kid", "value": 20001},
                    {"year": 2023, "EIC": "2kids", "value": 20002},
                    {"year": 2023, "EIC": "3+kids", "value": 20003},
                ]
            }
        )
        cmp_policy_objs(pol1, pol2)

        pol0 = Policy()
        pol0.set_year(2019)
        pol2.set_year(2019)

        assert np.allclose(pol0.EITC_c, pol2.EITC_c)

        pol2.set_state(year=[2020, 2021, 2022, 2023, 2024])
        val2020 = np.array([[10000, 10001, 10002, 10003]])
        val2023 = np.array([[20000, 20001, 20002, 20003]])

        exp = np.vstack([
            val2020,
            val2020 * (1 + pol2.inflation_rates(year=2020)),
            (
                val2020 * (1 + pol2.inflation_rates(year=2020))
            ).round(2) * (1 + pol2.inflation_rates(year=2021)),
            val2023,
            val2023 * (1 + pol2.inflation_rates(year=2023)),
        ]).round(2)
        np.testing.assert_allclose(pol2.EITC_c, exp)

    def test_adj_without_index_1(self):
        """
        Test update indexed parameter after turning off its
        indexed status.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {
                "EITC_c": {
                    2020: [10000, 10001, 10002, 10003],
                    2023: [20000, 20001, 20002, 20003],
                },
                "EITC_c-indexed": {2019: False},
            }
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "EITC_c": [
                    {"year": 2020, "EIC": "0kids", "value": 10000},
                    {"year": 2020, "EIC": "1kid", "value": 10001},
                    {"year": 2020, "EIC": "2kids", "value": 10002},
                    {"year": 2020, "EIC": "3+kids", "value": 10003},
                    {"year": 2023, "EIC": "0kids", "value": 20000},
                    {"year": 2023, "EIC": "1kid", "value": 20001},
                    {"year": 2023, "EIC": "2kids", "value": 20002},
                    {"year": 2023, "EIC": "3+kids", "value": 20003},
                ],
                "EITC_c-indexed": [{"year": 2019, "value": False}],
            }
        )
        cmp_policy_objs(pol1, pol2)

        pol0 = Policy()
        pol0.set_year(2019)
        pol2.set_year(2019)

        assert np.allclose(pol0.EITC_c, pol2.EITC_c)

        pol2.set_state(year=[2020, 2021, 2022, 2023, 2024])

        val2020 = np.array([[10000, 10001, 10002, 10003]])
        val2023 = np.array([[20000, 20001, 20002, 20003]])

        exp = np.vstack([
            val2020,
            val2020,
            val2020,
            val2023,
            val2023,
        ]).round(2)
        np.testing.assert_allclose(pol2.EITC_c, exp)

    def test_adj_without_index_2(self):
        """
        Test updating an indexed parameter, making it unindexed,
        and then adjusting it again.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {
                "EITC_c": {
                    2020: [10000, 10001, 10002, 10003],
                    2023: [20000, 20001, 20002, 20003],
                },
                "EITC_c-indexed": {2022: False},
            }
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "EITC_c": [
                    {"year": 2020, "EIC": "0kids", "value": 10000},
                    {"year": 2020, "EIC": "1kid", "value": 10001},
                    {"year": 2020, "EIC": "2kids", "value": 10002},
                    {"year": 2020, "EIC": "3+kids", "value": 10003},
                    {"year": 2023, "EIC": "0kids", "value": 20000},
                    {"year": 2023, "EIC": "1kid", "value": 20001},
                    {"year": 2023, "EIC": "2kids", "value": 20002},
                    {"year": 2023, "EIC": "3+kids", "value": 20003},
                ],
                "EITC_c-indexed": [{"year": 2022, "value": False}],
            }
        )
        cmp_policy_objs(pol1, pol2)

        pol0 = Policy()
        pol0.set_year(2019)
        pol2.set_year(2019)

        assert np.allclose(pol0.EITC_c, pol2.EITC_c)

        pol2.set_state(year=[2020, 2021, 2022, 2023, 2024])

        val2020 = np.array([[10000, 10001, 10002, 10003]])
        val2023 = np.array([[20000, 20001, 20002, 20003]])

        exp = np.vstack([
            val2020,
            val2020 * (1 + pol2.inflation_rates(year=2020)),
            (
                val2020 * (1 + pol2.inflation_rates(year=2020))
            ).round(2) * (1 + pol2.inflation_rates(year=2021)),
            val2023,
            val2023,
        ]).round(2)
        np.testing.assert_allclose(pol2.EITC_c, exp)

    def test_activate_index(self):
        """
        Test changing a non-indexed parameter to an indexed parameter.
        """
        pol1 = Policy()
        pol1.implement_reform({
            "CTC_c": {2022: 2000},
            "CTC_c-indexed": {2022: True}
        })

        pol2 = Policy()
        pol2.adjust(
            {
                "CTC_c": [{"year": 2022, "value": 2000}],
                "CTC_c-indexed": [{"year": 2022, "value": True}],
            }
        )
        cmp_policy_objs(pol1, pol2)

        pol0 = Policy()
        pol0.set_year(year=2021)
        pol2.set_state(year=[2021, 2022, 2023])
        exp = np.array([
            pol0.CTC_c[0],
            2000,
            2000 * (1 + pol2.inflation_rates(year=2022))
        ]).round(2)

        np.testing.assert_allclose(pol2.CTC_c, exp)

    def test_apply_cpi_offset(self):
        """
        Test applying the parameter_indexing_CPI_offset parameter
        without any other parameters.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {"parameter_indexing_CPI_offset": {2021: -0.001}}
        )

        pol2 = Policy()
        pol2.adjust(
            {"parameter_indexing_CPI_offset": [
                {"year": 2021, "value": -0.001}
            ]}
        )

        cmp_policy_objs(pol1, pol2)

        pol0 = Policy()
        pol0.implement_reform({"parameter_indexing_CPI_offset": {2021: 0}})

        init_rates = pol0.inflation_rates()
        new_rates = pol2.inflation_rates()

        start_ix = 2021 - pol2.start_year

        exp_rates = copy.deepcopy(new_rates)
        exp_rates[start_ix:] -= pol2._parameter_indexing_CPI_offset[start_ix:]
        np.testing.assert_allclose(init_rates, exp_rates)

        # make sure values prior to 2021 were not affected.
        cmp_policy_objs(pol0, pol2, year_range=range(pol2.start_year, 2021))

        pol2.set_state(year=[2021, 2022])
        np.testing.assert_equal(
            (pol2.EITC_c[1] / pol2.EITC_c[0] - 1).round(4),
            pol0.inflation_rates(year=2021) + (-0.001),
        )

    def test_multiple_cpi_swaps(self):
        """
        Test changing a parameter's indexed status multiple times.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {
                "II_em": {2016: 6000, 2018: 7500, 2020: 9000},
                "II_em-indexed": {2016: False, 2018: True},
            }
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "II_em": [
                    {"year": 2016, "value": 6000},
                    {"year": 2018, "value": 7500},
                    {"year": 2020, "value": 9000},
                ],
                "II_em-indexed": [
                    {"year": 2016, "value": False},
                    {"year": 2018, "value": True},
                ],
            }
        )

        cmp_policy_objs(pol1, pol2)

        # check inflation is not applied.
        pol2.set_state(year=[2016, 2017])
        np.testing.assert_equal(
            pol2.II_em[0], pol2.II_em[1]
        )

        # check inflation rate is applied.
        pol2.set_state(year=[2018, 2019])
        np.testing.assert_equal(
            (pol2.II_em[1] / pol2.II_em[0] - 1).round(4),
            pol2.inflation_rates(year=2018),
        )

        # check inflation rate applied for rest of window.
        window = list(range(2020, pol2.end_year + 1))
        pol2.set_state(year=window)
        np.testing.assert_equal(
            (pol2.II_em[1:] / pol2.II_em[:-1] - 1).round(4),
            [pol2.inflation_rates(year=year) for year in window[:-1]],
        )

    def test_multiple_cpi_swaps2(self):
        """
        Test changing the indexed status of multiple parameters multiple
        times.
        """
        pol1 = Policy()
        pol1.implement_reform(
            {
                "II_em": {2016: 6000, 2018: 7500, 2020: 9000},
                "II_em-indexed": {2016: False, 2018: True},
                "SS_Earnings_c": {2016: 300000, 2018: 500000},
                "SS_Earnings_c-indexed": {2017: False, 2019: True},
                "AMT_em-indexed": {2017: False, 2020: True},
            }
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "SS_Earnings_c": [
                    {"year": 2016, "value": 300000},
                    {"year": 2018, "value": 500000},
                ],
                "SS_Earnings_c-indexed": [
                    {"year": 2017, "value": False},
                    {"year": 2019, "value": True},
                ],
                "AMT_em-indexed": [
                    {"year": 2017, "value": False},
                    {"year": 2020, "value": True},
                ],
                "II_em": [
                    {"year": 2016, "value": 6000},
                    {"year": 2018, "value": 7500},
                    {"year": 2020, "value": 9000},
                ],
                "II_em-indexed": [
                    {"year": 2016, "value": False},
                    {"year": 2018, "value": True},
                ],
            }
        )

        cmp_policy_objs(pol1, pol2)

        # Test SS_Earnings_c
        # check inflation is still applied from 2016 to 2017.
        pol2.set_state(year=[2016, 2017])
        np.testing.assert_equal(
            (pol2.SS_Earnings_c[1] / pol2.SS_Earnings_c[0] - 1).round(4),
            pol2.wage_growth_rates(year=2016),
        )

        # check inflation rate is not applied after adjustment in 2018.
        pol2.set_state(year=[2018, 2019])
        np.testing.assert_equal(
            pol2.SS_Earnings_c[0], pol2.SS_Earnings_c[1]
        )

        # check inflation rate applied for rest of window.
        window = list(range(2019, pol2.end_year + 1))
        pol2.set_state(year=window)
        np.testing.assert_equal(
            (pol2.SS_Earnings_c[1:] / pol2.SS_Earnings_c[:-1] - 1).round(4),
            [pol2.wage_growth_rates(year=year) for year in window[:-1]],
        )

        # Test AMT
        # Check values for 2017 through 2020 are equal.
        pol2.set_state(year=[2017, 2018, 2019, 2020])
        for i in (1, 2, 3):
            np.testing.assert_equal(
                pol2.AMT_em[0], pol2.AMT_em[i]
            )

        # check inflation rate applied for rest of window.
        window = list(range(2020, pol2.end_year + 1))
        pol2.set_state(year=window)
        # repeat inflation rates accross matrix so they can be compared to the
        # rates derived from AMT_em, a 5 * N matrix.
        exp_rates = [pol2.inflation_rates(year=year) for year in window[:-1]]
        exp_rates = np.tile([exp_rates], (5, 1)).transpose()
        np.testing.assert_equal(
            (pol2.AMT_em[1:] / pol2.AMT_em[:-1] - 1).round(4),
            exp_rates,
        )

        # Test II_em
        # check inflation is not applied.
        pol2.set_state(year=[2016, 2017])
        np.testing.assert_equal(
            pol2.II_em[0], pol2.II_em[1]
        )

        # check inflation rate is applied.
        pol2.set_state(year=[2018, 2019])
        np.testing.assert_equal(
            (pol2.II_em[1] / pol2.II_em[0] - 1).round(4),
            pol2.inflation_rates(year=2018),
        )

        # check inflation rate applied for rest of window.
        window = list(range(2020, pol2.end_year + 1))
        pol2.set_state(year=window)
        np.testing.assert_equal(
            (pol2.II_em[1:] / pol2.II_em[:-1] - 1).round(4),
            [pol2.inflation_rates(year=year) for year in window[:-1]],
        )

    def test_adj_CPI_offset_and_index_status(self):
        """
        Test changing parameter_indexing_CPI_offset and another
        parameter simultaneously.
        """
        pol1 = Policy()
        pol1.implement_reform({
            "CTC_c-indexed": {2020: True},
            "parameter_indexing_CPI_offset": {2020: -0.005}},
        )

        pol2 = Policy()
        pol2.adjust(
            {
                "parameter_indexing_CPI_offset":
                    [{"year": 2020, "value": -0.005}],
                "CTC_c-indexed": [{"year": 2020, "value": True}],
            }
        )

        cmp_policy_objs(pol1, pol2)

        # Check no difference prior to 2020
        pol0 = Policy()
        pol0.implement_reform({"parameter_indexing_CPI_offset": {2020: 0}})
        cmp_policy_objs(
            pol0,
            pol2,
            year_range=range(pol2.start_year, 2020 + 1),
            exclude=["parameter_indexing_CPI_offset"]
        )

        pol2.set_state(year=[2021, 2022])
        np.testing.assert_equal(
            (pol2.CTC_c[1] / pol2.CTC_c[0] - 1).round(4),
            pol0.inflation_rates(year=2021) + (-0.005),
        )

    def test_adj_related_parameters_and_index_status(self):
        """
        Test changing two related parameters simulataneously and
        one of their indexed statuses.
        """

        pol = Policy()
        pol.adjust(
            {
                "II_brk7-indexed": [{"year": 2020, "value": True}],
                # Update II_brk5 in 2026 to make reform valid after reset.
                "II_brk5": [{"value": 330000, "MARS": "single", "year": 2026}],
                "II_brk6": [{"value": 316700, "MARS": "single", "year": 2020}],
                "II_brk7": [{"value": 445400, "MARS": "single", "year": 2020}],
            }
        )

        # Check no difference prior to 2020
        pol0 = Policy()
        cmp_policy_objs(
            pol0,
            pol,
            year_range=range(pol.start_year, 2019 + 1),
        )

        res = (
            (pol.sel["II_brk6"]["MARS"] == "single")
            & (pol.sel["II_brk6"]["year"] == 2020)
        )
        assert res.isel[0]["value"] == [316700]
        res = (
            (pol.sel["II_brk7"]["MARS"] == "single")
            & (pol.sel["II_brk7"]["year"] == 2020)
        )
        assert res.isel[0]["value"] == [445400]

        II_brk7 = pol.to_array("II_brk7", year=[2021, 2022])
        II_brk7_single = II_brk7[:, 0]
        np.testing.assert_equal(
            (II_brk7_single[1] / II_brk7_single[0] - 1).round(4),
            pol.inflation_rates(year=2021),
        )

    def test_indexed_status_parsing(self):
        pol1 = Policy()

        pol1.implement_reform({"EITC_c-indexed": {pol1.start_year: False}})

        pol2 = Policy()
        pol2.adjust({"EITC_c-indexed": False})

        cmp_policy_objs(pol1, pol2)

        with pytest.raises(pt.ValidationError):
            pol2.adjust({"EITC_c-indexed": 123})
