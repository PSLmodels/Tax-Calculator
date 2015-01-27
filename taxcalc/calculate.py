import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *
from .functions import *


all_cols = set()
def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])


def calculator(parameters, puf, mods="", **kwargs):
    if mods:
        import json
        dd = json.loads(mods)
        dd = {k:np.array(v) for k,v in dd.items() if type(v) == list}
        kwargs.update(dd)

    calc = Calculator(parameters, puf)
    if kwargs:
        calc.__dict__.update(kwargs)
    return calc

class Calculator(object):

    def __init__(self, parameters, puf):
        self.parameters = parameters
        self.puf = puf
        assert puf.current_year == parameters.current_year

    def __getattr__(self, val):

        if val in self.__dict__:
            return self.__dict__[val]
        else:
            try:
                return getattr(self.parameters, val)
            except AttributeError:
                try:
                    return getattr(self.puf, val)
                except AttributeError:
                    raise


    def calc_all(self):
        FilingStatus(self.parameters, self.puf)
        Adj(self.parameters, self.puf)
        CapGains(self.parameters, self.puf)
        SSBenefits(self.parameters, self.puf)
        AGI(self.parameters, self.puf)
        ItemDed(self.parameters, self.puf)
        EI_FICA(self.parameters, self.puf)
        StdDed(self.parameters, self.puf)
        XYZD(self.parameters, self.puf)
        NonGain(self.parameters, self.puf)
        TaxGains(self.parameters, self.puf)
        MUI(self.parameters, self.puf)
        AMTI(self.parameters, self.puf)
        F2441(self.parameters, self.puf)
        DepCareBen(self.parameters, self.puf)
        ExpEarnedInc(self.parameters, self.puf)
        RateRed(self.parameters, self.puf)
        NumDep(self.parameters, self.puf)
        ChildTaxCredit(self.parameters, self.puf)
        AmOppCr(self.parameters, self.puf)
        LLC(self.parameters, self.puf)
        RefAmOpp(self.parameters, self.puf)
        NonEdCr(self.parameters, self.puf)
        AddCTC(self.parameters, self.puf)
        F5405(self.parameters, self.puf)
        C1040(self.parameters, self.puf)
        DEITC(self.parameters, self.puf)
        SOIT(self.parameters, self.puf)

    def calc_all_test(self):
        all_dfs = []
        add_df(all_dfs, FilingStatus(self.parameters, self.puf))
        add_df(all_dfs, Adj(self.parameters, self.puf))
        add_df(all_dfs, CapGains(self.parameters, self.puf))
        add_df(all_dfs, SSBenefits(self.parameters, self.puf))
        add_df(all_dfs, AGI(self.parameters, self.puf))
        add_df(all_dfs, ItemDed(self.parameters, self.puf))
        add_df(all_dfs, EI_FICA(self.parameters, self.puf))
        add_df(all_dfs, StdDed(self.parameters, self.puf))
        add_df(all_dfs, XYZD(self.parameters, self.puf))
        add_df(all_dfs, NonGain(self.parameters, self.puf))
        add_df(all_dfs, TaxGains(self.parameters, self.puf))
        add_df(all_dfs, MUI(self.parameters, self.puf))
        add_df(all_dfs, AMTI(self.parameters, self.puf))
        add_df(all_dfs, F2441(self.parameters, self.puf))
        add_df(all_dfs, DepCareBen(self.parameters, self.puf))
        add_df(all_dfs, ExpEarnedInc(self.parameters, self.puf))
        add_df(all_dfs, RateRed(self.parameters, self.puf))
        add_df(all_dfs, NumDep(self.parameters, self.puf))
        add_df(all_dfs, ChildTaxCredit(self.parameters, self.puf))
        add_df(all_dfs, AmOppCr(self.parameters, self.puf))
        add_df(all_dfs, LLC(self.parameters, self.puf))
        add_df(all_dfs, RefAmOpp(self.parameters, self.puf))
        add_df(all_dfs, NonEdCr(self.parameters, self.puf))
        add_df(all_dfs, AddCTC(self.parameters, self.puf))
        add_df(all_dfs, F5405(self.parameters, self.puf))
        add_df(all_dfs, C1040(self.parameters, self.puf))
        add_df(all_dfs, DEITC(self.parameters, self.puf))
        add_df(all_dfs, SOIT(self.parameters, self.puf))
        totaldf = pd.concat(all_dfs, axis=1)
        return totaldf

    def increment_year(self):
        self.puf.increment_year()
        self.parameters.increment_year()

    @property
    def current_year(self):
        return self.parameters.current_year
