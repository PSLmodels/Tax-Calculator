"""
RECIPE00.PY
"""

from __future__ import print_function  # necessary only if using Python 2.7

from taxcalc import *


# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

# read JSON reform file and use default (that is, static) analysis assumptions
reform_filename = './ingredients/repeal_amt.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
if pol.reform_errors != '':  # check for reform error messages
    print(pol.reform_errors)
    exit(1)
calc2 = Calculator(policy=pol, records=recs)

# calculate tax liabilities for 2018
calc1.advance_to_year(2018)
calc1.calc_all()
calc2.advance_to_year(2018)
calc2.calc_all()

# compute total income tax liability under current law and the reform
# (records.iitax contains each filing unit's individual income tax liability
# and records.s006 contains each filing units's sampling weight)
itax_rev1 = (calc1.records.iitax * calc1.records.s006).sum()
itax_rev2 = (calc2.records.iitax * calc2.records.s006).sum()

# print total revenue estimates for 2018 in whole billons of dollars
print('2018_CLP_itax_rev($B)= {:.0f}'.format(itax_rev1 * 1e-9))
print('2018_REF_itax_rev($B)= {:.0f}'.format(itax_rev2 * 1e-9))
