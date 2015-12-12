"""
Tests for Tax-Calculator IncomeTaxIO class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_incometaxio.py
# pylint --disable=locally-disabled incometaxio.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '../../'))
from taxcalc import IncomeTaxIO  # pylint: disable=import-error


# use 1991 PUF-like data to emulate current PUF, which is private
FAUX_PUF_CSV = os.path.join(CUR_PATH, '../../tax_all1991_puf.gz')


def test_1():
    """
    Test IncomeTaxIO constructor with no policy reform.
    """
    taxyear = 2020
    inctax = IncomeTaxIO(input_filename=FAUX_PUF_CSV,
                         tax_year=taxyear,
                         reform_filename=None,
                         blowup_input_data=False)
    assert inctax.tax_year() == taxyear


def test_2():
    """
    Test IncomeTaxIO calculate method with no output writing.
    """
    taxyear = 2020
    inctax = IncomeTaxIO(input_filename=FAUX_PUF_CSV,
                         tax_year=taxyear,
                         reform_filename=None,
                         blowup_input_data=False)
    inctax.calculate(write_output_file=False)
    assert inctax.tax_year() == taxyear
