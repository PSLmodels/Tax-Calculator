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


def test_blow_up():
    tax_dta = pd.read_csv(tax_dta_path, compression='gzip')
    tax_dta.flpdyr += 18  # 1991 + 18 = 2009 to emulate using 2009 PUF

    params1 = Parameters(start_year=2013)
    records1 = Records(tax_dta)
    assert records1.current_year == 2009
    # r.current_year == 2009 implies Calculator ctor will call r.blowup()

    calc1 = Calculator(records=records1, params=params1)
    assert calc1.current_year == 2013

    # have e aliases of p variables been maintained after several blowups?
    assert calc1.records.e23250.sum() == calc1.records.p23250.sum()
    assert calc1.records.e22250.sum() == calc1.records.p22250.sum()


def test_imputation_of_cmbtp_itemizer():
    e17500 = np.array([20., 4.4, 5.])
    e00100 = np.array([40., 8.1, 90.1])
    e18400 = np.array([25., 34., 10.])
    e62100 = np.array([75., 12.4, 84.])
    e00700 = np.array([43.3, 34.1, 3.4])
    e04470 = np.array([21.2, 12., 13.1])
    e21040 = np.array([45.9, 3., 45.])
    e18500 = np.array([33.1, 18.2, 39.])
    e20800 = np.array([0.9, 32., 52.1])

    cmbtp_itemizer = np.array([85.4, -31.0025, -45.7])

    """
    Test case values:

    x = max(0., e17500 - max(0., e00100) * 0.075) = [17., 3.7925, 0]
    medical_adjustment = min(x, 0.025 * max(0.,e00100)) = [-1.,-.2025,0]
    state_adjustment = max(0, e18400) = [42., 34., 49.]

    _cmbtp_itemizer = (e62100 - medical_adjustment + e00700 + e04470 + e21040
                       - z - e00100 - e18500 - e20800)
                    = [68.4, -31.0025 ,-84.7]
    """

    test_itemizer = records.imputed_cmbtp_itemizer(e17500, e00100, e18400,
                                                   e62100, e00700, e04470,
                                                   e21040, e18500, e20800)
    assert np.allclose(cmbtp_itemizer, test_itemizer)
