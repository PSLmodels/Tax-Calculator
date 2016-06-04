"""
Tests for Tax-Calculator IncomeTaxIO class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_incometaxio.py
# pylint --disable=locally-disabled test_incometaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
from taxcalc import IncomeTaxIO  # pylint: disable=import-error
from io import StringIO
import pandas as pd
import pytest
import tempfile


RAWINPUTFILE_FUNITS = 4
RAWINPUTFILE_CONTENTS = (
    u'RECID,MARS\n'
    u'    1,   2\n'
    u'    2,   1\n'
    u'    3,   4\n'
    u'    4,   6\n'
)

EXPECTED_OUTPUT = (  # from using RAWINPUTFILE_CONTENTS as input
    '1. 2021 0 0.00 0.00 0.00 -7.65 0.00 15.30 0.00 0.00 0.00 0.00 0.00 '
    '0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00\n'
    '2. 2021 0 0.00 0.00 0.00 -7.65 0.00 15.30 0.00 0.00 0.00 0.00 0.00 '
    '0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00\n'
    '3. 2021 0 0.00 0.00 0.00 -7.65 0.00 15.30 0.00 0.00 0.00 0.00 0.00 '
    '0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00\n'
    '4. 2021 0 0.00 0.00 0.00 0.00 0.00 15.30 0.00 0.00 0.00 0.00 0.00 '
    '0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00\n'
)


@pytest.yield_fixture
def rawinputfile():
    """
    Temporary input file that contains minimum required input variables.
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


def test_0(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test incorrect IncomeTaxIO instantiation.
    """
    # pylint: disable=unused-variable
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data='no-dot-csv-filename',
                             tax_year=2013,
                             policy_reform=None,
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data=list(),
                             tax_year=2013,
                             policy_reform=None,
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data=rawinputfile.name,
                             tax_year=2013,
                             policy_reform=list(),
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data='bad_filename.csv',
                             tax_year=2013,
                             policy_reform=None,
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data=rawinputfile.name,
                             tax_year=2001,
                             policy_reform=None,
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)
    with pytest.raises(ValueError):
        inctax = IncomeTaxIO(input_data=rawinputfile.name,
                             tax_year=2099,
                             policy_reform=None,
                             blowup_input_data=True,
                             output_weights=False,
                             output_records=False,
                             csv_dump=False)


def test_1(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO instantiation with no policy reform and with blowup.
    """
    IncomeTaxIO.show_iovar_definitions()
    taxyear = 2021
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=None,
                         blowup_input_data=True,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    assert inctax.tax_year() == taxyear
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=None,
                         blowup_input_data=True,
                         output_weights=True,
                         output_records=False,
                         csv_dump=False)
    assert inctax.tax_year() == taxyear
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=None,
                         blowup_input_data=False,
                         output_weights=True,
                         output_records=False,
                         csv_dump=False)
    assert inctax.tax_year() == taxyear


def test_2(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup.
    """
    taxyear = 2021
    reform_dict = {
        2016: {'_SS_Earnings_c': [300000]},
        2018: {'_SS_Earnings_c': [500000]},
        2020: {'_SS_Earnings_c': [700000]}
    }
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=reform_dict,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    assert output == EXPECTED_OUTPUT


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
def reformfile1():
    """
    Temporary reform file with .json extension.
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
def reformfile2():
    """
    Temporary reform file without .json extension.
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


def test_3(rawinputfile, reformfile1):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup,
    using file name for IncomeTaxIO constructor input_data.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=reformfile1.name,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    assert output == EXPECTED_OUTPUT


def test_4(reformfile2):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup,
    using DataFrame for IncomeTaxIO constructor input_data.
    """
    input_stream = StringIO(RAWINPUTFILE_CONTENTS)
    input_dataframe = pd.read_csv(input_stream)
    taxyear = 2021
    inctax = IncomeTaxIO(input_data=input_dataframe,
                         tax_year=taxyear,
                         policy_reform=reformfile2.name,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    assert output == EXPECTED_OUTPUT


def test_5(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup and
    no reform, using the output_records option.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=None,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=True,
                         csv_dump=False)
    inctax.output_records(writing_output_file=False)
    assert inctax.tax_year() == taxyear


def test_6(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup and
    no reform, using the csv_dump option.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_data=rawinputfile.name,
                         tax_year=taxyear,
                         policy_reform=None,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=True)
    inctax.csv_dump(writing_output_file=False)
    assert inctax.tax_year() == taxyear
