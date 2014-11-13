import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
from numba import autojit, jit, vectorize, guvectorize
from taxcalc import *




ignore_list = []
# ['c82940', 'c82930', 'c82935', 'c82900', 'c82905', 'c82910', 'c82915', 
# 'c82920', 'c82937', '_othadd', 'c63100','c09600', 'c05800','c07100', 'y07100', 'x07100', 'c08795', 
# 'c08800', 'c09200', 'c07150', 'c33400', '_ctctax', 'c10300', 'c05750', 'c24580', 'c05100', '_taxbc']


all_cols = set()
tax_dta = pd.read_csv(os.path.join(cur_path, "../../tax_all91_puf.gz"), compression='gzip')

def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])

def run(puf=True):
    cur_path = os.path.abspath(os.path.dirname(__file__))
    calc = Calculator(tax_dta, default_year=91)
    set_input_data(calc)
    update_globals_from_calculator(calc)
    update_calculator_from_module(calc, constants)

    all_dfs = []
    add_df(all_dfs, FilingStatus())
    add_df(all_dfs, Adj())
    add_df(all_dfs, CapGains())
    add_df(all_dfs, SSBenefits())
    add_df(all_dfs, AGI())
    add_df(all_dfs, ItemDed(puf))
    df_EI_FICA, _earned = EI_FICA()
    add_df(all_dfs, df_EI_FICA)
    add_df(all_dfs, StdDed())
    add_df(all_dfs, XYZD())
    add_df(all_dfs, NonGain())
    df_Tax_Gains, c05750 = TaxGains()  
    add_df(all_dfs, df_Tax_Gains)
    add_df(all_dfs, MUI(c05750))
    df_AMTI, c05800 = AMTI(puf)
    add_df(all_dfs, df_AMTI)
    df_F2441, c32800 = F2441(puf, _earned)
    add_df(all_dfs, df_F2441)
    add_df(all_dfs, DepCareBen(c32800))
    add_df(all_dfs, ExpEarnedInc())
    add_df(all_dfs, RateRed(c05800))
    add_df(all_dfs, NumDep(puf))
    add_df(all_dfs, ChildTaxCredit())
    add_df(all_dfs, AmOppCr())
    df_LLC, c87550 = LLC(puf)
    add_df(all_dfs, df_LLC)
    add_df(all_dfs, RefAmOpp())
    add_df(all_dfs, NonEdCr(c87550))
    add_df(all_dfs, AddCTC(puf))
    add_df(all_dfs, F5405())
    df_C1040, _eitc = C1040(puf)
    add_df(all_dfs, df_C1040)
    add_df(all_dfs, DEITC())
    add_df(all_dfs, SOIT(_eitc))
    totaldf = pd.concat(all_dfs, axis=1)
    #drop duplicates
    totaldf = totaldf.T.groupby(level=0).first().T

    exp_results = pd.read_csv(os.path.join(cur_path, "../../exp_results.csv.gz"), compression='gzip')
    exp_set = set(exp_results.columns)
    cur_set = set(totaldf.columns)

    #assert(exp_set == cur_set)

    for label in totaldf.columns:
        if label not in exp_results.columns:
            print("this: ", label, " is not in the expected results!")

    for label in exp_results.columns:
        if label not in totaldf.columns:
            print(label, " was supposed to be in answer!")
        if label not in ignore_list:
            lhs = exp_results[label].values.reshape(len(exp_results))
            rhs = totaldf[label].values.reshape(len(exp_results))
            res = np.allclose(lhs, rhs, atol=1e-02)
            if not res:
                print(lhs)
                print(rhs)
                raise TaxCalcError('Problem found in var:{}'.format(label))

def test_sequence():
    run()

def test_make_Calculator():
    calc = Calculator(tax_dta)


def test_make_Calculator_mods():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    calc1 = calculator(tax_dta)
    calc2 = calculator(tax_dta, _amex=np.array([4000]))
    update_calculator_from_module(calc2, constants)
    update_globals_from_calculator(calc2)
    assert all(calc2._amex == np.array([4000]))

class TaxCalcError(Exception):

    def __init__(self, variable_label):
        self.var_label = variable_label

    def __str__(self):
        return "Problem found in variable: {}".format(self.var_label)

