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


INPUT_LINES = 2
INPUT = (
    '1 2014 0 1 0 0 95000 0 5000 0     0     0 0 0 0 0 0 0 0 0 9000 -1000\n'
    '2 2013 0 2 0 1 15000 0    0 0 50000 70000 0 0 0 0 0 0 0 0    0 -3000'
)


@pytest.yield_fixture
def input_file():
    """
    Temporary input file for SimpleTaxIO constructor.
    """
    ifile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ifile.write(INPUT + '\n')
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    os.remove(ifile.name)


def test1(input_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO operation with no policy reform and no output writing.
    """
    reform_file_name = None
    simtax = SimpleTaxIO(input_file.name, reform_file_name)
    # simtax.calculate(write_output_file=False)
    assert simtax.number_input_lines() == INPUT_LINES
