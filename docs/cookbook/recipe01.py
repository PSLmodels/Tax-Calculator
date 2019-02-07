import pandas as pd
from taxcalc import *

# read an "old" reform file from Tax-Calculator website
# ("old" means the reform file is defined relative to pre-TCJA policy)
REFORMS_URL = ('https://raw.githubusercontent.com/'
               'PSLmodels/Tax-Calculator/master/taxcalc/reforms/')

baseline_name = '2017_law.json'  # pre-TCJA policy
baseline_url = REFORMS_URL + baseline_name
baseline = Calculator.read_json_param_objects(baseline_url, None)

reform_name = 'TCJA.json'  # TCJA as passed by Congress
reform_url = REFORMS_URL + reform_name

# specify Policy object for pre-TCJA baseline
bpolicy = Policy()
bpolicy.implement_reform(baseline['policy'], print_warnings=False)
assert not bpolicy.parameter_errors

# specify Policy object for static analysis of reform relative to pre-TCJA
reform = Calculator.read_json_param_objects(reform_url, None)
rpolicy = Policy()
rpolicy.implement_reform(baseline['policy'], print_warnings=False)
assert not rpolicy.parameter_errors
rpolicy.implement_reform(reform['policy'], print_warnings=False)
assert not rpolicy.parameter_errors

cyr = 2018

# specify Calculator objects using bpolicy and rpolicy and calculate for cyr
recs = Records.cps_constructor()
calc1 = Calculator(policy=bpolicy, records=recs)
calc1.advance_to_year(cyr)
calc1.calc_all()
calc2 = Calculator(policy=rpolicy, records=recs)
calc2.advance_to_year(cyr)
calc2.calc_all()

# compare aggregate individual income tax revenue in cyr
iitax_rev1 = calc1.weighted_total('iitax')
iitax_rev2 = calc2.weighted_total('iitax')

# construct reform-vs-baseline difference table with results for income deciles
diff_table = calc2.difference_table(calc1, 'weighted_deciles', 'iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tax_cut', 'tax_inc',
                'tot_change', 'mean', 'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'taxfall(#m)', 'taxrise(#m)',
                'agg_diff($b)', 'mean_diff($)', 'aftertax_income_diff(%)']
for dname, ename in zip(dif_colnames, ext_colnames):
    diff_extract[ename] = diff_table[dname]

# print total revenue estimates for cyr
# (estimates in billons of dollars rounded to nearest tenth of a billion)
print('{}_BASELINE_iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev1 * 1e-9))
print('{}_REFORM___iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev2 * 1e-9))
print('')

# print reform-vs-baseline difference table
print(diff_extract)
