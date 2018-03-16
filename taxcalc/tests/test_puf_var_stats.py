"""
Test generates statistics for puf.csv variables.
"""
# CODING-STYLE CHECKS:
# pep8 test_puf_var_stats.py
# pylint --disable=locally-disabled test_puf_var_stats.py

import os
import sys
import json
import copy
import numpy as np
import pandas as pd
import pytest
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, nonsmall_diffs


def create_base_table(test_path):
    """
    Create and return base table.
    """
    # specify calculated variable names and descriptions
    calc_dict = {'eitc': 'Federal EITC',
                 'iitax': 'Federal income tax liability',
                 'payrolltax': 'Payroll taxes (ee+er) for OASDI+HI',
                 'c00100': 'Federal AGI',
                 'c02500': 'OASDI benefits in AGI',
                 'c04600': 'Post-phase-out personal exemption',
                 'c21040': 'Itemized deduction that is phased out',
                 'c04470': 'Post-phase-out itemized deduction',
                 'c04800': 'Federal regular taxable income',
                 'c05200': 'Regular tax on taxable income',
                 'c07220': 'Child tax credit (adjusted)',
                 'c11070': 'Extra child tax credit (refunded)',
                 'c07180': 'Child care credit',
                 'c09600': 'Federal AMT liability'}
    # specify read variable names and descriptions
    unused_var_set = set(['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED',
                          'h_seq', 'a_lineno', 'ffpos', 'fips', 'agi_bin',
                          'FLPDYR', 'FLPDMO', 'f2441', 'f3800', 'f6251',
                          'f8582', 'f8606', 'f8829', 'f8910', 'f8936', 'n20',
                          'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
                          'TFORM', 'IE', 'TXST', 'XFPT', 'XFST', 'XOCAH',
                          'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT', 'MARS', 'MIDR',
                          'RECID', 'gender', 'wage_head', 'wage_spouse',
                          'earnsplit', 'agedp1', 'agedp2', 'agedp3',
                          's006', 's008', 's009', 'WSAMP', 'TXRT',
                          'filer', 'matched_weight', 'e00200p', 'e00200s',
                          'e00900p', 'e00900s', 'e02100p', 'e02100s',
                          'age_head', 'age_spouse',
                          'nu18', 'n1820', 'n21',
                          'ssi_ben', 'snap_ben', 'other_ben',
                          'mcare_ben', 'mcaid_ben', 'vet_ben',
                          'housing_ben', 'tanf_ben', 'wic_ben',
                          'blind_head', 'blind_spouse'])
    read_vars = list(Records.USABLE_READ_VARS - unused_var_set)
    # get read variable information from JSON file
    rec_vars_path = os.path.join(test_path, '..', 'records_variables.json')
    with open(rec_vars_path) as rvfile:
        read_var_dict = json.load(rvfile)
    # create table_dict with sorted read vars followed by sorted calc vars
    table_dict = dict()
    for var in sorted(read_vars):
        table_dict[var] = read_var_dict['read'][var]['desc']
    sorted_calc_vars = sorted(calc_dict.keys())
    for var in sorted_calc_vars:
        table_dict[var] = calc_dict[var]
    # construct DataFrame table from table_dict
    table = pd.DataFrame.from_dict(table_dict, orient='index')
    table.columns = ['description']
    return table


def calculate_corr_stats(calc, table):
    """
    Calculate correlation coefficient matrix.
    """
    errmsg = ''
    for varname1 in table.index:
        var1 = calc.array(varname1)
        var1_cc = list()
        for varname2 in table.index:
            var2 = calc.array(varname2)
            try:
                cor = np.corrcoef(var1, var2)[0][1]
            except FloatingPointError:
                msg = 'corr-coef error for {} and {}\n'
                errmsg += msg.format(varname1, varname2)
                cor = 9.99  # because could not compute it
            var1_cc.append(cor)
        table[varname1] = var1_cc
    if errmsg:
        raise ValueError('\n' + errmsg)


def calculate_mean_stats(calc, table, year):
    """
    Calculate weighted means for year.
    """
    total_weight = calc.total_weight()
    means = list()
    for varname in table.index:
        wmean = calc.weighted_total(varname) / total_weight
        means.append(wmean)
    table[str(year)] = means


def differences(new_filename, old_filename, stat_kind, small):
    """
    Return message string if there are differences at least as large as small;
    otherwise (i.e., if there are only small differences) return empty string.
    """
    with open(new_filename, 'r') as vfile:
        new_text = vfile.read()
    with open(old_filename, 'r') as vfile:
        old_text = vfile.read()
    if nonsmall_diffs(new_text.splitlines(True),
                      old_text.splitlines(True), small):
        new_name = os.path.basename(new_filename)
        old_name = os.path.basename(old_filename)
        msg = '{} RESULTS DIFFER:\n'.format(stat_kind)
        msg += '-------------------------------------------------'
        msg += '-------------\n'
        msg += '--- NEW RESULTS IN {} FILE ---\n'.format(new_name)
        msg += '--- if new OK, copy {} to  ---\n'.format(new_name)
        msg += '---                 {}         ---\n'.format(old_name)
        msg += '---            and rerun test.                   '
        msg += '          ---\n'
        msg += '-------------------------------------------------'
        msg += '-------------\n'
    else:
        msg = ''
        os.remove(new_filename)
    return msg


MEAN_FILENAME = 'puf_var_wght_means_by_year.csv'
CORR_FILENAME = 'puf_var_correl_coeffs_2016.csv'


@pytest.mark.requires_pufcsv
def test_puf_var_stats(tests_path, puf_fullsample):
    """
    Main logic of test.
    """
    # create a baseline Policy object containing 2017_law.json parameters
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Calculator.read_json_param_objects(pre_tcja_jrf, None)
    baseline_policy = Policy()
    baseline_policy.implement_reform(pre_tcja['policy'])
    # create a Calculator object using baseline_policy and full puf.csv sample
    rec = Records(data=puf_fullsample)
    calc = Calculator(policy=baseline_policy, records=rec, verbose=False)
    # create base tables
    table_mean = create_base_table(tests_path)
    table_corr = copy.deepcopy(table_mean)
    del table_corr['description']
    # add statistics to tables
    year_headers = ['description']
    for year in range(Policy.JSON_START_YEAR, Policy.LAST_BUDGET_YEAR + 1):
        assert year == calc.policy_current_year()
        year_headers.append(str(year))
        calc.calc_all()
        calculate_mean_stats(calc, table_mean, year)
        if year == 2016:
            calculate_corr_stats(calc, table_corr)
        if year < Policy.LAST_BUDGET_YEAR:
            calc.increment_year()
    # write tables to new CSV files
    mean_path = os.path.join(tests_path, MEAN_FILENAME + '-new')
    table_mean.sort_index(inplace=True)
    table_mean.to_csv(mean_path, header=year_headers, float_format='%8.0f')
    corr_path = os.path.join(tests_path, CORR_FILENAME + '-new')
    table_corr.sort_index(inplace=True)
    table_corr.to_csv(corr_path, float_format='%8.2f',
                      columns=table_corr.index)
    # compare new and old CSV files for nonsmall differences
    if sys.version_info.major == 2:
        # tighter tests for Python 2.7
        mean_msg = differences(mean_path, mean_path[:-4],
                               'MEAN', small=0.0)
        corr_msg = differences(corr_path, corr_path[:-4],
                               'CORR', small=0.0)
    else:
        # looser tests for Python 3.6
        mean_msg = differences(mean_path, mean_path[:-4],
                               'MEAN', small=1.0)
        corr_msg = differences(corr_path, corr_path[:-4],
                               'CORR', small=0.01)
    if mean_msg or corr_msg:
        raise ValueError(mean_msg + corr_msg)
