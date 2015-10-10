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
import filecmp


INPUT1 = (
    '1 2013 0 2 0 1 15100 0 5000 0 50000 70000 0 0 0 0 0 1000 0 0 0 -3000'
)
OUTPUT1 = (
    '1. 2013 0 17141.25 0.00 2310.30 0.00 0.00 0.00 124335.00 '
    '1000.00 56235.00 0.00 7800.00 0.00 0.00 0.00 103135.00 17641.25 0.00 '
    '0.00 0.00 0.00 0.00 0.00 124335.00 0.00 17141.25'
)


@pytest.yield_fixture
def in1_file():
    """
    Temporary input file for SimpleTaxIO constructor.
    """
    ifile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ifile.write(INPUT1 + '\n')
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    os.remove(ifile.name)


@pytest.yield_fixture
def out1_file():
    """
    Expected output file produced from in1_file.
    """
    ofile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ofile.write(OUTPUT1 + '\n')
    ofile.close()
    # must close and then yield for Windows platform
    yield ofile
    os.remove(ofile.name)


def test1(in1_file, out1_file):  # pylint: disable=redefined-outer-name
    """
    Test SimpleTaxIO operation with no policy reform.
    """
    actual_output_file_name = '{}{}'.format(in1_file.name, '.out-simtax')
    simtax = SimpleTaxIO(in1_file.name, None)
    simtax.calculate()
    try:
        assert filecmp.cmp(actual_output_file_name, out1_file.name)
    except AssertionError:
        os.remove(actual_output_file_name)
        msg = 'SimpleTaxIO test1: actual and expected output files differ'
        raise Exception(msg)
    os.remove(actual_output_file_name)
