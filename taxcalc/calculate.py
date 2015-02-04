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
        for name, vals in kwargs.items():
            if name.startswith("_"):
                arr = getattr(calc, name)
                setattr(calc, name[1:], arr[0])

    return calc

class Calculator(object):

    def __init__(self, parameters, puf):
        self._parameters = parameters
        self._puf = puf
        assert puf.current_year == parameters.current_year

    @property
    def parameters(self):
        return self._parameters

    @property
    def puf(self):
        return self._puf

    def __getattr__(self, name):
        """
        Only allowed attributes on a Calculator are 'parameters' and 'puf'
        """

        if hasattr(self.parameters, name):
            return getattr(self.parameters, name)
        elif hasattr(self.puf, name):
            return getattr(self.puf, name)
        else:
            raise AttributeError(name + " not found")

    def __setattr__(self, name, val):
        """
        Only allowed attributes on a Calculator are 'parameters' and 'puf'
        """

        if name == "_parameters" or name == "_puf":
            self.__dict__[name] = val
            return

        if hasattr(self.parameters, name):
            return setattr(self.parameters, name, val)
        elif hasattr(self.puf, name):
            return setattr(self.puf, name, val)
        else:
            self.__setattr__(name, val)


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


    def mtr(self, income_type_string, diff = 100):
        """
        This method calculates the marginal tax rate for every record. 
        In order to avoid kinks, we find the marginal rates associated with 
        both a tax increase and a tax decrease and use the more modest of 
        the two. 
        """

        income_type = getattr(self, income_type_string)
        
        # Calculate the base level of taxes. 
        self.calc_all()
        taxes_base = np.copy(self.c05200)

        # Calculate the tax change with a marginal increase in income.
        setattr(self, income_type_string, income_type + diff)
        self.calc_all()
        delta_taxes_up = self.c05200 - taxes_base

        # Calculate the tax change with a marginal decrease in income.
        setattr(self, income_type_string, income_type - 2*diff)
        self.calc_all()
        delta_taxes_down = taxes_base - self.c05200

        # Reset the income_type to its starting point to avoid 
        # unintended consequences. 
        setattr(self, income_type_string, income_type + diff)

        # Choose the more modest effect of either adding or subtracting income.
        delta_taxes = np.where( np.absolute(delta_taxes_up) <= 
                            np.absolute(delta_taxes_down), 
                            delta_taxes_up , delta_taxes_down)

        # Calculate the marginal tax rate
        mtr = delta_taxes / diff

        return mtr

