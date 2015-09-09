import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import tempfile
import pytest
from numba import jit, vectorize, guvectorize
from taxcalc import *
import copy

WEIGHTS_FILENAME = "../../WEIGHTS_testing.csv"
weights_path = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
weights = pd.read_csv(weights_path)

all_cols = set()
tax_dta_path = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")
tax_dta = pd.read_csv(tax_dta_path, compression='gzip')

# Fix-up. MIdR needs to be type int64 to match PUF
tax_dta['midr'] = tax_dta['midr'].astype('int64')
tax_dta['s006'] = np.arange(0, len(tax_dta['s006']))

irates = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024}


@pytest.yield_fixture
def paramsfile():

    txt = """{"_almdep": {"value": [7150, 7250, 7400]},
             "_almsep": {"value": [40400, 41050]},
             "_rt5": {"value": [0.33 ]},
             "_rt7": {"value": [0.396]}}"""

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(txt + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])


def run(puf=True):

    # Create a Parameters object

    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    # Create a Calculator
    calc = Calculator(params=params, records=puf)
    totaldf = calc.calc_all_test()
    
    # drop duplicates
    totaldf = totaldf.T.groupby(level=0).first().T

    exp_results = pd.read_csv(os.path.join(CUR_PATH,
                                           "../../exp_results.csv.gz"),
                              compression='gzip')
    # Fix-up to bad column name in expected data
    exp_set = set(exp_results.columns)
    cur_set = set(totaldf.columns)

    assert(exp_set == cur_set)

    for label in exp_results.columns:
        lhs = exp_results[label].values.reshape(len(exp_results))
        rhs = totaldf[label].values.reshape(len(exp_results))
        res = np.allclose(lhs, rhs, atol=1e-02)
        if not res:
            print('Problem found in: ', label)


def test_sequence():
    run()


# Create a basic Records object using Public Use File
puf = Records(tax_dta)


def test_make_Calculator():
    # Create a Params object
    params = Parameters(start_year=1991, inflation_rates=irates)
    calc = Calculator(params, puf)


def test_make_Calculator_deepcopy():
    import copy
    # Create a Params object
    params = Parameters(start_year=1991, inflation_rates=irates)
    calc = Calculator(params, puf)
    calc2 = copy.deepcopy(calc)


def test_make_Calculator_from_files(paramsfile):
    calc = Calculator.from_files(paramsfile.name, tax_dta_path,
                                 start_year=1991,
                                 inflation_rates=irates)
    assert calc


def test_make_Calculator_files_to_ctor(paramsfile):
    calc = Calculator(params=paramsfile.name, records=tax_dta_path,
                      start_year=1991, inflation_rates=irates)
    assert calc


def test_make_Calculator_mods():

    # Create a Params object
    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    calc2 = calculator(params, puf, _II_em=np.array([4000]), _II_em_cpi=False)
    assert all(calc2.params._II_em == np.array([4000]))


def test_make_Calculator_json():

    # Create a Params object
    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    user_mods = """{"1991": { "_STD_Aged": [[1500, 1250, 1200, 1500, 1500, 1200 ]],
                     "_STD_Aged_cpi": false}}"""

    calc2 = calculator(params, puf, mods=user_mods, _II_em_cpi=False,
                       _II_em=np.array([4000]))
    assert calc2.params.II_em == 4000
    assert_array_equal(calc2.params._II_em, np.array([4000] * 12))
    exp_STD_Aged = [[1500, 1250, 1200, 1500, 1500, 1200]] * 12
    assert_array_equal(calc2.params._STD_Aged, np.array(exp_STD_Aged))
    assert_array_equal(calc2.params.STD_Aged, np.array([1500, 1250, 1200, 1500,
                                                        1500, 1200]))


def test_make_Calculator_user_mods_as_dict():

    # Create a Params object
    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    user_mods = {1991: {"_STD_Aged": [[1400, 1200]]}}
    user_mods[1991]['_II_em'] = [3925, 4000, 4100]
    user_mods[1991]['_II_em_cpi'] = False
    calc2 = calculator(params, puf, mods=user_mods)
    assert calc2.params.II_em == 3925
    exp_II_em = [3925, 4000] + [4100] * 10
    assert_array_equal(calc2.params._II_em, np.array(exp_II_em))
    assert_array_equal(calc2.params.STD_Aged, np.array([1400, 1200]))


def test_make_Calculator_increment_years_first():
    irates = {2008: 0.021, 2009: 0.022, 2010: 0.021,
              2011: 0.022}

    # create a Params object
    params = Parameters(start_year=2008, inflation_rates=irates,
                        budget_years=len(irates))
    # Create a Public Use File object

    tax_dta2 = pd.read_csv(tax_dta_path, compression='gzip')
    puf = Records(tax_dta2, start_year=2008)
    # specify reform in user_mods dictionary
    user_mods = {2010: {"_STD_Aged": [[1501, 1202, 1502, 1203, 1504, 1204]]}}
    user_mods[2010]['_II_em'] = [5000, 6000]
    user_mods[2010]['_II_em_cpi'] = False

    # create Calculator object with params as modified by user_mods
    calc = calculator(params, puf, mods=user_mods)

    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                            [1550, 1200, 1200, 1550, 1550, 1200],
                            [1501, 1202, 1502, 1203, 1504, 1204],
                            [1532, 1227, 1533, 1228, 1535, 1229]])
    exp_cur_STD_Aged = np.array([1501, 1202, 1502, 1203, 1504, 1204])

    exp_II_em = np.array([3900, 3950, 5000, 6000])
    exp_cur_II_em = 5000

    assert_array_equal(calc.params._STD_Aged, exp_STD_Aged)
    assert_array_equal(calc.params._II_em, exp_II_em)
    assert_array_equal(calc.params.STD_Aged, exp_cur_STD_Aged)
    assert_array_equal(calc.params.II_em, exp_cur_II_em)


def test_make_Calculator_user_mods_with_cpi_flags(paramsfile):

    calc = Calculator(params=paramsfile.name,
                      records=tax_dta_path, start_year=1991,
                      inflation_rates=irates)

    user_mods = {1991: {"_almdep": [7150, 7250, 7400],
                        "_almdep_cpi": True,
                        "_almsep": [40400, 41050],
                        "_almsep_cpi": False,
                        "_rt5": [0.33],
                        "_rt7": [0.396]}}

    inf_rates = [irates[1991 + i] for i in range(0, 12)]
    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)
    calc2 = calculator(params, puf, mods=user_mods)

    exp_almdep = expand_array(np.array([7150, 7250, 7400]), inflate=True,
                              inflation_rates=inf_rates, num_years=12)

    exp_almsep_values = [40400] + [41050] * 11
    exp_almsep = np.array(exp_almsep_values)

    assert_array_equal(calc2.params._almdep, exp_almdep)
    assert_array_equal(calc2.params._almsep, exp_almsep)


def test_make_Calculator_empty_params_is_default_params():
    # Create a Public Use File object
    puf_basic = Records(tax_dta, start_year=2013)
    calc_basic = Calculator(records=puf_basic)
    assert calc_basic


def test_Calculator_attr_access_to_params():

    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    # Create a Calculator
    calc = Calculator(params=params, records=puf)

    # Records data
    assert hasattr(calc.records, 'c01000')
    # Parameter data
    assert hasattr(calc.params, '_AMT_Child_em')
    # local attribute
    assert hasattr(calc, 'params')


def test_Calculator_create_distribution_table():

    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)
    # Create a Public Use File object
    puf = Records(tax_dta)
    # Create a Calculator
    calc = Calculator(params=params, records=puf)
    calc.calc_all()

    DIST_LABELS = ['Returns', 'AGI', 'Standard Deduction Filers',
                   'Standard Deduction', 'Itemizers',
                   'Itemized Deduction', 'Personal Exemption',
                   'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers',
                   'AMT', 'Tax before Credits', 'Non-refundable Credits',
                   'Tax before Refundable Credits', 'Refundable Credits',
                   'Revenue']
    t1 = create_distribution_table(calc, groupby="weighted_deciles",
                                   result_type="weighted_sum")
    t1.columns = DIST_LABELS
    t2 = create_distribution_table(calc, groupby="small_income_bins",
                                   result_type="weighted_avg")
    assert type(t1) == DataFrame
    assert type(t2) == DataFrame


def test_Calculator_create_difference_table():

    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)
    # Create a Public Use File object
    puf = Records(tax_dta)
    # Create a Calculator
    calc = Calculator(params=params, records=puf)
    calc.calc_all()

    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)
    # Create a Public Use File object
    puf = Records(tax_dta)
    user_mods = '{"1991": { "_rt7": [0.45] }}'
    calc2 = calculator(params, puf, mods=user_mods)

    t1 = create_difference_table(calc, calc2, groupby="weighted_deciles")
    assert type(t1) == DataFrame


def test_diagnostic_table():
    # we need the records' year at 2008 for blow up step.
    # So param's year needs to be 2008 to past the test
    irates = {2008: 0.015, 2009: 0.020, 2010: 0.022, 2011: 0.020, 2012: 0.021,
              2013: 0.022, 2014: 0.023, 2015: 0.024, 2016: 0.024, 2017: 0.024,
              2018: 0.024, 2019: 0.024}

    # Create a Parameters object
    params = Parameters(start_year=2008, inflation_rates=irates)
    # Create a Public Use File object
    tax_dta.flpdyr += 17
    puf = Records(tax_dta, weights=weights)
    # Create a Calculator

    calc = Calculator(params=params, records=puf, sync_years=False)

    calc.diagnostic_table()


class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
