import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import defaultdict

STATS_COLUMNS = ['_expanded_income', 'c00100', '_standard', 'c04470', 'c04600',
                 'c04800', 'c05200', 'c62100', 'c09600', 'c05800', 'c09200',
                 '_refund', 'c07100', '_ospctax', '_fica', '_combined', 's006']

# each entry in this array corresponds to the same entry in the array
# TABLE_LABELS below. this allows us to use TABLE_LABELS to map a
# label to the correct column in our distribution table

TABLE_COLUMNS = ['s006', 'c00100', 'num_returns_StandardDed', '_standard',
                 'num_returns_ItemDed', 'c04470', 'c04600', 'c04800', 'c05200',
                 'c62100', 'num_returns_AMT', 'c09600', 'c05800', 'c07100',
                 'c09200', '_refund', '_ospctax', '_fica', '_combined']

TABLE_LABELS = ['Returns', 'AGI', 'Standard Deduction Filers',
                'Standard Deduction', 'Itemizers',
                'Itemized Deduction', 'Personal Exemption',
                'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers', 'AMT',
                'Tax before Credits', 'Non-refundable Credits',
                'Tax before Refundable Credits', 'Refundable Credits',
                'Individual Income Tax Liabilities', 'Payroll Tax Liablities',
                'Combined Payroll and Individual Income Tax Liabilities']

# used in our difference table to label the columns
DIFF_TABLE_LABELS = ["Tax Units with Tax Cut", "Tax Units with Tax Increase",
                     "Count", "Average Tax Change", "Total Tax Difference",
                     "Percent with Tax Increase", "Percent with Tax Decrease",
                     "Share of Overall Change"]


LARGE_INCOME_BINS = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                     200000, 1e14]

SMALL_INCOME_BINS = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
                     49999, 74999, 99999, 199999, 499999, 999999, 1499999,
                     1999999, 4999999, 9999999, 1e14]

WEBAPP_INCOME_BINS = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                      199999, 499999, 1000000, 1e14]

EPSILON = 0.000000001


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


def count_gt_zero(agg):
    return sum([1 for a in agg if a > 0])


def count_lt_zero(agg):
    return sum([1 for a in agg if a < 0])


def weighted_count_lt_zero(agg, col_name, tolerance=-0.001):
    return agg[agg[col_name] < tolerance]['s006'].sum()


def weighted_count_gt_zero(agg, col_name, tolerance=0.001):
    return agg[agg[col_name] > tolerance]['s006'].sum()


def weighted_count(agg):
    return agg['s006'].sum()


def weighted_mean(agg, col_name):
    return (float((agg[col_name] * agg['s006']).sum()) /
            float(agg['s006'].sum()))


def weighted_sum(agg, col_name):
    return (agg[col_name] * agg['s006']).sum()


def weighted_perc_inc(agg, col_name):
    return (float(weighted_count_gt_zero(agg, col_name)) /
            float(weighted_count(agg)))


def weighted_perc_dec(agg, col_name):
    return (float(weighted_count_lt_zero(agg, col_name)) /
            float(weighted_count(agg)))


def weighted_share_of_total(agg, col_name, total):
    return float(weighted_sum(agg, col_name)) / (float(total) + EPSILON)


def add_weighted_decile_bins(df, income_measure='_expanded_income'):
    """

    Add a column of income bins based on each 10% of the income_measure,
    weighted by s006.

    The default income_measure is `expanded_income`, but `c00100` also works.

    This function will server as a "grouper" later on.

    """

    # First, sort by income_measure
    df.sort(income_measure, inplace=True)
    # Next, do a cumulative sum by the weights
    df['cumsum_weights'] = np.cumsum(df['s006'].values)
    # Max value of cum sum of weights
    max_ = df['cumsum_weights'].values[-1]
    # Create 10 bins and labels based on this cumulative weight
    bins = [0] + list(np.arange(1, 11) * (max_ / 10.0))
    labels = [range(1, 11)]
    #  Groupby weighted deciles
    df['bins'] = pd.cut(df['cumsum_weights'], bins, labels)
    return df


def add_income_bins(df, compare_with="soi", bins=None, right=True,
                    income_measure='_expanded_income'):
    """

    Add a column of income bins of income_measure using pandas 'cut'.
    This will serve as a "grouper" later on.


    Parameters
    ----------
    df: DataFrame object
        the object to which we are adding bins

    compare_with: String, optional
        options for input: 'tpc', 'soi', 'webapp'
        determines which types of bins will be added
        default: 'soi'

    bins: iterable of scalars, optional income breakpoints.
            Follows pandas convention. The breakpoint is inclusive if
            right=True. This argument overrides any choice of compare_with.


    right : bool, optional
        Indicates whether the bins include the rightmost edge or not.
        If right == True (the default), then the bins [1,2,3,4]
        indicate (1,2], (2,3], (3,4].

    Returns
    -------
    df: DataFrame object
        the original input that bins have been added to

    """
    if not bins:
        if compare_with == "tpc":
            bins = LARGE_INCOME_BINS

        elif compare_with == "soi":
            bins = SMALL_INCOME_BINS

        elif compare_with == "webapp":
            bins = WEBAPP_INCOME_BINS

        else:
            msg = "Unknown compare_with arg {0}".format(compare_with)
            raise ValueError(msg)

    # Groupby income_measure bins
    df['bins'] = pd.cut(df[income_measure], bins, right=right)
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
        if not colname.startswith('s006'):
            agg[colname] = df[colname] * df['s006']
    return agg


def get_sums(df, na=False):
    """
    Gets the unweighted sum of each column, saving the col name
    and the corresponding sum

    Returns
    -------
    pandas.Series
    """
    sums = defaultdict(lambda: 0)

    for col in df.columns.tolist():
        if col != 'bins':
            if na:
                sums[col] = 'n/a'
            else:
                sums[col] = (df[col]).sum()

    return pd.Series(sums, name='sums')


def results(c):
    """
    Gets the results from the tax calculator and organizes them into a table

    Parameters
    ----------
    c : Calculator object

    Returns
    -------
    DataFrame object
    """
    outputs = []
    for col in STATS_COLUMNS:
        if hasattr(c, 'records') and hasattr(c, 'policy'):
            if hasattr(c.policy, col):
                outputs.append(getattr(c.policy, col))
            else:
                outputs.append(getattr(c.records, col))
        else:
            outputs.append(getattr(c, col))
    return DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)


def weighted_avg_allcols(df, cols, income_measure='_expanded_income'):
    diff = DataFrame(df.groupby('bins', as_index=False).apply(weighted_mean,
                                                              income_measure),
                     columns=[income_measure])
    for col in cols:
        if (col == "s006" or col == 'num_returns_StandardDed' or
                col == 'num_returns_ItemDed' or col == 'num_returns_AMT'):
            diff[col] = df.groupby('bins', as_index=False)[col].sum()[col]
        elif col != income_measure:
            diff[col] = df.groupby('bins', as_index=False).apply(weighted_mean,
                                                                 col)

    return diff

def add_columns(res):
    # weight of returns with positive AGI and
    # itemized deduction greater than standard deduction
    res['c04470'] = res['c04470'].where(((res['c00100'] > 0) &
                                        (res['c04470'] > res['_standard'])),
                                        0)

    # weight of returns with positive AGI and itemized deduction
    res['num_returns_ItemDed'] = res['s006'].where(((res['c00100'] > 0) &
                                                   (res['c04470'] > 0)),
                                                   0)

    # weight of returns with positive AGI and standard deduction
    res['num_returns_StandardDed'] = res['s006'].where(((res['c00100'] > 0) &
                                                       (res['_standard'] > 0)),
                                                       0)

    # weight of returns with positive Alternative Minimum Tax (AMT)
    res['num_returns_AMT'] = res['s006'].where(res['c09600'] > 0, 0)

    return res

def create_distribution_table(calc, groupby, result_type,
                              income_measure='_expanded_income',
                              base_calc = None):
    """
    Gets results given by the tax calculator, sorts them based on groupby, and
        manipulates them based on result_type. Returns these as a table

    Parameters
    ----------
    calc : the Calculator object
    groupby : String object
        options for input: 'weighted_deciles', 'small_income_bins',
        'large_income_bins', 'webapp_income_bins';
        determines how the columns in the resulting DataFrame are sorted
    result_type : String object
        options for input: 'weighted_sum' or 'weighted_avg';
        determines how the data should be manipulated
    base_calc : A Calculator object
        carries the baseline plan

    Notes
    -----
    Taxpayer Characteristics:
        c04470 : Total itemized deduction

        c00100 : AGI (Defecit)

        c09600 : Alternative minimum tax

        s006 : used to weight population

    Returns
    -------
    DataFrame object
    """
    
    # check whether baseline calculator exist
    # keep reform plan
    if base_calc == None:
        res = results(calc)
        res = add_columns(res)
    else:
        resY = results(calc)
        resY = add_columns(resY)
        resX = results(base_calc)
        resX = add_columns(resX)
        
        res = resY.subtract(resX)
        res['c00100'] = resX['c00100']
        res['_expanded_income'] = resX['_expanded_income']
        res['s006'] = resX['s006']

    # sorts the data
    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(res, income_measure=income_measure)
    elif groupby == "small_income_bins":
        df = add_income_bins(res, compare_with="soi",
                             income_measure=income_measure)
    elif groupby == "large_income_bins":
        df = add_income_bins(res, compare_with="tpc",
                             income_measure=income_measure)
    elif groupby == "webapp_income_bins":
        df = add_income_bins(res, compare_with="webapp",
                             income_measure=income_measure)
    else:
        err = ("groupby must be either 'weighted_deciles' or"
               "'small_income_bins' or 'large_income_bins' or"
               "'webapp_income_bins'")
        raise ValueError(err)
    
    if base_calc != None:
        df['c00100'] = resY['c00100'] - resX['c00100']
        df['_expanded_income'] = resY['_expanded_income'] - resX['_expanded_income']

    # manipulates the data
    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == "weighted_sum":
        df = weighted(df, STATS_COLUMNS)
        gp_mean = df.groupby('bins', as_index=False)[TABLE_COLUMNS].sum()
        gp_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(df)[TABLE_COLUMNS]
    elif result_type == "weighted_avg":
        gp_mean = weighted_avg_allcols(df, TABLE_COLUMNS,
                                       income_measure=income_measure)
        sum_row = get_sums(df, na=True)[TABLE_COLUMNS]
    else:
        err = ("result_type must be either 'weighted_sum' or 'weighted_avg")
        raise ValueError(err)

    return gp_mean.append(sum_row)


def create_difference_table(calc1, calc2, groupby,
                            income_measure='_expanded_income',
                            income_to_present = '_ospctax'):
    """
    Gets results given by the two different tax calculators and outputs
        a table that compares the differing results.
        The table is sorted according the the groupby input.

    Parameters
    ----------
    calc1 :  the first Calculator object
    calc2 : the other Calculator object
    groupby : String object
        options for input: 'weighted_deciles', 'small_income_bins',
        'large_income_bins', 'webapp_income_bins'
        determines how the columns in the resulting DataFrame are sorted
    income_measure : string
        options for input: '_expanded_income', '_ospctax'
        classifier of income bins/deciles
    income_to_present : string
        options for input: '_ospctax', '_fica', '_combined'

    Returns
    -------
    DataFrame object
    """

    res1 = results(calc1)
    res2 = results(calc2)
    if groupby == "weighted_deciles":
        df = add_weighted_decile_bins(res2, income_measure=income_measure)
    elif groupby == "small_income_bins":
        df = add_income_bins(res2, compare_with="soi",
                             income_measure=income_measure)
    elif groupby == "large_income_bins":
        df = add_income_bins(res2, compare_with="tpc",
                             income_measure=income_measure)
    elif groupby == "webapp_income_bins":
        df = add_income_bins(res2, compare_with="webapp",
                             income_measure=income_measure)
    else:
        err = ("groupby must be either"
               "'weighted_deciles' or 'small_income_bins'"
               "or 'large_income_bins' or 'webapp_income_bins'")
        raise ValueError(err)

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    res2['tax_diff'] = res2[income_to_present] - res1[income_to_present]

    diffs = means_and_comparisons(res2, 'tax_diff',
                                  df.groupby('bins', as_index=False),
                                  (res2['tax_diff'] * res2['s006']).sum())

    sum_row = get_sums(diffs)[diffs.columns.tolist()]
    diffs = diffs.append(sum_row)

    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ["{0:.2f}%".format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)

    srs_cut = ["{0:.2f}%".format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)

    srs_change = ["{0:.2f}%".format(val * 100)
                  for val in diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)

    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [x for x in diffs.columns.tolist()
                    if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'

    return diffs
