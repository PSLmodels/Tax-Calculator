import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from numba import jit, vectorize, guvectorize
from taxcalc import *


def test_expand_1D_short_array():
    x = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = expand_1D(x)
    assert(np.allclose(exp.astype(x.dtype, casting='unsafe'), res))


def test_expand_1D_scalar():
    x = 10.0
    exp = np.array([10.0 * math.pow(1.02, i) for i in range(0, 10)])
    res = expand_1D(x)
    assert(np.allclose(exp, res))


def test_expand_2D_short_array():
    x = np.array([[1, 2, 3]], dtype='f8')
    val = np.array([1, 2, 3], dtype='f8')
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, num_years=5)
    assert(np.allclose(exp, res))
