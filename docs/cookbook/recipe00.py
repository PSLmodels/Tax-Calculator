from __future__ import print_function  # necessary only if using Python 2.7

from taxcalc import *


# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

# NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
#       so we can continue to use pol and recs in this script without any
#       concern about side effects from Calculator method calls.

# calculate aggregate current-law income tax liabilities for 2018
calc1.advance_to_year(2018)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# read JSON reform file and use (the default) static analysis assumptions
reform_filename = './ingredients/repeal_amt.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
if pol.reform_errors:  # check for reform error messages
    print(pol.reform_errors)
    exit(1)
calc2 = Calculator(policy=pol, records=recs)

# calculate reform income tax liabilities for 2018
calc2.advance_to_year(2018)
calc2.calc_all()
itax_rev2 = calc2.weighted_total('iitax')

# print reform documentation
print(Calculator.reform_documentation(params))

# print total revenue estimates for 2018
# (estimates in billons of dollars rounded to nearest tenth of a billion)
print('2018_CLP_itax_rev($B)= {:.1f}'.format(itax_rev1 * 1e-9))
print('2018_REF_itax_rev($B)= {:.1f}'.format(itax_rev2 * 1e-9))
