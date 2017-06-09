"""
PRIVATE utility functions for Tax-Calculator PUBLIC utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 _utils.py
# pylint --disable=locally-disabled _utils.py

import json
import random
import pandas as pd


EPSILON = 1e-9


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


def temporary_filename(suffix=''):
    """
    Return string containing filename.
    """
    return 'tmp{}{}'.format(random.randint(10000000, 99999999), suffix)
