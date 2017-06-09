"""
Utility functions used in taxcalc/filings/forms logic.
"""


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
