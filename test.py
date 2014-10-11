"""
Testing file for calculate.py
"""

from pandas import DataFrame, Series
from taxcalc.calculate import *


def run(puf=True):
    FilingStatus().to_csv('FilingStatus.csv')
    Adj().to_csv('Adj.csv')
    CapGains().to_csv('CapGains.csv')
    SSBenefits().to_csv('SSBenefits.csv')
    AGI().to_csv('AGI.csv')
    ItemDed(puf).to_csv('ItemDed.csv')
    df_EI_FICA, _earned = EI_FICA()
    df_EI_FICA.to_csv('EIFICA.csv')
    StdDed().to_csv('StdDed.csv')
    XYZD().to_csv('XYZD.csv')
    NonGain().to_csv('NonGain.csv')
    df_Tax_Gains, c05750 = TaxGains()
    df_Tax_Gains.to_csv('Taxgains.csv')
    MUI(c05750).to_csv('MUI.csv', header=True, index_label='c05750')
    df_AMTI, c05800 = AMTI(puf)
    df_AMTI.to_csv('AMTI.csv')
    df_F2441, c32800 = F2441(puf, _earned)
    df_F2441.to_csv('F2441.csv')
    DepCareBen(c32800).to_csv('DepCareBen.csv')
    ExpEarnedInc().to_csv('ExpEarnedInc.csv')
    RateRed(c05800).to_csv('RateRed.csv')
    NumDep(puf).to_csv('NumDep.csv')
    ChildTaxCredit().to_csv('ChildTaxCredit.csv')
    AmOppCr().to_csv('AmOppCr.csv')
    df_LLC, c87550 = LLC(puf)
    df_LLC.to_csv('LLC.csv')
    RefAmOpp().to_csv('RefAmOpp.csv')
    NonEdCr(c87550).to_csv('NonEdCr.csv')
    AddCTC(puf).to_csv('AddCTC.csv')
    F5405().to_csv('F5405.csv')
    df_C1040, _eitc = C1040(puf)
    df_C1040.to_csv('C1040.csv')
    DEITC().to_csv('DEITC.csv')
    SOIT(_eitc).to_csv('SOIT.csv')

if __name__ == '__main__':
    run()

