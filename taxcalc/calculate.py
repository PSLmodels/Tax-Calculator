"""
Tax-Calculator federal tax Calculator class.
"""
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
                 sync_years=True, behavior=None, growth=None):

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
        else:
            raise ValueError('must specify records as a Records object')

        if sync_years and self._records.current_year == Records.PUF_YEAR:
            print("You loaded data for " +
                  str(self._records.current_year) + '.')

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
        Personal_Credit(self.policy, self.records)
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
        IITAX(self.policy, self.records)
        ExpandIncome(self.policy, self.records)

    def calc_all(self):
        self.calc_one_year()
        BenefitSurtax(self)

    def increment_year(self):
        if self.growth.factor_adjustment != 0:
            if not np.array_equal(self.growth._factor_target,
                                  Growth.REAL_GDP_GROWTH_RATES):
                msg = "adjustment and target factor \
                       cannot be non-zero at the same time"
                raise ValueError(msg)
            else:
                adjustment(self, self.growth.factor_adjustment,
                           self.policy.current_year + 1)
        elif not np.array_equal(self.growth._factor_target,
                                Growth.REAL_GDP_GROWTH_RATES):
            target(self, self.growth._factor_target,
                   self.policy.current_year + 1)
        self.records.increment_year()
        self.policy.set_year(self.policy.current_year + 1)
        self.behavior.set_year(self.policy.current_year)

    @property
    def current_year(self):
        return self.policy.current_year

    def mtr(self, income_type_str='e00200p',
            wrt_full_compensation=True):
        """
        Calculates the marginal FICA, individual income, and combined
        tax rates for every tax filing unit.
          The marginal tax rates are approximated as the change in tax
        liability caused by a small increase (the finite_diff) in income
        (specified by the income_type_str) divided by that small increase
        in income, when wrt_full_compensation is false.
          If wrt_full_compensation is true, then the marginal tax rates
        are computed as the change in tax liability divided by the change
        in total compensation caused by the small increase in income
        (where the change in total compensation is the sum of the small
        increase in income and any increase in the employer share of FICA
        taxes caused by the small increase in income).

        Parameters
        ----------
        income_type_str: string
            specifies type of income that is increased to compute the
            marginal tax rates.  See Notes for list of valid income types.

        wrt_full_compensation: boolean
            specifies whether or not marginal tax rates on earned income
            are computed with respect to (wrt) changes in total compensation
            that includes the employer share of OASDI+HI payroll taxes.

        Returns
        -------
        mtr_fica: an array of marginal FICA tax rates.
        mtr_iit: an array of marginal individual income tax (IIT) rates.
        mtr_combined: an array of marginal combined FICA and IIT tax rates.

        Notes
        -----
        Valid income_type_str values are:
        'e00200p', taxpayer wage/salary earnings (which is the default value);
        'e00900p', taxpayer (Schedule C) self-employment income;
        'e00300',  taxable interest income;
        'e23250',  long-term capital gains;
        'e01700',  federally-taxable pension benefits; and
        'e02400',  social security (OASDI) benefits.
        """
        mtr_valid_income_types = ['e00200p', 'e00900p',
                                  'e00300', 'e23250',
                                  'e01700', 'e02400']
        # check validity of income_type_str parameter
        if income_type_str not in mtr_valid_income_types:
            msg = 'mtr income_type_str="{}" is not valid'
            raise ValueError(msg.format(income_type_str))
        # specify value for finite_diff parameter
        finite_diff = 0.01  # a one-cent difference
        # extract income_type array(s) from embedded records object
        income_type = getattr(self.records, income_type_str)
        if income_type_str == 'e00200p':
            earnings_type = self.records.e00200
        elif income_type_str == 'e00900p':
            seincome_type = self.records.e00900
        # calculate base level of taxes
        self.calc_all()
        fica_base = copy.deepcopy(self.records._fica)
        iitax_base = copy.deepcopy(self.records._iitax)
        combined_taxes_base = iitax_base + fica_base
        # calculate level of taxes after a marginal increase in income
        setattr(self.records, income_type_str, income_type + finite_diff)
        if income_type_str == 'e00200p':
            self.records.e00200 = earnings_type + finite_diff
        elif income_type_str == 'e00900p':
            self.records.e00900 = seincome_type + finite_diff
        self.calc_all()
        fica_up = copy.deepcopy(self.records._fica)
        iitax_up = copy.deepcopy(self.records._iitax)
        combined_taxes_up = iitax_up + fica_up
        # compute marginal changes in tax liability
        fica_delta = fica_up - fica_base
        iitax_delta = iitax_up - iitax_base
        combined_delta = combined_taxes_up - combined_taxes_base
        # return embedded records object to its original state and recalculate
        setattr(self.records, income_type_str, income_type)
        if income_type_str == 'e00200p':
            self.records.e00200 = earnings_type
        elif income_type_str == 'e00900p':
            self.records.e00900 = seincome_type
        self.calc_all()
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        if wrt_full_compensation and income_type_str == 'e00200p':
            adj = np.where(income_type <
                           self.policy.SS_Earnings_c,
                           0.5 * (self.policy.FICA_ss_trt +
                                  self.policy.FICA_mc_trt),
                           0.5 * self.policy.FICA_mc_trt)
        else:
            adj = 0.0
        # compute marginal tax rates
        mtr_fica = fica_delta / (finite_diff * (1.0 + adj))
        mtr_iit = iitax_delta / (finite_diff * (1.0 + adj))
        mtr_combined = combined_delta / (finite_diff * (1.0 + adj))
        # return the three marginal tax rate arrays
        return (mtr_fica, mtr_iit, mtr_combined)

    def capital_mtr(self):
        capital_income_sources = ['e00300', 'e00400', 'e00600', 'e00650', 'e01000',
                                  'e01400', 'e01500', 'e01700', 'e02000', 'e23250']
        
        length = len(self.records.s006)
        income_sum = np.zeros(length)
        originals = {}
        
        # get the sum of all capital income and save the values for later use
        for capital_income in capital_income_sources:
            income_sum += getattr(self.records, capital_income)
            originals[capital_income] = getattr(self.records, capital_income)

        self.calc_all()
        iitax_base = copy.deepcopy(self.records._iitax)

        # add the one-cent margin
        finite_diff = 0.01  # a one-cent difference   
        for capital_income in capital_income_sources:
            income_up = originals[capital_income] * (1 + finite_diff/income_sum)
            setattr(self.records, capital_income, income_up)

        self.calc_all()
        iitax_up = copy.deepcopy(self.records._iitax)

        # delta of the results with margin added
        iitax_delta = iitax_up - iitax_base
        
        # calculates mtrs
        mtr_iit = iitax_delta / finite_diff

        # reset everything
        for capital_income in capital_income_sources:
            setattr(self.records, capital_income, originals[capital_income])
        self.calc_all()
        
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

            # iitax
            revenue1 = (calc.records._iitax * calc.records.s006).sum()

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
                        "Ind inc tax ($b)", "Payroll tax ($b)"])
        df = df.transpose()
        pd.options.display.float_format = '{:8,.1f}'.format

        return df
