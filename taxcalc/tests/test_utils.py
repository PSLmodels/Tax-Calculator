import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
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
