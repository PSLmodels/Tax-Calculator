"""
Tests of Tax-Calculator using puf.csv input.

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_pufcsv.py
# pylint --disable=locally-disabled test_pufcsv.py

import os
import json
import pytest
import numpy as np
import pandas as pd
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator


START_YEAR = 2017


@pytest.mark.pufcsv_agg
@pytest.mark.requires_pufcsv
def test_agg(tests_path, puf_fullsample):
    """
    Test Tax-Calculator aggregate taxes with no policy reform using
    the full-sample puf.csv and a small sub-sample of puf.csv
    """
    # pylint: disable=too-many-locals,too-many-statements
    nyrs = 10
    # create a baseline Policy object with current-law policy parameters
    baseline_policy = Policy()
    # create a Records object (rec) containing all puf.csv input records
    recs = Records(data=puf_fullsample)
    # create a Calculator object using baseline policy and puf records
    calc = Calculator(policy=baseline_policy, records=recs)
    calc.advance_to_year(START_YEAR)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs).round(1)  # column labels are int
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # compare actual DataFrame, adt, with the expected DataFrame, edt
    aggres_path = os.path.join(tests_path, 'pufcsv_agg_expect.csv')
    edt = pd.read_csv(aggres_path, index_col=False)  # column labels are str
    edt.drop('Unnamed: 0', axis='columns', inplace=True)
    assert len(adt.columns.values) == len(edt.columns.values)
    diffs = False
    for icol in adt.columns.values:
        if not np.allclose(adt[icol].values, edt[str(icol)].values):
            diffs = True
    if diffs:
        new_filename = f'{aggres_path[:-10]}actual.csv'
        adt.to_csv(new_filename, float_format='%.1f')
        msg = 'PUFCSV AGG RESULTS DIFFER FOR FULL-SAMPLE\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN pufcsv_agg_actual.csv FILE ---\n'
        msg += '--- if new OK, copy pufcsv_agg_actual.csv to  ---\n'
        msg += '---                 pufcsv_agg_expect.csv     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '---       (both are in taxcalc/tests)         ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    # create aggregate diagnostic table using unweighted sub-sample of records
    fullsample = puf_fullsample
    rn_seed = 2222  # to ensure sub-sample is always the same
    subfrac = 0.05  # sub-sample fraction
    subsample = fullsample.sample(frac=subfrac, random_state=rn_seed)
    recs_subsample = Records(data=subsample)
    calc_subsample = Calculator(policy=baseline_policy, records=recs_subsample)
    calc_subsample.advance_to_year(START_YEAR)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    msg = ''
    for cyr in range(calc_start_year, calc_start_year + nyrs):
        reltol = 0.031  # maximum allowed relative difference in tax liability
        if not np.allclose(taxes_subsample[cyr], taxes_fullsample[cyr],
                           atol=0.0, rtol=reltol):
            reldiff = (taxes_subsample[cyr] / taxes_fullsample[cyr]) - 1.
            line1 = '\nPUFCSV AGG SUB-vs-FULL RESULTS DIFFER IN {}'
            line2 = '\n  when subfrac={:.3f}, rtol={:.4f}, seed={}'
            line3 = '\n  with sub={:.3f}, full={:.3f}, rdiff={:.4f}'
            msg += line1.format(cyr)
            msg += line2.format(subfrac, reltol, rn_seed)
            msg += line3.format(taxes_subsample[cyr],
                                taxes_fullsample[cyr],
                                reldiff)
    if msg:
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
    res += f'{sum_bincount} :'
    for idx in range(len(bin_edges) - 1):
        res += f' {bincount[idx]:6d}'
    res += '\n'
    if sum_bincount < mtr_data.size:
        res += 'WARNING: sum of bin counts is too low\n'
        mtr_min = mtr_data.min()
        mtr_max = mtr_data.max()
        bin_min = min(bin_edges)
        bin_max = max(bin_edges)
        if mtr_min < bin_min:
            res += f'         min(mtr)={mtr_min:.2f}\n'
            for idx in range(mtr_data.size):
                if mtr_data[idx] < bin_min:
                    res += (
                        f'         mtr={mtr_data[idx]:.2f} '
                        f'for recid={recid[idx]}\n'
                    )
        if mtr_max > bin_max:
            res += f'         max(mtr)={mtr_max:.2f}\n'
            for idx in range(mtr_data.size):
                if mtr_data[idx] > bin_max:
                    res += (
                        f'         mtr={mtr_data[idx]:.2f} '
                        f'for recid={recid[idx]}\n'
                    )
    return res


def nonsmall_diffs(linelist1, linelist2, small=0.0):
    """
    Return True if line lists differ significantly; otherwise return False.
    Significant numerical difference means one or more numbers differ (between
    linelist1 and linelist2) by more than the specified small amount.
    """
    # embedded function used only in nonsmall_diffs function
    def isfloat(value):
        """
        Return True if value can be cast to float; otherwise return False.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    # begin nonsmall_diffs logic
    assert isinstance(linelist1, list)
    assert isinstance(linelist2, list)
    if len(linelist1) != len(linelist2):
        return True
    assert 0.0 <= small <= 1.0
    epsilon = 1e-6
    smallamt = small + epsilon
    for line1, line2 in zip(linelist1, linelist2):
        if line1 == line2:
            continue
        tokens1 = line1.replace(',', '').split()
        tokens2 = line2.replace(',', '').split()
        for tok1, tok2 in zip(tokens1, tokens2):
            tok1_isfloat = isfloat(tok1)
            tok2_isfloat = isfloat(tok2)
            if tok1_isfloat and tok2_isfloat:
                if abs(float(tok1) - float(tok2)) <= smallamt:
                    continue
                return True
            if not tok1_isfloat and not tok2_isfloat:
                if tok1 == tok2:
                    continue
                return True
            return True
        return False


@pytest.mark.requires_pufcsv
def test_mtr(tests_path, puf_path):
    """
    Test Tax-Calculator marginal tax rates with no policy reform using puf.csv

    Compute histograms for each marginal tax rate income type using
    sample input from the puf.csv file and writing output to a string,
    which is then compared for differences with EXPECTED_MTR_RESULTS.
    """
    # pylint: disable=too-many-locals,too-many-statements
    assert len(PTAX_MTR_BIN_EDGES) == len(ITAX_MTR_BIN_EDGES)
    # construct actual results string, res
    res = ''
    if MTR_NEG_DIFF:
        res += 'MTR computed using NEGATIVE finite_diff '
    else:
        res += 'MTR computed using POSITIVE finite_diff '
    res += f'for tax year {MTR_TAX_YEAR}\n'
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    clp.set_year(MTR_TAX_YEAR)
    # create a Records object (puf) containing puf.csv input records
    puf = Records(data=puf_path)
    recid = puf.RECID  # pylint: disable=no-member
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    res += f'Total number of data records = {puf.array_length}\n'
    res += 'PTAX mtr histogram bin edges:\n'
    res += f'     {PTAX_MTR_BIN_EDGES}\n'
    res += 'ITAX mtr histogram bin edges:\n'
    res += f'     {ITAX_MTR_BIN_EDGES}\n'
    variable_header = 'PTAX and ITAX mtr histogram bin counts for'
    # compute marginal tax rate (mtr) histograms for each mtr variable
    for var_str in Calculator.MTR_VALID_VARIABLES:
        zero_out = var_str == 'e01400'
        (mtr_ptax, mtr_itax, _) = calc.mtr(variable_str=var_str,
                                           negative_finite_diff=MTR_NEG_DIFF,
                                           zero_out_calculated_vars=zero_out,
                                           wrt_full_compensation=False)
        if zero_out:
            # check that calculated variables are consistent
            assert np.allclose((calc.array('iitax') +
                                calc.array('payrolltax')),
                               calc.array('combined'))
            assert np.allclose(calc.array('ptax_was'),
                               calc.array('payrolltax'))
            assert np.allclose(calc.array('c21060') - calc.array('c21040'),
                               calc.array('c04470'))
            assert np.allclose(calc.array('taxbc') + calc.array('c09600'),
                               calc.array('c05800'))
            assert np.allclose((calc.array('c05800') +
                                calc.array('othertaxes') -
                                calc.array('c07100')),
                               calc.array('c09200'))
            assert np.allclose(calc.array('c09200') - calc.array('refund'),
                               calc.array('iitax'))
        if var_str == 'e00200s':
            # only MARS==2 filing units have valid MTR values
            mtr_ptax = mtr_ptax[calc.array('MARS') == 2]
            mtr_itax = mtr_itax[calc.array('MARS') == 2]
        res += f'{variable_header} {var_str}:\n'
        res += mtr_bin_counts(mtr_ptax, PTAX_MTR_BIN_EDGES, recid)
        res += mtr_bin_counts(mtr_itax, ITAX_MTR_BIN_EDGES, recid)
    # check for differences between actual and expected results
    mtrres_path = os.path.join(tests_path, 'pufcsv_mtr_expect.txt')
    with open(mtrres_path, 'r', encoding='utf-8') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    if nonsmall_diffs(res.splitlines(True), expected_results.splitlines(True)):
        new_filename = f'{mtrres_path[:-10]}actual.txt'
        with open(new_filename, 'w', encoding='utf-8') as new_file:
            new_file.write(res)
        msg = 'PUFCSV MTR RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN pufcsv_mtr_actual.txt FILE ---\n'
        msg += '--- if new OK, copy pufcsv_mtr_actual.txt to  ---\n'
        msg += '---                 pufcsv_mtr_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)


@pytest.mark.requires_pufcsv
def test_credit_reforms(puf_subsample):
    """
    Test personal credit reforms using puf.csv subsample
    """
    rec = Records(data=puf_subsample)
    reform_year = 2017
    # create current-law Calculator object, calc1
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    calc1.advance_to_year(reform_year)
    calc1.calc_all()
    itax1 = calc1.weighted_total('iitax')
    # create personal-refundable-credit-reform Calculator object, calc2
    reform = {'II_credit': {reform_year: [1000, 1000, 1000, 1000, 1000]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.advance_to_year(reform_year)
    calc2.calc_all()
    itax2 = calc2.weighted_total('iitax')
    # create personal-nonrefundable-credit-reform Calculator object, calc3
    reform = {'II_credit_nr': {reform_year: [1000, 1000, 1000, 1000, 1000]}}
    pol = Policy()
    pol.implement_reform(reform)
    calc3 = Calculator(policy=pol, records=rec)
    calc3.advance_to_year(reform_year)
    calc3.calc_all()
    itax3 = calc3.weighted_total('iitax')
    # check income tax revenues generated by the three Calculator objects
    assert itax2 < itax1  # because refundable credits lower revenues
    assert itax3 > itax2  # because nonrefundable credits lower revenues less
    assert itax3 < itax1  # because nonrefundable credits lower revenues some


@pytest.mark.requires_pufcsv
def test_puf_availability(tests_path, puf_path):
    """
    Cross-check records_variables.json data with variables in puf.csv file
    """
    # make set of variable names in puf.csv file
    pufdf = pd.read_csv(puf_path)
    pufvars = set(list(pufdf))
    # make set of variable names that are marked as puf.csv available
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r', encoding='utf-8') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_puf' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that pufvars and recvars sets are the same
    assert (pufvars - recvars) == set()
    assert (recvars - pufvars) == set()
