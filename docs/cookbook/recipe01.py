from __future__ import print_function  # necessary only if using Python 2.7
from taxcalc import *
import urllib as url_lib  # on Python 3.6 use "import urllib.request as url_lib"

# read two "old" reform files from Tax-Calculator website
# ("old" means the reform files are defined relative to pre-TCJA policy)
#   For more about the compound-reform technique used in this recipe,
#   read answer to Question 1 of FAQ at the following URL:
#   https://github.com/open-source-economics/Tax-Calculator/issues/1830
BASE_URL = ('https://raw.githubusercontent.com/'
            'open-source-economics/Tax-Calculator/master/taxcalc/reforms/')

baseline_name = '2017_law.json'  # pre-TCJA policy
baseline_text = url_lib.urlopen(BASE_URL + baseline_name).read()
baseline = Calculator.read_json_param_objects(baseline_text, None)

reform1_name = 'TCJA_Senate.json'  # TCJA as orginally proposed in Senate
reform1_text = url_lib.urlopen(BASE_URL + reform1_name).read()
reform2_name = 'TCJA_Reconciliation.json'  # TCJA as passed by Congress
reform2_text = url_lib.urlopen(BASE_URL + reform2_name).read()

# specify Policy object for static analysis of reform1 relative to pre-TCJA
reform1 = Calculator.read_json_param_objects(reform1_text, None)
policy1 = Policy()
policy1.implement_reform(baseline['policy'])
if policy1.reform_errors:
    print(policy1.reform_errors)
    exit(1)
policy1.implement_reform(reform1['policy'])
if policy1.reform_errors:
    print(policy1.reform_errors)
    exit(1)

# specify Policy object for static analysis of reform2 relative to pre-TCJA
reform2 = Calculator.read_json_param_objects(reform2_text, None)
policy2 = Policy()
policy1.implement_reform(baseline['policy'])
if policy1.reform_errors:
    print(policy1.reform_errors)
    exit(1)
policy2.implement_reform(reform2['policy'])
if policy2.reform_errors:
    print(policy2.reform_errors)
    exit(1)

cyr = 2018

# specify Calculator objects using policy1 and policy2 and calculate for cyr
calc1 = Calculator(policy=policy1, records=Records.cps_constructor())
calc1.advance_to_year(cyr)
calc1.calc_all()
calc2 = Calculator(policy=policy2, records=Records.cps_constructor())
calc2.advance_to_year(cyr)
calc2.calc_all()

# compare aggregate individual income tax revenue in cyr
iitax_rev1 = calc1.weighted_total('iitax')
iitax_rev2 = calc2.weighted_total('iitax')

# construct reform2-vs-reform1 difference table with results for income deciles
# NOTE: the bottom decile contains filing units with negative or zero
#       expanded income in the baseline (calc1) Calculator object;
#       if you want to somehow drop the filing units with non-positive
#       expanded income, extract the required data from calc1 and calc2
#       and use the extracted data to construct the table you want.
diff_table = calc1.difference_table(calc2, tax_to_diff='iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tax_cut', 'tax_inc',
                'tot_change', 'mean', 'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'taxfall(#m)', 'taxrise(#m)',
                'agg_diff($b)', 'mean_diff($)', 'aftertax_income_diff(%)']
scaling_factors = [1e-6, 1e-6, 1e-6, 1e-9, 1e0, 1e0, 1e0]
for dname, ename, sfactor in zip(dif_colnames, ext_colnames, scaling_factors):
    diff_extract[ename] = diff_table[dname] * sfactor

# print total revenue estimates for cyr
# (estimates in billons of dollars rounded to nearest tenth of a billion)
print('{}_REFORM1_iitax_rev($B)= {:.1f}'.format(cyr, iitax_rev1 * 1e-9))
print('{}_REFORM2_iitax_rev($B)= {:.1f}'.format(cyr, iitax_rev2 * 1e-9))
print('')

title = 'Extract of {} income-tax difference table by expanded-income decile'
print(title.format(cyr))
print('(taxfall is count of funits with cut in income tax in reform 2 vs 1)')
print('(taxrise is count of funits with rise in income tax in reform 2 vs 1)')
print(diff_extract)
print('Note: deciles are numbered 0-9 with top decile divided into bottom 5%,')
print('      next 4%, and top 1%, in the lines numbered 11-13, respectively')
