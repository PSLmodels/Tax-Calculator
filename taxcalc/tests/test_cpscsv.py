"""
Tests of Tax-Calculator using cps.csv input.

Note that the CPS-related files that are required to run this program
have been constructed by the Tax-Calculator development team from publicly
available Census data files.  Hence, the CPS-related files are freely
available and are part of the Tax-Calculator repository.

Read Tax-Calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_cpscsv.py
# pylint --disable=locally-disabled test_cpscsv.py

import os
import json
import pytest
import numpy as np
import pandas as pd
from taxcalc.growfactors import GrowFactors
from taxcalc.growdiff import GrowDiff
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator


START_YEAR = 2017


@pytest.mark.cpscsv_agg
def test_agg(tests_path, cps_fullsample):
    """
    Test current-law aggregate taxes using cps.csv file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    nyrs = 10
    # create a baseline Policy object with current-law policy parameters
    baseline_policy = Policy()
    # create a Records object (rec) containing all cps.csv input records
    recs = Records.cps_constructor(data=cps_fullsample)
    # create a Calculator object using baseline policy and cps records
    calc = Calculator(policy=baseline_policy, records=recs)
    calc.advance_to_year(START_YEAR)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs).round(1)  # column labels are int
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # compare actual DataFrame, adt, with the expected DataFrame, edt
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.csv')
    edt = pd.read_csv(aggres_path, index_col=False)  # column labels are str
    edt.drop('Unnamed: 0', axis='columns', inplace=True)
    assert len(adt.columns.values) == len(edt.columns.values)
    diffs = False
    for icol in adt.columns.values:
        if not np.allclose(adt[icol], edt[str(icol)]):
            diffs = True
    if diffs:
        new_filename = f'{aggres_path[:-10]}actual.csv'
        adt.to_csv(new_filename, float_format='%.1f')
        msg = 'CPSCSV AGG RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN cpscsv_agg_actual.csv FILE ---\n'
        msg += '--- if new OK, copy cpscsv_agg_actual.csv to  ---\n'
        msg += '---                 cpscsv_agg_expect.csv     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '---       (both are in taxcalc/tests)         ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    # create aggregate diagnostic table using unweighted sub-sample of records
    rn_seed = 180  # to ensure sub-sample is always the same
    subfrac = 0.07  # sub-sample fraction
    subsample = cps_fullsample.sample(frac=subfrac, random_state=rn_seed)
    recs_subsample = Records.cps_constructor(data=subsample)
    calc_subsample = Calculator(policy=baseline_policy, records=recs_subsample)
    calc_subsample.advance_to_year(START_YEAR)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    print('taxes_submsampe = ', taxes_subsample)
    print('TAXES full sample = ', taxes_fullsample)
    msg = ''
    for cyr in range(calc_start_year, calc_start_year + nyrs):
        if cyr == calc_start_year:
            reltol = 0.0232
        else:
            reltol = 0.0444
        if not np.allclose(taxes_subsample[cyr], taxes_fullsample[cyr],
                           atol=0.0, rtol=reltol):
            reldiff = (taxes_subsample[cyr] / taxes_fullsample[cyr]) - 1.
            line1 = f'\nCPSCSV AGG SUB-vs-FULL RESULTS DIFFER IN {cyr}'
            line2 = (
                f'\n  when subfrac={subfrac:.3f}, rtol={reltol:.4f}, '
                f'seed={rn_seed}'
            )
            line3 = (
                f'\n  with sub={taxes_subsample[cyr]:.3f}, '
                f'full={taxes_fullsample[cyr]:.3f}, '
                f'rdiff={reldiff:.4f}'
            )
            msg += line1 + line2 + line3
    if msg:
        raise ValueError(msg)


def test_cps_availability(tests_path, cps_path):
    """
    Cross-check records_variables.json data with variables in cps.csv file.
    """
    cpsdf = pd.read_csv(cps_path)
    cpsvars = set(list(cpsdf))
    # make set of variable names that are marked as cps.csv available
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r', encoding='utf-8') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_cps' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that cpsvars and recvars sets are the same
    assert (cpsvars - recvars) == set()
    assert (recvars - cpsvars) == set()


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


def test_flexible_last_budget_year(cps_fullsample):
    """
    Test flexible LAST_BUDGET_YEAR logic using cps.csv file.
    """
    tax_calc_year = Policy.LAST_BUDGET_YEAR - 1
    growdiff_year = tax_calc_year - 1
    growdiff_dict = {'AWAGE': {growdiff_year: 0.01, tax_calc_year: 0.0}}

    def default_calculator(growdiff_dictionary):
        """
        Return CPS-based Calculator object using default LAST_BUDGET_YEAR.
        """
        g_factors = GrowFactors()
        gdiff = GrowDiff()
        gdiff.update_growdiff(growdiff_dictionary)
        gdiff.apply_to(g_factors)
        pol = Policy(gfactors=g_factors)
        rec = Records.cps_constructor(data=cps_fullsample, gfactors=g_factors)
        calc = Calculator(policy=pol, records=rec)
        return calc

    def flexible_calculator(growdiff_dictionary, last_b_year):
        """
        Return CPS-based Calculator object using custom LAST_BUDGET_YEAR.
        """
        g_factors = GrowFactors()
        gdiff = GrowDiff(last_budget_year=last_b_year)
        gdiff.update_growdiff(growdiff_dictionary)
        gdiff.apply_to(g_factors)
        pol = Policy(gfactors=g_factors, last_budget_year=last_b_year)
        rec = Records.cps_constructor(data=cps_fullsample, gfactors=g_factors)
        calc = Calculator(policy=pol, records=rec)
        return calc

    # begin main test logic
    cdef = default_calculator(growdiff_dict)
    cdef.advance_to_year(tax_calc_year)
    cdef.calc_all()
    iitax_def = round(cdef.weighted_total('iitax'))

    cflx = flexible_calculator(growdiff_dict, tax_calc_year)
    cflx.advance_to_year(tax_calc_year)
    cflx.calc_all()
    iitax_flx = round(cflx.weighted_total('iitax'))

    assert np.allclose([iitax_flx], [iitax_def])
