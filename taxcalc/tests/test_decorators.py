"""
Test decorators.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_decorators.py
# pylint --disable=locally-disabled test_decorators.py

import os
import sys
import time
import shutil
import subprocess
import importlib
import numpy as np
import numba
from pandas import DataFrame
from pandas.testing import assert_frame_equal
import pytest
import taxcalc
from taxcalc.decorators import (
    iterate_jit,
    apply_jit,
    create_apply_function_string,
    create_toplevel_function_string,
    make_apply_function,
    JIT_CACHE_MAX_AGE_DAYS,
)


def test_create_apply_function_string():
    """Test docstring"""
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], [])
    exp = ('def ap_func(x_0,x_1,x_2,x_3,x_4):\n'
           '  for i in range(len(x_0)):\n'
           '    x_0[i],x_1[i],x_2[i] = jitted_f(x_3[i],x_4[i])\n'
           '  return x_0,x_1,x_2\n')
    assert ans == exp


def test_create_apply_function_string_with_params():
    """Test docstring"""
    ans = create_apply_function_string(['a', 'b', 'c'], ['d', 'e'], ['d'])
    exp = ('def ap_func(x_0,x_1,x_2,x_3,x_4):\n'
           '  for i in range(len(x_0)):\n'
           '    x_0[i],x_1[i],x_2[i] = jitted_f(x_3,x_4[i])\n'
           '  return x_0,x_1,x_2\n')
    assert ans == exp


def test_create_toplevel_function_string_mult_outputs():
    """Test docstring"""
    ans = create_toplevel_function_string(['a', 'b'], ['d', 'e'],
                                          ['pm', 'pm', 'pf', 'pm'])
    # pylint: disable=inconsistent-quotes
    exp = (
        "def hl_func(pm, pf):\n"
        "    from pandas import DataFrame\n"
        "    import numpy as np\n"
        "    import pandas as pd\n"
        "    def get_values(x):\n"
        "        if isinstance(x, pd.Series):\n"
        "            return x.values\n"
        "        else:\n"
        "            return x\n"
        "    outputs = \\\n"
        "        (pm.a, pm.b) = \\\n"
        "        applied_f(get_values(pm.a[0]), get_values(pm.b[0]), "
        "get_values(pf.d), get_values(pm.e[0]), )\n"
        "    header = ['a', 'b']\n"
        "    return DataFrame(data=np.column_stack(outputs),"
        "columns=header)"
    )
    # pylint: enable=inconsistent-quotes
    assert ans == exp


def test_create_toplevel_function_string():
    """Test docstring"""
    ans = create_toplevel_function_string(['a'], ['d', 'e'],
                                          ['pm', 'pf', 'pm'])
    # pylint: disable=inconsistent-quotes
    exp = (
        "def hl_func(pm, pf):\n"
        "    from pandas import DataFrame\n"
        "    import numpy as np\n"
        "    import pandas as pd\n"
        "    def get_values(x):\n"
        "        if isinstance(x, pd.Series):\n"
        "            return x.values\n"
        "        else:\n"
        "            return x\n"
        "    outputs = \\\n"
        "        (pm.a) = \\\n"
        "        applied_f(get_values(pm.a[0]), get_values(pf.d), "
        "get_values(pm.e[0]), )\n"
        "    header = ['a']\n"
        "    return DataFrame(data=outputs,"
        "columns=header)"
    )
    # pylint: enable=inconsistent-quotes
    assert ans == exp


def some_calc(x, y, z):
    """Function docstring"""
    a = x + y
    b = x + y + z
    return (a, b)


def test_make_apply_function():
    """Test docstring"""
    ans_do_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=True, no_python=True)
    assert ans_do_jit
    ans_no_jit = make_apply_function(some_calc, ['a', 'b'], ['x', 'y', 'z'],
                                     [], do_jit=False, no_python=True)
    assert ans_no_jit


@apply_jit(['a', 'b'], ['x', 'y', 'z'], nopython=True)
def magic_calc(x, y, z):
    """Function docstring"""
    a = x + y
    b = x + y + z
    return (a, b)


def magic(pm, pf):
    """Function docstring"""
    # Adjustments
    # pylint: disable=no-value-for-parameter
    outputs = pf.a, pf.b = magic_calc(pm, pf)
    # pylint: enable=no-value-for-parameter
    header = ['a', 'b']
    return DataFrame(data=np.column_stack(outputs), columns=header)


@iterate_jit(nopython=True)
def magic_calc2(x, y, z):
    """Function docstring"""
    a = x + y
    b = x + y + z
    return (a, b)


class Foo:  # pylint: disable=too-many-instance-attributes
    """Foo class"""

    def faux_method1(self):
        """ Foo method"""

    def faux_method2(self):
        """ Foo method"""


@iterate_jit(nopython=True)
def faux_function(mars):
    """Function docstring"""
    if mars == 1:
        var = 2
    else:
        var = 1
    return var


@iterate_jit(nopython=True)
def ret_everything(a, b, c, d, e, f):
    """Function docstring"""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    c = a + b
    d = a + b
    e = a + b
    f = a + b
    return (c, d, e,
            f)


# pylint: disable=attribute-defined-outside-init


def test_magic_apply_jit():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = magic(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=['a', 'b'])
    assert_frame_equal(xx, exp)


def test_magic_apply_jit_swap():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((5,))
    pm.b = np.ones((5,))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = magic(pf, pm)  # pylint: disable=arguments-out-of-order
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=['a', 'b'])
    assert_frame_equal(xx, exp)


# pylint: disable=no-value-for-parameter


def test_magic_iterate_jit():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    xx = magic_calc2(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5, columns=['a', 'b'])
    assert_frame_equal(xx, exp)


def test_faux_function_iterate_jit():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pf.mars = np.ones((5,))
    pf.var = np.ones((5,))
    ans = faux_function(pm, pf)  # pylint: disable=too-many-function-args
    exp = DataFrame(data=[2.0] * 5, columns=['var'])
    assert_frame_equal(ans, exp)


def test_ret_everything_iterate_jit():
    """Test docstring"""
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
                    columns=['c', 'd', 'e', 'f'])
    assert_frame_equal(ans, exp)


@iterate_jit(nopython=True)
def magic_calc3(x, y, z):
    """Function docstring"""
    a = x + y
    b = a + z
    return (a, b)


def test_function_takes_kwarg():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = magic_calc3(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=['a', 'b'])
    assert_frame_equal(ans, exp)


@iterate_jit(nopython=True)
def magic_calc4(x, y, z):
    """Function docstring"""
    a = x + y
    b = a + z
    return (a, b)


def test_function_no_parameters_listed():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = magic_calc4(pm, pf)
    exp = DataFrame(data=[[2.0, 3.0]] * 5,
                    columns=['a', 'b'])
    assert_frame_equal(ans, exp)


@iterate_jit(parameters=['w'], nopython=True)
def magic_calc5(w, x, y, z):
    """Function docstring"""
    a = x + y
    b = w[0] + x + y + z
    return (a, b)


def test_function_parameters_optional():
    """Test docstring"""
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = magic_calc5(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=['a', 'b'])
    assert_frame_equal(ans, exp)


# pylint: enable=no-value-for-parameter


def unjittable_function1(w, x, y, z):
    """Function docstring"""
    a = x + y  # pylint: disable=unused-variable
    b = w[0] + x + y + z  # pylint: disable=unused-variable


def unjittable_function2(w, x, y, z):
    """Function docstring"""
    a = x + y
    b = w[0] + x + y + z
    return (a, b, c)  # pylint: disable=undefined-variable


def test_iterate_jit_raises_on_no_return():
    """Test docstring"""
    with pytest.raises(ValueError):
        ij = iterate_jit(parameters=['w'], nopython=True)
        ij(unjittable_function1)


def test_iterate_jit_raises_on_unknown_return_argument():
    """Test docstring"""
    ij = iterate_jit(parameters=['w'], nopython=True)
    uf2 = ij(unjittable_function2)
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    with pytest.raises(AttributeError):
        ans = uf2(pm, pf)  # pylint: disable=unused-variable


def magic_calc6(w, x, y, z):
    """Function docstring"""
    a = x + y
    b = w[0] + x + y + z
    return (a, b)


def test_force_no_jit():
    """
    Force execution of code for "DO_JIT = False", which tests the
    id_wrapper function in the decorators.py file.
    """
    # set environment variable that turns off JIT decorator logic
    os.environ['NOTAXCALCJIT'] = 'NOJIT'
    # reload the decorators module
    importlib.reload(taxcalc.decorators)
    # verify magic_calc6 function works as expected
    magic_calc6_ = iterate_jit(parameters=['w'], nopython=True)(magic_calc6)
    pm = Foo()
    pf = Foo()
    pm.a = np.ones((1, 5))
    pm.b = np.ones((1, 5))
    pm.w = np.ones((1, 5))
    pf.x = np.ones((5,))
    pf.y = np.ones((5,))
    pf.z = np.ones((5,))
    ans = magic_calc6_(pm, pf)
    exp = DataFrame(data=[[2.0, 4.0]] * 5,
                    columns=['a', 'b'])
    assert_frame_equal(ans, exp)
    # restore normal JIT operation of decorators module
    del os.environ['NOTAXCALCJIT']
    importlib.reload(taxcalc.decorators)


CALL_AFTERTAXINCOME = """
import numpy as np
from taxcalc.calcfunctions import AfterTaxIncome
class Obj:
    pass
pm = Obj()
pf = Obj()
pf.combined = np.array([1.0, 2.0])
pf.expanded_income = np.array([10.0, 20.0])
pf.aftertax_income = np.zeros(2)
AfterTaxIncome(pm, pf)
print(pf.aftertax_income.tolist())
"""


def run_python(code, pkg_parent, cache_dir, nojit=False):
    """
    Execute code in a new Python process that imports the taxcalc package
    located in the pkg_parent folder and that caches JIT-compiled code in
    the cache_dir folder, returning the process's stdout and stderr.
    """
    env = dict(os.environ)
    env.pop('NOTAXCALCJIT', None)
    env.pop('TESTING', None)
    if nojit:
        env['NOTAXCALCJIT'] = 'NOJIT'
    env['TAXCALC_JIT_CACHE_DIR'] = str(cache_dir)
    env['PYTHONPATH'] = str(pkg_parent)
    env['NUMBA_DEBUG_CACHE'] = '1'
    proc = subprocess.run(
        [sys.executable, '-c', code],
        env=env, cwd=pkg_parent, capture_output=True, text=True, check=True,
    )
    return proc.stdout


def test_no_jit_cache_when_no_jit(tmp_path):
    """
    Check that nothing is written to the JIT cache when the NOTAXCALCJIT
    environment variable is set.
    """
    pkg_parent = os.path.dirname(os.path.dirname(taxcalc.__file__))
    cache_dir = tmp_path / 'cache'
    out = run_python(CALL_AFTERTAXINCOME, pkg_parent, cache_dir, nojit=True)
    assert out.strip().endswith('[9.0, 18.0]')
    assert not cache_dir.exists()


def test_jit_cache_not_writable(tmp_path):
    """
    Check that JIT-compiled code is not cached, but calculations work,
    when the JIT cache folder cannot be created.
    """
    pkg_parent = os.path.dirname(os.path.dirname(taxcalc.__file__))
    not_a_dir = tmp_path / 'file'
    not_a_dir.write_text('not a folder', encoding='utf-8')
    cache_dir = not_a_dir / 'cache'
    out = run_python(CALL_AFTERTAXINCOME, pkg_parent, cache_dir)
    assert out.strip().endswith('[9.0, 18.0]')
    assert 'data saved to' not in out
    assert not cache_dir.exists()


def test_jit_cache_pruning(tmp_path):
    """
    Check that importing taxcalc deletes cache folders for other source
    hashes that are unused for more than JIT_CACHE_MAX_AGE_DAYS days, but
    keeps recently used cache folders and folders not made by taxcalc.
    """
    pkg_parent = os.path.dirname(os.path.dirname(taxcalc.__file__))
    cache_dir = tmp_path / 'cache'
    old_time = time.time() - (JIT_CACHE_MAX_AGE_DAYS + 1) * 24 * 60 * 60
    new_time = time.time() - (JIT_CACHE_MAX_AGE_DAYS - 1) * 24 * 60 * 60
    folders = {
        '0123456789abcdef': old_time,  # old hash folder: deleted
        'fedcba9876543210': new_time,  # recent hash folder: kept
        'not-a-hash-name!': old_time,  # old non-hash folder: kept
    }
    for name, mtime in folders.items():
        folder = cache_dir / name
        folder.mkdir(parents=True)
        (folder / 'somefile').write_text('x', encoding='utf-8')
        os.utime(folder, (mtime, mtime))
    run_python('import taxcalc', pkg_parent, cache_dir)
    remaining = set(os.listdir(cache_dir))
    assert '0123456789abcdef' not in remaining
    assert 'fedcba9876543210' in remaining
    assert 'not-a-hash-name!' in remaining
    assert len(remaining) == 3  # includes the current hash folder


def test_jit_cache_invalidation(tmp_path):
    """
    Check that JIT-compiled code for calcfunctions.py functions is cached
    and reused, and that editing the body of a calcfunctions.py function
    causes its new code to be compiled and cached.
    """
    # copy the taxcalc package so that calcfunctions.py can be edited
    pkg_dir = os.path.dirname(taxcalc.__file__)
    pkg_parent = tmp_path / 'pkg'
    shutil.copytree(
        pkg_dir, pkg_parent / 'taxcalc',
        ignore=shutil.ignore_patterns(
            'tests', 'validation', '__pycache__', '*.gz',
        ),
    )
    cache_dir = tmp_path / 'cache'
    # first run compiles the code and writes it to the cache
    out = run_python(CALL_AFTERTAXINCOME, pkg_parent, cache_dir)
    assert out.strip().endswith('[9.0, 18.0]')
    assert 'data saved to' in out
    assert len(os.listdir(cache_dir)) == 1
    # second run loads the compiled code from the cache
    out = run_python(CALL_AFTERTAXINCOME, pkg_parent, cache_dir)
    assert out.strip().endswith('[9.0, 18.0]')
    assert 'data saved to' not in out
    assert 'data loaded from' in out
    assert len(os.listdir(cache_dir)) == 1
    # edit body of AfterTaxIncome function
    cf_path = pkg_parent / 'taxcalc' / 'calcfunctions.py'
    old_line = 'aftertax_income = expanded_income - combined\n'
    new_line = 'aftertax_income = expanded_income - 2.0 * combined\n'
    code = cf_path.read_text(encoding='utf-8')
    assert code.count(old_line) == 1
    cf_path.write_text(code.replace(old_line, new_line), encoding='utf-8')
    # third run compiles the edited code and writes it to a new cache folder
    out = run_python(CALL_AFTERTAXINCOME, pkg_parent, cache_dir)
    assert out.strip().endswith('[8.0, 16.0]')
    assert 'data saved to' in out
    assert len(os.listdir(cache_dir)) == 2


def test_jit_cache_root(monkeypatch, tmp_path):
    """
    Check the jit_cache_root function's handling of environment variables.
    """
    dec = taxcalc.decorators
    monkeypatch.setenv('TAXCALC_JIT_CACHE_DIR', str(tmp_path / 'tc'))
    monkeypatch.setenv('NUMBA_CACHE_DIR', str(tmp_path / 'nb'))
    assert dec.jit_cache_root() == str(tmp_path / 'tc')
    monkeypatch.delenv('TAXCALC_JIT_CACHE_DIR')
    assert dec.jit_cache_root() == os.path.join(tmp_path / 'nb', 'taxcalc')
    monkeypatch.delenv('NUMBA_CACHE_DIR')
    assert dec.jit_cache_root().endswith('taxcalc')


def test_prune_jit_cache(tmp_path):
    """
    Check that the prune_jit_cache function deletes only old cache folders
    for other source hashes and marks the current cache folder as used.
    """
    dec = taxcalc.decorators
    days = dec.JIT_CACHE_MAX_AGE_DAYS
    old_time = time.time() - (days + 1) * 24 * 60 * 60
    new_time = time.time() - (days - 1) * 24 * 60 * 60
    mtimes = {
        '0000000000000000': old_time,  # current hash folder: kept
        '0123456789abcdef': old_time,  # old hash folder: deleted
        'fedcba9876543210': new_time,  # recent hash folder: kept
        '0123456789ghijkl': old_time,  # old non-hash folder: kept
        'short': old_time,  # old non-hash folder: kept
    }
    for name, mtime in mtimes.items():
        folder = tmp_path / name
        folder.mkdir()
        os.utime(folder, (mtime, mtime))
    hashfile = tmp_path / 'aaaaaaaaaaaaaaaa'  # old file, not folder: kept
    hashfile.write_text('x', encoding='utf-8')
    os.utime(hashfile, (old_time, old_time))
    dec.prune_jit_cache(str(tmp_path), '0000000000000000')
    assert sorted(os.listdir(tmp_path)) == sorted([
        '0000000000000000', 'fedcba9876543210',
        '0123456789ghijkl', 'short', 'aaaaaaaaaaaaaaaa',
    ])
    current = tmp_path / '0000000000000000'
    assert current.stat().st_mtime > new_time


def test_jit_cache_class(monkeypatch, tmp_path):
    """
    Check the jit_cache_class function in normal and failure situations.
    """
    dec = taxcalc.decorators
    uncached_jit_cache_class = dec.jit_cache_class.__wrapped__
    monkeypatch.setenv('TAXCALC_JIT_CACHE_DIR', str(tmp_path / 'cache'))
    # normal situation
    cache_class = uncached_jit_cache_class()
    assert cache_class is not None
    assert os.listdir(tmp_path / 'cache') == [dec.source_hash()]
    # locator declines a function that has no cache tag
    # pylint: disable=protected-access
    locator_class = cache_class._impl_class._locator_classes[0]
    # pylint: enable=protected-access
    assert locator_class.from_function(some_calc, __file__) is None
    with pytest.raises(RuntimeError):
        cache_class(some_calc)
    # pruning error is ignored

    def raise_oserror(*args):
        raise OSError(args)

    monkeypatch.setattr(dec, 'prune_jit_cache', raise_oserror)
    assert uncached_jit_cache_class() is not None
    # cache folder cannot be created
    not_a_dir = tmp_path / 'file'
    not_a_dir.write_text('not a folder', encoding='utf-8')
    monkeypatch.setenv('TAXCALC_JIT_CACHE_DIR', str(not_a_dir / 'cache'))
    assert uncached_jit_cache_class() is None
    # Numba lacks the internal caching classes
    monkeypatch.setitem(sys.modules, 'numba.core.caching', None)
    assert uncached_jit_cache_class() is None


def test_enable_jit_cache(monkeypatch):
    """
    Check that enable_jit_cache leaves the dispatcher uncached when
    there is no cache class or when the cache class cannot be used.
    """
    dec = taxcalc.decorators

    def plus_one(x):
        return x + 1

    dispatcher = numba.jit(nopython=True)(plus_one)
    uncached = dispatcher._cache  # pylint: disable=protected-access
    # there is no cache class
    monkeypatch.setattr(dec, 'jit_cache_class', lambda: None)
    dec.enable_jit_cache(dispatcher, 'plus_one')
    assert dispatcher._cache is uncached  # pylint: disable=protected-access
    # cache class cannot be used

    def failing_cache_class(py_func):
        raise OSError(py_func)

    monkeypatch.setattr(dec, 'jit_cache_class', lambda: failing_cache_class)
    dec.enable_jit_cache(dispatcher, 'plus_one')
    assert dispatcher._cache is uncached  # pylint: disable=protected-access
    assert dispatcher(1) == 2


def test_iterate_jit_when_testing(monkeypatch):
    """
    Check that an iterate_jit function calls the undecorated function when
    the TESTING environment variable is True.
    """
    magic_calc6_ = iterate_jit(parameters=['w'], nopython=True)(magic_calc6)
    monkeypatch.setenv('TESTING', 'True')
    assert magic_calc6_(np.ones(1), 1.0, 2.0, 3.0) == (3.0, 7.0)
