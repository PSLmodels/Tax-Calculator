"""
Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 utils.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy utils.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)
#
# pylint: disable=too-many-lines

import copy
from collections import defaultdict, OrderedDict
import six
import numpy as np
import pandas as pd
try:
    BOKEH_AVAILABLE = True
    import bokeh.plotting as bp
except ImportError:
    BOKEH_AVAILABLE = False


STATS_COLUMNS = ['_expanded_income', 'c00100', '_standard',
                 'c04470', 'c04600', 'c04800', 'c05200', 'c62100', 'c09600',
                 'c05800', 'c09200', '_refund', 'c07100', '_iitax',
                 '_payrolltax', '_combined', 's006']

# Items in the TABLE_COLUMNS list below correspond to the items in the
# TABLE_LABELS list below; this correspondence allows us to use TABLE_LABELS
# to map a label to the correct column in our distribution tables.
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

# Following list is used in our difference table to label its columns.
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


def count_gt_zero(data):
    """
    Return unweighted count of positive data items.
    """
    return sum([1 for item in data if item > 0])


def count_lt_zero(data):
    """
    Return unweighted count of negative data items.
    """
    return sum([1 for item in data if item < 0])


def weighted_count_lt_zero(pdf, col_name, tolerance=-0.001):
    """
    Return weighted count of negative Pandas DateFrame col_name items.
    """
    return pdf[pdf[col_name] < tolerance]['s006'].sum()


def weighted_count_gt_zero(pdf, col_name, tolerance=0.001):
    """
    Return weighted count of positive Pandas DateFrame col_name items.
    """
    return pdf[pdf[col_name] > tolerance]['s006'].sum()


def weighted_count(pdf):
    """
    Return weighted count of items in Pandas DataFrame.
    """
    return pdf['s006'].sum()


def weighted_mean(pdf, col_name):
    """
    Return weighted mean of Pandas DataFrame col_name items.
    """
    return (float((pdf[col_name] * pdf['s006']).sum()) /
            float(pdf['s006'].sum() + EPSILON))


def wage_weighted(pdf, col_name):
    """
    Return wage-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    wage = 'e00200'
    return (float((pdf[col_name] * pdf[swght] * pdf[wage]).sum()) /
            float((pdf[swght] * pdf[wage]).sum() + EPSILON))


def agi_weighted(pdf, col_name):
    """
    Return AGI-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    agi = 'c00100'
    return (float((pdf[col_name] * pdf[swght] * pdf[agi]).sum()) /
            float((pdf[swght] * pdf[agi]).sum() + EPSILON))


def expanded_income_weighted(pdf, col_name):
    """
    Return expanded-income-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    expinc = '_expanded_income'
    return (float((pdf[col_name] * pdf[swght] * pdf[expinc]).sum()) /
            float((pdf[swght] * pdf[expinc]).sum() + EPSILON))


def weighted_sum(pdf, col_name):
    """
    Return weighted sum of Pandas DataFrame col_name items.
    """
    return (pdf[col_name] * pdf['s006']).sum()


def weighted_perc_inc(pdf, col_name):
    """
    Return weighted fraction (not percent) of positive values for the
    variable with col_name in the specified Pandas DataFrame.
    """
    return (float(weighted_count_gt_zero(pdf, col_name)) /
            float(weighted_count(pdf) + EPSILON))


def weighted_perc_dec(pdf, col_name):
    """
    Return weighted fraction (not percent) of negative values for the
    variable with col_name in the specified Pandas DataFrame.
    """
    return (float(weighted_count_lt_zero(pdf, col_name)) /
            float(weighted_count(pdf) + EPSILON))


def weighted_share_of_total(pdf, col_name, total):
    """
    Return ratio of weighted_sum(pdf, col_name) and specified total.
    """
    return float(weighted_sum(pdf, col_name)) / (float(total) + EPSILON)


def add_weighted_decile_bins(pdf, income_measure='_expanded_income',
                             num_bins=10, labels=None,
                             weight_by_income_measure=False):
    """
    Add a column of income bins based on each 10% of the income_measure,
    weighted by s006.

    The default income_measure is `expanded_income`, but `c00100` also works.

    This function will server as a 'grouper' later on.
    """
    # First, weight income measure by s006 if desired
    if weight_by_income_measure:
        pdf['s006_weighted'] = np.multiply(pdf[income_measure].values,
                                           pdf['s006'].values)
    # Next, sort by income_measure
    pdf.sort_values(by=income_measure, inplace=True)
    # Do a cumulative sum
    if weight_by_income_measure:
        pdf['cumsum_weights'] = np.cumsum(pdf['s006_weighted'].values)
    else:
        pdf['cumsum_weights'] = np.cumsum(pdf['s006'].values)
    # Max value of cum sum of weights
    max_ = pdf['cumsum_weights'].values[-1]
    # Create 10 bins and labels based on this cumulative weight
    bin_edges = [0] + list(np.arange(1, (num_bins + 1)) *
                           (max_ / float(num_bins)))
    if not labels:
        labels = range(1, (num_bins + 1))
    #  Groupby weighted deciles
    pdf['bins'] = pd.cut(pdf['cumsum_weights'], bins=bin_edges, labels=labels)
    return pdf


def add_income_bins(pdf, compare_with='soi', bins=None, right=True,
                    income_measure='_expanded_income'):
    """
    Add a column of income bins of income_measure using pandas 'cut'.
    This will serve as a 'grouper' later on.

    Parameters
    ----------
    pdf: Pandas DataFrame object
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
    pdf: Pandas DataFrame object
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
    pdf['bins'] = pd.cut(pdf[income_measure], bins, right=right)
    return pdf


def means_and_comparisons(pdf, col_name, gpdf, weighted_total):
    """
    Return Pandas DataFrame based specified grouped values of col_name in
    specified gpdf Pandas DataFrame.
    pdf: Pandas DataFrame for full results of calculation (NEVER USED)
    col_name: the column name to calculate against
    gpdf: grouped Pandas DataFrame
    """
    # pylint: disable=unused-argument
    # Who has a tax cut, and who has a tax increase
    diffs = gpdf.apply(weighted_count_lt_zero, col_name)
    diffs = pd.DataFrame(data=diffs, columns=['tax_cut'])
    diffs['tax_inc'] = gpdf.apply(weighted_count_gt_zero, col_name)
    diffs['count'] = gpdf.apply(weighted_count)
    diffs['mean'] = gpdf.apply(weighted_mean, col_name)
    diffs['tot_change'] = gpdf.apply(weighted_sum, col_name)
    diffs['perc_inc'] = gpdf.apply(weighted_perc_inc, col_name)
    diffs['perc_cut'] = gpdf.apply(weighted_perc_dec, col_name)
    diffs['share_of_change'] = gpdf.apply(weighted_share_of_total,
                                          col_name, weighted_total)
    return diffs


def weighted(pdf, col_names):
    """
    Return Pandas DataFrame in which each pdf column variable has been
    multiplied by the s006 weight variable in the specified Pandas DataFrame.
    """
    agg = pdf
    for colname in col_names:
        if not colname.startswith('s006'):
            agg[colname] = pdf[colname] * pdf['s006']
    return agg


def get_sums(pdf, not_available=False):
    """
    Compute unweighted sum of items in each column of a Pandas DataFrame.

    Returns
    -------
    Pandas Series object containing column sums indexed by pdf colum names.
    """
    sums = defaultdict(lambda: 0)
    for col in pdf.columns.values.tolist():
        if col != 'bins':
            if not_available:
                sums[col] = 'n/a'
            else:
                sums[col] = (pdf[col]).sum()
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
    return pd.DataFrame(data=np.column_stack(arrays), columns=STATS_COLUMNS)


def weighted_avg_allcols(pdf, col_list, income_measure='_expanded_income'):
    """
    Return Pandas DataFrame in which variables in col_list of pdf have
    their weighted_mean computed using the specifed income_measure, except
    for certain count-like column variables whose sum is computed.
    """
    wadf = pd.DataFrame(pdf.groupby('bins',
                                    as_index=False).apply(weighted_mean,
                                                          income_measure),
                        columns=[income_measure])
    for col in col_list:
        if (col == 's006' or col == 'num_returns_StandardDed' or
                col == 'num_returns_ItemDed' or col == 'num_returns_AMT'):
            wadf[col] = pdf.groupby('bins',
                                    as_index=False)[col].sum()[col]
        elif col != income_measure:
            wadf[col] = pdf.groupby('bins',
                                    as_index=False).apply(weighted_mean, col)
    return wadf


def add_columns(pdf):
    """
    Add several columns to specified Pandas DataFrame.
    """
    # weight of returns with positive AGI and
    # itemized deduction greater than standard deduction
    pdf['c04470'] = \
        pdf['c04470'].where(((pdf['c00100'] > 0.) &
                             (pdf['c04470'] > pdf['_standard'])), 0.)
    # weight of returns with positive AGI and itemized deduction
    pdf['num_returns_ItemDed'] = \
        pdf['s006'].where(((pdf['c00100'] > 0.) &
                           (pdf['c04470'] > 0.)), 0.)
    # weight of returns with positive AGI and standard deduction
    pdf['num_returns_StandardDed'] = \
        pdf['s006'].where(((pdf['c00100'] > 0.) &
                           (pdf['_standard'] > 0.)), 0.)
    # weight of returns with positive Alternative Minimum Tax (AMT)
    pdf['num_returns_AMT'] = pdf['s006'].where(pdf['c09600'] > 0., 0.)
    return pdf


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
        determines how the columns in the resulting Pandas DataFrame are sorted

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
    Pandas DataFrame object
    """
    # pylint: disable=too-many-arguments
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
        pdf = add_weighted_decile_bins(res, income_measure=income_measure)
    elif groupby == 'small_income_bins':
        pdf = add_income_bins(res, compare_with='soi',
                              income_measure=income_measure)
    elif groupby == 'large_income_bins':
        pdf = add_income_bins(res, compare_with='tpc',
                              income_measure=income_measure)
    elif groupby == 'webapp_income_bins':
        pdf = add_income_bins(res, compare_with='webapp',
                              income_measure=income_measure)
    else:
        msg = ("groupby must be either 'weighted_deciles' or "
               "'small_income_bins' or 'large_income_bins' or "
               "'webapp_income_bins'")
        raise ValueError(msg)
    # manipulates the data
    pd.options.display.float_format = '{:8,.0f}'.format
    if result_type == 'weighted_sum':
        pdf = weighted(pdf, STATS_COLUMNS)
        gpdf_mean = pdf.groupby('bins', as_index=False)[TABLE_COLUMNS].sum()
        gpdf_mean.drop('bins', axis=1, inplace=True)
        sum_row = get_sums(pdf)[TABLE_COLUMNS]
    elif result_type == 'weighted_avg':
        gpdf_mean = weighted_avg_allcols(pdf, TABLE_COLUMNS,
                                         income_measure=income_measure)
        sum_row = get_sums(pdf, not_available=True)[TABLE_COLUMNS]
    else:
        msg = "result_type must be either 'weighted_sum' or 'weighted_avg'"
        raise ValueError(msg)
    return gpdf_mean.append(sum_row)


def create_difference_table(recs1, recs2, groupby,
                            income_measure='_expanded_income',
                            income_to_present='_iitax'):
    """
    Get results from two different Records objects for the same year, compare
    the two results, and return the differences as a Pandas DataFrame that is
    sorted according to the variable specified by the groupby argument.

    Parameters
    ----------
    recs1 : a Tax-Calculator Records object that refers to the baseline

    recs2 : a Tax-Calculator Records object that refers to the reform

    groupby : String object
        options for input: 'weighted_deciles', 'small_income_bins',
        'large_income_bins', 'webapp_income_bins'
        determines how the columns in the resulting Pandas DataFrame are sorted

    income_measure : String object
        options for input: '_expanded_income', '_iitax'
        classifier of income bins/deciles

    income_to_present : String object
        options for input: '_iitax', '_payrolltax', '_combined'

    Returns
    -------
    Pandas DataFrame object
    """
    # pylint: disable=too-many-locals
    if recs1.current_year != recs2.current_year:
        msg = 'recs1.current_year not equal to recs2.current_year'
        raise ValueError(msg)
    res1 = results(recs1)
    res2 = results(recs2)
    baseline_income_measure = income_measure + '_baseline'
    res2[baseline_income_measure] = res1[income_measure]
    income_measure = baseline_income_measure
    if groupby == 'weighted_deciles':
        pdf = add_weighted_decile_bins(res2, income_measure=income_measure)
    elif groupby == 'small_income_bins':
        pdf = add_income_bins(res2, compare_with='soi',
                              income_measure=income_measure)
    elif groupby == 'large_income_bins':
        pdf = add_income_bins(res2, compare_with='tpc',
                              income_measure=income_measure)
    elif groupby == 'webapp_income_bins':
        pdf = add_income_bins(res2, compare_with='webapp',
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
                                  pdf.groupby('bins', as_index=False),
                                  (res2['tax_diff'] * res2['s006']).sum())
    sum_row = get_sums(diffs)[diffs.columns.values.tolist()]
    diffs = diffs.append(sum_row)  # pylint: disable=redefined-variable-type
    pd.options.display.float_format = '{:8,.0f}'.format
    srs_inc = ['{0:.2f}%'.format(val * 100) for val in diffs['perc_inc']]
    diffs['perc_inc'] = pd.Series(srs_inc, index=diffs.index)

    srs_cut = ['{0:.2f}%'.format(val * 100) for val in diffs['perc_cut']]
    diffs['perc_cut'] = pd.Series(srs_cut, index=diffs.index)
    srs_change = ['{0:.2f}%'.format(val * 100)
                  for val in diffs['share_of_change']]
    diffs['share_of_change'] = pd.Series(srs_change, index=diffs.index)
    # columns containing weighted values relative to the binning mechanism
    non_sum_cols = [col for col in diffs.columns
                    if 'mean' in col or 'perc' in col]
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
    # pylint: disable=protected-access
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
    ided1 = recs.c04470 * recs.s006
    val = ided1[recs.c04470 > 0.].sum()
    odict['Itemized Deduction ($b)'] = val * in_billions
    # number of standard deductions
    num = recs.s006[(recs._standard > 0.) * (recs.c00100 > 0.)].sum()
    odict['Standard Deduction Filers (#m)'] = num * in_millions
    # standard deduction
    sded1 = recs._standard * recs.s006
    val = sded1[(recs._standard > 0.) * (recs.c00100 > 0.)].sum()
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
    pdf = pd.DataFrame(data=odict,
                       index=[calc.current_year],
                       columns=odict.keys())
    pdf = pdf.transpose()
    pd.options.display.float_format = '{:8,.1f}'.format
    return pdf


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
    if num_years < 1:
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
    # ** List of integers corresponding to the numbers of the rows in the
    #    csv file, only rows in list will be recorded in final output.
    #    If left as [], results in entire file are being converted to ascii.
    #    Put in order from smallest to largest, for example:
    #    recids = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 108820]
    recids = [1, 4, 5]
    # ** Number of characters in each column, must be a nonnegative integer.
    col_size = 15
    # read csv_filename into a Pandas DataFrame
    pdf = pd.read_csv(csv_filename, dtype=object)
    # keep only listed recids if recids list is not empty
    if recids != []:
        def pdf_recid(recid):
            """ Return Pandas DataFrame recid value for specified recid """
            return recid - 1
        recids = map(pdf_recid, recids)  # pylint: disable=bad-builtin
        pdf = pdf.ix[recids]  # pylint: disable=no-member
    # do transposition
    out = pdf.T.reset_index()  # pylint: disable=no-member
    # format data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)
    # write ascii output to specified ascii_filename
    out.to_csv(ascii_filename, header=False, index=False,
               delim_whitespace=True, sep='\t')


def mtr_graph_data(calc1, calc2,
                   mars='ALL',
                   mtr_measure='combined',
                   mtr_variable='e00200p',
                   mtr_wrt_full_compen=True,
                   income_measure='wages',
                   dollar_weighting=False):
    """
    Prepare data needed by the mtr_graph_plot utility function.

    Parameters
    ----------
    calc1 : a Calculator object that refers to baseline policy

    calc2 : a Calculator object that refers to reform policy

    mars : integer or string
        options:
            'ALL': include all filing units in sample;
            1: include only single filing units;
            2: include only married-filing-jointly filing units;
            3: include only married-filing-separately filing units; and
            4: include only head-of-household filing units.
        specifies which filing status subgroup to show in the graph

    mtr_measure : string
        options:
            'itax': marginal individual income tax rate;
            'ptax': marginal payroll tax rate; and
            'combined': sum of marginal income and payroll tax rates.
        specifies which marginal tax rate to show on graph's y axis

    mtr_variable : string
        any string in the Calculator.VALID_MTR_VARS set
        specifies variable to change in order to compute marginal tax rates

    mtr_wrt_full_compen : boolean
        see documentation of Calculator.mtr() argument wrt_full_compensation
        (value has an effect only if mtr_variable is 'e00200p')

    income_measure : string
        options:
            'wages': wage and salary income (e00200);
            'agi': adjusted gross income, AGI (c00100); and
            'expanded_income': sum of AGI, non-taxable interest income,
                               non-taxable social security benefits, and
                               employer share of FICA taxes.
        specifies which income variable to show on the graph's x axis

    dollar_weighting : boolean
        False implies both income_measure percentiles on x axis and
        mtr values for each percentile on the y axis are computed
        without using dollar income_measure weights (just sampling weights);
        True implies both income_measure percentiles on x axis and
        mtr values for each percentile on the y axis are computed
        using dollar income_measure weights (in addition to sampling weights).
        Specifying True produces a graph x axis that shows income_measure
        (not filing unit) percentiles.

    Returns
    -------
    dictionary object suitable for passing to mtr_graph_plot utility function
    """
    # pylint: disable=too-many-arguments,too-many-statements,
    # pylint: disable=too-many-locals,too-many-branches
    # check validity of function arguments
    # . . check mars value
    if isinstance(mars, six.string_types):
        if mars != 'ALL':
            msg = 'string value of mars="{}" is not "ALL"'
            raise ValueError(msg.format(mars))
    elif isinstance(mars, int):
        if mars < 1 or mars > 4:
            msg = 'integer mars="{}" is not in [1,4] range'
            raise ValueError(msg.format(mars))
    else:
        msg = 'mars="{}" is neither a string nor an integer'
        raise ValueError(msg.format(mars))
    # . . check mtr_measure value
    if mtr_measure == 'itax':
        mtr_str = 'Income-Tax'
    elif mtr_measure == 'ptax':
        mtr_str = 'Payroll-Tax'
    elif mtr_measure == 'combined':
        mtr_str = 'Income+Payroll-Tax'
    else:
        msg = ('mtr_measure="{}" is neither '
               '"itax" nor "ptax" nor "combined"')
        raise ValueError(msg.format(mtr_measure))
    # . . check income_measure value
    if income_measure == 'wages':
        income_var = 'e00200'
        income_str = 'Wage'
    elif income_measure == 'agi':
        income_var = 'c00100'
        income_str = 'AGI'
    elif income_measure == 'expanded_income':
        income_var = '_expanded_income'
        income_str = 'Expanded Income'
    else:
        msg = ('income_measure="{}" is neither '
               '"wages", "agi", nor "expanded_income"')
        raise ValueError(msg.format(income_measure))
    # calculate marginal tax rates
    (mtr1_ptax, mtr1_itax,
     mtr1_combined) = calc1.mtr(variable_str=mtr_variable,
                                wrt_full_compensation=mtr_wrt_full_compen)
    (mtr2_ptax, mtr2_itax,
     mtr2_combined) = calc2.mtr(variable_str=mtr_variable,
                                wrt_full_compensation=mtr_wrt_full_compen)
    # extract needed output that is unchanged by reform from calc1
    record_columns = ['s006']
    if mars != 'ALL':
        record_columns.append('MARS')
    record_columns.append(income_var)
    output = [getattr(calc1.records, col) for col in record_columns]
    df1 = pd.DataFrame(data=np.column_stack(output), columns=record_columns)
    df2 = pd.DataFrame(data=np.column_stack(output), columns=record_columns)
    # set mtr given specified mtr_measure
    if mtr_measure == 'itax':
        df1['mtr'] = mtr1_itax
        df2['mtr'] = mtr2_itax
    elif mtr_measure == 'ptax':
        df1['mtr'] = mtr1_ptax
        df2['mtr'] = mtr2_ptax
    elif mtr_measure == 'combined':
        df1['mtr'] = mtr1_combined
        df2['mtr'] = mtr2_combined
    # select filing-status subgroup, if any
    if mars != 'ALL':
        df1 = df1[df1['MARS'] == mars]
        df2 = df2[df2['MARS'] == mars]
    # create 'bins' column given specified income_var and dollar_weighting
    df1 = add_weighted_decile_bins(df1,
                                   income_measure=income_var,
                                   num_bins=100,
                                   weight_by_income_measure=dollar_weighting)
    df2 = add_weighted_decile_bins(df2,
                                   income_measure=income_var,
                                   num_bins=100,
                                   weight_by_income_measure=dollar_weighting)
    # split into groups specified by 'bins'
    gdf1 = df1.groupby('bins', as_index=False)
    gdf2 = df2.groupby('bins', as_index=False)
    # specify mtr weighting function given dollar_weghting and income_measure
    if dollar_weighting:
        if income_measure == 'expanded_income':
            weighting_method = expanded_income_weighted
        elif income_measure == 'agi':
            weighting_method = agi_weighted
        else:  # if income_measure == 'wages'
            weighting_method = wage_weighted
    else:
        weighting_method = weighted_mean
    # apply the weighting_method to mtr
    wghtmtr1 = gdf1.apply(weighting_method, 'mtr')
    wghtmtr2 = gdf2.apply(weighting_method, 'mtr')
    wmtr1 = pd.DataFrame(data=wghtmtr1, columns=['wmtr'])
    wmtr2 = pd.DataFrame(data=wghtmtr2, columns=['wmtr'])
    # add bin labels to wmtr1 and wmtr2 DataFrames
    wmtr1['bins'] = np.arange(1, 101)
    wmtr2['bins'] = np.arange(1, 101)
    # merge dfN['bins'] and wmtrN DataFrames into a single DataFrame
    xdf1 = pd.merge(df1[['bins']], wmtr1, how='left')
    xdf2 = pd.merge(df2[['bins']], wmtr2, how='left')
    df1['wmtr'] = xdf1['wmtr'].values
    df2['wmtr'] = xdf2['wmtr'].values
    # eliminate duplicated bins
    df1.drop_duplicates(subset='bins', inplace=True)
    df2.drop_duplicates(subset='bins', inplace=True)
    # merge weighted mtr data inot a single DataFrame
    df1 = df1['wmtr']
    df2 = df2['wmtr']
    merged = pd.concat([df1, df2], axis=1, ignore_index=True)
    merged.columns = ['base', 'reform']
    merged.index = (merged.reset_index()).index
    if dollar_weighting:
        merged = merged[1:]
    # construct dictionary containing merged data and auto-generated labels
    data = dict()
    data['lines'] = merged
    if dollar_weighting:
        income_str = 'Dollar-weighted {}'.format(income_str)
        mtr_str = 'Dollar-weighted {}'.format(mtr_str)
    data['xlabel'] = '{} Percentile'.format(income_str)
    data['ylabel'] = '{} MTR'.format(mtr_str)
    title_str = 'Mean Marginal Tax Rate by Income Percentile'
    if mtr_variable == 'e00200p' and mtr_wrt_full_compen:
        title_str = '{} (wrt full compensation)'.format(title_str)
    data['title'] = title_str
    return data


def requires_bokeh(func):
    """
    Decorator for functions that require the bokeh package.
    If BOKEH_AVAILABLE=True, this does nothing.
    IF BOKEH_AVAILABLE=False, we raise an exception and tell the caller
    that they must install the bokeh package in order to use the function.
    """
    def wrapped_f(*args, **kwargs):
        """
        Raise error if bokeh package is not available.
        """
        if BOKEH_AVAILABLE:
            return func(*args, **kwargs)
        else:
            msg = ("`bokeh` is not installed. Please install "
                   "`bokeh` to use this package (`conda install "
                   "bokeh`)")
            raise RuntimeError(msg)
    return wrapped_f


@requires_bokeh
def mtr_graph_plot(data,
                   width=850,
                   height=500,
                   xlabel='',
                   ylabel='',
                   title='',
                   legendloc='bottom_right'):
    """
    Plot a marginal tax rate graph using data from mtr_graph_data function.

    Parameters
    ----------
    data : dictionary object returned from mtr_graph_data() utility function

    width : integer
        width of plot expressed in pixels

    height : integer
        height of plot expressed in pixels

    xlabel : string
        x-axis label; if '', then use label generated by mtr_graph_data

    ylabel : string
        y-axis label; if '', then use label generated by mtr_graph_data

    title : string
        graph title; if '', then use title generated by mtr_graph_data

    legendloc : string
        options: 'top_right', 'top_left', 'bottom_left', 'bottom_right'
        specifies location of the legend in the plot

    Returns
    -------
    bokeh.plotting figure object containing a raster graphics plot

    Notes
    -----
    USAGE EXAMPLE:
      gdata = mtr_graph_data(calc1, calc2)
      gplot = mtr_graph_plot(gdata)
    THEN  # when working interactively in a Python notebook
      bp.show(gplot)
    OR    # when executing script using Python command-line interpreter
      bp.output_file('anyname.html')  # file to write to when invoking bp.show
      bp.show(gplot, title='MTR by Income Percentile')
    WILL VISUALIZE GRAPH IN BROWSER

    To convert the visualized graph into a PNG-formatted file, click on
    the "Save" icon on the Toolbar (located in the top-right corner of
    the visualized graph) and a PNG-formatted file will written to your
    Download directory.

    The ONLY output option the bokeh.plotting figure has is HTML format,
    which (as described above) can be converted into a PNG-formatted
    raster graphics file.  There is no option to make the bokeh.plotting
    figure generate a vector graphics file such as an EPS file.
    """
    # pylint: disable=too-many-arguments
    if title == '':
        title = data['title']
    fig = bp.figure(plot_width=width, plot_height=height, title=title)
    fig.title.text_font_size = '12pt'
    lines = data['lines']
    fig.line((lines.reset_index()).index, (lines.reset_index()).base,
             line_color='blue', legend='Base')
    fig.line((lines.reset_index()).index, (lines.reset_index()).reform,
             line_color='red', legend='Reform')
    fig.circle(0, 0, visible=False)  # force zero to be included on y axis
    if xlabel == '':
        xlabel = data['xlabel']
    fig.xaxis.axis_label = xlabel
    fig.xaxis.axis_label_text_font_size = '12pt'
    fig.xaxis.axis_label_text_font_style = 'normal'
    if ylabel == '':
        ylabel = data['ylabel']
    fig.yaxis.axis_label = ylabel
    fig.yaxis.axis_label_text_font_size = '12pt'
    fig.yaxis.axis_label_text_font_style = 'normal'
    fig.legend.location = legendloc
    fig.legend.label_text_font = 'times'
    fig.legend.label_text_font_style = 'italic'
    fig.legend.label_width = 2
    fig.legend.label_height = 2
    fig.legend.label_standoff = 2
    fig.legend.glyph_width = 14
    fig.legend.glyph_height = 14
    fig.legend.spacing = 5
    fig.legend.padding = 5
    return fig


def string_to_number(string):
    """
    Return either integer or float conversion of specified string.
    """
    if not string:
        return 0
    try:
        return int(string)
    except ValueError:
        return float(string)
