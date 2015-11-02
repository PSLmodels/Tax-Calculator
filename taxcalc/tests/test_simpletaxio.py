"""
Tests for SimpleTaxIO class in taxcalc package.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_simpletaxio.py
# pylint --disable=locally-disabled test_simpletaxio.py

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '../../'))
from taxcalc import SimpleTaxIO  # pylint: disable=import-error
import pytest
import tempfile


NUM_INPUT_LINES = 2
INPUT_CONTENTS = (
    '1 2014 0 1 0 0 95000 0 5000 0     0     0 0 0 0 0 0 0 0 0 9000 -1000\n'
    '2 2013 0 2 0 1 15000 0    0 0 50000 70000 0 0 0 0 0 0 0 0    0 -3000\n'
)
REFORM_CONTENTS = """
// Example of a reform suitable for use as an optional SimpleTaxIO reform file.
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

// The JSON above is translated into the following Python dictionary with
// calendar year as the primary key, which is the data structure required
// as input to the Policy class implement_reform(reform) method.
//   reform = {
//       2015: {
//           '_AMT_tthd': [200000]
//       },
//       2016: {
//           '_EITC_c': [[ 900, 5000,  8000, 9000]],
//           '_II_em': [6000],
//           '_II_em_cpi': False,
//           '_SS_Earnings_c': [300000]
//       },
//       2017: {
//           '_AMT_tthd': [300000],
//           '_AMT_em_cpi': False
//       },
//       2018: {
//           '_II_em': [7500],
//           '_II_em_cpi': True,
//           '_SS_Earnings_c': [500000]
//       },
//       2019: {
//           '_EITC_c': [[1200, 7000, 10000, 12000]]
//       },
//       2020: {
//           '_II_em': [9000],
//           '_SS_Earnings_c': [700000],
//           '_AMT_em_cpi': True
//       }
//   }
"""


@pytest.yield_fixture
def input_file():
    """
    Temporary input file for SimpleTaxIO constructor.
    """
    ifile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ifile.write(INPUT_CONTENTS)
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture
def reform_file():
    """
    Temporary reform file for SimpleTaxIO constructor.
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


def test_1(input_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO contructor with no policy reform.
    """
    reform_file_name = None
    simtax = SimpleTaxIO(input_file.name, reform_file_name, False)
    assert simtax.number_input_lines() == NUM_INPUT_LINES


def test_2(input_file,  # pylint: disable=redefined-outer-name
           reform_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO contructor with a policy reform.
    """
    simtax = SimpleTaxIO(input_file.name, reform_file.name, False)
    assert simtax.number_input_lines() == NUM_INPUT_LINES
    # check that reform was implemented as specified above in REFORM_CONTENTS
    syr = 2013
    amt_tthd = simtax._policy._AMT_tthd  # pylint: disable=protected-access
    assert amt_tthd[2015 - syr] == 200000
    assert amt_tthd[2016 - syr] > 200000
    assert amt_tthd[2017 - syr] == 300000
    assert amt_tthd[2018 - syr] > 300000
    ii_em = simtax._policy._II_em  # pylint: disable=protected-access
    assert ii_em[2016 - syr] == 6000
    assert ii_em[2017 - syr] == 6000
    assert ii_em[2018 - syr] == 7500
    assert ii_em[2019 - syr] > 7500
    assert ii_em[2020 - syr] == 9000
    assert ii_em[2021 - syr] > 9000
    amt_em = simtax._policy._AMT_em  # pylint: disable=protected-access
    assert amt_em[2016 - syr, 0] > amt_em[2015 - syr, 0]
    assert amt_em[2017 - syr, 0] > amt_em[2016 - syr, 0]
    assert amt_em[2018 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2019 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2020 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2021 - syr, 0] > amt_em[2020 - syr, 0]
    assert amt_em[2022 - syr, 0] > amt_em[2021 - syr, 0]


def test_3(input_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO calculate method with no output writing.
    """
    reform_file_name = None
    simtax = SimpleTaxIO(input_file.name, reform_file_name, False)
    simtax.calculate(write_output_file=False)
    assert simtax.number_input_lines() == NUM_INPUT_LINES
