"""
PRIVATE utility functions for Tax-Calculator PUBLIC utility functions.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 _utils.py
# pylint --disable=locally-disabled _utils.py


EPSILON = 1e-9


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
