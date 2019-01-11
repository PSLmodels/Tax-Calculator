"""
Policy parameter projection script, which calculates future policy parameter
values under TCJA and which should be used when the following happens:
(1) the inflation factor values change in growfactors.csv, or
(2) the last known historical values of policy parameters are updated,
    in which case the byear parameter (see below) should be incremented.
USAGE:  $ python ppp.py
OUTPUT: ppp.old -- contains old parameter values in policy_current_law.json
        ppp.new -- contains new parameter values that should now be used
"""
from taxcalc import Policy

# specify year constants (only byear should vary)
syear = Policy.JSON_START_YEAR
pyear = 2017  # prior year before TCJA first implemented
byear = 2018  # base year: year for last known historical parameter values
fyear = 2026  # final year in which parameter values revert to pre-TCJA values

# ensure proper relationship between year constants
assert pyear == 2017
assert fyear == 2026
assert byear > pyear and byear < fyear

# specify current-law policy that includes TCJA inflation indexing rules
clp = Policy()
pdata = clp._vals

# identify policy parameters that have their values reverted in final year
skip_list = ['_II_brk7', '_PT_brk7']  # because they are both "infinity" (9e99)
fyr = '{}'.format(fyear)
reverting_params = list()
for pname in sorted(pdata.keys()):
    pdict = pdata[pname]
    if pdata[pname]['cpi_inflated'] and fyr in pdata[pname]['row_label']:
        if pname not in skip_list:
            reverting_params.append(pname)
print('number_of_reverting_parameters= {}'.format(len(reverting_params)))

# write ppp.old containing existing values for reverting policy parameters
old = open('ppp.old', 'w')
for pname in reverting_params:
    old.write('*** {} ***\n'.format(pname))
    # write parameter values for each year in [pyear,fyear] range
    for year in range(pyear, fyear + 1):
        value = pdata[pname]['value'][year - syear]
        old.write('{}: {}\n'.format(year, value))
old.close()

# get TCJA parameter inflation rates for each year
irate = clp.inflation_rates()

# construct final-year inflation factor from prior year
# < NOTE: pvalue[t+1] = pvalue[t] * ( 1 + irate[t] ) >
final_ifactor = 1.0
for year in range(pyear, fyear):
    final_ifactor *= 1 + irate[year - syear]

# construct intermediate-year inflation factors from base year
# < NOTE: pvalue[t+1] = pvalue[t] * ( 1 + irate[t] ) >
ifactor = dict()
factor = 1.0
for year in range(byear, fyear):
    ifactor[year] = factor
    factor *= 1 + irate[year - syear]

# write or calculate policy parameter values for pyear through fyear
new = open('ppp.new', 'w')
for pname in reverting_params:
    new.write('*** {} ***\n'.format(pname))
    # write parameter values for prior year
    value = pdata[pname]['value'][pyear - syear]
    new.write('{}: {}\n'.format(pyear, value))
    # write parameter values for year after prior year up through base year
    for year in range(pyear + 1, byear + 1):
        value = pdata[pname]['value'][year - syear]
        new.write('{}: {}\n'.format(year, value))
    # compute parameter values for intermediate years
    bvalue = pdata[pname]['value'][byear - syear]
    for year in range(byear + 1, fyear):
        if isinstance(bvalue, list):
            value = list()
            for idx in range(0, len(bvalue)):
                val = min(9e99, round(bvalue[idx] * ifactor[year], 2))
                value.append(val)
        else:
            value = min(9e99, round(bvalue * ifactor[year], 2))
        new.write('{}: {}\n'.format(year, value))
    # compute final year parameter value
    pvalue = pdata[pname]['value'][pyear - syear]
    if isinstance(pvalue, list):
        value = list()
        for idx in range(0, len(pvalue)):
            val = min(9e99, round(pvalue[idx] * final_ifactor, 0))
            value.append(val)
    else:
        value = min(9e99, round(pvalue * final_ifactor, 0))
    new.write('{}: {}\n'.format(fyear, value))
new.close()
