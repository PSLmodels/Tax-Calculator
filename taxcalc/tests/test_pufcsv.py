"""
Tests of Tax-Calculator using puf.csv input.

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.

Read tax-calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_pufcsv.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy \
#        test_pufcsv.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
from taxcalc import multiyear_diagnostic_table  # pylint: disable=import-error
PUFCSV_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
AGGRES_PATH = os.path.join(CUR_PATH, 'pufcsv_agg_expect.txt')
MTRRES_PATH = os.path.join(CUR_PATH, 'pufcsv_mtr_expect.txt')
import pytest
import difflib
import numpy as np
import pandas as pd


@pytest.mark.requires_pufcsv
def test_sample():
    """
    Test if reading in a sample of the data produces a reasonable estimate
    relative to the full data set
    """
    # Full dataset
    clp = Policy()
    puf = Records(data=PUFCSV_PATH)
    calc = Calculator(policy=clp, records=puf)
    adt = multiyear_diagnostic_table(calc, num_years=10)

    # Sample sample dataset
    clp2 = Policy()
    tax_data_full = pd.read_csv(PUFCSV_PATH)
    tax_data = tax_data_full.sample(frac=0.02)
    puf_sample = Records(data=tax_data)
    calc_sample = Calculator(policy=clp2, records=puf_sample)
    adt_sample = multiyear_diagnostic_table(calc_sample, num_years=10)

    # Get the final combined tax liability for the budget period
    # in the sample and the full dataset and make sure they are close
    full_tax_liability = adt.loc["Combined liability ($b)"]
    sample_tax_liability = adt_sample.loc["Combined liability ($b)"]
    max_val = max(full_tax_liability.max(), sample_tax_liability.max())
    rel_diff = max(abs(full_tax_liability - sample_tax_liability)) / max_val

    # Fail on greater than 5% releative difference in any budget year
    assert rel_diff < 0.05


@pytest.mark.requires_pufcsv
def test_agg():
    """
    Test Tax-Calculator aggregate taxes with no policy reform using puf.csv
    """
    # pylint: disable=too-many-locals
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    # create a Records object (puf) containing puf.csv input records
    puf = Records(data=PUFCSV_PATH)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = multiyear_diagnostic_table(calc, 10)
    # convert adt results to a string with a trailing EOL character
    adtstr = adt.to_string() + '\n'
    # generate differences between actual and expected results
    actual = adtstr.splitlines(True)
    with open(AGGRES_PATH, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    expected = expected_results.splitlines(True)
    diff = difflib.unified_diff(expected, actual,
                                fromfile='expected', tofile='actual', n=0)
    # convert diff generator into a list of lines:
    diff_lines = list()
    for line in diff:
        diff_lines.append(line)
    # test failure if there are any diff_lines
    if len(diff_lines) > 0:
        new_filename = '{}{}'.format(AGGRES_PATH[:-10], 'actual.txt')
        with open(new_filename, 'w') as new_file:
            new_file.write(adtstr)
        msg = 'PUFCSV AGG RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN pufcsv_agg_actual.txt FILE ---\n'
        msg += '--- if new OK, copy pufcsv_agg_actual.txt to  ---\n'
        msg += '---                 pufcsv_agg_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)


MTR_TAX_YEAR = 2013
MTR_NEG_DIFF = False  # set True to subtract (rather than add) small amount
# specify FICA mtr histogram bin boundaries (or edges):
FICA_MTR_BIN_EDGES = [0.0, 0.02, 0.04, 0.06, 0.08,
                      0.10, 0.12, 0.14, 0.16, 0.18, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries
# specify IIT mtr histogram bin boundaries (or edges):
IIT_MTR_BIN_EDGES = [-1.0, -0.30, -0.20, -0.10, 0.0,
                     0.10, 0.20, 0.30, 0.40, 0.50, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries


def mtr_bin_counts(mtr_data, bin_edges, recid):
    """
    Compute mtr histogram bin counts and return results as a string.
    """
    res = ''
    (bincount, _) = np.histogram(mtr_data, bins=bin_edges)
    sum_bincount = np.sum(bincount)
    res += '{} :'.format(sum_bincount)
    for idx in range(len(bin_edges) - 1):
        res += ' {:6d}'.format(bincount[idx])
    res += '\n'
    if sum_bincount < mtr_data.size:
        res += 'WARNING: sum of bin counts is too low\n'
        recinfo = '         mtr={:.2f} for recid={}\n'
        mtr_min = mtr_data.min()
        mtr_max = mtr_data.max()
        bin_min = min(bin_edges)
        bin_max = max(bin_edges)
        if mtr_min < bin_min:
            res += '         min(mtr)={:.2f}\n'.format(mtr_min)
            for idx in range(mtr_data.size):
                if mtr_data[idx] < bin_min:
                    res += recinfo.format(mtr_data[idx], recid[idx])
        if mtr_max > bin_max:
            res += '         max(mtr)={:.2f}\n'.format(mtr_max)
            for idx in range(mtr_data.size):
                if mtr_data[idx] > bin_max:
                    res += recinfo.format(mtr_data[idx], recid[idx])
    return res


@pytest.mark.requires_pufcsv
def test_mtr():
    """
    Test Tax-Calculator marginal tax rates with no policy reform using puf.csv

    Compute histograms for each marginal tax rate income type using
    sample input from the puf.csv file and writing output to a string,
    which is then compared for differences with EXPECTED_MTR_RESULTS.
    """
    # pylint: disable=too-many-locals
    assert len(FICA_MTR_BIN_EDGES) == len(IIT_MTR_BIN_EDGES)
    # construct actual results string, res
    res = ''
    if MTR_NEG_DIFF:
        res += 'MTR computed using NEGATIVE finite_diff '
    else:
        res += 'MTR computed using POSITIVE finite_diff '
    res += 'for tax year {}\n'.format(MTR_TAX_YEAR)
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    clp.set_year(MTR_TAX_YEAR)
    # create a Records object (puf) containing puf.csv input records
    puf = Records(data=PUFCSV_PATH)
    recid = puf.RECID  # pylint: disable=no-member
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    res += '{} = {}\n'.format('Total number of data records', puf.dim)
    res += 'FICA mtr histogram bin edges:\n'
    res += '     {}\n'.format(FICA_MTR_BIN_EDGES)
    res += 'IIT mtr histogram bin edges:\n'
    res += '     {}\n'.format(IIT_MTR_BIN_EDGES)
    inctype_header = 'FICA and IIT mtr histogram bin counts for'
    # compute marginal tax rate (mtr) histograms for each mtr income type
    for inctype in Calculator.MTR_VALID_INCOME_TYPES:
        if inctype == 'e01400':
            zero_out = True
        else:
            zero_out = False
        (mtr_fica, mtr_iit, _) = calc.mtr(income_type_str=inctype,
                                          negative_finite_diff=MTR_NEG_DIFF,
                                          zero_out_calculated_vars=zero_out,
                                          wrt_full_compensation=False)
        res += '{} {}:\n'.format(inctype_header, inctype)
        res += mtr_bin_counts(mtr_fica, FICA_MTR_BIN_EDGES, recid)
        res += mtr_bin_counts(mtr_iit, IIT_MTR_BIN_EDGES, recid)
    # generate differences between actual and expected results
    actual = res.splitlines(True)
    with open(MTRRES_PATH, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    expected = expected_results.splitlines(True)
    diff = difflib.unified_diff(expected, actual,
                                fromfile='expected', tofile='actual', n=0)
    # convert diff generator into a list of lines:
    diff_lines = list()
    for line in diff:
        diff_lines.append(line)
    # test failure if there are any diff_lines
    if len(diff_lines) > 0:
        new_filename = '{}{}'.format(MTRRES_PATH[:-10], 'actual.txt')
        with open(new_filename, 'w') as new_file:
            new_file.write(res)
        msg = 'PUFCSV MTR RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN pufcsv_mtr_actual.txt FILE ---\n'
        msg += '--- if new OK, copy pufcsv_mtr_actual.txt to  ---\n'
        msg += '---                 pufcsv_mtr_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
