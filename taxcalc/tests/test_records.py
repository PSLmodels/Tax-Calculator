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
from taxcalc.records import NAMES

tax_dta_path = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")


def test_create_records_withdata():
    r = Records(tax_dta_path)
    assert r


def test_create_records_from_file():
    r = Records.from_file(tax_dta_path)
    assert r


def test_create_blank_records():
    r = Records(dims=1)
    assert r
    for attr in NAMES:
        assert getattr(r, attr[0]) == 0


def test_create_personal_record():
    r = Records(dims=1)
    r.set_attr("e00100", 1000)
    assert r.e00100 == 1000


def test_imputation():
    e17500 = np.array([20., 4.4, 5.])
    e00100 = np.array([40., 8.1, 90.1])
    e18400 = np.array([25., 34., 10.])
    e18425 = np.array([42., 20.3, 49.])
    e62100 = np.array([75., 12.4, 84.])
    e00700 = np.array([43.3, 34.1, 3.4])
    e04470 = np.array([21.2, 12., 13.1])
    e21040 = np.array([45.9, 3., 45.])
    e18500 = np.array([33.1, 18.2, 39.])
    e20800 = np.array([0.9, 32., 52.1])

    cmbtp_itemizer = np.array([68.4, -31.0025, -84.7])

    """
    Test case values:

    x = max(0., e17500 - max(0., e00100) * 0.075) = [17., 3.7925, 0]
    medical_adjustment = min(x, 0.025 * max(0.,e00100)) = [-1.,-.2025,0]
    state_adjustment = max(0, max(e18400, e18425)) = [42., 34., 49.]

    _cmbtp_itemizer = (e62100 - medical_adjustment + e00700 + e04470 + e21040
                       - z - e00100 - e18500 - e20800)
                    = [68.4, -31.0025 ,-84.7]
    """

    test_itemizer = records.imputation(e17500, e00100, e18400, e18425,
                                       e62100, e00700, e04470,
                                       e21040, e18500, e20800)

    assert(np.allclose(cmbtp_itemizer, test_itemizer))
