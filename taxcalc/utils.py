"""
Tax-Calculator utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 utils.py
# pylint --disable=locally-disabled utils.py
#
# pylint: disable=too-many-lines

import os
import math
import copy
import json
import random
from collections import defaultdict, OrderedDict
from pkg_resources import resource_stream, Requirement
import six
import numpy as np
import pandas as pd
try:
    BOKEH_AVAILABLE = True
    import bokeh.io as bio
    import bokeh.plotting as bp
except ImportError:
    BOKEH_AVAILABLE = False


STATS_COLUMNS = ['expanded_income', 'c00100', 'aftertax_income', 'standard',
                 'c04470', 'c04600', 'c04800', 'taxbc', 'c62100', 'c09600',
                 'c05800', 'othertaxes', 'refund', 'c07100', 'iitax',
                 'payrolltax', 'combined', 's006']

# Items in the TABLE_COLUMNS list below correspond to the items in the
# TABLE_LABELS list below; this correspondence allows us to use TABLE_LABELS
# to map a label to the correct column in our distribution tables.
TABLE_COLUMNS = ['s006', 'c00100', 'num_returns_StandardDed', 'standard',
                 'num_returns_ItemDed', 'c04470', 'c04600', 'c04800', 'taxbc',
                 'c62100', 'num_returns_AMT', 'c09600', 'c05800', 'c07100',
                 'othertaxes', 'refund', 'iitax', 'payrolltax', 'combined']

TABLE_LABELS = ['Returns', 'AGI', 'Standard Deduction Filers',
                'Standard Deduction', 'Itemizers',
                'Itemized Deduction', 'Personal Exemption',
                'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers', 'AMT',
                'Tax before Credits', 'Non-refundable Credits',
                'Other Taxes', 'Refundable Credits',
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
    expinc = 'expanded_income'
    return (float((pdf[col_name] * pdf[swght] * pdf[expinc]).sum()) /
            float((pdf[swght] * pdf[expinc]).sum() + EPSILON))


def unweighted_sum(pdf, col_name):
    """
    Return unweighted sum of Pandas DataFrame col_name items.
    """
    return pdf[col_name].sum()


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


def add_weighted_income_bins(pdf, num_bins=10, labels=None,
                             income_measure='expanded_income',
                             weight_by_income_measure=False):
    """
    Add a column of income bins to specified Pandas DataFrame, pdf, with
    the new column being named 'bins'.  Assumes that specified pdf contains
    columns for the specified income_measure and for sample weights, s006.
    """
    pdf.sort_values(by=income_measure, inplace=True)
    if weight_by_income_measure:
        pdf['cumsum_temp'] = np.cumsum(np.multiply(pdf[income_measure].values,
                                                   pdf['s006'].values))
    else:
        pdf['cumsum_temp'] = np.cumsum(pdf['s006'].values)
    max_cumsum = pdf['cumsum_temp'].values[-1]
    bin_edges = [0] + list(np.arange(1, (num_bins + 1)) *
                           (max_cumsum / float(num_bins)))
    if not labels:
        labels = range(1, (num_bins + 1))
    pdf['bins'] = pd.cut(pdf['cumsum_temp'], bins=bin_edges, labels=labels)
    pdf.drop('cumsum_temp', axis=1, inplace=True)
    return pdf


def add_income_bins(pdf, compare_with='soi', bins=None, right=True,
                    income_measure='expanded_income'):
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


def means_and_comparisons(col_name, gpdf, weighted_total):
    """
    Return new Pandas DataFrame based on grouped values of specified
    col_name in specified gpdf Pandas DataFrame.
    col_name: the column name to calculate against
    gpdf: grouped Pandas DataFrame
    """
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


def weighted_avg_allcols(pdf, col_list, income_measure='expanded_income'):
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
    pdf['c04470'] = pdf['c04470'].where(
        ((pdf['c00100'] > 0.) & (pdf['c04470'] > pdf['standard'])), 0.)
    # weight of returns with positive AGI and itemized deduction
    pdf['num_returns_ItemDed'] = pdf['s006'].where(
        ((pdf['c00100'] > 0.) & (pdf['c04470'] > 0.)), 0.)
    # weight of returns with positive AGI and standard deduction
    pdf['num_returns_StandardDed'] = pdf['s006'].where(
        ((pdf['c00100'] > 0.) & (pdf['standard'] > 0.)), 0.)
    # weight of returns with positive Alternative Minimum Tax (AMT)
    pdf['num_returns_AMT'] = pdf['s006'].where(pdf['c09600'] > 0., 0.)
    return pdf


def create_distribution_table(obj, groupby, result_type,
                              income_measure='expanded_income',
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
        pdf = add_weighted_income_bins(res, num_bins=10,
                                       income_measure=income_measure)
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
                            income_measure='expanded_income',
                            income_to_present='iitax'):
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
        options for input: 'expanded_income', 'iitax'
        classifier of income bins/deciles

    income_to_present : String object
        options for input: 'iitax', 'payrolltax', 'combined'

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
    res2['aftertax_baseline'] = res1['aftertax_income']
    income_measure = baseline_income_measure
    if groupby == 'weighted_deciles':
        pdf = add_weighted_income_bins(res2, num_bins=10,
                                       income_measure=income_measure)
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
    res2['aftertax_perc'] = res2['tax_diff'] / res2['aftertax_baseline']
    diffs = means_and_comparisons('tax_diff',
                                  pdf.groupby('bins', as_index=False),
                                  (res2['tax_diff'] * res2['s006']).sum())
    aftertax_perc = pdf.groupby('bins', as_index=False).apply(weighted_mean,
                                                              'aftertax_perc')
    diffs['aftertax_perc'] = aftertax_perc
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
    srs_aftertax_perc = ['{0:.2f}%'.format(val * 100)
                         for val in diffs['aftertax_perc']]
    diffs['aftertax_perc'] = pd.Series(srs_aftertax_perc, index=diffs.index)
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
    num = recs.s006[(recs.standard > 0.) * (recs.c00100 > 0.)].sum()
    odict['Standard Deduction Filers (#m)'] = num * in_millions
    # standard deduction
    sded1 = recs.standard * recs.s006
    val = sded1[(recs.standard > 0.) * (recs.c00100 > 0.)].sum()
    odict['Standard Deduction ($b)'] = val * in_billions
    # personal exemption
    val = (recs.c04600 * recs.s006)[recs.c00100 > 0.].sum()
    odict['Personal Exemption ($b)'] = val * in_billions
    # taxable income
    val = (recs.c04800 * recs.s006).sum()
    odict['Taxable Income ($b)'] = val * in_billions
    # regular tax liability
    val = (recs.taxbc * recs.s006).sum()
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
    val = (recs.refund * recs.s006).sum()
    odict['Refundable Credits ($b)'] = val * in_billions
    # nonrefundable credits
    val = (recs.c07100 * recs.s006).sum()
    odict['Nonrefundable Credits ($b)'] = val * in_billions
    # reform surtaxes (part of federal individual income tax liability)
    val = (recs.surtax * recs.s006).sum()
    odict['Reform Surtaxes ($b)'] = val * in_billions
    # other taxes on Form 1040
    val = (recs.othertaxes * recs.s006).sum()
    odict['Other Taxes ($b)'] = val * in_billions
    # federal individual income tax liability
    val = (recs.iitax * recs.s006).sum()
    odict['Ind Income Tax ($b)'] = val * in_billions
    # OASDI+HI payroll tax liability (including employer share)
    val = (recs.payrolltax * recs.s006).sum()
    odict['Payroll Taxes ($b)'] = val * in_billions
    # combined income and payroll tax liability
    val = (recs.combined * recs.s006).sum()
    odict['Combined Liability ($b)'] = val * in_billions
    # number of tax units with non-positive income tax liability
    num = (recs.s006[recs.iitax <= 0]).sum()
    odict['With Income Tax <= 0 (#m)'] = num * in_millions
    # number of tax units with non-positive combined tax liability
    num = (recs.s006[recs.combined <= 0]).sum()
    odict['With Combined Tax <= 0 (#m)'] = num * in_millions
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
        recids = map(pdf_recid, recids)
        pdf = pdf.ix[recids]  # pylint: disable=no-member
    # do transposition
    out = pdf.T.reset_index()  # pylint: disable=no-member
    # format data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)
    # write ascii output to specified ascii_filename
    out.to_csv(ascii_filename, header=False, index=False, sep='\t')


def mtr_graph_data(calc1, calc2,
                   mars='ALL',
                   mtr_measure='combined',
                   mtr_variable='e00200p',
                   alt_e00200p_text='',
                   mtr_wrt_full_compen=False,
                   income_measure='expanded_income',
                   dollar_weighting=False):
    """
    Prepare marginal tax rate data needed by xtr_graph_plot utility function.

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

    alt_e00200p_text : string
        text to use in place of mtr_variable when mtr_variable is 'e00200p';
        if empty string then use 'e00200p'

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
    dictionary object suitable for passing to xtr_graph_plot utility function
    """
    # pylint: disable=too-many-arguments,too-many-statements,
    # pylint: disable=too-many-locals,too-many-branches
    # check that two calculator objects have the same current_year
    if calc1.current_year == calc2.current_year:
        year = calc1.current_year
    else:
        msg = 'calc1.current_year={} != calc2.current_year={}'
        raise ValueError(msg.format(calc1.current_year, calc2.current_year))
    # check validity of function arguments
    # . . check income_measure value
    weighting_function = weighted_mean
    if income_measure == 'wages':
        income_var = 'e00200'
        income_str = 'Wage'
        if dollar_weighting:
            weighting_function = wage_weighted
    elif income_measure == 'agi':
        income_var = 'c00100'
        income_str = 'AGI'
        if dollar_weighting:
            weighting_function = agi_weighted
    elif income_measure == 'expanded_income':
        income_var = 'expanded_income'
        income_str = 'Expanded Income'
        if dollar_weighting:
            weighting_function = expanded_income_weighted
    else:
        msg = ('income_measure="{}" is neither '
               '"wages", "agi", nor "expanded_income"')
        raise ValueError(msg.format(income_measure))
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
    # . . check mars value if mtr_variable is e00200s
    if mtr_variable == 'e00200s' and mars != 2:
        msg = 'mtr_variable == "e00200s" but mars != 2'
        raise ValueError(msg)
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
    # calculate marginal tax rates
    (mtr1_ptax, mtr1_itax,
     mtr1_combined) = calc1.mtr(variable_str=mtr_variable,
                                wrt_full_compensation=mtr_wrt_full_compen)
    (mtr2_ptax, mtr2_itax,
     mtr2_combined) = calc2.mtr(variable_str=mtr_variable,
                                wrt_full_compensation=mtr_wrt_full_compen)
    # extract needed output that is assumed unchanged by reform from calc1
    record_columns = ['s006']
    if mars != 'ALL':
        record_columns.append('MARS')
    record_columns.append(income_var)
    output = [getattr(calc1.records, col) for col in record_columns]
    dfx = pd.DataFrame(data=np.column_stack(output), columns=record_columns)
    # set mtr given specified mtr_measure
    if mtr_measure == 'itax':
        dfx['mtr1'] = mtr1_itax
        dfx['mtr2'] = mtr2_itax
    elif mtr_measure == 'ptax':
        dfx['mtr1'] = mtr1_ptax
        dfx['mtr2'] = mtr2_ptax
    elif mtr_measure == 'combined':
        dfx['mtr1'] = mtr1_combined
        dfx['mtr2'] = mtr2_combined
    # select filing-status subgroup, if any
    if mars != 'ALL':
        dfx = dfx[dfx['MARS'] == mars]
    # create 'bins' column given specified income_var and dollar_weighting
    dfx = add_weighted_income_bins(dfx, num_bins=100,
                                   income_measure=income_var,
                                   weight_by_income_measure=dollar_weighting)
    # split dfx into groups specified by 'bins' column
    gdfx = dfx.groupby('bins', as_index=False)
    # apply the weighting_function to percentile-grouped mtr values
    mtr1_series = gdfx.apply(weighting_function, 'mtr1')
    mtr2_series = gdfx.apply(weighting_function, 'mtr2')
    # construct DataFrame containing the two mtr?_series
    lines = pd.DataFrame()
    lines['base'] = mtr1_series
    lines['reform'] = mtr2_series
    # construct dictionary containing merged data and auto-generated labels
    data = dict()
    data['lines'] = lines
    if dollar_weighting:
        income_str = 'Dollar-weighted {}'.format(income_str)
        mtr_str = 'Dollar-weighted {}'.format(mtr_str)
    data['ylabel'] = '{} MTR'.format(mtr_str)
    xlabel_str = '{} Percentile'.format(income_str)
    if mars != 'ALL':
        xlabel_str = '{} for MARS={}'.format(xlabel_str, mars)
    data['xlabel'] = xlabel_str
    var_str = '{}'.format(mtr_variable)
    if mtr_variable == 'e00200p' and alt_e00200p_text != '':
        var_str = '{}'.format(alt_e00200p_text)
    if mtr_variable == 'e00200p' and mtr_wrt_full_compen:
        var_str = '{} wrt full compensation'.format(var_str)
    title_str = 'Mean Marginal Tax Rate for {} by Income Percentile'
    title_str = title_str.format(var_str)
    if mars != 'ALL':
        title_str = '{} for MARS={}'.format(title_str, mars)
    title_str = '{} for {}'.format(title_str, year)
    data['title'] = title_str
    return data


def atr_graph_data(calc1, calc2,
                   mars='ALL',
                   atr_measure='combined',
                   min_avginc=1000):
    """
    Prepare average tax rate data needed by xtr_graph_plot utility function.

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

    atr_measure : string
        options:
            'itax': average individual income tax rate;
            'ptax': average payroll tax rate; and
            'combined': sum of average income and payroll tax rates.
        specifies which average tax rate to show on graph's y axis

    min_avginc : float
        specifies the minimum average expanded income for a percentile to
        be included in the graph data; value must be positive

    Returns
    -------
    dictionary object suitable for passing to xtr_graph_plot utility function
    """
    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    # check that two calculator objects have the same current_year
    if calc1.current_year == calc2.current_year:
        year = calc1.current_year
    else:
        msg = 'calc1.current_year={} != calc2.current_year={}'
        raise ValueError(msg.format(calc1.current_year, calc2.current_year))
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
    # . . check atr_measure value
    if atr_measure == 'itax':
        atr_str = 'Income-Tax'
    elif atr_measure == 'ptax':
        atr_str = 'Payroll-Tax'
    elif atr_measure == 'combined':
        atr_str = 'Income+Payroll-Tax'
    else:
        msg = ('atr_measure="{}" is neither '
               '"itax" nor "ptax" nor "combined"')
        raise ValueError(msg.format(atr_measure))
    # . . check min_avginc value
    assert min_avginc > 0.
    # calculate taxes and expanded income
    calc1.calc_all()
    calc2.calc_all()
    # extract needed output that is assumed unchanged by reform from calc1
    record_columns = ['s006']
    if mars != 'ALL':
        record_columns.append('MARS')
    record_columns.append('expanded_income')
    output = [getattr(calc1.records, col) for col in record_columns]
    dfx = pd.DataFrame(data=np.column_stack(output), columns=record_columns)
    # create 'tax1' and 'tax2' columns given specified atr_measure
    if atr_measure == 'itax':
        dfx['tax1'] = calc1.records.iitax
        dfx['tax2'] = calc2.records.iitax
    elif atr_measure == 'ptax':
        dfx['tax1'] = calc1.records.payrolltax
        dfx['tax2'] = calc2.records.payrolltax
    elif atr_measure == 'combined':
        dfx['tax1'] = calc1.records.combined
        dfx['tax2'] = calc2.records.combined
    # select filing-status subgroup, if any
    if mars != 'ALL':
        dfx = dfx[dfx['MARS'] == mars]
    # create 'bins' column
    dfx = add_weighted_income_bins(dfx, num_bins=100,
                                   income_measure='expanded_income')
    # split dfx into groups specified by 'bins' column
    gdfx = dfx.groupby('bins', as_index=False)
    # apply weighted_mean function to percentile-grouped income/tax values
    avginc_series = gdfx.apply(weighted_mean, 'expanded_income')
    avgtax1_series = gdfx.apply(weighted_mean, 'tax1')
    avgtax2_series = gdfx.apply(weighted_mean, 'tax2')
    # compute average tax rates for each included income percentile
    included = np.array(avginc_series >= min_avginc, dtype=bool)
    atr1_series = np.zeros_like(avginc_series)
    atr1_series[included] = avgtax1_series[included] / avginc_series[included]
    atr2_series = np.zeros_like(avginc_series)
    atr2_series[included] = avgtax2_series[included] / avginc_series[included]
    # construct DataFrame containing the two atr?_series
    lines = pd.DataFrame()
    lines['base'] = atr1_series
    lines['reform'] = atr2_series
    # include only percentiles with average income no less than min_avginc
    lines = lines[included]
    # construct dictionary containing plot lines and auto-generated labels
    data = dict()
    data['lines'] = lines
    data['ylabel'] = '{} Average Tax Rate'.format(atr_str)
    xlabel_str = 'Expanded Income Percentile'
    if mars != 'ALL':
        xlabel_str = '{} for MARS={}'.format(xlabel_str, mars)
    data['xlabel'] = xlabel_str
    title_str = 'Average Tax Rate by Income Percentile'
    if mars != 'ALL':
        title_str = '{} for MARS={}'.format(title_str, mars)
    title_str = '{} for {}'.format(title_str, year)
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
            msg = "install graphing package using `conda install bokeh`"
            raise RuntimeError(msg)
    return wrapped_f


@requires_bokeh
def xtr_graph_plot(data,
                   width=850,
                   height=500,
                   xlabel='',
                   ylabel='',
                   title='',
                   legendloc='bottom_right'):
    """
    Plot marginal/average tax rate graph using data returned from either the
    mtr_graph_data function or the atr_graph_data function.

    Parameters
    ----------
    data : dictionary object returned from ?tr_graph_data() utility function

    width : integer
        width of plot expressed in pixels

    height : integer
        height of plot expressed in pixels

    xlabel : string
        x-axis label; if '', then use label generated by ?tr_graph_data

    ylabel : string
        y-axis label; if '', then use label generated by ?tr_graph_data

    title : string
        graph title; if '', then use title generated by ?tr_graph_data

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
      gplot = xtr_graph_plot(gdata)
    THEN  # when working interactively in a Python notebook
      bp.show(gplot)
    OR    # when executing script using Python command-line interpreter
      bio.output_file('graph-name.html', title='?TR by Income Percentile')
      bio.show(gplot)  [OR bio.save(gplot) WILL JUST WRITE FILE TO DISK]
    WILL VISUALIZE GRAPH IN BROWSER AND WRITE GRAPH TO SPECIFIED HTML FILE

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
    fig.line(lines.index, lines.base, line_color='blue', legend='Base')
    fig.line(lines.index, lines.reform, line_color='red', legend='Reform')
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


@requires_bokeh
def write_graph_file(figure, filename, title):
    """
    Write HTML file named filename containing figure.
    The title is the text displayed in the browser tab.

    Parameters
    ----------
    figure : bokeh.plotting figure object

    filename : string
        name of HTML file to which figure is written; should end in .html

    title : string
        text displayed in browser tab when HTML file is displayed in browser

    Returns
    -------
    Nothing
    """
    delete_file(filename)    # work around annoying 'already exists' bokeh msg
    bio.output_file(filename=filename, title=title)
    bio.save(figure)


def read_json_from_file(path):
    """
    Return a dict of data loaded from the json file stored at path.
    """
    with open(path, 'r') as rfile:
        data = json.load(rfile)
    return data


def write_json_to_file(data, path, indent=4, sort_keys=False):
    """
    Write data to a file at path in json format.
    """
    with open(path, 'w') as wfile:
        json.dump(data, wfile, indent=indent, sort_keys=sort_keys)


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


def isoelastic_utility_function(consumption, crra, cmin):
    """
    Calculate and return utility of consumption.

    Parameters
    ----------
    consumption : float
      consumption for a filing unit

    crra : non-negative float
      constant relative risk aversion parameter

    cmin : positive float
      consumption level below which marginal utility is assumed to be constant

    Returns
    -------
    utility of consumption
    """
    if consumption >= cmin:
        if crra == 1.0:
            return math.log(consumption)
        else:
            return math.pow(consumption, (1.0 - crra)) / (1.0 - crra)
    else:  # if consumption < cmin
        if crra == 1.0:
            tu_at_cmin = math.log(cmin)
        else:
            tu_at_cmin = math.pow(cmin, (1.0 - crra)) / (1.0 - crra)
        mu_at_cmin = math.pow(cmin, -crra)
        tu_at_c = tu_at_cmin + mu_at_cmin * (consumption - cmin)
        return tu_at_c


def expected_utility(consumption, probability, crra, cmin):
    """
    Calculate and return expected utility of consumption.

    Parameters
    ----------
    consumption : numpy array
      consumption for each filing unit

    probability : numpy array
      samplying probability of each filing unit

    crra : non-negative float
      constant relative risk aversion parameter of isoelastic utility function

    cmin : positive float
      consumption level below which marginal utility is assumed to be constant

    Returns
    -------
    expected utility of consumption array
    """
    utility = consumption.apply(isoelastic_utility_function,
                                args=(crra, cmin,))
    return np.inner(utility, probability)


def certainty_equivalent(exputil, crra, cmin):
    """
    Calculate and return certainty-equivalent of exputil of consumption
    assuming an isoelastic utility function with crra and cmin as parameters.

    Parameters
    ----------
    exputil : float
      expected utility value

    crra : non-negative float
      constant relative risk aversion parameter of isoelastic utility function

    cmin : positive float
      consumption level below which marginal utility is assumed to be constant

    Returns
    -------
    certainty-equivalent of specified expected utility, exputil
    """
    if crra == 1.0:
        tu_at_cmin = math.log(cmin)
    else:
        tu_at_cmin = math.pow(cmin, (1.0 - crra)) / (1.0 - crra)
    if exputil >= tu_at_cmin:
        if crra == 1.0:
            return math.exp(exputil)
        else:
            return math.pow((exputil * (1.0 - crra)), (1.0 / (1.0 - crra)))
    else:
        mu_at_cmin = math.pow(cmin, -crra)
        return ((exputil - tu_at_cmin) / mu_at_cmin) + cmin


def ce_aftertax_income(calc1, calc2,
                       custom_params=None,
                       require_no_agg_tax_change=True):
    """
    Return dictionary that contains certainty-equivalent of the expected
    utility of after-tax income computed for constant-relative-risk-aversion
    parameter values for each of two Calculator objects: calc1, which
    represents the pre-reform situation, and calc2, which represents the
    post-reform situation, both of which MUST have had calc_call() called
    before being passed to this function.

    IMPORTANT NOTES: These normative welfare calculations are very simple.
    It is assumed that utility is a function of only consumption, and that
    consumption is equal to after-tax income.  This means that any assumed
    behavioral responses that change work effort will not affect utility via
    the correpsonding change in leisure.  And any saving response to changes
    in after-tax income do not affect consumption.
    """
    # pylint: disable=too-many-locals
    # ... check that calc1 and calc2 are consistent
    assert calc1.records.dim == calc2.records.dim
    assert calc1.current_year == calc2.current_year
    # ... specify utility function parameters
    if custom_params:
        crras = custom_params['crra_list']
        for crra in crras:
            assert crra >= 0
        cmin = custom_params['cmin_value']
        assert cmin > 0
    else:
        crras = [0, 1, 2, 3, 4]
        cmin = 1000
    # The cmin value is the consumption level below which marginal utility
    # is considered to be constant.  This allows the handling of filing units
    # with very low or even negative after-tax income in the expected-utility
    # and certainty-equivalent calculations.
    # ... extract calc_all() data from calc1 and calc2
    record_columns = ['s006', 'payrolltax', 'iitax',
                      'combined', 'expanded_income']
    out = [getattr(calc1.records, col) for col in record_columns]
    df1 = pd.DataFrame(data=np.column_stack(out), columns=record_columns)
    out = [getattr(calc2.records, col) for col in record_columns]
    df2 = pd.DataFrame(data=np.column_stack(out), columns=record_columns)
    # ... compute aggregate combined tax revenue and aggregate after-tax income
    billion = 1.0e-9
    cedict = dict()
    cedict['year'] = calc1.current_year
    cedict['tax1'] = weighted_sum(df1, 'combined') * billion
    cedict['tax2'] = weighted_sum(df2, 'combined') * billion
    if require_no_agg_tax_change:
        diff = cedict['tax2'] - cedict['tax1']
        if abs(diff) >= 0.0005:
            msg = 'Aggregate taxes not equal when required_... arg is True:'
            msg += '\n            taxes1= {:9.3f}'
            msg += '\n            taxes2= {:9.3f}'
            msg += '\n            txdiff= {:9.3f}'
            msg += ('\n(adjust _LST or other parameter to bracket txdiff=0 '
                    'and then interpolate)')
            raise ValueError(msg.format(cedict['tax1'], cedict['tax2'], diff))
    cedict['inc1'] = weighted_sum(df1, 'expanded_income') * billion
    cedict['inc2'] = weighted_sum(df2, 'expanded_income') * billion
    # ... calculate sample-weighted probability of each filing unit
    # pylint: disable=no-member
    # (above pylint comment eliminates bogus np.divide warnings)
    prob_raw = np.divide(df1['s006'], df1['s006'].sum())
    prob = np.divide(prob_raw, prob_raw.sum())  # handle any rounding error
    # ... calculate after-tax income of each filing unit in calc1 and calc2
    ati1 = df1['expanded_income'] - df1['combined']
    ati2 = df2['expanded_income'] - df2['combined']
    # ... calculate certainty-equivaluent after-tax income in calc1 and calc2
    cedict['crra'] = crras
    ce1 = list()
    ce2 = list()
    for crra in crras:
        eu1 = expected_utility(ati1, prob, crra, cmin)
        ce1.append(certainty_equivalent(eu1, crra, cmin))
        eu2 = expected_utility(ati2, prob, crra, cmin)
        ce2.append(certainty_equivalent(eu2, crra, cmin))
    cedict['ceeu1'] = ce1
    cedict['ceeu2'] = ce2
    # ... return cedict
    return cedict


def read_egg_csv(fname, **kwargs):
    """
    Read from egg the file named fname that contains CSV data and
    return pandas DataFrame containing the data.
    """
    try:
        path_in_egg = os.path.join('taxcalc', fname)
        vdf = pd.read_csv(resource_stream(Requirement.parse('taxcalc'),
                                          path_in_egg), **kwargs)
    except:
        raise ValueError('could not read {} data from egg'.format(fname))
    return vdf


def read_egg_json(fname):
    """
    Read from egg the file named fname that contains JSON data and
    return dictionary containing the data.
    """
    try:
        path_in_egg = os.path.join('taxcalc', fname)
        pdict = json.loads(resource_stream(Requirement.parse('taxcalc'),
                                           path_in_egg).read().decode('utf-8'),
                           object_pairs_hook=OrderedDict)
    except:
        raise ValueError('could not read {} data from egg'.format(fname))
    return pdict


def temporary_filename(suffix=''):
    """
    Return string containing filename.
    """
    return 'tmp{}{}'.format(random.randint(10000000, 99999999), suffix)


def delete_file(filename):
    """
    Remove specified file if it exists.
    """
    if os.path.isfile(filename):
        os.remove(filename)
