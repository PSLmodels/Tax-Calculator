"""
Tests all the example JSON parameter files located in taxcalc/reforms directory
      and all the JSON parameter files located in taxcalc/taxbrain directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

import os
import glob
import pytest
# pylint: disable=import-error
from taxcalc import Calculator, Policy, Consumption, Behavior, Growdiff


@pytest.fixture(scope='session')
def reforms_path(tests_path):
    """
    Return path to taxcalc/reforms/*.json files
    """
    return os.path.join(tests_path, '..', 'reforms', '*.json')


def test_reforms(reforms_path):  # pylint: disable=redefined-outer-name
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform() method.
    While doing this, construct a set of Policy parameters (other than those
    ending in '_cpi') included in the JSON reform files.
    """
    params_set = set()
    for jrf in glob.glob(reforms_path):
        # read contents of jrf (JSON reform filename)
        jfile = open(jrf, 'r')
        jrf_text = jfile.read()
        # check that jrf_text has "policy" that can be implemented as a reform
        policy_dict = Calculator.read_json_policy_reform_text(jrf_text)
        policy = Policy()
        policy.implement_reform(policy_dict)
        # identify "policy" parameters included in jrf
        for year in policy_dict.keys():
            if year == 0:
                continue  # skip param_code info which is marked with year zero
            policy_year_dict = policy_dict[year]
            for param in policy_year_dict.keys():
                if param.endswith('_cpi'):
                    continue  # skip "policy" parameters ending in _cpi
                params_set.add(param)
    # FUTURE: compare params_set to parameters in current_law_policy.json
    assert len(params_set) > 0


@pytest.fixture(scope='session')
def taxbrain_path(tests_path):
    """
    Return path to taxcalc/taxbrain/*.json files
    """
    return os.path.join(tests_path, '..', 'taxbrain', '*.json')


def test_taxbrain_json(taxbrain_path):  # pylint: disable=redefined-outer-name
    """
    Check that each JSON parameter file can be converted into dictionaries
    that can be used to construct objects needed for a Calculator object.
    """
    for jpf in glob.glob(taxbrain_path):
        # read contents of jpf (JSON parameter filename)
        jfile = open(jpf, 'r')
        jpf_text = jfile.read()
        # check that jpf_text can be used to construct objects
        if '"policy"' in jpf_text:
            pol = Calculator.read_json_policy_reform_text(jpf_text)
            policy = Policy()
            policy.implement_reform(pol)
        elif ('"consumption"' in jpf_text and
              '"behavior"' in jpf_text and
              '"growdiff_baseline"' in jpf_text and
              '"growdiff_response"' in jpf_text):
            (con, beh, gdiff_base,
             gdiff_resp) = Calculator.read_json_econ_assump_text(jpf_text)
            cons = Consumption()
            cons.update_consumption(con)
            behv = Behavior()
            behv.update_behavior(beh)
            growdiff_baseline = Growdiff()
            growdiff_baseline.update_growdiff(gdiff_base)
            growdiff_response = Growdiff()
            growdiff_response.update_growdiff(gdiff_resp)
        else:  # jpf_text is not a valid JSON parameter file
            print('test-failing-filename: ' +
                  jpf)
            assert False
