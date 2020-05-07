"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pycodestyle test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

import os
import glob
import json
import pytest
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxcalc import Calculator, Policy, Records


def test_2017_law_reform(tests_path):
    """
    Check that policy parameter values in a future year under current-law
    policy and under the reform specified in the 2017_law.json file are
    sensible.
    """
    # create pre metadata dictionary for 2017_law.json reform in fyear
    pol = Policy()
    reform_file = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    with open(reform_file, 'r') as rfile:
        rtext = rfile.read()
    pol.implement_reform(Policy.read_json_reform(rtext))
    assert not pol.parameter_warnings
    pol.set_year(2018)
    pre_mdata = dict(pol.items())
    # check some policy parameter values against expected values under 2017 law
    pre_expect = {
        # relation '<' implies asserting that actual < expect
        # relation '>' implies asserting that actual > expect
        # ... parameters not affected by TCJA and that are not indexed
        'AMEDT_ec': {'relation': '=', 'value': 200000},
        'SS_thd85': {'relation': '=', 'value': 34000},
        # ... parameters not affected by TCJA and that are indexed
        'STD_Dep': {'relation': '>', 'value': 1050},
        'CG_brk2': {'relation': '>', 'value': 425800},
        'AMT_CG_brk1': {'relation': '>', 'value': 38600},
        'AMT_brk1': {'relation': '>', 'value': 191100},
        'EITC_c': {'relation': '>', 'value': 519},
        'EITC_ps': {'relation': '>', 'value': 8490},
        'EITC_ps_MarriedJ': {'relation': '>', 'value': 5680},
        'EITC_InvestIncome_c': {'relation': '>', 'value': 3500},
        # ... parameters affected by TCJA and that are not indexed
        'ID_Charity_crt_all': {'relation': '=', 'value': 0.5},
        'II_rt3': {'relation': '=', 'value': 0.25},
        # ... parameters affected by TCJA and that are indexed
        'II_brk3': {'relation': '>', 'value': 91900},
        'STD': {'relation': '<', 'value': 7000},
        'II_em': {'relation': '>', 'value': 4050},
        'AMT_em_pe': {'relation': '<', 'value': 260000}
    }
    assert isinstance(pre_expect, dict)
    assert set(pre_expect.keys()).issubset(set(pre_mdata.keys()))
    for name in pre_expect:
        aval = pre_mdata[name]
        if aval.ndim == 2:
            act = aval[0][0]  # comparing only first item in a vector parameter
        else:
            act = aval[0]
        exp = pre_expect[name]['value']
        if pre_expect[name]['relation'] == '<':
            assert act < exp, '{} a={} !< e={}'.format(name, act, exp)
        elif pre_expect[name]['relation'] == '>':
            assert act > exp, '{} a={} !> e={}'.format(name, act, exp)
        elif pre_expect[name]['relation'] == '=':
            assert act == exp, '{} a={} != e={}'.format(name, act, exp)


def test_round_trip_tcja_reform(tests_path):
    """
    Check that current-law policy has the same policy parameter values in
    a future year as does a compound reform that first implements the
    reform specified in the 2017_law.json file and then implements the
    reform specified in the TCJA.json file.  This test checks that the
    future-year parameter values for current-law policy (which incorporates
    TCJA) are the same as future-year parameter values for the compound
    round-trip reform.  Doing this check ensures that the 2017_law.json
    and TCJA.json reform files are specified in a consistent manner.
    """
    # pylint: disable=too-many-locals
    fyear = 2020
    # create clp metadata dictionary for current-law policy in fyear
    pol = Policy()
    pol.set_year(fyear)
    clp_mdata = dict(pol.items())
    # create rtr metadata dictionary for round-trip reform in fyear
    pol = Policy()
    reform_file = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    with open(reform_file, 'r') as rfile:
        rtext = rfile.read()
    pol.implement_reform(Policy.read_json_reform(rtext))

    assert not pol.parameter_warnings
    assert not pol.errors
    reform_file = os.path.join(tests_path, '..', 'reforms', 'TCJA.json')
    with open(reform_file, 'r') as rfile:
        rtext = rfile.read()
    pol.implement_reform(Policy.read_json_reform(rtext))
    assert not pol.parameter_warnings
    assert not pol.errors
    pol.set_year(fyear)
    rtr_mdata = dict(pol.items())
    # compare fyear policy parameter values
    assert clp_mdata.keys() == rtr_mdata.keys()
    fail_dump = False
    if fail_dump:
        rtr_fails = open('fails_rtr', 'w')
        clp_fails = open('fails_clp', 'w')
    fail_params = list()
    msg = '\nRound-trip-reform and current-law-policy param values differ for:'
    for pname in clp_mdata.keys():
        rtr_val = rtr_mdata[pname]
        clp_val = clp_mdata[pname]
        if not np.allclose(rtr_val, clp_val):
            fail_params.append(pname)
            msg += '\n  {} in {} : rtr={} clp={}'.format(
                pname, fyear, rtr_val, clp_val
            )
            if fail_dump:
                rtr_fails.write('{} {} {}\n'.format(pname, fyear, rtr_val))
                clp_fails.write('{} {} {}\n'.format(pname, fyear, clp_val))
    if fail_dump:
        rtr_fails.close()
        clp_fails.close()
    if fail_params:
        raise ValueError(msg)


def test_reform_json_and_output(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform method that
    generates no parameter_errors.
    Then use each reform to generate static tax results for small set of
    filing units in a single tax_year and compare those results with
    expected results from a CSV-formatted file.
    """
    # pylint: disable=too-many-statements,too-many-locals

    # embedded function used only in test_reform_json_and_output
    def write_res_file(calc, resfilename):
        """
        Write calc output to CSV-formatted file with resfilename.
        """
        varlist = [
            'RECID', 'c00100', 'standard', 'c04800', 'iitax', 'payrolltax'
        ]
        # varnames  AGI    STD         TaxInc    ITAX     PTAX
        stats = calc.dataframe(varlist)
        stats['RECID'] = stats['RECID'].astype(int)
        with open(resfilename, 'w') as resfile:
            stats.to_csv(resfile, index=False, float_format='%.2f')

    # embedded function used only in test_reform_json_and_output
    def res_and_out_are_same(base):
        """
        Return True if base.res.csv and base.out.csv file contents are same;
        return False if base.res.csv and base.out.csv file contents differ.
        """
        resdf = pd.read_csv(base + '.res.csv')
        outdf = pd.read_csv(base + '.out.csv')
        diffs = False
        for col in resdf:
            if col in outdf:
                if not np.allclose(resdf[col], outdf[col]):
                    diffs = True
            else:
                diffs = True
        return not diffs

    # specify Records object containing cases data
    tax_year = 2020
    cases_path = os.path.join(tests_path, '..', 'reforms', 'cases.csv')
    cases = Records(data=cases_path,
                    start_year=tax_year,  # set raw input data year
                    gfactors=None,  # keeps raw data unchanged
                    weights=None,
                    adjust_ratios=None)
    # specify list of reform failures
    failures = list()
    # specify current-law-policy Calculator object
    calc = Calculator(policy=Policy(), records=cases, verbose=False)
    calc.advance_to_year(tax_year)
    calc.calc_all()
    res_path = cases_path.replace('cases.csv', 'clp.res.csv')
    write_res_file(calc, res_path)
    if res_and_out_are_same(res_path.replace('.res.csv', '')):
        os.remove(res_path)
    else:
        failures.append(res_path)
    del calc
    # read 2017_law.json reform file and specify its parameters dictionary
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Policy.read_json_reform(pre_tcja_jrf)
    # check reform file contents and reform results for each reform
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    json_reform_files = glob.glob(reforms_path)
    for jrf in json_reform_files:
        # determine reform's baseline by reading contents of jrf
        with open(jrf, 'r') as rfile:
            jrf_text = rfile.read()
        pre_tcja_baseline = 'Reform_Baseline: 2017_law.json' in jrf_text
        # implement the reform relative to its baseline
        reform = Policy.read_json_reform(jrf_text)
        pol = Policy()  # current-law policy
        if pre_tcja_baseline:
            pol.implement_reform(pre_tcja)
            assert not pol.parameter_errors
        pol.implement_reform(reform)
        assert not pol.parameter_errors
        calc = Calculator(policy=pol, records=cases, verbose=False)
        calc.advance_to_year(tax_year)
        calc.calc_all()
        res_path = jrf.replace('.json', '.res.csv')
        write_res_file(calc, res_path)
        if res_and_out_are_same(res_path.replace('.res.csv', '')):
            os.remove(res_path)
        else:
            failures.append(res_path)
        del calc
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
    reform = dict()
    for name, value in reform_dict['value'].items():
        reform[name] = {start_year: value}
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
    return Policy.read_json_reform(pre_tcja_jrf)


@pytest.fixture(scope='module', name='reforms_dict')
def fixture_reforms_dict(tests_path):
    """
    Read reforms.json and convert to dictionary.
    """
    reforms_path = os.path.join(tests_path, 'reforms.json')
    with open(reforms_path, 'r') as rfile:
        rjson = rfile.read()
    return json.loads(rjson)


NUM_REFORMS = 64  # when changing this also change num_reforms in conftest.py


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('rid', [i for i in range(1, NUM_REFORMS + 1)])
def test_reforms(rid, test_reforms_init, tests_path, baseline_2017_law,
                 reforms_dict, puf_subsample):
    """
    Write actual reform results to files.
    """
    # pylint: disable=too-many-arguments
    assert test_reforms_init == NUM_REFORMS
    actual = reform_results(rid, reforms_dict[str(rid)],
                            puf_subsample, baseline_2017_law)
    afile_path = os.path.join(tests_path,
                              'reform_actual_{}.csv'.format(rid))
    with open(afile_path, 'w') as afile:
        afile.write('rid,res1,res2,res3,res4\n')
        afile.write('{}\n'.format(actual))
