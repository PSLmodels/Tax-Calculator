import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
import pandas as pd
from numba import jit, vectorize, guvectorize
from taxcalc import *


all_cols = set()
tax_dta = pd.read_csv(os.path.join(CUR_PATH, "../../tax_all91_puf.gz"),
                      compression='gzip')
# Fix-up. MIdR needs to be type int64 to match PUF
tax_dta['midr'] = tax_dta['midr'].astype('int64')


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


class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
