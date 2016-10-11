import copy
import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import defaultdict, OrderedDict

try:
    import bokeh
    BOKEH_AVAILABLE = True
    from bokeh.palettes import Blues4, Reds4
    from bokeh.plotting import figure, output_file, show

except ImportError:
    BOKEH_AVAILABLE = False
#

STATS_COLUMNS = ['_expanded_income', 'c00100', '_standard',
                 'c04470', 'c04600', 'c04800', 'c05200', 'c62100', 'c09600',
                 'c05800', 'c09200', '_refund', 'c07100', '_iitax',
                 '_payrolltax', '_combined', 's006']

# each entry in this array corresponds to the same entry in the array
# TABLE_LABELS below. this allows us to use TABLE_LABELS to map a
# label to the correct column in our distribution table

TABLE_COLUMNS = ['s006', 'c00100', 'num_returns_StandardDed', '_standard',
                 'num_returns_ItemDed', 'c04470', 'c04600', 'c04800', 'c05200',
                 'c62100', 'num_returns_AMT', 'c09600', 'c05800', 'c07100',
                 'c09200', '_refund', '_iitax', '_payrolltax', '_combined']

TABLE_LABELS = ['Returns', 'AGI', 'Standard Deduction Filers',
                'Standard Deduction', 'Itemizers',
                'Itemized Deduction', 'Personal Exemption',
                'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers', 'AMT',
                'Tax before Credits', 'Non-refundable Credits',
                'Tax before Refundable Credits', 'Refundable Credits',
                'Individual Income Tax Liabilities', 'Payroll Tax Liablities',
                'Combined Payroll and Individual Income Tax Liabilities']

# used in our difference table to label the columns
DIFF_TABLE_LABELS = ['Tax Units with Tax Cut', 'Tax Units with Tax Increase',
                     'Count', 'Average Tax Change', 'Total Tax Difference',
                     'Percent with Tax Increase', 'Percent with Tax Decrease',
                     'Share of Overall Change']

LARGE_INCOME_BINS = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                     200000, 1e14]

SMALL_INCOME_BINS = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
                     49999, 74999, 99999, 199999, 499999, 999999, 1499999,
                     1999999, 4999999, 9999999, 1e14]

WEBAPP_INCOME_BINS = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                      199999, 499999, 1000000, 1e14]

EPSILON = 0.000000001


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
            float(agg['s006'].sum() + EPSILON))


def wage_weighted(agg, col_name):
    return (float((agg[col_name] * agg['s006'] * agg['e00200']).sum()) /
            float((agg['s006'] * agg['e00200']).sum() + EPSILON))


def weighted_sum(agg, col_name):
    return (agg[col_name] * agg['s006']).sum()


def weighted_perc_inc(agg, col_name):
    return (float(weighted_count_gt_zero(agg, col_name)) /
            float(weighted_count(agg) + EPSILON))


def weighted_perc_dec(agg, col_name):
    return (float(weighted_count_lt_zero(agg, col_name)) /
            float(weighted_count(agg) + EPSILON))


def weighted_share_of_total(agg, col_name, total):
    return float(weighted_sum(agg, col_name)) / (float(total) + EPSILON)


def add_weighted_decile_bins(df, income_measure='_expanded_income',
                             num_bins=10, labels=None, complex_weight=False):
    """
    Add a column of income bins based on each 10% of the income_measure,
    weighted by s006.

    The default income_measure is `expanded_income`, but `c00100` also works.

    This function will server as a 'grouper' later on.
    """
    # First, weight income measure by s006 if desired
    if complex_weight:
        df['s006_weighted'] = np.multiply(df[income_measure].values,
                                          df['s006'].values)
    # Next, sort by income_measure
    df.sort(income_measure, inplace=True)
    # Do a cumulative sum
    if complex_weight:
        df['cumsum_weights'] = np.cumsum(df['s006_weighted'].values)
    else:
        df['cumsum_weights'] = np.cumsum(df['s006'].values)
    # Max value of cum sum of weights
    max_ = df['cumsum_weights'].values[-1]
    # Create 10 bins and labels based on this cumulative weight
    bin_edges = [0] + list(np.arange(1, (num_bins + 1)) *
                           (max_ / float(num_bins)))
    if not labels:
        labels = range(1, (num_bins + 1))
    #  Groupby weighted deciles
    df['bins'] = pd.cut(df['cumsum_weights'], bins=bin_edges, labels=labels)
    return df


def add_income_bins(df, compare_with='soi', bins=None, right=True,
                    income_measure='_expanded_income'):
    """
    Add a column of income bins of income_measure using pandas 'cut'.
    This will serve as a 'grouper' later on.

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
        if compare_with == 'tpc':
            bins = LARGE_INCOME_BINS

        elif compare_with == 'soi':
            bins = SMALL_INCOME_BINS

        elif compare_with == 'webapp':
            bins = WEBAPP_INCOME_BINS

        else:
            msg = 'Unknown compare_with arg {0}'.format(compare_with)
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


def results(obj):
    """
    Get results from object and organize them into a table.

    Parameters
    ----------
    obj : any object with array-like attributes named as in STATS_COLUMNS list
          Examples include a Tax-Calculator Records object and a
          Pandas DataFrame object

    Returns
    -------
    Pandas DataFrame object
    """
    arrays = [getattr(obj, name) for name in STATS_COLUMNS]
    return DataFrame(data=np.column_stack(arrays), columns=STATS_COLUMNS)


def exp_results(c):
    RES_COLUMNS = STATS_COLUMNS + ['e00200'] + ['MARS']
    outputs = []
    for col in RES_COLUMNS:
        outputs.append(getattr(c.records, col))
    return DataFrame(data=np.column_stack(outputs), columns=RES_COLUMNS)


def weighted_avg_allcols(df, cols, income_measure='_expanded_income'):
    diff = DataFrame(df.groupby('bins', as_index=False).apply(weighted_mean,
                                                              income_measure),
                     columns=[income_measure])
    for col in cols:
        if (col == 's006' or col == 'num_returns_StandardDed' or
                col == 'num_returns_ItemDed' or col == 'num_returns_AMT'):
            diff[col] = df.groupby('bins', as_index=False)[col].sum()[col]
        elif col != income_measure:
            diff[col] = df.groupby('bins', as_index=False).apply(weighted_mean,
                                                                 col)
    return diff


def add_columns(res):
    # weight of returns with positive AGI and
    # itemized deduction greater than standard deduction
    res['c04470'] = \
        res['c04470'].where(((res['c00100'] > 0.) &
                             (res['c04470'] > res['_standard'])), 0.)
    # weight of returns with positive AGI and itemized deduction
    res['num_returns_ItemDed'] = \
        res['s006'].where(((res['c00100'] > 0.) &
                           (res['c04470'] > 0.)), 0.)
    # weight of returns with positive AGI and standard deduction
    res['num_returns_StandardDed'] = \
        res['s006'].where(((res['c00100'] > 0.) &
                           (res['_standard'] > 0.)), 0.)
    # weight of returns with positive Alternative Minimum Tax (AMT)
    res['num_returns_AMT'] = res['s006'].where(res['c09600'] > 0., 0.)
    return res


def create_distribution_table(obj, groupby, result_type,
                              income_measure='_expanded_income',
                              baseline_obj=None, diffs=False):
    """
    Get results from object, sort them based on groupby, manipulate them
    based on result_type, and return them as a table.

    Parameters
    ----------
    obj : any object with array-like attributes named as in STATS_COLUMNS list
        Examples include a Tax-Calculator Records object and a
        Pandas DataFrame object, but if baseline_obj is specified, both obj
        and baseline_obj must have a current_year attribute

    groupby : String object
        options for input: 'weighted_deciles', 'small_income_bins',
        'large_income_bins', 'webapp_income_bins';
        determines how the columns in the resulting DataFrame are sorted

    result_type : String object
        options for input: 'weighted_sum' or 'weighted_avg';
        determines how the data should be manipulated

    baseline_obj : any object with array-like attributes named as in
        the STATS_COLUMNS list and having a current_year attribute
        Examples include a Tax-Calculator Records object

    diffs : boolean
        indicates showing the results from reform or the difference between
        the baseline and reform. Turn this switch to True if you want to see
        the difference

    Notes
    -----
    Taxpayer Characteristics:
        c04470 : Total itemized deduction

        c00100 : AGI (Defecit)

        c09600 : Alternative minimum tax

        s006 : filing unit sample weight

    Returns
    -------
    DataFrame object
    """
    res = results(obj)
    res = add_columns(res)
    if baseline_obj is not None:
        res_base = results(baseline_obj)
        if obj.current_year != baseline_obj.current_year:
            msg = 'current_year differs in baseline obj and reform obj'
            raise ValueError(msg)
        baseline_income_measure = income_measure + '_baseline'
        res[baseline_income_measure] = res_base[income_measure]
        income_measure = baseline_income_measure
        if diffs:
            res_base = add_columns(res_base)
            res = res.subtract(res_base)
            res['s006'] = res_base['s006']
    # sorts the data
    if groupby == 'weighted_deciles':
        df = add_weighted_decile_bins(res, income_measure=income_measure)
    elif groupby == 'small_income_bins':
        df = add_income_bins(res, compare_with='soi',
                             income_measure=income_measure)
    elif groupby == 'large_income_bins':
        df = add_income_bins(res, compare_with='tpc',
                             income_measure=income_measure)
    elif groupby == 'webapp_income_bins':
        df = add_income_bins(res, compare_with='webapp',
                             income_measure=income_measure)
    else:
        msg = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(msg)
    # manipulates the data
    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == 'weighted_sum':
        df = weighted(df, STATS_COLUMNS)
        gp_mean = df.groupby('bins', as_index=False)[TABLE_COLUMNS].sum()
        gp_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(df)[TABLE_COLUMNS]
    elif result_type == 'weighted_avg':
        gp_mean = weighted_avg_allcols(df, TABLE_COLUMNS,
                                       income_measure=income_measure)
        sum_row = get_sums(df, na=True)[TABLE_COLUMNS]
    else:
        msg = "result_type must be either 'weighted_sum' or 'weighted_avg'"
        raise ValueError(msg)
    return gp_mean.append(sum_row)


def create_difference_table(recs1, recs2, groupby,
                            income_measure='_expanded_income',
                            income_to_present='_iitax'):
    """
    Get results from two different Records objects for the same year,
    compare the two results, and return the differences as a table, which
    is sorted according to the variable specified by the groupby argument.

    Parameters
    ----------
    recs1 : a Tax-Calculator Records object that refers to the baseline

    recs2 : a Tax-Calculator Records object that refers to the reform

    groupby : String object
        options for input: 'weighted_deciles', 'small_income_bins',
        'large_income_bins', 'webapp_income_bins'
        determines how the columns in the resulting DataFrame are sorted

    income_measure : String object
        options for input: '_expanded_income', '_iitax'
        classifier of income bins/deciles

    income_to_present : String object
        options for input: '_iitax', '_payrolltax', '_combined'

    Returns
    -------
    DataFrame object
    """
    if recs1.current_year != recs2.current_year:
        msg = 'recs1.current_year not equal to recs2.current_year'
        raise ValueError(msg)
    res1 = results(recs1)
    res2 = results(recs2)
    baseline_income_measure = income_measure + '_baseline'
    res2[baseline_income_measure] = res1[income_measure]
    income_measure = baseline_income_measure
    if groupby == 'weighted_deciles':
        df = add_weighted_decile_bins(res2, income_measure=income_measure)
    elif groupby == 'small_income_bins':
        df = add_income_bins(res2, compare_with='soi',
                             income_measure=income_measure)
    elif groupby == 'large_income_bins':
        df = add_income_bins(res2, compare_with='tpc',
                             income_measure=income_measure)
    elif groupby == 'webapp_income_bins':
        df = add_income_bins(res2, compare_with='webapp',
                             income_measure=income_measure)
    else:
        msg = ("groupby must be either "
               "'weighted_deciles' or 'small_income_bins' "
               "or 'large_income_bins' or 'webapp_income_bins'")
        raise ValueError(msg)
    # compute difference in results
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    res2['tax_diff'] = res2[income_to_present] - res1[income_to_present]
    diffs = means_and_comparisons(res2, 'tax_diff',
                                  df.groupby('bins', as_index=False),
                                  (res2['tax_diff'] * res2['s006']).sum())
    sum_row = get_sums(diffs)[diffs.columns.tolist()]
    diffs = diffs.append(sum_row)
    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ['{0:.2f}%'.format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)

    srs_cut = ['{0:.2f}%'.format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)
    srs_change = ['{0:.2f}%'.format(val * 100)
                  for val in diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)
    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [x for x in diffs.columns.tolist()
                    if 'mean' in x or 'perc' in x]
    for col in non_sum_cols:
        diffs.loc['sums', col] = 'n/a'
    return diffs


def diagnostic_table_odict(recs):
    """
    Extract diagnostic table dictionary from specified Records object.

    Parameters
    ----------
    recs : Records class object

    Returns
    -------
    ordered dictionary of variable names and aggregate weighted values
    """
    # aggregate weighted values expressed in millions or billions
    in_millions = 1.0e-6
    in_billions = 1.0e-9
    odict = OrderedDict()
    # total number of filing units
    odict['Returns (#m)'] = recs.s006.sum() * in_millions
    # adjusted gross income
    odict['AGI ($b)'] = (recs.c00100 * recs.s006).sum() * in_billions
    # number of itemizers
    num = (recs.s006[(recs.c04470 > 0.) * (recs.c00100 > 0.)].sum())
    odict['Itemizers (#m)'] = num * in_millions
    # itemized deduction
    ID1 = recs.c04470 * recs.s006
    val = ID1[recs.c04470 > 0.].sum()
    odict['Itemized Deduction ($b)'] = val * in_billions
    # number of standard deductions
    num = recs.s006[(recs._standard > 0.) * (recs.c00100 > 0.)].sum()
    odict['Standard Deduction Filers (#m)'] = num * in_millions
    # standard deduction
    STD1 = recs._standard * recs.s006
    val = STD1[(recs._standard > 0.) * (recs.c00100 > 0.)].sum()
    odict['Standard Deduction ($b)'] = val * in_billions
    # personal exemption
    val = (recs.c04600 * recs.s006)[recs.c00100 > 0.].sum()
    odict['Personal Exemption ($b)'] = val * in_billions
    # taxable income
    val = (recs.c04800 * recs.s006).sum()
    odict['Taxable Income ($b)'] = val * in_billions
    # regular tax liability
    val = (recs.c05200 * recs.s006).sum()
    odict['Regular Tax ($b)'] = val * in_billions
    # AMT taxable income
    odict['AMT Income ($b)'] = (recs.c62100 * recs.s006).sum() * in_billions
    # total AMT liability
    odict['AMT Liability ($b)'] = (recs.c09600 * recs.s006).sum() * in_billions
    # number of people paying AMT
    odict['AMT Filers (#m)'] = recs.s006[recs.c09600 > 0.].sum() * in_millions
    # tax before credits
    val = (recs.c05800 * recs.s006).sum()
    odict['Tax before Credits ($b)'] = val * in_billions
    # refundable credits
    val = (recs._refund * recs.s006).sum()
    odict['Refundable Credits ($b)'] = val * in_billions
    # nonrefuncable credits
    val = (recs.c07100 * recs.s006).sum()
    odict['Nonrefundable Credits ($b)'] = val * in_billions
    # reform surtaxes (part of federal individual income tax liability)
    val = (recs._surtax * recs.s006).sum()
    odict['Reform Surtaxes ($b)'] = val * in_billions
    # federal individual income tax liability
    val = (recs._iitax * recs.s006).sum()
    odict['Ind Income Tax ($b)'] = val * in_billions
    # OASDI+HI payroll tax liability (including employer share)
    val = (recs._payrolltax * recs.s006).sum()
    odict['Payroll Taxes ($b)'] = val * in_billions
    # combined income and payroll tax liability
    val = (recs._combined * recs.s006).sum()
    odict['Combined Liability ($b)'] = val * in_billions
    return odict


def create_diagnostic_table(calc):
    """
    Extract diagnostic table from specified Calculator object.
    This function leaves the specified calc object unchanged.

    Parameters
    ----------
    calc : Calculator class object

    Returns
    -------
    Pandas DataFrame object containing the table for calc.current_year
    """
    odict = diagnostic_table_odict(calc.records)
    df = pd.DataFrame(data=odict,
                      index=[calc.current_year],
                      columns=odict.keys())
    df = df.transpose()
    pd.options.display.float_format = '{:8,.1f}'.format
    return df


def multiyear_diagnostic_table(calc, num_years=0):
    """
    Generate multi-year diagnostic table from specified Calculator object.
    This function leaves the specified calc object unchanged.

    Parameters
    ----------
    calc : Calculator class object

    num_years : integer (must be between 1 and number of available calc years)

    Returns
    -------
    Pandas DataFrame object containing the multi-year diagnostic table
    """
    if num_years <= 1:
        msg = 'num_year={} is less than one'.format(num_years)
        raise ValueError(msg)
    max_num_years = calc.policy.end_year - calc.policy.current_year + 1
    if num_years > max_num_years:
        msg = ('num_year={} is greater '
               'than max_num_years={}').format(num_years, max_num_years)
        raise ValueError(msg)
    cal = copy.deepcopy(calc)
    dtlist = list()
    for iyr in range(1, num_years + 1):
        if cal.behavior.has_response():
            cal_clp = cal.current_law_version()
            cal_br = cal.behavior.response(cal_clp, cal)
            dtlist.append(create_diagnostic_table(cal_br))
        else:
            cal.calc_all()
            dtlist.append(create_diagnostic_table(cal))
        if iyr < num_years:
            cal.increment_year()
    return pd.concat(dtlist, axis=1)


def ascii_output(csv_filename, ascii_filename):
    """
    Converts csv output from Calculator into ascii output with uniform
    columns and transposes data so columns are rows and rows are columns.
    In an ipython notebook, you can import this function from the utils module.
    """
    # list of integers corresponding to the number(s) of the row(s) in the
    # csv file, only rows in list will be recorded in final output
    # if left as [], results in entire file being converted to ascii
    # put in order from smallest to largest, for example:
    # recids = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 108820]
    recids = [1, 4, 5]
    # Number of characters in each column, must be whole nonnegative integer
    col_size = 15
    df = pd.read_csv(csv_filename, dtype=object)
    # keeps only listed recid's
    if recids != []:
        def f(x):
            return x - 1
        recids = map(f, recids)  # maps recids to correct index in df
        df = df.ix[recids]
    # does transposition
    out = df.T.reset_index()
    # formats data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)
    out.to_csv(ascii_filename, header=False, index=False,
               delim_whitespace=True, sep='\t')


def get_mtr_data(calcX, calcY, weights, MARS='ALL',
                 income_measure='e00200', mtr_measure='IIT',
                 complex_weight=False):
    """
    This function prepares the MTR data for two calculators.

    Parameters
    ----------
    calcX : a Tax-Calculator Records object that refers to the baseline

    calcY : a Tax-Calculator Records object that refers to the reform

    weights : String object
        options for input: weighted_count_lt_zero, weighted_count_gt_zero,
            weighted_mean, wage_weighted, weighted_sum,
            weighted_perc_inc, weighted_perc_dec
        Choose different weight measure

    MARS : Integer
        options for input: 1, 2, 3, 4
        Choose different filling status

    income_measure : String object
        options for input: '_expanded_income', 'c00100', 'e00200'
        classifier of income bins/deciles

    mtr_measure : String object
        options for input: '_iitax', '_payrolltax', '_combined'

    complex_weight : Boolean
        The cumulated sum will be carried out based on weighted income measure
        if this option is true
    Returns
    -------
    DataFrame object
    """
    # Get output columns
    df_x = exp_results(calcX)
    df_y = exp_results(calcY)

    # Calculate MTR
    a, mtr_iit_x, mtr_combined_x = calcX.mtr()
    a, mtr_iit_y, mtr_combined_y = calcY.mtr()
    df_x['mtr_iit'] = mtr_iit_x
    df_y['mtr_iit'] = mtr_iit_y
    df_x['mtr_combined'] = mtr_combined_x
    df_y['mtr_combined'] = mtr_combined_y

    df_y[income_measure] = df_x[income_measure]

    # Complex weighted bins or not
    if complex_weight:
        df_x = add_weighted_decile_bins(df_x, income_measure, 100,
                                        complex_weight=True)
        df_y = add_weighted_decile_bins(df_y, income_measure, 100,
                                        complex_weight=True)
    else:
        df_x = add_weighted_decile_bins(df_x, income_measure, 100)
        df_y = add_weighted_decile_bins(df_y, income_measure, 100)

    # Select either all filers or one filling status
    if MARS == 'ALL':
        df_filtered_x = df_x.copy()
        df_filtered_y = df_y.copy()
    else:
        df_filtered_x = df_x[(df_x['MARS'] == MARS)].copy()
        df_filtered_y = df_y[(df_y['MARS'] == MARS)].copy()

    # Split into groups by 'bins'
    gp_x = df_filtered_x.groupby('bins', as_index=False)
    gp_y = df_filtered_y.groupby('bins', as_index=False)

    # Apply desired weights to mtr
    if mtr_measure == 'combined':
        wgtpct_x = gp_x.apply(weights, 'mtr_combined')
        wgtpct_y = gp_y.apply(weights, 'mtr_combined')
    elif mtr_measure == 'IIT':
        wgtpct_x = gp_x.apply(weights, 'mtr_iit')
        wgtpct_y = gp_y.apply(weights, 'mtr_iit')

    wpct_x = DataFrame(data=wgtpct_x, columns=['w_mtr'])
    wpct_y = DataFrame(data=wgtpct_y, columns=['w_mtr'])

    # Add bin labels
    wpct_x['bins'] = np.arange(1, 101)
    wpct_y['bins'] = np.arange(1, 101)

    # Merge two dataframes
    rsltx = pd.merge(df_filtered_x[['bins']], wpct_x, how='left')
    rslty = pd.merge(df_filtered_y[['bins']], wpct_y, how='left')

    df_filtered_x['w_mtr'] = rsltx['w_mtr'].values
    df_filtered_y['w_mtr'] = rslty['w_mtr'].values

    # Get rid of duplicated bins
    df_filtered_x.drop_duplicates(subset='bins', inplace=True)
    df_filtered_y.drop_duplicates(subset='bins', inplace=True)

    # Prepare cleaned mtr data and concatenate into one datafram
    df_filtered_x = df_filtered_x['w_mtr']
    df_filtered_y = df_filtered_y['w_mtr']

    merged = pd.concat([df_filtered_x, df_filtered_y], axis=1,
                       ignore_index=True)
    merged.columns = ['base', 'reform']

    return merged


def requires_bokeh(fn):
    """
    Decorator for functions that require bokeh.
    If BOKEH_AVAILABLE=True, this does nothing.
    IF BOKEH_AVAILABEL=False, we raise an exception and tell the caller
    that they must install bokeh in order to use the function.
    """
    def wrapped_f(*args, **kwargs):
        if BOKEH_AVAILABLE:
            return fn(*args, **kwargs)
        else:
            msg = ("`bokeh` is not installed. Please install "
                   "`bokeh` to use this package (`conda install "
                   "bokeh`)")
            raise RuntimeError(msg)

    return wrapped_f


@requires_bokeh
def mtr_plot(source, xlab='Percentile', ylab='Avg. MTR', title='MTR plot',
             plot_width=425, plot_height=250, loc='top_left'):
    """
    This function generates marginal tax rate plot.
    Source data can be obtained from get_mtr_data function.

    Parameters
    ----------
    source : DataFrame which can be obtained using get_mtr_data() function

    xlab : String object
        Name for X axis

    ylab : String object
        Name for Y axis

    title : String object
        Caption for the plot

    plot_width : Numeric (Usually integer)
        Width of the plot

    plot_height : Numeric (Usually integer)
        Height of the plot

    loc : String object
        Toptions for input: "top_right", "top_left", "bottom_left",
            "bottom_right"
        Choose the location of the legend label
    Returns
    -------
    Figure Object (Use show(FIGURE_NAME) option to visualize)
        Note that, when using command line, output file needs to be
        first specified using command output_file("FILE_NAME.html")
    """
    PP = figure(plot_width=plot_width, plot_height=plot_height, title=title)

    PP.line((source.reset_index()).index,
            (source.reset_index()).base, line_color=Blues4[0], line_width=0.8,
            line_alpha=.8, legend="Base")

    PP.line((source.reset_index()).index,
            (source.reset_index()).reform, line_color=Reds4[1], line_width=0.8,
            line_alpha=1, legend="Reform")

    PP.legend.label_text_font = "times"
    PP.legend.label_text_font_style = "italic"
    PP.legend.location = loc

    PP.legend.label_width = 2
    PP.legend.label_height = 2
    PP.legend.label_standoff = 2
    PP.legend.glyph_width = 14
    PP.legend.glyph_height = 14
    PP.legend.legend_spacing = 5
    PP.legend.legend_padding = 5
    PP.yaxis.axis_label = ylab
    PP.xaxis.axis_label = xlab
    return PP


def string_to_number(string):
    if not string:
        return 0
    try:
        return int(string)
    except ValueError:
        return float(string)
