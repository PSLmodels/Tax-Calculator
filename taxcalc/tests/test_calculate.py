import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
from numba import jit, vectorize, guvectorize
from taxcalc import *


all_cols = set()
tax_dta = pd.read_csv(os.path.join(CUR_PATH, "../../tax_all91_puf.gz"),
                      compression='gzip')
# Fix-up. MIdR needs to be type int64 to match PUF
tax_dta['midr'] = tax_dta['midr'].astype('int64')
tax_dta['s006'] = np.arange(0,len(tax_dta['s006']))


def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])


def run(puf=True):

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)
    totaldf = calc.calc_all_test()

    # drop duplicates
    totaldf = totaldf.T.groupby(level=0).first().T

    exp_results = pd.read_csv(os.path.join(CUR_PATH, "../../exp_results.csv.gz"), compression='gzip')
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


def test_make_Calculator():
    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    calc = Calculator(params, puf)


def test_make_Calculator_mods():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    calc2 = calculator(params, puf, _amex=np.array([4000]))
    assert all(calc2._amex == np.array([4000]))


def test_make_Calculator_json():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    user_mods = '{ "_aged": [[1500], [1200]] }'
    calc2 = calculator(params, puf, mods=user_mods, _amex=np.array([4000]))
    assert all(calc2._amex == np.array([4000]))
    assert all(calc2._aged == np.array([[1500], [1200]]))
    assert all(calc2.aged == np.array([1500]))


def test_make_Parameters_credit_udfs():


    user_mods = '{ "credit_udf_0": [[100], [200], [300]] }'
    params = parameters(mods=user_mods)
    #calc2 = calculator(params, puf, mods=user_mods, _amex=np.array([4000]))
    assert all(params.udf_credit0 == np.array([100]))
    assert all(params.udf_credit1 == np.array([200]))
    assert all(params.udf_credit2 == np.array([300]))


def test_make_Parameters_credit_udfs_and_run():
    user_mods = '{ "credit_udf_0": [[100], [200], [300]] }'
    params = parameters(mods=user_mods, start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)
    totaldf = calc.calc_all()


def test_Calculator_attr_access_to_params():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = PUF(tax_dta)

    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)

    # PUF data
    assert hasattr(calc, 'c01000')
    # Parameter data
    assert hasattr(calc, '_almdep')
    # local attribute
    assert hasattr(calc, 'parameters')


def test_Calculator_set_attr_passes_through():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = PUF(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)

    assert id(calc.e00200) == id(calc.puf.e00200)
    calc.e00200 = calc.e00200 + 100
    assert id(calc.e00200) == id(calc.puf.e00200)
    assert_array_equal( calc.e00200, calc.puf.e00200)

    with pytest.raises(AttributeError):
        calc.foo == 14


def test_Calculator_create_distribution_table():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = PUF(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)
    calc.calc_all()

    t1 = create_distribution_table(calc, groupby="weighted_deciles")
    t2 = create_distribution_table(calc, groupby="agi_bins")
    assert type(t1) == DataFrame
    assert type(t2) == DataFrame

def test_Calculator_create_difference_table():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = PUF(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, puf=puf)
    calc.calc_all()

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = PUF(tax_dta)
    user_mods = '{ "_rt7": [0.45] }'
    calc2 = calculator(params, puf, mods=user_mods)

    t1 = create_difference_table(calc, calc2, groupby="weighted_deciles")
    t2 = create_difference_table(calc, calc2, groupby="agi_bins")
    assert type(t1) == DataFrame
    assert type(t2) == DataFrame



class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
