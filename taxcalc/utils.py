import numpy as np
import pandas as pd
from pandas import DataFrame

STATS_COLUMNS = ['c00100', 'c04100', 'c04470', 'c04800', 'c05200',
                 'c09600', 'c07100', 'c09200', '_refund', '_ospctax',
                 'c10300', 'e00100', 's006']

TABLE_COLUMNS = ['c00100', 'c04100', 'c04470', 'c04800', 'c05200',
                 'c09600', 'c07100', 'c09200', '_refund', '_ospctax',
                 'c10300']



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


def expand_1D(x, inflate, inflation_rate, num_years):
    """
    Expand the given data to account for the given number of budget years.
    If necessary, pad out additional years by increasing the last given
    year at the provided inflation rate.
    """
    if isinstance(x, np.ndarray):
        if len(x) >= num_years:
            return x
        else:
            ans = np.zeros(num_years)
            ans[:len(x)] = x
            if inflate:
                extra = [float(x[-1])*pow(1. + inflation_rate, i) for i in
                         range(1, num_years - len(x) + 1)]
            else:
                extra = [float(x[-1]) for i in
                         range(1, num_years - len(x) + 1)]

            ans[len(x):] = extra
            return ans.astype(x.dtype, casting='unsafe')

    return expand_1D(np.array([x]), inflate, inflation_rate, num_years)


def expand_2D(x, inflate, inflation_rate, num_years):
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
                extra = [x[-1, :]*pow(1. + inflation_rate, i) for i in
                     range(1, num_years - len(x) + 1)]
            else:
                extra = [x[-1, :] for i in
                     range(1, num_years - len(x) + 1)]

            ans[len(x):, :] = extra
            return ans.astype(x.dtype, casting='unsafe')

    return expand_2D(np.array([x]), inflate, inflation_rate, num_years)


def expand_array(x, inflate, inflation_rate=0.02, num_years=10):
    """
    Dispatch to either expand_1D or expand2D depending on the dimension of x

    Parameters:
    -----------
    x : value to expand

    inflate: Boolean
    As we expand, inflate values if this is True, otherwise, just copy

    inflation_rate: float
    Yearly inflation reate

    num_years: int
    Number of budget years to expand

    Returns:
    --------
    expanded numpy array
    """
    try:
        if len(x.shape) == 1:
            return expand_1D(x, inflate, inflation_rate, num_years)
        elif len(x.shape) == 2:
            return expand_2D(x, inflate, inflation_rate, num_years)
        else:
            raise ValueError("Need a 1D or 2D array")
    except AttributeError as ae:
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
    return float(weighted_count_gt_zero(agg, col_name)) / float(weighted_count(agg))


def weighted_perc_dec(agg, col_name):
    return float(weighted_count_lt_zero(agg, col_name)) / float(weighted_count(agg))


def weighted_share_of_total(agg, col_name, total):
    return float(weighted_sum(agg, col_name)) / float(total)


def groupby_weighted_decile(df):
    """

    Group by each 10% of AGI, weighed by s006

    """

    #First, sort by AGI
    df.sort('c00100', inplace=True)
    #Next, do a cumulative sum by the weights
    df['cumsum_weights'] = np.cumsum(df['s006'].values)
    #Max value of cum sum of weights
    max_ = df['cumsum_weights'].values[-1]
    #Create 10 bins and labels based on this cumulative weight
    bins = [0] + list(np.arange(1,11)*(max_/10.0))
    labels = [range(1,11)]
    # Groupby weighted deciles
    decile_bins = list(range(1, 11))
    df['wdecs'] = pd.cut(df['cumsum_weights'], bins, labels)
    return df.groupby('wdecs')


def groupby_income_bins(df):
    """

    Group by income bins of AGI

    """

    income_bins = ["negative", "lt10", "lt20", "lt30", "lt40", "lt50", "lt75",
                   "lt100", "lt200", "200plut"]

    # Groupby c00100 bins
    bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999, 200000, 1e14]
    df['bins'] = pd.cut(df['c00100'], bins)
    return df.groupby('bins')


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


def results(c):
    outputs = [getattr(c, col) for col in STATS_COLUMNS]
    return DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)


def create_distribution_table(calc, groupby):
    res = results(calc)
    if groupby == "weighted_deciles":
        gp = groupby_weighted_decile(res)
    elif groupby == "agi_bins":
        gp = groupby_income_bins(res)
    else:
        err = "groupby must be either 'weighted_deciles' or 'agi_bins'"
        raise ValueError(err)

    return gp[TABLE_COLUMNS].mean()

def create_difference_table(calc1, calc2, groupby):
    res1 = results(calc1)
    res2 = results(calc2)
    if groupby == "weighted_deciles":
        gp = groupby_weighted_decile(res2)
    elif groupby == "agi_bins":
        gp = groupby_income_bins(res2)
    else:
        err = "groupby must be either 'weighted_deciles' or 'agi_bins'"
        raise ValueError(err)


    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    res2['tax_diff'] = res2['_ospctax'] - res1['_ospctax']

    diffs = means_and_comparisons(res2, 'tax_diff', gp,
                                 (res2['tax_diff']*res2['s006']).sum())
    return diffs
