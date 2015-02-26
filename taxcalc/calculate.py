import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *
from .functions import *
from .parameters import Parameters
from .records import Records


all_cols = set()
def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])


def calculator(parameters, records, mods="", **kwargs):
    if mods:
        import json
        dd = json.loads(mods)
        dd = {k:np.array(v) for k,v in dd.items() if type(v) == list}
        kwargs.update(dd)

    calc = Calculator(parameters, records)
    if kwargs:
        calc.__dict__.update(kwargs)
        for name, vals in kwargs.items():
            if name.startswith("_"):
                arr = getattr(calc, name)
                setattr(calc, name[1:], arr[0])
    return calc

class Calculator(object):

    @classmethod
    def from_files(cls, pfname, rfname, **kwargs):
        """
        Create a Calculator object from a Parameters JSON file and a
        Records file

        Parameters
        ----------
        pfname: filename for Parameters

        rfname: filename for Records
        """
        params = Parameters.from_file(pfname, **kwargs)
        recs = Records.from_file(rfname, **kwargs)
        return cls(params, recs)


    def __init__(self, parameters, records, **kwargs):
        self._parameters = (parameters if not isinstance(parameters, str) else
                            Parameters.from_file(parameters, **kwargs))

        self._records = (records if not isinstance(records, str) else
                         Records.from_file(records, **kwargs))

        while self._records.current_year < self._parameters.current_year:
            self._records.increment_year()

        assert self._parameters.current_year == self._records.current_year

    @property
    def parameters(self):
        return self._parameters

    @property
    def records(self):
        return self._records

    def __getattr__(self, name):
        """
        Only allowed attributes on a Calculator are 'parameters' and 'records'
        """

        if hasattr(self.parameters, name):
            return getattr(self.parameters, name)
        elif hasattr(self.records, name):
            return getattr(self.records, name)
        else:
            try:
                self.__dict__[name]
            except KeyError:
                raise AttributeError(name + " not found")

    def __setattr__(self, name, val):
        """
        Only allowed attributes on a Calculator are 'parameters' and 'records'
        """

        if name == "_parameters" or name == "_records":
            self.__dict__[name] = val
            return

        if hasattr(self.parameters, name):
            return setattr(self.parameters, name, val)
        elif hasattr(self.records, name):
            return setattr(self.records, name, val)
        else:
            self.__dict__[name] = val

    def __getitem__(self, val):

        if val in self.__dict__:
            return self.__dict__[val]
        else:
            try:
                return getattr(self.parameters, val)
            except AttributeError:
                try:
                    return getattr(self.records, val)
                except AttributeError:
                    raise




    def calc_all(self):
        FilingStatus(self.parameters, self.records)
        Adj(self.parameters, self.records)
        CapGains(self.parameters, self.records)
        SSBenefits(self.parameters, self.records)
        AGI(self.parameters, self.records)
        ItemDed(self.parameters, self.records)
        EI_FICA(self.parameters, self.records)
        StdDed(self.parameters, self.records)
        XYZD(self.parameters, self.records)
        NonGain(self.parameters, self.records)
        TaxGains(self.parameters, self.records)
        MUI(self.parameters, self.records)
        AMTI(self.parameters, self.records)
        F2441(self.parameters, self.records)
        DepCareBen(self.parameters, self.records)
        ExpEarnedInc(self.parameters, self.records)
        RateRed(self.parameters, self.records)
        NumDep(self.parameters, self.records)
        ChildTaxCredit(self.parameters, self.records)
        AmOppCr(self.parameters, self.records)
        LLC(self.parameters, self.records)
        RefAmOpp(self.parameters, self.records)
        NonEdCr(self.parameters, self.records)
        AddCTC(self.parameters, self.records)
        F5405(self.parameters, self.records)
        C1040(self.parameters, self.records)
        DEITC(self.parameters, self.records)
        OSPC_TAX(self.parameters, self.records)

    def calc_all_test(self):
        all_dfs = []
        add_df(all_dfs, FilingStatus(self.parameters, self.records))
        add_df(all_dfs, Adj(self.parameters, self.records))
        add_df(all_dfs, CapGains(self.parameters, self.records))
        add_df(all_dfs, SSBenefits(self.parameters, self.records))
        add_df(all_dfs, AGI(self.parameters, self.records))
        add_df(all_dfs, ItemDed(self.parameters, self.records))
        add_df(all_dfs, EI_FICA(self.parameters, self.records))
        add_df(all_dfs, StdDed(self.parameters, self.records))
        add_df(all_dfs, XYZD(self.parameters, self.records))
        add_df(all_dfs, NonGain(self.parameters, self.records))
        add_df(all_dfs, TaxGains(self.parameters, self.records))
        add_df(all_dfs, MUI(self.parameters, self.records))
        add_df(all_dfs, AMTI(self.parameters, self.records))
        add_df(all_dfs, F2441(self.parameters, self.records))
        add_df(all_dfs, DepCareBen(self.parameters, self.records))
        add_df(all_dfs, ExpEarnedInc(self.parameters, self.records))
        add_df(all_dfs, RateRed(self.parameters, self.records))
        add_df(all_dfs, NumDep(self.parameters, self.records))
        add_df(all_dfs, ChildTaxCredit(self.parameters, self.records))
        add_df(all_dfs, AmOppCr(self.parameters, self.records))
        add_df(all_dfs, LLC(self.parameters, self.records))
        add_df(all_dfs, RefAmOpp(self.parameters, self.records))
        add_df(all_dfs, NonEdCr(self.parameters, self.records))
        add_df(all_dfs, AddCTC(self.parameters, self.records))
        add_df(all_dfs, F5405(self.parameters, self.records))
        add_df(all_dfs, C1040(self.parameters, self.records))
        add_df(all_dfs, DEITC(self.parameters, self.records))
        add_df(all_dfs, OSPC_TAX(self.parameters, self.records))
        totaldf = pd.concat(all_dfs, axis=1)
        return totaldf

    def increment_year(self):
        self.records.increment_year()
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
        taxes_base = np.copy(self._ospctax)

        # Calculate the tax change with a marginal increase in income.
        setattr(self, income_type_string, income_type + diff)
        self.calc_all()
        delta_taxes_up = self._ospctax - taxes_base

        # Calculate the tax change with a marginal decrease in income.
        setattr(self, income_type_string, income_type - diff)
        self.calc_all()
        delta_taxes_down = taxes_base - self._ospctax

        # Reset the income_type to its starting point to avoid 
        # unintended consequences. 
        setattr(self, income_type_string, income_type)
        self.calc_all()

        # Choose the more modest effect of either adding or subtracting income.
        delta_taxes = np.where( np.absolute(delta_taxes_up) <= 
                            np.absolute(delta_taxes_down), 
                            delta_taxes_up , delta_taxes_down)

        # Calculate the marginal tax rate
        mtr = delta_taxes / diff

        return mtr

