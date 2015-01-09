"""
Testing file for calculate.py
"""

from pandas import DataFrame, concat
from taxcalc.calculate import *
from taxcalc.puf import *
from taxcalc.parameters import *
import taxcalc.parameters as parameters
#from timer.timed_calculate import *


def to_csv(fname, df):
    """
    Save this dataframe to a CSV file with name 'fname' and containing
    a header with the column names of the dataframe.
    """
    df.to_csv(fname, float_format= '%1.3f', sep=',', header=True, index=False)



def run(puf=True):
    """
    Run each function defined in calculate.py, saving the ouput to a CSV file.
    'puf' set to True by default, to use the 'puf2.csv' as an input
    
    For functions returning an additional non-global variable in addition
    to the DataFrame to be printed, one line saves the dataFrame to be printed 
    first, and then saves the variable to be used by a following function second. 
    """
    tax_dta = pd.read_csv("puf2.csv")

    calc = Calculator(tax_dta)
    set_input_data(calc)
    update_globals_from_calculator(calc)

    update_calculator_from_module(calc, parameters)

    calculated = DataFrame()

    calculated = concat([calculated, FilingStatus(calc)], axis=1)
    calculated = concat([calculated, Adj(calc)], axis=1)
    calculated = concat([calculated, CapGains(calc)], axis = 1)
    calculated = concat([calculated, SSBenefits(calc)], axis=1)
    calculated = concat([calculated, AGI(calc)], axis=1)
    calculated = concat([calculated, ItemDed(puf, calc)], axis=1)
    df_EI_FICA, _earned = EI_FICA(calc)
    calculated = concat([calculated, df_EI_FICA], axis=1)
    calculated = concat([calculated, StdDed(calc)], axis=1)
    calculated = concat([calculated, XYZD(calc)], axis=1)
    calculated = concat([calculated, NonGain(calc)], axis=1)
    df_Tax_Gains = TaxGains(calc)
    calculated = concat([calculated, df_Tax_Gains], axis=1)
    calculated = concat([calculated, MUI(df_Tax_Gains.c05750, calc)], axis=1)
    df_AMTI, c05800 = AMTI(puf, calc)
    calculated = concat([calculated, df_AMTI], axis=1)
    df_F2441, c32800 = F2441(puf, _earned, calc)
    calculated = concat([calculated, df_F2441], axis=1)
    calculated = concat([calculated, DepCareBen(c32800, calc)], axis=1)
    calculated = concat([calculated, ExpEarnedInc(calc)], axis=1)
    calculated = concat([calculated, RateRed(c05800, calc)], axis=1)
    calculated = concat([calculated, NumDep(puf, calc)], axis=1)
    calculated = concat([calculated, ChildTaxCredit(calc)], axis=1)
    calculated = concat([calculated, AmOppCr(calc)], axis=1)
    df_LLC, c87550 = LLC(puf, calc)
    calculated = concat([calculated, df_LLC], axis=1)
    calculated = concat([calculated, RefAmOpp(calc)], axis=1)
    calculated = concat([calculated, NonEdCr(c87550, calc)], axis=1)
    calculated = concat([calculated, AddCTC(puf, calc)], axis=1)
    calculated = concat([calculated, F5405()], axis=1)
    df_C1040, _eitc = C1040(puf, calc)
    calculated = concat([calculated, df_C1040], axis=1)
    calculated = concat([calculated, DEITC(calc)], axis=1)
    calculated = concat([calculated, SOIT(_eitc, calc)], axis=1)
    to_csv("results.csv", calculated)


if __name__ == '__main__':
    run()
