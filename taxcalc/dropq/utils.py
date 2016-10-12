import json
import numpy as np
import pandas as pd
from taxcalc.utils import *

EPSILON = 1e-3

def cast_to_double(df):
    """
    Take all of the columns for E-codes and P-codes and make the columns of type
    'double' instead of 'int'. This is helpful for jitting purposes so that we
    don't have to jit once for type int and once for type double
    """
    cols = ['e00100', 'e00200', 'e00300', 'e00400', 'e00600', 'e00650', 'e00700', 'e00800',
     'e00900', 'e01000', 'e01100', 'e01200', 'e01400', 'e01500', 'e01700', 'e02000',
     'e02100', 'e02300', 'e02400', 'e02500', 'e03150', 'e03210', 'e03220', 'e03230',
     'e03240', 'e03260', 'e03270', 'e03290', 'e03300', 'e03400', 'e03500', 'e04250',
     'e04600', 'e04800', 'e05100', 'e05200', 'e05800', 'e06000', 'e06200', 'e06300',
     'e06500', 'e07150', 'e07180', 'e07200', 'e07220', 'e07230', 'e07240', 'e07260',
     'e07300', 'e07400', 'e07600', 'e08800', 'e09400', 'e09600', 'e09700', 'e09800',
     'e09900', 'e10300', 'e10605', 'e10700', 'e10900', 'e10950', 'e10960', 'e11070',
     'e11100', 'e11200', 'e11300', 'e11400', 'e11550', 'e11570', 'e11580', 'e11581',
     'e11582', 'e11583', 'e11900', 'e12000', 'e12200', 'e15100', 'e15210', 'e15250',
     'e15360', 'e17500', 'e18400', 'e18500', 'e18600', 'e19200', 'e19550', 'e19700',
     'e19800', 'e20100', 'e20400', 'e20500', 'e20550', 'e20600', 'e20800', 'e21040',
     'e22320', 'e22370', 'e24515', 'e24516', 'e24518', 'e24535', 'e24560', 'e24570',
     'e24598', 'e24615', 'e25820', 'e25850', 'e25860', 'e25920', 'e25940', 'e25960',
     'e25980', 'e26100', 'e26110', 'e26160', 'e26170', 'e26180', 'e26190', 'e26270',
     'e26390', 'e26400', 'e27200', 'e30400', 'e30500', 'e32800', 'e33000', 'e53240',
     'e53280', 'e53300', 'e53317', 'e53410', 'e53458', 'e58950', 'e58990', 'e59560',
     'e59680', 'e59700', 'e59720', 'e60000', 'e62100', 'e62720', 'e62730', 'e62740',
     'e62900', 'e68000', 'e82200', 'e87530', 'e87550', 'e87870', 'e87875', 'e87880',
     'p04470', 'p08000', 'p22250', 'p23250', 'p25350', 'p25380', 'p25470', 'p25700',
     'p27895', 'p60100', 'p61850', 'p65300', 'p65400']

    df[cols] = df[cols] * 1.0

def format_print(x, _type, num_decimals):
    float_types = [float, np.dtype('f8')]
    frmat_str = "0:.{num}f".format(num=num_decimals)
    frmat_str = "{" + frmat_str + "}"
    try:
        if _type in float_types or _type == None:
            return frmat_str.format(x)
        elif _type == int:
            return str(int(x))
        elif _type == str:
            return str(x)
        else:
            return NotImplementedError()
    except ValueError:
        #try making it a string - good luck!
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
            row_out[str(col_name)] = format_print(df.loc[idx, col], _type, num_decimals)
            #row_out[str(col_name)] = df.loc[idx, col]
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

def create_dropq_difference_table(df1, df2, groupby, res_col, diff_col, suffix, wsum):
    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(df2)
    elif groupby == "small_income_bins":
        df = add_income_bins(df2, compare_with="soi")
    elif groupby == "large_income_bins":
        df = add_income_bins(df2, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        df = add_income_bins(df2, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or 'small_income_bins'"
               "or 'large_income_bins' or 'webapp_income_bins'")
        raise ValueError(err)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2[res_col + suffix] = df2[diff_col + suffix] - df1[diff_col]

    diffs = means_and_comparisons(df2, res_col + suffix, df.groupby('bins', as_index=False),
                                  wsum + EPSILON)


    sum_row = get_sums(diffs)[diffs.columns.tolist()]
    diffs = diffs.append(sum_row)

    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ["{0:.2f}%".format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)

    srs_cut = ["{0:.2f}%".format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)

    srs_change = ["{0:.2f}%".format(val * 100) for val in diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)

    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [x for x in diffs.columns.tolist() if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'

    return diffs

def create_dropq_distribution_table(calc, groupby, result_type, suffix):
    res = calc

    res['c04470' + suffix ] = res['c04470' + suffix].where(((res['c00100' + suffix] > 0) &
                                        (res['c04470' + suffix] > res['_standard' + suffix])), 0)

    res['num_returns_ItemDed' + suffix] = res['s006' + suffix].where(((res['c00100' + suffix] > 0) &
                                                   (res['c04470' + suffix] > 0)), 0)

    res['num_returns_StandardDed' + suffix] = res['s006' + suffix].where(((res['c00100' + suffix] > 0) &
                                                       (res['_standard' + suffix] > 0)), 0)

    res['num_returns_AMT' + suffix] = res['s006' + suffix].where(res['c09600' + suffix] > 0, 0)

    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(res)
    elif groupby == "small_income_bins":
        df = add_income_bins(res, compare_with="soi")
    elif groupby == "large_income_bins":
        df = add_income_bins(res, compare_with="tpc")
    elif groupby == "webapp_income_bins":
        df = add_income_bins(res, compare_with="webapp")
    else:
        err = ("groupby must be either 'weighted_deciles' or 'small_income_bins'"
               "or 'large_income_bins' or 'webapp_income_bins'")
        raise ValueError(err)

    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == "weighted_sum":
        df = weighted(df, [col + suffix for col in STATS_COLUMNS])
        gp_mean = df.groupby('bins', as_index=False)[[col + suffix for col in TABLE_COLUMNS]].sum()
        gp_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(df)[[col + suffix for col in TABLE_COLUMNS]]
    elif result_type == "weighted_avg":
        gp_mean =weighted_avg_allcols(df, [col + suffix for col in TABLE_COLUMNS])
        sum_row = get_sums(df, na=True)[[col + suffix for col in TABLE_COLUMNS]]

    return gp_mean.append(sum_row)


