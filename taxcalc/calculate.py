import math
import copy
import numpy as np
import pandas as pd
from pandas import DataFrame
from .utils import *
from .functions import *
from .parameters import Parameters
from .records import Records
from .behavior import Behavior

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


class Calculator(object):

    def __init__(self, params=None, records=None,
                 sync_years=True, behavior=None, **kwargs):

        if isinstance(params, Parameters):
            self._params = params
        else:
            msg = 'Must supply tax parameters as a Parameters object'
            raise ValueError(msg)
        if isinstance(behavior, Behavior):
            self.behavior = behavior
        else:
            self.behavior = Behavior(start_year=params.start_year)

        if isinstance(records, Records):
            self._records = records
        elif isinstance(records, str):
            self._records = Records.from_file(records, **kwargs)
        else:
            msg = 'Must supply tax records as a file path or Records object'
            raise ValueError(msg)

        if sync_years and self._records.current_year == Records.PUF_YEAR:
            print("You loaded data for " +
                  str(self._records.current_year) + '.')

            if self._records.current_year == 2009:
                self.records.extrapolate_2009_puf()

            while self._records.current_year < self._params.current_year:
                self._records.increment_year()

            print("Your data have been extrapolated to " +
                  str(self._records.current_year) + ".")

        assert self._params.current_year == self._records.current_year

    @property
    def params(self):
        return self._params

    @property
    def records(self):
        return self._records

    def calc_one_year(self):
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

    def calc_all(self):
        self.calc_one_year()
        BenefitSurtax(self)

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
        self.params.set_year(self.params.current_year + 1)
        self.behavior.set_year(self.params.current_year)

    @property
    def current_year(self):
        return self.params.current_year

    def mtr(self, income_type_string, finite_diff=1, FICA=True, IIT=True):
        """
        Calculates the marginal tax rate for every record.
        Avoids kinks in the tax schedule by finding the marginal rates
        associated with both an income increase and an income decrease and
        then uses the more modest of the two.
        By default, both FICA and IIT are included in the MTR calculation.

        Parameters
        ----------
        income_type_string: string of an income attribute on the Records class.

        finite_diff: the marginal amount to be added or subtracted from income
            in order to calculate the marginal tax rate.

        FICA: boolean to indicate whether the MTR calculation includes FICA.

        IIT: boolean to indicate whether the MTR calculation includes IIT.

        Returns
        -------
        mtr: an array of marginal tax rates.

        """

        # Verify that the mtr calculation is for either FICA or IIT
        if FICA is False and IIT is False:
            msg = "mtr must be calculated for either FICA, IIT, or both."
            raise ValueError(msg)

        income_type = getattr(self.records, income_type_string)

        # Calculate the base level of taxes.
        self.calc_all()
        taxes_base = np.zeros(self.records._ospctax.shape)
        if IIT:
            taxes_base += np.copy(self.records._ospctax)
        if FICA:
            taxes_base += np.copy(self.records._fica)

        # Calculate the tax change with a marginal increase in income.
        setattr(self.records, income_type_string, income_type + finite_diff)
        self.calc_all()
        new_taxes_up = np.zeros(self.records._ospctax.shape)
        if IIT:
            new_taxes_up += self.records._ospctax
        if FICA:
            new_taxes_up += self.records._fica
        delta_taxes_up = new_taxes_up - taxes_base

        # Calculate the tax change with a marginal decrease in income.
        setattr(self.records, income_type_string, income_type - finite_diff)
        self.calc_all()
        new_taxes_down = np.zeros(self.records._ospctax.shape)
        if IIT:
            new_taxes_down += self.records._ospctax
        if FICA:
            new_taxes_down += self.records._fica
        delta_taxes_down = new_taxes_down - taxes_base

        # Reset the income_type to its starting point to avoid
        # unintended consequences.
        setattr(self.records, income_type_string, income_type)
        self.calc_all()

        # Choose the more modest effect of either adding or subtracting income
        delta_taxes = np.where(np.absolute(delta_taxes_up) <=
                               np.absolute(delta_taxes_down),
                               delta_taxes_up, delta_taxes_down)

        # Calculate the marginal tax rate
        mtr = delta_taxes / finite_diff

        return mtr

    def diagnostic_table(self, num_years=5):
        table = []
        row_years = []
        calc = copy.deepcopy(self)

        for i in range(0, num_years):
            calc.calc_all()

            row_years.append(calc.params._current_year)

            # totoal number of records
            returns = calc.records.s006.sum()

            # AGI
            agi = (calc.records.c00100 * calc.records.s006).sum()

            # number of itemizers
            ID1 = calc.records.c04470 * calc.records.s006
            STD1 = calc.records._standard * calc.records.s006
            deduction = np.maximum(calc.records.c04470, calc.records._standard)

            # S TD1 = (calc.c04100 + calc.c04200)*calc.s006
            NumItemizer1 = (calc.records.s006[(calc.records.c04470 > 0) *
                            (calc.records.c00100 > 0)].sum())

            # itemized deduction
            ID = ID1[calc.records.c04470 > 0].sum()

            NumSTD = calc.records.s006[(calc.records._standard > 0) *
                                       (calc.records.c00100 > 0)].sum()
            # standard deduction
            STD = STD1[(calc.records._standard > 0) *
                       (calc.records.c00100 > 0)].sum()

            # personal exemption
            PE = (calc.records.c04600 *
                  calc.records.s006)[calc.records.c00100 > 0].sum()

            # taxable income
            taxinc = (calc.records.c04800 * calc.records.s006).sum()

            # regular tax
            regular_tax = (calc.records.c05200 * calc.records.s006).sum()

            # AMT income
            AMTI = (calc.records.c62100 * calc.records.s006).sum()

            # total AMTs
            AMT = (calc.records.c09600 * calc.records.s006).sum()

            # number of people paying AMT
            NumAMT1 = calc.records.s006[calc.records.c09600 > 0].sum()

            # tax before credits
            tax_bf_credits = (calc.records.c05800 * calc.records.s006).sum()

            # tax before nonrefundable credits 09200
            tax_bf_nonrefundable = (calc.records.c09200 *
                                    calc.records.s006).sum()

            # refundable credits
            refundable = (calc.records._refund * calc.records.s006).sum()

            # nonrefuncable credits
            nonrefundable = (calc.records.c07100 * calc.records.s006).sum()

            # Misc. Surtax
            surtax = (calc.records._surtax * calc.records.s006).sum()

            # ospc_tax
            revenue1 = (calc.records._ospctax * calc.records.s006).sum()

            table.append([returns / math.pow(10, 6), agi / math.pow(10, 9),
                          NumItemizer1 / math.pow(10, 6), ID / math.pow(10, 9),
                          NumSTD / math.pow(10, 6), STD / math.pow(10, 9),
                          PE / math.pow(10, 9), taxinc / math.pow(10, 9),
                          regular_tax / math.pow(10, 9),
                          AMTI / math.pow(10, 9), AMT / math.pow(10, 9),
                          NumAMT1 / math.pow(10, 6),
                          tax_bf_credits / math.pow(10, 9),
                          refundable / math.pow(10, 9),
                          nonrefundable / math.pow(10, 9),
                          surtax / math.pow(10, 9),
                          revenue1 / math.pow(10, 9)])
            calc.increment_year()

        df = DataFrame(table, row_years,
                       ["Returns (#m)", "AGI ($b)", "Itemizers (#m)",
                        "Itemized Deduction ($b)",
                        "Standard Deduction Filers (#m)",
                        "Standard Deduction ($b)", "Personal Exemption ($b)",
                        "Taxable income ($b)", "Regular Tax ($b)",
                        "AMT income ($b)", "AMT amount ($b)",
                        "AMT number (#m)", "Tax before credits ($b)",
                        "refundable credits ($b)",
                        "nonrefundable credits ($b)",
                        "Misc. Surtax ($b)",
                        "ospctax ($b)"])
        df = df.transpose()
        pd.options.display.float_format = '{:8,.1f}'.format

        return df
