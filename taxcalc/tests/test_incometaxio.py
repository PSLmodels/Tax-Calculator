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
                         reform_filename=None,
                         blowup_input_data=False)
    assert inctax.tax_year() == taxyear


def test_2():
    """
    Test IncomeTaxIO calculate method with no output writing and no blowup.
    """
    taxyear = 2020
    inctax = IncomeTaxIO(input_filename=FAUX_PUF_CSV,
                         tax_year=taxyear,
                         reform_filename=None,
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


def test_3(rawinputfile):  # pylint: disable=redefined-outer-name
    """
    Test IncomeTaxIO calculate method with no output writing and with blowup.
    """
    taxyear = 2021
    inctax = IncomeTaxIO(input_filename=rawinputfile.name,
                         tax_year=taxyear,
                         reform_filename=None,
                         blowup_input_data=True)
    inctax.calculate(write_output_file=False)
    assert inctax.tax_year() == taxyear
