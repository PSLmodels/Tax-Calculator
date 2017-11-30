"""
Tests of Tax-Calculator using cps.csv input.

Note that the CPS-related files that are required to run this program
have been constructed by the Tax-Calculator development from publicly
available Census data files.  Hence, the CPS-related files are freely
available and are part of the Tax-Calculator repository.

Read tax-calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_cpscsv.py
# pylint --disable=locally-disabled test_cpscsv.py

import os
import sys
import json
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, multiyear_diagnostic_table
from taxcalc import Growfactors


def line_diff_list(actline, expline, small):
    """
    Return a list containing the pair of lines when they differ significantly;
    otherwise return an empty list.  Significant difference means one or more
    numbers differ (between actline and expline) by the "small" amount or more.
    """
    # embedded function used only in line_diff_list function
    def isfloat(value):
        """
        Return True if value can be cast to float; otherwise return False.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    # begin line_diff_list logic
    act_line = '<A>' + actline
    exp_line = '<E>' + expline
    diffs = list()
    act_tokens = actline.replace(',', '').split()
    exp_tokens = expline.replace(',', '').split()
    for atok, etok in zip(act_tokens, exp_tokens):
        atok_isfloat = isfloat(atok)
        etok_isfloat = isfloat(etok)
        if not atok_isfloat and not etok_isfloat:
            if atok == etok:
                continue
            else:
                diffs.extend([act_line, exp_line])
        elif atok_isfloat and etok_isfloat:
            if abs(float(atok) - float(etok)) < small:
                continue
            else:
                diffs.extend([act_line, exp_line])
        else:
            diffs.extend([act_line, exp_line])
    return diffs


def test_agg(tests_path):
    """
    Test current-law aggregate taxes using cps.csv file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    nyrs = 10
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    # create a Records object (rec) containing all cps.csv input records
    rec = Records.cps_constructor()
    # create a Calculator object using clp policy and cps records
    calc = Calculator(policy=clp, records=rec)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = multiyear_diagnostic_table(calc, nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # convert adt to a string with a trailing EOL character
    actual_results = adt.to_string() + '\n'
    act = actual_results.splitlines(True)
    # read expected results from file
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.txt')
    with open(aggres_path, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    exp = expected_results.splitlines(True)
    # ensure act and exp line lists have differences less than "small" value
    epsilon = 1e-6
    if sys.version_info.major == 2:
        small = epsilon  # tighter test for Python 2.7
    else:
        small = 0.1 + epsilon  # looser test for Python 3.6
    diff_lines = list()
    assert len(act) == len(exp)
    for actline, expline in zip(act, exp):
        if actline == expline:
            continue
        diffs = line_diff_list(actline, expline, small)
        if diffs:
            diff_lines.extend(diffs)
    # test failure if there are any diff_lines
    if diff_lines:
        new_filename = '{}{}'.format(aggres_path[:-10], 'actual.txt')
        with open(new_filename, 'w') as new_file:
            new_file.write(actual_results)
        msg = 'CPSCSV AGG RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN cpscsv_agg_actual.txt FILE ---\n'
        msg += '--- if new OK, copy cpscsv_agg_actual.txt to  ---\n'
        msg += '---                 cpscsv_agg_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        for line in diff_lines:
            msg += line
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    # create aggregate diagnostic table using unweighted sub-sample of records
    cps_filepath = os.path.join(tests_path, '..', 'cps.csv.gz')
    fullsample = pd.read_csv(cps_filepath)
    rn_seed = 180  # to ensure sub-sample is always the same
    subfrac = 0.03  # sub-sample fraction
    subsample = fullsample.sample(frac=subfrac, random_state=rn_seed)
    rec_subsample = Records(data=subsample,
                            gfactors=Growfactors(),
                            weights=Records.CPS_WEIGHTS_FILENAME,
                            adjust_ratios=Records.CPS_RATIOS_FILENAME,
                            start_year=Records.CPSCSV_YEAR)
    calc_subsample = Calculator(policy=Policy(), records=rec_subsample)
    adt_subsample = multiyear_diagnostic_table(calc_subsample, num_years=nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    reltol = 0.01  # maximum allowed relative difference in tax liability
    # TODO: skip first year because of BUG in cps_weights.csv file
    taxes_subsample = taxes_subsample[1:]  # TODO: eliminate code
    taxes_fullsample = taxes_fullsample[1:]  # TODO: eliminate code
    if not np.allclose(taxes_subsample, taxes_fullsample,
                       atol=0.0, rtol=reltol):
        msg = 'CPSCSV AGG RESULTS DIFFER IN SUB-SAMPLE AND FULL-SAMPLE\n'
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


def test_cps_availability(tests_path, cps_path):
    """
    Cross-check records_variables.json data with variables in cps.csv file.
    """
    cpsdf = pd.read_csv(cps_path)
    cpsvars = set(list(cpsdf))
    # make set of variable names that are marked as cps.csv available
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_cps' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that cpsvars and recvars sets are the same
    assert (cpsvars - recvars) == set()
    assert (recvars - cpsvars) == set()
