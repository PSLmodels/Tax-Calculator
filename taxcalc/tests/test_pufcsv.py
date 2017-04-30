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
# pylint --disable=locally-disabled test_pufcsv.py

import os
import difflib
import pytest
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, multiyear_diagnostic_table


@pytest.fixture(scope='session')
def puf_path(tests_path):
    """
    The path to the puf.csv taxpayer data file at repo root
    """
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.mark.requires_pufcsv
def test_agg(tests_path, puf_path):
    """
    Test Tax-Calculator aggregate taxes with no policy reform using
    the full-sample puf.csv and a two-percent sub-sample of puf.csv
    """
    # pylint: disable=too-many-locals,too-many-statements
    # for fixture args, pylint: disable=redefined-outer-name
    nyrs = 10
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    # create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_path)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=rec)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = multiyear_diagnostic_table(calc, nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # convert adt results to a string with a trailing EOL character
    adtstr = adt.to_string() + '\n'
    # generate differences between actual and expected results
    actual = adtstr.splitlines(True)
    aggres_path = os.path.join(tests_path, 'pufcsv_agg_expect.txt')
    with open(aggres_path, 'r') as expected_file:
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
        new_filename = '{}{}'.format(aggres_path[:-10], 'actual.txt')
        with open(new_filename, 'w') as new_file:
            new_file.write(adtstr)
        msg = 'PUFCSV AGG RESULTS DIFFER FOR FULL-SAMPLE\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN pufcsv_agg_actual.txt FILE ---\n'
        msg += '--- if new OK, copy pufcsv_agg_actual.txt to  ---\n'
        msg += '---                 pufcsv_agg_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    # create aggregate diagnostic table using sub sample of records
    fullsample = pd.read_csv(puf_path)
    rn_seed = 80  # to ensure two-percent sub-sample is always the same
    subsample = fullsample.sample(frac=0.02,  # pylint: disable=no-member
                                  random_state=rn_seed)
    rec_subsample = Records(data=subsample)
    calc_subsample = Calculator(policy=Policy(), records=rec_subsample)
    adt_subsample = multiyear_diagnostic_table(calc_subsample, num_years=nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    reltol = 0.01  # maximum allowed relative difference in tax liability
    if not np.allclose(taxes_subsample, taxes_fullsample,
                       atol=0.0, rtol=reltol):
        msg = 'PUFCSV AGG RESULTS DIFFER IN SUB-SAMPLE AND FULL-SAMPLE\n'
        msg += 'WHEN reltol = {:.4f}\n'.format(reltol)
        it_sub = np.nditer(taxes_subsample, flags=['f_index'])
        it_all = np.nditer(taxes_fullsample, flags=['f_index'])
        while not it_sub.finished:
            cyr = it_sub.index + calc_start_year
            tax_sub = float(it_sub[0])
            tax_all = float(it_all[0])
            reldiff = abs(tax_sub - tax_all) / abs(tax_all)
            if reldiff > reltol:
                msgstr = ' year,sub,full,reldif= {}\t{:.2f}\t{:.2f}\t{:.4f}\n'
                msg += msgstr.format(cyr, tax_sub, tax_all, reldiff)
            it_sub.iternext()
            it_all.iternext()
        raise ValueError(msg)


MTR_TAX_YEAR = 2013
MTR_NEG_DIFF = False  # set True to subtract (rather than add) small amount
# specify payrolltax mtr histogram bin boundaries (or edges):
PTAX_MTR_BIN_EDGES = [0.0, 0.02, 0.04, 0.06, 0.08,
                      0.10, 0.12, 0.14, 0.16, 0.18, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries
# specify incometax mtr histogram bin boundaries (or edges):
ITAX_MTR_BIN_EDGES = [-1.0, -0.30, -0.20, -0.10, 0.0,
                      0.10, 0.20, 0.30, 0.40, 0.50, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries


def mtr_bin_counts(mtr_data, bin_edges, recid):
    """
    Compute mtr histogram bin counts and return results as a string.
    """
    res = ''
    (bincount, _) = np.histogram(mtr_data.round(decimals=4), bins=bin_edges)
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
def test_mtr(tests_path, puf_path):
    """
    Test Tax-Calculator marginal tax rates with no policy reform using puf.csv

    Compute histograms for each marginal tax rate income type using
    sample input from the puf.csv file and writing output to a string,
    which is then compared for differences with EXPECTED_MTR_RESULTS.
    """
    # pylint: disable=too-many-locals,too-many-statements
    # for fixture args, pylint: disable=redefined-outer-name
    assert len(PTAX_MTR_BIN_EDGES) == len(ITAX_MTR_BIN_EDGES)
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
    puf = Records(data=puf_path)
    recid = puf.RECID  # pylint: disable=no-member
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    res += '{} = {}\n'.format('Total number of data records', puf.dim)
    res += 'PTAX mtr histogram bin edges:\n'
    res += '     {}\n'.format(PTAX_MTR_BIN_EDGES)
    res += 'ITAX mtr histogram bin edges:\n'
    res += '     {}\n'.format(ITAX_MTR_BIN_EDGES)
    variable_header = 'PTAX and ITAX mtr histogram bin counts for'
    # compute marginal tax rate (mtr) histograms for each mtr variable
    for var_str in Calculator.MTR_VALID_VARIABLES:
        zero_out = (var_str == 'e01400')
        (mtr_ptax, mtr_itax, _) = calc.mtr(variable_str=var_str,
                                           negative_finite_diff=MTR_NEG_DIFF,
                                           zero_out_calculated_vars=zero_out,
                                           wrt_full_compensation=False)
        if zero_out:
            # check that calculated variables are consistent
            crs = calc.records
            assert np.allclose(crs.iitax + crs.payrolltax, crs.combined)
            assert np.allclose(crs.ptax_was + crs.setax + crs.ptax_amc,
                               crs.payrolltax)
            assert np.allclose(crs.c21060 - crs.c21040, crs.c04470)
            assert np.allclose(crs.taxbc + crs.c09600, crs.c05800)
        if var_str == 'e00200s':
            # only MARS==2 filing units have valid MTR values
            mtr_ptax = mtr_ptax[calc.records.MARS == 2]
            mtr_itax = mtr_itax[calc.records.MARS == 2]
        res += '{} {}:\n'.format(variable_header, var_str)
        res += mtr_bin_counts(mtr_ptax, PTAX_MTR_BIN_EDGES, recid)
        res += mtr_bin_counts(mtr_itax, ITAX_MTR_BIN_EDGES, recid)
    # generate differences between actual and expected results
    actual = res.splitlines(True)
    mtrres_path = os.path.join(tests_path, 'pufcsv_mtr_expect.txt')
    with open(mtrres_path, 'r') as expected_file:
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
        new_filename = '{}{}'.format(mtrres_path[:-10], 'actual.txt')
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
