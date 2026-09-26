"""
The pytest configuration file.
"""

import os
import re
import ast
import glob
import json
import numpy
import pandas
import pytest
from taxcalc import Policy, calcfunctions


# convert all numpy warnings into errors so they can be detected in tests
numpy.seterr(all='raise')


def pytest_sessionfinish(session):
    """
    Merge any cpscsv_agg_actual_YYYY-YYYY.csv chunk files written by the
    failing test_cpscsv.py::test_agg year chunks into a single complete
    cpscsv_agg_actual.csv file.  This hook runs after all the pytest-xdist
    workers have finished, so the chunk files are merged without any race
    among the workers.
    """
    if hasattr(session.config, 'workerinput'):
        return  # skip in pytest-xdist workers; merge only in main process
    merge_cpscsv_agg_chunks(os.path.abspath(os.path.dirname(__file__)))


def merge_cpscsv_agg_chunks(tests_path):
    """
    Copy year columns from each cpscsv_agg_actual_YYYY-YYYY.csv chunk file
    into the cpscsv_agg_expect.csv table, write the resulting table to the
    cpscsv_agg_actual.csv file, and remove the chunk files.
    """
    chunk_paths = sorted(glob.glob(
        os.path.join(tests_path, 'cpscsv_agg_actual_[0-9]*-[0-9]*.csv')
    ))
    if not chunk_paths:
        return
    expect_path = os.path.join(tests_path, 'cpscsv_agg_expect.csv')
    table = pandas.read_csv(expect_path, index_col=0)
    for chunk_path in chunk_paths:
        match = re.search(r'_(\d{4})-(\d{4})\.csv$', chunk_path)
        first_year, last_year = int(match.group(1)), int(match.group(2))
        chunk = pandas.read_csv(chunk_path, index_col=0)
        for year in range(first_year, last_year + 1):
            table[str(year)] = chunk[str(year)].values
        os.remove(chunk_path)
    actual_path = os.path.join(tests_path, 'cpscsv_agg_actual.csv')
    table.to_csv(actual_path, float_format='%.1f')


@pytest.fixture(scope='session', name='tests_path')
def tests_path_fixture():
    """Fixture docstring"""
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session', name='cps_data_path')
def cps_data_path_fixture(tests_path):
    """Fixture docstring"""
    return os.path.join(tests_path, '..', 'cps.csv.gz')


@pytest.fixture(scope='session', name='cps_fullsample')
def cps_fullsample_fixture(cps_data_path):
    """Fixture docstring"""
    return pandas.read_csv(cps_data_path)


@pytest.fixture(scope='session')
def cps_subsample(cps_fullsample):
    """Fixture docstring"""
    # draw a small cps.csv subsample
    return cps_fullsample.sample(frac=0.01, random_state=123456789)


@pytest.fixture(scope='session', name='puf_data_path')
def puf_data_path_fixture(tests_path):
    """Fixture docstring"""
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.fixture(scope='session', name='tmd_data_path')
def tmd_data_path_fixture(tests_path):
    """Fixture docstring"""
    return os.path.join(tests_path, '..', '..', 'tmd.csv')


@pytest.fixture(scope='session', name='full_claiming_assumption')
def full_credit_claiming_assumption_fixture():
    """Returns parameter dictionary specifying full credit claiming"""
    return {
        'eitc_claim_prob_scale': {2013: 9e99},
        'actc_claim_prob_scale': {2013: 9e99},
    }


@pytest.fixture(scope='session', name='calcfunc_argnames')
def calcfunc_argnames_fixture(tests_path):
    """
    Returns dictionary that maps each function name in calcfunctions.py
    to the list of that function's argument names.  The argument names
    are found by parsing the source code because the iterate_jit
    decorator does not preserve the signature of the function it wraps.
    """
    path = os.path.join(tests_path, '..', 'calcfunctions.py')
    with open(path, 'r', encoding='utf-8') as cfile:
        tree = ast.parse(cfile.read())
    return {node.name: [arg.arg for arg in node.args.args]
            for node in tree.body if isinstance(node, ast.FunctionDef)}


@pytest.fixture(scope='session', name='policy_cache')
def policy_cache_fixture():
    """
    Returns empty dictionary used to cache Policy objects, indexed by
    (year, reform) key, that are shared by all call_calcfunc calls.
    The cached Policy objects must be treated as read-only.
    """
    return {}


@pytest.fixture(name='call_calcfunc')
def call_calcfunc_fixture(calcfunc_argnames, policy_cache, monkeypatch):
    """
    Returns a function that calls the named calcfunctions.py function
    (in pure Python, without JIT compilation) using arguments assembled
    by name:
    - each policy parameter argument has its value in the specified
      year (2025 by default) under current law as optionally modified
      by the specified reform dictionary;
    - each other argument (a Records input variable or a variable
      calculated by the function) is zero unless a value is specified
      as a keyword argument.
    Specifying an argument name that the function does not have raises
    an error, as does omitting MARS for a function that uses MARS.
    """
    monkeypatch.setenv('TESTING', 'True')
    param_names = set(Policy.parameter_list())

    def _call(fname, reform=None, year=2025, **rvars):
        argnames = calcfunc_argnames[fname]
        unknown = set(rvars) - set(argnames)
        assert not unknown, f'{fname} has no arguments {sorted(unknown)}'
        if 'MARS' in argnames:
            assert 'MARS' in rvars, f'{fname} call must specify MARS'
        key = (year, json.dumps(reform, sort_keys=True))
        if key not in policy_cache:
            pol = Policy()
            if reform:
                pol.implement_reform(reform)
            pol.set_year(year)
            policy_cache[key] = pol
        pol = policy_cache[key]
        args = []
        for name in argnames:
            if name in rvars:
                args.append(rvars[name])
            elif name in param_names:
                args.append(getattr(pol, name)[0])
            else:
                args.append(0)
        func = getattr(calcfunctions, fname)
        # call the pure Python function wrapped by a JIT decorator, if any
        func = getattr(func, 'py_func', func)
        return func(*args)

    return _call
