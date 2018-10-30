"""
PRIVATE utility functions for Tax-Calculator PUBLIC utility functions.
"""
# CODING-STYLE CHECKS:
# pycodestyle utilsprvt.py
# pylint --disable=locally-disabled utilsprvt.py


EPSILON = 1e-9


def weighted_count_lt_zero(dframe, col_name, tolerance=-0.001):
    """
    Return weighted count of negative Pandas DataFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
    """
    return dframe[dframe[col_name] < tolerance]['s006'].sum()


def weighted_count_gt_zero(dframe, col_name, tolerance=0.001):
    """
    Return weighted count of positive Pandas DataFrame col_name items.
    If condition is not met by any items, the result of applying sum to an
    empty dataframe is NaN.  This is undesirable and 0 is returned instead.
    """
    return dframe[dframe[col_name] > tolerance]['s006'].sum()


def weighted_count(dframe):
    """
    Return weighted count of items in Pandas DataFrame.
    """
    return dframe['s006'].sum()


def weighted_mean(dframe, col_name):
    """
    Return weighted mean of Pandas DataFrame col_name items.
    """
    return ((dframe[col_name] * dframe['s006']).sum() /
            (dframe['s006'].sum() + EPSILON))


def wage_weighted(dframe, col_name):
    """
    Return wage-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    wage = 'e00200'
    return (((dframe[col_name] * dframe[swght] * dframe[wage]).sum()) /
            ((dframe[swght] * dframe[wage]).sum() + EPSILON))


def agi_weighted(dframe, col_name):
    """
    Return AGI-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    agi = 'c00100'
    return ((dframe[col_name] * dframe[swght] * dframe[agi]).sum() /
            ((dframe[swght] * dframe[agi]).sum() + EPSILON))


def expanded_income_weighted(dframe, col_name):
    """
    Return expanded-income-weighted mean of Pandas DataFrame col_name items.
    """
    swght = 's006'
    expinc = 'expanded_income'
    return ((dframe[col_name] * dframe[swght] * dframe[expinc]).sum() /
            ((dframe[swght] * dframe[expinc]).sum() + EPSILON))
