import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
import pandas as pd
from numba import jit, vectorize, guvectorize
from taxcalc import *


all_cols = set()
tax_dta = pd.read_csv(os.path.join(CUR_PATH, "../../tax_all91_puf.gz"), compression='gzip')
#Fix-up. MIdR needs to be type int64 to match PUF 
tax_dta['midr'] = tax_dta['midr'].astype('int64')

def add_df(alldfs, df):
    try:
        for col in df.columns:
            if col not in all_cols:
                all_cols.add(col)
                alldfs.append(df[col])
    except AttributeError:
        import pdb
        pdb.set_trace()
        pass

def run(puf=True):
    calc = Calculator(tax_dta, default_year=91)
    set_input_data(calc)
    update_globals_from_calculator(calc)
    update_calculator_from_module(calc, parameters)

    all_dfs = []
    add_df(all_dfs, FilingStatus(calc))
    add_df(all_dfs, Adj())
    add_df(all_dfs, CapGains(calc))
    add_df(all_dfs, SSBenefits(calc))
    add_df(all_dfs, AGI(calc))
    add_df(all_dfs, ItemDed(puf, calc))
    df_EI_FICA, _earned = EI_FICA(calc)
    add_df(all_dfs, df_EI_FICA)
    add_df(all_dfs, StdDed(calc))
    add_df(all_dfs, XYZD(calc))
    add_df(all_dfs, NonGain())
    df_Tax_Gains, c05750 = TaxGains(calc)
    add_df(all_dfs, df_Tax_Gains)
    add_df(all_dfs, MUI(c05750, calc))
    df_AMTI, c05800 = AMTI(puf, calc)
    add_df(all_dfs, df_AMTI)

    # df_F2441, c32800 = F2441(puf, _earned, calc)
    # add_df(all_dfs, df_F2441)
    # add_df(all_dfs, DepCareBen(c32800, calc))

    add_df(all_dfs, F2441(puf, calc))
    add_df(all_dfs, DepCareBen(calc))

    add_df(all_dfs, ExpEarnedInc(calc))
    add_df(all_dfs, RateRed(c05800, calc))
    add_df(all_dfs, NumDep(puf, calc))
    add_df(all_dfs, ChildTaxCredit(calc))
    add_df(all_dfs, AmOppCr(calc))
    df_LLC, c87550 = LLC(puf, calc)
    add_df(all_dfs, df_LLC)
    add_df(all_dfs, RefAmOpp(calc))
    add_df(all_dfs, NonEdCr(c87550, calc))
    add_df(all_dfs, AddCTC(puf, calc))
    add_df(all_dfs, F5405())
    df_C1040, _eitc = C1040(puf, calc)
    add_df(all_dfs, df_C1040)
    add_df(all_dfs, DEITC(calc))
    add_df(all_dfs, SOIT(_eitc, calc))
    totaldf = pd.concat(all_dfs, axis=1)
    #drop duplicates
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
    calc = Calculator(tax_dta)


def test_make_Calculator_mods():
    calc1 = calculator(tax_dta)
    calc2 = calculator(tax_dta, _amex=np.array([4000]))
    update_calculator_from_module(calc2, parameters)
    update_globals_from_calculator(calc2)
    assert all(calc2._amex == np.array([4000]))


def test_make_Calculator_json():
    user_mods = '{ "_aged": [[1500], [1200]] }'
    calc2 = calculator(tax_dta, mods=user_mods, _amex=np.array([4000]))
    update_calculator_from_module(calc2, parameters)
    update_globals_from_calculator(calc2)
    assert all(calc2._amex == np.array([4000]))
    assert all(calc2._aged == np.array([[1500], [1200]]))



class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
