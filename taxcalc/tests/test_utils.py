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

@extract_array
@vectorize(['int32(int32)'])
def fnvec_ifelse_df(inc_in):
    ans = -42
    if inc_in < 5:
        ans = -42
    if inc_in >= 5 and inc_in < 8:
        ans = 42
    if inc_in >= 8:
        ans = 99
    return ans


@dataframe_vectorize(['int32(int32)'])
def fnvec_ifelse_df2(inc_in):
    """Docstring"""
    ans = -42
    if inc_in < 5:
        ans = -42
    if inc_in >= 5 and inc_in < 8:
        ans = 42
    if inc_in >= 8:
        ans = 99
    return ans


@extract_array
@guvectorize(["void(int32[:],int32[:])"], "(x) -> (x)")
def fnvec_copy_df(inc_in, inc_out):
    for i in range(inc_in.shape[0]):
        inc_out[i] = inc_in[i]


@dataframe_guvectorize(["void(int32[:],int32[:])"], "(x) -> (x)")
def fnvec_copy_df2(inc_in, inc_out):
    """Docstring"""
    for i in range(inc_in.shape[0]):
        inc_out[i] = inc_in[i]


def test_with_df_wrapper():
    x = np.array([4, 5, 9], dtype='i4')
    y = np.array([0, 0, 0], dtype='i4')
    df = pd.DataFrame(data=np.column_stack((x, y)), columns=['x', 'y'])

    fnvec_copy_df(df.x, df.y)
    assert np.all(df.x.values == df.y.values)

    z = fnvec_ifelse_df(df.x)
    assert np.all(np.array([-42, 42, 99], dtype='i4') == z)


def test_with_dataframe_guvec():
    x = np.array([4, 5, 9], dtype='i4')
    y = np.array([0, 0, 0], dtype='i4')
    df = pd.DataFrame(data=np.column_stack((x, y)), columns=['x', 'y'])
    fnvec_copy_df2(df.x, df.y)
    assert fnvec_copy_df2.__name__ == 'fnvec_copy_df2'
    assert fnvec_copy_df2.__doc__ == 'Docstring'
    assert np.all(df.x.values == df.y.values)


def test_with_dataframe_vec():
    x = np.array([4, 5, 9], dtype='i4')
    y = np.array([0, 0, 0], dtype='i4')
    df = pd.DataFrame(data=np.column_stack((x, y)), columns=['x', 'y'])

    z = fnvec_ifelse_df2(df.x)
    assert fnvec_ifelse_df2.__name__ == 'fnvec_ifelse_df2'
    assert fnvec_ifelse_df2.__doc__ == 'Docstring'
    assert np.all(np.array([-42, 42, 99], dtype='i4') == z)


@dataframe_wrap_guvectorize(["void(int32[:],int32[:])"], "(x) -> (x)")
def fnvec_copy_dfw(x, y):
    for i in range(x.shape[0]):
        y[i] = x[i]


def test_with_dataframe_wrap_guvectorize():
    x = np.array([4, 5, 9], dtype='i4')
    y = np.array([0, 0, 0], dtype='i4')
    df = pd.DataFrame(data=np.column_stack((x, y)), columns=['x', 'y'])
    fnvec_copy_dfw(df)
    assert(np.all(df.x == df.y))


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


@apply_jit("a, b", "x, y, z", nopython=True)
def Magic_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


def Magic(pm, pf):
    # Adjustments
    outputs = \
        pf.a, pf.b = \
            Magic_calc(pm, pf)

    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs),
                     columns=header)

class Foo(object):
    pass


def test_magic():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=["a", "b"])
    assert_frame_equal(xx, exp)
