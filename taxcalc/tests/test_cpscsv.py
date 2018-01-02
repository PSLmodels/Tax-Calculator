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
from taxcalc import Policy, Records, Calculator, Growfactors, nonsmall_diffs


def test_agg(tests_path):
    """
    Test current-law aggregate taxes using cps.csv file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    nyrs = 10
    # create a baseline Policy object containing 2017_law.json parameters
    pre_tcja_jrf = os.path.join(tests_path, '..', 'reforms', '2017_law.json')
    pre_tcja = Calculator.read_json_param_objects(pre_tcja_jrf, None)
    baseline_policy = Policy()
    baseline_policy.implement_reform(pre_tcja['policy'])
    # create a Records object (rec) containing all cps.csv input records
    rec = Records.cps_constructor()
    # create a Calculator object using baseline policy and cps records
    calc = Calculator(policy=baseline_policy, records=rec)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # convert adt to a string with a trailing EOL character
    actual_results = adt.to_string() + '\n'
    # read expected results from file
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.txt')
    with open(aggres_path, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    # ensure actual and expected results have no nonsmall differences
    if sys.version_info.major == 2:
        small = 0.0  # tighter test for Python 2.7
    else:
        small = 0.1  # looser test for Python 3.6
    diffs = nonsmall_diffs(actual_results.splitlines(True),
                           expected_results.splitlines(True), small)
    if diffs:
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
    calc_subsample = Calculator(policy=baseline_policy, records=rec_subsample)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
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
