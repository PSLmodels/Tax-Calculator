"""
Tests for Tax-Calculator TaxCalcIO class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_taxcalcio.py
# pylint --disable=locally-disabled test_taxcalcio.py

import os
import tempfile
from io import StringIO
import pytest
import pandas as pd
from taxcalc import TaxCalcIO, Growdiff  # pylint: disable=import-error


RAWINPUTFILE_FUNITS = 4
RAWINPUTFILE_CONTENTS = (
    u'RECID,MARS\n'
    u'    1,   2\n'
    u'    2,   1\n'
    u'    3,   4\n'
    u'    4,   6\n'
)


EXPECTED_TO_STRING_OUTPUT = (  # from using RAWINPUTFILE_CONTENTS as input
    'RECID  YEAR  WEIGHT  INCTAX  LSTAX  PAYTAX\n'
    '    1  2021     0.0     0.0    0.0     0.0\n'
    '    2  2021     0.0     0.0    0.0     0.0\n'
    '    3  2021     0.0     0.0    0.0     0.0\n'
    '    4  2021     0.0     0.0    0.0     0.0'  # no trailing EOL character
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


@pytest.mark.parametrize("input_data, exact", [
    ('no-dot-csv-filename', True),
    (list(), False),
    ('bad_filename.csv', False),
])
def test_incorrect_creation_1(input_data, exact):
    """
    Ensure a ValueError is raised when created with invalid data pointers
    """
    with pytest.raises(ValueError):
        TaxCalcIO(input_data=input_data,
                  tax_year=2013,
                  reform=None,
                  assump=None,
                  growdiff_response=None,
                  aging_input_data=False,
                  exact_calculations=exact)


@pytest.yield_fixture
def reformfile0():
    """
    specify JSON text for reform
    """
    txt = """
    {
        "policy": {
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


# for fixture args, pylint: disable=redefined-outer-name


@pytest.mark.parametrize("year, ref, asm, gdr", [
    (2013, list(), None, None),
    (2013, None, list(), None),
    (2001, None, None, None),
    (2099, None, None, None),
    (2020, 'no-dot-json-reformfile', None, None),
    (2020, 'reformfile0', 'no-dot-json-assumpfile', None),
    (2020, 'reformfile0', None, dict()),
])
def test_incorrect_creation_2(rawinputfile, reformfile0, year, ref, asm, gdr):
    """
    Ensure a ValueError is raised when created with invalid parameters
    """
    # pylint: disable=too-many-arguments
    if ref == 'reformfile0':
        reform = reformfile0.name
    else:
        reform = ref
    with pytest.raises(ValueError):
        TaxCalcIO(
            input_data=rawinputfile.name,
            tax_year=year,
            reform=reform,
            assump=asm,
            growdiff_response=gdr,
            aging_input_data=False,
            exact_calculations=False)


def test_creation_with_aging(rawinputfile, reformfile0):
    """
    Test TaxCalcIO instantiation with no policy reform and with aging.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     reform=reformfile0.name,
                     assump=None,
                     growdiff_response=Growdiff(),
                     aging_input_data=True,
                     exact_calculations=False)
    assert tcio.tax_year() == taxyear
    taxyear = 2016
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     reform=None,
                     assump=None,
                     growdiff_response=None,
                     aging_input_data=True,
                     exact_calculations=False)
    assert tcio.tax_year() == taxyear


def test_2(rawinputfile, reformfile0):
    """
    Test TaxCalcIO calculate method with no output writing and no aging.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     reform=reformfile0.name,
                     assump=None,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    output = tcio.static_analysis()
    assert output == EXPECTED_TO_STRING_OUTPUT


REFORM_CONTENTS = """
// Example of a reform file suitable for the read_json_param_files() function.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within the "policy" object, the primary keys are parameters and
// secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
  "policy": {
    "_AMT_brk1": // top of first AMT tax bracket
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


ASSUMP_CONTENTS = """
// Example of an assump file suitable for the read_json_param_files() function.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within each "consumption", "behavior", "growdiff_baseline" and
// "growdiff_response" object, the primary keys are parameters and
// the secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
  "title": "",
  "author": "",
  "date": "",
  "consumption": { "_MPC_e18400": {"2018": [0.05]} },
  "behavior": {},
  "growdiff_baseline": {},
  "growdiff_response": {}
}
"""


@pytest.yield_fixture
def assumpfile1():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    afile.write(ASSUMP_CONTENTS)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_3(rawinputfile, reformfile1, assumpfile1):
    """
    Test TaxCalcIO calculate method with output writing but no aging,
    using file name for TaxCalcIO constructor input_data.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     reform=reformfile1.name,
                     assump=assumpfile1.name,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    outfilepath = tcio.output_filepath()
    # --ceeu output and standard output
    try:
        output = tcio.static_analysis(writing_output_file=True,
                                      output_ceeu=True)
    except:  # pylint: disable=bare-except
        if os.path.isfile(outfilepath):
            try:
                os.remove(outfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.calculate(ceeu)_ok' == 'no'
    # --dump output
    try:
        output = tcio.static_analysis(writing_output_file=True,
                                      output_dump=True)
    except:  # pylint: disable=bare-except
        if os.path.isfile(outfilepath):
            try:
                os.remove(outfilepath)
            except OSError:
                pass  # sometimes we can't remove a generated temporary file
        assert 'TaxCalcIO.calculate(dump)_ok' == 'no'
    # if tries were successful, try to remove the output files
    if os.path.isfile(outfilepath):
        try:
            os.remove(outfilepath)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file
    # check that output is empty string (because output was written to file)
    assert output == ''


def test_4(reformfile2, assumpfile1):
    """
    Test TaxCalcIO calculate method with no output writing and no aging,
    using DataFrame for TaxCalcIO constructor input_data.
    """
    input_stream = StringIO(RAWINPUTFILE_CONTENTS)
    input_dataframe = pd.read_csv(input_stream)
    taxyear = 2021
    tcio = TaxCalcIO(input_data=input_dataframe,
                     tax_year=taxyear,
                     reform=reformfile2.name,
                     assump=assumpfile1.name,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    output = tcio.static_analysis()
    assert output == EXPECTED_TO_STRING_OUTPUT


# skip test_5 until have a more realistic sample to replace puf_1991
# def test_5(puf_1991, reformfile1):
#     #
#     Test TaxCalcIO calculate method with output writing but no aging,
#     using file name for TaxCalcIO constructor input_data and writing
#     --graph output.
#     #
#     tcio = TaxCalcIO(input_data=puf_1991,
#                      tax_year=2016,
#                      reform=reformfile1.name,
#                      assump=None,
#                      growdiff_response=None,
#                      aging_input_data=False,
#                      exact_calculations=False)
#     output = tcio.static_analysis(writing_output_file=False,
#                                   output_graph=True)
#     # cleanup html files
#     assert output != ''


def test_6(rawinputfile):
    """
    Test TaxCalcIO calculate method with no output writing and no aging and
    no reform, using the --dump option.
    """
    taxyear = 2021
    tcio = TaxCalcIO(input_data=rawinputfile.name,
                     tax_year=taxyear,
                     reform=None,
                     assump=None,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    output = tcio.static_analysis(writing_output_file=False, output_dump=True)
    assert len(output) > 5000
    assert tcio.tax_year() == taxyear


LUMPSUM_REFORM_CONTENTS = """
{
  "policy": {
    "_LST": {"2013": [200]}
  }
}
"""


@pytest.yield_fixture
def lumpsumreformfile():
    """
    Temporary reform file without .json extension.
    """
    rfile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    rfile.write(LUMPSUM_REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_7(reformfile1, lumpsumreformfile):
    """
    Test TaxCalcIO calculate method with no output writing using ceeu option.
    """
    taxyear = 2020
    recdict = {'RECID': 1, 'MARS': 1, 'e00300': 100000, 's006': 1e8}
    recdf = pd.DataFrame(data=recdict, index=[0])

    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     reform=reformfile1.name,
                     assump=None,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    output = tcio.static_analysis(writing_output_file=False, output_ceeu=True)
    assert tcio.tax_year() == taxyear
    assert len(output) > 0

    tcio = TaxCalcIO(input_data=recdf,
                     tax_year=taxyear,
                     reform=lumpsumreformfile.name,
                     assump=None,
                     growdiff_response=None,
                     aging_input_data=False,
                     exact_calculations=False)
    output = tcio.static_analysis(writing_output_file=False, output_ceeu=True)
    assert tcio.tax_year() == taxyear
    assert len(output) > 0


BAD1_ASSUMP_CONTENTS = """
{
  "consumption": {
  },
  "behavior": {
      "_BE_sub": {"2020": [0.05]}
  },
  "growdiff_baseline": {
  },
  "growdiff_response": {
  }
}
"""


BAD2_ASSUMP_CONTENTS = """
{
  "consumption": {
  },
  "behavior": {
  },
  "growdiff_baseline": {
  },
  "growdiff_response": {
      "_ABOOK": {"2015": [-0.01]}
  }
}
"""


@pytest.yield_fixture
def assumpfile_bad1():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    afile.write(BAD1_ASSUMP_CONTENTS)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture
def assumpfile_bad2():
    """
    Temporary assumption file with .json extension.
    """
    afile = tempfile.NamedTemporaryFile(suffix='.json', mode='a', delete=False)
    afile.write(BAD2_ASSUMP_CONTENTS)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_9(reformfile2, assumpfile_bad1, assumpfile_bad2):
    """
    Test TaxCalcIO constructor with illegal assumptions.
    """
    input_stream = StringIO(RAWINPUTFILE_CONTENTS)
    input_dataframe = pd.read_csv(input_stream)
    taxyear = 2022
    with pytest.raises(ValueError):
        TaxCalcIO(input_data=input_dataframe,
                  tax_year=taxyear,
                  reform=reformfile2.name,
                  assump=assumpfile_bad1.name,
                  growdiff_response=None,
                  aging_input_data=False,
                  exact_calculations=False)
    with pytest.raises(ValueError):
        TaxCalcIO(input_data=input_dataframe,
                  tax_year=taxyear,
                  reform=reformfile2.name,
                  assump=assumpfile_bad2.name,
                  growdiff_response=None,
                  aging_input_data=False,
                  exact_calculations=False)
