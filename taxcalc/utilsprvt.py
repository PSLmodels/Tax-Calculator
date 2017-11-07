"""
PRIVATE utility functions for Tax-Calculator PUBLIC utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 utilsprvt.py
# pylint --disable=locally-disabled utilsprvt.py

import numpy as np


EPSILON = 1e-9


def weighted_count_lt_zero(pdf, col_name, tolerance=-0.001):
    """
    Return weighted count of negative Pandas DateFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
    """
    return pdf[pdf[col_name] < tolerance]['s006'].zsum()


def weighted_count_gt_zero(pdf, col_name, tolerance=0.001):
    """
    Return weighted count of positive Pandas DateFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
    """
    return pdf[pdf[col_name] > tolerance]['s006'].zsum()


def weighted_count(pdf):
    """
    Return weighted count of items in Pandas DataFrame.
    """
    return pdf['s006'].zsum()


def weighted_mean(pdf, col_name):
    """
    Return weighted mean of Pandas DataFrame col_name items.
    """
    if len(pdf) > 0:
        return ((pdf[col_name] * pdf['s006']).zsum() /
                (pdf['s006'].zsum() + EPSILON))
    else:
        return 0


def wage_weighted(pdf, col_name):
    """
    Return wage-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    wage = 'e00200'
    return (((pdf[col_name] * pdf[swght] * pdf[wage]).zsum()) /
            ((pdf[swght] * pdf[wage]).zsum() + EPSILON))


def agi_weighted(pdf, col_name):
    """
    Return AGI-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    agi = 'c00100'
    return ((pdf[col_name] * pdf[swght] * pdf[agi]).zsum() /
            ((pdf[swght] * pdf[agi]).zsum() + EPSILON))


def expanded_income_weighted(pdf, col_name):
    """
    Return expanded-income-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    expinc = 'expanded_income'
    return ((pdf[col_name] * pdf[swght] * pdf[expinc]).zsum() /
            ((pdf[swght] * pdf[expinc]).zsum() + EPSILON))


def weighted_perc_inc(pdf, col_name):
    """
    Return weighted fraction (not percent) of positive values for the
    variable with col_name in the specified Pandas DataFrame.
    """
    return (weighted_count_gt_zero(pdf, col_name) /
            (weighted_count(pdf) + EPSILON))


def weighted_perc_cut(pdf, col_name):
    """
    Return weighted fraction (not percent) of negative values for the
    variable with col_name in the specified Pandas DataFrame.
    """
    return (weighted_count_lt_zero(pdf, col_name) /
            (weighted_count(pdf) + EPSILON))
