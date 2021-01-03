# CODING-STYLE CHECKS:
# pycodestyle test_growdiff.py

import os
import json
import numpy as np
import pytest
from taxcalc import GrowDiff, GrowFactors, Policy


def test_year_consistency():
    assert GrowDiff.JSON_START_YEAR == Policy.JSON_START_YEAR
    assert GrowDiff.DEFAULT_NUM_YEARS == Policy.DEFAULT_NUM_YEARS


def test_update_and_apply_growdiff():
    gdiff = GrowDiff()
    # update GrowDiff instance
    diffs = {
        'AWAGE': {2014: 0.01,
                  2016: 0.02}
    }
    gdiff.update_growdiff(diffs)
    expected_wage_diffs = [0.00, 0.00, 0.00, 0.01, 0.01, 0.02, 0.02]
    extra_years = GrowDiff.DEFAULT_NUM_YEARS - len(expected_wage_diffs)
    expected_wage_diffs.extend([0.02] * extra_years)
    assert np.allclose(gdiff._AWAGE, expected_wage_diffs, atol=0.0, rtol=0.0)
    # apply growdiff to GrowFactors instance
    gf = GrowFactors()
    syr = GrowDiff.JSON_START_YEAR
    nyrs = GrowDiff.DEFAULT_NUM_YEARS
    lyr = syr + nyrs - 1
    pir_pre = gf.price_inflation_rates(syr, lyr)
    wgr_pre = gf.wage_growth_rates(syr, lyr)
    gfactors = GrowFactors()
    gdiff.apply_to(gfactors)
    pir_pst = gfactors.price_inflation_rates(syr, lyr)
    wgr_pst = gfactors.wage_growth_rates(syr, lyr)
    expected_wgr_pst = [wgr_pre[i] + expected_wage_diffs[i]
                        for i in range(0, nyrs)]
    assert np.allclose(pir_pre, pir_pst, atol=0.0, rtol=0.0)
    assert np.allclose(wgr_pst, expected_wgr_pst, atol=1.0e-9, rtol=0.0)


def test_has_any_response():
    start_year = GrowDiff.JSON_START_YEAR
    gdiff = GrowDiff()
    assert gdiff.current_year == start_year
    assert gdiff.has_any_response() is False
    gdiff.update_growdiff({'AWAGE': {2020: 0.01}})
    assert gdiff.current_year == start_year
    assert gdiff.has_any_response() is True


def test_description_punctuation(tests_path):
    """
    Check that each description ends in a period.
    """
    # read JSON file into a dictionary
    path = os.path.join(tests_path, '..', 'growdiff.json')
    with open(path, 'r') as jsonfile:
        dct = json.load(jsonfile)
    all_desc_ok = True
    for param in dct.keys():
        if param == "schema":
            continue
        if not dct[param]['description'].endswith('.'):
            all_desc_ok = False
            print('param,description=',
                  str(param),
                  dct[param]['description'])
    assert all_desc_ok


def test_boolean_value_infomation(tests_path):
    """
    Check consistency of boolean_value in growdiff.json file.
    """
    # read growdiff.json file into a dictionary
    path = os.path.join(tests_path, '..', 'growdiff.json')
    with open(path, 'r') as gddfile:
        gdd = json.load(gddfile)
    for param in gdd.keys():
        if param == "schema":
            continue
        val = gdd[param]['value']
        if isinstance(val, list):
            val = val[0]
            if isinstance(val, list):
                val = val[0]
        valstr = str(val)
        if valstr == 'True' or valstr == 'False':
            val_is_boolean = True
        else:
            val_is_boolean = False
        type_is_boolean = gdd[param]['type'] == 'bool'
        if val_is_boolean and not type_is_boolean:
            print('param,value_type,val,val_is_boolean=',
                  str(param),
                  gdd[param]['value_type'],
                  val,
                  val_is_boolean)
