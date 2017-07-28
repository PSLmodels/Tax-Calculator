import os
import tempfile
import numpy
import pandas
import pytest


# convert all numpy warnings into errors so they can be detected in tests
numpy.seterr(all='raise')


@pytest.fixture(scope='session')
def tests_path():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def cps_path(tests_path):
    return os.path.join(tests_path, '..', 'cps.csv.gz')


@pytest.fixture(scope='session')
def cps_fullsample(cps_path):
    return pandas.read_csv(cps_path)


@pytest.fixture(scope='session')
def cps_subsample(cps_fullsample):
    return cps_fullsample.sample(frac=0.01, random_state=123456789)


@pytest.fixture(scope='session')
def puf_path(tests_path):
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.fixture(scope='session')
def puf_fullsample(puf_path):
    return pandas.read_csv(puf_path)


@pytest.fixture(scope='session')
def puf_subsample(puf_fullsample):
    return puf_fullsample.sample(frac=0.01, random_state=123456789)


# following fixtures used exclusively in test_taxcalcio.py tests:


@pytest.yield_fixture(scope='session')
def rawinputfile():
    """
    Temporary input file that contains minimum required input variables.
    """
    ifile = tempfile.NamedTemporaryFile(suffix='.csv', mode='a', delete=False)
    contents = (
        u'RECID,MARS\n'
        u'    1,   2\n'
        u'    2,   1\n'
        u'    3,   4\n'
        u'    4,   3\n'
    )
    ifile.write(contents)
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def reformfile0():
    """
    Specify JSON reform file.
    """
    txt = """
    { "policy": {
        "_SS_Earnings_c": {"2016": [300000],
                           "2018": [500000],
                           "2020": [700000]}
      }
    }
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    rfile.write(txt + '\n')
    rfile.close()
    # Must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def assumpfile0():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    {
    "consumption": {},
    "behavior": {"_BE_sub": {"2020": [0.05]}},
    "growdiff_baseline": {},
    "growdiff_response": {"_ABOOK": {"2015": [-0.01]}}
    }
    """
    afile.write(contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def reformfile1():
    """
    Temporary reform file with .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    { "policy": {
        "_AMT_brk1": { // top of first AMT tax bracket
          "2015": [200000],
          "2017": [300000]},
        "_EITC_c": { // max EITC amount by number of qualifying kids (0,1,2,3+)
          "2016": [[ 900, 5000,  8000,  9000]],
          "2019": [[1200, 7000, 10000, 12000]]},
        "_II_em": { // personal exemption amount (see indexing changes below)
          "2016": [6000],
          "2018": [7500],
          "2020": [9000]},
        "_II_em_cpi": { // personal exemption amount indexing status
          "2016": false, // values in future years are same as this year value
          "2018": true // values in future years indexed with this year as base
          },
        "_SS_Earnings_c": { // social security (OASDI) maximum taxable earnings
          "2016": [300000],
          "2018": [500000],
          "2020": [700000]},
        "_AMT_em_cpi": { // AMT exemption amount indexing status
          "2017": false, // values in future years are same as this year value
          "2020": true // values in future years indexed with this year as base
        }
      }
    }
    """
    rfile.write(contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def assumpfile1():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    contents = """
    { "consumption": { "_MPC_e18400": {"2018": [0.05]} },
      "behavior": {},
      "growdiff_baseline": {},
      "growdiff_response": {}
    }
    """
    afile.write(contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def lumpsumreformfile():
    """
    Temporary reform file without .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    lumpsum_reform_contents = """
    {
      "policy": {"_LST": {"2013": [200]}}
    }
    """
    rfile.write(lumpsum_reform_contents)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture(scope='session')
def assumpfile2():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    assump2_contents = """
    {
    "consumption": {},
    "behavior": {"_BE_sub": {"2020": [0.05]}},
    "growdiff_baseline": {},
    "growdiff_response": {}
    }
    """
    afile.write(assump2_contents)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file
