"""
Testing file for ation.py
"""

from translation import *

if __name__ == '__main__':

    puf = PUF
    
    FilingStatus()
    Adj()
    CapGains()
    SSBenefits()
    AGI()
    ItemDed(puf)
    _earned = EI_FICA()
    StdDed()
    XYZD()
    NonGain()
    c05750 = TaxGains()
    MUI(c05750)
    c05800 = AMTI(puf)
    c32800 = F2441(puf, _earned)
    DepCareBen(c32800)
    ExpEarnedInc()
    RateRed(c05800)
    NumDep(puf)
    ChildTaxCredit()
    AmOppCr()
    c87550 = LLC(puf)
    RefAmOpp()
    NonEdCr(c87550)
    AddCTC(puf)
    F5405()
    _eitc = C1040(puf)
    DEITC()
    SOIT(_eitc)



