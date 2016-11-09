import json
import numpy as np
import pandas as pd
from taxcalc.utils import *

EPSILON = 1e-3


def format_print(x, _type, num_decimals):
    float_types = [float, np.dtype('f8')]
    frmat_str = "0:.{num}f".format(num=num_decimals)
    frmat_str = "{" + frmat_str + "}"
    try:
        if _type in float_types or _type is None:
            return frmat_str.format(x)
        elif _type == int:
            return str(int(x))
        elif _type == str:
            return str(x)
        else:
            raise NotImplementedError()
    except ValueError:
        # try making it a string - good luck!
        return str(x)


def create_json_blob(df, row_names=None, column_names=None,
                     column_types=None, num_decimals=2, **kwargs):
    out = {}
    if row_names is None:
        row_names = list(df.index)

    if column_names is None:
        column_names = list(df.columns)

    if column_types is None:
        column_types = [df[col].dtype for col in df.columns]

    assert len(df.index) == len(row_names)
    assert len(df.columns) == len(column_names)
    assert len(df.columns) == len(column_types)

    for idx, row_name in zip(df.index, row_names):
        row_out = {}
        for col, col_name, _type in zip(df.columns, column_names,
                                        column_types):
            row_out[str(col_name)] = format_print(df.loc[idx, col], _type,
                                                  num_decimals)
        out[str(row_name)] = row_out

    return json.dumps(out, **kwargs)


def create_json_table(df, row_names=None, column_types=None, num_decimals=2):
    out = {}
    if row_names is None:
        row_names = [str(x) for x in list(df.index)]

    if column_types is None:
        column_types = [df[col].dtype for col in df.columns]

    assert len(df.index) == len(row_names)

    for idx, row_name in zip(df.index, row_names):
        row_out = out.get(row_name, [])
        for col, _type in zip(df.columns, column_types):
            row_out.append(format_print(df.loc[idx, col], _type, num_decimals))
        out[row_name] = row_out

    return out


def create_dropq_difference_table(df1, df2, groupby, res_col, diff_col,
                                  suffix, wsum):
    if groupby == "weighted_deciles":
        df = add_weighted_income_bins(df2, num_bins=10)
    elif groupby == "small_income_bins":
        df = add_income_bins(df2, compare_with="soi")
    elif groupby == "large_income_bins":
        df = add_income_bins(df2, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        df = add_income_bins(df2, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(err)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2[res_col + suffix] = df2[diff_col + suffix] - df1[diff_col]

    diffs = means_and_comparisons(df2, res_col + suffix,
                                  df.groupby('bins', as_index=False),
                                  wsum + EPSILON)

    sum_row = get_sums(diffs)[diffs.columns.tolist()]
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
    non_sum_cols = [x for x in diffs.columns.tolist()
                    if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'

    return diffs


def create_dropq_distribution_table(calc, groupby, result_type, suffix):
    res = calc
    c04470suf = 'c04470' + suffix
    c00100suf = 'c00100' + suffix
    c09600suf = 'c09600' + suffix
    standardsuf = '_standard' + suffix
    s006suf = 's006' + suffix
    returnsItemDedsuf = 'num_returns_ItemDed' + suffix
    returnsStandDedsuf = 'num_returns_StandardDed' + suffix
    returnsAMTsuf = 'num_returns_AMT' + suffix
    res[c04470suf] = res[c04470suf].where(((res[c00100suf] > 0) &
                                          (res[c04470suf] > res[standardsuf])),
                                          0)

    res[returnsItemDedsuf] = res[s006suf].where(((res[c00100suf] > 0) &
                                                (res[c04470suf] > 0)), 0)

    res[returnsStandDedsuf] = res[s006suf].where(((res[c00100suf] > 0) &
                                                  (res[standardsuf] > 0)), 0)

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
