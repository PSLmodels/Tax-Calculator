"""
Tax-Calculator federal tax Calculator class.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 calculate.py
# pylint --disable=locally-disabled calculate.py
#
# pylint: disable=invalid-name,no-value-for-parameter,too-many-lines

import os
import json
import re
import copy
import six
import numpy as np
import pandas as pd
from taxcalc.functions import (TaxInc, SchXYZTax, GainsTax, AGIsurtax,
                               NetInvIncTax, AMT, EI_PayrollTax, Adj,
                               DependentCare, ALD_InvInc_ec_base, CapGains,
                               SSBenefits, UBI, AGI, ItemDedCap, ItemDed,
                               StdDed, AdditionalMedicareTax, F2441, EITC,
                               SchR, ChildTaxCredit, AdditionalCTC, CTC_new,
                               PersonalTaxCredit,
                               AmOppCreditParts, EducationTaxCredit,
                               NonrefundableCredits, C1040, IITAX,
                               BenefitSurtax, BenefitLimitation,
                               FairShareTax, LumpSumTax, BenefitPrograms,
                               ExpandIncome, AfterTaxIncome)
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.consumption import Consumption
from taxcalc.behavior import Behavior
from taxcalc.growdiff import Growdiff
from taxcalc.growfactors import Growfactors
from taxcalc.utils import (DIST_VARIABLES, create_distribution_table,
                           DIFF_VARIABLES, create_difference_table,
                           create_diagnostic_table,
                           ce_aftertax_expanded_income,
                           mtr_graph_data, atr_graph_data, xtr_graph_plot,
                           dec_graph_data, dec_graph_plot,
                           qin_graph_data, qin_graph_plot)
# import pdb


class Calculator(object):
    """
    Constructor for the Calculator class.

    Parameters
    ----------
    policy: Policy class object
        this argument must be specified and object is copied for internal use

    records: Records class object
        this argument must be specified and object is copied for internal use

    verbose: boolean
        specifies whether or not to write to stdout data-loaded and
        data-extrapolated progress reports; default value is true.

    sync_years: boolean
        specifies whether or not to synchronize policy year and records year;
        default value is true.

    consumption: Consumption class object
        specifies consumption response assumptions used to calculate
        "effective" marginal tax rates; default is None, which implies
        no consumption responses assumed in marginal tax rate calculations;
        when argument is an object it is copied for internal use;
        also specifies consumption value of in-kind benefis with no in-kind
        consumption values specified implying consumption value is equal to
        government cost of providing the in-kind benefits

    behavior: Behavior class object
        specifies behavioral responses used by Calculator; default is None,
        which implies no behavioral responses to policy reform;
        when argument is an object it is copied for internal use

    Raises
    ------
    ValueError:
        if parameters are not the appropriate type.

    Returns
    -------
    class instance: Calculator

    Notes
    -----
    The most efficient way to specify current-law and reform Calculator
    objects is as follows:
         pol = Policy()
         rec = Records()
         calc1 = Calculator(policy=pol, records=rec)  # current-law
         pol.implement_reform(...)
         calc2 = Calculator(policy=pol, records=rec)  # reform
    All calculations are done on the internal copies of the Policy and
    Records objects passed to each of the two Calculator constructors.
    """
    # pylint: disable=too-many-public-methods

    def __init__(self, policy=None, records=None, verbose=True,
                 sync_years=True, consumption=None, behavior=None):
        # pylint: disable=too-many-arguments,too-many-branches
        if isinstance(policy, Policy):
            self.__policy = copy.deepcopy(policy)
        else:
            raise ValueError('must specify policy as a Policy object')
        if isinstance(records, Records):
            self.__records = copy.deepcopy(records)
        else:
            raise ValueError('must specify records as a Records object')
        if self.__policy.current_year < self.__records.data_year:
            self.__policy.set_year(self.__records.data_year)
        if consumption is None:
            self.__consumption = Consumption(start_year=policy.start_year)
        elif isinstance(consumption, Consumption):
            self.__consumption = copy.deepcopy(consumption)
            while self.__consumption.current_year < self.__policy.current_year:
                next_year = self.__consumption.current_year + 1
                self.__consumption.set_year(next_year)
        else:
            raise ValueError('consumption must be None or Consumption object')
        if behavior is None:
            self.__behavior = Behavior(start_year=policy.start_year)
        elif isinstance(behavior, Behavior):
            self.__behavior = copy.deepcopy(behavior)
            while self.__behavior.current_year < self.__policy.current_year:
                next_year = self.__behavior.current_year + 1
                self.__behavior.set_year(next_year)
        else:
            raise ValueError('behavior must be None or Behavior object')
        current_year_is_data_year = (
            self.__records.current_year == self.__records.data_year)
        if sync_years and current_year_is_data_year:
            if verbose:
                print('You loaded data for ' +
                      str(self.__records.data_year) + '.')
                if self.__records.IGNORED_VARS:
                    print('Your data include the following unused ' +
                          'variables that will be ignored:')
                    for var in self.__records.IGNORED_VARS:
                        print('  ' +
                              var)
            while self.__records.current_year < self.__policy.current_year:
                self.__records.increment_year()
            if verbose:
                print('Tax-Calculator startup automatically ' +
                      'extrapolated your data to ' +
                      str(self.__records.current_year) + '.')
        assert self.__policy.current_year == self.__records.current_year
        self.__stored_records = None

    def increment_year(self):
        """
        Advance all embedded objects to next year.
        """
        next_year = self.__policy.current_year + 1
        self.__records.increment_year()
        self.__policy.set_year(next_year)
        self.__consumption.set_year(next_year)
        self.__behavior.set_year(next_year)

    def advance_to_year(self, year):
        """
        The advance_to_year function gives an optional way of implementing
        increment year functionality by immediately specifying the year
        as input.  New year must be at least the current year.
        """
        iteration = year - self.current_year
        if iteration < 0:
            raise ValueError('New current year must be ' +
                             'greater than current year!')
        for _ in range(iteration):
            self.increment_year()
        assert self.current_year == year

    def calc_all(self, zero_out_calc_vars=False):
        """
        Call all tax-calculation functions for the current_year.
        """
        # conducts static analysis of Calculator object for current_year
        assert self.__records.current_year == self.__policy.current_year
        BenefitPrograms(self)
        self._calc_one_year(zero_out_calc_vars)
        BenefitSurtax(self)
        BenefitLimitation(self)
        FairShareTax(self.__policy, self.__records)
        LumpSumTax(self.__policy, self.__records)
        ExpandIncome(self.__policy, self.__records)
        AfterTaxIncome(self.__policy, self.__records)

    def weighted_total(self, variable_name):
        """
        Return all-filing-unit weighted total of named Records variable.
        """
        return (self.array(variable_name) * self.array('s006')).sum()

    def total_weight(self):
        """
        Return all-filing-unit total of sampling weights.
        NOTE: var_weighted_mean = calc.weighted_total(var)/calc.total_weight()
        """
        return self.array('s006').sum()

    def dataframe(self, variable_list):
        """
        Return pandas DataFrame containing the listed variables from embedded
        Records object.
        """
        assert isinstance(variable_list, list)
        arys = [self.array(vname) for vname in variable_list]
        return pd.DataFrame(data=np.column_stack(arys), columns=variable_list)

    def array(self, variable_name, variable_value=None):
        """
        If variable_value is None, return numpy ndarray containing the
         named variable in embedded Records object.
        If variable_value is not None, set named variable in embedded Records
         object to specified variable_value.
        """
        if variable_value is None:
            return getattr(self.__records, variable_name)
        else:
            assert isinstance(variable_value, np.ndarray)
            setattr(self.__records, variable_name, variable_value)

    def incarray(self, variable_name, variable_add):
        """
        Add variable_add to named variable in embedded Records object.
        """
        assert isinstance(variable_add, np.ndarray)
        setattr(self.__records, variable_name,
                self.array(variable_name) + variable_add)

    def zeroarray(self, variable_name):
        """
        Set named variable in embedded Records object to zeros.
        """
        setattr(self.__records, variable_name, np.zeros(self.array_len))

    def store_records(self):
        """
        Make internal copy of embedded Records object that can then be
        restored after interim calculations that make temporary changes
        to the embedded Records object.
        """
        assert self.__stored_records is None
        self.__stored_records = copy.deepcopy(self.__records)

    def restore_records(self):
        """
        Set the embedded Records object to the stored Records object
        that was saved in the last call to the store_records() method.
        """
        assert isinstance(self.__stored_records, Records)
        self.__records = copy.deepcopy(self.__stored_records)
        self.__stored_records = None

    def records_current_year(self, year=None):
        """
        If year is None, return current_year of embedded Records object.
        If year is not None, set embedded Records current_year to year.
        """
        if year is None:
            return self.__records.current_year
        else:
            assert isinstance(year, int)
            self.__records.set_current_year(year)

    @property
    def array_len(self):
        """
        Length of arrays in embedded Records object.
        """
        return self.__records.array_length

    def param(self, param_name, param_value=None):
        """
        If param_value is None, return named parameter in
         embedded Policy object.
        If param_value is not None, set named parameter in
         embedded Policy object to specified param_value.
        """
        if param_value is None:
            return getattr(self.__policy, param_name)
        else:
            setattr(self.__policy, param_name, param_value)

    def consump_param(self, param_name):
        """
        Return value of named parameter in embedded Consumption object.
        """
        return getattr(self.__consumption, param_name)

    def behavior_has_response(self):
        """
        Return True if embedded Behavior object has response;
        otherwise return False.
        """
        return self.__behavior.has_response()

    def behavior(self, param_name, param_value=None):
        """
        If param_value is None, return named parameter in
         embedded Behavior object.
        If param_value is not None, set named parameter in
         embedded Behavior object to specified param_value.
        """
        if param_value is None:
            return getattr(self.__behavior, param_name)
        else:
            setattr(self.__behavior, param_name, param_value)

    def records_include_behavioral_responses(self):
        """
        Mark embedded Records object as including behavioral responses
        """
        self.__records.behavioral_responses_are_included = True

    @property
    def reform_warnings(self):
        """
        Calculator class embedded Policy object's reform_warnings.
        """
        return self.__policy.reform_warnings

    def policy_current_year(self, year=None):
        """
        If year is None, return current_year of embedded Policy object.
        If year is not None, set embedded Policy current_year to year.
        """
        if year is None:
            return self.__policy.current_year
        else:
            assert isinstance(year, int)
            self.__policy.set_year(year)

    @property
    def current_year(self):
        """
        Calculator class current calendar year property.
        """
        return self.__policy.current_year

    @property
    def data_year(self):
        """
        Calculator class initial (i.e., first) records data year property.
        """
        return self.__records.data_year

    def diagnostic_table(self, num_years):
        """
        Generate multi-year diagnostic table;
        this method leaves the Calculator object unchanged.

        Parameters
        ----------
        num_years : Integer
            number of years to include in diagnostic table starting
            with the Calculator object's current_year (must be at least
            one and no more than what would exceed Policy end_year)

        Returns
        -------
        Pandas DataFrame object containing the multi-year diagnostic table
        """
        assert num_years >= 1
        max_num_years = self.__policy.end_year - self.__policy.current_year + 1
        assert num_years <= max_num_years
        calc = copy.deepcopy(self)
        tlist = list()
        for iyr in range(1, num_years + 1):
            assert calc.behavior_has_response() is False
            calc.calc_all()
            diag = create_diagnostic_table(calc.dataframe(DIST_VARIABLES),
                                           calc.current_year)
            tlist.append(diag)
            if iyr < num_years:
                calc.increment_year()
        return pd.concat(tlist, axis=1)

    def distribution_tables(self, calc,
                            groupby='weighted_deciles',
                            income_measure='expanded_income',
                            result_type='weighted_sum'):
        """
        Get results from self and calc, sort them based on groupby using
        income_measure, manipulate grouped statistics based on result_type,
        and return tables as a pair of Pandas dataframes.
        Note that the returned tables have consistent income groups (based
        on the self income_measure) even though the income_measure in self
        and the income_measure in calc are different.

        Parameters
        ----------
        calc : Calculator object or None
            typically represents the reform while self represents the baseline;
            if calc is None, the second returned table is None

        groupby : String object
            options for input: 'weighted_deciles', 'webapp_income_bins',
                               'large_income_bins', 'small_income_bins';
            determines how the columns in returned tables are sorted
        NOTE: when groupby is 'weighted_deciles', the returned table has three
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent).

        income_measure : String object
            options for input: 'expanded_income' or 'c00100'(AGI)

        result_type : String object
            options for input: 'weighted_sum' or 'weighted_avg';
            determines how whether or not table entries are averages or totals

        Typical usage
        -------------
        dist1, dist2 = calc1.distribution_tables(calc2)
        OR
        dist1, _ = calc1.distribution_tables(None)
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object)
        """
        # nested function used only by this method
        def have_same_income_measure(calc1, calc2, income_measure):
            """
            Return true if calc1 and calc2 contain the same income_measure;
            otherwise, return false.  (Note that "same" means nobody's
            income_measure differs by more than one cent.)
            """
            im1 = calc1.array(income_measure)
            im2 = calc2.array(income_measure)
            return np.allclose(im1, im2, rtol=0.0, atol=0.01)
        # main logic of method
        assert calc is None or isinstance(calc, Calculator)
        assert (groupby == 'weighted_deciles' or
                groupby == 'webapp_income_bins' or
                groupby == 'large_income_bins' or
                groupby == 'small_income_bins')
        assert (income_measure == 'expanded_income' or
                income_measure == 'c00100')
        assert (result_type == 'weighted_sum' or
                result_type == 'weighted_avg')
        dt1 = create_distribution_table(self.dataframe(DIST_VARIABLES),
                                        groupby=groupby,
                                        income_measure=income_measure,
                                        result_type=result_type)
        if calc is None:
            dt2 = None
        else:
            assert calc.current_year == self.current_year
            assert calc.array_len == self.array_len
            var_dataframe = calc.dataframe(DIST_VARIABLES)
            if have_same_income_measure(self, calc, income_measure):
                imeasure = income_measure
            else:
                imeasure = income_measure + '_baseline'
                var_dataframe[imeasure] = self.array(income_measure)
            dt2 = create_distribution_table(var_dataframe,
                                            groupby=groupby,
                                            income_measure=imeasure,
                                            result_type=result_type)
        return dt1, dt2

    def difference_table(self, calc,
                         groupby='weighted_deciles',
                         income_measure='expanded_income',
                         tax_to_diff='combined'):
        """
        Get results from self and calc, sort them based on groupby using
        income_measure, and return tax-difference table as a Pandas dataframe.

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline

        groupby : String object
            options for input: 'weighted_deciles', 'webapp_income_bins',
                               'large_income_bins', 'small_income_bins';
            determines how the columns in returned tables are sorted
        NOTE: when groupby is 'weighted_deciles', the returned table has three
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent).

        income_measure : String object
            options for input: 'expanded_income' or 'c00100'(AGI)

        tax_to_diff : String object
            options for input: 'iitax', 'payrolltax', 'combined'
            specifies which tax to difference

        Typical usage
        -------------
        diff = calc1.difference_table(calc2)
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object)
        """
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        diff = create_difference_table(self.dataframe(DIFF_VARIABLES),
                                       calc.dataframe(DIFF_VARIABLES),
                                       groupby=groupby,
                                       income_measure=income_measure,
                                       tax_to_diff=tax_to_diff)
        return diff

    MTR_VALID_VARIABLES = ['e00200p', 'e00200s',
                           'e00900p', 'e00300',
                           'e00400', 'e00600',
                           'e00650', 'e01400',
                           'e01700', 'e02000',
                           'e02400', 'p22250',
                           'p23250', 'e18500',
                           'e19200', 'e26270',
                           'e19800', 'e20100']

    def mtr(self, variable_str='e00200p',
            negative_finite_diff=False,
            zero_out_calculated_vars=False,
            calc_all_already_called=False,
            wrt_full_compensation=True):
        """
        Calculates the marginal payroll, individual income, and combined
        tax rates for every tax filing unit, leaving the Calculator object
        in exactly the same state as it would be in after a calc_all() call.

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

        If using 'e00200s' as variable_str, the marginal tax rate for all
        records where MARS != 2 will be missing.  If you want to perform a
        function such as np.mean() on the returned arrays, you will need to
        account for this.

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

        calc_all_already_called: boolean
            specifies whether self has already had its Calculor.calc_all()
            method called, in which case this method will not do a final
            calc_all() call but use the incoming embedded Records object
            as the outgoing Records object embedding in self.

        wrt_full_compensation: boolean
            specifies whether or not marginal tax rates on earned income
            are computed with respect to (wrt) changes in total compensation
            that includes the employer share of OASDI and HI payroll taxes.

        Returns
        -------
        A tuple of numpy arrays in the following order:
        mtr_payrolltax: an array of marginal payroll tax rates.
        mtr_incometax: an array of marginal individual income tax rates.
        mtr_combined: an array of marginal combined tax rates, which is
                      the sum of mtr_payrolltax and mtr_incometax.

        Notes
        -----
        The arguments zero_out_calculated_vars and calc_all_already_called
        cannot both be true.

        Valid variable_str values are:
        'e00200p', taxpayer wage/salary earnings (also included in e00200);
        'e00200s', spouse wage/salary earnings (also included in e00200);
        'e00900p', taxpayer Schedule C self-employment income (also in e00900);
        'e00300',  taxable interest income;
        'e00400',  federally-tax-exempt interest income;
        'e00600',  all dividends included in AGI
        'e00650',  qualified dividends (also included in e00600)
        'e01400',  federally-taxable IRA distribution;
        'e01700',  federally-taxable pension benefits;
        'e02000',  Schedule E total net income/loss
        'e02400',  all social security (OASDI) benefits;
        'p22250',  short-term capital gains;
        'p23250',  long-term capital gains;
        'e18500',  Schedule A real-estate-tax paid;
        'e19200',  Schedule A interest paid;
        'e26270',  S-corporation/partnership income (also included in e02000);
        'e19800',  Charity cash contributions;
        'e20100',  Charity non-cash contributions.
        """
        # pylint: disable=too-many-arguments,too-many-statements
        # pylint: disable=too-many-locals,too-many-branches
        assert not zero_out_calculated_vars or not calc_all_already_called
        # check validity of variable_str parameter
        if variable_str not in Calculator.MTR_VALID_VARIABLES:
            msg = 'mtr variable_str="{}" is not valid'
            raise ValueError(msg.format(variable_str))
        # specify value for finite_diff parameter
        finite_diff = 0.01  # a one-cent difference
        if negative_finite_diff:
            finite_diff *= -1.0
        # remember records object in order to restore it after mtr computations
        self.store_records()
        # extract variable array(s) from embedded records object
        variable = self.array(variable_str)
        if variable_str == 'e00200p':
            earnings_var = self.array('e00200')
        elif variable_str == 'e00200s':
            earnings_var = self.array('e00200')
        elif variable_str == 'e00900p':
            seincome_var = self.array('e00900')
        elif variable_str == 'e00650':
            divincome_var = self.array('e00600')
        elif variable_str == 'e26270':
            schEincome_var = self.array('e02000')
        # calculate level of taxes after a marginal increase in income
        self.array(variable_str, variable + finite_diff)
        if variable_str == 'e00200p':
            self.array('e00200', earnings_var + finite_diff)
        elif variable_str == 'e00200s':
            self.array('e00200', earnings_var + finite_diff)
        elif variable_str == 'e00900p':
            self.array('e00900', seincome_var + finite_diff)
        elif variable_str == 'e00650':
            self.array('e00600', divincome_var + finite_diff)
        elif variable_str == 'e26270':
            self.array('e02000', schEincome_var + finite_diff)
        if self.__consumption.has_response():
            self.__consumption.response(self.__records, finite_diff)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_chng = self.array('payrolltax')
        incometax_chng = self.array('iitax')
        combined_taxes_chng = incometax_chng + payrolltax_chng
        # calculate base level of taxes after restoring records object
        self.restore_records()
        if not calc_all_already_called or zero_out_calculated_vars:
            self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_base = self.array('payrolltax')
        incometax_base = self.array('iitax')
        combined_taxes_base = incometax_base + payrolltax_base
        # compute marginal changes in combined tax liability
        payrolltax_diff = payrolltax_chng - payrolltax_base
        incometax_diff = incometax_chng - incometax_base
        combined_diff = combined_taxes_chng - combined_taxes_base
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        mtr_on_earnings = (variable_str == 'e00200p' or
                           variable_str == 'e00200s')
        if wrt_full_compensation and mtr_on_earnings:
            adj = np.where(variable < self.param('SS_Earnings_c'),
                           0.5 * (self.param('FICA_ss_trt') +
                                  self.param('FICA_mc_trt')),
                           0.5 * self.param('FICA_mc_trt'))
        else:
            adj = 0.0
        # compute marginal tax rates
        mtr_payrolltax = payrolltax_diff / (finite_diff * (1.0 + adj))
        mtr_incometax = incometax_diff / (finite_diff * (1.0 + adj))
        mtr_combined = combined_diff / (finite_diff * (1.0 + adj))
        # if variable_str is e00200s, set MTR to NaN for units without a spouse
        if variable_str == 'e00200s':
            mars = self.array('MARS')
            mtr_payrolltax = np.where(mars == 2, mtr_payrolltax, np.nan)
            mtr_incometax = np.where(mars == 2, mtr_incometax, np.nan)
            mtr_combined = np.where(mars == 2, mtr_combined, np.nan)
        # return the three marginal tax rate arrays
        return (mtr_payrolltax, mtr_incometax, mtr_combined)

    def mtr_graph(self, calc,
                  mars='ALL',
                  mtr_measure='combined',
                  mtr_variable='e00200p',
                  alt_e00200p_text='',
                  mtr_wrt_full_compen=False,
                  income_measure='expanded_income',
                  dollar_weighting=False):
        """
        Create marginal tax rate graph that can be written to an HTML
        file (using the write_graph_file utility function) or shown on
        the screen immediately in an interactive or notebook session
        (following the instructions in the documentation of the
        xtr_graph_plot utility function).

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline

        mars : integer or string
            specifies which filing status subgroup to show in the graph

            - 'ALL': include all filing units in sample

            - 1: include only single filing units

            - 2: include only married-filing-jointly filing units

            - 3: include only married-filing-separately filing units

            - 4: include only head-of-household filing units

        mtr_measure : string
            specifies which marginal tax rate to show on graph's y axis

            - 'itax': marginal individual income tax rate

            - 'ptax': marginal payroll tax rate

            - 'combined': sum of marginal income and payroll tax rates

        mtr_variable : string
            any string in the Calculator.VALID_MTR_VARS set
            specifies variable to change in order to compute marginal tax rates

        alt_e00200p_text : string
            text to use in place of mtr_variable
            when mtr_variable is 'e00200p';
            if empty string then use 'e00200p'

        mtr_wrt_full_compen : boolean
            see documentation of Calculator.mtr()
            argument wrt_full_compensation
            (value has an effect only if mtr_variable is 'e00200p')

        income_measure : string
            specifies which income variable to show on the graph's x axis

            - 'wages': wage and salary income (e00200)

            - 'agi': adjusted gross income, AGI (c00100)

            - 'expanded_income': sum of AGI, non-taxable interest income,
              non-taxable social security benefits, and employer share of
              FICA taxes.

        dollar_weighting : boolean
            False implies both income_measure percentiles on x axis
            and mtr values for each percentile on the y axis are
            computed without using dollar income_measure weights (just
            sampling weights); True implies both income_measure
            percentiles on x axis and mtr values for each percentile
            on the y axis are computed using dollar income_measure
            weights (in addition to sampling weights).  Specifying
            True produces a graph x axis that shows income_measure
            (not filing unit) percentiles.

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # pylint: disable=too-many-arguments,too-many-locals
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        # check validity of mars parameter
        assert mars == 'ALL' or (mars >= 1 and mars <= 4)
        # check validity of income_measure
        assert (income_measure == 'expanded_income' or
                income_measure == 'agi' or
                income_measure == 'wages')
        if income_measure == 'expanded_income':
            income_variable = 'expanded_income'
        elif income_measure == 'agi':
            income_variable = 'c00100'
        elif income_measure == 'wages':
            income_variable = 'e00200'
        # check validity of mtr_measure parameter
        assert (mtr_measure == 'combined' or
                mtr_measure == 'itax' or
                mtr_measure == 'ptax')
        # calculate marginal tax rates
        (mtr1_ptax, mtr1_itax,
         mtr1_combined) = self.mtr(variable_str=mtr_variable,
                                   wrt_full_compensation=mtr_wrt_full_compen)
        (mtr2_ptax, mtr2_itax,
         mtr2_combined) = calc.mtr(variable_str=mtr_variable,
                                   wrt_full_compensation=mtr_wrt_full_compen)
        if mtr_measure == 'combined':
            mtr1 = mtr1_combined
            mtr2 = mtr2_combined
        elif mtr_measure == 'itax':
            mtr1 = mtr1_itax
            mtr2 = mtr2_itax
        elif mtr_measure == 'ptax':
            mtr1 = mtr1_ptax
            mtr2 = mtr2_ptax
        # extract datafames needed by mtr_graph_data utility function
        record_variables = ['s006']
        if mars != 'ALL':
            record_variables.append('MARS')
        record_variables.append(income_variable)
        vdf = self.dataframe(record_variables)
        vdf['mtr1'] = mtr1
        vdf['mtr2'] = mtr2
        # select filing-status subgroup, if any
        if mars != 'ALL':
            vdf = vdf[vdf['MARS'] == mars]
        # construct data for graph
        data = mtr_graph_data(vdf,
                              year=self.current_year,
                              mars=mars,
                              mtr_measure=mtr_measure,
                              alt_e00200p_text=alt_e00200p_text,
                              mtr_wrt_full_compen=mtr_wrt_full_compen,
                              income_measure=income_measure,
                              dollar_weighting=dollar_weighting)
        # construct figure from data
        fig = xtr_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='',
                             legendloc='bottom_right')
        return fig

    def atr_graph(self, calc,
                  mars='ALL',
                  atr_measure='combined',
                  min_avginc=1000):
        """
        Create average tax rate graph that can be written to an HTML
        file (using the write_graph_file utility function) or shown on
        the screen immediately in an interactive or notebook session
        (following the instructions in the documentation of the
        xtr_graph_plot utility function).  The graph shows the mean
        average tax rate for each expanded-income percentile.

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline,
            where both self and calc have calculated taxes for this year
            before being used by this method

        mars : integer or string
            specifies which filing status subgroup to show in the graph

            - 'ALL': include all filing units in sample

            - 1: include only single filing units

            - 2: include only married-filing-jointly filing units

            - 3: include only married-filing-separately filing units

            - 4: include only head-of-household filing units

        atr_measure : string
            specifies which average tax rate to show on graph's y axis

            - 'itax': average individual income tax rate

            - 'ptax': average payroll tax rate

            - 'combined': sum of average income and payroll tax rates

        min_avginc : float
            specifies the minimum average expanded income for a percentile to
            be included in the graph data; value must be positive

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        # check validity of function arguments
        assert mars == 'ALL' or (mars >= 1 and mars <= 4)
        assert (atr_measure == 'combined' or
                atr_measure == 'itax' or
                atr_measure == 'ptax')
        assert min_avginc > 0
        # extract needed output that is assumed unchanged by reform from self
        record_variables = ['s006']
        if mars != 'ALL':
            record_variables.append('MARS')
        record_variables.append('expanded_income')
        vdf = self.dataframe(record_variables)
        # create 'tax1' and 'tax2' columns given specified atr_measure
        if atr_measure == 'combined':
            vdf['tax1'] = self.array('combined')
            vdf['tax2'] = calc.array('combined')
        elif atr_measure == 'itax':
            vdf['tax1'] = self.array('iitax')
            vdf['tax2'] = calc.array('iitax')
        elif atr_measure == 'ptax':
            vdf['tax1'] = self.array('payrolltax')
            vdf['tax2'] = calc.array('payrolltax')
        # select filing-status subgroup, if any
        if mars != 'ALL':
            vdf = vdf[vdf['MARS'] == mars]
        # construct data for graph
        data = atr_graph_data(vdf,
                              year=self.current_year,
                              mars=mars,
                              atr_measure=atr_measure,
                              min_avginc=min_avginc)
        # construct figure from data
        fig = xtr_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='',
                             legendloc='bottom_right')
        return fig

    def decile_graph(self, calc):
        """
        Create graph that shows percentage change in aftertax expanded
        income (from going from policy in self to policy in calc) for
        each expanded-income decile and subgroups of the top decile.
        The graph can be written to an HTML file (using the
        write_graph_file utility function) or shown on the screen
        immediately in an interactive or notebook session (following
        the instructions in the documentation of the xtr_graph_plot
        utility function).

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline,
            where both self and calc have calculated taxes for this year
            before being used by this method

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        diff_table = self.difference_table(calc,
                                           groupby='weighted_deciles',
                                           income_measure='expanded_income',
                                           tax_to_diff='combined')
        # construct data for graph
        data = dec_graph_data(diff_table, year=self.current_year)
        # construct figure from data
        fig = dec_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='')
        return fig

    def quintile_graph(self, calc):
        """
        Create graph that shows percentage change in aftertax expanded
        income (from going from policy in self to policy in calc) for
        each expanded-income quintile and subgroups of the top quintile.
        The graph can be written to an HTML file (using the
        write_graph_file utility function) or shown on the screen
        immediately in an interactive or notebook session (following
        the instructions in the documentation of the xtr_graph_plot
        utility function).

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline,
            where both self and calc have calculated taxes for this year
            before being used by this method

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        diff_table = self.difference_table(calc,
                                           groupby='weighted_deciles',
                                           income_measure='expanded_income',
                                           tax_to_diff='combined')
        # construct data for graph
        data = qin_graph_data(diff_table, year=self.current_year)
        # construct figure from data
        fig = qin_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='')
        return fig

    @staticmethod
    def read_json_param_objects(reform, assump):
        """
        Read JSON reform and assump objects and
        return a single dictionary containing five key:dict pairs:
        'policy':dict, 'consumption':dict, 'behavior':dict,
        'growdiff_baseline':dict and 'growdiff_response':dict.

        Note that either of the first two parameters may be None.
        If reform is None, the dict in the 'policy':dict pair is empty.
        If assump is None, the dict in the 'consumption':dict pair,
        in the 'behavior':dict pair, in the 'growdiff_baseline':dict pair,
        and in the 'growdiff_response':dict pair, are all empty.

        Also note that either of the first two parameters can be strings
        containing a valid JSON string (rather than a filename),
        in which case the file reading is skipped and the appropriate
        read_json_*_text method is called.

        The reform file contents or JSON string must be like this:
        {"policy": {...}}
        and the assump file contents or JSON string must be like:
        {"consumption": {...},
         "behavior": {...},
         "growdiff_baseline": {...},
         "growdiff_response": {...}
        }

        The returned dictionary contains parameter lists (not arrays).
        """
        # first process second assump parameter
        if assump is None:
            cons_dict = dict()
            behv_dict = dict()
            gdiff_base_dict = dict()
            gdiff_resp_dict = dict()
        elif isinstance(assump, six.string_types):
            if os.path.isfile(assump):
                txt = open(assump, 'r').read()
            else:
                txt = assump
            (cons_dict,
             behv_dict,
             gdiff_base_dict,
             gdiff_resp_dict) = Calculator._read_json_econ_assump_text(txt)
        else:
            raise ValueError('assump is neither None nor string')
        # next process first reform parameter
        if reform is None:
            rpol_dict = dict()
        elif isinstance(reform, six.string_types):
            if os.path.isfile(reform):
                txt = open(reform, 'r').read()
            else:
                txt = reform
            rpol_dict = (
                Calculator._read_json_policy_reform_text(txt,
                                                         gdiff_base_dict,
                                                         gdiff_resp_dict)
            )
        else:
            raise ValueError('reform is neither None nor string')
        # finally construct and return single composite dictionary
        param_dict = dict()
        param_dict['policy'] = rpol_dict
        param_dict['consumption'] = cons_dict
        param_dict['behavior'] = behv_dict
        param_dict['growdiff_baseline'] = gdiff_base_dict
        param_dict['growdiff_response'] = gdiff_resp_dict
        return param_dict

    REQUIRED_REFORM_KEYS = set(['policy'])
    REQUIRED_ASSUMP_KEYS = set(['consumption', 'behavior',
                                'growdiff_baseline', 'growdiff_response'])

    @staticmethod
    def reform_documentation(params, policy_dicts=None):
        """
        Generate reform documentation.

        Parameters
        ----------
        params: dict
            dictionary is structured like dict returned from
            the static Calculator method read_json_param_objects()

        policy_dicts : list of dict or None
            each dictionary in list is a params['policy'] dictionary
            representing second or subsequent elements of a compound
            reform; None implies no compound reform with the simple
            reform characterized in the params['policy'] dictionary

        Returns
        -------
        doc: String
            the documentation for the policy reform specified in params
        """
        # pylint: disable=too-many-statements,too-many-branches

        # nested function used only in reform_documentation
        def param_doc(years, change, base):
            """
            Parameters
            ----------
            years: list of change years
            change: dictionary of parameter changes
            base: Policy or Growdiff object with baseline values
            syear: parameter start calendar year

            Returns
            -------
            doc: String
            """
            # pylint: disable=too-many-locals

            # nested function used only in param_doc
            def lines(text, num_indent_spaces, max_line_length=77):
                """
                Return list of text lines, each one of which is no longer
                than max_line_length, with the second and subsequent lines
                being indented by the number of specified num_indent_spaces;
                each line in the list ends with the '\n' character
                """
                if len(text) < max_line_length:
                    # all text fits on one line
                    line = text + '\n'
                    return [line]
                # all text does not fix on one line
                first_line = True
                line_list = list()
                words = text.split()
                while words:
                    if first_line:
                        line = ''
                        first_line = False
                    else:
                        line = ' ' * num_indent_spaces
                    while (words and
                           (len(words[0]) + len(line)) < max_line_length):
                        line += words.pop(0) + ' '
                    line = line[:-1] + '\n'
                    line_list.append(line)
                return line_list

            # begin main logic of param_doc
            # pylint: disable=too-many-nested-blocks
            assert len(years) == len(change.keys())
            basex = copy.deepcopy(base)
            basevals = getattr(basex, '_vals', None)
            assert isinstance(basevals, dict)
            doc = ''
            for year in years:
                # write year
                basex.set_year(year)
                doc += '{}:\n'.format(year)
                # write info for each param in year
                for param in sorted(change[year].keys()):
                    # ... write param:value line
                    pval = change[year][param]
                    if isinstance(pval, list):
                        pval = pval[0]
                        if basevals[param]['boolean_value']:
                            if isinstance(pval, list):
                                pval = [True if item else
                                        False for item in pval]
                            else:
                                pval = bool(pval)
                    doc += ' {} : {}\n'.format(param, pval)
                    # ... write optional param-index line
                    if isinstance(pval, list):
                        pval = basevals[param]['col_label']
                        pval = [str(item) for item in pval]
                        doc += ' ' * (4 + len(param)) + '{}\n'.format(pval)
                    # ... write name line
                    if param.endswith('_cpi'):
                        rootparam = param[:-4]
                        name = '{} inflation indexing status'.format(rootparam)
                    else:
                        name = basevals[param]['long_name']
                    for line in lines('name: ' + name, 6):
                        doc += '  ' + line
                    # ... write optional desc line
                    if not param.endswith('_cpi'):
                        desc = basevals[param]['description']
                        for line in lines('desc: ' + desc, 6):
                            doc += '  ' + line
                    # ... write baseline_value line
                    if isinstance(basex, Policy):
                        if param.endswith('_cpi'):
                            rootparam = param[:-4]
                            bval = basevals[rootparam].get('cpi_inflated',
                                                           False)
                        else:
                            bval = getattr(basex, param[1:], None)
                            if isinstance(bval, np.ndarray):
                                bval = bval.tolist()
                                if basevals[param]['boolean_value']:
                                    bval = [True if item else
                                            False for item in bval]
                            elif basevals[param]['boolean_value']:
                                bval = bool(bval)
                        doc += '  baseline_value: {}\n'.format(bval)
                    else:  # if basex is Growdiff object
                        # all Growdiff parameters have zero as default value
                        doc += '  baseline_value: 0.0\n'
            return doc

        # begin main logic of reform_documentation
        # create Policy object with pre-reform (i.e., baseline) values
        # ... create gdiff_baseline object
        gdb = Growdiff()
        gdb.update_growdiff(params['growdiff_baseline'])
        # ... create Growfactors clp object that incorporates gdiff_baseline
        gfactors_clp = Growfactors()
        gdb.apply_to(gfactors_clp)
        # ... create Policy object containing pre-reform parameter values
        clp = Policy(gfactors=gfactors_clp)
        # generate documentation text
        doc = 'REFORM DOCUMENTATION\n'
        doc += 'Baseline Growth-Difference Assumption Values by Year:\n'
        years = sorted(params['growdiff_baseline'].keys())
        if years:
            doc += param_doc(years, params['growdiff_baseline'], gdb)
        else:
            doc += 'none: using default baseline growth assumptions\n'
        doc += 'Policy Reform Parameter Values by Year:\n'
        years = sorted(params['policy'].keys())
        if years:
            doc += param_doc(years, params['policy'], clp)
        else:
            doc += 'none: using current-law policy parameters\n'
        if policy_dicts is not None:
            assert isinstance(policy_dicts, list)
            base = clp
            base.implement_reform(params['policy'])
            assert not base.reform_errors
            for policy_dict in policy_dicts:
                assert isinstance(policy_dict, dict)
                doc += 'Policy Reform Parameter Values by Year:\n'
                years = sorted(policy_dict.keys())
                doc += param_doc(years, policy_dict, base)
                base.implement_reform(policy_dict)
                assert not base.reform_errors
        return doc

    def ce_aftertax_income(self, calc,
                           custom_params=None,
                           require_no_agg_tax_change=True):
        """
        Return dictionary that contains certainty-equivalent of the
        expected utility of after-tax expanded income computed for
        several constant-relative-risk-aversion parameter values
        for each of two Calculator objects: self, which represents
        the pre-reform situation, and calc, which represents the
        post-reform situation, both of which MUST have had calc_call()
        called before being passed to this function.

        IMPORTANT NOTES: These normative welfare calculations are very
        simple.  It is assumed that utility is a function of only
        consumption, and that consumption is equal to after-tax
        income.  This means that any assumed behavioral responses that
        change work effort will not affect utility via the
        correpsonding change in leisure.  And any saving response to
        changes in after-tax income do not affect consumption.

        The cmin value is the consumption level below which marginal
        utility is considered to be constant.  This allows the handling
        of filing units with very low or even negative after-tax expanded
        income in the expected-utility and certainty-equivalent calculations.
        """
        # check that calc and self are consistent
        assert isinstance(calc, Calculator)
        assert calc.array_len == self.array_len
        assert calc.current_year == self.current_year
        # extract data from self and calc
        records_variables = ['s006', 'combined', 'expanded_income']
        df1 = self.dataframe(records_variables)
        df2 = calc.dataframe(records_variables)
        cedict = ce_aftertax_expanded_income(
            df1, df2,
            custom_params=custom_params,
            require_no_agg_tax_change=require_no_agg_tax_change)
        cedict['year'] = self.current_year
        return cedict

    # ----- begin private methods of Calculator class -----

    def _taxinc_to_amt(self):
        """
        Call TaxInc through AMT functions.
        """
        TaxInc(self.__policy, self.__records)
        SchXYZTax(self.__policy, self.__records)
        GainsTax(self.__policy, self.__records)
        AGIsurtax(self.__policy, self.__records)
        NetInvIncTax(self.__policy, self.__records)
        AMT(self.__policy, self.__records)

    def _calc_one_year(self, zero_out_calc_vars=False):
        """
        Call all the functions except those in the calc_all() method.
        """
        if zero_out_calc_vars:
            self.__records.zero_out_changing_calculated_vars()
        # pdb.set_trace()
        EI_PayrollTax(self.__policy, self.__records)
        DependentCare(self.__policy, self.__records)
        Adj(self.__policy, self.__records)
        ALD_InvInc_ec_base(self.__policy, self.__records)
        CapGains(self.__policy, self.__records)
        SSBenefits(self.__policy, self.__records)
        UBI(self.__policy, self.__records)
        AGI(self.__policy, self.__records)
        ItemDedCap(self.__policy, self.__records)
        ItemDed(self.__policy, self.__records)
        AdditionalMedicareTax(self.__policy, self.__records)
        StdDed(self.__policy, self.__records)
        # Store calculated standard deduction, calculate
        # taxes with standard deduction, store AMT + Regular Tax
        std = copy.deepcopy(self.array('standard'))
        item = copy.deepcopy(self.array('c04470'))
        item_no_limit = copy.deepcopy(self.array('c21060'))
        item_phaseout = copy.deepcopy(self.array('c21040'))
        self.zeroarray('c04470')
        self.zeroarray('c21060')
        self.zeroarray('c21040')
        self._taxinc_to_amt()
        std_taxes = copy.deepcopy(self.array('c05800'))
        # Set standard deduction to zero, calculate taxes w/o
        # standard deduction, and store AMT + Regular Tax
        self.zeroarray('standard')
        self.array('c21060', item_no_limit)
        self.array('c21040', item_phaseout)
        self.array('c04470', item)
        self._taxinc_to_amt()
        item_taxes = copy.deepcopy(self.array('c05800'))
        # Replace standard deduction with zero where the taxpayer
        # would be better off itemizing
        self.array('standard', np.where(item_taxes < std_taxes,
                                        0., std))
        self.array('c04470', np.where(item_taxes < std_taxes,
                                      item, 0.))
        self.array('c21060', np.where(item_taxes < std_taxes,
                                      item_no_limit, 0.))
        self.array('c21040', np.where(item_taxes < std_taxes,
                                      item_phaseout, 0.))
        # Calculate taxes with optimal itemized deduction
        self._taxinc_to_amt()
        F2441(self.__policy, self.__records)
        EITC(self.__policy, self.__records)
        ChildTaxCredit(self.__policy, self.__records)
        PersonalTaxCredit(self.__policy, self.__records)
        AmOppCreditParts(self.__policy, self.__records)
        SchR(self.__policy, self.__records)
        EducationTaxCredit(self.__policy, self.__records)
        NonrefundableCredits(self.__policy, self.__records)
        AdditionalCTC(self.__policy, self.__records)
        C1040(self.__policy, self.__records)
        CTC_new(self.__policy, self.__records)
        IITAX(self.__policy, self.__records)

    @staticmethod
    def _read_json_policy_reform_text(text_string,
                                      growdiff_baseline_dict,
                                      growdiff_response_dict):
        """
        Strip //-comments from text_string and return 1 dict based on the JSON.

        Specified text is JSON with at least 1 high-level string:object pair:
        a "policy": {...} pair.

        Other high-level pairs will be ignored by this method, except
        that a "consumption", "behavior", "growdiff_baseline" or
        "growdiff_response" key will raise a ValueError.

        The {...}  object may be empty (that is, be {}), or
        may contain one or more pairs with parameter string primary keys
        and string years as secondary keys.  See tests/test_calculate.py for
        an extended example of a commented JSON policy reform text
        that can be read by this method.

        Returned dictionary prdict has integer years as primary keys and
        string parameters as secondary keys.  This returned dictionary is
        suitable as the argument to the Policy implement_reform(prdict) method.
        """
        # strip out //-comments without changing line numbers
        json_str = re.sub('//.*', ' ', text_string)
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
        # check key contents of dictionary
        actual_keys = raw_dict.keys()
        for rkey in Calculator.REQUIRED_REFORM_KEYS:
            if rkey not in actual_keys:
                msg = 'key "{}" is not in policy reform file'
                raise ValueError(msg.format(rkey))
        for rkey in actual_keys:
            if rkey in Calculator.REQUIRED_ASSUMP_KEYS:
                msg = 'key "{}" should be in economic assumption file'
                raise ValueError(msg.format(rkey))
        # convert raw_dict['policy'] dictionary into prdict
        tdict = Policy.translate_json_reform_suffixes(raw_dict['policy'],
                                                      growdiff_baseline_dict,
                                                      growdiff_response_dict)
        prdict = Calculator._convert_parameter_dict(tdict)
        return prdict

    @staticmethod
    def _read_json_econ_assump_text(text_string):
        """
        Strip //-comments from text_string and return 4 dict based on the JSON.

        Specified text is JSON with at least 4 high-level string:object pairs:
        a "consumption": {...} pair,
        a "behavior": {...} pair,
        a "growdiff_baseline": {...} pair, and
        a "growdiff_response": {...} pair.

        Other high-level pairs will be ignored by this method, except that
        a "policy" key will raise a ValueError.

        The {...}  object may be empty (that is, be {}), or
        may contain one or more pairs with parameter string primary keys
        and string years as secondary keys.  See tests/test_calculate.py for
        an extended example of a commented JSON economic assumption text
        that can be read by this method.

        Note that an example is shown in the ASSUMP_CONTENTS string in
          tests/test_calculate.py file.

        Returned dictionaries (cons_dict, behv_dict, gdiff_baseline_dict,
        gdiff_respose_dict) have integer years as primary keys and
        string parameters as secondary keys.

        These returned dictionaries are suitable as the arguments to
        the Consumption.update_consumption(cons_dict) method, or
        the Behavior.update_behavior(behv_dict) method, or
        the Growdiff.update_growdiff(gdiff_dict) method.
        """
        # pylint: disable=too-many-locals
        # strip out //-comments without changing line numbers
        json_str = re.sub('//.*', ' ', text_string)
        # convert JSON text into a Python dictionary
        try:
            raw_dict = json.loads(json_str)
        except ValueError as valerr:
            msg = 'Economic assumption text below contains invalid JSON:\n'
            msg += str(valerr) + '\n'
            msg += 'Above location of the first error may be approximate.\n'
            msg += 'The invalid JSON asssump text is between the lines:\n'
            bline = 'XX----.----1----.----2----.----3----.----4'
            bline += '----.----5----.----6----.----7'
            msg += bline + '\n'
            linenum = 0
            for line in json_str.split('\n'):
                linenum += 1
                msg += '{:02d}{}'.format(linenum, line) + '\n'
            msg += bline + '\n'
            raise ValueError(msg)
        # check key contents of dictionary
        actual_keys = raw_dict.keys()
        for rkey in Calculator.REQUIRED_ASSUMP_KEYS:
            if rkey not in actual_keys:
                msg = 'key "{}" is not in economic assumption file'
                raise ValueError(msg.format(rkey))
        for rkey in actual_keys:
            if rkey in Calculator.REQUIRED_REFORM_KEYS:
                msg = 'key "{}" should be in policy reform file'
                raise ValueError(msg.format(rkey))
        # convert the assumption dictionaries in raw_dict
        key = 'consumption'
        cons_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'behavior'
        behv_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'growdiff_baseline'
        gdiff_base_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'growdiff_response'
        gdiff_resp_dict = Calculator._convert_parameter_dict(raw_dict[key])
        return (cons_dict, behv_dict, gdiff_base_dict, gdiff_resp_dict)

    @staticmethod
    def _convert_parameter_dict(param_key_dict):
        """
        Converts specified param_key_dict into a dictionary whose primary
        keys are calendar years, and hence, is suitable as the argument to
        the Policy.implement_reform() method, or
        the Consumption.update_consumption() method, or
        the Behavior.update_behavior() method, or
        the Growdiff.update_growdiff() method.

        Specified input dictionary has string parameter primary keys and
        string years as secondary keys.

        Returned dictionary has integer years as primary keys and
        string parameters as secondary keys.
        """
        # convert year skey strings into integers and
        # optionally convert lists into np.arrays
        year_param = dict()
        for pkey, sdict in param_key_dict.items():
            if not isinstance(pkey, six.string_types):
                msg = 'pkey {} in reform is not a string'
                raise ValueError(msg.format(pkey))
            rdict = dict()
            if not isinstance(sdict, dict):
                msg = 'pkey {} in reform is not paired with a dict'
                raise ValueError(msg.format(pkey))
            for skey, val in sdict.items():
                if not isinstance(skey, six.string_types):
                    msg = 'skey {} in reform is not a string'
                    raise ValueError(msg.format(skey))
                else:
                    year = int(skey)
                rdict[year] = val
            year_param[pkey] = rdict
        # convert year_param dictionary to year_key_dict dictionary
        year_key_dict = dict()
        years = set()
        for param, sdict in year_param.items():
            for year, val in sdict.items():
                if year not in years:
                    years.add(year)
                    year_key_dict[year] = dict()
                year_key_dict[year][param] = val
        return year_key_dict
