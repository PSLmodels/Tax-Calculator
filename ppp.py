"""
Policy parameter projection script, which calculates policy parameter
values that were changed by TCJA and will revert to their pre-TCJA
values in 2026 (adjusted for inflation). The script should be run
when the inflation factor values change in growfactors.csv.

USAGE:  $ python ppp.py

Note: running this script will write the new 2026 parameter values
directly to policy_current_law.json.  So, if you want to compare
the new 2026 parameter values with the old 2026 parameter values,
be sure to copy policy_current_law.json before running this script.
"""
import json
import collections
from taxcalc import Policy

params = Policy()

# parameters that will revert
long_params = ['II_brk7', 'II_brk6', 'II_brk5', 'II_brk4',
               'II_brk3', 'II_brk2', 'II_brk1',
               'PT_brk7', 'PT_brk6', 'PT_brk5', 'PT_brk4',
               'PT_brk3', 'PT_brk2', 'PT_brk1',
               'PT_qbid_taxinc_thd',
               'ALD_BusinessLosses_c',
               'STD', 'II_em', 'II_em_ps',
               'AMT_em', 'AMT_em_ps', 'AMT_em_pe',
               'ID_ps', 'ID_AllTaxes_c']

# calculate the inflation factor used to calculate the
# inflation-adjusted 2026 parameter values
FINAL_IFACTOR = 1.0
PYEAR = 2017  # prior year before TCJA first implemented
FYEAR = 2026  # final year in which parameter values revert to
# pre-TCJA values
# construct final-year inflation factor from prior year
# NOTE: pvalue[t+1] = pvalue[t] * ( 1 + irate[t] )
for year in range(PYEAR, FYEAR):
    yindex = year - params.start_year
    rate = params._inflation_rates[yindex]  # pylint: disable=protected-access
    FINAL_IFACTOR *= 1 + rate

long_param_vals = collections.defaultdict(list)

for param in long_params:
    vos = params.select_eq(param, year=PYEAR)
    # use FINAL_IFACTOR to inflate from 2017 to 2026
    for vo in vos:
        long_param_vals[param].append(
            # create new dict to avoid modifying the original
            dict(
                vo,
                value=min(9e99, round(
                    vo["value"] * FINAL_IFACTOR, 0)),
                year=FYEAR,
            )
        )

# call adjust method for new 2026 values
params.adjust(long_param_vals)
params.clear_state()
param_data = params.specification(
    meta_data=False, serializable=True, use_state=False, _auto=False)

# read existing policy_current_law.json
with open('taxcalc/policy_current_law.json', 'r', encoding='utf-8') as pcl_old:
    pcl = json.load(pcl_old)

# replace 2026 values in the pcl dictionary
for param in param_data:
    pcl[param]["value"] = param_data[param]

# write new pcl dictionary to policy_current_law.json
with open('taxcalc/policy_current_law.json', 'w', encoding='utf-8') as pcl_new:
    json.dump(pcl, pcl_new, indent=4)
