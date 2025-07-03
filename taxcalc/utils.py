"""
PUBLIC low-level utility functions for Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pycodestyle utils.py
# pylint --disable=locally-disabled utils.py
#
# pylint: disable=too-many-lines

import os
import re
import math
import json
import copy
import collections
import importlib.resources as implibres
import numpy as np
import pandas as pd
import bokeh.plotting as bp
from bokeh.models import PrintfTickFormatter
from taxcalc.utilsprvt import (weighted_mean,
                               wage_weighted, agi_weighted,
                               expanded_income_weighted)


# Items in the DIST_TABLE_COLUMNS list below correspond to the items in the
# DIST_TABLE_LABELS list below; this correspondence allows us to use this
# labels list to map a label to the correct column in a distribution table.

DIST_VARIABLES = ['expanded_income', 'c00100', 'aftertax_income', 'standard',
                  'c04470', 'c04600', 'c04800', 'taxbc', 'c62100', 'c09600',
                  'c05800', 'surtax', 'othertaxes', 'refund', 'c07100',
                  'iitax', 'payrolltax', 'combined', 's006', 'ubi',
                  'benefit_cost_total', 'benefit_value_total', 'XTOT']

DIST_TABLE_COLUMNS = ['count',
                      'c00100',
                      'count_StandardDed',
                      'standard',
                      'count_ItemDed',
                      'c04470',
                      'c04600',
                      'c04800',
                      'taxbc',
                      'c62100',
                      'count_AMT',
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

DIST_TABLE_LABELS = ['Number of Returns',
                     'AGI',
                     'Number of Returns Claiming Standard Deduction',
                     'Standard Deduction',
                     'Number of Returns Itemizing',
                     'Itemized Deduction',
                     'Personal Exemption',
                     'Taxable Income',
                     'Regular Tax',
                     'AMTI',
                     'Number of Returns with AMT',
                     'AMT',
                     'Tax before Credits',
                     'Non-refundable Credits',
                     'Other Taxes',
                     'Refundable Credits',
                     'Individual Income Tax Liabilities',
                     'Payroll Tax Liabilities',
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
                  'iitax', 'payrolltax', 'combined', 's006', 'XTOT',
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

DIFF_TABLE_LABELS = ['Number of Returns',
                     'Number of Returns with Tax Cut',
                     'Percent with Tax Cut',
                     'Number of Returns with Tax Increase',
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
                                    pop_quantiles=False,
                                    decile_details=False,
                                    weight_by_income_measure=False):
    """
    Add a variable to specified Pandas DataFrame, dframe, that specifies
    the table row and is called 'table_row'.

    When weight_by_income_measure=False, the rows hold an equal number of
    people if pop_quantiles=True or an equal number of filing units if
    pop_quantiles=False.

    When weight_by_income_measure=True, the rows hold an equal number
    of income dollars.

    This function assumes that specified dframe contains columns for
    the specified income_measure and for sample weights, s006, and when
    pop_quantiles=True, number of exemptions, XTOT.

 .  When num_quantiles is 10 and decile_details is True,
    the bottom decile is broken up into three subgroups
    (neg, zero, and pos income_measure)
    and the top decile is broken into three subgroups
    (90-95, 95-99, and top 1%).
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-locals
    assert isinstance(dframe, pd.DataFrame)
    assert income_measure in dframe
    assert 's006' in dframe
    if decile_details and num_quantiles != 10:
        msg = 'decile_details is True when num_quantiles is {}'
        raise ValueError(msg.format(num_quantiles))
    if pop_quantiles:
        assert not weight_by_income_measure
        assert 'XTOT' in dframe
        # adjust income measure by square root of filing unit size
        adj = np.sqrt(np.where(dframe['XTOT'] == 0, 1, dframe['XTOT']))
        dframe['adj_income_measure'] = np.divide(dframe[income_measure], adj)
    else:
        dframe['adj_income_measure'] = dframe[income_measure]
    dframe.sort_values(by='adj_income_measure', inplace=True)
    if weight_by_income_measure:
        dframe['cumsum_temp'] = np.cumsum(
            np.multiply(dframe[income_measure].values, dframe['s006'].values)
        )
        min_cumsum = dframe['cumsum_temp'].values[0]
    else:
        if pop_quantiles:
            dframe['cumsum_temp'] = np.cumsum(
                np.multiply(dframe['XTOT'].values, dframe['s006'].values)
            )
        else:
            dframe['cumsum_temp'] = np.cumsum(
                dframe['s006'].values
            )
        min_cumsum = 0.  # because s006 and XTOT values are non-negative
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
        neg_im = np.less_equal(dframe[income_measure], -1e-9)
        neg_wght = dframe['s006'][neg_im].sum()
        zer_im = np.logical_and(
            np.greater(dframe[income_measure], -1e-9),
            np.less(dframe[income_measure], 1e-9)
        )
        zer_wght = dframe['s006'][zer_im].sum()
        bin_edges.insert(1, neg_wght + zer_wght)  # top of zeros
        bin_edges.insert(1, neg_wght)  # top of negatives
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
    sums = {}
    for col in dframe.columns.values.tolist():
        if col != 'table_row':
            sums[col] = dframe[col].sum()
    return pd.Series(sums, name='ALL')


def create_distribution_table(vdf, groupby, income_measure,
                              pop_quantiles=False, scaling=True):
    """
    Get results from vdf, sort them by expanded_income based on groupby,
    and return them as a table.

    Parameters
    ----------
    vdf : Pandas DataFrame including columns named in DIST_TABLE_COLUMNS list
        for example, an object returned from the distribution_table_dataframe
        function in the Calculator distribution_tables method

    groupby : String object
        options for input: 'weighted_deciles' or
                           'standard_income_bins' or 'soi_agi_bins'
        determines how the rows in the resulting Pandas DataFrame are sorted

    income_measure: String object
        options for input: 'expanded_income' or 'expanded_income_baseline'
        determines which variable is used to sort rows

    pop_quantiles : boolean
        specifies whether or not weighted_deciles contain an equal number
        of people (True) or an equal number of filing units (False)

    scaling : boolean
        specifies whether or not table entry values are scaled

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
        unweighted_columns = ['count', 'count_StandardDed',
                              'count_ItemDed', 'count_AMT']
        sdf = pd.DataFrame()
        for col in DIST_TABLE_COLUMNS:
            if col in unweighted_columns:
                sdf[col] = gdf.apply(
                    unweighted_sum, col, include_groups=False
                ).values[:, 1]
            else:
                sdf[col] = gdf.apply(
                    weighted_sum, col, include_groups=False
                ).values[:, 1]
        return sdf
    # main logic of create_distribution_table
    assert isinstance(vdf, pd.DataFrame)
    assert groupby in ('weighted_deciles',
                       'standard_income_bins',
                       'soi_agi_bins')
    assert income_measure in ('expanded_income', 'expanded_income_baseline')
    assert income_measure in vdf
    assert 'table_row' not in vdf
    if pop_quantiles:
        assert groupby == 'weighted_deciles'
    # sort the data given specified groupby and income_measure
    dframe = None
    if groupby == 'weighted_deciles':
        dframe = add_quantile_table_row_variable(vdf, income_measure, 10,
                                                 pop_quantiles=pop_quantiles,
                                                 decile_details=True)
    elif groupby == 'standard_income_bins':
        dframe = add_income_table_row_variable(vdf, income_measure,
                                               STANDARD_INCOME_BINS)
    elif groupby == 'soi_agi_bins':
        dframe = add_income_table_row_variable(vdf, income_measure,
                                               SOI_AGI_BINS)
    # construct grouped DataFrame
    gdf = dframe.groupby('table_row', observed=False, as_index=False)
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
        dist_table.iloc[15] = dist_table.iloc[13]
        dist_table.iloc[14] = dist_table.iloc[12]
        dist_table.iloc[13] = dist_table.iloc[11]
        dist_table.iloc[12] = sum_row
        dist_table.iloc[11] = topdec_row
        del topdec_row
    else:
        dist_table.loc["ALL"] = sum_row
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
        count_vars = ['count',
                      'count_StandardDed',
                      'count_ItemDed',
                      'count_AMT']
        for col in dist_table.columns:
            # if col in count_vars:
            #     dist_table[col] = np.round(dist_table[col] * 1e-6, 2)
            # else:
            #     dist_table[col] = np.round(dist_table[col] * 1e-9, 3)
            if col in count_vars:
                dist_table[col] *= 1e-6
                dist_table.round({col: 2})
            else:
                dist_table[col] *= 1e-9
                dist_table.round({col: 3})
    # return table as Pandas DataFrame
    vdf.sort_index(inplace=True)
    return dist_table


def create_difference_table(vdf1, vdf2, groupby, tax_to_diff,
                            pop_quantiles=False):
    """
    Get results from two different vdf, construct tax difference results,
    and return the difference statistics as a table.

    Parameters
    ----------
    vdf1 : Pandas DataFrame including columns named in DIFF_VARIABLES list
           for example, object returned from a dataframe(DIFF_VARIABLES) call
           on the basesline Calculator object

    vdf2 : Pandas DataFrame including columns in the DIFF_VARIABLES list
           for example, object returned from a dataframe(DIFF_VARIABLES) call
           on the reform Calculator object

    groupby : String object
        options for input: 'weighted_deciles' or
                           'standard_income_bins' or 'soi_agi_bins'
        determines how the rows in the resulting Pandas DataFrame are sorted

    tax_to_diff : String object
        options for input: 'iitax', 'payrolltax', 'combined'
        specifies which tax to difference

    pop_quantiles : boolean
        specifies whether or not weighted_deciles contain an equal number
        of people (True) or an equal number of filing units (False)

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
        def count_lt_zero(dframe, col_name, tolerance=-0.001):
            """
            Return count sum of negative Pandas DataFrame col_name items.
            """
            return dframe[dframe[col_name] < tolerance]['count'].sum()

        def count_gt_zero(dframe, col_name, tolerance=0.001):
            """
            Return count sum of positive Pandas DataFrame col_name items.
            """
            return dframe[dframe[col_name] > tolerance]['count'].sum()
        # start of additive_stats_dataframe code
        sdf = pd.DataFrame()
        sdf['count'] = gdf.apply(
            unweighted_sum, 'count', include_groups=False
        ).values[:, 1]
        sdf['tax_cut'] = gdf.apply(
            count_lt_zero, 'tax_diff', include_groups=False
        ).values[:, 1]
        sdf['tax_inc'] = gdf.apply(
            count_gt_zero, 'tax_diff', include_groups=False
        ).values[:, 1]
        sdf['tot_change'] = gdf.apply(
            weighted_sum, 'tax_diff', include_groups=False
        ).values[:, 1]
        sdf['ubi'] = gdf.apply(
            weighted_sum, 'ubi', include_groups=False
        ).values[:, 1]
        sdf['benefit_cost_total'] = gdf.apply(
            weighted_sum, 'benefit_cost_total', include_groups=False
        ).values[:, 1]
        sdf['benefit_value_total'] = gdf.apply(
            weighted_sum, 'benefit_value_total', include_groups=False
        ).values[:, 1]
        sdf['atinc1'] = gdf.apply(
            weighted_sum, 'atinc1', include_groups=False
        ).values[:, 1]
        sdf['atinc2'] = gdf.apply(
            weighted_sum, 'atinc2', include_groups=False
        ).values[:, 1]
        return sdf
    # main logic of create_difference_table
    assert groupby in ('weighted_deciles',
                       'standard_income_bins',
                       'soi_agi_bins')
    if pop_quantiles:
        assert groupby == 'weighted_deciles'
    assert 'expanded_income' in vdf1
    assert tax_to_diff in ('iitax', 'payrolltax', 'combined')
    assert 'table_row' not in vdf1
    assert 'table_row' not in vdf2
    assert isinstance(vdf1, pd.DataFrame)
    assert isinstance(vdf2, pd.DataFrame)
    assert np.allclose(vdf1['XTOT'], vdf2['XTOT'])  # check rows are the same
    assert np.allclose(vdf1['s006'], vdf2['s006'])  # units and in same order
    baseline_expanded_income = 'expanded_income_baseline'
    df2 = copy.deepcopy(vdf2)
    df2[baseline_expanded_income] = vdf1['expanded_income']
    df2['tax_diff'] = df2[tax_to_diff] - vdf1[tax_to_diff]
    for col in ['ubi', 'benefit_cost_total', 'benefit_value_total']:
        df2[col] = df2[col] - vdf1[col]
    df2['atinc1'] = vdf1['aftertax_income']
    df2['atinc2'] = vdf2['aftertax_income']
    # specify count variable in df2
    if pop_quantiles:
        df2['count'] = np.multiply(df2['s006'], df2['XTOT'])

    else:
        df2['count'] = df2['s006']
    # add table_row column to df2 given specified groupby and income_measure
    dframe = None
    if groupby == 'weighted_deciles':
        dframe = add_quantile_table_row_variable(
            df2, baseline_expanded_income, 10,
            pop_quantiles=pop_quantiles, decile_details=True)
    elif groupby == 'standard_income_bins':
        dframe = add_income_table_row_variable(
            df2, baseline_expanded_income, STANDARD_INCOME_BINS)
    elif groupby == 'soi_agi_bins':
        dframe = add_income_table_row_variable(
            df2, baseline_expanded_income, SOI_AGI_BINS)
    del df2
    # create grouped Pandas DataFrame
    gdf = dframe.groupby('table_row', as_index=False, observed=False)
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
        diff_table.iloc[15] = diff_table.iloc[13]
        diff_table.iloc[14] = diff_table.iloc[12]
        diff_table.iloc[13] = diff_table.iloc[11]
        diff_table.iloc[12] = sum_row
        diff_table.iloc[11] = topdec_row
        del topdec_row
    else:
        diff_table.loc["ALL"] = sum_row
    # delete intermediate Pandas DataFrame objects
    del gdf
    del dframe
    # compute non-additive stats in each table cell
    count = diff_table['count'].values
    diff_table['perc_cut'] = np.divide(
        100 * diff_table['tax_cut'].values, count,
        out=np.zeros_like(diff_table['tax_cut'].values),
        where=count > 0)
    diff_table['perc_inc'] = np.divide(
        100 * diff_table['tax_inc'].values, count,
        out=np.zeros_like(diff_table['tax_inc'].values),
        where=count > 0)
    diff_table['mean'] = np.divide(
        diff_table['tot_change'].values, count,
        out=np.zeros_like(diff_table['tot_change'].values),
        where=count > 0)
    total_change = sum_row['tot_change']
    diff_table['share_of_change'] = np.divide(
        100 * diff_table['tot_change'].values, total_change,
        out=np.zeros_like(diff_table['tot_change'].values),
        where=total_change > 0)
    quotient = np.divide(
        diff_table['atinc2'].values, diff_table['atinc1'].values,
        out=np.zeros_like(diff_table['atinc2'].values),
        where=diff_table['atinc1'].values != 0)
    diff_table['pc_aftertaxinc'] = np.where(
        diff_table['atinc1'].values == 0., np.nan, 100 * (quotient - 1))
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
    count_vars = ['count', 'tax_cut', 'tax_inc']
    scale_vars = ['tot_change', 'ubi',
                  'benefit_cost_total', 'benefit_value_total']
    for col in diff_table.columns:
        if col in count_vars:
            diff_table[col] *= 1e-6
            diff_table.round({col: 2})
        elif col in scale_vars:
            diff_table[col] *= 1e-9
            diff_table.round({col: 3})
        else:
            diff_table.round({col: 1})
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
        val = wghts[vdf['c04470'] > 0.].sum()
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
        # UBI benefits
        val = (vdf['ubi'] * wghts).sum()
        odict['UBI Benefits ($b)'] = round(val * in_billions, 3)
        # Total consumption value of benefits
        val = (vdf['benefit_value_total'] * wghts).sum()
        odict['Total Benefits, Consumption Value ($b)'] = round(
            val * in_billions, 3)
        # Total dollar cost of benefits
        val = (vdf['benefit_cost_total'] * wghts).sum()
        odict['Total Benefits Cost ($b)'] = round(val * in_billions, 3)
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
    tlist = []
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
                   pop_quantiles=False,
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

    pop_quantiles : boolean
        specifies whether or not quantiles contain an equal number
        of people (True) or an equal number of filing units (False)

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
    # pylint: disable=too-many-arguments,,too-many-positional-arguments
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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
    # . . check pop_quantiles and dollar_weighting
    if pop_quantiles:
        assert not dollar_weighting
    # create 'table_row' column given specified income_var and dollar_weighting
    dfx = add_quantile_table_row_variable(
        vdf, income_var, 100,
        pop_quantiles=pop_quantiles,
        weight_by_income_measure=dollar_weighting
    )
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', observed=False, as_index=False)
    # apply the weighting_function to percentile-grouped mtr values
    mtr1_series = gdfx.apply(
        weighting_function, 'mtr1', include_groups=False
    ).values[:, 1]
    mtr2_series = gdfx.apply(
        weighting_function, 'mtr2', include_groups=False
    ).values[:, 1]
    # construct DataFrame containing the two mtr?_series
    lines = pd.DataFrame()
    lines['base'] = np.round(mtr1_series, decimals=4)
    lines['reform'] = np.round(mtr2_series, decimals=4)
    # construct dictionary containing merged data and auto-generated labels
    data = {}
    data['lines'] = lines
    if dollar_weighting:
        income_str = f'Dollar-weighted {income_str}'
        mtr_str = f'Dollar-weighted {mtr_str}'
    data['ylabel'] = f'{mtr_str} MTR'
    xlabel_str = f'Baseline {income_str} Percentile'
    if mars != 'ALL':
        xlabel_str = f'{xlabel_str} for MARS={mars}'
    data['xlabel'] = xlabel_str
    var_str = f'{mtr_variable}'
    if mtr_variable == 'e00200p' and alt_e00200p_text != '':
        var_str = f'{alt_e00200p_text}'
    if mtr_variable == 'e00200p' and mtr_wrt_full_compen:
        var_str = f'{var_str} wrt full compensation'
    title_str = f'Mean Marginal Tax Rate for {var_str} by Income Percentile'
    if mars != 'ALL':
        title_str = f'{title_str} for MARS={mars}'
    title_str = f'{title_str} for {year}'
    data['title'] = title_str
    return data


def atr_graph_data(vdf, year,
                   mars='ALL',
                   atr_measure='combined',
                   pop_quantiles=False):
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

    pop_quantiles : boolean
        specifies whether or not quantiles contain an equal number
        of people (True) or an equal number of filing units (False)

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
    dfx = add_quantile_table_row_variable(vdf, 'expanded_income', 100,
                                          pop_quantiles=pop_quantiles)
    # specify which 'table_row' are included
    include = [0] * num_bins_with_nonpos + [1] * (100 - num_bins_with_nonpos)
    included = np.array(include, dtype=bool)
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', observed=False, as_index=False)
    # apply weighted_mean function to percentile-grouped values
    avginc_series = gdfx.apply(
        weighted_mean, 'expanded_income', include_groups=False
    ).values[:, 1]
    avgtax1_series = gdfx.apply(
        weighted_mean, 'tax1', include_groups=False
    ).values[:, 1]
    avgtax2_series = gdfx.apply(
        weighted_mean, 'tax2', include_groups=False
    ).values[:, 1]
    # compute average tax rates for each included income percentile
    atr1_series = np.zeros(avginc_series.shape)
    atr1_series[included] = np.divide(
        avgtax1_series[included], avginc_series[included],
        out=np.zeros_like(avgtax1_series[included]),
        where=avginc_series[included] != 0)
    atr2_series = np.zeros(avginc_series.shape)
    atr2_series[included] = np.divide(
        avgtax2_series[included], avginc_series[included],
        out=np.zeros_like(avgtax2_series[included]),
        where=avginc_series[included] != 0)
    # construct DataFrame containing the two atr?_series
    lines = pd.DataFrame()
    lines['base'] = np.round(atr1_series, decimals=4)
    lines['reform'] = np.round(atr2_series, decimals=4)
    # include only percentiles with average income no less than min_avginc
    lines = lines[included]
    # construct dictionary containing plot lines and auto-generated labels
    data = {}
    data['lines'] = lines
    data['ylabel'] = f'{atr_str} Average Tax Rate'
    xlabel_str = 'Baseline Expanded-Income Percentile'
    if mars != 'ALL':
        xlabel_str = f'{xlabel_str} for MARS={mars}'
    data['xlabel'] = xlabel_str
    title_str = 'Average Tax Rate by Income Percentile'
    if mars != 'ALL':
        title_str = f'{title_str} for MARS={mars}'
    title_str = f'{title_str} for {year}'
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

      bp.output_file('graph-name.html', title='?TR by Income Percentile')
      bp.show(gplot)  [OR bp.save(gplot) WILL JUST WRITE FILE TO DISK]

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
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    if title == '':
        title = data['title']
    fig = bp.figure(width=width, height=height, title=title)
    fig.title.text_font_size = '12pt'
    lines = data['lines']
    fig.line(lines.index, lines.base,
             line_color='blue', line_width=3, legend_label='Baseline')
    fig.line(lines.index, lines.reform,
             line_color='red', line_width=3, legend_label='Reform')
    fig.scatter(0, 0, visible=False)  # force zero to be included on y axis
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


def pch_graph_data(vdf, year, pop_quantiles=False):
    """
    Prepare percentage change in after-tax expanded income data needed by
    pch_graph_plot utility function.

    Parameters
    ----------
    vdf : a Pandas DataFrame object containing variables
        (See Calculator.pch_graph method for required elements of vdf.)

    year : integer
        specifies calendar year of the data in vdf

    pop_quantiles : boolean
        specifies whether or not quantiles contain an equal number
        of people (True) or an equal number of filing units (False)

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
    dfx = add_quantile_table_row_variable(vdf, 'expanded_income', 100,
                                          pop_quantiles=pop_quantiles)
    # specify which 'table_row' are included
    include = [0] * num_bins_with_nonpos + [1] * (100 - num_bins_with_nonpos)
    included = np.array(include, dtype=bool)
    # split dfx into groups specified by 'table_row' column
    gdfx = dfx.groupby('table_row', observed=False, as_index=False)
    # apply weighted_mean function to percentile-grouped values
    avginc_series = gdfx.apply(
        weighted_mean, 'expanded_income', include_groups=False
    ).values[:, 1]
    change_series = gdfx.apply(
        weighted_mean, 'chg_aftinc', include_groups=False
    ).values[:, 1]
    # compute percentage change statistic each included income percentile
    pch_series = np.zeros(avginc_series.shape)
    pch_series[included] = np.divide(
        change_series[included], avginc_series[included],
        out=np.zeros_like(change_series[included]),
        where=avginc_series[included] != 0)
    # construct DataFrame containing the pch_series expressed as percent
    line = pd.DataFrame()
    line['pch'] = np.round(pch_series * 100, decimals=2)
    # include only percentiles with average income no less than min_avginc
    line = line[included]
    # construct dictionary containing plot line and auto-generated labels
    data = {}
    data['line'] = line
    data['ylabel'] = 'Change in After-Tax Expanded Income'
    data['xlabel'] = 'Baseline Expanded-Income Percentile'
    title_str = ('Percentage Change in After-Tax Expanded Income '
                 'by Income Percentile')
    title_str = f'{title_str} for {year}'
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
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    if title == '':
        title = data['title']
    fig = bp.figure(width=width, height=height, title=title)
    fig.title.text_font_size = '12pt'
    line = data['line']
    fig.line(line.index, line.pch, line_color='blue', line_width=3)
    fig.scatter(0, 0, visible=False)  # force zero to be included on y axis
    zero_grid_line_range = line.index
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
    fig.yaxis[0].formatter = PrintfTickFormatter(format='%.1f')
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
    delete_file(filename)
    if figure:
        bp.output_file(filename=filename, title=title)
        bp.save(figure)


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
    responses that change work effort will not affect utility via the
    correpsonding change in leisure.  And any saving response to changes
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
    cedict = {}
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
    prob_raw = np.divide(df1['s006'], df1['s006'].sum())
    # handle any rounding error in probability calculation
    prob = np.divide(prob_raw, prob_raw.sum())
    # calculate after-tax income of each filing unit in df1 and df2
    ati1 = df1['expanded_income'] - df1['combined']
    ati2 = df2['expanded_income'] - df2['combined']
    # calculate certainty-equivaluent after-tax income in df1 and df2
    cedict['crra'] = crras
    ce1 = []
    ce2 = []
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
        path_in_egg = implibres.files('taxcalc').joinpath(fname)
        with implibres.as_file(path_in_egg) as rname:
            vdf = pd.read_csv(rname, index_col=index_col)
    except Exception as exc:
        raise ValueError(f'could not read {fname} data from egg') from exc
    # cannot call read_egg_ function in unit tests
    return vdf  # pragma: no cover


def read_egg_json(fname):
    """
    Read from egg the file named fname that contains JSON data and
    return dictionary containing the data.
    """
    try:
        path_in_egg = implibres.files('taxcalc').joinpath(fname)
        with implibres.as_file(path_in_egg) as rname:
            pdict = json.loads(rname)
    except Exception as exc:
        raise ValueError(f'could not read {fname} data from package') from exc
    # cannot call read_egg_ function in pytest unit tests
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
    bsest = {}
    bsest['seed'] = seed
    np.random.seed(seed)
    dlen = len(data)
    idx = np.random.randint(low=0, high=dlen, size=(num_samples, dlen))
    samples = data[idx]
    stat = statistic(samples, axis=1)
    bsest['B'] = num_samples
    bsest['se'] = np.std(stat, ddof=1)
    stat = np.sort(stat)
    bsest['alpha'] = alpha
    bsest['cilo'] = stat[int(round(alpha * num_samples)) - 1]
    bsest['cihi'] = stat[int(round((1 - alpha) * num_samples)) - 1]
    return bsest


def json_to_dict(jsontext):
    """
    Convert specified JSON text into an ordered Python dictionary.

    Parameters
    ----------
    jsontext: string
        JSON text that may contain comments, which will be removed

    Raises
    ------
    ValueError:
        if jsontext contains a JSON syntax error after comments are removed

    Returns
    -------
    dictionary: collections.OrderedDict
        JSON data expressed as an ordered Python dictionary
    """
    def remove_comments(string):
        """
        Remove single and multiline comments from JSON.
        Logic follows https://stackoverflow.com/a/18381470/9100772
        """
        def _replacer(match):
            # if the 2nd group (capturing comments) is not None,
            # it means we have captured a non-quoted (real) comment string.
            if match.group(2) is not None:
                return "\n"  # preserve line numbers
            # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string
        # begin main remove_comments function logic
        pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
        # first group captures quoted strings (double or single)
        # second group captures comments (//single-line or /* multi-line */)
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
        return regex.sub(_replacer, string)
    # begin main json_to_dict function logic
    json_text = remove_comments(jsontext)
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
            msg += f'{linenum:04d}{line}\n'
        msg += bline + '\n'
        msg += 'If still puzzled, try using JSONLint online.\n'
        raise ValueError(msg) from valerr
    return ordered_dict
