from taxcalc import *
import pandas as pd
import taxcalc
import json
import numpy.testing as npt

STATS_COLUMNS = ['c00100', '_standard', 'c04470', 'c04600', 'c04800', 'c05200',
                 'c09600', 'c05800', 'c09200', '_refund', 'c07100', '_ospctax',
                 's006']

TABLE_COLUMNS = ['c00100', 'num_returns_StandardDed', '_standard',
                 'num_returns_ItemDed', 'c04470', 'c04600', 'c04800', 'c05200',
                 'num_returns_AMT', 'c09600', 'c05800', 'c09200', '_refund',
                 'c07100', '_ospctax', 's006']

def results(c):
    outputs = [getattr(c, col) for col in STATS_COLUMNS]
    return DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)

myvars = {2015:{}}
myvars[2015]['_II_rt4'] = [0.39]

#Create a Public Use File object
tax_dta = pd.read_csv("puf.csv.gz", compression='gzip')

records = Records(tax_dta)
params = Parameters(start_year=2013)

records2 = Records(tax_dta.copy(deep=True))
params2 = Parameters(start_year=2013)

#Build default plan X, advance to 2015
calc1 = Calculator(parameters=params, records=records)
calc1.increment_year()
calc1.increment_year()
assert calc1.current_year==2015

#Build plan Y, advance to 2015
calc2 = calculator(parameters=params2, records=records2, mods=myvars)
assert calc1.current_year==2015

income_bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
               199999, 499999, 1000000, 1e14]

#1. The 10-year revenue table
all_tax_tots = []

#2. plan x vars, avg by decile and total
all_mX_dec = []

#3. plan y vars, avg by decile and total
all_mY_dec = []
#4. diff, avg by decile and total
all_df_dec =[]
#5. plan x vars, avg by agi group and total
all_mX_bin = []
#6. plan y vars, avg by agi group and total
all_mY_bin = []
#7. diff, avg by agi group and total.
all_df_bin = []

for i in range(0, 10):
    calc1.calc_all()
    calc2.calc_all()

    #Select out the columns we want
    df1 = results(calc1)
    df2 = results(calc2)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2['tax_diff_dec'] = df2['_ospctax'] - df1['_ospctax']
    df2['tax_diff_bin'] = df2['_ospctax'] - df1['_ospctax']

    dec_sum = (df2['tax_diff_dec']*df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin']*df2['s006']).sum()

    # Sanity check
    npt.assert_almost_equal(dec_sum, bin_sum)

    # Difference tables, grouped by decile and bins
    diffs_dec = create_difference_table(calc1, calc2, 'weighted_deciles')

    diffs_bin = create_difference_table(calc1, calc2, 'large_agi_bins')


    #1. The 10-year revenue table
    all_tax_tots.append(dec_sum)

    #2. plan x vars, avg by decile and total
    mX_dec = create_distribution_table(calc1, groupby='weighted_deciles',
                                      result_type='weighted_sum')

    all_mX_dec.append(mX_dec)

    #3. plan y vars, avg by decile and total
    mY_dec = create_distribution_table(calc2, groupby='weighted_deciles',
                                      result_type='weighted_sum')
    all_mY_dec.append(mY_dec)

    #4. diff, avg by decile and total
    all_df_dec.append(diffs_dec)

    #5. plan x vars, avg by agi group and total
    mX_bin = create_distribution_table(calc1, groupby='large_agi_bins',
                                      result_type='weighted_sum')
    all_mX_bin.append(mX_bin)

    #6. plan y vars, avg by agi group and total
    mY_bin = create_distribution_table(calc2, groupby='large_agi_bins',
                                      result_type='weighted_sum')
    all_mY_bin.append(mY_bin)

    #7. diff, avg by agi group and total.
    all_df_bin.append(diffs_bin)
