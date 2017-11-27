from __future__ import print_function  # necessary only if using Python 2.7

from taxcalc import *


# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

# NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
#       so we can continue to use pol and recs in this script without any
#       concern about side effects from Calculator method calls on calc1.

# calculate aggregate current-law income tax liabilities for 2018
calc1.advance_to_year(2018)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# read JSON reform file and use (the default) static analysis assumptions
reform_filename = './ingredients/raise_stdded_and_rates.json'
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
print('')
print(Calculator.reform_documentation(params))

# print total revenue estimates for 2018
# (estimates in billons of dollars rounded to nearest hundredth of a billion)
print('2018_CLP_itax_rev($B)= {:.2f}'.format(itax_rev1 * 1e-9))
print('2018_REF_itax_rev($B)= {:.2f}'.format(itax_rev2 * 1e-9))
print('')

# generate several other standard results tables:

# aggregate diagnostic tables for 2018
# read source code at following URL for details
# http://taxcalc.readthedocs.io/en/latest/_modules/taxcalc/utils.html#create_diagnostic_table
clp_diagnostic_table = create_diagnostic_table(calc1)
ref_diagnostic_table = create_diagnostic_table(calc2)

# income-tax distribution for 2018 with CLP and REF results side-by-side
# read source code at following URL for details
# http://taxcalc.readthedocs.io/en/latest/_modules/taxcalc/utils.html#create_distribution_table
dist_table1 = create_distribution_table(calc1.records,
                                        groupby='weighted_deciles',
                                        income_measure='expanded_income',
                                        result_type='weighted_sum')
setattr(calc2.records, 'expanded_income_baseline',
        getattr(calc1.records, 'expanded_income'))
exp_inc_baseline = 'expanded_income_baseline'
dist_table2 = create_distribution_table(calc2.records,
                                        groupby='weighted_deciles',
                                        # so can compare the two dist tables:
                                        income_measure=exp_inc_baseline,
                                        result_type='weighted_sum')
assert isinstance(dist_table1, pd.DataFrame)
assert isinstance(dist_table2, pd.DataFrame)
dist_extract = pd.DataFrame()
dist_extract['funits(#m)'] = dist_table1['s006'] * 1e-6
dist_extract['itax1($b)'] = dist_table1['iitax'] * 1e-9
dist_extract['itax2($b)'] = dist_table2['iitax'] * 1e-9
dist_extract['aftertax_inc1($b)'] = dist_table1['aftertax_income'] * 1e-9
dist_extract['aftertax_inc2($b)'] = dist_table2['aftertax_income'] * 1e-9

# income-tax difference table extract for 2018 by expanded-income decile
# read source code at following URL for details
# http://taxcalc.readthedocs.io/en/latest/_modules/taxcalc/utils.html#create_difference_table
diff_table = create_difference_table(calc1.records, calc2.records,
                                     groupby='weighted_deciles',
                                     income_measure='expanded_income',
                                     tax_to_diff='iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tot_change', 'mean',
                'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'agg_diff($b)', 'mean_diff($)',
                'aftertaxinc_diff(%)']
scaling_factors = [1e-6, 1e-9, 1e0, 1e0, 1e0]
for dname, ename, sfactor in zip(dif_colnames, ext_colnames, scaling_factors):
    diff_extract[ename] = diff_table[dname] * sfactor

print('CLP diagnostic table for 2018:')
print(clp_diagnostic_table)
print('')
print('REF diagnostic table for 2018:')
print(ref_diagnostic_table)
print('')

print('Extract of 2018 distribution tables by expanded-income decile:')
print(dist_extract)
print('Note: deciles are numbered 0-9 with top decile divided into bottom 5%,')
print('      next 4%, and top 1%, in the lines numbered 11-13, respectively')
print('')

print('Extract of 2018 income-tax difference table by expanded-income decile:')
print(diff_extract)
print('Note: deciles are numbered 0-9 with top decile divided into bottom 5%,')
print('      next 4%, and top 1%, in the lines numbered 11-13, respectively')
