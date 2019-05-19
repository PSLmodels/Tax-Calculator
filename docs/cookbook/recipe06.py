"""
Recipe that illustrates how to customize the taxcalc Calculator class so that
it can analyze a non-parametric reform (that is, a reform that cannot be
represented using existing taxcalc Policy parameters.

The technique for doing this customization is standard in object-oriented
programming.  A new, customized class is derived from another class.  The
derived class inherits all the data and methods of the parent class, but
can be customized by adding new data and methods or by overriding inherited
methods.

The reform used to illustrate this programming technique is somewhat like
the Cost-of-Living Refund, a refundable credit that was being discussed in
tax policy circles during 2019 as a replacement for the EITC.  But the
reform analyzed here is not exactly like the Cost-of-Living Refund, so we
call it a pseudo cost-of-living refund to emphasize that it is not meant
to be an accurate representation of the Cost-of-Living Refund proposal.
"""
import numpy as np
import pandas as pd
import taxcalc as tc


class Calculator(tc.Calculator):
    """
    Customized tc.Calculator class that inherits all tc.Calculator methods,
    adding or overriding some to get the desired customization.
    """
    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None,
                 # new Calculator constructor argument used in customization
                 colr_active=False):
        # start with same class constructor arguments as tc.Calculator class
        super().__init__(policy=policy, records=records,
                         verbose=verbose, sync_years=sync_years,
                         consumption=consumption)
        # remember whether pseudo_COLR policy is active or not
        self.colr_active = colr_active

    def specify_pseudo_COLR_policy(self):
        """
        Specifies policy parameters for the COLR policy in the current_year.
        See use of these parameters below in the pseudo_COLR_amount method.
        """
        # reform implementation year
        reform_year = 2020
        # specify dictionary of parameter names and values for reform_year
        self.colr_param = {
            # credit phase-in rate on earnings
            'COLR_rt': 1.0,
            # ceiling on refundable credit varies by filing-unit type, MARS
            'COLR_c': np.array([4000.0, 8000.0, 4000.0, 4000.0, 4000.0],
                               dtype=np.float64),
            # credit phase-out start AGI level varies by filing-unit type, MARS
            'COLR_ps': np.array([30000.0, 50000.0, 30000.0, 30000.0, 30000.0],
                                dtype=np.float64),
            # credit phase-out rate per dollar of AGI above COLR_ps level
            'COLR_prt': 0.2
        }
        # set pseudo COLR parameter values for current year
        this_year = self.current_year
        if self.colr_active and this_year >= reform_year:
            # set inflation-indexed values of COLR_c and COLR_ps for this_year
            irates = self.__policy.inflation_rates()
            syr = tc.Policy.JSON_START_YEAR
            for name in ['COLR_c', 'COLR_ps']:
                value = self.colr_param[name]
                for year in range(reform_year, this_year):
                    value *= (1.0 + irates[year - syr])
                self.colr_param[name] = np.round(value, 2)  # to nearest penny
        else:  # if policy not active or if this year is before the reform year
            # set pseudo COLR ceiling amount to zero
            self.colr_param['COLR_c'] = np.array([0.0, 0.0, 0.0, 0.0, 0.0],
                                                  dtype=np.float64)
        tracing = False
        if tracing:
            for name in self.colr_param:
                print('> {} {} {}'.format(
                    this_year, name, self.colr_param[name]
                ))

    def pseudo_COLR_amount(self):
        """
        Calculates pseudo Cost-of-Living Refund amount.
        Note this is simply meant to illustrate a Python programming technique;
        this function does NOT calculate an exact Cost-of-Living Refund amount.
        See setting of parameters above in specify_pseudo_COLR_policy method.
        """
        recs = self.__records
        # create MARS-specific policy parameter arrays
        mars_list = [recs.MARS == 1, recs.MARS == 2, recs.MARS == 3,
                     recs.MARS == 4, recs.MARS == 5]
        colr_c = np.select(mars_list, self.colr_param['COLR_c'])
        colr_ps = np.select(mars_list, self.colr_param['COLR_ps'])
        colr_rt = self.colr_param['COLR_rt']
        colr_prt = self.colr_param['COLR_prt']
        # compute colr_amt
        amt_pre_phaseout = np.minimum(recs.e00200 * colr_rt, colr_c)
        phaseout = np.maximum((recs.c00100 - colr_ps) * colr_prt, 0.)
        colr_amt = np.maximum(amt_pre_phaseout - phaseout, 0.)
        setattr(recs, 'COLR_amount', colr_amt)
        # reduce income and combined taxes because COLR is a refundable credit
        recs.iitax -= colr_amt
        recs.combined -= colr_amt
        # delete local arrays used only in this method
        del mars_list
        del colr_c
        del colr_ps
        del amt_pre_phaseout
        del phaseout
        del colr_amt

    def calc_all(self, zero_out_calc_vars=False):
        """
        Call all tax-calculation functions for the current_year.
        """
        tc.BenefitPrograms(self)
        self._calc_one_year(zero_out_calc_vars)
        tc.BenefitSurtax(self)
        tc.BenefitLimitation(self)
        tc.FairShareTax(self.__policy, self.__records)
        tc.LumpSumTax(self.__policy, self.__records)
        # specify new Policy parameters to characterize pseudo COLR policy
        self.specify_pseudo_COLR_policy()  # (see above)
        # call new method that calculates pseudo COLR amount
        self.pseudo_COLR_amount()  # (see above)
        tc.ExpandIncome(self.__policy, self.__records)
        tc.AfterTaxIncome(self.__policy, self.__records)

# end of customized Calculator class definition


# top-level logic of program that uses customized Calculator class

"""
# read an "old" reform file from Tax-Calculator website
# ("old" means the reform file is defined relative to pre-TCJA policy)
reforms_url = ('https://raw.githubusercontent.com/'
               'PSLmodels/Tax-Calculator/master/taxcalc/reforms/')

# specify reform dictionary for pre-TCJA policy
reform1 = tc.Policy.read_json_reform(reforms_url + '2017_law.json')

# specify reform dictionary for TCJA as passed by Congress in late 2017
reform2 = tc.Policy.read_json_reform(reforms_url + 'TCJA.json')

# specify Policy object for pre-TCJA policy
bpolicy = tc.Policy()
bpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
assert not bpolicy.parameter_errors

# specify Policy object for TCJA reform relative to pre-TCJA policy
rpolicy = tc.Policy()
rpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
assert not rpolicy.parameter_errors
rpolicy.implement_reform(reform2, print_warnings=False, raise_errors=False)
assert not rpolicy.parameter_errors
"""

bpolicy = tc.Policy()
rpolicy = tc.Policy()

# specify customized Calculator objects using bpolicy and rpolicy
recs = tc.Records.cps_constructor()
calc1 = Calculator(policy=bpolicy, records=recs, colr_active=False)
calc2 = Calculator(policy=rpolicy, records=recs, colr_active=True)

for cyr in range(2018, 2022 + 1):
    # advance to and calculate for specified cyr
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    calc2.advance_to_year(cyr)
    calc2.calc_all()
    # extract weighted amounts
    iitax_funits = calc1.total_weight()
    iitax_reven1 = calc1.weighted_total('iitax')
    iitax_reven2 = calc2.weighted_total('iitax')
    colr_amount = calc2.weighted_total('COLR_amount')
    # print weighted amounts for cyr
    line = 'YEAR,NUM,ITAX1,ITAX2,COLR=  {}  {:.3f}  {:.3f}  {:.3f}  {:.3f}'
    print(line.format(
        cyr,
        iitax_funits * 1e-6,
        iitax_reven1 * 1e-9,
        iitax_reven2 * 1e-9,
        colr_amount * 1e-9
    ))
