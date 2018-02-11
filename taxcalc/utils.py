"""
PUBLIC low-level utility functions for Tax-Calculator.
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
import collections
import pkg_resources
import six
import numpy as np
import pandas as pd
import bokeh.io as bio
import bokeh.plotting as bp
from bokeh.models import PrintfTickFormatter
from taxcalc.utilsprvt import (weighted_count_lt_zero,
                               weighted_count_gt_zero,
                               weighted_count, weighted_mean,
                               wage_weighted, agi_weighted,
                               expanded_income_weighted,
                               weighted_perc_inc, weighted_perc_cut,
                               EPSILON)


# Items in the DIST_TABLE_COLUMNS list below correspond to the items in the
# DIST_TABLE_LABELS list below; this correspondence allows us to use this
# labels list to map a label to the correct column in a distribution table.

DIST_VARIABLES = ['expanded_income', 'c00100', 'aftertax_income', 'standard',
                  'c04470', 'c04600', 'c04800', 'taxbc', 'c62100', 'c09600',
                  'c05800', 'othertaxes', 'refund', 'c07100', 'surtax',
                  'iitax', 'payrolltax', 'combined', 's006']

DIST_TABLE_COLUMNS = ['s006',
                      'c00100',
                      'num_returns_StandardDed',
                      'standard',
                      'num_returns_ItemDed',
                      'c04470',
                      'c04600',
                      'c04800',
                      'taxbc',
                      'c62100',
                      'num_returns_AMT',
                      'c09600',
                      'c05800',
                      'c07100',
                      'othertaxes',
                      'refund',
                      'iitax',
                      'payrolltax',
                      'combined',
                      'expanded_income',
                      'aftertax_income']

DIST_TABLE_LABELS = ['Returns',
                     'AGI',
                     'Standard Deduction Filers',
                     'Standard Deduction',
                     'Itemizers',
                     'Itemized Deduction',
                     'Personal Exemption',
                     'Taxable Income',
                     'Regular Tax',
                     'AMTI',
                     'AMT Filers',
                     'AMT',
                     'Tax before Credits',
                     'Non-refundable Credits',
                     'Other Taxes',
                     'Refundable Credits',
                     'Individual Income Tax Liabilities',
                     'Payroll Tax Liablities',
                     'Combined Payroll and Individual Income Tax Liabilities',
                     'Expanded Income',
                     'After-Tax Expanded Income']

# Items in the DIFF_TABLE_COLUMNS list below correspond to the items in the
# DIFF_TABLE_LABELS list below; this correspondence allows us to use this
# labels list to map a label to the correct column in a difference table.

DIFF_VARIABLES = ['expanded_income', 'c00100', 'aftertax_income',
                  'iitax', 'payrolltax', 'combined', 's006']

DIFF_TABLE_COLUMNS = ['count',
                      'tax_cut',
                      'perc_cut',
                      'tax_inc',
                      'perc_inc',
                      'mean',
                      'tot_change',
                      'share_of_change',
                      'perc_aftertax',
                      'pc_aftertaxinc']

DIFF_TABLE_LABELS = ['All Tax Units',
                     'Tax Units with Tax Cut',
                     'Percent with Tax Cut',
                     'Tax Units with Tax Increase',
                     'Percent with Tax Increase',
                     'Average Tax Change',
                     'Total Tax Difference',
                     'Share of Overall Change',
                     'Change as % of After-Tax Income',
                     '% Change in After-Tax Income']

DECILE_ROW_NAMES = ['0-10', '10-20', '20-30', '30-40', '40-50',
                    '50-60', '60-70', '70-80', '80-90', '90-100',
                    'all',
                    '90-95', '95-99', 'Top 1%']

WEBAPP_INCOME_BINS = [-9e99, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                      199999, 499999, 1000000, 9e99]

WEBBIN_ROW_NAMES = ['<$10K', '$10-20K', '$20-30K', '$30-40K',
                    '$40-50K', '$50-75K', '$75-100K',
                    '$100-200K', '$200-500K',
                    '$500-1000K', '>$1000K', 'all']

LARGE_INCOME_BINS = [-9e99, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
                     200000, 9e99]

SMALL_INCOME_BINS = [-9e99, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
                     49999, 74999, 99999, 199999, 499999, 999999, 1499999,
                     1999999, 4999999, 9999999, 9e99]


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


def add_quantile_bins(pdf, income_measure, num_bins,
                      weight_by_income_measure=False, labels=None):
    """
    Add a column of income bins to specified Pandas DataFrame, pdf, with
    the new column being named 'bins'.  The bins hold equal number of
    filing units when weight_by_income_measure=False or equal number of
    income dollars when weight_by_income_measure=True.  Assumes that
    specified pdf contains columns for the specified income_measure and
    for sample weights, s006.
    """
    pdf.sort_values(by=income_measure, inplace=True)
    if weight_by_income_measure:
        pdf['cumsum_temp'] = np.cumsum(np.multiply(pdf[income_measure].values,
                                                   pdf['s006'].values))
        min_cumsum = pdf['cumsum_temp'].values[0]
    else:
        pdf['cumsum_temp'] = np.cumsum(pdf['s006'].values)
        min_cumsum = 0.  # because s006 values are non-negative
    max_cumsum = pdf['cumsum_temp'].values[-1]
    cumsum_range = max_cumsum - min_cumsum
    bin_width = cumsum_range / float(num_bins)
    bin_edges = list(min_cumsum + np.arange(0, (num_bins + 1)) * bin_width)
    bin_edges[-1] = 9e99  # raise top of last bin to include all observations
    bin_edges[0] = -9e99  # lower bottom of 1st bin to include all observations
    if not labels:
        labels = range(1, (num_bins + 1))
    pdf['bins'] = pd.cut(pdf['cumsum_temp'], bins=bin_edges, labels=labels)
    pdf.drop('cumsum_temp', axis=1, inplace=True)
    return pdf


def add_income_bins(pdf, income_measure,
                    bin_type='soi', bins=None, right=True):
    """
    Add a column of income bins of income_measure using Pandas 'cut' function.

    Parameters
    ----------
    pdf: Pandas DataFrame
        the object to which we are adding bins

    income_measure: String
        specifies income variable used to construct bins

    bin_type: String, optional
        options for input: 'webapp', 'tpc', 'soi'
        default: 'soi'

    bins: iterable of scalars, optional income breakpoints
        follows Pandas convention; the breakpoint is inclusive if
        right=True; this argument overrides the compare_with argument

    right : bool, optional
        indicates whether the bins include the rightmost edge or not;
        if right == True (the default), then bins=[1,2,3,4] implies
        this bin grouping (1,2], (2,3], (3,4]

    Returns
    -------
    pdf: Pandas DataFrame
        the original input plus the added 'bin' column
    """
    if not bins:
        if bin_type == 'webapp':
            bins = WEBAPP_INCOME_BINS
        elif bin_type == 'tpc':
            bins = LARGE_INCOME_BINS
        elif bin_type == 'soi':
            bins = SMALL_INCOME_BINS
        else:
            msg = 'Unknown bin_type argument {}'.format(bin_type)
            raise ValueError(msg)
    pdf['bins'] = pd.cut(pdf[income_measure], bins, right=right)
    return pdf


def get_sums(pdf):
    """
    Compute unweighted sum of items in each column of Pandas DataFrame, pdf.

    Returns
    -------
    Pandas Series object containing column sums indexed by pdf column names.
    """
    sums = dict()
    for col in pdf.columns.values.tolist():
        if col != 'bins':
            sums[col] = pdf[col].sum()
    return pd.Series(sums, name='sums')


def create_distribution_table(vdf, groupby, income_measure, result_type):
    """
    Get results from vdf, sort them based on groupby using income_measure,
    manipulate them based on result_type, and return them as a table.

    Parameters
    ----------
    vdf : Pandas DataFrame including columns named as in STATS_VARIABLES list
        for example, object returned from Calculator dataframe method in a
        call like this: vdf = calc.dataframe(STATS_VARIABLES)

    groupby : String object
        options for input: 'weighted_deciles', 'webapp_income_bins',
                           'large_income_bins', 'small_income_bins';
        determines how the columns in the resulting Pandas DataFrame are sorted
    NOTE: when groupby is 'weighted_deciles', the returned table has three
          extra rows containing top-decile detail consisting of statistics
          for the 0.90-0.95 quantile range (bottom half of top decile),
          for the 0.95-0.99 quantile range, and
          for the 0.99-1.00 quantile range (top one percent).

    result_type : String object
        options for input: 'weighted_sum' or 'weighted_avg';
        determines how the data should be manipulated

    income_measure : String object
        options for input: 'expanded_income', 'c00100'(AGI),
                           'expanded_income_baseline', 'c00100_baseline'

    Notes
    -----
    Taxpayer Characteristics:
        c04470 : Total itemized deduction

        c00100 : AGI (Defecit)

        c09600 : Alternative minimum tax

        s006 : filing unit sample weight

    Returns
    -------
    distribution table as a Pandas DataFrame, with DIST_TABLE_COLUMNS and
    groupby rows, where the rows run from lowest bin/decile to the highest
    followed by a sums row with the top-decile detail in an additional three
    rows following the sums row
    """
    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    # nested function that specifies calculated columns
    def add_columns(pdf):
        """
        Nested function that adds several columns to
        the specified Pandas DataFrame, pdf.
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

    # nested function that specifies calculated columns
    def stat_dataframe(gpdf):
        """
        Nested function that returns statistics DataFrame derived from the
        specified grouped Dataframe object, gpdf.
        """
        unweighted_columns = ['s006', 'num_returns_StandardDed',
                              'num_returns_ItemDed', 'num_returns_AMT']
        stats = list()
        for col in DIST_TABLE_COLUMNS:
            if col in unweighted_columns:
                stats.append(gpdf.apply(unweighted_sum, col))
            else:
                stats.append(gpdf.apply(weighted_sum, col))
        sdf = pd.DataFrame(data=np.column_stack(stats),
                           columns=DIST_TABLE_COLUMNS)
        return sdf

    # main logic of create_distribution_table
    assert isinstance(vdf, pd.DataFrame)
    assert (groupby == 'weighted_deciles' or
            groupby == 'webapp_income_bins' or
            groupby == 'large_income_bins' or
            groupby == 'small_income_bins')
    assert result_type == 'weighted_sum' or result_type == 'weighted_avg'
    assert (income_measure == 'expanded_income' or
            income_measure == 'expanded_income_baseline' or
            income_measure == 'c00100' or
            income_measure == 'c00100_baseline')
    assert income_measure in vdf
    # copy vdf and add variable columns
    res = copy.deepcopy(vdf)
    res = add_columns(res)
    # sort the data given specified groupby and income_measure
    if groupby == 'weighted_deciles':
        pdf = add_quantile_bins(res, income_measure, 10)
    elif groupby == 'webapp_income_bins':
        pdf = add_income_bins(res, income_measure, bin_type='webapp')
    elif groupby == 'large_income_bins':
        pdf = add_income_bins(res, income_measure, bin_type='tpc')
    elif groupby == 'small_income_bins':
        pdf = add_income_bins(res, income_measure, bin_type='soi')
    # construct weighted_sum table
    gpdf = pdf.groupby('bins', as_index=False)
    dist_table = stat_dataframe(gpdf)
    # append sum row
    row = get_sums(dist_table)[dist_table.columns]
    dist_table = dist_table.append(row)
    # append top-decile-detail rows
    if groupby == 'weighted_deciles':
        pdf = gpdf.get_group(10)  # top decile as its own DataFrame
        pdf = add_quantile_bins(copy.deepcopy(pdf), income_measure, 10)
        pdf['bins'].replace(to_replace=[1, 2, 3, 4, 5],
                            value=[0, 0, 0, 0, 0], inplace=True)
        pdf['bins'].replace(to_replace=[6, 7, 8, 9],
                            value=[1, 1, 1, 1], inplace=True)
        pdf['bins'].replace(to_replace=[10], value=[2], inplace=True)
        gpdf = pdf.groupby('bins', as_index=False)
        rows = stat_dataframe(gpdf)
        dist_table = dist_table.append(rows, ignore_index=True)
    # optionally construct weighted_avg table
    if result_type == 'weighted_avg':
        for col in DIST_TABLE_COLUMNS:
            if col != 's006':
                dist_table[col] /= dist_table['s006']
    # set print display format for float table elements
    pd.options.display.float_format = '{:8,.0f}'.format
    # ensure dist_table columns are in correct order
    assert dist_table.columns.values.tolist() == DIST_TABLE_COLUMNS
    return dist_table


def create_difference_table(vdf1, vdf2, groupby, income_measure, tax_to_diff):
    """
    Get results from two different vdf, construct tax difference results,
    and return the difference statistics as a table.

    Parameters
    ----------
    vdf1 : Pandas DataFrame object including columns in the DIFF_VARIABLES
           list drawn from a baseline Calculator object using the
           Calculator.dataframe method

    vdf2 : Pandas DataFrame object including columns in the DIFF_VARIABLES
           list drawn from a baseline Calculator object using the
           Calculator.dataframe method

    groupby : String object
        options for input: 'weighted_deciles', 'webapp_income_bins',
                           'large_income_bins', 'small_income_bins'
        specifies kind of bins used to group filing units
    NOTE: when groupby is 'weighted_deciles', the returned table has three
          extra rows containing top-decile detail consisting of statistics
          for the 0.90-0.95 quantile range (bottom half of top decile),
          for the 0.95-0.99 quantile range, and
          for the 0.99-1.00 quantile range (top one percent).

    income_measure : String object
        options for input: 'expanded_income', 'c00100'(AGI)
        specifies statistic to place filing units in bins

    tax_to_diff : String object
        options for input: 'iitax', 'payrolltax', 'combined'
        specifies which tax to difference

    Returns
    -------
    difference table as a Pandas DataFrame, with DIFF_TABLE_COLUMNS and
    groupby rows, where the rows run from lowest bin/decile to the highest
    followed by a sums row with the top-decile detail in an additional three
    rows following the sums row
    """
    # pylint: disable=too-many-statements
    # nested function that actually creates the difference table
    def diff_table_stats(res2, groupby, income_measure):
        """
        Return new Pandas DataFrame containing difference table statistics
        based on grouped values of specified col_name in the specified res2.

        res2: reform difference results Pandas DataFrame
        groupby: string naming type of bins
        income_measure: string naming column used to create res2 bins
        """
        # pylint: disable=too-many-locals
        def stat_dataframe(gpdf):
            """
            Nested function that returns statistics DataFrame derived from gpdf
            """
            def weighted_share_of_total(gpdf, colname, total):
                """
                Nested function that returns the ratio of the
                weighted_sum(pdf, colname) and specified total
                """
                return weighted_sum(gpdf, colname) / (total + EPSILON)
            # main logic of stat_dataframe function
            # construct basic stat_dataframe columns
            sdf = pd.DataFrame()
            sdf['count'] = gpdf.apply(weighted_count)
            sdf['tax_cut'] = gpdf.apply(weighted_count_lt_zero, 'tax_diff')
            sdf['perc_cut'] = gpdf.apply(weighted_perc_cut, 'tax_diff')
            sdf['tax_inc'] = gpdf.apply(weighted_count_gt_zero, 'tax_diff')
            sdf['perc_inc'] = gpdf.apply(weighted_perc_inc, 'tax_diff')
            sdf['mean'] = gpdf.apply(weighted_mean, 'tax_diff')
            sdf['tot_change'] = gpdf.apply(weighted_sum, 'tax_diff')
            wtotal = (res2['tax_diff'] * res2['s006']).sum()
            sdf['share_of_change'] = gpdf.apply(weighted_share_of_total,
                                                'tax_diff', wtotal)
            res2['afinc1'] = res1['aftertax_income']
            res2['afinc2'] = res2['aftertax_income']
            sdf['atinc1'] = gpdf.apply(weighted_sum, 'atinc1')
            sdf['atinc2'] = gpdf.apply(weighted_sum, 'atinc2')
            return sdf

        # main logic of diff_table_stats function
        # calculate whole-sample perc_cut and perc_inc statistics
        sums_perc_cut = weighted_perc_cut(res2, 'tax_diff')
        sums_perc_inc = weighted_perc_inc(res2, 'tax_diff')
        # add bin column to res2 given specified groupby and income_measure
        if groupby == 'weighted_deciles':
            pdf = add_quantile_bins(res2, income_measure, 10)
        elif groupby == 'webapp_income_bins':
            pdf = add_income_bins(res2, income_measure, bin_type='webapp')
        elif groupby == 'large_income_bins':
            pdf = add_income_bins(res2, income_measure, bin_type='tpc')
        elif groupby == 'small_income_bins':
            pdf = add_income_bins(res2, income_measure, bin_type='soi')
        # create grouped Pandas DataFrame
        gpdf = pdf.groupby('bins', as_index=False)
        # create difference table statistics from gpdf in a new DataFrame
        diffs_without_sums = stat_dataframe(gpdf)
        # calculate sums row
        row = get_sums(diffs_without_sums)[diffs_without_sums.columns]
        row['mean'] = 0
        if row['count'] > 0:
            row['mean'] = row['tot_change'] / row['count']
        row['perc_cut'] = sums_perc_cut
        row['perc_inc'] = sums_perc_inc
        row['share_of_change'] = 1.0  # avoid rounding error
        diffs = diffs_without_sums.append(row)
        # append top-decile-detail rows
        if groupby == 'weighted_deciles':
            pdf = gpdf.get_group(10)  # top decile as its own DataFrame
            pdf = add_quantile_bins(copy.deepcopy(pdf), income_measure, 10)
            # TODO: following statement generates this IGNORED error:
            # ValueError: Buffer dtype mismatch,
            #             expected 'Python object' but got 'long'
            # Exception ValueError: "Buffer dtype mismatch,
            #              expected 'Python object' but got 'long'"
            #              in 'pandas._libs.lib.is_bool_array' ignored
            #                                                  ^^^^^^^
            # It is hoped that Pandas PR#18252, which is scheduled for
            # inclusion in Pandas version 0.23.0 (Apr 2018), will fix this.
            # See discussion at the following URL:
            # https://github.com/pandas-dev/pandas/issues/19037
            pdf['bins'].replace(to_replace=[1, 2, 3, 4, 5],
                                value=[0, 0, 0, 0, 0], inplace=True)
            pdf['bins'].replace(to_replace=[6, 7, 8, 9],
                                value=[1, 1, 1, 1], inplace=True)
            pdf['bins'].replace(to_replace=[10], value=[2], inplace=True)
            gpdf = pdf.groupby('bins', as_index=False)
            sdf = stat_dataframe(gpdf)
            diffs = diffs.append(sdf, ignore_index=True)
        return diffs
    # main logic of create_difference_table
    assert isinstance(vdf1, pd.DataFrame)
    assert isinstance(vdf2, pd.DataFrame)
    assert (groupby == 'weighted_deciles' or
            groupby == 'webapp_income_bins' or
            groupby == 'large_income_bins' or
            groupby == 'small_income_bins')
    assert (income_measure == 'expanded_income' or
            income_measure == 'c00100')
    assert income_measure in vdf1
    assert (tax_to_diff == 'iitax' or
            tax_to_diff == 'payrolltax' or
            tax_to_diff == 'combined')
    res1 = copy.deepcopy(vdf1)
    res2 = copy.deepcopy(vdf2)
    baseline_income_measure = income_measure + '_baseline'
    res2[baseline_income_measure] = res1[income_measure]
    res2['tax_diff'] = res2[tax_to_diff] - res1[tax_to_diff]
    res2['atinc1'] = res1['aftertax_income']
    res2['atinc2'] = res2['aftertax_income']
    diffs = diff_table_stats(res2, groupby, baseline_income_measure)
    diffs['perc_aftertax'] = diffs['tot_change'] / diffs['atinc1']
    diffs['pc_aftertaxinc'] = (diffs['atinc2'] / diffs['atinc1']) - 1.0
    # delete intermediate atinc1 and atinc2 columns
    del diffs['atinc1']
    del diffs['atinc2']
    # convert some columns to percentages
    percent_columns = ['perc_inc', 'perc_cut', 'share_of_change',
                       'perc_aftertax', 'pc_aftertaxinc']
    for col in percent_columns:
        diffs[col] *= 100.0
    # set print display format for float table elements
    pd.options.display.float_format = '{:10,.2f}'.format
    # ensure diffs columns are in correct order
    assert diffs.columns.values.tolist() == DIFF_TABLE_COLUMNS
    return diffs


def create_diagnostic_table(vdf, year):
    """
    Extract single-year diagnostic table from Pandas DataFrame object
    derived from a Calculator object using the dataframe(DIST_VARIABLES)
    method.

    Parameters
    ----------
    vdf : Pandas DataFrame object containing the variables

    year : calendar year for which variables were drawn from Calculator object

    Returns
    -------
    Pandas DataFrame object containing the diagnostic table
    """
    # pylint: disable=too-many-statements
    def diagnostic_table_odict(recs):
        """
        Nested function that extracts diagnostic table dictionary from
        the specified Pandas DataFrame object, vdf.

        Parameters
        ----------
        vdf : Pandas DataFrame object containing the variables

        Returns
        -------
        ordered dictionary of variable names and aggregate weighted values
        """
        # aggregate weighted values expressed in millions or billions
        in_millions = 1.0e-6
        in_billions = 1.0e-9
        odict = collections.OrderedDict()
        # total number of filing units
        wghts = vdf['s006']
        odict['Returns (#m)'] = wghts.sum() * in_millions
        # adjusted gross income
        agi = vdf['c00100']
        odict['AGI ($b)'] = (agi * wghts).sum() * in_billions
        # number of itemizers
        num = (wghts[(vdf['c04470'] > 0.) & (agi > 0.)].sum())
        odict['Itemizers (#m)'] = num * in_millions
        # itemized deduction
        ided1 = vdf['c04470'] * wghts
        val = ided1[vdf['c04470'] > 0.].sum()
        odict['Itemized Deduction ($b)'] = val * in_billions
        # number of standard deductions
        num = wghts[(vdf['standard'] > 0.) & (agi > 0.)].sum()
        odict['Standard Deduction Filers (#m)'] = num * in_millions
        # standard deduction
        sded1 = recs.standard * wghts
        val = sded1[(vdf['standard'] > 0.) & (agi > 0.)].sum()
        odict['Standard Deduction ($b)'] = val * in_billions
        # personal exemption
        val = (vdf['c04600'] * wghts)[agi > 0.].sum()
        odict['Personal Exemption ($b)'] = val * in_billions
        # taxable income
        val = (vdf['c04800'] * wghts).sum()
        odict['Taxable Income ($b)'] = val * in_billions
        # regular tax liability
        val = (vdf['taxbc'] * wghts).sum()
        odict['Regular Tax ($b)'] = val * in_billions
        # AMT taxable income
        odict['AMT Income ($b)'] = ((vdf['c62100'] * wghts).sum() *
                                    in_billions)
        # total AMT liability
        odict['AMT Liability ($b)'] = ((vdf['c09600'] * wghts).sum() *
                                       in_billions)
        # number of people paying AMT
        odict['AMT Filers (#m)'] = (wghts[vdf['c09600'] > 0.].sum() *
                                    in_millions)
        # tax before credits
        val = (vdf['c05800'] * wghts).sum()
        odict['Tax before Credits ($b)'] = val * in_billions
        # refundable credits
        val = (vdf['refund'] * wghts).sum()
        odict['Refundable Credits ($b)'] = val * in_billions
        # nonrefundable credits
        val = (vdf['c07100'] * wghts).sum()
        odict['Nonrefundable Credits ($b)'] = val * in_billions
        # reform surtaxes (part of federal individual income tax liability)
        val = (vdf['surtax'] * wghts).sum()
        odict['Reform Surtaxes ($b)'] = val * in_billions
        # other taxes on Form 1040
        val = (vdf['othertaxes'] * wghts).sum()
        odict['Other Taxes ($b)'] = val * in_billions
        # federal individual income tax liability
        val = (vdf['iitax'] * wghts).sum()
        odict['Ind Income Tax ($b)'] = val * in_billions
        # OASDI+HI payroll tax liability (including employer share)
        val = (vdf['payrolltax'] * wghts).sum()
        odict['Payroll Taxes ($b)'] = val * in_billions
        # combined income and payroll tax liability
        val = (vdf['combined'] * wghts).sum()
        odict['Combined Liability ($b)'] = val * in_billions
        # number of tax units with non-positive income tax liability
        num = (wghts[vdf['iitax'] <= 0]).sum()
        odict['With Income Tax <= 0 (#m)'] = num * in_millions
        # number of tax units with non-positive combined tax liability
        num = (wghts[vdf['combined'] <= 0]).sum()
        odict['With Combined Tax <= 0 (#m)'] = num * in_millions
        return odict
    # tabulate diagnostic table
    odict = diagnostic_table_odict(vdf)
    pdf = pd.DataFrame(data=odict, index=[year], columns=odict.keys())
    pdf = pdf.transpose()
    pd.options.display.float_format = '{:8,.1f}'.format
    return pdf


def mtr_graph_data(vdf, year,
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
    vdf : a Pandas DataFrame object containing variables and marginal tax rates
        (See Calculator.mtr_graph method for required elements of vdf.)

    year : integer
        specifies calendar year of the data in vdf

    mars : integer or string
        specifies which filing status subgroup to show in the graph

        - 'ALL': include all filing units in sample

        - 1: include only single filing units

        - 2: include only married-filing-jointly filing units

        - 3: include only married-filing-separately filing units

        - 4: include only head-of-household filing units

    mtr_measure : string
        specifies which marginal tax rate to show on graph's y axis

        - 'itax': marginal individual income tax rate

        - 'ptax': marginal payroll tax rate

        - 'combined': sum of marginal income and payroll tax rates

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
        specifies which income variable to show on the graph's x axis

        - 'wages': wage and salary income (e00200)

        - 'agi': adjusted gross income, AGI (c00100)

        - 'expanded_income': sum of AGI, non-taxable interest income,
          non-taxable social security benefits, and employer share of
          FICA taxes.

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
    # pylint: disable=too-many-arguments,too-many-statements
    # pylint: disable=too-many-locals,too-many-branches
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
        income_str = 'Expanded-Income'
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
    # . . check vdf
    assert isinstance(vdf, pd.DataFrame)
    # create 'bins' column given specified income_var and dollar_weighting
    dfx = add_quantile_bins(vdf, income_var, 100,
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
    xlabel_str = 'Baseline {} Percentile'.format(income_str)
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


def atr_graph_data(vdf, year,
                   mars='ALL',
                   atr_measure='combined',
                   min_avginc=1000):
    """
    Prepare average tax rate data needed by xtr_graph_plot utility function.

    Parameters
    ----------
    vdf : a Pandas DataFrame object containing variables and tax liabilities
        (See Calculator.atr_graph method for required elements of vdf.)

    year : integer
        specifies calendar year of the data in vdf

    mars : integer or string
        specifies which filing status subgroup to show in the graph

        - 'ALL': include all filing units in sample

        - 1: include only single filing units

        - 2: include only married-filing-jointly filing units

        - 3: include only married-filing-separately filing units

        - 4: include only head-of-household filing units

    atr_measure : string
        specifies which average tax rate to show on graph's y axis

        - 'itax': average individual income tax rate

        - 'ptax': average payroll tax rate

        - 'combined': sum of average income and payroll tax rates

    min_avginc : float
        specifies the minimum average expanded income for a percentile to
        be included in the graph data; value must be positive

    Returns
    -------
    dictionary object suitable for passing to xtr_graph_plot utility function
    """
    # pylint: disable=too-many-locals
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
    if atr_measure == 'combined':
        atr_str = 'Income+Payroll-Tax'
    elif atr_measure == 'itax':
        atr_str = 'Income-Tax'
    elif atr_measure == 'ptax':
        atr_str = 'Payroll-Tax'
    else:
        msg = ('atr_measure="{}" is neither '
               '"itax" nor "ptax" nor "combined"')
        raise ValueError(msg.format(atr_measure))
    # . . check min_avginc value
    assert min_avginc > 0
    # . . check vdf object
    assert isinstance(vdf, pd.DataFrame)
    # create 'bins' column
    dfx = add_quantile_bins(vdf, 'expanded_income', 100)
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
    xlabel_str = 'Baseline Expanded-Income Percentile'
    if mars != 'ALL':
        xlabel_str = '{} for MARS={}'.format(xlabel_str, mars)
    data['xlabel'] = xlabel_str
    title_str = 'Average Tax Rate by Income Percentile'
    if mars != 'ALL':
        title_str = '{} for MARS={}'.format(title_str, mars)
    title_str = '{} for {}'.format(title_str, year)
    data['title'] = title_str
    return data


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
    USAGE EXAMPLE::

      gdata = mtr_graph_data(...)
      gplot = xtr_graph_plot(gdata)

    THEN when working interactively in a Python notebook::

      bp.show(gplot)

    OR when executing script using Python command-line interpreter::

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
    fig.line(lines.index, lines.base, line_color='blue', legend='Baseline')
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
    delete_file(filename)  # work around annoying 'already exists' bokeh msg
    bio.output_file(filename=filename, title=title)
    bio.save(figure)


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
        return math.pow((exputil * (1.0 - crra)), (1.0 / (1.0 - crra)))
    mu_at_cmin = math.pow(cmin, -crra)
    return ((exputil - tu_at_cmin) / mu_at_cmin) + cmin


def ce_aftertax_expanded_income(df1, df2,
                                custom_params=None,
                                require_no_agg_tax_change=True):
    """
    Return dictionary that contains certainty-equivalent of the
    expected utility of after-tax expanded income computed for
    several constant-relative-risk-aversion parameter values
    for each of two Pandas DataFrame objects: df1, which represents
    the pre-reform situation, and df2, which represents the
    post-reform situation.  Both DataFrame objects must contain
    's006', 'combined', and 'expanded_income' columns.

    IMPORTANT NOTES: These normative welfare calculations are very simple.
    It is assumed that utility is a function of only consumption, and that
    consumption is equal to after-tax income.  This means that any assumed
    behavioral responses that change work effort will not affect utility via
    the correpsonding change in leisure.  And any saving response to changes
    in after-tax income do not affect consumption.

    The cmin value is the consumption level below which marginal utility
    is considered to be constant.  This allows the handling of filing units
    with very low or even negative after-tax expanded income in the
    expected-utility and certainty-equivalent calculations.
    """
    # pylint: disable=too-many-locals
    # check consistency of the two DataFrame objects
    assert isinstance(df1, pd.DataFrame)
    assert isinstance(df2, pd.DataFrame)
    assert df1.shape == df2.shape
    # specify utility function parameters
    if custom_params:
        crras = custom_params['crra_list']
        for crra in crras:
            assert crra >= 0
        cmin = custom_params['cmin_value']
        assert cmin > 0
    else:
        crras = [0, 1, 2, 3, 4]
        cmin = 1000
    # compute aggregate combined tax revenue and aggregate after-tax income
    billion = 1.0e-9
    cedict = dict()
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
    # calculate sample-weighted probability of each filing unit
    prob_raw = np.divide(df1['s006'],  # pylint: disable=no-member
                         df1['s006'].sum())
    prob = np.divide(prob_raw,  # pylint: disable=no-member
                     prob_raw.sum())  # handle any rounding error
    # calculate after-tax income of each filing unit in df1 and df2
    ati1 = df1['expanded_income'] - df1['combined']
    ati2 = df2['expanded_income'] - df2['combined']
    # calculate certainty-equivaluent after-tax income in df1 and df2
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


def read_egg_csv(fname, index_col=None):
    """
    Read from egg the file named fname that contains CSV data and
    return pandas DataFrame containing the data.
    """
    try:
        path_in_egg = os.path.join('taxcalc', fname)
        vdf = pd.read_csv(
            pkg_resources.resource_stream(
                pkg_resources.Requirement.parse('taxcalc'),
                path_in_egg),
            index_col=index_col
        )
    except:
        raise ValueError('could not read {} data from egg'.format(fname))
    # cannot call read_egg_ function in unit tests
    return vdf  # pragma: no cover


def read_egg_json(fname):
    """
    Read from egg the file named fname that contains JSON data and
    return dictionary containing the data.
    """
    try:
        path_in_egg = os.path.join('taxcalc', fname)
        pdict = json.loads(
            pkg_resources.resource_stream(
                pkg_resources.Requirement.parse('taxcalc'),
                path_in_egg).read().decode('utf-8'),
            object_pairs_hook=collections.OrderedDict
        )
    except:
        raise ValueError('could not read {} data from egg'.format(fname))
    # cannot call read_egg_ function in unit tests
    return pdict  # pragma: no cover


def delete_file(filename):
    """
    Remove specified file if it exists.
    """
    if os.path.isfile(filename):
        os.remove(filename)


def bootstrap_se_ci(data, seed, num_samples, statistic, alpha):
    """
    Return bootstrap estimate of standard error of statistic and
    bootstrap estimate of 100*(1-2*alpha)% confidence interval for statistic
    in a dictionary along with specified seed and nun_samples (B) and alpha.
    """
    assert isinstance(data, np.ndarray)
    assert isinstance(seed, int)
    assert isinstance(num_samples, int)
    assert callable(statistic)  # function that computes statistic from data
    assert isinstance(alpha, float)
    bsest = dict()
    bsest['seed'] = seed
    np.random.seed(seed)  # pylint: disable=no-member
    dlen = len(data)
    idx = np.random.randint(low=0, high=dlen,   # pylint: disable=no-member
                            size=(num_samples, dlen))
    samples = data[idx]
    stat = statistic(samples, axis=1)
    bsest['B'] = num_samples
    bsest['se'] = np.std(stat, ddof=1)
    stat = np.sort(stat)
    bsest['alpha'] = alpha
    bsest['cilo'] = stat[int(round(alpha * num_samples)) - 1]
    bsest['cihi'] = stat[int(round((1 - alpha) * num_samples)) - 1]
    return bsest


def dec_graph_data(diff_table, year):
    """
    Prepare data needed by dec_graph_plot utility function.

    Parameters
    ----------
    diff_table : a Pandas DataFrame object returned from the
        Calculator class difference_table method

    year : integer
        specifies calendar year of the data in the diff_table

    Returns
    -------
    dictionary object suitable for passing to dec_graph_plot utility function
    """
    # construct dictionary containing the bar data required by dec_graph_plot
    bars = dict()
    for idx in range(0, 14):  # the ten income deciles, all, plus top details
        info = dict()
        info['label'] = DECILE_ROW_NAMES[idx]
        info['value'] = diff_table['pc_aftertaxinc'][idx]
        if info['label'] == 'all':
            info['label'] = '---------'
            info['value'] = 0
        bars[idx] = info
    # construct dictionary containing bar data and auto-generated labels
    data = dict()
    data['bars'] = bars
    xlabel = 'Reform-Induced Percentage Change in After-Tax Expanded Income'
    data['xlabel'] = xlabel
    ylabel = 'Expanded Income Percentile Group'
    data['ylabel'] = ylabel
    title_str = 'Change in After-Tax Income by Income Percentile Group'
    data['title'] = '{} for {}'.format(title_str, year)
    return data


def dec_graph_plot(data,
                   width=850,
                   height=500,
                   xlabel='',
                   ylabel='',
                   title=''):
    """
    Plot stacked decile graph using data returned from dec_graph_data function.

    Parameters
    ----------
    data : dictionary object returned from dec_graph_data() utility function

    width : integer
        width of plot expressed in pixels

    height : integer
        height of plot expressed in pixels

    xlabel : string
        x-axis label; if '', then use label generated by dec_graph_data

    ylabel : string
        y-axis label; if '', then use label generated by dec_graph_data

    title : string
        graph title; if '', then use title generated by dec_graph_data

    Returns
    -------
    bokeh.plotting figure object containing a raster graphics plot

    Notes
    -----
    USAGE EXAMPLE::

      gdata = dec_graph_data(...)
      gplot = dec_graph_plot(gdata)

    THEN when working interactively in a Python notebook::

      bp.show(gplot)

    OR when executing script using Python command-line interpreter::

      bio.output_file('graph-name.html', title='Change in After-Tax Income')
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
    # pylint: disable=too-many-arguments,too-many-locals
    if title == '':
        title = data['title']
    bar_keys = sorted(data['bars'].keys())
    bar_labels = [data['bars'][key]['label'] for key in bar_keys]
    fig = bp.figure(plot_width=width, plot_height=height, title=title,
                    y_range=bar_labels)
    fig.title.text_font_size = '12pt'
    fig.outline_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.minor_tick_line_color = None
    fig.axis.axis_label_text_font_size = '12pt'
    fig.axis.axis_label_text_font_style = 'normal'
    fig.axis.major_label_text_font_size = '12pt'
    if xlabel == '':
        xlabel = data['xlabel']
    fig.xaxis.axis_label = xlabel
    fig.xaxis[0].formatter = PrintfTickFormatter(format='%+.1f%%')
    if ylabel == '':
        ylabel = data['ylabel']
    fig.yaxis.axis_label = ylabel
    fig.ygrid.grid_line_color = None
    # plot thick x-axis grid line at zero
    fig.line(x=[0, 0], y=[0, 14], line_width=1, line_color='black')
    # plot bars
    barheight = 0.8
    bcolor = 'blue'
    yidx = 0
    for idx in bar_keys:
        bval = data['bars'][idx]['value']
        blabel = data['bars'][idx]['label']
        bheight = barheight
        if blabel == '90-95':
            bheight *= 0.5
            bcolor = 'red'
        elif blabel == '95-99':
            bheight *= 0.4
        elif blabel == 'Top 1%':
            bheight *= 0.1
        fig.rect(x=(bval / 2.0),   # x-coordinate of center of the rectangle
                 y=(yidx + 0.5),   # y-coordinate of center of the rectangle
                 width=abs(bval),  # width of the rectangle
                 height=bheight,   # height of the rectangle
                 color=bcolor)
        yidx += 1
    return fig


def nonsmall_diffs(linelist1, linelist2, small=0.0):
    """
    Return True if line lists differ significantly; otherwise return False.
    Significant difference means one or more numbers differ (between
    linelist1 and linelist2) by more than the small amount.
    NOTE: this function is meant to be used only in the unit tests to handle
    small differences in floating point values generated by Python 2.7 and 3.6,
    where a nonzero small amount is used only under Python 3.6.
    """
    # embedded function used only in nonsmall_diffs function
    def isfloat(value):
        """
        Return True if value can be cast to float; otherwise return False.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    # begin nonsmall_diffs logic
    assert isinstance(linelist1, list)
    assert isinstance(linelist2, list)
    if len(linelist1) != len(linelist2):
        return True
    assert small >= 0.0 and small <= 1.0
    epsilon = 1e-6
    smallamt = small + epsilon
    for line1, line2 in zip(linelist1, linelist2):
        if line1 == line2:
            continue
        else:
            tokens1 = line1.replace(',', '').split()
            tokens2 = line2.replace(',', '').split()
            for tok1, tok2 in zip(tokens1, tokens2):
                tok1_isfloat = isfloat(tok1)
                tok2_isfloat = isfloat(tok2)
                if tok1_isfloat and tok2_isfloat:
                    if abs(float(tok1) - float(tok2)) <= smallamt:
                        continue
                    else:
                        return True
                elif not tok1_isfloat and not tok2_isfloat:
                    if tok1 == tok2:
                        continue
                    else:
                        return True
                else:
                    return True
        return False
