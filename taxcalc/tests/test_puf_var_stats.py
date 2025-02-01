"""
Test generates statistics for puf.csv variables.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_puf_var_stats.py
# pylint --disable=locally-disabled test_puf_var_stats.py

import os
import json
import copy
import numpy as np
import pandas as pd
import pytest
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator


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
    unused_var_set = set(['DSI', 'EIC',
                          'h_seq', 'a_lineno', 'ffpos', 'fips', 'agi_bin',
                          'FLPDYR', 'FLPDMO', 'f2441', 'f3800', 'f6251',
                          'f8582', 'f8606', 'f8829', 'f8910', 'f8936', 'n20',
                          'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
                          'TFORM', 'IE', 'TXST', 'XFPT', 'XFST', 'XOCAH',
                          'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT', 'MARS', 'MIDR',
                          'RECID', 'gender', 'wage_head', 'wage_spouse',
                          'earnsplit', 'agedp1', 'agedp2', 'agedp3',
                          's006', 's008', 's009', 'WSAMP', 'TXRT',
                          'matched_weight', 'e00200p', 'e00200s',
                          'e00900p', 'e00900s', 'e02100p', 'e02100s',
                          'age_head', 'age_spouse',
                          'nu18', 'n1820', 'n21',
                          'ssi_ben', 'snap_ben', 'other_ben',
                          'mcare_ben', 'mcaid_ben', 'vet_ben',
                          'housing_ben', 'tanf_ben', 'wic_ben',
                          'blind_head', 'blind_spouse',
                          'PT_SSTB_income',
                          'PT_binc_w2_wages',
                          'PT_ubia_property'])
    records_varinfo = Records(data=None)
    read_vars = list(records_varinfo.USABLE_READ_VARS - unused_var_set)
    # get read variable information from JSON file
    rec_vars_path = os.path.join(test_path, '..', 'records_variables.json')
    with open(rec_vars_path, 'r', encoding='utf-8') as rvfile:
        read_var_dict = json.load(rvfile)
    # create table_dict with sorted read vars followed by sorted calc vars
    table_dict = {}
    for var in sorted(read_vars):
        if "taxdata_puf" in read_var_dict['read'][var]['availability']:
            table_dict[var] = read_var_dict['read'][var]['desc']
        else:
            pass
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
        var1_cc = []
        for varname2 in table.index:
            var2 = calc.array(varname2)
            try:
                cor = np.corrcoef(var1, var2)[0][1]
            except FloatingPointError:
                msg = f'corr-coef error for {varname1} and {varname2}\n'
                errmsg += msg
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
    means = []
    for varname in table.index:
        wmean = calc.weighted_total(varname) / total_weight
        means.append(wmean)
    table[str(year)] = means


def differences(new_filename, old_filename, stat_kind):
    """
    Return message string if differences detected by np.allclose();
    otherwise return empty string.
    """
    new_df = pd.read_csv(new_filename)
    old_df = pd.read_csv(old_filename)
    diffs = False
    if list(new_df.columns.values) == list(old_df.columns.values):
        for col in new_df.columns[1:]:
            if col == 'description':
                continue  # skip description column
            if not np.allclose(new_df[col], old_df[col]):
                diffs = True
    else:
        diffs = True
    if diffs:
        new_name = os.path.basename(new_filename)
        old_name = os.path.basename(old_filename)
        msg = f'{stat_kind} RESULTS DIFFER:\n'
        msg += '-------------------------------------------------'
        msg += '-------------\n'
        msg += f'--- NEW RESULTS IN {new_name} FILE ---\n'
        msg += f'--- if new OK, copy {new_name} to\n'
        msg += f'---                 {old_name}   \n'
        msg += '---            and rerun test.      '
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
    pre_tcja = Policy.read_json_reform(pre_tcja_jrf)
    baseline_policy = Policy()
    baseline_policy.implement_reform(pre_tcja)
    # create a Calculator object using baseline_policy and full puf.csv sample
    rec = Records(data=puf_fullsample)
    calc = Calculator(policy=baseline_policy, records=rec, verbose=False)
    # create base tables
    table_mean = create_base_table(tests_path)
    table_corr = copy.deepcopy(table_mean)
    del table_corr['description']
    # add statistics to tables
    year_headers = ['description']
    for year in range(Policy.JSON_START_YEAR, 2034 + 1):
        assert year == calc.current_year
        year_headers.append(str(year))
        calc.calc_all()
        calculate_mean_stats(calc, table_mean, year)
        if year == 2016:
            calculate_corr_stats(calc, table_corr)
        if year < 2034:
            calc.increment_year()
    # write tables to new CSV files
    mean_path = os.path.join(tests_path, MEAN_FILENAME + '-new')
    table_mean.sort_index(inplace=True)
    table_mean.to_csv(mean_path, header=year_headers, float_format='%8.0f')
    corr_path = os.path.join(tests_path, CORR_FILENAME + '-new')
    table_corr.sort_index(inplace=True)
    table_corr.to_csv(corr_path, float_format='%8.2f',
                      columns=table_corr.index)
    # compare new and old CSV files for differences
    mean_msg = differences(mean_path, mean_path[:-4], 'MEAN')
    corr_msg = differences(corr_path, corr_path[:-4], 'CORR')
    if mean_msg or corr_msg:
        raise ValueError(mean_msg + corr_msg)
