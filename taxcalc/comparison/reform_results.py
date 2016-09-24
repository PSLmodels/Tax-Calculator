"""
This script generates policy experiment results and
compares them with JCT Tax Expenditure or Budget Options, if available.

It reads reforms stored in the 'reforms.json' file, and
writes all results and comparisons to the 'reform_results.txt' file.

puf.csv needs to be in the top-level directory of Tax-Calculator source tree.

USAGE: python reform_results.py
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 reform_results.py
# pylint --disable=locally-disabled reform_results.py

import json
import pandas as pd
import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "..", ".."))
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, Behavior
PUF_PATH = os.path.join(CUR_PATH, "..", "..", "puf.csv")
PUF_DATA = pd.read_csv(PUF_PATH)

# read all reforms from JSON file
with open("reforms.json") as json_file:
    REFORMS_JSON = json.load(json_file)
NUM_REFORMS = len(REFORMS_JSON)

# create a dictionary of all reform results
RESULTS = {}

# analyze one reform a time, simulating each reform for four years
NUM_YEARS = 4
for i in range(1, NUM_REFORMS + 1):
    # create current-law-policy calculator
    pol1 = Policy()
    rec1 = Records(data=PUF_DATA)
    calc1 = Calculator(policy=pol1, records=rec1, verbose=False, behavior=None)

    # create reform calculator with possible behavioral responses
    this_reform = "r" + str(i)
    start_year = REFORMS_JSON.get(this_reform).get("start_year")
    beh2 = Behavior()
    if "_BE_cg" in REFORMS_JSON.get(this_reform).get("value"):
        elasticity = REFORMS_JSON[this_reform]["value"]["_BE_cg"]
        del REFORMS_JSON[this_reform]["value"]["_BE_cg"]  # to not break reform
        beh_assump = {start_year: {"_BE_cg": elasticity}}
        beh2.update_behavior(beh_assump)
    reform = {start_year: REFORMS_JSON.get(this_reform).get("value")}
    pol2 = Policy()
    pol2.implement_reform(reform)
    rec2 = Records(data=PUF_DATA)
    calc2 = Calculator(policy=pol2, records=rec2, verbose=False, behavior=beh2)
    output_type = REFORMS_JSON.get(this_reform).get("output_type")
    reform_name = REFORMS_JSON.get(this_reform).get("name")

    # increment both calculators to reform's start_year
    calc1.advance_to_year(start_year)
    calc2.advance_to_year(start_year)

    # calculate prereform and postreform for num_years
    reform_results = []
    for _ in range(0, NUM_YEARS):
        calc1.calc_all()
        prereform = getattr(calc1.records, output_type)
        if calc2.behavior.has_response():
            calc_clp = calc2.current_law_version()
            calc2_br = Behavior.response(calc_clp, calc2)
            postreform = getattr(calc2_br.records, output_type)
        else:
            calc2.calc_all()
            postreform = getattr(calc2.records, output_type)
        diff = postreform - prereform
        weighted_sum_diff = (diff * calc1.records.s006).sum() * 1.0e-9
        reform_results.append(weighted_sum_diff)
        calc1.increment_year()
        calc2.increment_year()

    # put reform_results in the dictionary of all results
    RESULTS[reform_name] = reform_results

# write RESULTS to text file
OFILE = open('reform_results.txt', 'w')
for i in range(1, NUM_REFORMS + 1):
    reform = REFORMS_JSON['r' + str(i)]
    OFILE.write('""\n')
    if "section_name" in reform:
        OFILE.write('{}\n'.format(reform["section_name"]))
        OFILE.write('""\n')
    reform_name = reform["name"]
    OFILE.write('{}\n'.format(reform_name))
    value = RESULTS[reform_name]
    OFILE.write('Tax-Calculator')
    for iyr in range(0, NUM_YEARS):
        OFILE.write(',{:.1f}'.format(value[iyr]))
    OFILE.write('\n')
    if "Tax Expenditure" in reform["compare_with"]:
        comp = reform["compare_with"]["Tax Expenditure"]
        OFILE.write('Tax Expenditure')
        for iyr in range(0, NUM_YEARS):
            OFILE.write(',{:.0f}'.format(comp[iyr]))
        OFILE.write('\n')
    if "Budget Options" in reform["compare_with"]:
        comp = reform["compare_with"]["Budget Options"]
        OFILE.write('Budget Options')
        for iyr in range(0, NUM_YEARS):
            OFILE.write(',{:.0f}'.format(comp[iyr]))
        OFILE.write('\n')
    if "Tax Foundation" in reform["compare_with"]:
        comp = reform["compare_with"]["Tax Foundation"]
        OFILE.write('Tax Foundation:')
        for idx in range(0, len(comp)):
            OFILE.write(' {}'.format(comp[idx]))
        OFILE.write('\n')
OFILE.close()
