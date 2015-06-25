import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *
from .functions import *
from .parameters import Parameters
from .records import Records
import copy

all_cols = set()
def add_df(alldfs, df):
    for col in df.columns:
        if col not in all_cols:
            all_cols.add(col)
            alldfs.append(df[col])
        else:
            dup_index = [i for i,
                         series in enumerate(alldfs) if series.name == col][0]
            alldfs[dup_index] = df[col]


def calculator(params, records, mods="", **kwargs):
    update_mods = {}
    if mods:
        if isinstance(mods, str):
            import json
            dd = json.loads(mods)
            dd = {int(k): (np.array(v) if type(v) == list else v)
                  for k, v in dd.items()}
            update_mods.update(dd)
        else:
            update_mods.update(mods)

    final_mods = toolz.merge_with(toolz.merge, update_mods,
                                  {params.current_year: kwargs})

    if not all(isinstance(yr, int) for yr in final_mods):
        raise ValueError("All keys in mods must be years")
    if final_mods:
        max_yr = max(yr for yr in final_mods)
    else:
        max_yr = 0
    if (params.current_year < max_yr):
        msg = ("Modifications are for year {0} and Parameters are for"
               " year {1}. Parameters will be advanced to year {0}")
        print(msg.format(max_yr, params.current_year))

    while params.current_year < max_yr:
        params.increment_year()

    if (records.current_year < max_yr):
        msg = ("Modifications are for year {0} and Records are for"
               " year {1}. Records will be advanced to year {0}")
        print(msg.format(max_yr, records.current_year))

    while records.current_year < max_yr:
        records.increment_year()

    params.update(final_mods)
    calc = Calculator(params, records)
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

    def __init__(self, params=None, records=None, sync_years=True, **kwargs):

        if isinstance(params, Parameters):
            self._params = params
        else:
            self._params = Parameters.from_file(params, **kwargs)

        if records is None:
            raise ValueError("Must supply tax records path or Records object")

        self._records = (records if not isinstance(records, str) else
                         Records.from_file(records, **kwargs))

        if sync_years and self._records.current_year == 2008:
            print("You loaded data for "+str(self._records.current_year)+'.')

            while self._records.current_year < self._params.current_year:
                self._records.increment_year()

            print("Your data have beeen extrapolated to "
                  + str(self._records.current_year) + ".")

        assert self._params.current_year == self._records.current_year

    @property
    def params(self):
        return self._params

    @property
    def records(self):
        return self._records

    def calc_all(self):
        FilingStatus(self.params, self.records)
        Adj(self.params, self.records)
        CapGains(self.params, self.records)
        SSBenefits(self.params, self.records)
        AGI(self.params, self.records)
        ItemDed(self.params, self.records)
        EI_FICA(self.params, self.records)
        AMED(self.params, self.records)
        StdDed(self.params, self.records)
        XYZD(self.params, self.records)
        NonGain(self.params, self.records)
        TaxGains(self.params, self.records)
        MUI(self.params, self.records)
        AMTI(self.params, self.records)
        F2441(self.params, self.records)
        DepCareBen(self.params, self.records)
        ExpEarnedInc(self.params, self.records)
        RateRed(self.params, self.records)
        NumDep(self.params, self.records)
        ChildTaxCredit(self.params, self.records)
        AmOppCr(self.params, self.records)
        LLC(self.params, self.records)
        RefAmOpp(self.params, self.records)
        NonEdCr(self.params, self.records)
        AddCTC(self.params, self.records)
        F5405(self.params, self.records)
        C1040(self.params, self.records)
        DEITC(self.params, self.records)
        OSPC_TAX(self.params, self.records)
        ExpandIncome(self.params, self.records)

    def calc_all_test(self):
        all_dfs = []
        add_df(all_dfs, FilingStatus(self.params, self.records))
        add_df(all_dfs, Adj(self.params, self.records))
        add_df(all_dfs, CapGains(self.params, self.records))
        add_df(all_dfs, SSBenefits(self.params, self.records))
        add_df(all_dfs, AGI(self.params, self.records))
        add_df(all_dfs, ItemDed(self.params, self.records))
        add_df(all_dfs, EI_FICA(self.params, self.records))
        add_df(all_dfs, AMED(self.params, self.records))
        add_df(all_dfs, StdDed(self.params, self.records))
        add_df(all_dfs, XYZD(self.params, self.records))
        add_df(all_dfs, NonGain(self.params, self.records))
        add_df(all_dfs, TaxGains(self.params, self.records))
        add_df(all_dfs, MUI(self.params, self.records))
        add_df(all_dfs, AMTI(self.params, self.records))
        add_df(all_dfs, F2441(self.params, self.records))
        add_df(all_dfs, DepCareBen(self.params, self.records))
        add_df(all_dfs, ExpEarnedInc(self.params, self.records))
        add_df(all_dfs, RateRed(self.params, self.records))
        add_df(all_dfs, NumDep(self.params, self.records))
        add_df(all_dfs, ChildTaxCredit(self.params, self.records))
        add_df(all_dfs, AmOppCr(self.params, self.records))
        add_df(all_dfs, LLC(self.params, self.records))
        add_df(all_dfs, RefAmOpp(self.params, self.records))
        add_df(all_dfs, NonEdCr(self.params, self.records))
        add_df(all_dfs, AddCTC(self.params, self.records))
        add_df(all_dfs, F5405(self.params, self.records))
        add_df(all_dfs, C1040(self.params, self.records))
        add_df(all_dfs, DEITC(self.params, self.records))
        add_df(all_dfs, OSPC_TAX(self.params, self.records))
        add_df(all_dfs, ExpandIncome(self.params, self.records))
        totaldf = pd.concat(all_dfs, axis=1)
        return totaldf

    def increment_year(self):
        self.records.increment_year()
        self.params.increment_year()

    @property
    def current_year(self):
        return self.params.current_year

    def mtr(self, income_type_string, diff=100):
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

        # Choose the more modest effect of either adding or subtracting income
        delta_taxes = np.where(np.absolute(delta_taxes_up) <=
                               np.absolute(delta_taxes_down),
                               delta_taxes_up, delta_taxes_down)

        # Calculate the marginal tax rate
        mtr = delta_taxes / diff

        return mtr
