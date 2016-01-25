"""
Tests for Tax-Calculator IncomeTaxIO class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_incometaxio.py
# pylint --disable=locally-disabled test_incometaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import IncomeTaxIO  # pylint: disable=import-error
import pytest
import tempfile


# use 1991 PUF-like data to emulate current PUF, which is private
FAUX_PUF_CSV = os.path.join(CUR_PATH, '..', '..', 'tax_all1991_puf.gz')


def test_1():
    """
    Test IncomeTaxIO constructor with no policy reform and no blowup.
    """
    taxyear = 2020
    inctax = IncomeTaxIO(input_filename=FAUX_PUF_CSV,
                         tax_year=taxyear,
                         reform=None,
                         blowup_input_data=False)
    assert inctax.tax_year() == taxyear


def test_2():
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup.
    """
    taxyear = 2020
    policy_reform = {
        2016: {'_SS_Earnings_c': [300000]},
        2018: {'_SS_Earnings_c': [500000]},
        2020: {'_SS_Earnings_c': [700000]}
    }
    inctax = IncomeTaxIO(input_filename=FAUX_PUF_CSV,
                         tax_year=taxyear,
                         reform=policy_reform,
                         blowup_input_data=False)
    inctax.calculate(write_output_file=False)
    assert inctax.tax_year() == taxyear


RAWINPUTFILE_FUNITS = 4
RAWINPUTFILE_CONTENTS = (
    'RECID,MARS\n'
    '1,2\n'
    '2,1\n'
    '3,4\n'
    '4,6\n'
)


@pytest.yield_fixture
def rawinputfile():
    """
    Temporary input file that contains minimum required input varaibles.
    """
    ifile = tempfile.NamedTemporaryFile(suffix='.csv', mode='a', delete=False)
    ifile.write(RAWINPUTFILE_CONTENTS)
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


REFORM_CONTENTS = """
// Example of a reform suitable for use as an optional IncomeTaxIO reform file.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// The primary keys are policy parameters and secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
    "_AMT_tthd": // AMT taxinc threshold separating the two AMT tax brackets
    {"2015": [200000],
     "2017": [300000]
    },
    "_EITC_c": // maximum EITC amount by number of qualifying kids (0,1,2,3+)
    {"2016": [[ 900, 5000,  8000,  9000]],
     "2019": [[1200, 7000, 10000, 12000]]
    },
    "_II_em": // personal exemption amount (see indexing changes below)
    {"2016": [6000],
     "2018": [7500],
     "2020": [9000]
    },
    "_II_em_cpi": // personal exemption amount indexing status
    {"2016": false, // values in future years are same as this year value
     "2018": true   // values in future years indexed with this year as base
    },
    "_SS_Earnings_c": // social security (OASDI) maximum taxable earnings
    {"2016": [300000],
     "2018": [500000],
     "2020": [700000]
    },
    "_AMT_em_cpi": // AMT exemption amount indexing status
    {"2017": false, // values in future years are same as this year value
     "2020": true   // values in future years indexed with this year as base
    }
}
"""


@pytest.yield_fixture
def reformfileA():
    """
    Temporary reform file with .json extension for IncomeTaxIO constructor.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    rfile.write(REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture
def reformfileB():
    """
    Temporary reform file without .json extension for IncomeTaxIO constructor.
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_3(rawinputfile, reformfileA):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and with blowup.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_filename=rawinputfile.name,
                         tax_year=taxyear,
                         reform=reformfileA.name,
                         blowup_input_data=False)
    inctax.calculate(write_output_file=False)
    assert inctax.tax_year() == taxyear


def test_4(rawinputfile, reformfileB):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and with blowup.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_filename=rawinputfile.name,
                         tax_year=taxyear,
                         reform=reformfileB.name,
                         blowup_input_data=False)
    inctax.calculate(write_output_file=False)
    assert inctax.tax_year() == taxyear
