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
import numpy as np
import pandas as pd
import pytest
from taxcalc.growfactors import GrowFactors
from taxcalc.growdiff import GrowDiff
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator


START_YEAR = 2017
NUM_YEARS = 19
# split the NUM_YEARS into chunks that pytest-xdist can execute in parallel
# (each chunk is a (first_year, number_of_years) pair)
YEAR_CHUNKS = [(2017, 7), (2024, 6), (2030, 6)]


def test_year_chunks():
    """
    Check that YEAR_CHUNKS exactly cover the NUM_YEARS starting in START_YEAR.
    """
    years = []
    for first_year, nyrs in YEAR_CHUNKS:
        years.extend(range(first_year, first_year + nyrs))
    assert years == list(range(START_YEAR, START_YEAR + NUM_YEARS))


@pytest.mark.parametrize('first_year, nyrs', YEAR_CHUNKS)
def test_agg(first_year, nyrs,
             tests_path, cps_fullsample, full_claiming_assumption):
    """
    Test current-law aggregate taxes using cps.csv file for nyrs years
    beginning with first_year.
    """
    # pylint: disable=too-many-locals
    # create a baseline Policy object with current-law policy parameters
    baseline_policy = Policy()
    baseline_policy.implement_reform(full_claiming_assumption)
    # create a Records object (rec) containing all cps.csv input records
    recs = Records.cps_constructor(data=cps_fullsample)
    # create a Calculator object using baseline policy and cps records
    calc = Calculator(policy=baseline_policy, records=recs)
    calc.advance_to_year(first_year)
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs).round(1)  # column labels are int
    # compare actual DataFrame, adt, with the expected DataFrame, edt
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.csv')
    edt = pd.read_csv(aggres_path, index_col=0)  # column labels are str
    years = [str(year) for year in range(first_year, first_year + nyrs)]
    assert list(adt.columns.values) == [int(year) for year in years]
    assert set(years).issubset(set(edt.columns.values))
    diffs = False
    for icol in adt.columns.values:
        if not np.allclose(adt[icol], edt[str(icol)]):
            diffs = True
    if diffs:
        # write this chunk's actual results to a chunk file, which is
        # merged into cpscsv_agg_actual.csv at the end of the pytest session
        # by the pytest_sessionfinish hook in conftest.py
        last_year = first_year + nyrs - 1
        chunk_filename = (
            f'{aggres_path[:-10]}actual_{first_year}-{last_year}.csv'
        )
        adt.to_csv(chunk_filename, float_format='%.1f')
        msg = f'CPSCSV AGG RESULTS DIFFER IN {first_year}-{last_year}\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN cpscsv_agg_actual.csv FILE ---\n'
        msg += '--- if new OK, copy cpscsv_agg_actual.csv to  ---\n'
        msg += '---                 cpscsv_agg_expect.csv     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '---       (both are in taxcalc/tests)         ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)


def test_agg_subsample(tests_path, cps_fullsample, full_claiming_assumption):
    """
    Test that current-law aggregate taxes computed using an unweighted
    sub-sample of cps.csv records are close to the full-sample taxes,
    which are read from the cpscsv_agg_expect.csv file (whose contents
    are checked by the test_agg function).
    """
    # pylint: disable=too-many-locals
    nyrs = NUM_YEARS
    # get full-sample combined tax liability from expected results file
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.csv')
    edt = pd.read_csv(aggres_path, index_col=0)  # column labels are str
    taxes_fullsample = edt.loc['Combined Liability ($b)']
    # create aggregate diagnostic table using unweighted sub-sample of records
    baseline_policy = Policy()
    baseline_policy.implement_reform(full_claiming_assumption)
    rn_seed = 180  # to ensure sub-sample is always the same
    subfrac = 0.07  # sub-sample fraction
    subsample = cps_fullsample.sample(frac=subfrac, random_state=rn_seed)
    recs_subsample = Records.cps_constructor(data=subsample)
    calc_subsample = Calculator(policy=baseline_policy, records=recs_subsample)
    calc_subsample.advance_to_year(START_YEAR)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc['Combined Liability ($b)']
    msg = ''
    for cyr in range(START_YEAR, START_YEAR + nyrs):
        if cyr == START_YEAR:
            reltol = 0.0232
        else:
            reltol = 0.0444
        tax_sub = taxes_subsample[cyr]
        tax_full = taxes_fullsample[str(cyr)]
        if not np.allclose(tax_sub, tax_full, atol=0.0, rtol=reltol):
            reldiff = (tax_sub / tax_full) - 1.
            line1 = f'\nCPSCSV AGG SUB-vs-FULL RESULTS DIFFER IN {cyr}'
            line2 = (
                f'\n  when subfrac={subfrac:.3f}, rtol={reltol:.4f}, '
                f'seed={rn_seed}'
            )
            line3 = (
                f'\n  with sub={tax_sub:.3f}, '
                f'full={tax_full:.3f}, '
                f'rdiff={reldiff:.4f}'
            )
            msg += line1 + line2 + line3
    if msg:
        raise ValueError(msg)


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
