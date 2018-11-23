"""
PUBLIC low-level utility functions for Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pycodestyle utils.py
# pylint --disable=locally-disabled utils.py
#
# pylint: disable=too-many-lines

import os
import math
import json
import collections
import pkg_resources
import numpy as np
import pandas as pd
import bokeh.io as bio
import bokeh.plotting as bp
from bokeh.models import PrintfTickFormatter
from taxcalc.utilsprvt import (weighted_count_lt_zero,
                               weighted_count_gt_zero,
                               weighted_count, weighted_mean,
                               wage_weighted, agi_weighted,
                               expanded_income_weighted)


# Items in the DIST_TABLE_COLUMNS list below correspond to the items in the
# DIST_TABLE_LABELS list below; this correspondence allows us to use this
# labels list to map a label to the correct column in a distribution table.

DIST_VARIABLES = ['expanded_income', 'c00100', 'aftertax_income', 'standard',
                  'c04470', 'c04600', 'c04800', 'taxbc', 'c62100', 'c09600',
                  'c05800', 'surtax', 'othertaxes', 'refund', 'c07100',
                  'iitax', 'payrolltax', 'combined', 's006', 'ubi',
                  'benefit_cost_total', 'benefit_value_total']

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
                      'ubi',
                      'benefit_cost_total',
                      'benefit_value_total',
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
                     'Universal Basic Income',
                     'Total Cost of Benefits',
                     'Consumption Value of Benefits',
                     'Expanded Income',
                     'After-Tax Expanded Income']

# Items in the DIFF_TABLE_COLUMNS list below correspond to the items in the
# DIFF_TABLE_LABELS list below; this correspondence allows us to use this
# labels list to map a label to the correct column in a difference table.

DIFF_VARIABLES = ['expanded_income', 'c00100', 'aftertax_income',
                  'iitax', 'payrolltax', 'combined', 's006',
                  'ubi', 'benefit_cost_total', 'benefit_value_total']

DIFF_TABLE_COLUMNS = ['count',
                      'tax_cut',
                      'perc_cut',
                      'tax_inc',
                      'perc_inc',
                      'mean',
                      'tot_change',
                      'share_of_change',
                      'ubi',
                      'benefit_cost_total',
                      'benefit_value_total',
                      'pc_aftertaxinc']

DIFF_TABLE_LABELS = ['All Tax Units',
                     'Tax Units with Tax Cut',
                     'Percent with Tax Cut',
                     'Tax Units with Tax Increase',
                     'Percent with Tax Increase',
                     'Average Tax Change',
                     'Total Tax Difference',
                     'Share of Overall Change',
                     'Universal Basic Income',
                     'Total Cost of Benefits',
                     'Consumption Value of Benefits',
                     '% Change in After-Tax Income']

DECILE_ROW_NAMES = ['0-10n', '0-10z', '0-10p',
                    '10-20', '20-30', '30-40', '40-50',
                    '50-60', '60-70', '70-80', '80-90', '90-100',
                    'ALL',
                    '90-95', '95-99', 'Top 1%']

STANDARD_ROW_NAMES = ['<$0K', '=$0K', '$0-10K', '$10-20K', '$20-30K',
                      '$30-40K', '$40-50K', '$50-75K', '$75-100K',
                      '$100-200K', '$200-500K', '$500-1000K', '>$1000K', 'ALL']

STANDARD_INCOME_BINS = [-9e99, -1e-9, 1e-9, 10e3, 20e3, 30e3, 40e3, 50e3,
                        75e3, 100e3, 200e3, 500e3, 1e6, 9e99]

SOI_AGI_BINS = [-9e99, 1.0, 5e3, 10e3, 15e3, 20e3, 25e3, 30e3, 40e3, 50e3,
                75e3, 100e3, 200e3, 500e3, 1e6, 1.5e6, 2e6, 5e6, 10e6, 9e99]


def unweighted_sum(dframe, col_name):
    """
    Return unweighted sum of Pandas DataFrame col_name items.
    """
    return dframe[col_name].sum()


def weighted_sum(dframe, col_name):
    """
    Return weighted sum of Pandas DataFrame col_name items.
    """
    return (dframe[col_name] * dframe['s006']).sum()


def add_quantile_table_row_variable(dframe, income_measure, num_quantiles,
                                    decile_details=False,
                                    weight_by_income_measure=False):
    """
    Add a variable to specified Pandas DataFrame, dframe, that specifies the
    table row and is called 'table_row'.  The rows hold equal number of
    filing units when weight_by_income_measure=False or equal number of
    income dollars when weight_by_income_measure=True.  Assumes that
    specified dframe contains columns for the specified income_measure and
    for sample weights, s006.  When num_quantiles is 10 and decile_details
    is True, the bottom decile is broken up into three subgroups (neg, zero,
    and pos income_measure ) and the top decile is broken into three subgroups
    (90-95, 95-99, and top 1%).
    """
    assert isinstance(dframe, pd.DataFrame)
    assert income_measure in dframe
    if decile_details and num_quantiles != 10:
        msg = 'decile_details is True when num_quantiles is {}'
        raise ValueError(msg.format(num_quantiles))
    dframe.sort_values(by=income_measure, inplace=True)
    if weight_by_income_measure:
        dframe['cumsum_temp'] = np.cumsum(
            np.multiply(dframe[income_measure].values, dframe['s006'].values)
        )
        min_cumsum = dframe['cumsum_temp'].values[0]
    else:
        dframe['cumsum_temp'] = np.cumsum(dframe['s006'].values)
        min_cumsum = 0.  # because s006 values are non-negative
    max_cumsum = dframe['cumsum_temp'].values[-1]
    cumsum_range = max_cumsum - min_cumsum
    bin_width = cumsum_range / float(num_quantiles)
    bin_edges = list(min_cumsum +
                     np.arange(0, (num_quantiles + 1)) * bin_width)
    bin_edges[-1] = 9e99  # raise top of last bin to include all observations
    bin_edges[0] = -9e99  # lower bottom of 1st bin to include all observations
    num_bins = num_quantiles
    if decile_details:
        assert bin_edges[1] > 1e-9  # bin_edges[1] is top of bottom decile
        bin_edges.insert(1, 1e-9)  # top of zeros
        bin_edges.insert(1, -1e-9)  # top of negatives
        bin_edges.insert(-1, bin_edges[-2] + 0.5 * bin_width)  # top of 90-95
        bin_edges.insert(-1, bin_edges[-2] + 0.4 * bin_width)  # top of 95-99
        num_bins += 4
    labels = range(1, (num_bins + 1))
    dframe['table_row'] = pd.cut(dframe['cumsum_temp'], bin_edges,
                                 right=False, labels=labels)
    dframe.drop('cumsum_temp', axis=1, inplace=True)
    return dframe


def add_income_table_row_variable(dframe, income_measure, bin_edges):
    """
    Add a variable to specified Pandas DataFrame, dframe, that specifies the
    table row and is called 'table_row'.  The rows are defined by the
    specified bin_edges function argument.  Note that the bin groupings
    are LEFT INCLUSIVE, which means that bin_edges=[1,2,3,4] implies these
    three bin groupings: [1,2), [2,3), [3,4).

    Parameters
    ----------
    dframe: Pandas DataFrame
        the object to which we are adding bins

    income_measure: String
        specifies income variable used to construct bins

    bin_edges: list of scalar bin edges

    Returns
    -------
    dframe: Pandas DataFrame
        the original input plus the added 'table_row' column
    """
    assert isinstance(dframe, pd.DataFrame)
    assert income_measure in dframe
    assert isinstance(bin_edges, list)
    dframe['table_row'] = pd.cut(dframe[income_measure],
                                 bin_edges, right=False)
    return dframe


def get_sums(dframe):
    """
    Compute unweighted sum of items in each column of Pandas DataFrame, dframe.

    Returns
    -------
    Pandas Series object containing column sums indexed by dframe column names.
    """
    sums = dict()
    for col in dframe.columns.values.tolist():
        if col != 'table_row':
            sums[col] = dframe[col].sum()
    return pd.Series(sums, name='ALL')


def create_distribution_table(vdf, groupby, income_measure, scaling=True):
    """
    Get results from vdf, sort them by expanded_income based on groupby,
    and return them as a table.

    Parameters
    ----------
    vdf : Pandas DataFrame including columns named in DIST_TABLE_COLUMNS list
        for example, an object returned from the Calculator class
        distribution_table_dataframe method

    groupby : String object
        options for input: 'weighted_deciles' or
                           'standard_income_bins' or 'soi_agi_bins'
        determines how the rows in the resulting Pandas DataFrame are sorted

    income_measure: String object
        options for input: 'expanded_income' or 'expanded_income_baseline'
        determines which variable is used to sort rows

    scaling : boolean
        specifies whether or not table entries are scaled

    Returns
    -------
    distribution table as a Pandas DataFrame with DIST_TABLE_COLUMNS and
    groupby rows.
    NOTE: when groupby is 'weighted_deciles', the returned table has three
          extra rows containing top-decile detail consisting of statistics
          for the 0.90-0.95 quantile range (bottom half of top decile),
          for the 0.95-0.99 quantile range, and
          for the 0.99-1.00 quantile range (top one percent); and the
          returned table splits the bottom decile into filing units with
          negative (denoted by a 0-10n row label),
          zero (denoted by a 0-10z row label), and
          positive (denoted by a 0-10p row label) values of the
          specified income_measure.
    """
    # pylint: disable=too-many-statements,too-many-branches
    # nested function that returns calculated column statistics as a DataFrame
    def stat_dataframe(gdf):
        """
        Returns calculated distribution table column statistics derived from
        the specified grouped Dataframe object, gdf.
        """
        unweighted_columns = ['s006', 'num_returns_StandardDed',
                              'num_returns_ItemDed', 'num_returns_AMT']
        sdf = pd.DataFrame()
        for col in DIST_TABLE_COLUMNS:
            if col in unweighted_columns:
                sdf[col] = gdf.apply(unweighted_sum, col)
            else:
                sdf[col] = gdf.apply(weighted_sum, col)
        return sdf
    # main logic of create_distribution_table
    assert isinstance(vdf, pd.DataFrame)
    assert groupby in ('weighted_deciles',
                       'standard_income_bins',
                       'soi_agi_bins')
    assert income_measure in ('expanded_income', 'expanded_income_baseline')
    assert income_measure in vdf
    assert 'table_row' not in list(vdf.columns.values)
    # sort the data given specified groupby and income_measure
    if groupby == 'weighted_deciles':
        dframe = add_quantile_table_row_variable(vdf, income_measure,
                                                 10, decile_details=True)
    elif groupby == 'standard_income_bins':
        dframe = add_income_table_row_variable(vdf, income_measure,
                                               STANDARD_INCOME_BINS)
    elif groupby == 'soi_agi_bins':
        dframe = add_income_table_row_variable(vdf, income_measure,
                                               SOI_AGI_BINS)
    # construct grouped DataFrame
    gdf = dframe.groupby('table_row', as_index=False)
    dist_table = stat_dataframe(gdf)
    del dframe['table_row']
    # compute sum row
    sum_row = get_sums(dist_table)[dist_table.columns]
    # handle placement of sum_row in table
    if groupby == 'weighted_deciles':
        # compute top-decile row
        lenindex = len(dist_table.index)
        assert lenindex == 14  # rows should be indexed from 0 to 13
        topdec_row = get_sums(dist_table[11:lenindex])[dist_table.columns]
        # move top-decile detail rows to make room for topdec_row and sum_row
        dist_table = dist_table.reindex(index=range(0, lenindex + 2))
        # pylint: disable=no-member
        dist_table.iloc[15] = dist_table.iloc[13]
        dist_table.iloc[14] = dist_table.iloc[12]
        dist_table.iloc[13] = dist_table.iloc[11]
        dist_table.iloc[12] = sum_row
        dist_table.iloc[11] = topdec_row
        del topdec_row
    else:
        dist_table = dist_table.append(sum_row)
    del sum_row
    # ensure dist_table columns are in correct order
    assert dist_table.columns.values.tolist() == DIST_TABLE_COLUMNS
    # add row names to table if using weighted_deciles or standard_income_bins
    if groupby == 'weighted_deciles':
        rownames = DECILE_ROW_NAMES
    elif groupby == 'standard_income_bins':
        rownames = STANDARD_ROW_NAMES
    else:
        rownames = None
    if rownames:
        assert len(dist_table.index) == len(rownames)
        dist_table.index = rownames
        del rownames
    # delete intermediate Pandas DataFrame objects
    del gdf
    del dframe
    # scale table elements
    if scaling:
        count_vars = ['s006',
                      'num_returns_StandardDed',
                      'num_returns_ItemDed',
                      'num_returns_AMT']
        for col in dist_table.columns:
            if col in count_vars:
                dist_table[col] = np.round(dist_table[col] * 1e-6, 2)
            else:
                dist_table[col] = np.round(dist_table[col] * 1e-9, 3)
    # return table as Pandas DataFrame
    vdf.sort_index(inplace=True)
    return dist_table


def create_difference_table(vdf1, vdf2, groupby, tax_to_diff):
    """
    Get results from two different vdf, construct tax difference results,
    and return the difference statistics as a table.

    Parameters
    ----------
    vdf1 : Pandas DataFrame including columns named in DIFF_VARIABLES list
           for example, object returned from a dataframe(DIFF_VARIABLE) call
           on the basesline Calculator object

    vdf2 : Pandas DataFrame including columns in the DIFF_VARIABLES list
           for example, object returned from a dataframe(DIFF_VARIABLE) call
           on the reform Calculator object

    groupby : String object
        options for input: 'weighted_deciles' or
                           'standard_income_bins' or 'soi_agi_bins'
        determines how the rows in the resulting Pandas DataFrame are sorted

    tax_to_diff : String object
        options for input: 'iitax', 'payrolltax', 'combined'
        specifies which tax to difference

    Returns
    -------
    difference table as a Pandas DataFrame with DIFF_TABLE_COLUMNS and
    groupby rows.
    NOTE: when groupby is 'weighted_deciles', the returned table has three
          extra rows containing top-decile detail consisting of statistics
          for the 0.90-0.95 quantile range (bottom half of top decile),
          for the 0.95-0.99 quantile range, and
          for the 0.99-1.00 quantile range (top one percent); and the
          returned table splits the bottom decile into filing units with
          negative (denoted by a 0-10n row label),
          zero (denoted by a 0-10z row label), and
          positive (denoted by a 0-10p row label) values of the
          specified income_measure.
    """
    # pylint: disable=too-many-statements,too-many-locals,too-many-branches
    # nested function that creates dataframe containing additive statistics
    def additive_stats_dataframe(gdf):
        """
        Nested function that returns additive stats DataFrame derived from gdf
        """
        sdf = pd.DataFrame()
        sdf['count'] = gdf.apply(weighted_count)
        sdf['tax_cut'] = gdf.apply(weighted_count_lt_zero, 'tax_diff')
        sdf['tax_inc'] = gdf.apply(weighted_count_gt_zero, 'tax_diff')
        sdf['tot_change'] = gdf.apply(weighted_sum, 'tax_diff')
        sdf['ubi'] = gdf.apply(weighted_sum, 'ubi')
        sdf['benefit_cost_total'] = gdf.apply(weighted_sum,
                                              'benefit_cost_total')
        sdf['benefit_value_total'] = gdf.apply(weighted_sum,
                                               'benefit_value_total')
        sdf['atinc1'] = gdf.apply(weighted_sum, 'atinc1')
        sdf['atinc2'] = gdf.apply(weighted_sum, 'atinc2')
        return sdf
    # main logic of create_difference_table
    assert isinstance(vdf1, pd.DataFrame)
    assert isinstance(vdf2, pd.DataFrame)
    assert np.allclose(vdf1['s006'], vdf2['s006'])  # check rows in same order
    assert groupby in ('weighted_deciles',
                       'standard_income_bins',
                       'soi_agi_bins')
    assert 'expanded_income' in vdf1
    assert tax_to_diff in ('iitax', 'payrolltax', 'combined')
    assert 'table_row' not in list(vdf1.columns.values)
    assert 'table_row' not in list(vdf2.columns.values)
    baseline_expanded_income = 'expanded_income_baseline'
    vdf2[baseline_expanded_income] = vdf1['expanded_income']
    vdf2['tax_diff'] = vdf2[tax_to_diff] - vdf1[tax_to_diff]
    for col in ['ubi', 'benefit_cost_total', 'benefit_value_total']:
        vdf2[col] = vdf2[col] - vdf1[col]
    vdf2['atinc1'] = vdf1['aftertax_income']
    vdf2['atinc2'] = vdf2['aftertax_income']
    # add table_row column to vdf2 given specified groupby and income_measure
    if groupby == 'weighted_deciles':
        dframe = add_quantile_table_row_variable(vdf2,
                                                 baseline_expanded_income,
                                                 10, decile_details=True)
    elif groupby == 'standard_income_bins':
        dframe = add_income_table_row_variable(vdf2,
                                               baseline_expanded_income,
                                               STANDARD_INCOME_BINS)
    elif groupby == 'soi_agi_bins':
        dframe = add_income_table_row_variable(vdf2,
                                               baseline_expanded_income,
                                               SOI_AGI_BINS)
    # create grouped Pandas DataFrame
    gdf = dframe.groupby('table_row', as_index=False)
    del dframe['table_row']
    # create additive difference table statistics from gdf
    diff_table = additive_stats_dataframe(gdf)
    # calculate additive statistics on sums row
    sum_row = get_sums(diff_table)[diff_table.columns]
    # handle placement of sum_row in table
    if groupby == 'weighted_deciles':
        # compute top-decile row
        lenindex = len(diff_table.index)
        assert lenindex == 14  # rows should be indexed from 0 to 13
        topdec_row = get_sums(diff_table[11:lenindex])[diff_table.columns]
        # move top-decile detail rows to make room for topdec_row and sum_row
        diff_table = diff_table.reindex(index=range(0, lenindex + 2))
        # pylint: disable=no-member
        diff_table.iloc[15] = diff_table.iloc[13]
        diff_table.iloc[14] = diff_table.iloc[12]
        diff_table.iloc[13] = diff_table.iloc[11]
        diff_table.iloc[12] = sum_row
        diff_table.iloc[11] = topdec_row
        del topdec_row
    else:
        diff_table = diff_table.append(sum_row)
    # delete intermediate Pandas DataFrame objects
    del gdf
    del dframe
    # compute non-additive stats in each table cell
    count = diff_table['count']
    diff_table['perc_cut'] = np.where(count > 0.,
                                      100 * diff_table['tax_cut'] / count,
                                      0.)
    diff_table['perc_inc'] = np.where(count > 0.,
                                      100 * diff_table['tax_inc'] / count,
                                      0.)
    diff_table['mean'] = np.where(count > 0.,
                                  diff_table['tot_change'] / count,
                                  0.)
    total_change = sum_row['tot_change']
    diff_table['share_of_change'] = np.where(total_change == 0.,
                                             np.nan,
                                             (100 * diff_table['tot_change'] /
                                              total_change))
    diff_table['pc_aftertaxinc'] = np.where(diff_table['atinc1'] == 0.,
                                            np.nan,
                                            (100 * (diff_table['atinc2'] /
                                                    diff_table['atinc1'] - 1)))
    # delete intermediate Pandas DataFrame objects
    del diff_table['atinc1']
    del diff_table['atinc2']
    del count
    del sum_row
    # put diff_table columns in correct order
    diff_table = diff_table.reindex(columns=DIFF_TABLE_COLUMNS)
    # add row names to table if using weighted_deciles or standard_income_bins
    if groupby == 'weighted_deciles':
        rownames = DECILE_ROW_NAMES
    elif groupby == 'standard_income_bins':
        rownames = STANDARD_ROW_NAMES
    else:
        rownames = None
    if rownames:
        assert len(diff_table.index) == len(rownames)
        diff_table.index = rownames
        del rownames
    # scale table elements
    count_vars = ['count']
    scale_vars = ['tax_cut', 'tax_inc', 'tot_change', 'ubi',
                  'benefit_cost_total', 'benefit_value_total']
    for col in diff_table.columns:
        if col in count_vars:
            diff_table[col] = np.round(diff_table[col] * 1e-6, 2)
        elif col in scale_vars:
            diff_table[col] = np.round(diff_table[col] * 1e-9, 3)
        else:
            diff_table[col] = np.round(diff_table[col], 1)
    # return table as Pandas DataFrame
    vdf1.sort_index(inplace=True)
    vdf2.sort_index(inplace=True)
    return diff_table


def create_diagnostic_table(dframe_list, year_list):
    """
    Extract diagnostic table from list of Pandas DataFrame objects
    returned from a Calculator dataframe(DIST_VARIABLES) call for
    each year in the specified list of years.

    Parameters
    ----------
    dframe_list : list of Pandas DataFrame objects containing the variables

    year_list : list of calendar years corresponding to the dframe_list

    Returns
    -------
    Pandas DataFrame object containing the diagnostic table
    """
    # pylint: disable=too-many-statements
    def diagnostic_table_odict(vdf):
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
        odict['Returns (#m)'] = round(wghts.sum() * in_millions, 2)
        # adjusted gross income
        agi = vdf['c00100']
        odict['AGI ($b)'] = round((agi * wghts).sum() * in_billions, 3)
        # number of itemizers
        val = (wghts[vdf['c04470'] > 0.].sum())
        odict['Itemizers (#m)'] = round(val * in_millions, 2)
        # itemized deduction
        ided1 = vdf['c04470'] * wghts
        val = ided1[vdf['c04470'] > 0.].sum()
        odict['Itemized Deduction ($b)'] = round(val * in_billions, 3)
        # number of standard deductions
        val = wghts[vdf['standard'] > 0.].sum()
        odict['Standard Deduction Filers (#m)'] = round(val * in_millions, 2)
        # standard deduction
        sded1 = vdf['standard'] * wghts
        val = sded1[vdf['standard'] > 0.].sum()
        odict['Standard Deduction ($b)'] = round(val * in_billions, 3)
        # personal exemption
        val = (vdf['c04600'] * wghts).sum()
        odict['Personal Exemption ($b)'] = round(val * in_billions, 3)
        # taxable income
        val = (vdf['c04800'] * wghts).sum()
        odict['Taxable Income ($b)'] = round(val * in_billions, 3)
        # regular tax liability
        val = (vdf['taxbc'] * wghts).sum()
        odict['Regular Tax ($b)'] = round(val * in_billions, 3)
        # AMT taxable income
        val = (vdf['c62100'] * wghts).sum()
        odict['AMT Income ($b)'] = round(val * in_billions, 3)
        # total AMT liability
        val = (vdf['c09600'] * wghts).sum()
        odict['AMT Liability ($b)'] = round(val * in_billions, 3)
        # number of people paying AMT
        val = wghts[vdf['c09600'] > 0.].sum()
        odict['AMT Filers (#m)'] = round(val * in_millions, 2)
        # tax before credits
        val = (vdf['c05800'] * wghts).sum()
        odict['Tax before Credits ($b)'] = round(val * in_billions, 3)
        # refundable credits
        val = (vdf['refund'] * wghts).sum()
        odict['Refundable Credits ($b)'] = round(val * in_billions, 3)
        # nonrefundable credits
        val = (vdf['c07100'] * wghts).sum()
        odict['Nonrefundable Credits ($b)'] = round(val * in_billions, 3)
        # reform surtaxes (part of federal individual income tax liability)
        val = (vdf['surtax'] * wghts).sum()
        odict['Reform Surtaxes ($b)'] = round(val * in_billions, 3)
        # other taxes on Form 1040
        val = (vdf['othertaxes'] * wghts).sum()
        odict['Other Taxes ($b)'] = round(val * in_billions, 3)
        # federal individual income tax liability
        val = (vdf['iitax'] * wghts).sum()
        odict['Ind Income Tax ($b)'] = round(val * in_billions, 3)
        # OASDI+HI payroll tax liability (including employer share)
        val = (vdf['payrolltax'] * wghts).sum()
        odict['Payroll Taxes ($b)'] = round(val * in_billions, 3)
        # combined income and payroll tax liability
        val = (vdf['combined'] * wghts).sum()
        odict['Combined Liability ($b)'] = round(val * in_billions, 3)
        # number of tax units with non-positive income tax liability
        val = (wghts[vdf['iitax'] <= 0]).sum()
        odict['With Income Tax <= 0 (#m)'] = round(val * in_millions, 2)
        # number of tax units with non-positive combined tax liability
        val = (wghts[vdf['combined'] <= 0]).sum()
        odict['With Combined Tax <= 0 (#m)'] = round(val * in_millions, 2)
        return odict
    # check function arguments
    assert isinstance(dframe_list, list)
    assert dframe_list
    assert isinstance(year_list, list)
    assert year_list
    assert len(dframe_list) == len(year_list)
    assert isinstance(year_list[0], int)
    assert isinstance(dframe_list[0], pd.DataFrame)
    # construct diagnostic table
    tlist = list()
    for year, vardf in zip(year_list, dframe_list):
        odict = diagnostic_table_odict(vardf)
        ddf = pd.DataFrame(data=odict, index=[year], columns=odict.keys())
        ddf = ddf.transpose()
        tlist.append(ddf)
    del odict
    return pd.concat(tlist, axis=1)


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
    if isinstance(mars, str):
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
    # create 'table_row' column given specified income_var and dollar_weighting
    dfx = add_quantile_table_row_variable(
        vdf, income_var, 100, weight_by_income_measure=dollar_weighting)
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', as_index=False)
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
                   atr_measure='combined'):
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

    Returns
    -------
    dictionary object suitable for passing to xtr_graph_plot utility function
    """
    # pylint: disable=too-many-locals,too-many-statements
    # check validity of function arguments
    # . . check mars value
    if isinstance(mars, str):
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
    # . . check vdf object
    assert isinstance(vdf, pd.DataFrame)
    # determine last bin that contains non-positive expanded_income values
    weights = vdf['s006']
    nonpos = np.array(vdf['expanded_income'] <= 0, dtype=bool)
    nonpos_frac = weights[nonpos].sum() / weights.sum()
    num_bins_with_nonpos = int(math.ceil(100 * nonpos_frac))
    # create 'table_row' column
    dfx = add_quantile_table_row_variable(vdf, 'expanded_income', 100)
    # specify which 'table_row' are included
    include = [0] * num_bins_with_nonpos + [1] * (100 - num_bins_with_nonpos)
    included = np.array(include, dtype=bool)
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', as_index=False)
    # apply weighted_mean function to percentile-grouped values
    avginc_series = gdfx.apply(weighted_mean, 'expanded_income')
    avgtax1_series = gdfx.apply(weighted_mean, 'tax1')
    avgtax2_series = gdfx.apply(weighted_mean, 'tax2')
    # compute average tax rates for each included income percentile
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
    fig.line(lines.index, lines.base,
             line_color='blue', line_width=3, legend='Baseline')
    fig.line(lines.index, lines.reform,
             line_color='red', line_width=3, legend='Reform')
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


def pch_graph_data(vdf, year):
    """
    Prepare percentage change in after-tax expanded income data needed by
    pch_graph_plot utility function.

    Parameters
    ----------
    vdf : a Pandas DataFrame object containing variables
        (See Calculator.pch_graph method for required elements of vdf.)

    year : integer
        specifies calendar year of the data in vdf

    Returns
    -------
    dictionary object suitable for passing to pch_graph_plot utility function
    """
    # pylint: disable=too-many-locals
    # check validity of function arguments
    assert isinstance(vdf, pd.DataFrame)
    # determine last bin that contains non-positive expanded_income values
    weights = vdf['s006']
    nonpos = np.array(vdf['expanded_income'] <= 0, dtype=bool)
    nonpos_frac = weights[nonpos].sum() / weights.sum()
    num_bins_with_nonpos = int(math.ceil(100 * nonpos_frac))
    # create 'table_row' column
    dfx = add_quantile_table_row_variable(vdf, 'expanded_income', 100)
    # specify which 'table_row' are included
    include = [0] * num_bins_with_nonpos + [1] * (100 - num_bins_with_nonpos)
    included = np.array(include, dtype=bool)
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', as_index=False)
    # apply weighted_mean function to percentile-grouped values
    avginc_series = gdfx.apply(weighted_mean, 'expanded_income')
    change_series = gdfx.apply(weighted_mean, 'chg_aftinc')
    # compute percentage change statistic each included income percentile
    pch_series = np.zeros_like(avginc_series)
    pch_series[included] = change_series[included] / avginc_series[included]
    # construct DataFrame containing the pch_series expressed as percent
    line = pd.DataFrame()
    line['pch'] = pch_series * 100
    # include only percentiles with average income no less than min_avginc
    line = line[included]
    # construct dictionary containing plot line and auto-generated labels
    data = dict()
    data['line'] = line
    data['ylabel'] = 'Change in After-Tax Expanded Income'
    data['xlabel'] = 'Baseline Expanded-Income Percentile'
    title_str = ('Percentage Change in After-Tax Expanded Income '
                 'by Income Percentile')
    title_str = '{} for {}'.format(title_str, year)
    data['title'] = title_str
    return data


def pch_graph_plot(data,
                   width=850,
                   height=500,
                   xlabel='',
                   ylabel='',
                   title=''):
    """
    Plot percentage change in after-tax expanded income using data returned
    from the pch_graph_data function.

    Parameters
    ----------
    data : dictionary object returned from ?tr_graph_data() utility function

    width : integer
        width of plot expressed in pixels

    height : integer
        height of plot expressed in pixels

    xlabel : string
        x-axis label; if '', then use label generated by pch_graph_data

    ylabel : string
        y-axis label; if '', then use label generated by pch_graph_data

    title : string
        graph title; if '', then use title generated by pch_graph_data

    Returns
    -------
    bokeh.plotting figure object containing a raster graphics plot

    Notes
    -----
    See Notes to xtr_graph_plot function.
    """
    # pylint: disable=too-many-arguments
    if title == '':
        title = data['title']
    fig = bp.figure(plot_width=width, plot_height=height, title=title)
    fig.title.text_font_size = '12pt'
    fig.line(data['line'].index, data['line'].pch,
             line_color='blue', line_width=3)
    fig.circle(0, 0, visible=False)  # force zero to be included on y axis
    zero_grid_line_range = range(0, 101)
    zero_grid_line_height = [0] * len(zero_grid_line_range)
    fig.line(zero_grid_line_range, zero_grid_line_height,
             line_color='black', line_width=1)
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
    fig.yaxis[0].formatter = PrintfTickFormatter(format='%+.1f%%')
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
    # else if consumption < cmin
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
    except Exception:
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
    except Exception:
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


def dec_graph_data(dist_table1, dist_table2, year,
                   include_zero_incomes, include_negative_incomes):
    """
    Prepare data needed by dec_graph_plot utility function.

    Parameters
    ----------
    dist_table1 : a Pandas DataFrame object returned from the
        Calculator class distribution_tables method for baseline

    dist_table2 : a Pandas DataFrame object returned from the
        Calculator class distribution_tables method for reform

    year : integer
        specifies calendar year of the data in the diff_table

    include_zero_incomes : boolean
        if True, the bottom decile does contain filing units
        with zero expanded_income;
        if False, the bottom decile does not contain filing units
        with zero expanded_income.

    include_negative_incomes : boolean
        if True, the bottom decile does contain filing units
        with negative expanded_income;
        if False, the bottom decile does not contain filing units
        with negative expanded_income.

    Returns
    -------
    dictionary object suitable for passing to dec_graph_plot utility function
    """
    # pylint: disable=too-many-locals
    # check that the two distribution tables are consistent
    assert len(dist_table1.index) == len(DECILE_ROW_NAMES)
    assert len(dist_table2.index) == len(DECILE_ROW_NAMES)
    assert np.allclose(dist_table1['s006'], dist_table2['s006'])
    # compute bottom bar width and statistic value
    wght = dist_table1['s006']
    total_wght = wght[2] + wght[1] + wght[0]
    included_wght = wght[2]
    included_val1 = dist_table1['aftertax_income'][2] * wght[2]
    included_val2 = dist_table2['aftertax_income'][2] * wght[2]
    if include_zero_incomes:
        included_wght += wght[1]
        included_val1 += dist_table1['aftertax_income'][1] * wght[1]
        included_val2 += dist_table2['aftertax_income'][1] * wght[1]
    if include_negative_incomes:
        included_wght += wght[0]
        included_val1 += dist_table1['aftertax_income'][0] * wght[0]
        included_val2 += dist_table2['aftertax_income'][0] * wght[0]
    bottom_bar_width = included_wght / total_wght
    bottom_bar_value = (included_val2 / included_val1 - 1.) * 100.
    # construct dictionary containing the bar data required by dec_graph_plot
    bars = dict()
    # ... bottom bar
    info = dict()
    if include_zero_incomes and include_negative_incomes:
        info['label'] = '0-10'
    elif include_zero_incomes and not include_negative_incomes:
        info['label'] = '0-10zp'
    if not include_zero_incomes and include_negative_incomes:
        info['label'] = '0-10np'
    if not include_zero_incomes and not include_negative_incomes:
        info['label'] = '0-10p'
    info['value'] = bottom_bar_value
    bars[0] = info
    # ... other bars
    offset = 2
    for idx in range(offset + 1, len(DECILE_ROW_NAMES)):
        info = dict()
        info['label'] = DECILE_ROW_NAMES[idx]
        val1 = dist_table1['aftertax_income'][idx] * wght[idx]
        val2 = dist_table2['aftertax_income'][idx] * wght[idx]
        info['value'] = (val2 / val1 - 1.) * 100.
        if info['label'] == 'ALL':
            info['label'] = '---------'
            info['value'] = 0
        bars[idx - offset] = info
    # construct dictionary containing bar data and auto-generated labels
    data = dict()
    data['bottom_bar_width'] = bottom_bar_width
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
        if blabel == '0-10':
            bheight *= data['bottom_bar_width']
        elif blabel == '90-95':
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
    Significant numerical difference means one or more numbers differ (between
    linelist1 and linelist2) by more than the specified small amount.
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
    assert 0.0 <= small <= 1.0
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


def quantity_response(quantity,
                      price_elasticity,
                      aftertax_price1,
                      aftertax_price2,
                      income_elasticity,
                      aftertax_income1,
                      aftertax_income2):
    """
    Calculate dollar change in quantity using a log-log response equation,
    which assumes that the proportional change in the quantity is equal to
    the sum of two terms:
    (1) the proportional change in the quanitity's marginal aftertax price
        times an assumed price elasticity, and
    (2) the proportional change in aftertax income
        times an assumed income elasticity.

    Parameters
    ----------
    quantity: numpy array
        pre-response quantity whose response is being calculated

    price_elasticity: float
        coefficient of the percentage change in aftertax price of
        the quantity in the log-log response equation

    aftertax_price1: numpy array
        marginal aftertax price of the quanitity under baseline policy
          Note that this function forces prices to be in [0.01, inf] range,
          but the caller of this function may want to constrain negative
          or very small prices to be somewhat larger in order to avoid extreme
          proportional changes in price.
          Note this is NOT an array of marginal tax rates (MTR), but rather
            usually 1-MTR (or in the case of quantities, like charitable
            giving, whose MTR values are non-positive, 1+MTR).

    aftertax_price2: numpy array
        marginal aftertax price of the quantity under reform policy
          Note that this function forces prices to be in [0.01, inf] range,
          but the caller of this function may want to constrain negative
          or very small prices to be somewhat larger in order to avoid extreme
          proportional changes in price.
          Note this is NOT an array of marginal tax rates (MTR), but rather
            usually 1-MTR (or in the case of quantities, like charitable
            giving, whose MTR values are non-positive, 1+MTR).

    income_elasticity: float
        coefficient of the percentage change in aftertax income in the
        log-log response equation

    aftertax_income1: numpy array
        aftertax income under baseline policy
          Note that this function forces income to be in [1, inf] range,
          but the caller of this function may want to constrain negative
          or small incomes to be somewhat larger in order to avoid extreme
          proportional changes in aftertax income.

    aftertax_income2: numpy array
        aftertax income under reform policy
          Note that this function forces income to be in [1, inf] range,
          but the caller of this function may want to constrain negative
          or small incomes to be somewhat larger in order to avoid extreme
          proportional changes in aftertax income.

    Returns
    -------
    response: numpy array
        dollar change in quantity calculated from log-log response equation
    """
    # pylint: disable=too-many-arguments
    # compute price term in log-log response equation
    if price_elasticity == 0.:
        pch_price = np.zeros(quantity.shape)
    else:
        atp1 = np.where(aftertax_price1 < 0.01, 0.01, aftertax_price1)
        atp2 = np.where(aftertax_price2 < 0.01, 0.01, aftertax_price2)
        pch_price = atp2 / atp1 - 1.
    # compute income term in log-log response equation
    if income_elasticity == 0.:
        pch_income = np.zeros(quantity.shape)
    else:
        ati1 = np.where(aftertax_income1 < 1.0, 1.0, aftertax_income1)
        ati2 = np.where(aftertax_income2 < 1.0, 1.0, aftertax_income2)
        pch_income = ati2 / ati1 - 1.
    # compute response
    pch_q = price_elasticity * pch_price + income_elasticity * pch_income
    response = pch_q * quantity
    return response


def json_to_dict(json_text):
    """
    Convert specified JSON text into an ordered Python dictionary.

    Parameters
    ----------
    json_text: string
        JSON text.

    Raises
    ------
    ValueError:
        if json_text contains a JSON syntax error.

    Returns
    -------
    dictionary: collections.OrderedDict
        JSON data expressed as an ordered Python dictionary.
    """
    try:
        ordered_dict = json.loads(json_text,
                                  object_pairs_hook=collections.OrderedDict)
    except ValueError as valerr:
        text_lines = json_text.split('\n')
        msg = 'Text below contains invalid JSON:\n'
        msg += str(valerr) + '\n'
        msg += 'Above location of the first error may be approximate.\n'
        msg += 'The invalid JSON text is between the lines:\n'
        bline = ('XXXX----.----1----.----2----.----3----.----4'
                 '----.----5----.----6----.----7')
        msg += bline + '\n'
        linenum = 0
        for line in text_lines:
            linenum += 1
            msg += '{:04d}{}'.format(linenum, line) + '\n'
        msg += bline + '\n'
        raise ValueError(msg)
    return ordered_dict
