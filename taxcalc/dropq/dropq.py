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
from taxcalc.dropq.dropq_utils import (dropq_calculate,
                                       results,
                                       random_seed,
                                       dropq_summary,
                                       create_json_table)
from taxcalc import TABLE_LABELS, proportional_change_gdp


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
