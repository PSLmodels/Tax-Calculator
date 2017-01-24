import os

import pandas
import pytest

from taxcalc import Records


@pytest.fixture(scope='session')
def tests_path():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def puf_1991_path(tests_path):
    return os.path.join(tests_path, '..', 'altdata', 'puf91taxdata.csv.gz')


@pytest.fixture(scope='session')
def weights_1991_path(tests_path):
    # Not yet used, but can be used in test_correct_Records_instantiation
    # to provide test coverage for records.py#458 ` ..._read_egg_csv...'
    return os.path.join(tests_path, '..', 'altdata', 'puf91weights.csv.gz')


@pytest.fixture(scope='session')
def adjust_1991_path(tests_path):
    return os.path.join(tests_path, '..', 'altdata', 'puf91adjustments.csv.gz')

@pytest.fixture(scope='session')
def puf_1991(puf_1991_path):
    return pandas.read_csv(puf_1991_path, compression='gzip')


@pytest.fixture(scope='session')
def weights_1991(weights_1991_path):
    return pandas.read_csv(weights_1991_path, compression='gzip')


@pytest.fixture(scope='session')
def adjust_1991(adjust_1991_path):
    return pandas.read_csv(adjust_1991_path, compression='gzip')


@pytest.fixture()
def records_2009(puf_1991, weights_1991, adjust_1991):
    """
    Provides a new Records object starting in 2009.
    Uses 1991 PUF-like data to emulate taxpayer data, which is private.
    """
    return Records(data=puf_1991, weights=weights_1991,
                   adjust_factors=adjust_1991, start_year=2009)
