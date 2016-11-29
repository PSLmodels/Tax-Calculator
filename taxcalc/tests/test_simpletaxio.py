"""
Tests for Tax-Calculator SimpleTaxIO class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_simpletaxio.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy \
#        test_simpletaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import tempfile
import pytest
from taxcalc import SimpleTaxIO  # pylint: disable=import-error


NUM_INPUT_LINES = 4
INPUT_CONTENTS = (
    '1 2014 0 1 0    0 95000 0 5000 0     0     0 0 0 0 0 0 0 0 0 9000 -1000\n'
    '2 2013 0 2 0    2 15000 0    0 0 50000 70000 0 0 0 0 0 0 0 0    0 -3000\n'
    '3 2014 0 3 1    0 40000 0 1000 0     0     0 0 0 0 0 0 0 0 0 1000 -1000\n'
    '4 2015 0 2 0 4039 15000 0    0 0 50000 70000 0 0 0 0 0 0 0 0    0 -3000\n'
)
REFORM_CONTENTS = """
// Example of a reform file suitable for the read_json_reform_file function.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within each "policy", "behavior", and "growth" object, the
// primary keys are parameters and secondary keys are years.
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
  },
  "behavior": {
  },
  "growth": {
  }
}
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


@pytest.mark.parametrize("filename, exact", [
    (list(), True),
    ('badname', False),
])
def test_incorrect_creation(filename, exact):
    """
    Test incorrect SimpleTaxIO instantiation.
    """
    with pytest.raises(ValueError):
        SimpleTaxIO(
            input_filename=filename,
            reform=None,
            exact_calculations=exact,
            emulate_taxsim_2441_logic=False,
            output_records=False
        )


BAD_REFORM_CONTENTS = """
{
  "policy": {
    "_AMT_brk1": {"2015": [200000], "2017": [300000]}
  },
  "behavior": {
    "_BE_sub": {"2013": [0.2]} // non-empty is illegal for SimpleTaxIO class
  },
  "growth": {
  }
}
"""


@pytest.yield_fixture
def bad_reform_file():
    """
    Temporary reform file for SimpleTaxIO constructor.
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(BAD_REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.mark.parametrize("reform", [
    'badname.json',
    list(),
    bad_reform_file])
def test_invalid_creation_w_file(input_file, reform):
    """
    Test incorrect SimpleTaxIO instantiation with input_file
    """
    # for fixture args, pylint: disable=redefined-outer-name
    with pytest.raises(ValueError):
        SimpleTaxIO(
            input_filename=input_file.name,
            reform=reform,
            exact_calculations=False,
            emulate_taxsim_2441_logic=False,
            output_records=False
        )


def test_1(input_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO instantiation with no policy reform.
    """
    SimpleTaxIO.show_iovar_definitions()
    simtax = SimpleTaxIO(input_filename=input_file.name,
                         reform=None,
                         exact_calculations=False,
                         emulate_taxsim_2441_logic=False,
                         output_records=False)
    assert simtax.number_input_lines() == NUM_INPUT_LINES
    # test extracting of weight and debugging variables
    crecs = simtax._calc.records  # pylint: disable=protected-access
    SimpleTaxIO.DVAR_NAMES = ['f2441']
    # pylint: disable=unused-variable
    ovar = SimpleTaxIO.extract_output(crecs, 0,
                                      exact=True, extract_weight=True)
    SimpleTaxIO.DVAR_NAMES = ['badvar']
    with pytest.raises(ValueError):
        ovar = SimpleTaxIO.extract_output(crecs, 0)
    SimpleTaxIO.DVAR_NAMES = []


def test_2(input_file,  # pylint: disable=redefined-outer-name
           reform_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO instantiation with a policy reform from JSON file.
    """
    simtax = SimpleTaxIO(input_filename=input_file.name,
                         reform=reform_file.name,
                         exact_calculations=False,
                         emulate_taxsim_2441_logic=False,
                         output_records=False)
    assert simtax.number_input_lines() == NUM_INPUT_LINES
    # check that reform was implemented as specified above in REFORM_CONTENTS
    syr = simtax.start_year()
    amt_brk1 = simtax._policy._AMT_brk1  # pylint: disable=protected-access
    assert amt_brk1[2015 - syr] == 200000
    assert amt_brk1[2016 - syr] > 200000
    assert amt_brk1[2017 - syr] == 300000
    assert amt_brk1[2018 - syr] > 300000
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
    Test SimpleTaxIO calculate method with a policy reform from dictionary.
    """
    policy_reform = {
        2016: {'_SS_Earnings_c': [300000]},
        2018: {'_SS_Earnings_c': [500000]},
        2020: {'_SS_Earnings_c': [700000]}
    }
    simtax = SimpleTaxIO(input_filename=input_file.name,
                         reform=policy_reform,
                         exact_calculations=False,
                         emulate_taxsim_2441_logic=True,
                         output_records=False)
    simtax.calculate()
    assert simtax.number_input_lines() == NUM_INPUT_LINES


@pytest.mark.parametrize("contents", [
    '1 2013 0 2 0\n',
    '1 2014 0 1 0 0 zyzab 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 1 0 0 95000 0 -500 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2001 0 1 0 0 95000 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 6 1 0 0 95000 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 4 0 0 95000 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 3 0 0 95000 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 1 0 2 95000 0 5000 0 0 0 0 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 1 0 0 95000 0 5000 0 0 0 9 0 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 1 0 0 95000 0 5000 0 0 0 0 9 0 0 0 0 0 0 9000 -1000\n',
    '1 2014 0 1 0 0 95000 0 5000 0 0 0 0 0 0 0 0 0 1 0 9000 -1000\n',
    ('1 2014 0 1 0 0 95000 0 5000 0     0     0 0 0 0 0 0 0 0 0 9000 -1000\n'
     '1 2013 0 2 0 2 15000 0    0 0 50000 70000 0 0 0 0 0 0 0 0    0 -3000\n'),
])
def test_bad_input_file(contents):
    """
    Ensure the provided file contents force a ValueError when used as input
    """
    ifile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ifile.write(contents)
    ifile.close()

    with pytest.raises(ValueError):
        SimpleTaxIO(
            input_filename=ifile.name,
            reform=None,
            exact_calculations=False,
            emulate_taxsim_2441_logic=False,
            output_records=False
        )

    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file
