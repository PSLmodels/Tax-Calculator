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
VALID_READ_VARS = set([
        'e00200', 'e00300', 'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
        'e00900', 'e01000', 'e01100', 'e01200', 'e01400', 'e01500', 'e01700',
        'e02000', 'e02100', 'e02300', 'e02400', 'e02500', 'e03150', 'e03210',
        'e03220', 'e03230', 'e03260', 'e03270', 'e03240', 'e03290', 'e03300',
        'e03400', 'e03500', 'e00100', 'p04470', 'e04250', 'e04600', 'e04800',
        'e05100', 'e05200', 'e05800', 'e06000', 'e06200', 'e06300', 'e09600',
        'e07180', 'e07200', 'e07220', 'e07230', 'e07240', 'e07260', 'e07300',
        'e07400', 'e07600', 'p08000', 'e07150', 'e06500', 'e08800', 'e09400',
        'e09700', 'e09800', 'e09900', 'e10300', 'e10700', 'e10900', 'e10950',
        'e10960', 'e15100', 'e15210', 'e15250', 'e15360', 'e18600', 'e59560',
        'e59680', 'e59700', 'e59720', 'e11550', 'e11070', 'e11100', 'e11200',
        'e11300', 'e11400', 'e11570', 'e11580', 'e11581', 'e11582', 'e11583',
        'e10605', 'e11900', 'e12000', 'e12200', 'e17500', 'e18400', 'e18500',
        'e19200', 'e19550', 'e19800', 'e20100', 'e19700', 'e20550', 'e20600',
        'e20400', 'e20800', 'e20500', 'e21040', 'p22250', 'e22320', 'e22370',
        'p23250', 'e24515', 'e24516', 'e24518', 'e24535', 'e24560', 'e24598',
        'e24615', 'e24570', 'p25350', 'p25380', 'p25470', 'p25700', 'e25820',
        'e25850', 'e25860', 'e25940', 'e25980', 'e25920', 'e25960', 'e26110',
        'e26170', 'e26190', 'e26160', 'e26180', 'e26270', 'e26100', 'e26390',
        'e26400', 'e27200', 'e30400', 'e30500', 'e32800', 'e33000', 'e53240',
        'e53280', 'e53410', 'e53300', 'e53317', 'e53458', 'e58950', 'e58990',
        'p60100', 'p61850', 'e60000', 'e62100', 'e62900', 'e62720', 'e62730',
        'e62740', 'p65300', 'p65400', 'p87482', 'p87521', 'e68000', 'e82200',
        't27800', 's27860', 'p27895', 'e87530', 'e87550', 'e87870', 'e87875',
        'e87880',])

PUF_CODES_INPUATATIONS = ['AGIR1', 'DSI', 'EFI', 'EIC', 'ELECT', 'FDED', 'FLPDYR', 'FLPDMO',
        'f2441', 'f3800', 'f6251', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n24', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR', 'XTOT', 'MARS', 'MIDR', 'RECID', 'gender',
        'wage_head', 'wage_spouse', 'earnsplit',
        'age', 'agedp1', 'agedp2', 'agedp3', 'AGERANGE',
        's006', 's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight','e00200p', 'e00200s',
        'e00900p', 'e00900s', 'e02100p', 'e02100s']


UNUSED_READ_VARS = set([
        'AGIR1', 'EFI', 'ELECT', 'FLPDMO',
        'f3800', 'f8582', 'f8606', 'f8829', 'f8910', 'f8936',
        'n20', 'n25', 'n30', 'PREP', 'SCHB', 'SCHCF', 'SCHE',
        'TFORM', 'IE', 'TXST', 'XFPT', 'XFST',
        'XOCAH', 'XOCAWH', 'XOODEP', 'XOPAR',
        'gender',
        'earnsplit',
        'agedp1', 'agedp2', 'agedp3',
        's008', 's009', 'WSAMP', 'TXRT', 'filer', 'matched_weight',
        'e87870', 'e30400', 'e24598', 'e11300', 'e24535', 'e30500',
        'e07180', 'e53458', 'e33000', 'e25940', 'e12000', 'p65400',
        'e15210', 'e24615', 'e07230', 'e11100', 'e10900', 'e11581',
        'e11582', 'e11583', 'e25920', 's27860', 'e10960', 'e59720',
        'e87550', 'e26190', 'e53317', 'e53410', 'e04600', 'e26390',
        'e15250', 'p65300', 'p25350', 'e06500', 'e10300', 'e26170',
        'e26400', 'e11400', 'p25700', 'e01500', 'e04250', 'e07150',
        'e59680', 'e24570', 'e11570', 'e53300', 'e10605', 'e22320',
        'e26160', 'e22370', 'e53240', 'p25380', 'e10700', 'e09600',
        'e06200', 'e24560', 'p61850', 'e25980', 'e53280', 'e25850',
        'e25820', 'e10950', 'e68000', 'e26110', 'e58950', 'e26180',
        'e04800', 'e06000', 'e87880', 't27800', 'e06300', 'e59700',
        'e26100', 'e05200', 'e87875', 'e82200', 'e25860', 'e07220',
        'e11900', 'e18600', 'e25960', 'e15100', 'p27895', 'e12200'])

USED_VARS = list(VALID_READ_VARS - UNUSED_READ_VARS)


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

# create a calculator
tax_dta1 = pd.read_csv(PUF_PATH)
records1 = Records(tax_dta1)
policy1 = Policy(start_year = 2013)
growth1 = Growth()
calc1 = Calculator(records=records1, policy=policy1)


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

