"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

import os
import glob
import json
import pytest
from taxcalc import Calculator, Policy  # pylint: disable=import-error
from taxcalc import Records, Behavior  # pylint: disable=import-error


def test_reform_json(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform() method.
    """
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    for jpf in glob.glob(reforms_path):
        # read contents of jpf (JSON parameter filename)
        jfile = open(jpf, 'r')
        jpf_text = jfile.read()
        # check that jpf_text has "policy" that can be implemented as a reform
        if '"policy"' in jpf_text:
            gdiffbase = {}
            gdiffresp = {}
            # pylint: disable=protected-access
            policy_dict = (
                Calculator._read_json_policy_reform_text(jpf_text,
                                                         gdiffbase, gdiffresp)
            )
            policy = Policy()
            policy.implement_reform(policy_dict)
        else:  # jpf_text is not a valid JSON policy reform file
            print('test-failing-filename: ' +
                  jpf)
            assert False


def reform_results(reform_dict, puf_data):
    """
    Return actual results of the reform specified in reform_dict.
    """
    # pylint: disable=too-many-locals
    # create current-law-policy Calculator object
    pol = Policy()
    rec = Records(data=puf_data)
    calc1 = Calculator(policy=pol, records=rec, verbose=False, behavior=None)
    # create reform Calculator object with possible behavioral responses
    start_year = reform_dict['start_year']
    beh = Behavior()
    if '_BE_cg' in reform_dict['value']:
        elasticity = reform_dict['value']['_BE_cg']
        del reform_dict['value']['_BE_cg']  # in order to have a valid reform
        beh_assump = {start_year: {'_BE_cg': elasticity}}
        beh.update_behavior(beh_assump)
    reform = {start_year: reform_dict['value']}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec, verbose=False, behavior=beh)
    # increment both calculators to reform's start_year
    calc1.advance_to_year(start_year)
    calc2.advance_to_year(start_year)
    # calculate prereform and postreform output for several years
    output_type = reform_dict['output_type']
    num_years = 4
    results = list()
    for _ in range(0, num_years):
        calc1.calc_all()
        prereform = calc1.array(output_type)
        if calc2.behavior.has_response():
            calc_clp = calc2.current_law_version()
            calc2_br = Behavior.response(calc_clp, calc2)
            postreform = calc2_br.array(output_type)
        else:
            calc2.calc_all()
            postreform = calc2.array(output_type)
        diff = postreform - prereform
        weighted_sum_diff = (diff * calc1.array('s006')).sum() * 1.0e-9
        results.append(weighted_sum_diff)
        calc1.increment_year()
        calc2.increment_year()
    # write actual results to actual_str
    actual_str = 'Tax-Calculator'
    for iyr in range(0, num_years):
        actual_str += ',{:.1f}'.format(results[iyr])
    return actual_str


@pytest.fixture(scope='module', name='reforms_dict')
def fixture_reforms_dict(tests_path):
    """
    Read reforms.json and convert to dictionary.
    """
    reforms_path = os.path.join(tests_path, 'reforms.json')
    with open(reforms_path, 'r') as rfile:
        rjson = rfile.read()
    return json.loads(rjson)


NUM_REFORMS = 62


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('rid', [i for i in range(1, NUM_REFORMS + 1)])
def test_reform(rid, reforms_dict, puf_subsample):
    """
    Compare actual and expected results for specified reform in reforms_dict.
    """
    reform_id = str(rid)
    actual = reform_results(reforms_dict[reform_id], puf_subsample)
    assert actual == reforms_dict[reform_id]['expected']
