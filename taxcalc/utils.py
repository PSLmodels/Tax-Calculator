import numpy as np
import pandas as pd
from numba import jit, vectorize, guvectorize


def extract_array(f):
    """
    A sanity check decorator. When combined with numba.vectorize
    or guvectorize, it provides the same capability as dataframe_vectorize
    or dataframe_guvectorize
    """
    def wrapper(*args, **kwargs):
        arrays = [arg.values for arg in args]
        return f(*arrays)
    return wrapper


def dataframe_guvectorize(dtype_args, dtype_sig):
    """
    Extracts numpy arrays from caller arguments and passes them
    to guvectorized numba functions
    """
    def make_wrapper(func):
        vecd_f = guvectorize(dtype_args, dtype_sig)(func)

        def wrapper(*args, **kwargs):
            # np_arrays = [getattr(args[0], i).values for i in theargs]
            arrays = [arg.values for arg in args]
            ans = vecd_f(*arrays)
            return ans
        return wrapper
    return make_wrapper


def dataframe_vectorize(dtype_args):
    """
    Extracts numpy arrays from caller arguments and passes them
    to vectorized numba functions
    """
    def make_wrapper(func):
        vecd_f = vectorize(dtype_args)(func)

        def wrapper(*args, **kwargs):
            # np_arrays = [getattr(args[0], i).values for i in theargs]
            arrays = [arg.values for arg in args]
            ans = vecd_f(*arrays)
            return ans
        return wrapper
    return make_wrapper


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
    ans = -42
    if inc_in < 5:
        ans = -42
    if inc_in >= 5 and inc_in < 8:
        ans = 42
    if inc_in >= 8:
        ans = 99
    return ans
