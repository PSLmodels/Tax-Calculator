"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

from __future__ import print_function
import os
import sys
import glob
import json
import pytest
# pylint: disable=import-error
from taxcalc import Calculator, Policy, Records, Behavior
from taxcalc import line_diff_list


def test_reform_json_and_output(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform() method that
    generates no reform_errors.
    Then use each reform to generate static tax results for small set of
    filing units in a single tax_year and compare those results with
    expected results from a text file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    def res_and_out_are_same(base):
        """
        Return true if base.res and base.out file contents are the same;
        return false if base.res and base.out file contents differ.
        """
        with open(base + '.out') as outfile:
            exp_res = outfile.read()
        exp = exp_res.splitlines(True)
        with open(base + '.res') as resfile:
            act_res = resfile.read()
        act = act_res.splitlines(True)
        # assure act & exp line lists have differences less than "small" value
        epsilon = 1e-6
        if sys.version_info.major == 2:
            small = epsilon  # tighter test for Python 2.7
        else:
            small = 0.10 + epsilon  # looser test for Python 3.6
        diff_lines = list()
        assert len(act) == len(exp)
        for actline, expline in zip(act, exp):
            if actline == expline:
                continue
            diffs = line_diff_list(actline, expline, small)
            if diffs:
                diff_lines.extend(diffs)
        if diff_lines:
            return False
        return True
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
    fails = list()
    res_path = os.path.join(tests_path, '..', 'reforms', 'clp.res')
    with open(res_path, 'w') as resfile:
        dist1.to_string(resfile)
    if res_and_out_are_same(res_path.replace('.res', '')):
        os.remove(res_path)
    else:
        fails.append(res_path)
    # check reform file contents and reform results for each reform
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    json_reform_files = glob.glob(reforms_path)
    for jrf in json_reform_files:
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
            resname = os.path.basename(jrf).replace('.json', '.res')
            res_path = os.path.join(tests_path, '..', 'reforms', resname)
            with open(res_path, 'w') as resfile:
                diff.to_string(resfile)
            if res_and_out_are_same(res_path.replace('.res', '')):
                os.remove(res_path)
            else:
                fails.append(res_path)
        else:  # jrf_text has no "policy" key
            msg = 'ERROR: missing policy key in file: {}'
            raise ValueError(msg.format(os.path.basename(jrf)))
    if fails:
        msg = 'Following reforms have res-vs-out differences:\n'
        for ref in fails:
            msg += '{}\n'.format(os.path.basename(ref))
        raise ValueError(msg)


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
