"""
This script calculates weighted means for PUF variables used in the Calculator
and 16 calculated variables.
USAGE:
Generate statistics summary: python stats_summary.py
Generate correlation matrix: python stats_summary.py --output correlation
"""

import pandas as pd
from pandas import DataFrame
import numpy as np
import os
import sys
import argparse
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "..", ".."))
from taxcalc import Policy, Records, Calculator
PUF_PATH = os.path.join(CUR_PATH, "..", "..", "puf.csv")
EVAR_PATH = os.path.join(CUR_PATH, "..", "e_variable_info.csv")


def main():
    parser = argparse.ArgumentParser(
        prog="python stats_summary.py",
        description=('Generates a files for either statistics summary'
                     'on a 10-year span or correlation matrix of current'
                     'tax year. Adding either sum-stats or correlation'
                     'as an argument after python Stats_Summary.py --output')
    )
    parser.add_argument('--output',
                        default='sum-stats')
    args = parser.parse_args()
    # create a calculator
    tax_dta1 = pd.read_csv(PUF_PATH)
    records1 = Records(tax_dta1)
    policy1 = Policy(start_year=2013)
    calc1 = Calculator(records=records1, policy=policy1)
    table = creat_table_base()
    if args.output == 'sum-stats':
        gen_sum_stats(table, calc=calc1)
    elif args.output == 'correlation':
        gen_correlation(table, calc=calc1)
    else:
        print("no such output available")
    return 0


def creat_table_base():
    # saved caculated variable names and descriptions in json format
    # currently only includes 16 most used variables
    calculated_vars = {"_iitax": "Federal income tax liability",
                       "_fica": "FICA taxes  (ee+er) for OASDI+HI",
                       "c00100": "Federal AGI",
                       "c02500": "OASDI benefits in AGI",
                       "c04600": "Post-phase-out personal exemption",
                       "_prexmp": "Pre-phase-out personal exemption",
                       "c21040": "Itemized deduction that is phased out",
                       "c04470": "Post-phase-out itemized deduction",
                       "c04800": "Federal regular taxable income",
                       "c05200": "Regular tax on taxable income",
                       "c07220": "Child tax credit (adjusted)",
                       "c11070": "Extra child tax credit (refunded)",
                       "c07180": "Child care credit",
                       "_eitc": "Federal EITC",
                       "c62100_everyone": "federal AMT taxable income",
                       "c09600": "federal AMT liability"}
    cal = DataFrame.from_dict(calculated_vars, orient='index')
    cal.columns = ['description']
    puf_ecodes_info = pd.read_csv(EVAR_PATH)
    # Use all variable list minus unused variable list
    # to get used variable list
    codes_imp_set = set(['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED',
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
    used_vars_set = list(Records.VALID_READ_VARS - codes_imp_set)
    # read variable description from e_variable_info.csv
    table = {}
    for i in range(0, len(used_vars_set) - 1):
        # use variable names as keys of dictionary
        var_name = used_vars_set[i]
        fval = (puf_ecodes_info.Input_Name == var_name)
        description = puf_ecodes_info.Definition_2014[fval].values[0]
        table[var_name] = description
    table = pd.DataFrame.from_dict(table, orient='index')
    table.columns = ["description"]
    table = table.append(cal)
    return table


def gen_sum_stats(table, calc):
    # calculates weighted mean for each variable
    # in total 10 years
    total_pop = calc.records.s006.sum()
    for year in range(2013, 2027):
        calc.calc_all()
        stat = []
        for variable in table.index:
            weighted = getattr(calc.records, variable) * calc.records.s006
            this_record = weighted.sum() / total_pop
            stat.append(this_record)

        column = "mean_" + str(year)
        table[column] = stat

        year += 1
        if year != 2027:
            calc.increment_year()
    table.to_csv("variable_stats_summary.csv",
                 header=['description', '2013', '2014', '2015',
                         '2016', '2017', '2018', '2019', '2020',
                         '2021', '2022', '2023', '2024', '2025', '2026'],
                 float_format='%8.2f')


def gen_correlation(table, calc):
    # for now we only do correlation matrix for 2016
    calc.advance_to_year(2016)
    calc.calc_all()
    for var1 in table.index:
        variable1 = getattr(calc.records, var1)
        var1_cor = []
        for var2 in table.index:
            variable2 = getattr(calc.records, var2)
            cor = np.corrcoef(variable1, variable2)[0][1]
            var1_cor.append(cor)
        table[var1] = var1_cor
    table.to_csv("correlation.csv")


if __name__ == '__main__':
    sys.exit(main())
