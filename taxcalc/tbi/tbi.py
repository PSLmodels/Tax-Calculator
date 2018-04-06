"""
The public API of the TaxBrain Interface (tbi).

The tbi functions are used by TaxBrain to call Tax-Calculator in order
to do distributed processing of TaxBrain runs and in order to maintain
the privacy of the IRS-SOI PUF data being used by TaxBrain.  Maintaining
privacy is done by "fuzzing" reform results for several randomly selected
filing units in each table cell.  The filing units randomly selected
differ for each policy reform and the "fuzzing" involves replacing the
post-reform tax results for the selected units with their pre-reform
tax results.
"""
# CODING-STYLE CHECKS:
# pep8 tbi.py
# pylint --disable=locally-disabled tbi.py

from __future__ import print_function
import gc
import time
import numpy as np
import pandas as pd
from taxcalc.tbi.tbi_utils import (check_years_return_first_year,
                                   calculate,
                                   random_seed,
                                   summary,
                                   create_dict_table,
                                   AGGR_ROW_NAMES)
from taxcalc import (DIST_TABLE_LABELS, DIFF_TABLE_LABELS,
                     proportional_change_in_gdp,
                     Growdiff, Growfactors, Policy)

AGG_ROW_NAMES = AGGR_ROW_NAMES

GDP_ELAST_ROW_NAMES = ['gdp_proportional_change']


def reform_warnings_errors(user_mods):
    """
    The reform_warnings_errors function assumes user_mods is a dictionary
    returned by the Calculator.read_json_param_objects() function.

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
        pol.implement_reform(user_mods['policy'],
                             print_warnings=False,
                             raise_errors=False)
        rtn_dict['warnings'] = pol.reform_warnings
        rtn_dict['errors'] = pol.reform_errors
    except ValueError as valerr_msg:
        rtn_dict['errors'] = valerr_msg.__str__()
    return rtn_dict


def run_nth_year_tax_calc_model(year_n, start_year,
                                use_puf_not_cps,
                                use_full_sample,
                                user_mods,
                                return_dict=True):
    """
    The run_nth_year_tax_calc_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-locals

    start_time = time.time()

    # create calc1 and calc2 calculated for year_n and mask
    check_years_return_first_year(year_n, start_year, use_puf_not_cps)
    (calc1, calc2, mask) = calculate(year_n, start_year,
                                     use_puf_not_cps, use_full_sample,
                                     user_mods,
                                     behavior_allowed=True)

    # extract raw results from calc1 and calc2
    rawres1 = calc1.distribution_table_dataframe()
    rawres2 = calc2.distribution_table_dataframe()

    # delete calc1 and calc2 now that raw results have been extracted
    del calc1
    del calc2
    gc.collect()

    # seed random number generator with a seed value based on user_mods
    seed = random_seed(user_mods)
    print('seed={}'.format(seed))
    np.random.seed(seed)  # pylint: disable=no-member

    # construct TaxBrain summary results from raw results
    summ = summary(rawres1, rawres2, mask)
    del rawres1
    del rawres2
    gc.collect()

    def append_year(pdf):
        """
        append_year embedded function revises all column names in pdf
        """
        pdf.columns = [str(col) + '_{}'.format(year_n) for col in pdf.columns]
        return pdf

    # optionally return non-JSON-like results
    if not return_dict:
        res = dict()
        for tbl in summ:
            res[tbl] = append_year(summ[tbl])
        elapsed_time = time.time() - start_time
        print('elapsed time for this run: {:.1f}'.format(elapsed_time))
        return res

    # optionally construct JSON-like results dictionaries for year n
    dec_rownames = list(summ['diff_comb_xdec'].index.values)
    dec_row_names_n = [x + '_' + str(year_n) for x in dec_rownames]
    bin_rownames = list(summ['diff_comb_xbin'].index.values)
    bin_row_names_n = [x + '_' + str(year_n) for x in bin_rownames]
    agg_row_names_n = [x + '_' + str(year_n) for x in AGG_ROW_NAMES]
    dist_column_types = [float] * len(DIST_TABLE_LABELS)
    diff_column_types = [float] * len(DIFF_TABLE_LABELS)
    info = dict()
    for tbl in summ:
        info[tbl] = {'row_names': [], 'col_types': []}
        if 'dec' in tbl:
            info[tbl]['row_names'] = dec_row_names_n
        elif 'bin' in tbl:
            info[tbl]['row_names'] = bin_row_names_n
        else:
            info[tbl]['row_names'] = agg_row_names_n
        if 'dist' in tbl:
            info[tbl]['col_types'] = dist_column_types
        elif 'diff' in tbl:
            info[tbl]['col_types'] = diff_column_types
    res = dict()
    for tbl in summ:
        if 'aggr' in tbl:
            res_table = create_dict_table(summ[tbl],
                                          row_names=info[tbl]['row_names'])
            res[tbl] = dict((k, v[0]) for k, v in res_table.items())
        else:
            res[tbl] = create_dict_table(summ[tbl],
                                         row_names=info[tbl]['row_names'],
                                         column_types=info[tbl]['col_types'])

    elapsed_time = time.time() - start_time
    print('elapsed time for this run: {:.1f}'.format(elapsed_time))

    return res


def run_nth_year_gdp_elast_model(year_n, start_year,
                                 use_puf_not_cps,
                                 use_full_sample,
                                 user_mods,
                                 gdp_elasticity,
                                 return_dict=True):
    """
    The run_nth_year_gdp_elast_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-locals

    # calculate gdp_effect
    fyear = check_years_return_first_year(year_n, start_year, use_puf_not_cps)
    if year_n > 0 and (start_year + year_n) > fyear:
        # create calc1 and calc2 calculated for year_n - 1
        (calc1, calc2, _) = calculate((year_n - 1), start_year,
                                      use_puf_not_cps,
                                      use_full_sample,
                                      user_mods,
                                      behavior_allowed=False)
        # compute GDP effect given specified gdp_elasticity
        gdp_effect = proportional_change_in_gdp((start_year + year_n),
                                                calc1, calc2, gdp_elasticity)
    else:
        gdp_effect = 0.0

    # return gdp_effect results
    if return_dict:
        gdp_df = pd.DataFrame(data=[gdp_effect], columns=['col0'])
        gdp_elast_names_n = [x + '_' + str(year_n)
                             for x in GDP_ELAST_ROW_NAMES]
        gdp_elast_total = create_dict_table(gdp_df,
                                            row_names=gdp_elast_names_n,
                                            num_decimals=5)
        gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())
        return gdp_elast_total
    return gdp_effect
