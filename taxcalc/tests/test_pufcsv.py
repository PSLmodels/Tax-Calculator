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
# pycodestyle test_pufcsv.py
# pylint --disable=locally-disabled test_pufcsv.py

from __future__ import print_function
import os
import sys
import json
import pytest
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, nonsmall_diffs
from taxcalc import run_nth_year_tax_calc_model


@pytest.mark.requires_pufcsv
def test_agg(tests_path, puf_fullsample):
    """
    Test Tax-Calculator aggregate taxes with no policy reform using
    the full-sample puf.csv and a small sub-sample of puf.csv
    """
    # pylint: disable=too-many-locals,too-many-statements
    nyrs = 10
    # create a baseline Policy object containing 2017_law.json parameters
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Calculator.read_json_param_objects(pre_tcja_jrf, None)
    baseline_policy = Policy()
    baseline_policy.implement_reform(pre_tcja['policy'])
    # create a Records object (rec) containing all puf.csv input records
    recs = Records(data=puf_fullsample)
    # create a Calculator object using baseline policy and puf records
    calc = Calculator(policy=baseline_policy, records=recs)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # convert adt results to a string with a trailing EOL character
    adtstr = adt.to_string() + '\n'
    # create actual and expected lists of diagnostic table lines
    actual = adtstr.splitlines(True)
    aggres_path = os.path.join(tests_path, 'pufcsv_agg_expect.txt')
    with open(aggres_path, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    expect = expected_results.splitlines(True)
    # ensure actual and expect lines have differences no more than small value
    if sys.version_info.major == 2:
        small = 0.0  # tighter test for Python 2.7
    else:
        small = 0.1  # looser test for Python 3.6
    diffs = nonsmall_diffs(actual, expect, small)
    if diffs:
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
    # create aggregate diagnostic table using unweighted sub-sample of records
    fullsample = puf_fullsample
    rn_seed = 180  # to ensure sub-sample is always the same
    subfrac = 0.05  # sub-sample fraction
    subsample = fullsample.sample(frac=subfrac, random_state=rn_seed)
    rec_subsample = Records(data=subsample)
    calc_subsample = Calculator(policy=baseline_policy, records=rec_subsample)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    reltol = 0.01  # maximum allowed relative difference in tax liability
    if not np.allclose(taxes_subsample, taxes_fullsample,
                       atol=0.0, rtol=reltol):
        msg = 'PUFCSV AGG RESULTS DIFFER IN SUB-SAMPLE AND FULL-SAMPLE\n'
        msg += 'WHEN subfrac={:.3f}, rtol={:.4f}, seed={}\n'.format(subfrac,
                                                                    reltol,
                                                                    rn_seed)
        it_sub = np.nditer(taxes_subsample, flags=['f_index'])
        it_all = np.nditer(taxes_fullsample, flags=['f_index'])
        while not it_sub.finished:
            cyr = it_sub.index + calc_start_year
            tax_sub = float(it_sub[0])
            tax_all = float(it_all[0])
            reldiff = abs(tax_sub - tax_all) / abs(tax_all)
            if reldiff > reltol:
                msgstr = ' year,sub,full,reldiff= {}\t{:.2f}\t{:.2f}\t{:.4f}\n'
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
    res += '{} = {}\n'.format('Total number of data records', puf.array_length)
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
            assert np.allclose((calc.array('iitax') +
                                calc.array('payrolltax')),
                               calc.array('combined'))
            assert np.allclose((calc.array('ptax_was') +
                                calc.array('setax') +
                                calc.array('ptax_amc')),
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
        res += '{} {}:\n'.format(variable_header, var_str)
        res += mtr_bin_counts(mtr_ptax, PTAX_MTR_BIN_EDGES, recid)
        res += mtr_bin_counts(mtr_itax, ITAX_MTR_BIN_EDGES, recid)
    # check for differences between actual and expected results
    mtrres_path = os.path.join(tests_path, 'pufcsv_mtr_expect.txt')
    with open(mtrres_path, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    if nonsmall_diffs(res.splitlines(True), expected_results.splitlines(True)):
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


@pytest.mark.requires_pufcsv
def test_mtr_pt_active(puf_subsample):
    """
    Test whether including wages in active income causes
    MTRs on e00900p and e26270 to be less than -1 (i.e., -100%)
    """
    # pylint: disable=too-many-locals
    rec = Records(data=puf_subsample)
    reform_year = 2018
    # create current-law Calculator object, calc1
    pol1 = Policy()
    calc1 = Calculator(policy=pol1, records=rec)
    calc1.advance_to_year(reform_year)
    calc1.calc_all()
    mtr1_e00900p = calc1.mtr('e00900p')[2]
    mtr1_e26270 = calc1.mtr('e26270')[2]
    assert min(mtr1_e00900p) > -1
    assert min(mtr1_e26270) > -1
    # change PT rates, calc2
    reform2 = {reform_year: {'_PT_rt7': [0.35]}}
    pol2 = Policy()
    pol2.implement_reform(reform2)
    calc2 = Calculator(policy=pol2, records=rec)
    calc2.advance_to_year(reform_year)
    calc2.calc_all()
    mtr2_e00900p = calc2.mtr('e00900p')[2]
    mtr2_e26270 = calc2.mtr('e26270')[2]
    assert min(mtr2_e00900p) > -1
    assert min(mtr2_e26270) > -1
    # change PT_wages_active_income
    reform3 = {reform_year: {'_PT_wages_active_income': [True]}}
    pol3 = Policy()
    pol3.implement_reform(reform3)
    calc3 = Calculator(policy=pol3, records=rec)
    calc3.advance_to_year(reform_year)
    calc3.calc_all()
    mtr3_e00900p = calc3.mtr('e00900p')[2]
    mtr3_e26270 = calc3.mtr('e26270')[2]
    assert min(mtr3_e00900p) > -1
    assert min(mtr3_e26270) > -1
    # change PT rates and PT_wages_active_income
    reform4 = {reform_year: {'_PT_wages_active_income': [True],
                             '_PT_rt7': [0.35]}}
    pol4 = Policy()
    pol4.implement_reform(reform4)
    calc4 = Calculator(policy=pol4, records=rec)
    calc4.advance_to_year(reform_year)
    calc4.calc_all()
    mtr4_e00900p = calc4.mtr('e00900p')[2]
    mtr4_e26270 = calc4.mtr('e26270')[2]
    assert min(mtr4_e00900p) > -1
    assert min(mtr4_e26270) > -1


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
    reform = {reform_year: {'_II_credit': [[1000, 1000, 1000, 1000, 1000]]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.advance_to_year(reform_year)
    calc2.calc_all()
    itax2 = calc2.weighted_total('iitax')
    # create personal-nonrefundable-credit-reform Calculator object, calc3
    reform = {reform_year: {'_II_credit_nr': [[1000, 1000, 1000, 1000, 1000]]}}
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
    with open(rvpath, 'r') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_puf' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that pufvars and recvars sets are the same
    assert (pufvars - recvars) == set()
    assert (recvars - pufvars) == set()


@pytest.mark.requires_pufcsv
@pytest.mark.xfail
def test_ubi_n_variables(puf_path):
    """
    Ensure that the three UBI n* variables add up to XTOT variable,
    recognizing that XTOT values are often capped in the IRS-SOI PUF,
    so that XTOT < NSUM might not indicate any data inconsistency.
    """
    pufdf = pd.read_csv(puf_path)
    xtot = pufdf['XTOT']
    nsum = pufdf['nu18'] + pufdf['n1820'] + pufdf['n21']
    if not np.sum(xtot > nsum) == 0:
        print('number xtot > nsum is:', np.sum(xtot > nsum))
        assert 'XTOT' <= '(nu18+n1820+n21)'


@pytest.mark.requires_pufcsv
def test_run_tax_calc_model(tests_path):
    """
    Test tbi.run_nth_year_tax_calc_model function using PUF data.
    """
    user_modifications = {
        'policy': {
            2016: {'_II_rt3': [0.33],
                   '_PT_rt3': [0.33],
                   '_II_rt4': [0.33],
                   '_PT_rt4': [0.33]}
        },
        'consumption': {
            2016: {'_MPC_e20400': [0.01]}
        },
        'behavior': {
            2016: {'_BE_sub': [0.25]}
        },
        'growdiff_baseline': {
        },
        'growdiff_response': {
        }
    }
    res = run_nth_year_tax_calc_model(year_n=2, start_year=2018,
                                      use_puf_not_cps=True,
                                      use_full_sample=False,
                                      user_mods=user_modifications,
                                      return_dict=True)
    assert isinstance(res, dict)
    # put actual results in a multiline string
    actual_results = ''
    for tbl in sorted(res.keys()):
        actual_results += 'TABLE {} RESULTS:\n'.format(tbl)
        actual_results += json.dumps(res[tbl], sort_keys=True,
                                     indent=4, separators=(',', ': ')) + '\n'
    # read expected results from file
    expect_fname = 'tbi_puf_expect.txt'
    expect_path = os.path.join(tests_path, expect_fname)
    with open(expect_path, 'r') as expect_file:
        expect_results = expect_file.read()
    # ensure actual and expect results have no differences
    diffs = nonsmall_diffs(actual_results.splitlines(True),
                           expect_results.splitlines(True))
    if diffs:
        actual_fname = '{}{}'.format(expect_fname[:-10], 'actual.txt')
        actual_path = os.path.join(tests_path, actual_fname)
        with open(actual_path, 'w') as actual_file:
            actual_file.write(actual_results)
        msg = 'TBI RESULTS DIFFER\n'
        msg += '----------------------------------------------\n'
        msg += '--- NEW RESULTS IN {} FILE ---\n'
        msg += '--- if new OK, copy {} to  ---\n'
        msg += '---                 {}     ---\n'
        msg += '---            and rerun test.             ---\n'
        msg += '----------------------------------------------\n'
        raise ValueError(msg.format(actual_fname, actual_fname, expect_fname))
