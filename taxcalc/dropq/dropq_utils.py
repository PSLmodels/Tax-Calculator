"""
Utility functions used by functions in dropq.py file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 dropq_utils.py
# pylint --disable=locally-disabled dropq_utils.py

import hashlib
import numpy as np
import pandas as pd
from taxcalc.utils import (add_income_bins, add_weighted_income_bins,
                           means_and_comparisons, get_sums,
                           weighted, weighted_avg_allcols,
                           STATS_COLUMNS, TABLE_COLUMNS, WEBAPP_INCOME_BINS)
# pylint: disable=invalid-name
# TODO: remove above line


EPSILON = 1e-3


def check_user_mods(user_mods):
    """
    Ensure specified user_mods is properly structured.
    """
    if not isinstance(user_mods, dict):
        raise ValueError('user_mods is not a dictionary')
    actual_keys = set(list(user_mods.keys()))
    expected_keys = set(['policy', 'consumption', 'behavior',
                         'growdiff_baseline', 'growdiff_response',
                         'gdp_elasticity'])
    missing_keys = expected_keys - actual_keys
    if len(missing_keys) > 0:
        raise ValueError('user_mods has missing keys: {}'.format(missing_keys))
    extra_keys = actual_keys - expected_keys
    if len(extra_keys) > 0:
        raise ValueError('user_mods has extra keys: {}'.format(extra_keys))


def random_seed_from_subdict(subdict):
    """
    Compute random seed from one user_mods subdictionary.
    """
    assert isinstance(subdict, dict)
    all_vals = []
    for year in sorted(subdict.keys()):
        all_vals.append(str(year))
        params = subdict[year]
        for param in sorted(params.keys()):
            try:
                tple = tuple(params[param])
            except TypeError:
                # params[param] is not an iterable value; make it so
                tple = tuple((params[param],))
            all_vals.append(str((param, tple)))
    txt = u''.join(all_vals).encode('utf-8')
    hsh = hashlib.sha512(txt)
    seed = int(hsh.hexdigest(), 16)
    return seed % np.iinfo(np.uint32).max  # pylint: disable=no-member


def chooser(agg):
    """
    This is a transformation function that should be called on each group.
    It is assumed that the chunk 'agg' is a chunk of the 'mask' column.
    This chooser selects three of those mask indices with the output for
    those three indices being zero and the output for all the other indices
    being one.
    """
    indices = np.where(agg)
    three = 3
    if len(indices[0]) >= three:
        choices = np.random.choice(indices[0],  # pylint: disable=no-member
                                   size=three, replace=False)
    else:
        msg = ('Not enough differences in income tax when adding '
               'one dollar for chunk with name: {}')
        raise ValueError(msg.format(agg.name))
    ans = [1] * len(agg)
    for idx in choices:
        ans[idx] = 0
    return ans


def results(calc):
    """
    Return DataFrame containing results for STATS_COLUMNS Records variables.
    """
    outputs = []
    for col in STATS_COLUMNS:
        outputs.append(getattr(calc.records, col))
    return pd.DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)


def drop_records(df1, df2, mask):
    """
    Modify DataFrame df1 and DataFrame df2 by adding statistical 'fuzz'.
    df1 contains results for the standard plan X and X'
    df2 contains results for the user-specified plan (Plan Y)
    mask is the boolean mask where X and X' match
    This function groups both DataFrames based on the web application's
    income groupings (both weighted decile and income bins), and then
    pseudo-randomly picks three records to 'drop' within each bin.
    We keep track of the three dropped records in both group-by
    strategies and then use these 'flag' columns to modify all
    columns of interest, creating new '*_dec' columns for later
    statistics based on weighted deciles and '*_bin' columns
    for statitistics based on grouping by income bins.
    in each bin in two group-by actions. Lastly we calculate
    individual income tax differences, payroll tax differences, and
    combined tax differences between the baseline and reform
    for the two groupings.
    """
    # perform all statistics on (Y + X') - X

    # Group first
    df2['mask'] = mask
    df1['mask'] = mask

    df2 = add_weighted_income_bins(df2)
    df1 = add_weighted_income_bins(df1)
    gp2_dec = df2.groupby('bins')

    income_bins = WEBAPP_INCOME_BINS

    df2 = add_income_bins(df2, bins=income_bins)
    df1 = add_income_bins(df1, bins=income_bins)
    gp2_bin = df2.groupby('bins')

    # Transform to get the 'flag' column (3 choices to drop in each bin)
    df2['flag_dec'] = gp2_dec['mask'].transform(chooser)
    df2['flag_bin'] = gp2_bin['mask'].transform(chooser)

    # first calculate all of X'
    columns_to_make_noisy = set(TABLE_COLUMNS) | set(STATS_COLUMNS)
    # these don't exist yet
    columns_to_make_noisy.remove('num_returns_ItemDed')
    columns_to_make_noisy.remove('num_returns_StandardDed')
    columns_to_make_noisy.remove('num_returns_AMT')
    for col in columns_to_make_noisy:
        df2[col + '_dec'] = (df2[col] * df2['flag_dec'] -
                             df1[col] * df2['flag_dec'] + df1[col])
        df2[col + '_bin'] = (df2[col] * df2['flag_bin'] -
                             df1[col] * df2['flag_bin'] + df1[col])

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2['tax_diff_dec'] = df2['iitax_dec'] - df1['iitax']
    df2['tax_diff_bin'] = df2['iitax_bin'] - df1['iitax']
    df2['payrolltax_diff_dec'] = df2['payrolltax_dec'] - df1['payrolltax']
    df2['payrolltax_diff_bin'] = df2['payrolltax_bin'] - df1['payrolltax']
    df2['combined_diff_dec'] = df2['combined_dec'] - df1['combined']
    df2['combined_diff_bin'] = df2['combined_bin'] - df1['combined']

    return df1, df2


def format_print(x, _type, num_decimals):
    """
    Formatted conversion of number into a string.
    """
    float_types = [float, np.dtype('f8')]
    int_types = [int, np.dtype('i8')]
    frmat_str = "0:.{num}f".format(num=num_decimals)
    frmat_str = "{" + frmat_str + "}"
    try:
        if _type in float_types or _type is None:
            return frmat_str.format(x)
        elif _type in int_types:
            return str(int(x))
        elif _type == str:
            return str(x)
        else:
            raise NotImplementedError()
    except ValueError:
        # try making it a string - good luck!
        return str(x)


def create_json_table(df, row_names=None, column_types=None, num_decimals=2):
    """
    Create dictionary with JSON-like contents.
    """
    out = {}
    if row_names is None:
        row_names = [str(x) for x in list(df.index)]
    else:
        assert len(row_names) == len(df.index)
    if column_types is None:
        column_types = [df[col].dtype for col in df.columns]
    else:
        assert len(column_types) == len(df.columns)
    for idx, row_name in zip(df.index, row_names):
        row_out = out.get(row_name, [])
        for col, _type in zip(df.columns, column_types):
            row_out.append(format_print(df.loc[idx, col], _type, num_decimals))
        out[row_name] = row_out
    return out


def create_dropq_difference_table(df1, df2, groupby,
                                  res_col, diff_col,
                                  suffix, wsum):
    """
    Create difference table.
    """
    # pylint: disable=too-many-arguments,too-many-locals
    if groupby == "weighted_deciles":
        gdf = add_weighted_income_bins(df2, num_bins=10)
    elif groupby == "small_income_bins":
        gdf = add_income_bins(df2, compare_with="soi")
    elif groupby == "large_income_bins":
        gdf = add_income_bins(df2, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        gdf = add_income_bins(df2, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(err)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2[res_col + suffix] = df2[diff_col + suffix] - df1[diff_col]

    diffs = means_and_comparisons(res_col + suffix,
                                  gdf.groupby('bins', as_index=False),
                                  wsum + EPSILON)
    sum_row = get_sums(diffs)[diffs.columns]
    diffs = diffs.append(sum_row)

    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ["{0:.2f}%".format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)

    srs_cut = ["{0:.2f}%".format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)

    srs_change = ["{0:.2f}%".format(val * 100) for val in
                  diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)

    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [x for x in diffs.columns if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'

    return diffs


def create_dropq_distribution_table(resdf, groupby, result_type, suffix):
    """
    Create distribution table.
    """
    # pylint: disable=too-many-locals
    res = resdf
    c04470suf = 'c04470' + suffix
    c00100suf = 'c00100' + suffix
    c09600suf = 'c09600' + suffix
    standardsuf = 'standard' + suffix
    s006suf = 's006' + suffix
    returnsItemDedsuf = 'num_returns_ItemDed' + suffix
    returnsStandDedsuf = 'num_returns_StandardDed' + suffix
    returnsAMTsuf = 'num_returns_AMT' + suffix
    res[c04470suf] = res[c04470suf].where(((res[c00100suf] > 0) &
                                           (res[c04470suf] > res[standardsuf])),
                                          0)
    res[returnsItemDedsuf] = res[s006suf].where(((res[c00100suf] > 0) &
                                                 (res[c04470suf] > 0)),
                                                0)
    res[returnsStandDedsuf] = res[s006suf].where(((res[c00100suf] > 0) &
                                                  (res[standardsuf] > 0)),
                                                 0)
    res[returnsAMTsuf] = res[s006suf].where(res[c09600suf] > 0, 0)

    if groupby == "weighted_deciles":
        df = add_weighted_income_bins(res, num_bins=10)
    elif groupby == "small_income_bins":
        df = add_income_bins(res, compare_with="soi")
    elif groupby == "large_income_bins":
        df = add_income_bins(res, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        df = add_income_bins(res, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(err)

    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == "weighted_sum":
        df = weighted(df, [col + suffix for col in STATS_COLUMNS])
        gby_bins = df.groupby('bins', as_index=False)
        gp_mean = gby_bins[[col + suffix for col in TABLE_COLUMNS]].sum()
        gp_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(df)[[col + suffix for col in TABLE_COLUMNS]]
    elif result_type == "weighted_avg":
        gp_mean = weighted_avg_allcols(df,
                                       [col + suffix for col in TABLE_COLUMNS])
        all_sums = get_sums(df, not_available=True)
        sum_row = all_sums[[col + suffix for col in TABLE_COLUMNS]]
    else:
        err = ("result_type must be either 'weighted_sum' or "
               "'weighted_avg'")
        raise ValueError(err)

    return gp_mean.append(sum_row)
