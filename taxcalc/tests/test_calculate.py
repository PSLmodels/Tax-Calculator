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


all_cols = set()
tax_dta_path = os.path.join(CUR_PATH, "../../tax_all91_puf.gz")
tax_dta = pd.read_csv(tax_dta_path, compression='gzip')
                      
# Fix-up. MIdR needs to be type int64 to match PUF
tax_dta['midr'] = tax_dta['midr'].astype('int64')
tax_dta['s006'] = np.arange(0,len(tax_dta['s006']))


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
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = Records(tax_dta)

    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)
    totaldf = calc.calc_all_test()

    # drop duplicates
    totaldf = totaldf.T.groupby(level=0).first().T

    exp_results = pd.read_csv(os.path.join(CUR_PATH, "../../exp_results.csv.gz"), compression='gzip')
    # Fix-up to bad column name in expected data
    exp_results.rename(columns=lambda x: x.replace('_phase2', '_phase2_i'), inplace=True)
    exp_set = set(exp_results.columns)
    # Add new col names to exp_set
    exp_set.add('_ospctax')
    exp_set.add('_refund')
    exp_set.add('_othertax')
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
    puf = Records(tax_dta)

    calc = Calculator(params, puf)


def test_make_Calculator_from_files(paramsfile):
    calc = Calculator.from_files(paramsfile.name, tax_dta_path, start_year=91)
    assert calc


def test_make_Calculator_files_to_ctor(paramsfile):
    calc = Calculator(parameters=paramsfile.name, records=tax_dta_path, start_year=91)
    assert calc


def test_make_Calculator_mods():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = Records(tax_dta)

    calc2 = calculator(params, puf, _amex=np.array([4000]))
    assert all(calc2._amex == np.array([4000]))


def test_make_Calculator_json():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = Records(tax_dta)

    user_mods = '{ "_aged": [[1500], [1200]] }'
    calc2 = calculator(params, puf, mods=user_mods, _amex=np.array([4000]))
    assert all(calc2._amex == np.array([4000]))
    assert all(calc2._aged == np.array([[1500], [1200]]))
    assert all(calc2.aged == np.array([1500]))


def test_Calculator_attr_access_to_params():

    # Create a Parameters object
    params = Parameters(start_year=91)

    # Create a Public Use File object
    puf = Records(tax_dta)

    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)

    # Records data
    assert hasattr(calc, 'c01000')
    # Parameter data
    assert hasattr(calc, '_AMT_Child_em')
    # local attribute
    assert hasattr(calc, 'parameters')


def test_Calculator_set_attr_passes_through():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = Records(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)

    assert id(calc.e00200) == id(calc.records.e00200)
    calc.e00200 = calc.e00200 + 100
    assert id(calc.e00200) == id(calc.records.e00200)
    assert_array_equal( calc.e00200, calc.records.e00200)

    with pytest.raises(AttributeError):
        calc.foo == 14


def test_Calculator_create_distribution_table():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = Records(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)
    calc.calc_all()

    t1 = create_distribution_table(calc, groupby="weighted_deciles")
    t2 = create_distribution_table(calc, groupby="agi_bins")
    assert type(t1) == DataFrame
    assert type(t2) == DataFrame

def test_Calculator_create_difference_table():

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = Records(tax_dta)
    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)
    calc.calc_all()

    # Create a Parameters object
    params = Parameters(start_year=91)
    # Create a Public Use File object
    puf = Records(tax_dta)
    user_mods = '{ "_rt7": [0.45] }'
    calc2 = calculator(params, puf, mods=user_mods)

    t1 = create_difference_table(calc, calc2, groupby="weighted_deciles")
    assert type(t1) == DataFrame



class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
