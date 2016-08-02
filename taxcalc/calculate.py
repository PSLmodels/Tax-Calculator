"""
Tax-Calculator federal tax Calculator class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 calculate.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy calculat.py
#
# pylint: disable=wildcard-import,unused-wildcard-import
# pylint: disable=wildcard-import,missing-docstring,invalid-name
# pylint: disable=too-many-arguments,too-many-branches,too-many-locals
# pylint: disable=no-value-for-parameter,protected-access


import copy
import numpy as np
from .utils import *
from .functions import *
from .policy import Policy
from .records import Records
from .behavior import Behavior
from .growth import Growth
from .consumption import Consumption
# import pdb


class Calculator(object):
    """
    Constructor for the Calculator class.

    Parameters
    ----------
    policy: Policy class object
        this argument must be specified
        IMPORTANT NOTE: never pass the same Policy object to more than one
                        Calculator.  In other words, when specifying more
                        than one Calculator object, do this:
                        pol1 = Policy()
                        rec1 = Records()
                        calc1 = Calculator(policy=pol1, records=rec1)
                        pol2 = Policy()
                        rec2 = Records()
                        calc2 = Calculator(policy=pol2, records=rec2)

    records: Records class object
        this argument must be specified
        IMPORTANT NOTE: never pass the same Records object to more than one
                        Calculator.  In other words, when specifying more
                        than one Calculator object, do this:
                        pol1 = Policy()
                        rec1 = Records()
                        calc1 = Calculator(policy=pol1, records=rec1)
                        pol2 = Policy()
                        rec2 = Records()
                        calc2 = Calculator(policy=pol2, records=rec2)

    verbose: boolean
        specifies whether or not to write to stdout data-loaded and
        data-extrapolated progress reports; default value is true.

    sync_years: boolean
        specifies whether or not to syncronize policy year and records year;
        default value is true.

    behavior: Behavior class object
        specifies behaviorial responses used by Calculator; default is None,
        which implies no behavioral responses.

    growth: Growth class object
        specifies economic growth assumptions used by Calculator; default is
        None, which implies use of standard economic growth assumptions.

    consumption: Consumption class object
        specifies consumption response assumptions used to calculate
        "effective" marginal tax rates; default is None, which implies
        no consumption responses.

    Raises
    ------
    ValueError:
        if parameters are not the appropriate type.

    Returns
    -------
    class instance: Calculator
    """

    def __init__(self, policy=None, records=None, verbose=True,
                 sync_years=True, behavior=None, growth=None,
                 consumption=None):
        if isinstance(policy, Policy):
            self._policy = policy
        else:
            raise ValueError('must specify policy as a Policy object')
        if isinstance(records, Records):
            self._records = records
        else:
            raise ValueError('must specify records as a Records object')
        if behavior is None:
            self.behavior = Behavior(start_year=policy.start_year)
        elif isinstance(behavior, Behavior):
            self.behavior = behavior
        else:
            raise ValueError('behavior must be None or Behavior object')
        if growth is None:
            self.growth = Growth(start_year=policy.start_year)
        elif isinstance(growth, Growth):
            self.growth = growth
        else:
            raise ValueError('growth must be None or Growth object')
        if consumption is None:
            self.consumption = Consumption(start_year=policy.start_year)
        elif isinstance(consumption, Consumption):
            self.consumption = consumption
        else:
            raise ValueError('consumption must be None or Consumption object')
        if sync_years and self._records.current_year == Records.PUF_YEAR:
            if verbose:
                print('You loaded data for ' +
                      str(self._records.current_year) + '.')
            while self._records.current_year < self._policy.current_year:
                self._records.increment_year()
            if verbose:
                print('Your data have been extrapolated to ' +
                      str(self._records.current_year) + '.')
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
        TaxGains(self.policy, self.records)
        MUI(self.policy, self.records)
        AMTI(self.policy, self.records)

    def calc_one_year(self, zero_out_calc_vars=False):
        # calls all the functions except BenefitSurtax and ExpandIncome
        if zero_out_calc_vars:
            self.records.zero_out_changing_calculated_vars()
        # pdb.set_trace()
        EI_FICA(self.policy, self.records)
        Adj(self.policy, self.records)
        CapGains(self.policy, self.records)
        SSBenefits(self.policy, self.records)
        AGI(self.policy, self.records)
        ItemDed(self.policy, self.records)
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
        self.records._standard[:] = np.where(item_taxes < std_taxes,
                                             0., std)
        self.records.c04470[:] = np.where(item_taxes < std_taxes,
                                          item, 0.)
        self.records.c21060[:] = np.where(item_taxes < std_taxes,
                                          item_no_limit, 0.)
        # Calculate taxes with optimal itemized deduction
        self.TaxInc_to_AMTI()
        F2441(self.policy, self.records)
        NumDep(self.policy, self.records)
        ChildTaxCredit(self.policy, self.records)
        AmOppCr(self.policy, self.records)
        LLC(self.policy, self.records)
        RefAmOpp(self.policy, self.records)
        SchR(self.policy, self.records)
        NonEdCr(self.policy, self.records)
        AddCTC(self.policy, self.records)
        F5405(self.policy, self.records)
        C1040(self.policy, self.records)
        DEITC(self.policy, self.records)
        IITAX(self.policy, self.records)
        ExpandIncome(self.policy, self.records)

    def calc_all(self, zero_out_calc_vars=False):
        # conducts static analysis of Calculator object for current_year
        self.calc_one_year(zero_out_calc_vars)
        BenefitSurtax(self)

    def increment_year(self):
        next_year = self.policy.current_year + 1
        self.growth.apply_change(self.records, next_year)
        self.growth.set_year(next_year)
        self.records.increment_year()
        self.policy.set_year(next_year)
        self.behavior.set_year(next_year)
        self.consumption.set_year(next_year)

    def advance_to_year(self, year):
        '''
        The advance_to_year function gives an optional way of implementing
        increment year functionality by immediately specifying the year
        as input. New year must be at least the current year.
        '''
        iteration = year - self.records.current_year
        if iteration < 0:
            raise ValueError('New current year must be ' +
                             'greater than current year!')
        for _ in range(iteration):
            self.increment_year()
        assert self.records.current_year == year

    @property
    def current_year(self):
        return self.policy.current_year

    MTR_VALID_INCOME_TYPES = ['e00200p', 'e00900p',
                              'e00300', 'e00400',
                              'e00600', 'e00650',
                              'e01400', 'e01700',
                              'e02000', 'e02400',
                              'p22250', 'p23250']

    def mtr(self, income_type_str='e00200p',
            negative_finite_diff=False,
            zero_out_calculated_vars=False,
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

        negative_finite_diff: boolean
            specifies whether or not marginal tax rates are computed by
            subtracting (rather than adding) a small finite_diff amount
            to the specified income type.

        zero_out_calculated_vars: boolean
            specifies value of zero_out_calc_vars parameter used in calls
            of Calculator.calc_all() method.

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
        'e00200p', taxpayer wage/salary earnings (also included in e00200);
        'e00900p', taxpayer Schedule C self-employment income (also in e00900);
        'e00300',  taxable interest income;
        'e00400',  federally-tax-exempt interest income;
        'e00600',  all dividends included in AGI
        'e00650',  qualified dividends (also included in e00600)
        'e01400',  federally-taxable IRA distribution;
        'e01700',  federally-taxable pension benefits;
        'e02000',  Schedule E net income/loss
        'e02400',  all social security (OASDI) benefits;
        'p22250',  short-term capital gains;
        'p23250',  long-term capital gains.
        """
        # check validity of income_type_str parameter
        if income_type_str not in Calculator.MTR_VALID_INCOME_TYPES:
            msg = 'mtr income_type_str="{}" is not valid'
            raise ValueError(msg.format(income_type_str))
        # specify value for finite_diff parameter
        finite_diff = 0.01  # a one-cent difference
        if negative_finite_diff:
            finite_diff *= -1.0
        # save records object in order to restore it after mtr computations
        recs0 = copy.deepcopy(self.records)
        # extract income_type array(s) from embedded records object
        income_type = getattr(self.records, income_type_str)
        if income_type_str == 'e00200p':
            earnings_type = self.records.e00200
        elif income_type_str == 'e00900p':
            seincome_type = self.records.e00900
        elif income_type_str == 'e00650':
            divincome_type = self.records.e00600
        elif income_type_str == 'e01700':
            penben_type = self.records.e01500
        # calculate level of taxes after a marginal increase in income
        setattr(self.records, income_type_str, income_type + finite_diff)
        if income_type_str == 'e00200p':
            self.records.e00200 = earnings_type + finite_diff
        elif income_type_str == 'e00900p':
            self.records.e00900 = seincome_type + finite_diff
        elif income_type_str == 'e00650':
            self.records.e00600 = divincome_type + finite_diff
        elif income_type_str == 'e01700':
            self.records.e01500 = penben_type + finite_diff
        if self.consumption.has_response():
            self.consumption.response(self.records, finite_diff)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        fica_chng = copy.deepcopy(self.records._fica)
        iitax_chng = copy.deepcopy(self.records._iitax)
        combined_taxes_chng = iitax_chng + fica_chng
        # calculate base level of taxes after restoring records object
        setattr(self, '_records', recs0)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        fica_base = copy.deepcopy(self.records._fica)
        iitax_base = copy.deepcopy(self.records._iitax)
        combined_taxes_base = iitax_base + fica_base
        # compute marginal changes in tax liability
        fica_diff = fica_chng - fica_base
        iitax_diff = iitax_chng - iitax_base
        combined_diff = combined_taxes_chng - combined_taxes_base
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        if wrt_full_compensation and income_type_str == 'e00200p':
            adj = np.where(income_type < self.policy.SS_Earnings_c,
                           0.5 * (self.policy.FICA_ss_trt +
                                  self.policy.FICA_mc_trt),
                           0.5 * self.policy.FICA_mc_trt)
        else:
            adj = 0.0
        # compute marginal tax rates
        mtr_fica = fica_diff / (finite_diff * (1.0 + adj))
        mtr_iit = iitax_diff / (finite_diff * (1.0 + adj))
        mtr_combined = combined_diff / (finite_diff * (1.0 + adj))
        # return the three marginal tax rate arrays
        return (mtr_fica, mtr_iit, mtr_combined)

    def current_law_version(self):
        """
        Return Calculator object same as self except with current-law policy.
        """
        clp = self._policy.current_law_version()
        recs = copy.deepcopy(self._records)
        behv = copy.deepcopy(self.behavior)
        grow = copy.deepcopy(self.growth)
        cons = copy.deepcopy(self.consumption)
        calc = Calculator(policy=clp, records=recs, sync_years=False,
                          behavior=behv, growth=grow, consumption=cons)
        return calc
