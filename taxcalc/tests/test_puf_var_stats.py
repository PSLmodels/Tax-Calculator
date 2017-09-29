"""
Test generates statistics for puf.csv variables.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_puf_var_stats.py
# pylint --disable=locally-disabled test_puf_var_stats.py

import os
import json
import copy
import numpy as np
import pandas as pd
import pytest
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error


def create_base_table(test_path):
    """
    Create and return base table.
    """
    # specify caculated variable names and descriptions in dictionary
    # (currently includes only 16 of the most used variables)
    calc_dict = {'iitax': 'Federal income tax liability',
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
                 'eitc': 'Federal EITC',
                 'c09600': 'Federal AMT liability'}
    # specify set of unused read variables in statistics calculations
    unused_var_set = set(['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED',
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
                          'blind_head', 'blind_spouse'])
    # calculate for all usable read variables minus unused variables
    read_vars = list(Records.USABLE_READ_VARS - unused_var_set)
    # read variable descriptions from JSON file
    rec_vars_path = os.path.join(test_path, '..', 'records_variables.json')
    with open(rec_vars_path) as vfile:
        vardict = json.load(vfile)
    # create table_dict with sorted read vars first then sorted calc vars
    table_dict = dict()
    for var in sorted(read_vars):
        description = vardict['read'][var]['desc']
        table_dict[var] = description
    sorted_calc_vars = sorted(calc_dict.keys())
    for var in sorted_calc_vars:
        table_dict[var] = calc_dict[var]
    # construct DataFrame table from table_dict
    table = pd.DataFrame.from_dict(table_dict, orient='index')
    table.columns = ['description']
    return table


def generate_corr_stats(calc, table, test_path):
    """
    Calculate correlation coefficient matrix for 2016.
    """
    for varname1 in table.index:
        var1 = getattr(calc.records, varname1)
        var1_cc = list()
        for varname2 in table.index:
            var2 = getattr(calc.records, varname2)
            cor = np.corrcoef(var1, var2)[0][1]
            var1_cc.append(cor)
        table[varname1] = var1_cc
    out_path = os.path.join(test_path, 'puf_var_correl_coeffs_2016.csv')
    table.to_csv(out_path, float_format='%8.3f')


def generate_all_stats(calc, table_mean, table_corr, test_path):
    """
    Calculate weighted mean each year and correlation coefficients for 2016
    """
    year_headers = ['description']
    for year in range(Policy.JSON_START_YEAR, Policy.LAST_BUDGET_YEAR + 1):
        assert year == calc.policy.current_year
        year_headers.append(str(year))
        calc.calc_all()
        if year == 2016:
            # calculate correlation coefficients for 2016
            generate_corr_stats(calc, table_corr, test_path)
        # calculate weighted means for this year
        total_weight = calc.records.s006.sum()
        stat = list()
        for variable in table_mean.index:
            weighted = getattr(calc.records, variable) * calc.records.s006
            this_record = weighted.sum() / total_weight
            stat.append(this_record)
        column = 'mean_' + str(year)
        table_mean[column] = stat
        if year < Policy.LAST_BUDGET_YEAR:
            calc.increment_year()
    out_path = os.path.join(test_path, 'puf_var_wght_means_by_year.csv')
    table_mean.to_csv(out_path, header=year_headers, float_format='%8.3f')

@pytest.mark.one
@pytest.mark.requires_pufcsv
def test_puf_var_stats(tests_path, puf_fullsample):
    """
    Main logic of test.
    """
    # create a Calculator object
    rec = Records(data=puf_fullsample)
    calc = Calculator(policy=Policy(), records=rec, verbose=False)
    table_mean = create_base_table(tests_path)
    table_corr = copy.deepcopy(table_mean)
    generate_all_stats(calc, table_mean, table_corr, tests_path)
