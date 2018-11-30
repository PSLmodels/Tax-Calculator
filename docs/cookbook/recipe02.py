from taxcalc import *
import behresp

# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify baseline Calculator object representing current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

cyr = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc1.advance_to_year(cyr)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# read JSON reform file
reform_filename = './ingredients/reformA.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
calc2 = Calculator(policy=pol, records=recs)

# calculate reform income tax liabilities for cyr under static assumptions
calc2.advance_to_year(cyr)
calc2.calc_all()
itax_rev2sa = calc2.weighted_total('iitax')

# specify behavioral-response assumptions
behresp_json = '{"BE_sub": {"2018": 0.25}}'
behresp_dict = Calculator.read_json_assumptions(behresp_json)

# specify Calculator object for analysis of reform with behavioral response
calc2 = Calculator(policy=pol, records=recs)
calc2.advance_to_year(cyr)
_, df2br = behresp.response(calc1, calc2, behresp_dict)

# calculate reform income tax liabilities for cyr with behavioral response
itax_rev2br = (df2br['iitax'] * df2br['s006']).sum()

# print total income tax revenue estimates for cyr
# (estimates in billons of dollars rounded to nearest hundredth of a billion)
print('{}_CURRENT_LAW_P__itax_rev($B)= {:.3f}'.format(cyr, itax_rev1 * 1e-9))
print('{}_REFORM_STATIC__itax_rev($B)= {:.3f}'.format(cyr, itax_rev2sa * 1e-9))
print('{}_REFORM_DYNAMIC_itax_rev($B)= {:.3f}'.format(cyr, itax_rev2br * 1e-9))

# create multi-year diagnostic tables for
# (1) baseline,
# (2) reform excluding behavioral responses, and
# (3) reform including behavioral responses
num_years = 3  # number of diagnostic table years beginning with cyr
dtable1 = calc1.diagnostic_table(num_years)
dtable2 = calc2.diagnostic_table(num_years)
dvar_list3 = list()
year_list3 = list()
for year in range(cyr, cyr + num_years):
    calc1.advance_to_year(year)
    calc2.advance_to_year(year)
    _, df2br = behresp.response(calc1, calc2, behresp_dict)
    dvar_list3.append(df2br)
    year_list3.append(year)
dtable3 = create_diagnostic_table(dvar_list3, year_list3)
print()
print('DIAGNOSTIC TABLE FOR BASELINE')
print(dtable1)
print('DIAGNOSTIC TABLE FOR REFORM EXCLUDING BEHAVIORAL RESPONSES')
print(dtable2)
print('DIAGNOSTIC TABLE FOR REFORM INCLUDING BEHAVIORAL RESPONSES')
print(dtable3)
