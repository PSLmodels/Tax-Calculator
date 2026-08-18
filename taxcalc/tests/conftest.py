"""
The pytest configuration file.
"""

import os
import numpy
import pandas
import pytest


# convert all numpy warnings into errors so they can be detected in tests
numpy.seterr(all='raise')


@pytest.fixture
def skip_jit(monkeypatch):
    """Fixture docstring"""
    monkeypatch.setenv('TESTING', 'True')
    yield


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


@pytest.fixture(scope='session', name='puf_weights_path')
def puf_weights_path_fixture(tests_path):
    """Fixture docstring"""
    return os.path.join(tests_path, '..', '..', 'puf_weights.csv.gz')


@pytest.fixture(scope='session', name='puf_ratios_path')
def puf_ratios_path_fixture(tests_path):
    """Fixture docstring"""
    return os.path.join(tests_path, '..', '..', 'puf_ratios.csv')


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
