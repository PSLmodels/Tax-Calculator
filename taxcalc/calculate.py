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


import os
import json
import re
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
            self.policy = policy
        else:
            raise ValueError('must specify policy as a Policy object')
        if isinstance(records, Records):
            self.records = records
        else:
            raise ValueError('must specify records as a Records object')
        if behavior is None:
            self.behavior = Behavior(start_year=policy.start_year)
        elif isinstance(behavior, Behavior):
            self.behavior = behavior
            while self.behavior.current_year < self.policy.current_year:
                next_year = self.behavior.current_year + 1
                self.behavior.set_year(next_year)
        else:
            raise ValueError('behavior must be None or Behavior object')
        if growth is None:
            self.growth = Growth(start_year=policy.start_year)
        elif isinstance(growth, Growth):
            self.growth = growth
            while self.growth.current_year < self.policy.current_year:
                next_year = self.growth.current_year + 1
                self.growth.set_year(next_year)
        else:
            raise ValueError('growth must be None or Growth object')
        if consumption is None:
            self.consumption = Consumption(start_year=policy.start_year)
        elif isinstance(consumption, Consumption):
            self.consumption = consumption
            while self.consumption.current_year < self.policy.current_year:
                next_year = self.consumption.current_year + 1
                self.consumption.set_year(next_year)
        else:
            raise ValueError('consumption must be None or Consumption object')
        if sync_years and self.records.current_year == Records.PUF_YEAR:
            if verbose:
                print('You loaded data for ' +
                      str(self.records.current_year) + '.')
                if len(self.records.IGNORED_VARS) > 0:
                    print('Your data include the following unused ' +
                          'variables that will be ignored:')
                    for var in self.records.IGNORED_VARS:
                        print('  ' +
                              var)
            while self.records.current_year < self.policy.current_year:
                next_year = self.records.current_year + 1
                if next_year >= self.growth.start_year:
                    self.growth.set_year(next_year)
                    self.growth.apply_change(self.records)
                self.records.increment_year()
            if verbose:
                print('Your data have been extrapolated to ' +
                      str(self.records.current_year) + '.')
        assert self.policy.current_year == self.records.current_year

    def TaxInc_to_AMT(self):
        TaxInc(self.policy, self.records)
        SchXYZTax(self.policy, self.records)
        GainsTax(self.policy, self.records)
        AGIsurtax(self.policy, self.records)
        NetInvIncTax(self.policy, self.records)
        AMT(self.policy, self.records)

    def calc_one_year(self, zero_out_calc_vars=False):
        # calls all the functions except those in calc_all() function
        if zero_out_calc_vars:
            self.records.zero_out_changing_calculated_vars()
        # pdb.set_trace()
        EI_PayrollTax(self.policy, self.records)
        DependentCare(self.policy, self.records)
        Adj(self.policy, self.records)
        if self.policy.ALD_invinc_ec_base_code_active:
            ALD_invinc_ec_base_code(self)
        else:
            ALD_invinc_ec_base_nocode(self.policy, self.records)
        CapGains(self.policy, self.records)
        SSBenefits(self.policy, self.records)
        AGI(self.policy, self.records)
        ItemDed(self.policy, self.records)
        AdditionalMedicareTax(self.policy, self.records)
        StdDed(self.policy, self.records)
        # Store calculated standard deduction, calculate
        # taxes with standard deduction, store AMT + Regular Tax
        std = copy.deepcopy(self.records._standard)
        item = copy.deepcopy(self.records.c04470)
        item_no_limit = copy.deepcopy(self.records.c21060)
        self.records.c04470 = np.zeros(self.records.dim)
        self.records.c21060 = np.zeros(self.records.dim)
        self.TaxInc_to_AMT()
        std_taxes = copy.deepcopy(self.records.c05800)
        # Set standard deduction to zero, calculate taxes w/o
        # standard deduction, and store AMT + Regular Tax
        self.records._standard = np.zeros(self.records.dim)
        self.records.c21060 = item_no_limit
        self.records.c04470 = item
        self.TaxInc_to_AMT()
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
        self.TaxInc_to_AMT()
        F2441(self.policy, self.records)
        EITC(self.policy, self.records)
        ChildTaxCredit(self.policy, self.records)
        AmOppCreditParts(self.policy, self.records)
        SchR(self.policy, self.records)
        EducationTaxCredit(self.policy, self.records)
        NonrefundableCredits(self.policy, self.records)
        AdditionalCTC(self.policy, self.records)
        C1040(self.policy, self.records)
        if self.policy.CTC_new_code_active:
            CTC_new_code_function(self)
        IITAX(self.policy, self.records)

    def calc_all(self, zero_out_calc_vars=False):
        # conducts static analysis of Calculator object for current_year
        self.calc_one_year(zero_out_calc_vars)
        BenefitSurtax(self)
        BenefitLimitation(self)
        FairShareTax(self.policy, self.records)
        LumpSumTax(self.policy, self.records)
        ExpandIncome(self.policy, self.records)

    def increment_year(self):
        next_year = self.policy.current_year + 1
        self.growth.set_year(next_year)
        self.growth.apply_change(self.records)
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

    MTR_VALID_VARIABLES = ['e00200p', 'e00900p',
                           'e00300', 'e00400',
                           'e00600', 'e00650',
                           'e01400', 'e01700',
                           'e02000', 'e02400',
                           'p22250', 'p23250',
                           'e18500', 'e19200',
                           'e26270', 'e19800']

    def mtr(self, variable_str='e00200p',
            negative_finite_diff=False,
            zero_out_calculated_vars=False,
            wrt_full_compensation=True):
        """
        Calculates the marginal payroll, individual income, and combined
        tax rates for every tax filing unit.
          The marginal tax rates are approximated as the change in tax
        liability caused by a small increase (the finite_diff) in the variable
        specified by the variable_str divided by that small increase in the
        variable, when wrt_full_compensation is false.
          If wrt_full_compensation is true, then the marginal tax rates
        are computed as the change in tax liability divided by the change
        in total compensation caused by the small increase in the variable
        (where the change in total compensation is the sum of the small
        increase in the variable and any increase in the employer share of
        payroll taxes caused by the small increase in the variable).

        Parameters
        ----------
        variable_str: string
            specifies type of income or expense that is increased to compute
            the marginal tax rates.  See Notes for list of valid variables.

        negative_finite_diff: boolean
            specifies whether or not marginal tax rates are computed by
            subtracting (rather than adding) a small finite_diff amount
            to the specified variable.

        zero_out_calculated_vars: boolean
            specifies value of zero_out_calc_vars parameter used in calls
            of Calculator.calc_all() method.

        wrt_full_compensation: boolean
            specifies whether or not marginal tax rates on earned income
            are computed with respect to (wrt) changes in total compensation
            that includes the employer share of OASDI and HI payroll taxes.

        Returns
        -------
        mtr_payrolltax: an array of marginal payroll tax rates.
        mtr_incometax: an array of marginal individual income tax rates.
        mtr_combined: an array of marginal combined tax rates, which is
                      the sum of mtr_payrolltax and mtr_incometax.

        Notes
        -----
        Valid variable_str values are:
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
        'p23250',  long-term capital gains;
        'e18500',  Schedule A real-estate-tax deduction;
        'e19200',  Schedule A total-interest deduction;
        'e26270',  S-corporation/partnership income (also included in e02000);
        'e19800',  Charity cash contributions.
        """
        # check validity of variable_str parameter
        if variable_str not in Calculator.MTR_VALID_VARIABLES:
            msg = 'mtr variable_str="{}" is not valid'
            raise ValueError(msg.format(variable_str))
        # specify value for finite_diff parameter
        finite_diff = 0.01  # a one-cent difference
        if negative_finite_diff:
            finite_diff *= -1.0
        # save records object in order to restore it after mtr computations
        recs0 = copy.deepcopy(self.records)
        # extract variable array(s) from embedded records object
        variable = getattr(self.records, variable_str)
        if variable_str == 'e00200p':
            earnings_var = self.records.e00200
        elif variable_str == 'e00900p':
            seincome_var = self.records.e00900
        elif variable_str == 'e00650':
            divincome_var = self.records.e00600
        elif variable_str == 'e26270':
            schEincome_var = self.records.e02000
        # calculate level of taxes after a marginal increase in income
        setattr(self.records, variable_str, variable + finite_diff)
        if variable_str == 'e00200p':
            self.records.e00200 = earnings_var + finite_diff
        elif variable_str == 'e00900p':
            self.records.e00900 = seincome_var + finite_diff
        elif variable_str == 'e00650':
            self.records.e00600 = divincome_var + finite_diff
        elif variable_str == 'e26270':
            self.records.e02000 = schEincome_var + finite_diff
        if self.consumption.has_response():
            self.consumption.response(self.records, finite_diff)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_chng = copy.deepcopy(self.records._payrolltax)
        incometax_chng = copy.deepcopy(self.records._iitax)
        combined_taxes_chng = incometax_chng + payrolltax_chng
        # calculate base level of taxes after restoring records object
        setattr(self, 'records', recs0)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_base = copy.deepcopy(self.records._payrolltax)
        incometax_base = copy.deepcopy(self.records._iitax)
        combined_taxes_base = incometax_base + payrolltax_base
        # compute marginal changes in combined tax liability
        payrolltax_diff = payrolltax_chng - payrolltax_base
        incometax_diff = incometax_chng - incometax_base
        combined_diff = combined_taxes_chng - combined_taxes_base
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        if wrt_full_compensation and variable_str == 'e00200p':
            adj = np.where(variable < self.policy.SS_Earnings_c,
                           0.5 * (self.policy.FICA_ss_trt +
                                  self.policy.FICA_mc_trt),
                           0.5 * self.policy.FICA_mc_trt)
        else:
            adj = 0.0
        # compute marginal tax rates
        mtr_payrolltax = payrolltax_diff / (finite_diff * (1.0 + adj))
        mtr_incometax = incometax_diff / (finite_diff * (1.0 + adj))
        mtr_combined = combined_diff / (finite_diff * (1.0 + adj))
        # return the three marginal tax rate arrays
        return (mtr_payrolltax, mtr_incometax, mtr_combined)

    def current_law_version(self):
        """
        Return Calculator object same as self except with current-law policy.
        """
        clp = self.policy.current_law_version()
        recs = copy.deepcopy(self.records)
        behv = copy.deepcopy(self.behavior)
        grow = copy.deepcopy(self.growth)
        cons = copy.deepcopy(self.consumption)
        calc = Calculator(policy=clp, records=recs, sync_years=False,
                          behavior=behv, growth=grow, consumption=cons)
        return calc

    @staticmethod
    def read_json_reform_file(reform_filename):
        """
        Read JSON reform file and call Calculator.read_json_reform_text method.
        """
        if os.path.isfile(reform_filename):
            txt = open(reform_filename, 'r').read()
            return Calculator.read_json_reform_text(txt)
        else:
            msg = 'reform file {} could not be found'
            raise ValueError(msg.format(reform_filename))

    @staticmethod
    def read_json_reform_text(text_string):
        """
        Strip //-comments from text_string and return 4 dict based on the JSON.
        The reform text is JSON with four high-level string:object pairs:
           a "policy": {...} pair,
           a "behavior": {...} pair,
           a "growth": {...} pair, and
           a "consumption": {...} pair.
           In all four cases the {...} object may be empty (that is, be {}),
           or may contain one or more pairs with parameter string primary keys
           and string years as secondary keys.  See tests/test_calculate.py for
           an extended example of a commented JSON reform text that can be read
           by this method.  Note that parameter code in the policy object is
           enclosed inside a pair of double pipe characters (||) as shown
           in the REFORM_CONTENTS string in the tests/test_calculate.py file.
        Returned dictionaries (reform_policy, reform_behavior,
                               reform_growth reform_consumption)
           have integer years as primary keys
           and string parameters as secondary keys.
        The returned dictionaries are suitable as the argument to
           the Policy implement_reform(reform_policy) method, or
           the Behavior update_behavior(reform_behavior) method, or
           the Growth update_growth(reform_growth) method, or
           the Consumption update_consumption(reform_consumption) method.
        """
        # strip out //-comments without changing line numbers
        json_without_comments = re.sub('//.*', ' ', text_string)
        # convert multi-line string between pairs of || into a simple string

        def repl(mat):
            code = mat.group(2).replace('\r', '\\r').replace('\n', '\\n')
            return '"' + code + '"'

        json_str = re.sub('(\|\|)(.*?)(\|\|)',  # pylint: disable=W1401
                          repl, json_without_comments, flags=re.DOTALL)
        # convert JSON text into a Python dictionary
        try:
            raw_dict = json.loads(json_str)
        except ValueError as valerr:
            msg = 'Policy reform text below contains invalid JSON:\n'
            msg += str(valerr) + '\n'
            msg += 'Above location of the first error may be approximate.\n'
            msg += 'The invalid JSON reform text is between the lines:\n'
            bline = 'XX----.----1----.----2----.----3----.----4'
            bline += '----.----5----.----6----.----7'
            msg += bline + '\n'
            linenum = 0
            for line in json_str.split('\n'):
                linenum += 1
                msg += '{:02d}{}'.format(linenum, line) + '\n'
            msg += bline + '\n'
            raise ValueError(msg)
        # check contents of dictionary
        expect_keys = set(['policy', 'behavior', 'growth', 'consumption'])
        actual_keys = set(raw_dict.keys())
        if actual_keys != expect_keys:
            msg = 'reform keys {} not equal to {}'
            raise ValueError(msg.format(actual_keys, expect_keys))
        # handle special param_code key in raw_dict policy component dictionary
        paramcode = raw_dict['policy'].pop('param_code', None)
        if paramcode:
            if Policy.PROHIBIT_PARAM_CODE:
                msg = 'JSON reform file containing "param_code" is not allowed'
                raise ValueError(msg)
            for param, code in paramcode.items():
                raw_dict['policy'][param] = {'0': code}
        # convert raw_dict component dictionaries
        pol_dict = Calculator.convert_reform_dict(raw_dict['policy'])
        beh_dict = Calculator.convert_reform_dict(raw_dict['behavior'])
        gro_dict = Calculator.convert_reform_dict(raw_dict['growth'])
        con_dict = Calculator.convert_reform_dict(raw_dict['consumption'])
        return (pol_dict, beh_dict, gro_dict, con_dict)

    @staticmethod
    def convert_reform_dict(param_key_dict):
        """
        Converts specified param_key_dict into a dictionary whose primary
          keys are calendary years, and hence, is suitable as the argument to
          the Policy implement_reform(reform_policy) method, or
          the Behavior update_behavior(reform_behavior) method, or
          the Growth update_growth(reform_growth) method, or
          the Consumption update_consumption(reform_consumption) method.
        Specified input dictionary has string parameter primary keys and
           string years as secondary keys.
        Returned dictionary has integer years as primary keys and
           string parameters as secondary keys.
        """
        # convert year skey strings to integers and lists into np.arrays
        reform_pkey_param = {}
        for pkey, sdict in param_key_dict.items():
            if not isinstance(pkey, six.string_types):
                msg = 'pkey {} in reform is not a string'
                raise ValueError(msg.format(pkey))
            rdict = {}
            if not isinstance(sdict, dict):
                msg = 'pkey {} in reform is not paired with a dict'
                raise ValueError(msg.format(pkey))
            for skey, val in sdict.items():
                if not isinstance(skey, six.string_types):
                    msg = 'skey {} in reform is not a string'
                    raise ValueError(msg.format(skey))
                else:
                    year = int(skey)
                rdict[year] = (np.array(val)
                               if isinstance(val, list) else val)
            reform_pkey_param[pkey] = rdict
        # convert reform_pkey_param dictionary to reform_pkey_year dictionary
        years = set()
        reform_pkey_year = dict()
        for param, sdict in reform_pkey_param.items():
            for year, val in sdict.items():
                if year not in years:
                    years.add(year)
                    reform_pkey_year[year] = {}
                reform_pkey_year[year][param] = val
        return reform_pkey_year
