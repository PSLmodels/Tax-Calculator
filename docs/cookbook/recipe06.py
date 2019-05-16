import numpy as np
import pandas as pd
import taxcalc as tc


# begin customizing tc.Calculator class methods and calcfunctions

def specify_pseudo_COLR_policy(self):
    """
    Specifies policy parameters for the policy in the self.current_year
    """
    # reform implementation year
    reform_year = 2020
    # one dollar refundable credit for each dollar of earnings
    self.__policy.setattr('colr_rt', 1.0)
    # ceiling on refundable credit varies by type of filing unit
    valuelist = [4000.0, 8000.0, 4000.0, 4000.0, 4000.0]
    self.__policy.setattr('colr_c', np.array(valuelist, np.float64))
    # AGI phase-out start threshold varies by type of filing unit
    valuelist = [30000.0, 50000.0, 30000.0, 30000.0, 30000.0]
    self.__policy.setattr('colr_ps', np.array(valuelist, np.float64))
    # credit phase-out rate per dollar of AGI above phase-out start threshold
    self.__policy.setattr('colr_prt', 0.20)
    # set parameters for years other than reform_year
    this_year = self.current_year
    if self.colr_active and this_year >= reform_year:
        # set inflation-indexed values of colr_c and colr_ps for this_year
        irates = self.__policy.inflation_rates()
        syr = Policy.JSON_START_YEAR
        for param in ['colr_c', 'colr_ps']:
            value = self.__policy.getattr(param)
            for year in range(reform_year, this_year):
                value *= (1.0 + irates[year - syr])
            self.__policy.setattr(param, value)
    else:
        # set credit ceiling to zero
        valuelist = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.__policy.setattr('colr_c', np.array(valuelist, np.float65))

@tc.iterate_jit(nopython=True)
def pseudo_COLR(e00200, MARS, col_refund, iitax, combined):
    """
    Calculates pseudo Cost-of-Living Refund amount.
    Note this is simply meant to illustrate a Python programming technique;
    this function does NOT calculate the exact Cost-of-Living Refund amount.
    """
    # calculate pseudo refund amount
    col_refund = 1000.
    # reduce income & combined tax liability because it is a refundable credit
    iitax -= col_refund
    combined -= col_refund
    return (col_refund, iitax, combined)
    
# end new calcfunctions used by customized Calculator class

class Calculator(tc.Calculator):
    """
    Customized tc.Calculator class that inherits all tc.Calculator methods
    and calcfunctions, adding/overriding some to get desired customization.
    """
    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None,
                 # new Calculator constructor argument used in customization
                 colr_active=False):
        # start with same class constructor arguments as tc.Calculator class
        super().__init__(policy=policy, records=records,
                         verbose=verbose, sync_years=sync_years,
                         consumption=consumption)
        # remember whether pseudo_COLR is active or not
        self.colr_active = colr_active

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
        # specify new Records variable to hold pseudo COLR amount
        zeros = np.zeros(self.__records.array_length, dtype=np.float64)
        setattr(self.__records, 'col_refund', zeros)
        # specify new Policy parameters to characterize pseudo COLR policy
        
        # call new function that calculates pseudo COLRefund amount
        pseudo_COLR(self.__policy, self.__records)  # (see above)
        tc.ExpandIncome(self.__policy, self.__records)
        tc.AfterTaxIncome(self.__policy, self.__records)

# end of customized Calculator class definition

# top-level logic of program that uses customized Calculator class

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

# specify customized Calculator objects using bpolicy and rpolicy
recs = tc.Records.cps_constructor()
calc1 = Calculator(policy=bpolicy, records=recs)
calc2 = Calculator(policy=rpolicy, records=recs)

cyr = 2018

# calculate for specified cyr
calc1.advance_to_year(cyr)
calc1.calc_all()
calc2.advance_to_year(cyr)
calc2.calc_all()

# compare aggregate individual income tax revenue in cyr
iitax_rev1 = calc1.weighted_total('iitax')
iitax_rev2 = calc2.weighted_total('iitax')

# print total revenue estimates for cyr
# (estimates in billons of dollars)
print('{}_REFORM1_iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev1 * 1e-9))
print('{}_REFORM2_iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev2 * 1e-9))
print('')
