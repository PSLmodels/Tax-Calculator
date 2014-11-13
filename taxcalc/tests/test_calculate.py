import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
import networkx as nx
from numba import jit, vectorize, guvectorize
from taxcalc import *


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

    assert(exp_set == cur_set)

    json_file_path = os.path.join(cur_path, 'variable_graph.json')
    checker = TaxCalcErrorChecker(exp_results, totaldf, json_file_path)

    for label in exp_results.columns:
        if label in checker:
            checker.check_for_errors(label)
        else:
            lhs = exp_results[label].values.reshape(len(exp_results))
            rhs = totaldf[label].values.reshape(len(exp_results))
            res = np.allclose(lhs, rhs, atol=1e-02)
            if not res:
                print('Problem found in: ', label)
                # raise TaxCalcError('Problem found in var:{}'.format(label))
                raise

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



class TaxCalcMismatchError(Exception):

    def __init__(self, variable_label):
        self.var_label = variable_label
        self.ancest = ancestors
        self.descend = descendants
        self.message = (
            'Mismatch from gold standard in {0}\n'
            'The following variables might have caused it:\n{1}\n'
            'The following variables may be affected by it:\n{2}\n'
            )

    def __str__(self):
        return self.message.format(self.var_label, self.ancest, self.descend)


class TaxCalcErrorChecker(object):
    """Class used for checking labels for errors with use of a directed graph.
    TODO: set np.allclose as local."""

    def __init__(self, exp_results, totaldf, graph_file):
        # set up the DFs for comparison
        self.gold_std = exp_results
        self.reshape_len = len(exp_results)
        self.new_results = totaldf

        # read in network graph
        from networkx.readwrite import json_graph
        import json
        json_data = json.load(open(graph_file))
        self.Graph = json_graph.node_link_graph(json_data)

        # set up related node lookup functions
        self.ancestors = self.look_up_relatives(nx.ancestors)
        self.descendants = self.look_up_relatives(nx.descendants)

    def __contains__(self, label):
        return self.Graph.has_node(label)

    def check_for_errors(self, label, tol=1e-02):
        '''Checks a particular label for errors against the setup used to
        initiate the class.
        Naturally expects some label as argument. Optionally accepts custom
        tolerance cutoff value.
        '''
        if not self.check_match(label, tol):
            ancestors = self.ancestors(label, True, tol=tol)
            descendants = self.descendants(label, True, tol=tol)
            raise TaxCalcMismatchError(label, ancestors, descendants)

    def check_match(self, label, tol=1e-02):
        '''Function checks if values for a label in the gold standard
        match those in a new set of results within the tolerance threshold
        set by tol.
        '''
        lhs = self.gold_std[label].values.reshape(self.reshape_len)
        rhs = self.new_results[label].values.reshape(self.reshape_len)
        return np.allclose(lhs, rhs, atol=tol)

    def look_up_relatives(self, method):
        '''This function simply sets up a way to lookup relatives of a node
        in a graph.
        It currrently accepts any valid networkx tree traversal method
        such as networkx.ancestors or networkx.descendants
        '''

        def lookup_inner(label, original=False, tol=1e-02):
            '''This function actually does the work of recursively searching
            the graph and building a list of related nodes.
            '''
            if original:
                relatives = []
                match = False
            else:
                match = self.check_match(label, tol)
                if match:
                    return []
                else:
                    relatives = [match]

            if not match:
                for rel_lbl in method(self.Graph, label):
                    relatives += self.lookup_inner(rel_lbl, tol=tol)

            return relatives

        return lookup_inner
