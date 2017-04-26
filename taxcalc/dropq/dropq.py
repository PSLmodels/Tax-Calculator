"""
dropq functions used by TaxBrain to call Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 dropq.py
# pylint --disable=locally-disabled dropq.py

from __future__ import print_function
import time
import numpy as np
import pandas as pd
from taxcalc.dropq.dropq_utils import (check_user_mods,
                                       random_seed_from_subdict,
                                       results,
                                       drop_records)
from taxcalc.dropq.dropq_utils import (create_dropq_distribution_table as
                                       dropq_dist_table)
from taxcalc.dropq.dropq_utils import (create_dropq_difference_table as
                                       dropq_diff_table)
from taxcalc.dropq.dropq_utils import create_json_table
from taxcalc import (Calculator, Growfactors, Records,
                     Policy, Consumption, Behavior, Growdiff,
                     proportional_change_gdp, TABLE_LABELS,
                     create_distribution_table)


# specify constants
PLAN_COLUMN_TYPES = [float] * len(TABLE_LABELS)

DIFF_COLUMN_TYPES = [int, int, int, float, float, str, str, str]

DECILE_ROW_NAMES = ['perc0-10', 'perc10-20', 'perc20-30', 'perc30-40',
                    'perc40-50', 'perc50-60', 'perc60-70', 'perc70-80',
                    'perc80-90', 'perc90-100', 'all']

BIN_ROW_NAMES = ['less_than_10', 'ten_twenty', 'twenty_thirty', 'thirty_forty',
                 'forty_fifty', 'fifty_seventyfive', 'seventyfive_hundred',
                 'hundred_twohundred', 'twohundred_fivehundred',
                 'fivehundred_thousand', 'thousand_up', 'all']

TOTAL_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']

GDP_ELAST_ROW_NAMES = ['gdp_elasticity']

OGUSA_ROW_NAMES = ['GDP', 'Consumption', 'Investment', 'Hours Worked',
                   'Wages', 'Interest Rates', 'Total Taxes']


def dropq_calculate(year_n, start_year,
                    taxrec_df, user_mods,
                    behavior_allowed, mask_computed):
    """
    The dropq_calculate function assumes specified user_mods is
      a dictionary returned by the Calculator.read_json_parameter_files()
      function with an extra key:value pair that is specified as
      'gdp_elasticity': {'value': <float_value>}.
    The function returns (calc1, calc2, mask) where
      calc1 is pre-reform Calculator object calculated for year_n,
      calc2 is post-reform Calculator object calculated for year_n, and
      mask is boolean array if compute_mask=True or None otherwise
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-statements

    check_user_mods(user_mods)

    # specify Consumption instance
    consump = Consumption()
    consump_assumptions = user_mods['consumption']
    consump.update_consumption(consump_assumptions)

    # specify growdiff_baseline and growdiff_response
    growdiff_baseline = Growdiff()
    growdiff_response = Growdiff()
    growdiff_base_assumps = user_mods['growdiff_baseline']
    growdiff_resp_assumps = user_mods['growdiff_response']
    growdiff_baseline.update_growdiff(growdiff_base_assumps)
    growdiff_response.update_growdiff(growdiff_resp_assumps)

    # create pre-reform and post-reform Growfactors instances
    growfactors_pre = Growfactors()
    growdiff_baseline.apply_to(growfactors_pre)
    growfactors_post = Growfactors()
    growdiff_baseline.apply_to(growfactors_post)
    growdiff_response.apply_to(growfactors_post)

    # create pre-reform Calculator instance
    recs1 = Records(data=taxrec_df.copy(deep=True),
                    gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=recs1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    calc1.calc_all()
    assert calc1.current_year == start_year

    # optionally compute mask
    if mask_computed:
        # create pre-reform Calculator instance with extra income
        recs1p = Records(data=taxrec_df.copy(deep=True),
                         gfactors=growfactors_pre)
        # add one dollar to total wages and salaries of each filing unit
        recs1p.e00200 += 1.0  # pylint: disable=no-member
        policy1p = Policy(gfactors=growfactors_pre)
        # create Calculator with recs1p and calculate for start_year
        calc1p = Calculator(policy=policy1p, records=recs1p,
                            consumption=consump)
        while calc1p.current_year < start_year:
            calc1p.increment_year()
        calc1p.calc_all()
        assert calc1p.current_year == start_year
        # compute mask that shows which of the calc1 and calc1p results differ
        res1 = results(calc1)
        res1p = results(calc1p)
        mask = (res1.iitax != res1p.iitax)
    else:
        mask = None

    # specify Behavior instance
    behv = Behavior()
    behavior_assumps = user_mods['behavior']
    behv.update_behavior(behavior_assumps)

    # always prevent both behavioral response and growdiff response
    if behv.has_any_response() and growdiff_response.has_any_response():
        msg = 'BOTH behavior AND growdiff_response HAVE RESPONSE'
        raise ValueError(msg)

    # optionally prevent behavioral response
    if behv.has_any_response() and not behavior_allowed:
        msg = 'A behavior RESPONSE IS NOT ALLOWED'
        raise ValueError(msg)

    # create post-reform Calculator instance
    recs2 = Records(data=taxrec_df.copy(deep=True),
                    gfactors=growfactors_post)
    policy2 = Policy(gfactors=growfactors_post)
    policy_reform = user_mods['policy']
    policy2.implement_reform(policy_reform)
    calc2 = Calculator(policy=policy2, records=recs2,
                       consumption=consump, behavior=behv)
    while calc2.current_year < start_year:
        calc2.increment_year()
    calc2.calc_all()
    assert calc2.current_year == start_year

    # increment Calculator objects for year_n years and calculate
    for _ in range(0, year_n):
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    if calc2.behavior.has_response():
        calc2 = Behavior.response(calc1, calc2)
    else:
        calc2.calc_all()

    # return calculated Calculator objects and mask
    return (calc1, calc2, mask)


def random_seed(user_mods):
    """
    Compute random seed based on specified user_mods, which is a
    dictionary returned by the Calculator.read_json_parameter_files()
    function with an extra key:value pair that is specified as
    'gdp_elasticity': {'value': <float_value>}.
    """
    ans = 0
    for subdict_name in user_mods:
        if subdict_name != 'gdp_elasticity':
            ans += random_seed_from_subdict(user_mods[subdict_name])
    return ans % np.iinfo(np.uint32).max  # pylint: disable=no-member


def dropq_summary(df1, df2, mask):
    """
    df1 contains raw results for the standard plan X and X'
    df2 contains raw results the user-specified plan (Plan Y)
    mask is the boolean mask where X and X' match
    """
    # pylint: disable=too-many-locals

    df1, df2 = drop_records(df1, df2, mask)

    # Totals for diff between baseline and reform
    dec_sum = (df2['tax_diff_dec'] * df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin'] * df2['s006']).sum()
    pr_dec_sum = (df2['payrolltax_diff_dec'] * df2['s006']).sum()
    pr_bin_sum = (df2['payrolltax_diff_bin'] * df2['s006']).sum()
    combined_dec_sum = (df2['combined_diff_dec'] * df2['s006']).sum()
    combined_bin_sum = (df2['combined_diff_bin'] * df2['s006']).sum()

    # Totals for baseline
    sum_baseline = (df1['iitax'] * df1['s006']).sum()
    pr_sum_baseline = (df1['payrolltax'] * df1['s006']).sum()
    combined_sum_baseline = (df1['combined'] * df1['s006']).sum()

    # Totals for reform
    sum_reform = (df2['iitax_dec'] * df2['s006']).sum()
    pr_sum_reform = (df2['payrolltax_dec'] * df2['s006']).sum()
    combined_sum_reform = (df2['combined_dec'] * df2['s006']).sum()

    # Create difference tables, grouped by deciles and bins
    diffs_dec = dropq_diff_table(df1, df2,
                                 groupby='weighted_deciles',
                                 res_col='tax_diff',
                                 diff_col='iitax',
                                 suffix='_dec', wsum=dec_sum)

    diffs_bin = dropq_diff_table(df1, df2,
                                 groupby='webapp_income_bins',
                                 res_col='tax_diff',
                                 diff_col='iitax',
                                 suffix='_bin', wsum=bin_sum)

    pr_diffs_dec = dropq_diff_table(df1, df2,
                                    groupby='weighted_deciles',
                                    res_col='payrolltax_diff',
                                    diff_col='payrolltax',
                                    suffix='_dec', wsum=pr_dec_sum)

    pr_diffs_bin = dropq_diff_table(df1, df2,
                                    groupby='webapp_income_bins',
                                    res_col='payrolltax_diff',
                                    diff_col='payrolltax',
                                    suffix='_bin', wsum=pr_bin_sum)

    comb_diffs_dec = dropq_diff_table(df1, df2,
                                      groupby='weighted_deciles',
                                      res_col='combined_diff',
                                      diff_col='combined',
                                      suffix='_dec', wsum=combined_dec_sum)

    comb_diffs_bin = dropq_diff_table(df1, df2,
                                      groupby='webapp_income_bins',
                                      res_col='combined_diff',
                                      diff_col='combined',
                                      suffix='_bin', wsum=combined_bin_sum)

    mX_dec = create_distribution_table(df1, groupby='weighted_deciles',
                                       result_type='weighted_sum')

    mY_dec = dropq_dist_table(df2, groupby='weighted_deciles',
                              result_type='weighted_sum', suffix='_dec')

    mX_bin = create_distribution_table(df1, groupby='webapp_income_bins',
                                       result_type='weighted_sum')

    mY_bin = dropq_dist_table(df2, groupby='webapp_income_bins',
                              result_type='weighted_sum', suffix='_bin')

    return (mY_dec, mX_dec, diffs_dec, pr_diffs_dec, comb_diffs_dec,
            mY_bin, mX_bin, diffs_bin, pr_diffs_bin, comb_diffs_bin,
            dec_sum, pr_dec_sum, combined_dec_sum,
            sum_baseline, pr_sum_baseline, combined_sum_baseline,
            sum_reform, pr_sum_reform, combined_sum_reform)


def run_nth_year_gdp_elast_model(year_n, start_year,
                                 taxrec_df, user_mods,
                                 return_json=True):
    """
    The run_nth_year_gdp_elast_model function assumes user_mods is a
    dictionary returned by the Calculator.read_json_parameter_files()
    function with an extra key:value pair that is specified as
    'gdp_elasticity': {'value': <float_value>}.
    """
    # create calc1 and calc2 calculated for year_n
    (calc1, calc2, _) = dropq_calculate(year_n, start_year,
                                        taxrec_df, user_mods,
                                        behavior_allowed=False,
                                        mask_computed=False)

    # compute GDP effect given assumed gdp elasticity
    gdp_elasticity = user_mods['gdp_elasticity']['value']
    gdp_effect = proportional_change_gdp(calc1, calc2, gdp_elasticity)

    # return gdp_effect results
    if return_json:
        gdp_df = pd.DataFrame(data=[gdp_effect], columns=['col0'])
        gdp_elast_names_i = [x + '_' + str(year_n)
                             for x in GDP_ELAST_ROW_NAMES]
        gdp_elast_total = create_json_table(gdp_df,
                                            row_names=gdp_elast_names_i,
                                            num_decimals=5)
        gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())
        return gdp_elast_total
    else:
        return gdp_effect


def run_nth_year_tax_calc_model(year_n, start_year,
                                taxrec_df, user_mods,
                                return_json=True):
    """
    The run_nth_year_tax_calc_model function assumes user_mods is a
    dictionary returned by the Calculator.read_json_parameter_files()
    function with an extra key:value pair that is specified as
    'gdp_elasticity': {'value': <float_value>}.
    """
    # pylint: disable=too-many-locals
    start_time = time.time()

    # create calc1 and calc2 calculated for year_n and mask
    (calc1, calc2, mask) = dropq_calculate(year_n, start_year,
                                           taxrec_df, user_mods,
                                           behavior_allowed=True,
                                           mask_computed=True)

    # extract raw results from calc1 and calc2
    rawres1 = results(calc1)
    rawres2 = results(calc2)

    # seed random number generator with a seed value based on user_mods
    seed = random_seed(user_mods)
    print('seed={}'.format(seed))
    np.random.seed(seed)  # pylint: disable=no-member

    # construct dropq summary results from raw results
    (mY_dec, mX_dec, df_dec, pdf_dec, cdf_dec,
     mY_bin, mX_bin, df_bin, pdf_bin, cdf_bin,
     diff_sum, payrolltax_diff_sum, combined_diff_sum,
     sum_baseline, pr_sum_baseline, combined_sum_baseline,
     sum_reform, pr_sum_reform,
     combined_sum_reform) = dropq_summary(rawres1, rawres2, mask)

    elapsed_time = time.time() - start_time
    print('elapsed time for this run: ', elapsed_time)

    # construct DataFrames containing selected summary results
    tots = [diff_sum, payrolltax_diff_sum, combined_diff_sum]
    fiscal_tots_diff = pd.DataFrame(data=tots, index=TOTAL_ROW_NAMES)

    tots_baseline = [sum_baseline, pr_sum_baseline, combined_sum_baseline]
    fiscal_tots_baseline = pd.DataFrame(data=tots_baseline,
                                        index=TOTAL_ROW_NAMES)

    tots_reform = [sum_reform, pr_sum_reform, combined_sum_reform]
    fiscal_tots_reform = pd.DataFrame(data=tots_reform,
                                      index=TOTAL_ROW_NAMES)

    # remove negative incomes from selected summary results
    df_bin.drop(df_bin.index[0], inplace=True)
    pdf_bin.drop(pdf_bin.index[0], inplace=True)
    cdf_bin.drop(cdf_bin.index[0], inplace=True)
    mY_bin.drop(mY_bin.index[0], inplace=True)
    mX_bin.drop(mX_bin.index[0], inplace=True)

    def append_year(x):
        """
        append_year embedded function
        """
        x.columns = [str(col) + '_{}'.format(year_n) for col in x.columns]
        return x

    # optionally return non-JSON results
    if not return_json:
        return (append_year(mY_dec), append_year(mX_dec), append_year(df_dec),
                append_year(pdf_dec), append_year(cdf_dec),
                append_year(mY_bin), append_year(mX_bin), append_year(df_bin),
                append_year(pdf_bin), append_year(cdf_bin),
                append_year(fiscal_tots_diff),
                append_year(fiscal_tots_baseline),
                append_year(fiscal_tots_reform))

    # optionally construct JSON results
    decile_row_names_i = [x + '_' + str(year_n) for x in DECILE_ROW_NAMES]
    mY_dec_table_i = create_json_table(mY_dec,
                                       row_names=decile_row_names_i,
                                       column_types=PLAN_COLUMN_TYPES)
    mX_dec_table_i = create_json_table(mX_dec,
                                       row_names=decile_row_names_i,
                                       column_types=PLAN_COLUMN_TYPES)
    df_dec_table_i = create_json_table(df_dec,
                                       row_names=decile_row_names_i,
                                       column_types=DIFF_COLUMN_TYPES)
    pdf_dec_table_i = create_json_table(pdf_dec,
                                        row_names=decile_row_names_i,
                                        column_types=DIFF_COLUMN_TYPES)
    cdf_dec_table_i = create_json_table(cdf_dec,
                                        row_names=decile_row_names_i,
                                        column_types=DIFF_COLUMN_TYPES)
    bin_row_names_i = [x + '_' + str(year_n) for x in BIN_ROW_NAMES]
    mY_bin_table_i = create_json_table(mY_bin,
                                       row_names=bin_row_names_i,
                                       column_types=PLAN_COLUMN_TYPES)
    mX_bin_table_i = create_json_table(mX_bin,
                                       row_names=bin_row_names_i,
                                       column_types=PLAN_COLUMN_TYPES)
    df_bin_table_i = create_json_table(df_bin,
                                       row_names=bin_row_names_i,
                                       column_types=DIFF_COLUMN_TYPES)
    pdf_bin_table_i = create_json_table(pdf_bin,
                                        row_names=bin_row_names_i,
                                        column_types=DIFF_COLUMN_TYPES)
    cdf_bin_table_i = create_json_table(cdf_bin,
                                        row_names=bin_row_names_i,
                                        column_types=DIFF_COLUMN_TYPES)
    total_row_names_i = [x + '_' + str(year_n) for x in TOTAL_ROW_NAMES]
    fiscal_yr_total_df = create_json_table(fiscal_tots_diff,
                                           row_names=total_row_names_i)
    fiscal_yr_total_df = dict((k, v[0]) for k, v in fiscal_yr_total_df.items())
    fiscal_yr_total_bl = create_json_table(fiscal_tots_baseline,
                                           row_names=total_row_names_i)
    fiscal_yr_total_bl = dict((k, v[0]) for k, v in fiscal_yr_total_bl.items())
    fiscal_yr_total_rf = create_json_table(fiscal_tots_reform,
                                           row_names=total_row_names_i)
    fiscal_yr_total_rf = dict((k, v[0]) for k, v in fiscal_yr_total_rf.items())

    # return JSON results
    return (mY_dec_table_i, mX_dec_table_i, df_dec_table_i, pdf_dec_table_i,
            cdf_dec_table_i, mY_bin_table_i, mX_bin_table_i, df_bin_table_i,
            pdf_bin_table_i, cdf_bin_table_i, fiscal_yr_total_df,
            fiscal_yr_total_bl, fiscal_yr_total_rf)


def format_macro_results(diff_data, return_json=True):
    """
    format_macro_results function.
    """
    ogusadf = pd.DataFrame(diff_data)
    if not return_json:
        return ogusadf
    column_types = [float] * diff_data.shape[1]
    df_ogusa_table = create_json_table(ogusadf,
                                       row_names=OGUSA_ROW_NAMES,
                                       column_types=column_types,
                                       num_decimals=3)
    return df_ogusa_table
