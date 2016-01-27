
"""
This script generates policy experiment results,
and compare them with JCT Tax Expenditure or Budget Options if available.

It uses reforms stored in 'reforms.json',
and export and save all results and comparisons in a CSV file

puf.csv needs to be in the current directory.
Otherwise replace the file name with full path

USAGE: python Genrate_comparison_results.py
"""

import json
import copy
import csv
import pandas as pd
from taxcalc import Policy, Records, Calculator, behavior


# import all reforms from this JSON file
with open("reforms.json") as json_file:
    reforms_json = json.load(json_file)
num_reforms = len(reforms_json)

# create two calculators, one for baseline and the other for reforms
tax_dta1 = pd.read_csv("puf.csv")
records1 = Records(tax_dta1)
policy1 = Policy(start_year=2013)
calc1 = Calculator(records=records1, policy=policy1)

tax_dta2 = pd.read_csv("puf.csv")
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
    for j in range(1, start_year-2010):
        output_type = reforms_json.get(this_reform).get("output_type")

        c1.calc_all()
        baseline = getattr(c1.records, output_type)
        if has_behavior:
            c2_behavior = behavior(c1, c2)
            diff = getattr(c2_behavior.records, output_type) - baseline
        else:
            c2.calc_all()
            diff = getattr(c2.records, output_type) - baseline

        weighted_sum_diff = (diff * c1.records.s006).sum()/1000000000

        this_reform_results.append(weighted_sum_diff)

        c1.increment_year()
        c2.increment_year()

    # put this reform results in the dictionary for final results
    results[reforms_json.get(this_reform).get("name")] = this_reform_results


# export all results to a CSV file
writer = csv.writer(open('comparison_results.csv', 'wb'))

for i in range(1, num_reforms + 1):
    this_reform = 'r' + str(i)
    writer.writerow([""])

    if "section_name" in reforms_json[this_reform]:
        writer.writerow([reforms_json[this_reform]["section_name"]])
        writer.writerow([""])

    reform_name = reforms_json[this_reform]["name"]
    writer.writerow([reform_name])

    value = results[reform_name]
    writer.writerow(["OSPC", round(value[0], 1), round(value[1], 1),
                     round(value[2], 1), round(value[3], 1)])

    if "Tax Expenditure" in reforms_json[this_reform]["compare_with"]:
        comp = reforms_json[this_reform]["compare_with"]["Tax Expenditure"]
        writer.writerow(["Tax Expenditure",
                         comp[0], comp[1], comp[2], comp[3]])

    if "Budget Options" in reforms_json[this_reform]["compare_with"]:
        comp = reforms_json[this_reform]["compare_with"]["Budget Options"]
        writer.writerow(["Budget Options", comp[0], comp[1], comp[2], comp[3]])
