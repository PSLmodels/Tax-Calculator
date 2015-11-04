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
            raise ValueError('must specify policy as a Policy object')

        if behavior:
            if isinstance(behavior, Behavior):
                self.behavior = behavior
            else:
                raise ValueError('behavior must be a Behavior object')
        else:
            self.behavior = Behavior(start_year=policy.start_year)

        if growth:
            if isinstance(growth, Growth):
                self.growth = growth
            else:
                raise ValueError('growth must be a Growth object')
        else:
            self.growth = Growth(start_year=policy.start_year)

        if isinstance(records, Records):
            self._records = records
        elif isinstance(records, str):
            self._records = Records.from_file(records, **kwargs)
        else:
            msg = 'must specify records as a file path or Records object'
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
        std_taxes = copy.deepcopy(self.records.c05800)
        # Set standard deduction to zero, calculate taxes w/o
        # standard deduction, and store AMT + Regular Tax
        self.records._standard = np.zeros(self.records.dim)
        self.records.c21060 = item_no_limit
        self.records.c04470 = item
        self.TaxInc_to_AMTI()
        item_taxes = copy.deepcopy(self.records.c05800)
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
                   self.policy.inflation_rates,
                   self.policy.current_year + 1)
        self.records.increment_year()
        self.policy.set_year(self.policy.current_year + 1)
        self.behavior.set_year(self.policy.current_year)

    @property
    def current_year(self):
        return self.policy.current_year

    def mtr(self, income_type_str='e00200p',
            finite_diff=0.01,
            wrt_adjusted_income=True):
        """
        Calculates the individual income tax, FICA, and combined marginal tax
        rates for every record. Avoids kinks in the tax schedule by finding
        the marginal rates associated with both an income increase and an
        income decrease and then uses the more modest of the two.

        Parameters
        ----------
        income_type_str: string
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
        mtr_fica: an array of marginal FICA tax rates.
        mtr_iit: an array of marginal individual income tax (IIT) rates.
        mtr_combined: an array of marginal combined FICA and IIT tax rates.
        """
        MTR_VALID_INCOME_TYPES = ['e00200p']
        MTR_IND_EARNINGS_TYPES = ['e00200p', 'e00200s']
        # check validity of income_type_str parameter
        if income_type_str not in MTR_VALID_INCOME_TYPES:
            msg = 'mtr income_type_str={} not valid'
            raise ValueError(msg.format(income_type_str))
        # check for reasonable value of finite_diff parameter
        if finite_diff <= 0.0 or finite_diff > 10.0:
            msg = 'mtr finite_diff={} not in (0,10] range'
            raise ValueError(msg.format(finite_diff))
        # extract income_type(s) from embedded records object
        income_type = getattr(self.records, income_type_str)
        if income_type_str in MTR_IND_EARNINGS_TYPES:
            earnings_type = self.records.e00200
        # calculate base level of taxes
        self.calc_all()
        fica_base = copy.deepcopy(self.records._fica)
        ospctax_base = copy.deepcopy(self.records._ospctax)
        combined_taxes_base = ospctax_base + fica_base
        # calculate level of taxes after a marginal increase in income
        setattr(self.records, income_type_str, income_type + finite_diff)
        if income_type_str in MTR_IND_EARNINGS_TYPES:
            self.records.e00200 = earnings_type + finite_diff
        self.calc_all()
        fica_up = copy.deepcopy(self.records._fica)
        ospctax_up = copy.deepcopy(self.records._ospctax)
        combined_taxes_up = ospctax_up + fica_up
        # return embedded records object to its original state and recalculate
        setattr(self.records, income_type_str, income_type)
        if income_type_str in MTR_IND_EARNINGS_TYPES:
            self.records.e00200 = earnings_type
        self.calc_all()
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        #    The marginal tax rate we want is the "after-tax share
        #    of tax in compensation". Since only half of the OASDI+HI
        #    payroll tax is included in wages for income tax purposes,
        #    we need to increase the denominator by the excluded portion
        #    of the OASDI+HI payroll tax.  Note that OASDI is "social
        #    security" [_ss_ below] and that HI is "Medicare" [_mc_ below]
        #    and that they are combined in the "FICA" or payroll tax.
        if wrt_adjusted_income and income_type_str in MTR_IND_EARNINGS_TYPES:
            er_fica_adjustment = np.where(income_type <
                                          self.policy.SS_Earnings_c,
                                          (0.5 * self.policy.FICA_ss_trt +
                                           0.5 * self.policy.FICA_mc_trt),
                                          0.5 * self.policy.FICA_mc_trt)
            adjusted_finite_diff = finite_diff * (1.0 + er_fica_adjustment)
        else:
            adjusted_finite_diff = finite_diff
        # compute marginal tax rates
        fica_delta = fica_up - fica_base
        ospctax_delta = ospctax_up - ospctax_base
        combined_delta = combined_taxes_up - combined_taxes_base
        mtr_fica = fica_delta / adjusted_finite_diff
        mtr_iit = ospctax_delta / adjusted_finite_diff
        mtr_combined = combined_delta / adjusted_finite_diff
        # return the three marginal tax rate arrays
        return (mtr_fica, mtr_iit, mtr_combined)

    def diagnostic_table(self, num_years=5):
        table = []
        row_years = []
        calc = copy.deepcopy(self)

        for i in range(0, num_years):
            calc.calc_all()

            row_years.append(calc.policy.current_year)

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
