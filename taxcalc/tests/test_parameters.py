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
import taxcalc
from taxcalc import *
from taxcalc.utils import expand_array


@pytest.yield_fixture
def paramsfile():

    txt = """{"_almdep": {"value": [7150, 7250, 7400],
                          "cpi_inflated": true},

             "_almsep": {"value": [40400, 41050],
                         "cpi_inflated": true},

             "_rt5": {"value": [0.33 ],
                      "cpi_inflated": false},

             "_rt7": {"value": [0.396],
                      "cpi_inflated": false}}"""

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(txt + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)

def test_create_parameters():
    p = Parameters()
    assert p

def test_create_parameters_from_file(paramsfile):
    p = Parameters.from_file(paramsfile.name)
    irates = Parameters._Parameters__rates
    assert_array_equal(p._almdep,
                       expand_array(np.array([7150, 7250, 7400]), inflate=True,
                                    inflation_rates=irates, num_years=12))
    assert_array_equal(p._almsep,
                       expand_array(np.array([40400, 41050]), inflate=True,
                                    inflation_rates=irates, num_years=12))
    assert_array_equal(p._rt5,
                       expand_array(np.array([0.33]), inflate=False,
                                    inflation_rates=irates, num_years=12))
    assert_array_equal(p._rt7,
                       expand_array(np.array([0.396]), inflate=False,
                                    inflation_rates=irates, num_years=12))

def test_parameters_get_default(paramsfile):
    paramdata = taxcalc.parameters.default_data()
    assert paramdata['_CDCC_ps'] == [15000]
