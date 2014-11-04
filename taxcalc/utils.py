import numpy as np
import pandas as pd
import inspect
from numba import jit, vectorize, guvectorize
from functools import wraps


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

        @wraps(func)
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

        @wraps(func)
        def wrapper(*args, **kwargs):
            # np_arrays = [getattr(args[0], i).values for i in theargs]
            arrays = [arg.values for arg in args]
            ans = vecd_f(*arrays)
            return ans
        return wrapper
    return make_wrapper


def dataframe_wrap_guvectorize(dtype_args, dtype_sig):
    """
    Extracts particular numpy arrays from caller argments and passes
    them to guvectorize. Goes one step further than dataframe_guvectorize
    by looking for the column names in the dataframe and just extracting those
    """
    def make_wrapper(func):
        theargs = inspect.getargspec(func).args
        vecd_f = guvectorize(dtype_args, dtype_sig)(func)

        def wrapper(*args, **kwargs):
            np_arrays = [getattr(args[0], i).values for i in theargs]
            ans = vecd_f(*np_arrays)
            return ans
        return wrapper
    return make_wrapper
