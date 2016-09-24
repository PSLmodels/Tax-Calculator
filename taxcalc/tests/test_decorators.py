import os
import sys
import pytest
from six.moves import reload_module
import numpy as np
from pandas import DataFrame
from taxcalc.decorators import *
from pandas.util.testing import assert_frame_equal


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


def test_magic_apply_jit_swap():
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = Magic(pf, pm)
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


@iterate_jit(nopython=True)
def Magic_calc3(x, y, z):
    a = x + y
    b = a + z
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


@iterate_jit(nopython=True)
def Magic_calc4(x, y, z):
    a = x + y
    b = a + z
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


@iterate_jit(parameters=['w'], nopython=True)
def Magic_calc5(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
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


def unjittable_function1(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z


def unjittable_function2(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
    return (a, b, c)


def test_iterate_jit_raises_on_no_return():
    with pytest.raises(ValueError):
        ij = iterate_jit(parameters=['w'], nopython=True)
        ij(unjittable_function1)


def test_iterate_jit_raises_on_unknown_return_argument():
    ij = iterate_jit(parameters=['w'], nopython=True)
    uf2 = ij(unjittable_function2)
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pm.w = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    with pytest.raises(AttributeError):
        ans = uf2(pm, pf)


def Magic_calc6(w, x, y, z):
    a = x + y
    b = w[0] + x + y + z
    return (a, b)


def test_force_no_numba():
    """
    Force execution of code for non-existence of Numba
    """
    global Magic_calc6

    # Mock the numba module
    from mock import Mock
    mck = Mock()
    hasattr(mck, 'jit')
    del mck.jit
    import taxcalc
    nmba = sys.modules.get('numba', None)
    sys.modules.update([('numba', mck)])
    # Reload the decorators with faked out numba
    reload_module(taxcalc.decorators)
    # Get access to iterate_jit and force to jit
    ij = taxcalc.decorators.iterate_jit
    taxcalc.decorators.DO_JIT = True
    # Now use iterate_jit on a dummy function
    Magic_calc6 = ij(parameters=['w'], nopython=True)(Magic_calc6)
    # Do work and verify function works as expected
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pm.w = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = Magic_calc6(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=["a", "b"])
    assert_frame_equal(ans, exp)
    # Restore numba module
    if nmba:
        sys.modules['numba'] = nmba
