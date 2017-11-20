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
import json
import difflib
import pytest
import numpy as np
import pandas as pd
import copy
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, multiyear_diagnostic_table


@pytest.mark.requires_pufcsv
def test_agg(tests_path, puf_fullsample):
    """
    Test Tax-Calculator aggregate taxes with no policy reform using
    the full-sample puf.csv and a small sub-sample of puf.csv
    """
    # pylint: disable=too-many-locals,too-many-statements
    nyrs = 10
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    # create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_fullsample)
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
    if diff_lines:
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
    subsample = fullsample.sample(frac=subfrac,  # pylint: disable=no-member
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
            assert np.allclose(crs.c05800 + crs.othertaxes - crs.c07100,
                               crs.c09200)
            assert np.allclose(crs.c09200 - crs.refund, crs.iitax)
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
    if diff_lines:
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
    itax1 = (calc1.records.iitax * calc1.records.s006).sum()
    # create personal-refundable-credit-reform Calculator object, calc2
    reform = {reform_year: {'_II_credit': [[1000, 1000, 1000, 1000, 1000]]}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc2.advance_to_year(reform_year)
    calc2.calc_all()
    itax2 = (calc2.records.iitax * calc2.records.s006).sum()
    # create personal-nonrefundable-credit-reform Calculator object, calc3
    reform = {reform_year: {'_II_credit_nr': [[1000, 1000, 1000, 1000, 1000]]}}
    pol = Policy()
    pol.implement_reform(reform)
    calc3 = Calculator(policy=pol, records=rec)
    calc3.advance_to_year(reform_year)
    calc3.calc_all()
    itax3 = (calc3.records.iitax * calc3.records.s006).sum()
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
@pytest.mark.pre_release
def test_compatible_data(tests_path, puf_subsample):
    """

    """

    clppath = os.path.join(tests_path, '..', 'current_law_policy.json')
    pfile = open(clppath, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)

    # These parameters are exempt because they are not active under
    # current law and activating them would deactive other parameters.

    exempt = ['_CG_ec', '_CG_reinvest_ec_rt']

    p_xx = Policy()

    # Set baseline to activate parameters that are inactive under current law.
    reform_xx = {
        2017: {
            '_CTC_new_refund_limited': [True],
            '_FST_AGI_trt': [0.5],
            '_CTC_new_rt': [0.5],
            '_CTC_new_c': [5000],
            '_CTC_new_prt': [0.1],
            '_ID_BenefitSurtax_trt': [0.1],
            '_UBI3': [1000],
            '_PT_brk7': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ID_BenefitSurtax_crt': [0.1],
            '_II_credit_prt': [0.1],
            '_II_credit': [[100, 100, 100, 100, 100]],
            '_CG_brk3': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ALD_Dependents_Child_c': [1000],
            '_II_credit_nr': [[1000, 1000, 1000, 1000, 1000]],
            '_II_credit_nr_prt': [0.1],
            '_AMT_CG_brk3': [[500000, 500000, 500000, 500000, 500000]],
            '_AGI_surtax_thd': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_AGI_surtax_trt': [0.5],
            '_ID_AmountCap_rt': [0.5],
            '_II_brk7': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ID_BenefitCap_rt': [0.5],
            '_DependentCredit_Child_c': [500],
            '_PT_exclusion_rt': [.2],
            '_PT_rt7': [.35]
        }
    }

    p_xx.implement_reform(reform_xx)
    rec_xx = Records(data=puf_subsample)
    c_xx = Calculator(policy=p_xx, records=rec_xx)
    c_xx.advance_to_year(2018)
    c_xx.calc_all()

    for pname in allparams:
        param = allparams[pname]
        max_listed = param['range']['max']
        # Handle links to other params or self
        if isinstance(max_listed, unicode):
            if max_listed == 'default':
                max_val = param['value'][-1]
            else:
                max_val = allparams[max_listed]['value'][0]
        if not isinstance(max_listed, unicode):
            if isinstance(param['value'][0], list):
                max_val = [max_listed] * len(param['value'][0])
            else:
                max_val = max_listed
        min_listed = param['range']['min']
        if isinstance(min_listed, unicode):
            if min_listed == 'default':
                min_val = param['value'][-1]
            else:
                min_val = allparams[min_listed]['value'][0]
        if not isinstance(min_listed, unicode):
            if isinstance(param['value'][0], list):
                min_val = [min_listed] * len(param['value'][0])
            else:
                min_val = min_listed
        # Create reform dictionaries
        max_reform = copy.deepcopy(reform_xx)
        min_reform = copy.deepcopy(reform_xx)
        max_reform[2017][str(pname)] = [max_val]
        min_reform[2017][str(pname)] = [min_val]
        # Assess whether max reform changes results
        rec_yy = Records(data=puf_subsample)
        p_yy = Policy()
        p_yy.implement_reform(max_reform)
        c_yy = Calculator(policy=p_yy, records=rec_yy)
        c_yy.advance_to_year(2018)
        c_yy.calc_all()
        max_reform_change = ((c_yy.records.combined - c_xx.records.combined) *
                             c_xx.records.s006).sum()
        min_reform_change = 0
        # Assess whether min reform changes results, if max reform did not
        if max_reform_change == 0:
            p_yy = Policy()
            p_yy.implement_reform(min_reform)
            c_yy = Calculator(policy=p_yy, records=rec_xx)
            c_yy.advance_to_year(2018)
            c_yy.calc_all()
            min_reform_change = ((c_yy.records.combined -
                                 c_xx.records.combined) *
                                 c_xx.records.s006).sum()
            if min_reform_change == 0 and pname not in exempt:
                print(pname)
                assert param['compatible_data']['puf'] is False
        if max_reform_change != 0 or min_reform_change != 0:
            print(pname)
            assert param['compatible_data']['puf'] is True
