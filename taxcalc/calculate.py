import math
import copy
import numpy as np
import pandas as pd
from pandas import DataFrame
from .utils import *
from .functions import *
from .policy import Policy
from .records import Records
from .behavior import Behavior
from .growth import Growth, adjustment, target

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

    def __init__(self, policy=None, records=None,
                 sync_years=True, behavior=None, growth=None, **kwargs):

        if isinstance(policy, Policy):
            self._policy = policy
        else:
            msg = 'Must supply tax parameters as a Policy object'
            raise ValueError(msg)

        if isinstance(behavior, Behavior):
            self.behavior = behavior
        else:
            self.behavior = Behavior(start_year=policy.start_year)

        if growth:
            if isinstance(growth, Growth):
                self.growth = growth
            else:
                raise ValueError("Must supply growth as a Growth object")
        else:
            self.growth = Growth(start_year=policy.start_year)

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

            while self._records.current_year < self._policy.current_year:
                self._records.increment_year()

            print("Your data have been extrapolated to " +
                  str(self._records.current_year) + ".")

        assert self._policy.current_year == self._records.current_year

    @property
    def policy(self):
        return self._policy

    @property
    def records(self):
        return self._records

    def TaxInc_to_AMTI(self):
        TaxInc(self.policy, self.records)
        XYZD(self.policy, self.records)
        NonGain(self.policy, self.records)
        TaxGains(self.policy, self.records)
        MUI(self.policy, self.records)
        AMTI(self.policy, self.records)

    def calc_one_year(self):
        FilingStatus(self.policy, self.records)
        Adj(self.policy, self.records)
        CapGains(self.policy, self.records)
        SSBenefits(self.policy, self.records)
        AGI(self.policy, self.records)
        ItemDed(self.policy, self.records)
        EI_FICA(self.policy, self.records)
        AMED(self.policy, self.records)
        StdDed(self.policy, self.records)
        # Store calculated standard deduction, calculate
        # taxes with standard deduction, store AMT + Regular Tax
        std = copy.deepcopy(self.records._standard)
        item = copy.deepcopy(self.records.c04470)
        item_no_limit = copy.deepcopy(self.records.c21060)
        self.records.c04470 = np.zeros(self.records.dim)
        self.records.c21060 = np.zeros(self.records.dim)
        self.TaxInc_to_AMTI()
        std_taxes = copy.deepcopy(self.records.c05200 +
                                  self.records.c09600)
        # Set standard deduction to zero, calculate taxes w/o
        # standard deduction, and store AMT + Regular Tax
        self.records._standard = np.zeros(self.records.dim)
        self.records.c21060 = item_no_limit
        self.records.c04470 = item
        self.TaxInc_to_AMTI()
        item_taxes = copy.deepcopy(self.records.c05200 +
                                   self.records.c09600)
        # Replace standard deduction with zero where the taxpayer
        # would be better off itemizing
        self.records._standard = np.where(item_taxes <
                                          std_taxes,
                                          0, std)
        self.records.c04470 = np.where(item_taxes <
                                       std_taxes,
                                       item, 0)
        self.records.c21060 = np.where(item_taxes <
                                       std_taxes,
                                       item_no_limit, 0)

        # Calculate taxes with optimal itemized deduction
        TaxInc(self.policy, self.records)
        XYZD(self.policy, self.records)
        NonGain(self.policy, self.records)
        TaxGains(self.policy, self.records)
        MUI(self.policy, self.records)
        AMTI(self.policy, self.records)
        F2441(self.policy, self.records)
        DepCareBen(self.policy, self.records)
        ExpEarnedInc(self.policy, self.records)
        NumDep(self.policy, self.records)
        ChildTaxCredit(self.policy, self.records)
        AmOppCr(self.policy, self.records)
        LLC(self.policy, self.records)
        RefAmOpp(self.policy, self.records)
        NonEdCr(self.policy, self.records)
        AddCTC(self.policy, self.records)
        F5405(self.policy, self.records)
        C1040(self.policy, self.records)
        DEITC(self.policy, self.records)
        OSPC_TAX(self.policy, self.records)
        ExpandIncome(self.policy, self.records)

    def calc_all(self):
        self.calc_one_year()
        BenefitSurtax(self)

    def calc_all_test(self):
        all_dfs = []
        add_df(all_dfs, FilingStatus(self.policy, self.records))
        add_df(all_dfs, Adj(self.policy, self.records))
        add_df(all_dfs, CapGains(self.policy, self.records))
        add_df(all_dfs, SSBenefits(self.policy, self.records))
        add_df(all_dfs, AGI(self.policy, self.records))
        add_df(all_dfs, ItemDed(self.policy, self.records))
        add_df(all_dfs, EI_FICA(self.policy, self.records))
        add_df(all_dfs, AMED(self.policy, self.records))
        add_df(all_dfs, StdDed(self.policy, self.records))
        add_df(all_dfs, TaxInc(self.policy, self.records))
        add_df(all_dfs, XYZD(self.policy, self.records))
        add_df(all_dfs, NonGain(self.policy, self.records))
        add_df(all_dfs, TaxGains(self.policy, self.records))
        add_df(all_dfs, MUI(self.policy, self.records))
        add_df(all_dfs, AMTI(self.policy, self.records))
        add_df(all_dfs, F2441(self.policy, self.records))
        add_df(all_dfs, DepCareBen(self.policy, self.records))
        add_df(all_dfs, ExpEarnedInc(self.policy, self.records))
        add_df(all_dfs, NumDep(self.policy, self.records))
        add_df(all_dfs, ChildTaxCredit(self.policy, self.records))
        add_df(all_dfs, AmOppCr(self.policy, self.records))
        add_df(all_dfs, LLC(self.policy, self.records))
        add_df(all_dfs, RefAmOpp(self.policy, self.records))
        add_df(all_dfs, NonEdCr(self.policy, self.records))
        add_df(all_dfs, AddCTC(self.policy, self.records))
        add_df(all_dfs, F5405(self.policy, self.records))
        add_df(all_dfs, C1040(self.policy, self.records))
        add_df(all_dfs, DEITC(self.policy, self.records))
        add_df(all_dfs, OSPC_TAX(self.policy, self.records))
        add_df(all_dfs, ExpandIncome(self.policy, self.records))
        totaldf = pd.concat(all_dfs, axis=1)
        return totaldf

    def increment_year(self):
        if self.growth.factor_adjustment != 0:
            if np.any(self.growth._factor_target) != 0:
                msg = "adjustment and target factor \
                       cannot be non-zero at the same time"
                raise ValueError(msg)
            else:
                adjustment(self, self.growth.factor_adjustment,
                           self.policy.current_year + 1)
        elif np.any(self.growth._factor_target) != 0:
            target(self, self.growth._factor_target,
                   self.policy._inflation_rates,
                   self.policy.current_year + 1)

        self.records.increment_year()
        self.policy.set_year(self.policy.current_year + 1)
        self.behavior.set_year(self.policy.current_year)

    @property
    def current_year(self):
        return self.policy.current_year

    def mtr(self, income_type_string,
            finite_diff=1.0,
            wrt_adjusted_income=True):
        """
        Calculates the individual income tax, FICA, and combined marginal tax
        rates for every record. Avoids kinks in the tax schedule by finding
        the marginal rates associated with both an income increase and an
        income decrease and then uses the more modest of the two.

        Parameters
        ----------
        income_type_string: string
            specifies an income attribute in the Records class.

        finite_diff: float
            specifies marginal amount to be added or subtracted from income
            in order to calculate the marginal tax rate.

        wrt_adjusted_income: boolean
            specifies whether or not marginal tax rates on earned income are
            computed with respect to (wrt) changes in adjusted income that
            includes the employer share of OASDI+HI payroll taxes.

        Returns
        -------
        mtr_fica: an array of FICA marginal tax rates.
        mtr_iit: an array of individual income tax marginal tax rates.
        mtr_combined: an array of combined IIT and FICA marginal tax rates.
        """
        # Check validity of income_type_string parameter.
        if income_type_string == 'e00200p':
            pass
        else:
            msg = 'mtr income_type_string={} not yet supported'
            raise ValueError(msg.format(income_type_string))

        # Check for reasonable value of finite_diff parameter.
        if finite_diff <= 0.0 or finite_diff > 10.0:
            msg = 'mtr finite_diff={} not in (0,10] range'
            raise ValueError(msg.format(finite_diff))

        income_type = getattr(self.records, income_type_string)
        earnings_type = getattr(self.records, 'e00200')

        # Calculate the base level of taxes.
        self.calc_all()
        _ospctax_base = copy.deepcopy(self.records._ospctax)
        _fica_base = copy.deepcopy(self.records._fica)
        _combined_taxes_base = _ospctax_base + _fica_base

        # Calculate the tax change with a marginal increase in income.
        setattr(self.records, income_type_string, income_type + finite_diff)
        setattr(self.records, 'e00200', earnings_type + finite_diff)
        self.calc_all()

        _ospctax_up = copy.deepcopy(self.records._ospctax)
        _fica_up = copy.deepcopy(self.records._fica)
        _combined_taxes_up = _ospctax_up + _fica_up

        delta_fica_up = _fica_up - _fica_base
        delta_ospctax_up = _ospctax_up - _ospctax_base
        delta_combined_taxes_up = _combined_taxes_up - _combined_taxes_base

        # Calculate the tax change with a marginal decrease in income.
        setattr(self.records, income_type_string,
                income_type - 2 * finite_diff)
        setattr(self.records, 'e00200',
                earnings_type - 2 * finite_diff)
        self.calc_all()

        _ospctax_down = copy.deepcopy(self.records._ospctax)
        _fica_down = copy.deepcopy(self.records._fica)
        _combined_taxes_down = _ospctax_down + _fica_down

        # We never take the downward version
        # when the taxpayer's wages are sent negative.
        delta_fica_down = np.where(income_type >=
                                   finite_diff,
                                   _fica_base - _fica_down,
                                   delta_fica_up)
        delta_ospctax_down = np.where(income_type >=
                                      finite_diff,
                                      _ospctax_base - _ospctax_down,
                                      delta_ospctax_up)
        delta_combined_taxes_down = np.where(income_type >=
                                             finite_diff,
                                             _combined_taxes_base -
                                             _combined_taxes_down,
                                             delta_combined_taxes_up)

        # Reset the income_type to its starting point to avoid
        # unintended consequences.
        setattr(self.records, income_type_string, income_type + finite_diff)
        setattr(self.records, 'e00200', earnings_type + finite_diff)
        self.calc_all()

        # Choose the more modest effect of either adding or subtracting income
        delta_fica = np.where(np.absolute(delta_fica_up) <=
                              np.absolute(delta_fica_down),
                              delta_fica_up, delta_fica_down)
        delta_ospctax = np.where(np.absolute(delta_ospctax_up) <=
                                 np.absolute(delta_ospctax_down),
                                 delta_ospctax_up, delta_ospctax_down)
        delta_combined_taxes = np.where(np.absolute(delta_combined_taxes_up) <=
                                        np.absolute(delta_combined_taxes_down),
                                        delta_combined_taxes_up,
                                        delta_combined_taxes_down)

        # Calculate marginal tax rates:
        # The rate we want is the "after-tax share of tax in compensation".
        # Since only half of the social security tax is including in wages for
        # income tax purposes, we need to increase the denominator by the
        # excluded portion of FICA.
        if (wrt_adjusted_income and
            (income_type_string == 'e00200' or
             income_type_string == 'e00200s' or
             income_type_string == 'e00200p')):
            employer_fica_adjustment = np.where(self.records.e00200 <
                                                self.policy.SS_Earnings_c,
                                                0.5 * self.policy.FICA_ss_trt +
                                                0.5 * self.policy.FICA_mc_trt,
                                                0.5 * self.policy.FICA_mc_trt)
        else:
            employer_fica_adjustment = 0.

        mtr_fica = delta_fica / (finite_diff + employer_fica_adjustment)
        mtr_iit = delta_ospctax / (finite_diff + employer_fica_adjustment)
        mtr_combined = delta_combined_taxes / (finite_diff +
                                               employer_fica_adjustment)
        return (mtr_fica, mtr_iit, mtr_combined)

    def diagnostic_table(self, num_years=5):
        table = []
        row_years = []
        calc = copy.deepcopy(self)

        for i in range(0, num_years):
            calc.calc_all()

            row_years.append(calc.policy._current_year)

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

            # payroll tax (FICA)
            payroll = (calc.records._fica * calc.records.s006).sum()

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
                          revenue1 / math.pow(10, 9),
                          payroll / math.pow(10, 9)])
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
                        "ospctax ($b)", "Payroll tax ($b)"])
        df = df.transpose()
        pd.options.display.float_format = '{:8,.1f}'.format

        return df
