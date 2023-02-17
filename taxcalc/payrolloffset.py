"""
employer side payroll tax offset function
"""
import copy
import numpy as np
import taxcalc as tc
from taxcalc.policy import Policy
from taxcalc.records import Records

def employer_payroll_offset(reform, ccalc, cpolicy, rrecs, dump=False):
    """
    This function constructs a new calculator object to consider the employer side payroll tax change offset upon
    an input calculator object and an input reform. It implement the offset under the calculator object's current year.
    Calculation methods of this function follow the CBO article "THE INCOME AND PAYROLL TAX OFFSET TO CHANGES IN 
    PAYROLL TAX REVENUES" at https://www.jct.gov/publications/2016/jcx-89-16/
    
    Basic logic is that, under the assumption of the total compensation from the employer to the employee remains the 
    same at all time, an increase on the employer side payroll tax rate will result in a decrease in the employee's wages, 
    which will then result in a decrease the income tax revenue from the employee side. 
    
    Note: OASDI social security tax have a maximum taxable value, $118500 in 2016. For wages below this value, the wages
    will be taxed by the actual value of the wages; for wages above this value, the employee will be taxed by this OASID 
    maximum taxable value.
    
    Specifically, (1) for employee whose wage is below the OASDI taxable maximum value:
    After offset Wage = Base Wage * (1 + rate1_FICA_mc_trt_employer + rate1_FICA_ss_trt_employer)/
                                    (1 + rate2_FICA_mc_trt_employer + rate2_FICA_ss_trt_employer)
    (2) for employee whose wage is above the OASDI taxable maximum value:
    total compensation = (1 + rate1_FICA_mc_trt_employer) * Base Wage + rate1_FICA_ss_trt_employer * OASDI max taxable amount
    After offset Wage = (total compensation - rate2_FICA_ss_trt_employer * OASDI max taxable amount ) 
                        / (1 + rate2_FICA_mc_trt_employer)
    
    Note: this function internally modifies a copy of the ccalc, cpolicy, crecs to account for the tax offset.
    None of them are affected by this offset function.
    
    
    Parameters
    -------
    reform: dict
        reform to be implemented
    
    ccalc: Caculator object
        original calculator object before the reform and the tax offset
    
    cpolicy: dict
        policy of the ccalc object
    
    rrecs: dict
        record of the ccalc object
        
    dump: boolean
        when the value is False, the function will return the dataframe of tc.DIST_VARIABLES,
        a short list of output variables 
        when the value is True, the function will return the dataframe of a full list of taxcalculator
        input and output variables 
    
    
    
    Returns
    -------
    df: dataframe
        the dataframe of (output and input) variables of the calculator object after the implementation of the offset of
        employer side payroll tax
        
    Notes
    -------
    The most efficient way to conduct the offset analysis is as follows:
    
    Especially, when conducting multi-year analysis

    """
    # Check if the employer side payroll tax parameters are changed in this reform
    if reform.get("FICA_ss_trt_employer") or reform.get("FICA_mc_trt_employer") is not None:
        
        # make deep copy for the calculator variable from the argument, to be used internally only; their value will not be changed outside of this function
        # To be noticed calc is a tool calculator object. It does not represent the calculator object after the implementation of offset (problems will appear when doing multi year analysis)
        calc = copy.deepcopy(ccalc)
        dpolicy = copy.deepcopy(cpolicy)
        drecs = copy.deepcopy(rrecs)
        # Check function argument types
        assert isinstance(calc, tc.Calculator)
        assert isinstance(reform, dict)
        assert isinstance(dpolicy, Policy)
        assert isinstance(drecs, Records)
        
        # make copy of the employer side payroll tax rate before the reform
        rate1_FICA_mc_trt_employer = calc.policy_param('FICA_mc_trt_employer')
        rate1_FICA_ss_trt_employer = calc.policy_param('FICA_ss_trt_employer')
        
        # implement the reform
        CYR = calc.current_year
        dpolicy.implement_reform(reform, print_warnings=False, raise_errors=False)
        calc = tc.Calculator(policy=dpolicy, records=drecs)
        calc.advance_to_year(CYR)
        calc.calc_all()
        
        # make copy of the employer side payroll tax rate after the reform
        rate2_FICA_mc_trt_employer = calc.policy_param('FICA_mc_trt_employer')
        rate2_FICA_ss_trt_employer = calc.policy_param('FICA_ss_trt_employer')
        
        # Calculate the employer side payroll tax offset rate
        offset_rate = (1 + rate1_FICA_mc_trt_employer + rate1_FICA_ss_trt_employer)/(1 + rate2_FICA_mc_trt_employer + rate2_FICA_ss_trt_employer)
        # wage & income above this maximum of OASDI taxable value will be taxed at this value, instead of the value of wage       
        taxmax = calc.policy_param('SS_Earnings_c')
        
        # Implement the employer payroll tax offset upon individual taxpayers e00200p, e00200s
        # e00200 the filling unit will be calculated based upon e00200p and e00200s

        pre_wage_p = calc.array('e00200p')        
        # check if the taxpaer's wage & income is above or below the maximum OASDI taxable value
        oasdi_capped_p = pre_wage_p < taxmax
        # Calculate the offset for the taxpayer's wage & income which is above the maximum OASDI taxable value
        total_comp_above_line_p = (1 + rate1_FICA_mc_trt_employer) * pre_wage_p + rate1_FICA_ss_trt_employer * taxmax
        new_wage_above_line_p = (total_comp_above_line_p - rate2_FICA_ss_trt_employer * taxmax ) / (1 + rate2_FICA_mc_trt_employer)
        # Calculate the offset for the taxpayer's wage & income which is below the maximum OASDI taxable value
        new_wage_below_line_p = pre_wage_p * offset_rate
        new_wage_p  = np.where(oasdi_capped_p, new_wage_below_line_p, new_wage_above_line_p)
        calc.zeroarray('e00200p')
        calc.incarray('e00200p', new_wage_p)
        
        pre_wage_s = calc.array('e00200s')        
        # check if the taxpaer's wage & income is above or below the maximum OASDI taxable value
        oasdi_capped_s = pre_wage_s < taxmax
        # Calculate the offset for the taxpayer's wage & income which is above the maximum OASDI taxable value
        total_comp_above_line_s = (1 + rate1_FICA_mc_trt_employer) * pre_wage_s + rate1_FICA_ss_trt_employer * taxmax
        new_wage_above_line_s = (total_comp_above_line_s - rate2_FICA_ss_trt_employer * taxmax ) / (1 + rate2_FICA_mc_trt_employer)
        # Calculate the offset for the taxpayer's wage & income which is below the maximum OASDI taxable value
        new_wage_below_line_s = pre_wage_s * offset_rate
        new_wage_s  = np.where(oasdi_capped_s, new_wage_below_line_s, new_wage_above_line_s)
        calc.zeroarray('e00200s')
        calc.incarray('e00200s', new_wage_s)
        
        # note: e00200 is calculated through e00200 = e00200p + e00200s, instead of multiplying the offset rate which may cause this equation not held because of the decimial issues
        new_wage = new_wage_s + new_wage_p
        calc.zeroarray('e00200')
        calc.incarray('e00200', new_wage)
        
        
        calc.calc_all()
        
        # extract dataframe from calc
        if dump:
            recs_vinfo = tc.Records(data=None)  # contains records VARINFO only
            dvars = list(recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS)
            df = calc.dataframe(dvars)

        else:
            df = calc.dataframe(tc.DIST_VARIABLES)
        
        # delete the tool calculator
        del calc
        
        # return to the dataframe
        return df
    
    # If there is no change upon the empoyersie payroll tax rate, then no offset will be implemented
    else:
        if dump:
            recs_vinfo = tc.Records(data=None)  # contains records VARINFO only
            dvars = list(recs_vinfo.USABLE_READ_VARS | recs_vinfo.CALCULATED_VARS)
            df = ccalc.dataframe(dvars)

        else:
            df = ccalc.dataframe(tc.DIST_VARIABLES)
        return df

