"""
Tax-Calculator federal income and payroll tax Calculator class.
"""
# CODING-STYLE CHECKS:
# pycodestyle calculator.py
# pylint --disable=locally-disabled calculator.py
#
# pylint: disable=too-many-lines,no-value-for-parameter

import copy
from collections import OrderedDict
import numpy as np
import pandas as pd
import paramtools
from taxcalc.calcfunctions import (TaxInc, SchXYZTax, GainsTax, AGIsurtax,
                                   NetInvIncTax, AMT, EI_PayrollTax, Adj,
                                   DependentCare, ALD_InvInc_ec_base, CapGains,
                                   SSBenefits, UBI, AGI, ItemDedCap, ItemDed,
                                   StdDed, AdditionalMedicareTax, F2441, EITC,
                                   RefundablePayrollTaxCredit,
                                   ChildDepTaxCredit, AdditionalCTC, CTC_new,
                                   PersonalTaxCredit, SchR,
                                   AmOppCreditParts, EducationTaxCredit,
                                   CharityCredit,
                                   NonrefundableCredits, C1040, IITAX,
                                   BenefitSurtax, BenefitLimitation,
                                   FairShareTax, LumpSumTax, BenefitPrograms,
                                   ExpandIncome, AfterTaxIncome)
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff
from taxcalc.growfactors import GrowFactors
from taxcalc.utils import (DIST_VARIABLES, create_distribution_table,
                           DIFF_VARIABLES, create_difference_table,
                           create_diagnostic_table,
                           ce_aftertax_expanded_income,
                           mtr_graph_data, atr_graph_data, xtr_graph_plot,
                           pch_graph_data, pch_graph_plot)
# import pdb


class Calculator():
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
        data-extrapolated progress reports; default value is false.

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

    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None):
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
            self.__consumption = Consumption()
        elif isinstance(consumption, Consumption):
            self.__consumption = copy.deepcopy(consumption)
        else:
            raise ValueError('consumption must be None or Consumption object')
        if self.__consumption.current_year < self.__policy.current_year:
            self.__consumption.set_year(self.__policy.current_year)
        if verbose:
            if self.__records.IGNORED_VARS:
                print('Your data include the following unused ' +
                      'variables that will be ignored:')
                for var in self.__records.IGNORED_VARS:
                    print('  ' +
                          var)
        current_year_is_data_year = (
            self.__records.current_year == self.__records.data_year)
        if sync_years and current_year_is_data_year:
            if verbose:
                print('You loaded data for ' +
                      str(self.__records.data_year) + '.')
            while self.__records.current_year < self.__policy.current_year:
                self.__records.increment_year()
            if verbose:
                print('Tax-Calculator startup automatically ' +
                      'extrapolated your data to ' +
                      str(self.__records.current_year) + '.')
        else:
            if verbose:
                print('Tax-Calculator startup did not ' +
                      'extrapolate your data.')
        assert self.__policy.current_year == self.__records.current_year
        assert self.__policy.current_year == self.__consumption.current_year
        self.__stored_records = None

    def increment_year(self):
        """
        Advance all embedded objects to next year.
        """
        next_year = self.__policy.current_year + 1
        self.__records.increment_year()
        self.__policy.set_year(next_year)
        self.__consumption.set_year(next_year)

    def advance_to_year(self, year):
        """
        The advance_to_year function gives an optional way of implementing
        increment year functionality by immediately specifying the year
        as input.  New year must be at least the current year.
        """
        iteration = year - self.current_year
        if iteration < 0:
            raise ValueError('New current year must be ' +
                             'greater than or equal to current year!')
        for _ in range(iteration):
            self.increment_year()
        assert self.current_year == year

    def calc_all(self, zero_out_calc_vars=False):
        """
        Call all tax-calculation functions for the current_year.
        """
        df = self._Calculator__records._datastore
        def get_params(params: list):
            pl = OrderedDict()
            for p in params:
                pl[p] = self.policy_param(p)
            return pl


        pl = get_params(['UBI_u18', 'UBI_1820', 'UBI_21', 'UBI_ecrt'])
        return_ubi = UBI(df.nu18, df.n1820, df.n21, *pl.values())
        for out_arg, col in zip(['ubi', 'taxable_ubi', 'nontaxable_ubi'], return_ubi):
            df[out_arg] = col

        BenefitPrograms(self)
        self._calc_one_year(zero_out_calc_vars)
        BenefitSurtax(self)
        BenefitLimitation(self)

        pl = get_params(['FST_AGI_trt', 'FST_AGI_thd_lo', 'FST_AGI_thd_hi'])
        pl['FST_AGI_thd_lo'] = pl['FST_AGI_thd_lo'][df.MARS-1]
        pl['FST_AGI_thd_hi'] = pl['FST_AGI_thd_hi'][df.MARS-1]
        return_fairshare = FairShareTax(df.c00100, df.MARS, df.ptax_was, df.setax, df.ptax_amc,
                                        df.iitax, df.combined, df.surtax,
                                        *pl.values())
        for out_arg, col in zip(['fstax', 'iitax', 'combined', 'surtax'], return_fairshare):
            df[out_arg] = col

        return_lumpsumtax = LumpSumTax(df.DSI, df.num, df.XTOT, df.combined,
                            self.policy_param('LST'))
        for out_arg, col in zip(['lumpsumtax', 'combined'], return_lumpsumtax):
            df[out_arg] = col

        df['expanded_income'] =  ExpandIncome(df.e00200, df.pencon_p, df.pencon_s, df.e00300, df.e00400, df.e00600,
                                        df.e00700, df.e00800, df.e00900, df.e01100, df.e01200, df.e01400, df.e01500,
                                        df.e02000, df.e02100, df.p22250, df.p23250, df.cmbtp, df.ptax_was,
                                        df.benefit_value_total)

        df['aftertax_income'] = AfterTaxIncome(df.combined, df.expanded_income)

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

    def dataframe(self, variable_list, all_vars=False):
        """
        Return Pandas DataFrame containing the listed variables from the
        embedded Records object.  If all_vars is True, then the variable_list
        is ignored and all variables used as input to and calculated by the
        Calculator.calc_all() method (which does not include marginal tax
        rates) are included in the returned Pandas DataFrame.
        """
        if all_vars:
            varlist = list(self.__records.USABLE_READ_VARS |
                           self.__records.CALCULATED_VARS)
        else:
            assert isinstance(variable_list, list)
            varlist = variable_list
        dframe = self.__records._datastore.loc[:, varlist]
        del varlist
        return dframe

    def array(self, variable_name, variable_value=None):
        """
        If variable_value is None, return numpy ndarray containing the
         named variable in embedded Records object.
        If variable_value is not None, set named variable in embedded Records
         object to specified variable_value and return None (which can be
         ignored).
        """
        if variable_value is None:
            return getattr(self.__records, variable_name)
        assert isinstance(variable_value, (pd.Series, np.ndarray))
        setattr(self.__records, variable_name, variable_value)
        return None

    def n65(self):
        """
        Return numpy ndarray containing the number of
        individuals age 65+ in each filing unit.
        """
        vdf = self.dataframe(['age_head', 'age_spouse', 'elderly_dependents'])
        return ((vdf['age_head'] >= 65).astype(int) +
                (vdf['age_spouse'] >= 65).astype(int) +
                vdf['elderly_dependents'])

    def incarray(self, variable_name, variable_add):
        """
        Add variable_add to named variable in embedded Records object.
        """
        assert isinstance(variable_add, (pd.Series, np.ndarray))
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
        del self.__stored_records
        self.__stored_records = None

    @property
    def array_len(self):
        """
        Length of arrays in embedded Records object.
        """
        return self.__records.array_length

    def policy_param(self, param_name, param_value=None):
        """
        If param_value is None, return named parameter in
         embedded Policy object.
        If param_value is not None, set named parameter in
         embedded Policy object to specified param_value and
         return None (which can be ignored).
        """
        if param_value is None:
            val = getattr(self.__policy, param_name)
            if param_name.startswith("_"):
                return val
            else:
                return val[0]  # drop down a dimension.
        setattr(self.__policy, param_name, param_value)
        return None

    def consump_param(self, param_name):
        """
        Return value of named parameter in embedded Consumption object.
        """
        return getattr(self.__consumption, param_name)

    def consump_benval_params(self):
        """
        Return list of benefit-consumption-value parameter values
        in embedded Consumption object.
        """
        return self.__consumption.benval_params()

    @property
    def reform_warnings(self):
        """
        Calculator class embedded Policy object's parameter_warnings.
        """
        return self.__policy.parameter_warnings

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
        Generate multi-year diagnostic table containing aggregate statistics;
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
        yearlist = list()
        varlist = list()
        for iyr in range(1, num_years + 1):
            calc.calc_all()
            yearlist.append(calc.current_year)
            varlist.append(calc.dataframe(DIST_VARIABLES))
            if iyr < num_years:
                calc.increment_year()
        del calc
        return create_diagnostic_table(varlist, yearlist)

    def distribution_tables(self, calc, groupby,
                            pop_quantiles=False, scaling=True):
        """
        Get results from self and calc, sort them by expanded_income into
        table rows defined by groupby, compute grouped statistics, and
        return tables as a pair of Pandas dataframes.
        This method leaves the Calculator object(s) unchanged.
        Note that the returned tables have consistent income groups (based
        on the self expanded_income) even though the baseline expanded_income
        in self and the reform expanded_income in calc are different.

        Parameters
        ----------
        calc : Calculator object or None
            typically represents the reform while self represents the baseline;
            if calc is None, the second returned table is None

        groupby : String object
            options for input: 'weighted_deciles', 'standard_income_bins',
                               'soi_agi_bins'
            determines how the columns in resulting Pandas DataFrame are sorted

        pop_quantiles : boolean
            specifies whether or not weighted_deciles contain an equal number
            of people (True) or an equal number of filing units (False)

        scaling : boolean
            specifies create_distribution_table utility function argument
            that determines whether table entry values are scaled or not

        Return and typical usage
        ------------------------
        dist1, dist2 = calc1.distribution_tables(calc2, 'weighted_deciles')
        OR
        dist1, _ = calc1.distribution_tables(None, 'weighted_deciles')
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object).
        Each of the dist1 and optional dist2 is a distribution table as a
        Pandas DataFrame with DIST_TABLE_COLUMNS and groupby rows.
        NOTE: when groupby is 'weighted_deciles', the returned tables have 3
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent); and the
              returned table splits the bottom decile into filing units with
              negative (denoted by a 0-10n row label),
              zero (denoted by a 0-10z row label), and
              positive (denoted by a 0-10p row label) values of the
              specified income_measure.
        """
        # nested functions used only by this method
        def distribution_table_dataframe(calcobj):
            """
            Return pandas DataFrame containing the DIST_TABLE_COLUMNS variables
            from specified Calculator object, calcobj.
            """
            dframe = calcobj.dataframe(DIST_VARIABLES)
            # weighted count of all people or filing units
            if pop_quantiles:
                dframe['count'] = np.multiply(dframe['s006'], dframe['XTOT'])
            else:
                dframe['count'] = dframe['s006']
            # weighted count of those with itemized-deduction returns
            dframe['count_ItemDed'] = dframe['count'].where(
                dframe['c04470'] > 0., 0.)
            # weighted count of those with standard-deduction returns
            dframe['count_StandardDed'] = dframe['count'].where(
                dframe['standard'] > 0., 0.)
            # weight count of those with positive Alternative Minimum Tax (AMT)
            dframe['count_AMT'] = dframe['count'].where(
                dframe['c09600'] > 0., 0.)
            return dframe

        def have_same_income_measure(calc1, calc2):
            """
            Return true if calc1 and calc2 contain the same expanded_income;
            otherwise, return false.  (Note that "same" means nobody's
            expanded_income differs by more than one cent.)
            """
            im1 = calc1.array('expanded_income')
            im2 = calc2.array('expanded_income')
            return np.allclose(im1, im2, rtol=0.0, atol=0.01)

        # main logic of distribution_tables method
        assert calc is None or isinstance(calc, Calculator)
        assert groupby in ('weighted_deciles', 'standard_income_bins',
                           'soi_agi_bins')
        if calc is not None:
            assert np.allclose(self.array('s006'),
                               calc.array('s006'))  # check rows in same order
        var_dataframe = distribution_table_dataframe(self)
        imeasure = 'expanded_income'
        dt1 = create_distribution_table(var_dataframe, groupby, imeasure,
                                        pop_quantiles, scaling)
        del var_dataframe
        if calc is None:
            dt2 = None
        else:
            assert calc.current_year == self.current_year
            assert calc.array_len == self.array_len
            assert np.allclose(self.consump_benval_params(),
                               calc.consump_benval_params())
            var_dataframe = distribution_table_dataframe(calc)
            if have_same_income_measure(self, calc):
                imeasure = 'expanded_income'
            else:
                imeasure = 'expanded_income_baseline'
                var_dataframe[imeasure] = self.array('expanded_income')
            dt2 = create_distribution_table(var_dataframe, groupby, imeasure,
                                            pop_quantiles, scaling)
            del var_dataframe
        return (dt1, dt2)

    def difference_table(self, calc, groupby, tax_to_diff,
                         pop_quantiles=False):
        """
        Get results from self and calc, sort them by expanded_income into
        table rows defined by groupby, compute grouped statistics, and
        return tax-difference table as a Pandas dataframe.
        This method leaves the Calculator objects unchanged.
        Note that the returned tables have consistent income groups (based
        on the self expanded_income) even though the baseline expanded_income
        in self and the reform expanded_income in calc are different.

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline

        groupby : String object
            options for input: 'weighted_deciles', 'standard_income_bins'
            determines how the columns in resulting Pandas DataFrame are sorted

        tax_to_diff : String object
            options for input: 'iitax', 'payrolltax', 'combined'
            specifies which tax to difference

        pop_quantiles : boolean
            specifies whether or not weighted_deciles contain an equal number
            of people (True) or an equal number of filing units (False)

        Returns and typical usage
        -------------------------
        diff = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object).
        The returned diff is a difference table as a Pandas DataFrame
        with DIST_TABLE_COLUMNS and groupby rows.
        NOTE: when groupby is 'weighted_deciles', the returned table has three
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent); and the
              returned table splits the bottom decile into filing units with
              negative (denoted by a 0-10n row label),
              zero (denoted by a 0-10z row label), and
              positive (denoted by a 0-10p row label) values of the
              specified income_measure.
        """
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        assert np.allclose(self.consump_benval_params(),
                           calc.consump_benval_params())
        self_var_dframe = self.dataframe(DIFF_VARIABLES)
        calc_var_dframe = calc.dataframe(DIFF_VARIABLES)
        diff = create_difference_table(self_var_dframe, calc_var_dframe,
                                       groupby, tax_to_diff, pop_quantiles)
        del self_var_dframe
        del calc_var_dframe
        return diff

    MTR_VALID_VARIABLES = ['e00200p', 'e00200s',
                           'e00900p', 'e00300',
                           'e00400', 'e00600',
                           'e00650', 'e01400',
                           'e01700', 'e02000',
                           'e02400', 'p22250',
                           'p23250', 'e18500',
                           'e19200', 'e26270',
                           'e19800', 'e20100',
                           'k1bx14p']

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
        'e20100',  Charity non-cash contributions;
        'k1bx14p', Partnership income (also included in e26270 and e02000).
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
            scheincome_var = self.array('e02000')
        elif variable_str == 'k1bx14p':
            scheincome_var = self.array('e02000')
            scorpincome_var = self.array('e26270')
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
            self.array('e02000', scheincome_var + finite_diff)
        elif variable_str == 'k1bx14p':
            self.array('e02000', scheincome_var + finite_diff)
            self.array('e26270', scorpincome_var + finite_diff)
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
        mtr_on_earnings = variable_str in ('e00200p', 'e00200s')
        if wrt_full_compensation and mtr_on_earnings:
            oasdi_taxed = np.logical_or(
                variable < self.policy_param('SS_Earnings_c'),
                variable >= self.policy_param('SS_Earnings_thd')
            )
            adj = np.where(oasdi_taxed,
                           0.5 * (self.policy_param('FICA_ss_trt') +
                                  self.policy_param('FICA_mc_trt')),
                           0.5 * self.policy_param('FICA_mc_trt'))
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
        # delete intermediate variables
        del variable
        if variable_str in ('e00200p', 'e00200s'):
            del earnings_var
        elif variable_str == 'e00900p':
            del seincome_var
        elif variable_str == 'e00650':
            del divincome_var
        elif variable_str == 'e26270':
            del scheincome_var
        elif variable_str == 'k1bx14p':
            del scheincome_var
            del scorpincome_var
        del payrolltax_chng
        del incometax_chng
        del combined_taxes_chng
        del payrolltax_base
        del incometax_base
        del combined_taxes_base
        del payrolltax_diff
        del incometax_diff
        del combined_diff
        del adj
        # return the three marginal tax rate arrays
        return (mtr_payrolltax, mtr_incometax, mtr_combined)

    def mtr_graph(self, calc,
                  mars='ALL',
                  mtr_measure='combined',
                  mtr_variable='e00200p',
                  alt_e00200p_text='',
                  mtr_wrt_full_compen=False,
                  income_measure='expanded_income',
                  pop_quantiles=False,
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

            - 'expanded_income': broader than AGI (see definition in
                                 calcfunctions.py file).

        pop_quantiles : boolean
            specifies whether or not weighted_deciles contain an equal number
            of people (True) or an equal number of filing units (False)

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
        assert mars == 'ALL' or 1 <= mars <= 4
        # check validity of income_measure
        assert income_measure in ('expanded_income', 'agi', 'wages')
        if income_measure == 'expanded_income':
            income_variable = 'expanded_income'
        elif income_measure == 'agi':
            income_variable = 'c00100'
        elif income_measure == 'wages':
            income_variable = 'e00200'
        # check validity of mtr_measure parameter
        assert mtr_measure in ('combined', 'itax', 'ptax')
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
        record_variables = ['s006', 'XTOT']
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
                              pop_quantiles=pop_quantiles,
                              dollar_weighting=dollar_weighting)
        # delete intermediate variables
        del vdf
        del mtr1_ptax
        del mtr1_itax
        del mtr1_combined
        del mtr1
        del mtr2_ptax
        del mtr2_itax
        del mtr2_combined
        del mtr2
        del record_variables
        # construct figure from data
        fig = xtr_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='',
                             legendloc='bottom_right')
        del data
        return fig

    def atr_graph(self, calc,
                  mars='ALL',
                  atr_measure='combined',
                  pop_quantiles=False):
        """
        Create average tax rate graph that can be written to an HTML
        file (using the write_graph_file utility function) or shown on
        the screen immediately in an interactive or notebook session
        (following the instructions in the documentation of the
        xtr_graph_plot utility function).  The graph shows the mean
        average tax rate for each expanded-income percentile excluding
        any percentile that includes a filing unit with negative or
        zero basline (self) expanded income.

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

        pop_quantiles : boolean
            specifies whether or not weighted_deciles contain an equal number
            of people (True) or an equal number of filing units (False)

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        # check validity of function arguments
        assert mars == 'ALL' or 1 <= mars <= 4
        assert atr_measure in ('combined', 'itax', 'ptax')
        # extract needed output that is assumed unchanged by reform from self
        record_variables = ['s006', 'XTOT']
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
                              pop_quantiles=pop_quantiles)
        # delete intermediate variables
        del vdf
        del record_variables
        # construct figure from data
        fig = xtr_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='',
                             legendloc='bottom_right')
        del data
        return fig

    def pch_graph(self, calc, pop_quantiles=False):
        """
        Create percentage change in after-tax expanded income graph that
        can be written to an HTML file (using the write_graph_file utility
        function) or shown on the screen immediately in an interactive or
        notebook session (following the instructions in the documentation
        of the xtr_graph_plot utility function).  The graph shows the
        dollar-weighted mean percentage change in after-tax expanded income
        for each expanded-income percentile excluding any percentile that
        includes a filing unit with negative or zero basline (self) expanded
        income.

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline,
            where both self and calc have calculated taxes for this year
            before being used by this method

        pop_quantiles : boolean
            specifies whether or not weighted_deciles contain an equal number
            of people (True) or an equal number of filing units (False)

        Returns
        -------
        graph that is a bokeh.plotting figure object
        """
        # check that two Calculator objects are comparable
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        # extract needed output from baseline and reform Calculator objects
        vdf1 = self.dataframe(['s006', 'XTOT', 'aftertax_income',
                               'expanded_income'])
        vdf2 = calc.dataframe(['s006', 'XTOT', 'aftertax_income'])
        assert np.allclose(vdf1['s006'], vdf2['s006'])
        assert np.allclose(vdf1['XTOT'], vdf2['XTOT'])
        vdf = pd.DataFrame()
        vdf['s006'] = vdf1['s006']
        vdf['XTOT'] = vdf1['XTOT']
        vdf['expanded_income'] = vdf1['expanded_income']
        vdf['chg_aftinc'] = vdf2['aftertax_income'] - vdf1['aftertax_income']
        # construct data for graph
        data = pch_graph_data(vdf, year=self.current_year,
                              pop_quantiles=pop_quantiles)
        del vdf
        del vdf1
        del vdf2
        # construct figure from data
        fig = pch_graph_plot(data,
                             width=850,
                             height=500,
                             xlabel='',
                             ylabel='',
                             title='')
        del data
        return fig

    REQUIRED_REFORM_KEYS = set(['policy'])
    REQUIRED_ASSUMP_KEYS = set(['consumption',
                                'growdiff_baseline', 'growdiff_response'])

    @staticmethod
    def read_json_param_objects(reform, assump):
        """
        Read JSON reform and assump objects and
        return a composite dictionary containing four key:dict pairs:
        'policy':dict, 'consumption':dict,
        'growdiff_baseline':dict, and 'growdiff_response':dict.

        Note that either of the two function arguments can be None.
        If reform is None, the dict in the 'policy':dict pair is empty.
        If assump is None, the dict in all the other key:dict pairs is empty.

        Also note that either of the two function arguments can be strings
        containing a valid JSON string (rather than a local filename).

        Either of the two function arguments can also be a valid URL string
        beginning with 'http' and pointing to a valid JSON file hosted online.

        The reform file/URL contents or JSON string must be like this:
        {"policy": {...}} OR {...}
        (in other words, the top-level policy key is optional)
        and the assump file/URL contents or JSON string must be like this:
        {"consumption": {...},
         "growdiff_baseline": {...},
         "growdiff_response": {...}}
        The {...} should be empty like this {} if not specifying a policy
        reform or if not specifying any non-default economic assumptions
        of that type.

        The 'policy' subdictionary of the returned dictionary is
        suitable as input into the Policy.implement_reform method.

        The 'consumption' subdictionary of the returned dictionary is
        suitable as input into the Consumption.update_consumption method.

        The 'growdiff_baseline' subdictionary of the returned dictionary is
        suitable as input into the GrowDiff.update_growdiff method.

        The 'growdiff_response' subdictionary of the returned dictionary is
        suitable as input into the GrowDiff.update_growdiff method.
        """
        # construct the composite dictionary
        param_dict = dict()
        param_dict['policy'] = Policy.read_json_reform(reform)
        param_dict['consumption'] = Consumption.read_json_update(assump)
        for topkey in ['growdiff_baseline', 'growdiff_response']:
            param_dict[topkey] = GrowDiff.read_json_update(assump, topkey)
        # return the composite dictionary
        return param_dict

    @staticmethod
    def reform_documentation(params, policy_dicts=None):
        """
        Generate reform documentation versus current-law policy.

        Parameters
        ----------
        params: dict
            dictionary is structured like dict returned from
            the static Calculator.read_json_param_objects() method

        policy_dicts : list of dict or None
            each dictionary in list is a params['policy'] dictionary
            representing second and subsequent elements of a compound
            reform; None implies no compound reform with the simple
            reform characterized in the params['policy'] dictionary

        Returns
        -------
        doc: String
            the documentation for the specified policy reform
        """
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals

        # nested function used only in reform_documentation function
        def param_doc(years_list, updated, baseline):
            """
            Parameters
            ----------
            years_list: list of parameter-change years
            updated: reform Policy or updated GrowDiff object
            base: current-law Policy or default GrowDiff object

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

            # begin main logic of nested function param_doc
            # pylint: disable=too-many-nested-blocks
            doc = ''
            assert isinstance(years_list, list)
            years = sorted(years_list)
            for year in years:
                baseline.set_year(year)
                updated.set_year(year)
                assert set(baseline.keys()) == set(updated.keys())
                params_with_diff = list()
                for pname in baseline.keys():
                    upda_value = getattr(updated, pname)
                    base_value = getattr(baseline, pname)
                    if (
                        (isinstance(upda_value, np.ndarray) and
                         np.allclose(upda_value, base_value)) or
                        (not isinstance(upda_value, np.ndarray) and
                         upda_value != base_value)
                    ):
                        params_with_diff.append(pname)
                if params_with_diff:
                    mdata_base = baseline.specification(meta_data=True)
                    # write year
                    doc += '{}:\n'.format(year)
                    for pname in sorted(params_with_diff):
                        # write updated value line
                        pval = getattr(updated, pname).tolist()[0]
                        if mdata_base[pname]['type'] == 'bool':
                            if isinstance(pval, list):
                                pval = [bool(item) for item in pval]
                            else:
                                pval = bool(pval)
                        doc += ' {} : {}\n'.format(pname, pval)
                        # ... write optional param-vector-index line
                        if isinstance(pval, list):
                            labels = paramtools.consistent_labels(
                                [mdata_base[pname]["value"][0]]
                            )
                            label = None
                            for _label in labels:
                                if _label not in ("value", "year"):
                                    label = _label
                                    break
                            if label:
                                lv = baseline._stateless_label_grid[label]
                                lv = [
                                    str(item) for item in lv
                                ]
                                doc += ' ' * (
                                    4 + len(pname)
                                ) + '{}\n'.format(lv)
                        # ... write param-name line
                        name = mdata_base[pname]['title']
                        for line in lines('name: ' + name, 6):
                            doc += '  ' + line
                        # ... write param-description line
                        desc = mdata_base[pname]['description']
                        for line in lines('desc: ' + desc, 6):
                            doc += '  ' + line
                        # ... write param-baseline-value line
                        if isinstance(baseline, Policy):
                            pval = getattr(baseline, pname).tolist()[0]
                            ptype = mdata_base[pname]['type']
                            if isinstance(pval, list):
                                if ptype == 'bool':
                                    pval = [bool(item) for item in pval]
                            elif ptype == 'bool':
                                pval = bool(pval)
                            doc += '  baseline_value: {}\n'.format(pval)
                        else:  # if baseline is GrowDiff object
                            # each GrowDiff parameter has zero as default value
                            doc += '  baseline_value: 0.0\n'
            del mdata_base
            return doc

        # begin main logic of reform_documentation
        # create Policy object with current-law-policy values
        gdiff_base = GrowDiff()
        gdiff_base.update_growdiff(params['growdiff_baseline'])
        gfactors_clp = GrowFactors()
        gdiff_base.apply_to(gfactors_clp)
        clp = Policy(gfactors=gfactors_clp)
        # create Policy object with post-reform values
        gdiff_resp = GrowDiff()
        gdiff_resp.update_growdiff(params['growdiff_response'])
        gfactors_ref = GrowFactors()
        gdiff_base.apply_to(gfactors_ref)
        gdiff_resp.apply_to(gfactors_ref)
        ref = Policy(gfactors=gfactors_ref)
        ref.implement_reform(params['policy'])
        reform_years = Policy.years_in_revision(params['policy'])
        if policy_dicts is not None:  # compound reform has been specified
            assert isinstance(policy_dicts, list)
            for policy_dict in policy_dicts:
                ref.implement_reform(policy_dict)
                xyears = Policy.years_in_revision(policy_dict)
                for year in xyears:
                    if year not in reform_years:
                        reform_years.append(year)
        # generate documentation text
        doc = 'REFORM DOCUMENTATION\n'
        # ... documentation for baseline growdiff assumptions
        doc += 'Baseline Growth-Difference Assumption Values by Year:\n'
        years = GrowDiff.years_in_revision(params['growdiff_baseline'])
        if years:
            doc += param_doc(years, gdiff_base, GrowDiff())
        else:
            doc += 'none: no baseline GrowDiff assumptions specified\n'
        # ... documentation for reform growdiff assumptions
        doc += 'Response Growth-Difference Assumption Values by Year:\n'
        years = GrowDiff.years_in_revision(params['growdiff_response'])
        if years:
            doc += param_doc(years, gdiff_resp, GrowDiff())
        else:
            doc += 'none: no response GrowDiff assumptions specified\n'
        # ... documentation for (possibly compound) policy reform
        if policy_dicts is None:
            doc += 'Policy Reform Parameter Values by Year:\n'
        else:
            doc += 'Compound Policy Reform Parameter Values by Year:\n'
        # ... use clp and ref Policy objects to generate documentation
        if reform_years:
            doc += param_doc(reform_years, ref, clp)
        else:
            doc += 'none: using current-law policy parameters\n'
        # cleanup local objects
        del gdiff_base
        del gfactors_clp
        del gdiff_resp
        del gfactors_ref
        del clp
        del ref
        del years
        del reform_years
        # return documentation string
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
        income.  This means that any assumed responses that
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
        assert np.allclose(calc.consump_benval_params(),
                           self.consump_benval_params())
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
        df = self._Calculator__records._datastore
        def get_params(params: list):
            pl = OrderedDict()
            for p in params:
                pl[p] = self.policy_param(p)
            return pl

        
        pl = get_params(['PT_qbid_rt', 'PT_qbid_taxinc_thd', 'PT_qbid_taxinc_gap',
                         'PT_qbid_w2_wages_rt', 'PT_qbid_alt_w2_wages_rt',
                         'PT_qbid_alt_property_rt', 'PT_qbid_ps', 'PT_qbid_prt',
                         'PT_qbid_limit_switch', 'UI_em', 'UI_thd'])
        for p in ['UI_thd', 'PT_qbid_taxinc_thd', 'PT_qbid_taxinc_gap', 'PT_qbid_ps']:
            pl[p] = pl[p][df.MARS-1]
        df['c04800'], df['qbided'] = TaxInc(df.c00100, df.standard, df.c04470, df.c04600,
               df.MARS, df.e00900, df.e26270, df.e02100,
               df.e27200, df.e00650, df.c01000, df.e02300, df.PT_SSTB_income,
               df.PT_binc_w2_wages, df.PT_ubia_property, *pl.values())



        pl = get_params(['PT_rt1', 'PT_rt2', 'PT_rt3', 'PT_rt4', 'PT_rt5',
                         'PT_rt6', 'PT_rt7', 'PT_rt8',
                         'PT_brk1', 'PT_brk2', 'PT_brk3', 'PT_brk4', 'PT_brk5',
                         'PT_brk6', 'PT_brk7',
                         'II_rt1', 'II_rt2', 'II_rt3', 'II_rt4', 'II_rt5',
                         'II_rt6', 'II_rt7', 'II_rt8',
                         'II_brk1', 'II_brk2', 'II_brk3', 'II_brk4', 'II_brk5',
                         'II_brk6', 'II_brk7', 'PT_EligibleRate_active',
                         'PT_EligibleRate_passive', 'PT_wages_active_income',
                         'PT_top_stacking'])
        df['c05200'] = SchXYZTax(df.c04800, df.MARS, df.e00900, df.e26270, df.e02000, df.e00200, *pl.values())
        



        df_args = [df.e00650, df.c01000, df.c23650, df.p23250, df.e01100, df.e58990, df.e00200,
                   df.e24515, df.e24518, df.MARS, df.c04800, df.c05200, df.e00900, df.e26270, df.e02000]
        pl = get_params(['II_rt1', 'II_rt2', 'II_rt3', 'II_rt4', 'II_rt5', 'II_rt6', 'II_rt7', 'II_rt8',
                         'II_brk1', 'II_brk2', 'II_brk3', 'II_brk4', 'II_brk5', 'II_brk6', 'II_brk7',
                         'PT_rt1', 'PT_rt2', 'PT_rt3', 'PT_rt4', 'PT_rt5', 'PT_rt6', 'PT_rt7', 'PT_rt8',
                         'PT_brk1', 'PT_brk2', 'PT_brk3', 'PT_brk4', 'PT_brk5', 'PT_brk6', 'PT_brk7',
                         'CG_nodiff', 'PT_EligibleRate_active', 'PT_EligibleRate_passive',
                         'PT_wages_active_income', 'PT_top_stacking',
                         'CG_rt1', 'CG_rt2', 'CG_rt3', 'CG_rt4', 'CG_brk1', 'CG_brk2', 'CG_brk3'])
        return_gt = GainsTax(*df_args, *pl.values())
        for out_arg, col in zip(['dwks10', 'dwks13', 'dwks14', 'dwks19', 'c05700', 'taxbc'], return_gt):
            df[out_arg] = col




        pl = get_params(['AGI_surtax_trt', 'AGI_surtax_thd'])
        df['taxbc'], df['surtax'] = AGIsurtax(df.c00100, df.MARS, df.taxbc, df.surtax, *pl.values())




        pl = get_params(['NIIT_thd', 'NIIT_PT_taxed', 'NIIT_rt'])
        df['niit'] = NetInvIncTax(df.e00300, df.e00600, df.e02000, df.e26270, df.c01000,
                 df.c00100, df.MARS, df.niit, *pl.values())


        df_args = [df.e07300, df.dwks13, df.standard, df.f6251, df.c00100, df.c18300, df.taxbc,
                   df.c04470, df.c17000, df.c20800, df.c21040, df.e24515, df.MARS, df.sep, df.dwks19,
                   df.dwks14, df.c05700, df.e62900, df.e00700, df.dwks10, df.age_head, df.age_spouse,
                   df.earned, df.cmbtp]
        pl = get_params(['AMT_child_em_c_age', 'AMT_brk1',
                         'AMT_em', 'AMT_prt', 'AMT_rt1', 'AMT_rt2',
                         'AMT_child_em', 'AMT_em_ps', 'AMT_em_pe',
                         'AMT_CG_brk1', 'AMT_CG_brk2', 'AMT_CG_brk3', 'AMT_CG_rt1', 'AMT_CG_rt2',
                         'AMT_CG_rt3', 'AMT_CG_rt4'])
        return_amt = AMT(*df_args, *pl.values())
        for out_arg, col in zip(['c62100', 'c09600', 'c05800'], return_amt):
            df[out_arg] = col

    def _calc_one_year(self, zero_out_calc_vars=False):

        """
        Call all the functions except those in the calc_all() method.
        """
        df = self._Calculator__records._datastore
        def get_params(params: list):
            pl = OrderedDict()
            for p in params:
                pl[p] = self.policy_param(p)
            return pl

        # pylint: disable=too-many-statements
        if zero_out_calc_vars:
            self.__records.zero_out_changing_calculated_vars()
        # pdb.set_trace()
        pl = get_params(['FICA_ss_trt', 'FICA_mc_trt','ALD_SelfEmploymentTax_hc',
                        'SS_Earnings_c','SS_Earnings_thd'])
        returns_EI_payroll = EI_PayrollTax(df.e00200p, df.e00200s, df.e00900p, df.e00900s, df.e02100p, df.e02100s,
                  df.k1bx14p, df.k1bx14s, df.pencon_p, df.pencon_s, *pl.values())
        out_args = ['sey', 'payrolltax', 'ptax_was', 'setax', 'c03260', 'ptax_oasdi',
                    'earned', 'earned_p', 'earned_s', 'was_plus_sey_p', 'was_plus_sey_s']
        for out_arg, col in zip(out_args, returns_EI_payroll):
            df[out_arg] = col


        pl = get_params(['ALD_Dependents_thd', 'ALD_Dependents_hc', 'ALD_Dependents_Child_c', 'ALD_Dependents_Elder_c'])
        df['care_deduction'] = DependentCare(df.nu13, df.elderly_dependents, df.earned, df.MARS,
                                             *pl.values())

        df_args = [df.e03150, df.e03210, df.c03260,
                   df.e03270, df.e03300, df.e03400, df.e03500, df.e00800,
                   df.e03220, df.e03230, df.e03240, df.e03290, df.care_deduction]
        pl = get_params(['ALD_StudentLoan_hc', 'ALD_SelfEmp_HealthIns_hc', 'ALD_KEOGH_SEP_hc',
                         'ALD_EarlyWithdraw_hc', 'ALD_AlimonyPaid_hc', 'ALD_AlimonyReceived_hc',
                         'ALD_EducatorExpenses_hc', 'ALD_HSADeduction_hc', 'ALD_IRAContributions_hc',
                         'ALD_DomesticProduction_hc', 'ALD_Tuition_hc'])
        df['c02900'] = Adj(*df_args, *pl.values())

        df['invinc_ec_base'] = ALD_InvInc_ec_base(df.p22250, df.p23250, df.sep,
                       df.e00300, df.e00600, df.e01100, df.e01200)
        
        pl = get_params(['ALD_InvInc_ec_rt', 'CG_nodiff', 'CG_ec',
             'CG_reinvest_ec_rt', 'ALD_StudentLoan_hc', 'ALD_BusinessLosses_c'])
        return_capgains = CapGains(df.p23250, df.p22250, df.sep, df.invinc_ec_base, df.MARS,
             df.e00200, df.e00300, df.e00600, df.e00650, df.e00700, df.e00800,
             df.e00900, df.e01100, df.e01200, df.e01400, df.e01700, df.e02000, df.e02100,
             df.e02300, df.e00400, df.e02400, df.c02900, df.e03210, df.e03230, df.e03240,
             *pl.values())
        for out_arg, col in zip(['c01000', 'c23650', 'ymod', 'ymod1', 'invinc_agi_ec'], return_capgains):
            df[out_arg] = col

        pl = get_params(['SS_thd50', 'SS_thd85', 'SS_percentage1', 'SS_percentage2'])
        df['c02500'] = SSBenefits(df.MARS, df.ymod, df.e02400, *pl.values())

        pl = get_params(['II_em', 'II_em_ps', 'II_prt', 'II_no_em_nu18'])
        pl['II_em_ps'] = self.policy_param('II_em_ps')[df.MARS-1]
        return_AGI = AGI(df.ymod1, df.c02500, df.c02900, df.XTOT,
                         df.MARS, df.sep, df.DSI, df.exact, df.nu18, df.taxable_ubi,
                         *pl.values())
        for out_arg, col in zip(['c00100', 'pre_c04600', 'c04600'], return_AGI):
            df[out_arg] = col

        

        pl = get_params(['ID_AmountCap_rt', 'ID_AmountCap_Switch'])
        return_itemdedcap = ItemDedCap(df.e17500, df.e18400, df.e18500, df.e19200, df.e19800,
                                        df.e20100, df.e20400, df.g20500,df.c00100,
                                        *pl.values())
        out_args = ['e17500_capped', 'e18400_capped', 'e18500_capped', 'g20500_capped',
                    'e20400_capped', 'e19200_capped', 'e19800_capped', 'e20100_capped']
        for out_arg, col in zip(out_args, return_itemdedcap):
            df[out_arg] = col

        df_args = [df.e17500_capped, df.e18400_capped, df.e18500_capped, df.e19200_capped,
                   df.e19800_capped, df.e20100_capped, df.e20400_capped, df.g20500_capped,
                   df.MARS, df.age_head, df.age_spouse, df.c00100]
        pl = get_params(['ID_ps', 'ID_Medical_frt', 'ID_Medical_frt_add4aged', 'ID_Medical_hc',
                         'ID_Casualty_frt', 'ID_Casualty_hc', 'ID_Miscellaneous_frt',
                         'ID_Miscellaneous_hc', 'ID_Charity_crt_all', 'ID_Charity_crt_noncash',
                         'ID_prt', 'ID_crt', 'ID_c', 'ID_StateLocalTax_hc', 'ID_Charity_frt',
                         'ID_Charity_hc', 'ID_InterestPaid_hc', 'ID_RealEstate_hc',
                         'ID_Medical_c', 'ID_StateLocalTax_c', 'ID_RealEstate_c',
                         'ID_InterestPaid_c', 'ID_Charity_c', 'ID_Casualty_c',
                         'ID_Miscellaneous_c', 'ID_AllTaxes_c', 'ID_AllTaxes_hc',
                         'ID_StateLocalTax_crt', 'ID_RealEstate_crt', 'ID_Charity_f'])
        return_itemded = ItemDed(*df_args, *pl.values())
        out_args = ['c17000', 'c18300', 'c19200', 'c19700', 'c20500', 'c20800',
                    'c21040', 'c21060', 'c04470']
        for out_arg, col in zip(out_args, return_itemded):
            df[out_arg] = col

        pl = get_params(['AMEDT_ec', 'AMEDT_rt', 'FICA_mc_trt', 'FICA_ss_trt'])
        return_addmedtax = AdditionalMedicareTax(df.e00200, df.MARS, df.sey, df.payrolltax, *pl.values())
        for out_arg, col in zip(['ptax_amc', 'payrolltax'], return_addmedtax):
            df[out_arg] = col

        pl = get_params(['STD', 'STD_Aged', 'STD_Dep', 'STD_allow_charity_ded_nonitemizers',
                        'STD_charity_ded_nonitemizers_max'])
        df['standard'] = StdDed(df.DSI, df.earned, df.age_head, df.age_spouse,
                                df.MARS, df.MIDR, df.blind_head, df.blind_spouse,
                                df.standard, df.c19700, *pl.values())

        # Store calculated standard deduction, calculate
        # taxes with standard deduction, store AMT + Regular Tax
        std = self.array('standard').copy()
        item = self.array('c04470').copy()
        item_no_limit = self.array('c21060').copy()
        item_phaseout = self.array('c21040').copy()
        item_component_variable_names = ['c17000', 'c18300', 'c19200',
                                         'c19700', 'c20500', 'c20800']
        item_cvar = dict()
        for cvname in item_component_variable_names:
            item_cvar[cvname] = self.array(cvname).copy()
        self.zeroarray('c04470')
        self.zeroarray('c21060')
        self.zeroarray('c21040')
        for cvname in item_component_variable_names:
            self.zeroarray(cvname)
        self._taxinc_to_amt()
        std_taxes = self.array('c05800').copy()
        # Set standard deduction to zero, calculate taxes w/o
        # standard deduction, and store AMT + Regular Tax
        self.zeroarray('standard')
        self.array('c21060', item_no_limit)
        self.array('c21040', item_phaseout)
        self.array('c04470', item)
        self._taxinc_to_amt()
        item_taxes = self.array('c05800').copy()
        # Replace standard deduction with zero so the filing unit
        # would always be better off itemizing
        self.array('standard', np.where(item_taxes < std_taxes,
                                        0., std))
        self.array('c04470', np.where(item_taxes < std_taxes,
                                      item, 0.))
        self.array('c21060', np.where(item_taxes < std_taxes,
                                      item_no_limit, 0.))
        self.array('c21040', np.where(item_taxes < std_taxes,
                                      item_phaseout, 0.))
        for cvname in item_component_variable_names:
            self.array(cvname, np.where(item_taxes < std_taxes,
                                        item_cvar[cvname], 0.))
        del std
        del item
        del item_no_limit
        del item_phaseout
        del item_cvar
        # Calculate taxes with optimal itemized deduction
        self._taxinc_to_amt()


        pl = get_params(['CDCC_c', 'CDCC_ps', 'CDCC_ps2', 'CDCC_crt',
                        'CDCC_frt', 'CDCC_prt', 'CDCC_refundable'])
        return_f2441 = F2441(df.MARS, df.earned_p, df.earned_s,
                            df.f2441, df.e32800, df.exact, df.c00100,
                            df.c05800, df.e07300, df.c07180, df.CDCC_refund, *pl.values())
        for out_arg, col in zip(['c07180', 'CDCC_refund'], return_f2441):
            df[out_arg] = col



        pl = get_params(['EITC_ps', 'EITC_MinEligAge', 'EITC_MaxEligAge', 'EITC_ps_MarriedJ',
                         'EITC_rt', 'EITC_c', 'EITC_prt', 'EITC_basic_frac',
                         'EITC_InvestIncome_c', 'EITC_excess_InvestIncome_rt',
                         'EITC_indiv', 'EITC_sep_filers_elig'])
        for p in ['EITC_rt', 'EITC_ps', 'EITC_c', 'EITC_prt', 'EITC_ps_MarriedJ']:
            pl[p] = pl[p][df.EIC]
        df['c59660'] = EITC(df.MARS, df.DSI, df.EIC, df.c00100, df.e00300, df.e00400, df.e00600, df.c01000,
            df.e02000, df.e26270, df.age_head, df.age_spouse, df.earned, df.earned_p, df.earned_s,
            *pl.values())


        return_rptc = RefundablePayrollTaxCredit(df.was_plus_sey_p, df.was_plus_sey_s,
                                    *get_params(['RPTC_c', 'RPTC_rt']).values())
        df['rptc_p'], df['rptc_s'], df['rptc'] = return_rptc



        pl = get_params(['II_credit', 'II_credit_ps', 'II_credit_prt',
                         'II_credit_nr', 'II_credit_nr_ps', 'II_credit_nr_prt',
                         'RRC_c', 'RRC_ps', 'RRC_pe'])
        return_ptc = PersonalTaxCredit(df.MARS, df.c00100, df.XTOT, *pl.values())
        out_args = ['personal_refundable_credit', 'personal_nonrefundable_credit',
                    'recovery_rebate_credit']
        for out_arg, col in zip(out_args, return_ptc):
            df[out_arg] = col



        df['c10960'], df['c87668'] = AmOppCreditParts(df.exact, df.e87521, df.num, df.c00100,
                *get_params(['CR_AmOppRefundable_hc', 'CR_AmOppNonRefundable_hc']).values())
        


        df['c07200'] = SchR(df.age_head, df.age_spouse, df.MARS, df.c00100,
                            df.c05800, df.e07300, df.c07180, df.e02400, df.c02500,
                            df.e01500, df.e01700, self.policy_param('CR_SchR_hc'))



        pl = get_params(['LLC_Expense_c', 'ETC_pe_Single', 'ETC_pe_Married',
                       'CR_Education_hc'])
        df['c07230'] = EducationTaxCredit(df.exact, df.e87530, df.MARS, df.c00100, df.num, df.c05800,
                       df.e07300, df.c07180, df.c07200, df.c87668, *pl.values())

        df['charity_credit'] = CharityCredit(df.e19800, df.e20100, df.c00100, df.MARS,
            *get_params(['CR_Charity_rt', 'CR_Charity_f', 'CR_Charity_frt']).values())


        pl = get_params(['CTC_c', 'CTC_ps', 'CTC_prt', 'ODC_c', 'CR_ForeignTax_hc',
                         'CR_ResidentialEnergy_hc', 'CTC_c_under6_bonus',
                         'CTC_refundable', 'CTC_include17', 'CR_RetirementSavings_hc'])
        pl['CTC_ps'] = pl['CTC_ps'][df.MARS-1]
        return_cdtc = ChildDepTaxCredit(df.n24, df.MARS, df.c00100, df.XTOT, df.num, df.c05800,
                          df.e07260, df.e07300, df.c07180, df.c07230, df.e07240,
                          df.c07200, df.n21, df.n1820, df.exact, df.nu06, *pl.values())
        for out_arg, col in zip(['c07220', 'odc', 'codtc_limited'], return_cdtc):
            df[out_arg] = col



        pl = get_params(['CTC_refundable',
                         'CR_RetirementSavings_hc', 'CR_ForeignTax_hc',
                         'CR_ResidentialEnergy_hc', 'CR_GeneralBusiness_hc',
                         'CR_MinimumTax_hc', 'CR_OtherCredits_hc'])
        return_nfc = NonrefundableCredits(df.c07300, df.c07180, df.c07230, df.c07240, df.c07220,
                             df.c07260, df.c07400, df.c07600, df.c07200, df.c08000,
                             df.c05800, df.e07240, df.e07260, df.e07300, df.e07400,
                             df.e07600, df.p08000, df.odc,
                             df.personal_nonrefundable_credit, df.charity_credit,
                             *pl.values())
        out_args = ['c07180', 'c07200', 'c07220', 'c07230', 'c07240', 'odc',
            'c07260', 'c07300', 'c07400', 'c07600', 'c08000', 'charity_credit',
            'personal_nonrefundable_credit']
        for out_arg, col in zip(out_args, return_nfc):
            df[out_arg] = col

        pl = get_params(['ACTC_c', 'ACTC_Income_thd',
                         'ACTC_rt', 'ACTC_rt_bonus_under6family', 'ACTC_ChildNum',
                         'CTC_refundable', 'CTC_include17'])
        df['c11070'] = AdditionalCTC(df.codtc_limited, df.nu06, df.n24,
                                    df.earned, df.XTOT, df.n21, df.n1820, df.num,
                                    df.ptax_was, df.c03260, df.e09800, df.c59660, df.e11200, *pl.values())


        return_c1040 = C1040(df.c05800, df.c07180, df.c07200, df.c07220, df.c07230, df.c07240, df.c07260, df.c07300,
              df.c07400, df.c07600, df.c08000, df.e09700, df.e09800, df.e09900, df.niit, df.othertaxes,
              df.c07100, df.c09200, df.odc, df.charity_credit,
              df.personal_nonrefundable_credit,
              *get_params(['CTC_refundable']).values())
        for out_arg, col in zip(['c07100', 'othertaxes', 'c09200'], return_c1040):
            df[out_arg] = col

        pl = get_params(['CTC_new_c', 'CTC_new_rt', 'CTC_new_c_under6_bonus',
                        'CTC_new_ps', 'CTC_new_prt', 'CTC_new_for_all', 'CTC_include17',
                        'CTC_new_refund_limited', 'CTC_new_refund_limit_payroll_rt',
                        'CTC_new_refund_limited_all_payroll'])
        pl['CTC_new_ps'] = pl['CTC_new_ps'][df.MARS-1]
        df['ctc_new'] = CTC_new(df.payrolltax, df.n24, df.nu06, df.XTOT,
            df.n21, df.n1820, df.num, df.c00100, df.MARS,
            df.ptax_oasdi,df.c09200, *pl.values())

        return_iitax = IITAX(df.c59660, df.c11070, df.c10960, df.personal_refundable_credit, df.ctc_new, df.rptc,
          df.c09200, df.payrolltax, df.recovery_rebate_credit, df.eitc, df.c07220,
          df.refund, df.iitax, df.combined, df.CDCC_refund, self.policy_param('CTC_refundable'))
        for out_arg, col in zip(['eitc', 'refund', 'iitax', 'combined'], return_iitax):
            df[out_arg] = col
