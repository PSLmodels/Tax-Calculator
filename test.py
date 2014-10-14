"""
Testing file for calculate.py
"""

from pandas import DataFrame
from taxcalc.calculate import *


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
    to_csv('FilingStatus.csv', FilingStatus())
    to_csv('Adj.csv', Adj())
    to_csv('CapGains.csv', CapGains())
    to_csv('SSBenefits.csv', SSBenefits())
    to_csv('AGI.csv', AGI())
    to_csv('ItemDed.csv', ItemDed(puf))
    df_EI_FICA, _earned = EI_FICA()
    to_csv('EIFICA.csv', df_EI_FICA)
    to_csv('StdDed.csv', StdDed())
    to_csv('XYZD.csv', XYZD())
    to_csv('NonGain.csv', NonGain())
    df_Tax_Gains, c05750 = TaxGains()
    to_csv('Taxgains.csv', df_Tax_Gains)
    to_csv('MUI.csv', MUI(c05750))
    df_AMTI, c05800 = AMTI(puf)
    to_csv('AMTI.csv', df_AMTI)
    df_F2441, c32800 = F2441(puf, _earned)
    to_csv('F2441.csv', df_F2441)
    to_csv('DepCareBen.csv', DepCareBen(c32800))
    to_csv('ExpEarnedInc.csv', ExpEarnedInc())
    to_csv('RateRed.csv', RateRed(c05800))
    to_csv('NumDep.csv', NumDep(puf))
    to_csv('ChildTaxCredit.csv', ChildTaxCredit())
    to_csv('AmOppCr.csv', AmOppCr())
    df_LLC, c87550 = LLC(puf)
    to_csv('LLC.csv', df_LLC)
    to_csv('RefAmOpp.csv', RefAmOpp())
    to_csv('NonEdCr.csv', NonEdCr(c87550))
    to_csv('AddCTC.csv', AddCTC(puf))
    to_csv('F5405.csv', F5405())
    df_C1040, _eitc = C1040(puf)
    to_csv('C1040.csv', df_C1040)
    to_csv('DEITC.csv', DEITC())
    to_csv('SOIT.csv', SOIT(_eitc))

if __name__ == '__main__':
    run()

