"""
PRIVATE utility functions for Tax-Calculator PUBLIC utility functions.
"""
# CODING-STYLE CHECKS:
# pycodestyle utilsprvt.py
# pylint --disable=locally-disabled utilsprvt.py


EPSILON = 1e-9


def weighted_count_lt_zero(pdf, col_name, tolerance=-0.001):
    """
    Return weighted count of negative Pandas DataFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
    """
    return pdf[pdf[col_name] < tolerance]['s006'].sum()


def weighted_count_gt_zero(pdf, col_name, tolerance=0.001):
    """
    Return weighted count of positive Pandas DataFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
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
    return ((pdf[col_name] * pdf['s006']).sum() /
            (pdf['s006'].sum() + EPSILON))


def wage_weighted(pdf, col_name):
    """
    Return wage-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    wage = 'e00200'
    return (((pdf[col_name] * pdf[swght] * pdf[wage]).sum()) /
            ((pdf[swght] * pdf[wage]).sum() + EPSILON))


def agi_weighted(pdf, col_name):
    """
    Return AGI-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    agi = 'c00100'
    return ((pdf[col_name] * pdf[swght] * pdf[agi]).sum() /
            ((pdf[swght] * pdf[agi]).sum() + EPSILON))


def expanded_income_weighted(pdf, col_name):
    """
    Return expanded-income-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    expinc = 'expanded_income'
    return ((pdf[col_name] * pdf[swght] * pdf[expinc]).sum() /
            ((pdf[swght] * pdf[expinc]).sum() + EPSILON))
