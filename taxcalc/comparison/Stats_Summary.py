"""
This script calculates weighted means for PUF variables used in the Calculator
and 16 calculated variables.

Currently all stats saved in 'variable_stats_summary.csv'

USAGE: python Stats_Summary.py

"""

import pandas as pd
from pandas import DataFrame
import numpy as np
import copy
import os
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "..", ".."))
from taxcalc import Policy, Records, Calculator, Growth, behavior
PUF_PATH = os.path.join(CUR_PATH, "..", "..", "puf.csv")
EVAR_PATH = os.path.join(CUR_PATH, "..", "e_variable_info.csv")

# create a calculator
tax_dta1 = pd.read_csv(PUF_PATH)
records1 = Records(tax_dta1)
policy1 = Policy(start_year = 2013)
growth1 = Growth()
calc1 = Calculator(records=records1, policy=policy1)

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


# Use all variable list minus unused variable list to get used variable list
VALID_READ_VARS = records1.VALID_READ_VARS

PUF_CODES_INPUATATIONS = set(['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED', 'FLPDYR', 'FLPDMO',
        'f2441', 'f3800', 'f6251', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT', 'MARS', 'MIDR', 'RECID', 'gender',
        'wage_head', 'wage_spouse', 'earnsplit',
        'age', 'agedp1', 'agedp2', 'agedp3', 'AGERANGE',
        's006', 's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight','e00200p', 'e00200s',
        'e00900p', 'e00900s', 'e02100p', 'e02100s'])


UNUSED_READ_VARS = records1.UNUSED_READ_VARS

USED_VARS = list(VALID_READ_VARS - PUF_CODES_INPUATATIONS - UNUSED_READ_VARS)


# read variable description from e_variable_info.csv
sum_stats = {}
for i in range(0, len(USED_VARS)-1):
    # use variable names as keys of dictionary
    var_name = USED_VARS[i]
    description = puf_ecodes_info.Definition_2014[puf_ecodes_info.Input_Name==var_name].values[0]
    sum_stats[var_name] = description

sum_stats = pd.DataFrame.from_dict(sum_stats, orient='index')
sum_stats.columns = ["description"]

sum_stats = sum_stats.append(cal)

# calculates weighted mean for each variable
# in total 10 years
total_pop = calc1.records.s006.sum()
for year in range(2013, 2027):
    calc1.calc_all()
    stat = []
    for variable in sum_stats.index:
        this_record = (getattr(calc1.records, variable) * calc1.records.s006).sum()/total_pop
        stat.append(this_record)
        
    column = "mean_"+str(year)
    sum_stats[column] = stat
    
    year+=1
    if year != 2027:
        calc1.increment_year()

sum_stats.to_csv("variable_stats_summary.csv", header=['description','2013','2014','2015','2016','2017','2018',
                                                        '2019', '2020','2021', '2022', '2023', '2024','2025', '2026'], float_format='%8.2f')

