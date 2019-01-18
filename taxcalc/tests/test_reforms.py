"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pycodestyle test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

import os
import glob
import json
import time
import numpy as np
import pytest
# pylint: disable=import-error
from taxcalc import Calculator, Policy, Records, DIST_TABLE_COLUMNS
from taxcalc import nonsmall_diffs


def test_reform_json_and_output(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform method that
    generates no parameter_errors.
    Then use each reform to generate static tax results for small set of
    filing units in a single tax_year and compare those results with
    expected results from a text file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    used_dist_stats = ['c00100',  # AGI
                       'c04600',  # personal exemptions
                       'standard',  # standard deduction
                       'c04800',  # regular taxable income
                       'c05800',  # income tax before credits
                       'iitax',  # income tax after credits
                       'payrolltax',  # payroll taxes
                       'aftertax_income']  # aftertax expanded income
    unused_dist_stats = set(DIST_TABLE_COLUMNS) - set(used_dist_stats)
    renamed_columns = {'c00100': 'AGI',
                       'c04600': 'pexempt',
                       'standard': 'stdded',
                       'c04800': 'taxinc',
                       'c05800': 'tax-wo-credits',
                       'iitax': 'inctax',
                       'payrolltax': 'paytax',
                       'aftertax_income': 'ataxinc'}

    # embedded function used only in test_reform_json_and_output
    def write_distribution_table(calc, resfilename):
        """
        Write abbreviated distribution table calc to file with resfilename.
        """
        dist, _ = calc.distribution_tables(None, 'standard_income_bins',
                                           scaling=False)
        for stat in unused_dist_stats:
            del dist[stat]
        dist = dist[used_dist_stats]
        dist.rename(mapper=renamed_columns, axis='columns', inplace=True)
        with open(resfilename, 'w') as resfile:
            dist.to_string(resfile, float_format='%7.0f')

    # embedded function used only in test_reform_json_and_output
    def res_and_out_are_same(base):
        """
        Return True if base.res and base.out file contents are the same;
        return False if base.res and base.out file contents differ.
        """
        with open(base + '.res') as resfile:
            act_res = resfile.read()
        with open(base + '.out') as outfile:
            exp_res = outfile.read()
        # check to see if act_res & exp_res have differences
        return not nonsmall_diffs(act_res.splitlines(True),
                                  exp_res.splitlines(True))
    # specify Records object containing cases data
    tax_year = 2020
    cases_path = os.path.join(tests_path, '..', 'reforms', 'cases.csv')
    cases = Records(data=cases_path,
                    gfactors=None,  # keeps raw data unchanged
                    weights=None,
                    adjust_ratios=None,
                    start_year=tax_year)  # set raw input data year
    # specify list of reform failures
    failures = list()
    # specify current-law-policy Calculator object
    calc1 = Calculator(policy=Policy(), records=cases, verbose=False)
    calc1.advance_to_year(tax_year)
    calc1.calc_all()
    res_path = cases_path.replace('cases.csv', 'clp.res')
    write_distribution_table(calc1, res_path)
    if res_and_out_are_same(res_path.replace('.res', '')):
        os.remove(res_path)
    else:
        failures.append(res_path)
    # read 2017_law.json reform file and specify its parameters dictionary
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Calculator.read_json_param_objects(pre_tcja_jrf, None)
    # check reform file contents and reform results for each reform
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    json_reform_files = glob.glob(reforms_path)
    for jrf in json_reform_files:
        # determine reform's baseline by reading contents of jrf
        with open(jrf, 'r') as rfile:
            jrf_text = rfile.read()
            pre_tcja_baseline = 'Reform_Baseline: 2017_law.json' in jrf_text
        # implement the reform relative to its baseline
        reform = Calculator.read_json_param_objects(jrf_text, None)
        pol = Policy()  # current-law policy
        if pre_tcja_baseline:
            pol.implement_reform(pre_tcja['policy'])
        pol.implement_reform(reform['policy'])
        assert not pol.parameter_errors
        calc2 = Calculator(policy=pol, records=cases, verbose=False)
        calc2.advance_to_year(tax_year)
        calc2.calc_all()
        res_path = jrf.replace('.json', '.res')
        write_distribution_table(calc2, res_path)
        if res_and_out_are_same(res_path.replace('.res', '')):
            os.remove(res_path)
        else:
            failures.append(res_path)
    if failures:
        msg = 'Following reforms have res-vs-out differences:\n'
        for ref in failures:
            msg += '{}\n'.format(os.path.basename(ref))
        raise ValueError(msg)


def reform_results(rid, reform_dict, puf_data, reform_2017_law):
    """
    Return actual results of the reform specified by rid and reform_dict.
    """
    # pylint: disable=too-many-locals
    rec = Records(data=puf_data)
    # create baseline Calculator object, calc1
    pol = Policy()
    if reform_dict['baseline'] == '2017_law.json':
        pol.implement_reform(reform_2017_law)
    elif reform_dict['baseline'] == 'policy_current_law.json':
        pass
    else:
        msg = 'illegal baseline value {}'
        raise ValueError(msg.format(reform_dict['baseline']))
    calc1 = Calculator(policy=pol, records=rec, verbose=False)
    # create reform Calculator object, calc2
    start_year = reform_dict['start_year']
    reform = {start_year: reform_dict['value']}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec, verbose=False)
    # increment both Calculator objects to reform's start_year
    calc1.advance_to_year(start_year)
    calc2.advance_to_year(start_year)
    # calculate baseline and reform output for several years
    output_type = reform_dict['output_type']
    num_years = 4
    results = list()
    for _ in range(0, num_years):
        calc1.calc_all()
        baseline = calc1.array(output_type)
        calc2.calc_all()
        reform = calc2.array(output_type)
        diff = reform - baseline
        weighted_sum_diff = (diff * calc1.array('s006')).sum() * 1.0e-9
        results.append(weighted_sum_diff)
        calc1.increment_year()
        calc2.increment_year()
    # write actual results to actual_str
    actual_str = '{}'.format(rid)
    for iyr in range(0, num_years):
        actual_str += ',{:.1f}'.format(results[iyr])
    return actual_str


@pytest.fixture(scope='module', name='baseline_2017_law')
def fixture_baseline_2017_law(tests_path):
    """
    Read ../reforms/2017_law.json and return its policy dictionary.
    """
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Calculator.read_json_param_objects(pre_tcja_jrf, None)
    return pre_tcja['policy']


@pytest.fixture(scope='module', name='reforms_dict')
def fixture_reforms_dict(tests_path):
    """
    Read reforms.json and convert to dictionary.
    """
    reforms_path = os.path.join(tests_path, 'reforms.json')
    with open(reforms_path, 'r') as rfile:
        rjson = rfile.read()
    return json.loads(rjson)


NUM_REFORMS = 64
NUM_VOID_REFORMS = 1

@pytest.mark.one
@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('rid', [i for i in range(1, NUM_REFORMS + 1)])
def test_reform(rid, tests_path, baseline_2017_law,
                reforms_dict, puf_subsample):
    """
    Compare actual and expected results for specified reform in reforms_dict.
    """
    # pylint: disable=too-many-locals
    # remove actual files at start
    actfile_path = os.path.join(tests_path, 'reforms_actual.csv')
    afiles = os.path.join(tests_path, 'reform_actual_*.csv')
    if rid == 1:
        if os.path.isfile(actfile_path):
            os.remove(actfile_path)
        for afile in glob.glob(afiles):
            os.remove(afile)
    # conduct test for rid writing actual results to a file
    if reforms_dict[str(rid)] != dict():
        actual = reform_results(rid, reforms_dict[str(rid)],
                                puf_subsample, baseline_2017_law)
        afile_path = os.path.join(tests_path,
                                  'reform_actual_{}.csv'.format(rid))
        with open(afile_path, 'w') as afile:
            afile.write('rid,res1,res2,res3,res4\n')
            afile.write('{}\n'.format(actual))
    # compare actual and expected results at end
    if rid == NUM_REFORMS:
        # ... wait until all reform_actual_*.csv files are written
        number_of_reforms = NUM_REFORMS - NUM_VOID_REFORMS
        wait_secs = 2
        max_waits = 20
        for _ in range(0, max_waits):
            time.sleep(wait_secs)
            if len(glob.glob(afiles)) == number_of_reforms:
                break   # out of for loop
        assert len(glob.glob(afiles)) == number_of_reforms
        # ... read expected results
        efile_path = os.path.join(tests_path, 'reforms_expect.csv')
        with open(efile_path, 'r') as efile:
            expect_lines = efile.readlines()
        # ... compare actual and expected results for each test
        differences = False
        actfile = open(actfile_path, 'w')
        actfile.write('rid,res1,res2,res3,res4\n')
        idx = 1  # expect_lines list index
        for rnum in range(1, NUM_REFORMS + 1):
            if reforms_dict[str(rnum)] != dict():
                afile_path = os.path.join(tests_path,
                                          'reform_actual_{}.csv'.format(rnum))
                with open(afile_path, 'r') as afile:
                    actual_lines = afile.readlines()
                os.remove(afile_path)
                actfile.write(actual_lines[1])
                actual = [float(itm) for itm in actual_lines[1].split(',')]
                expect = [float(itm) for itm in expect_lines[idx].split(',')]
                if not np.allclose(actual, expect, atol=0.0, rtol=0.0):
                    differences = True
                idx += 1
        actfile.close()
        # ... remove 'reforms_actual.csv' file if no differences
        if differences:
            assert 'reforms_actual.csv' == 'reform_expect.csv'
        else:
            os.remove(actfile_path)
