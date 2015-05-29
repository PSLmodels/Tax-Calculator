import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
import tempfile
from numba import jit, vectorize, guvectorize
from taxcalc import *
from taxcalc.utils import expand_array

tax_dta_path = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")


def test_create_records():
    r = Records(tax_dta_path)
    assert r


def test_create_records_from_file():
    r = Records.from_file(tax_dta_path)
    assert r


def test_imputation():
	"""
	Just tests the imputation function on scalars
	"""

    # Randomly chosen values for testing
    e17500 = 20.
    e00100 = 40.
    e18400 = 25.
    e18425 = 42.
    e62100 = 75.
    e00700 = 43.3
    e04470 = 21.2
    e21040 = 45.9
    e18500 = 33.1
    e20800 = 0.9

    cmbtp_itemizer = 68.4

    """
    Test case values:

    x = max(0., e17500 - max(0., e00100) * 0.075) = 17.
    y = -1 * min(x, 0.025 * max(0., e00100)) = -1.
    z = max(0, max(e18400, e18425)) = 42.

    _cmbtp_itemizer = (y + e62100 + e00700 + e04470 + e21040 - z - e00100
                       - e18500 - e20800) = 68.4
    """

    test_itemizer = records.imputation(e17500, e00100, e18400, e18425,
    	                               e62100, e00700, e04470,
                                       e21040, e18500, e20800)

    assert(cmbtp_itemizer == test_itemizer)
