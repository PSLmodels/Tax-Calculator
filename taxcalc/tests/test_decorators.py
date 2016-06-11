import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
from pandas import DataFrame
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


def test_create_apply_function_string():
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], [])
    exp = ("def ap_func(x_0,x_1,x_2,x_3,x_4):\n"
           "  for i in range(len(x_0)):\n"
           "    x_0[i],x_1[i],x_2[i] = jitted_f(x_3[i],x_4[i])\n"
           "  return x_0,x_1,x_2\n")
    assert ans == exp


def test_create_apply_function_string_with_params():
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], ['d'])
    exp = ("def ap_func(x_0,x_1,x_2,x_3,x_4):\n"
           "  for i in range(len(x_0)):\n"
           "    x_0[i],x_1[i],x_2[i] = jitted_f(x_3,x_4[i])\n"
           "  return x_0,x_1,x_2\n")
    assert ans == exp


def test_create_toplevel_function_string_mult_outputs():
    ans = create_toplevel_function_string(['a', 'b'], ['d', 'e'],
                                          ['pm', 'pm', 'pf', 'pm'])
    exp = ''
    exp = ("def hl_func(pm, pf):\n"
           "    from pandas import DataFrame\n"
           "    import numpy as np\n"
           "    outputs = \\\n"
           "        (pm.a, pm.b) = \\\n"
           "        applied_f(pm.a, pm.b, pf.d, pm.e, )\n"
           "    header = ['a', 'b']\n"
           "    return DataFrame(data=np.column_stack(outputs),"
           "columns=header)")

    assert ans == exp


def test_create_toplevel_function_string():
    ans = create_toplevel_function_string(['a'], ['d', 'e'],
                                          ['pm', 'pf', 'pm'])
    exp = ''
    exp = ("def hl_func(pm, pf):\n"
           "    from pandas import DataFrame\n"
           "    import numpy as np\n"
           "    outputs = \\\n"
           "        (pm.a) = \\\n"
           "        applied_f(pm.a, pf.d, pm.e, )\n"
           "    header = ['a']\n"
           "    return DataFrame(data=outputs,"
           "columns=header)")

    assert ans == exp


def some_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


def test_make_apply_function():
    ans_do_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=True, no_python=True)
    assert ans_do_jit
    ans_no_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=False, no_python=True)
    assert ans_no_jit


@apply_jit(["a", "b"], ["x", "y", "z"], nopython=True)
def Magic_calc(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


def Magic(pm, pf):
    # Adjustments
    outputs = \
        pf.a, pf.b = Magic_calc(pm, pf)

    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs),
                     columns=header)


@iterate_jit(nopython=True)
def Magic_calc2(x, y, z):
    a = x + y
    b = x + y + z
    return (a, b)


class Foo(object):
    pass


@iterate_jit(nopython=True)
def bar(MARS):
    if MARS == 1 or MARS == 6:
        _sep = 2
    else:
        _sep = 1
    return _sep


@iterate_jit(nopython=True)
def ret_everything(a, b, c, d, e, f):

    c = a + b
    d = a + b
    e = a + b
    f = a + b

    return (c, d, e,
            f)


def test_magic_apply_jit():
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


def test_magic_iterate_jit():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic_calc2(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=["a", "b"])
    assert_frame_equal(xx, exp)


def test_bar_iterate_jit():
    pm = Foo()
    pf = Foo()
    pf.MARS = np.ones((5,))
    pf._sep = np.ones((5,))
    ans = bar(pm, pf)
    exp = DataFrame(data=[2.0] * 5, columns=["_sep"])
    assert_frame_equal(ans, exp)


def test_ret_everything_iterate_jit():
    pm = Foo()
    pf = Foo()
    pf.a = np.ones((5,))
    pf.b = np.ones((5,))
    pf.c = np.ones((5,))
    pf.d = np.ones((5,))
    pf.e = np.ones((5,))
    pf.f = np.ones((5,))
    ans = ret_everything(pm, pf)
    exp = DataFrame(data=[[2.0, 2.0, 2.0, 2.0]] * 5,
                    columns=["c", "d", "e", "f"])
    assert_frame_equal(ans, exp)


@iterate_jit(parameters=['puf'], nopython=True, puf=True)
def Magic_calc3(x, y, z, puf):
    a = x + y
    if (puf):
        b = x + y + z
    else:
        b = 42
    return (a, b)


def test_function_takes_kwarg():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc3(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


def test_function_takes_kwarg_nondefault_value():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc3(pm, pf, puf=False)
    exp = DataFrame(data=[[2.0, 42.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


@iterate_jit(nopython=True, puf=True)
def Magic_calc4(x, y, z, puf):
    a = x + y
    if (puf):
        b = x + y + z
    else:
        b = 42
    return (a, b)


def test_function_no_parameters_listed():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc4(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)


@iterate_jit(parameters=['w'], nopython=True, puf=True)
def Magic_calc5(w, x, y, z, puf):
    a = x + y
    if (puf):
        b = w[0] + x + y + z
    else:
        b = 42
    return (a, b)


def test_function_parameters_optional():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pm.w = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc5(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)
