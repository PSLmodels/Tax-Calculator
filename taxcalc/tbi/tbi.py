"""
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
# pep8 --ignore=E402 tbi.py
# pylint --disable=locally-disabled tbi.py

from __future__ import print_function
import time
import numpy as np
import pandas as pd
from taxcalc.tbi.tbi_utils import (calculate,
                                   random_seed,
                                   summary,
                                   AGGR_ROW_NAMES)
from taxcalc import (results, DIST_TABLE_LABELS,
                     proportional_change_gdp, Growdiff, Growfactors, Policy)


# specify constants
DIST_COLUMN_TYPES = [float] * len(DIST_TABLE_LABELS)

DIFF_COLUMN_TYPES = [int, int, int, float, float, str, str, str, str]

DEC_ROW_NAMES = ['perc0-10', 'perc10-20', 'perc20-30', 'perc30-40',
                 'perc40-50', 'perc50-60', 'perc60-70', 'perc70-80',
                 'perc80-90', 'perc90-100', 'all']

BIN_ROW_NAMES = ['less_than_10', 'ten_twenty', 'twenty_thirty', 'thirty_forty',
                 'forty_fifty', 'fifty_seventyfive', 'seventyfive_hundred',
                 'hundred_twohundred', 'twohundred_fivehundred',
                 'fivehundred_thousand', 'thousand_up', 'all']

AGG_ROW_NAMES = AGGR_ROW_NAMES

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
    (calc1, calc2, mask) = calculate(year_n, start_year,
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

    # construct TaxBrain summary results from raw results
    summ = summary(rawres1, rawres2, mask)

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
        res = dict()
        for tbl in summ:
            res[tbl] = append_year(summ[tbl])
        return res

    # optionally construct JSON results tables for year n
    dec_row_names_n = [x + '_' + str(year_n) for x in DEC_ROW_NAMES]
    bin_row_names_n = [x + '_' + str(year_n) for x in BIN_ROW_NAMES]
    agg_row_names_n = [x + '_' + str(year_n) for x in AGG_ROW_NAMES]
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
            info[tbl]['col_types'] = DIST_COLUMN_TYPES
        elif 'diff' in tbl:
            info[tbl]['col_types'] = DIFF_COLUMN_TYPES
    res = dict()
    for tbl in summ:
        if 'aggr' in tbl:
            res_table = create_json_table(summ[tbl],
                                          row_names=info[tbl]['row_names'])
            res[tbl] = dict((k, v[0]) for k, v in res_table.items())
        else:
            res[tbl] = create_json_table(summ[tbl],
                                         row_names=info[tbl]['row_names'],
                                         column_types=info[tbl]['col_types'])
    return res


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
    (calc1, calc2, _) = calculate(year_n, start_year,
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
