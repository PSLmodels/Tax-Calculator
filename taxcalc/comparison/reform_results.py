
"""
This script generates policy experiment results,
and compare them with JCT Tax Expenditure or Budget Options if available.

It uses reforms stored in 'reforms.json',
and export and save all results and comparisons in a txt file

puf.csv needs to be in the top level of Tax-calculator.
Otherwise replace the file name with full path

USAGE: python reform_results.py
"""

import json
import copy
import pandas as pd
import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "..", ".."))
from taxcalc import Policy, Records, Calculator, behavior
from taxcalc import Policy, Records, Calculator, behavior
PUF_PATH = os.path.join(CUR_PATH, "..", "..", "puf.csv")

# import all reforms from this JSON file
with open("reforms.json") as json_file:
    reforms_json = json.load(json_file)
num_reforms = len(reforms_json)

# create two calculators, one for baseline and the other for reforms
tax_dta1 = pd.read_csv(PUF_PATH)
records1 = Records(tax_dta1)
policy1 = Policy(start_year=2013)
calc1 = Calculator(records=records1, policy=policy1)

tax_dta2 = pd.read_csv(PUF_PATH)
records2 = Records(tax_dta2)
policy2 = Policy(start_year=2013)
calc2 = Calculator(records=records2, policy=policy2)


# increment both calculators to 2015, when most reforms start
calc1.increment_year()
calc1.increment_year()
calc2.increment_year()
calc2.increment_year()

# create a dictionary to save all results
results = {}

# runs one reform a time, each reform for 4 years
# modify the number of reform & number of years as needed
for i in range(1, num_reforms + 1):
    # make two deep copies so the originals could be used again in next loop
    c1 = copy.deepcopy(calc1)
    c2 = copy.deepcopy(calc2)

    # fetch this reform from json and implement in policy object
    this_reform = 'r' + str(i)
    start_year = reforms_json.get(this_reform).get("start_year")

    # implement behavior assumptions if any,
    # and remove the node so it wont break policy object
    has_behavior = False
    if "_BE_CG_per" in reforms_json.get(this_reform).get("value"):
        persistent = reforms_json[this_reform]["value"]["_BE_CG_per"]
        assumption = {start_year: {"_BE_CG_per": persistent}}
        c2.behavior.update_behavior(assumption)
        has_behavior = True
        del reforms_json[this_reform]["value"]["_BE_CG_per"]

    # implement reforms on policy
    reform = {start_year: reforms_json.get(this_reform).get("value")}
    c2.policy.implement_reform(reform)

    # run the current reform for 4 years
    this_reform_results = []
    for j in range(1, start_year - 2010):
        output_type = reforms_json.get(this_reform).get("output_type")

        c1.calc_all()
        baseline = getattr(c1.records, output_type)
        if has_behavior:
            c2_behavior = behavior(c1, c2)
            diff = getattr(c2_behavior.records, output_type) - baseline
        else:
            c2.calc_all()
            diff = getattr(c2.records, output_type) - baseline

        weighted_sum_diff = (diff * c1.records.s006).sum() / 1000000000

        this_reform_results.append(weighted_sum_diff)

        c1.increment_year()
        c2.increment_year()

    # put this reform results in the dictionary for final results
    results[reforms_json.get(this_reform).get("name")] = this_reform_results


# export all results to a CSV file
# write all results to a text file
ofile = open('reform_results.txt', 'w')
for i in range(1, num_reforms + 1):
    reform = reforms_json['r' + str(i)]
    ofile.write('""\n')

    if "section_name" in reform:
        ofile.write('{}\n'.format(reform["section_name"]))
        ofile.write('""\n')

    reform_name = reform["name"]
    ofile.write('{}\n'.format(reform_name))

    value = results[reform_name]
    ofile.write('Tax-Calculator')
    ofile.write(',{:.1f},{:.1f},{:.1f},{:.1f}\n'.format(value[0], value[1],
                                                        value[2], value[3]))

    if "Tax Expenditure" in reform["compare_with"]:
        comp = reform["compare_with"]["Tax Expenditure"]
        ofile.write('Tax Expenditure')
        ofile.write(',{:.0f},{:.0f},{:.0f},{:.0f}\n'.format(comp[0], comp[1],
                                                            comp[2], comp[3]))

    if "Budget Options" in reform["compare_with"]:
        comp = reform["compare_with"]["Budget Options"]
        ofile.write('Budget Options')
        ofile.write(',{:.0f},{:.0f},{:.0f},{:.0f}\n'.format(comp[0], comp[1],
                                                            comp[2], comp[3]))
ofile.close()
