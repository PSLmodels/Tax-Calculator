import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import defaultdict

STATS_COLUMNS = ['c00100', '_standard', 'c04470', 'c04600', 'c04800', 'c05200',
                 'c09600', 'c05800', 'c09200', '_refund', 'c07100', '_ospctax',
                 's006']

TABLE_COLUMNS = ['c00100', 'num_returns_StandardDed', '_standard',
                 'num_returns_ItemDed', 'c04470', 'c04600', 'c04800', 'c05200',
                 'num_returns_AMT', 'c09600', 'c05800', 'c09200', '_refund',
                 'c07100', '_ospctax', 's006']


def extract_array(f):
    """
    A sanity check decorator. When combined with numba.vectorize
    or guvectorize, it provides the same capability as dataframe_vectorize
    or dataframe_guvectorize
    """
    def wrapper(*args, **kwargs):
        arrays = [arg.values for arg in args]
        return f(*arrays)
    return wrapper


def expand_1D(x, inflate, inflation_rates, num_years):
    """
    Expand the given data to account for the given number of budget years.
    If necessary, pad out additional years by increasing the last given
    year at the provided inflation rate.
    """

    assert len(inflation_rates) == num_years

    if isinstance(x, np.ndarray):
        if len(x) >= num_years:
            return x
        else:
            ans = np.zeros(num_years, dtype='f8')
            ans[:len(x)] = x
            if inflate:
                extra = []
                cur = x[-1]
                for i in range(1, num_years - len(x) + 1):
                    inf_idx = i + len(x) - 1
                    cur *= (1. + inflation_rates[inf_idx])
                    extra.append(cur)
            else:
                extra = [float(x[-1]) for i in
                         range(1, num_years - len(x) + 1)]

            ans[len(x):] = extra
            return ans.astype(x.dtype, casting='unsafe')

    return expand_1D(np.array([x]), inflate, inflation_rates, num_years)


def expand_2D(x, inflate, inflation_rates, num_years):
    """
    Expand the given data to account for the given number of budget years.
    For 2D arrays, we expand out the number of rows until we have num_years
    number of rows. For each expanded row, we inflate by the given inflation
    rate.
    """

    if isinstance(x, np.ndarray):
        if x.shape[0] >= num_years:
            return x
        else:
            ans = np.zeros((num_years, x.shape[1]))
            ans[:len(x), :] = x
            if inflate:
                extra = []
                cur = x[-1]
                for i in range(1, num_years - len(x) + 1):
                    inf_idx = i + len(x) - 1
                    cur = np.array(cur*(1. + inflation_rates[inf_idx]))
                    extra.append(cur)
            else:
                extra = [x[-1, :] for i in
                         range(1, num_years - len(x) + 1)]

            ans[len(x):, :] = extra
            return ans.astype(x.dtype, casting='unsafe')

    return expand_2D(np.array([x]), inflate, inflation_rates, num_years)


def expand_array(x, inflate, inflation_rates, num_years):
    """
    Dispatch to either expand_1D or expand2D depending on the dimension of x

    Parameters
    ----------
    x : value to expand

    inflate: Boolean
        As we expand, inflate values if this is True, otherwise, just copy

    inflation_rate: float
        Yearly inflation reate

    num_years: int
        Number of budget years to expand

    Returns
    -------
    expanded numpy array
    """
    try:
        if len(x.shape) == 1:
            return expand_1D(x, inflate, inflation_rates, num_years)
        elif len(x.shape) == 2:
            return expand_2D(x, inflate, inflation_rates, num_years)
        else:
            raise ValueError("Need a 1D or 2D array")
    except AttributeError:
        raise ValueError("Must pass a numpy array")


def count_gt_zero(agg):
    return sum([1 for a in agg if a > 0])


def count_lt_zero(agg):
    return sum([1 for a in agg if a < 0])


def weighted_count_lt_zero(agg, col_name):
    return agg[agg[col_name] < 0]['s006'].sum()


def weighted_count_gt_zero(agg, col_name):
    return agg[agg[col_name] > 0]['s006'].sum()


def weighted_count(agg):
    return agg['s006'].sum()


def weighted_mean(agg, col_name):
    return float((agg[col_name]*agg['s006']).sum()) / float(agg['s006'].sum())


def weighted_sum(agg, col_name):
    return (agg[col_name]*agg['s006']).sum()


def weighted_perc_inc(agg, col_name):
    return (float(weighted_count_gt_zero(agg, col_name)) /
            float(weighted_count(agg)))


def weighted_perc_dec(agg, col_name):
    return (float(weighted_count_lt_zero(agg, col_name)) /
            float(weighted_count(agg)))


def weighted_share_of_total(agg, col_name, total):
    return float(weighted_sum(agg, col_name)) / float(total)


def add_weighted_decile_bins(df):
    """

    Add a column of income bins based on each 10% of AGI, weighted by s006.
    This will server as a "grouper" later on.

    """

    # First, sort by AGI
    df.sort('c00100', inplace=True)
    # Next, do a cumulative sum by the weights
    df['cumsum_weights'] = np.cumsum(df['s006'].values)
    # Max value of cum sum of weights
    max_ = df['cumsum_weights'].values[-1]
    # Create 10 bins and labels based on this cumulative weight
    bins = [0] + list(np.arange(1, 11)*(max_/10.0))
    labels = [range(1, 11)]
    #  Groupby weighted deciles
    df['bins'] = pd.cut(df['cumsum_weights'], bins, labels)
    return df


def add_income_bins(df, compare_with="soi", bins=None, right=True):
    """

    Add a column of income bins of AGI using pandas 'cut'. This will
    serve as a "grouper" later on.

    df: DataFrame to group

    compare_with: string, optional
            Some names to specify certain pre-defined bins

    bins: iterable of scalars, optional
            AGI income breakpoints. Follows pandas convention. The
            breakpoint is inclusive if right=True. This argument
            overrides any choice of compare_with

    right : bool, optional
            Indicates whether the bins include the rightmost edge or not.
            If right == True (the default), then the bins [1,2,3,4]
            indicate (1,2], (2,3], (3,4].

    """
    if not bins:
        if compare_with == "tpc":
            bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                    200000, 1e14]

        elif compare_with == "soi":
            bins = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
                    49999, 74999, 99999, 199999, 499999, 999999, 1499999,
                    1999999, 4999999, 9999999, 1e14]

        else:
            msg = "Unknown compare_with arg {0}".format(compare_with)
            raise ValueError(msg)

    # Groupby c00100 bins
    df['bins'] = pd.cut(df['c00100'], bins, right=right)
    return df


def means_and_comparisons(df, col_name, gp, weighted_total):
    """

    Using grouped values, perform aggregate operations
    to populate
    df: DataFrame for full results of calculation
    col_name: the column name to calculate against
    gp: grouped DataFrame
    """

    # Who has a tax cut, and who has a tax increase
    diffs = gp.apply(weighted_count_lt_zero, col_name)
    diffs = DataFrame(data=diffs, columns=['tax_cut'])
    diffs['tax_inc'] = gp.apply(weighted_count_gt_zero, col_name)
    diffs['count'] = gp.apply(weighted_count)
    diffs['mean'] = gp.apply(weighted_mean, col_name)
    diffs['tot_change'] = gp.apply(weighted_sum, col_name)
    diffs['perc_inc'] = gp.apply(weighted_perc_inc, col_name)
    diffs['perc_cut'] = gp.apply(weighted_perc_dec, col_name)
    diffs['share_of_change'] = gp.apply(weighted_share_of_total,
                                        col_name, weighted_total)

    return diffs


def weighted(df, X):
    agg = df
    for colname in X:
        if colname != 's006':
            agg[colname] = df[colname]*df['s006']
    return agg


def get_sums(df):
    """
    Gets the unweighted sum of each column, saving the col name and the corresponding sum

    Returns
    -------
    pandas.Series
    """
    sums = defaultdict(lambda: 0)

    for col in df.columns.tolist():
        if col != 'bins':
            sums[col] = (df[col]).sum()

    return pd.Series(sums, name='sums')


def results(c):
    outputs = [getattr(c, col) for col in STATS_COLUMNS]
    return DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)


def weighted_avg_allcols(df, cols):
    diff = DataFrame(df.groupby('bins').apply(weighted_mean, "c00100"),
                     columns=['c00100'])

    for col in cols:
        if (col == "s006" or col == 'num_returns_StandardDed' or
           col == 'num_returns_ItemDed' or col == 'num_returns_AMT'):
            diff[col] = df.groupby('bins')[col].sum()
        elif col != "c00100":
            diff[col] = df.groupby('bins').apply(weighted_mean, col)

    return diff


def create_distribution_table(calc, groupby, result_type):
    res = results(calc)

    res['c04470'] = res['c04470'].where(((res['c00100'] > 0) &
                                        (res['c04470'] > res['_standard'])), 0)

    res['num_returns_ItemDed'] = res['s006'].where(((res['c00100'] > 0) &
                                                   (res['c04470'] > 0)), 0)

    res['num_returns_StandardDed'] = res['s006'].where(((res['c00100'] > 0) &
                                                       (res['_standard'] > 0)), 0)

    res['num_returns_AMT'] = res['s006'].where(res['c09600'] > 0, 0)

    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(res)
    elif groupby == "small_agi_bins":
        df = add_income_bins(res, compare_with="soi")
    elif groupby == "large_agi_bins":
        df = add_income_bins(res, compare_with="tpc")
    else:
        err = ("groupby must be either 'weighted_deciles' or 'small_agi_bins'"
               "or 'large_agi_bins'")
        raise ValueError(err)

    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == "weighted_sum":
        df = weighted(df, STATS_COLUMNS)
        gp_mean = df.groupby('bins')[TABLE_COLUMNS].sum()
        sum_row = get_sums(df)[TABLE_COLUMNS]
        return gp_mean.append(sum_row)
    elif result_type == "weighted_avg":
        return weighted_avg_allcols(df, TABLE_COLUMNS)


def create_difference_table(calc1, calc2, groupby):
    res1 = results(calc1)
    res2 = results(calc2)
    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(res2)
    elif groupby == "small_agi_bins":
        df = add_income_bins(res2, compare_with="soi")
    elif groupby == "large_agi_bins":
        df = add_income_bins(res2, compare_with="tpc")
    else:
        err = ("groupby must be either 'weighted_deciles' or 'small_agi_bins'"
               "or 'large_agi_bins'")
        raise ValueError(err)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    res2['tax_diff'] = res2['_ospctax'] - res1['_ospctax']

    diffs = means_and_comparisons(res2, 'tax_diff', df.groupby('bins'),
                                  (res2['tax_diff']*res2['s006']).sum())

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
