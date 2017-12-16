"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

from __future__ import print_function
import os
import glob
import json
import pytest
from taxcalc import Calculator, Policy  # pylint: disable=import-error
from taxcalc import Records, Behavior  # pylint: disable=import-error

@pytest.mark.one
def test_reform_json_and_output(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform() method that
    generates no reform_errors.
    Then use each reform to generate static tax results for small set of
    filing units in a single tax_year and compare those results with
    expected results from a text file.
    """
    # pylint: disable=too-many-locals
    # set tracing to True to see test output rather than writing to files
    tracing = False # setting to True force test failure
    # specify Records object containing cases data
    tax_year = 2020
    cases_path = os.path.join(tests_path, '..', 'reforms', 'cases.csv')
    cases = Records(data=cases_path,
                    gfactors=None,  # keeps raw data unchanged
                    weights=None,
                    adjust_ratios=None,
                    start_year=tax_year)  # set raw input data year
    # specify current-law-policy Calculator object
    calc1 = Calculator(policy=Policy(), records=cases, verbose=False)
    calc1.advance_to_year(tax_year)
    calc1.calc_all()
    dist1, _ = calc1.distribution_tables(calc=None,
                                         groupby='large_income_bins')
    if tracing:
        print('TRACING: current-law-policy distribution table:')
        print(dist1)
    else:
        outfilename = 'clp.out'
        out_path = os.path.join(tests_path, '..', 'reforms', 'clp.out')
        with open(out_path,'w') as outfile:
            dist1.to_string(outfile)
    # check reform file contents and reform results for each reform
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    for jrf in glob.glob(reforms_path):
        # read contents of jrf (JSON reform file)
        with open(jrf, 'r') as jfile:
            jrf_text = jfile.read()
        # check that jrf_text has "policy" that can be implemented as a reform
        if '"policy"' in jrf_text:
            gdiffbase = {}
            gdiffresp = {}
            # pylint: disable=protected-access
            policy_dict = (
                Calculator._read_json_policy_reform_text(jrf_text,
                                                         gdiffbase, gdiffresp)
            )
            pol = Policy()
            pol.implement_reform(policy_dict)
            calc2 = Calculator(policy=pol, records=cases, verbose=False)
            calc2.advance_to_year(tax_year)
            calc2.calc_all()
            diff = calc1.difference_table(calc2,
                                          groupby='large_income_bins')
            del diff['perc_aftertax']
            if tracing:
                print('TRACING: difference table '
                      'for reform in {}:'.format(os.path.basename(jrf)))
                print(diff)
            else:
                outname = os.path.basename(jrf).replace('.json', '.out')
                out_path = os.path.join(tests_path, '..', 'reforms', outname)
                with open(out_path,'w') as outfile:
                    diff.to_string(outfile)
        else:  # jrf_text has no "policy" key
            print('ERROR: missing policy key in file: ' +
                  os.path.basename(jrf))
            assert False
    if tracing:
        print('TRACING: end-of-test failure so can see printed output')
        assert 1 == 2


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
