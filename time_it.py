"""
Timing file for calculate.py
"""

from pandas import DataFrame, concat
from taxcalc.calculate import *
from taxcalc.puf import *
from taxcalc.parameters import *
import taxcalc.parameters as parameters



def run(puf=True, data=None):
    """
    Run each function defined in calculate.py, without saving the output to a CSV file.

    :param puf:     (boolean) set to True by default
    :param data:    (pandas.DataFrame or None) set to None by default

    For functions returning an additional non-global variable in addition
    to the DataFrame to be printed, one line saves the dataFrame to be printed
    first, and then saves the variable to be used by a following function second.
    """
    if data is None:
        data = pd.read_csv("puf2.csv")

    calc = Calculator(data)
    set_input_data(calc)
    update_globals_from_calculator(calc)
    update_calculator_from_module(calc, parameters)

    FilingStatus(calc)
    Adj()
    CapGains(calc)
    SSBenefits(calc)
    AGI(calc)
    ItemDed(puf, calc)
    df_EI_FICA, _earned = EI_FICA(calc)
    StdDed(calc)
    XYZD(calc)
    NonGain()
    df_Tax_Gains, c05750 = TaxGains(calc)
    MUI(c05750, calc)
    df_AMTI, c05800 = AMTI(puf, calc)
    df_F2441, c32800 = F2441(puf, _earned, calc)
    DepCareBen(c32800, calc)
    ExpEarnedInc(calc)
    RateRed(c05800)
    NumDep(puf, calc)
    ChildTaxCredit(calc)
    AmOppCr()
    df_LLC, c87550 = LLC(puf, calc)
    RefAmOpp()
    NonEdCr(c87550, calc)
    AddCTC(puf, calc)
    F5405()
    df_C1040, _eitc = C1040(puf)
    DEITC()
    SOIT(_eitc)



if __name__ == '__main__':
    tax_dta = pd.read_csv("puf2.csv")

    print ('jit compile running\n')
    run(data=tax_dta)
    
    from timer.timed_avg_func_calculate import *
    for i in range(5):
        print ('running iteration #{iter} \n'.format(iter=i+1))
        run(data=tax_dta)

    for funct_timer in timers:
        print(funct_timer)




