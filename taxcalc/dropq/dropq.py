"""
The dropq functions are used by TaxBrain to call Tax-Calculator in order
to maintain the privacy of the micro data being used by TaxBrain.
This is done by "fuzzing" reform results for several randomly selected
filing units in each table cell.  The filing units randomly selected
differs for each policy reform and the "fuzzing" involves replacing the
post-reform tax results for the selected units with those the pre-reform
tax results for those selected units.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 dropq.py
# pylint --disable=locally-disabled dropq.py

from __future__ import print_function
import time
import numpy as np
import pandas as pd
from taxcalc.dropq.dropq_utils import (dropq_calculate,
                                       random_seed,
                                       dropq_summary)
from taxcalc import (results, TABLE_LABELS, proportional_change_gdp,
                     Growdiff, Growfactors, Policy)


# specify constants
PLAN_COLUMN_TYPES = [float] * len(TABLE_LABELS)

DIFF_COLUMN_TYPES = [int, int, int, float, float, str, str, str, str]

DECILE_ROW_NAMES = ['perc0-10', 'perc10-20', 'perc20-30', 'perc30-40',
                    'perc40-50', 'perc50-60', 'perc60-70', 'perc70-80',
                    'perc80-90', 'perc90-100', 'all']

BIN_ROW_NAMES = ['less_than_10', 'ten_twenty', 'twenty_thirty', 'thirty_forty',
                 'forty_fifty', 'fifty_seventyfive', 'seventyfive_hundred',
                 'hundred_twohundred', 'twohundred_fivehundred',
                 'fivehundred_thousand', 'thousand_up', 'all']

TOTAL_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']

GDP_ELAST_ROW_NAMES = ['gdp_elasticity']


def reform_warnings_errors(user_mods):
    """
    The reform_warnings_errors function assumes user_mods is a dictionary
    returned by the Calculator.read_json_parameter_files() function.

    This function returns a dictionary containing two STR:STR pairs:
    {'warnings': '<empty-or-message(s)>', 'errors': '<empty-or-message(s)>'}
    In each pair the second string is empty if there are no messages.
    Any returned messages are generated using current_law_policy.json
    information on known policy parameter names and parameter value ranges.

    Note that this function will return one or more error messages if
    the user_mods['policy'] dictionary contains any unknown policy
    parameter names or if any *_cpi parameters have values other than
    True or False.  These situations prevent implementing the policy
    reform specified in user_mods, and therefore, no range-related
    warnings or errors will be returned in this case.
    """
    rtn_dict = {'warnings': '', 'errors': ''}
    # create Growfactors object
    gdiff_baseline = Growdiff()
    gdiff_baseline.update_growdiff(user_mods['growdiff_baseline'])
    gdiff_response = Growdiff()
    gdiff_response.update_growdiff(user_mods['growdiff_response'])
    growfactors = Growfactors()
    gdiff_baseline.apply_to(growfactors)
    gdiff_response.apply_to(growfactors)
    # create Policy object and implement reform
    pol = Policy(gfactors=growfactors)
    try:
        pol.implement_reform(user_mods['policy'])
        rtn_dict['warnings'] = pol.reform_warnings
        rtn_dict['errors'] = pol.reform_errors
    except ValueError as valerr_msg:
        rtn_dict['errors'] = valerr_msg.__str__()
    return rtn_dict


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
    rawres1 = results(calc1.records)
    rawres2 = results(calc2.records)

    # seed random number generator with a seed value based on user_mods
    seed = random_seed(user_mods)
    print('seed={}'.format(seed))
    np.random.seed(seed)  # pylint: disable=no-member

    # construct dropq summary results from raw results
    (dist1_dec, dist2_dec,
     diff_itax_dec, diff_ptax_dec, diff_comb_dec,
     dist1_bin, dist2_bin,
     diff_itax_bin, diff_ptax_bin, diff_comb_bin,
     aggr_itax_d, aggr_ptax_d, aggr_comb_d,
     aggr_itax_1, aggr_ptax_1, aggr_comb_1,
     aggr_itax_2, aggr_ptax_2, aggr_comb_2) = dropq_summary(rawres1,
                                                            rawres2,
                                                            mask)

    # construct DataFrames containing aggregate tax totals
    # ... for reform-minus-baseline difference
    aggrd = [aggr_itax_d, aggr_ptax_d, aggr_comb_d]
    aggr_d = pd.DataFrame(data=aggrd, index=TOTAL_ROW_NAMES)
    # ... for baseline
    aggr1 = [aggr_itax_1, aggr_ptax_1, aggr_comb_1]
    aggr_1 = pd.DataFrame(data=aggr1, index=TOTAL_ROW_NAMES)
    # ... for reform
    aggr2 = [aggr_itax_2, aggr_ptax_2, aggr_comb_2]
    aggr_2 = pd.DataFrame(data=aggr2, index=TOTAL_ROW_NAMES)

    elapsed_time = time.time() - start_time
    print('elapsed time for this run: ', elapsed_time)

    def append_year(pdf):
        """
        append_year embedded function revises all column names in pdf
        """
        pdf.columns = [str(col) + '_{}'.format(year_n) for col in pdf.columns]
        return pdf

    # optionally return non-JSON results
    if not return_json:
        return (append_year(dist2_dec),
                append_year(dist1_dec),
                append_year(diff_itax_dec),
                append_year(diff_ptax_dec),
                append_year(diff_comb_dec),
                append_year(dist2_bin),
                append_year(dist1_bin),
                append_year(diff_itax_bin),
                append_year(diff_ptax_bin),
                append_year(diff_comb_bin),
                append_year(aggr_d),
                append_year(aggr_1),
                append_year(aggr_2))

    # optionally construct JSON results tables for year n
    dec_row_names_n = [x + '_' + str(year_n) for x in DECILE_ROW_NAMES]
    dist2_dec_table_n = create_json_table(dist2_dec,
                                          row_names=dec_row_names_n,
                                          column_types=PLAN_COLUMN_TYPES)
    dist1_dec_table_n = create_json_table(dist1_dec,
                                          row_names=dec_row_names_n,
                                          column_types=PLAN_COLUMN_TYPES)
    diff_itax_dec_table_n = create_json_table(diff_itax_dec,
                                              row_names=dec_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    diff_ptax_dec_table_n = create_json_table(diff_ptax_dec,
                                              row_names=dec_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    diff_comb_dec_table_n = create_json_table(diff_comb_dec,
                                              row_names=dec_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    bin_row_names_n = [x + '_' + str(year_n) for x in BIN_ROW_NAMES]
    dist2_bin_table_n = create_json_table(dist2_bin,
                                          row_names=bin_row_names_n,
                                          column_types=PLAN_COLUMN_TYPES)
    dist1_bin_table_n = create_json_table(dist1_bin,
                                          row_names=bin_row_names_n,
                                          column_types=PLAN_COLUMN_TYPES)
    diff_itax_bin_table_n = create_json_table(diff_itax_bin,
                                              row_names=bin_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    diff_ptax_bin_table_n = create_json_table(diff_ptax_bin,
                                              row_names=bin_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    diff_comb_bin_table_n = create_json_table(diff_comb_bin,
                                              row_names=bin_row_names_n,
                                              column_types=DIFF_COLUMN_TYPES)
    total_row_names_n = [x + '_' + str(year_n) for x in TOTAL_ROW_NAMES]
    aggr_d_table_n = create_json_table(aggr_d,
                                       row_names=total_row_names_n)
    aggr_d_table_n = dict((k, v[0]) for k, v in aggr_d_table_n.items())
    aggr_1_table_n = create_json_table(aggr_1,
                                       row_names=total_row_names_n)
    aggr_1_table_n = dict((k, v[0]) for k, v in aggr_1_table_n.items())
    aggr_2_table_n = create_json_table(aggr_2,
                                       row_names=total_row_names_n)
    aggr_2_table_n = dict((k, v[0]) for k, v in aggr_2_table_n.items())

    # return JSON results
    return (dist2_dec_table_n,
            dist1_dec_table_n,
            diff_itax_dec_table_n,
            diff_ptax_dec_table_n,
            diff_comb_dec_table_n,
            dist2_bin_table_n,
            dist1_bin_table_n,
            diff_itax_bin_table_n,
            diff_ptax_bin_table_n,
            diff_comb_bin_table_n,
            aggr_d_table_n,
            aggr_1_table_n,
            aggr_2_table_n)


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
        gdp_elast_names_n = [x + '_' + str(year_n)
                             for x in GDP_ELAST_ROW_NAMES]
        gdp_elast_total = create_json_table(gdp_df,
                                            row_names=gdp_elast_names_n,
                                            num_decimals=5)
        gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())
        return gdp_elast_total
    else:
        return gdp_effect


def create_json_table(dframe, row_names=None, column_types=None,
                      num_decimals=2):
    """
    Create and return dictionary with JSON-like contents from specified dframe.
    """
    # embedded formatted_string function
    def formatted_string(val, _type, num_decimals):
        """
        Return formatted conversion of number val into a string.
        """
        float_types = [float, np.dtype('f8')]
        int_types = [int, np.dtype('i8')]
        frmat_str = "0:.{num}f".format(num=num_decimals)
        frmat_str = "{" + frmat_str + "}"
        try:
            if _type in float_types or _type is None:
                return frmat_str.format(val)
            elif _type in int_types:
                return str(int(val))
            elif _type == str:
                return str(val)
            else:
                raise NotImplementedError()
        except ValueError:
            # try making it a string - good luck!
            return str(val)
    # high-level create_json_table function logic
    out = dict()
    if row_names is None:
        row_names = [str(x) for x in list(dframe.index)]
    else:
        assert len(row_names) == len(dframe.index)
    if column_types is None:
        column_types = [dframe[col].dtype for col in dframe.columns]
    else:
        assert len(column_types) == len(dframe.columns)
    for idx, row_name in zip(dframe.index, row_names):
        row_out = out.get(row_name, [])
        for col, dtype in zip(dframe.columns, column_types):
            row_out.append(formatted_string(dframe.loc[idx, col],
                                            dtype, num_decimals))
        out[row_name] = row_out
    return out
