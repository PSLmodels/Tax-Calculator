import pandas as pd
from pandas import DataFrame
import math
import numpy as np
from .utils import *
#from .parameters import *
from .functions import *

class Calculator(object):

    def __init__(self, parameters, puf):
        self.parameters = parameters
        self.puf = puf
        assert puf.current_year == parameters.current_year

    def calc_all(self):
        FilingStatus(self.parameters, self.puf)
        Adj(self.parameters, self.puf)
        CapGains(self.parameters, self.puf)
        SSBenefits(self.parameters, self.puf)
        AGI(self.parameters, self.puf)
        #ItemDed(puf, calc)], axis=1)
        """EI_FICA(calc)
        df_EI_FICA], axis=1)
        StdDed(calc)], axis=1)
        XYZD(calc)], axis=1)
        NonGain()], axis=1)
        TaxGains(calc)
        df_Tax_Gains], axis=1)
        MUI(c05750, calc)], axis=1)
        AMTI(puf, calc)
        df_AMTI], axis=1)
        F2441(puf, _earned, calc)
        df_F2441], axis=1)
        DepCareBen(c32800, calc)], axis=1)
        ExpEarnedInc(calc)], axis=1)
        RateRed(c05800)], axis=1)
        NumDep(puf, calc)], axis=1)
        ChildTaxCredit(calc)], axis=1)
        AmOppCr()], axis=1)
        LLC(puf, calc)
        df_LLC], axis=1)
        RefAmOpp()], axis=1)
        NonEdCr(c87550, calc)], axis=1)
        AddCTC(puf, calc)], axis=1)
        F5405()], axis=1)
        C1040(puf)
        DEITC()], axis=1)
        SOIT(_eitc)], axis=1)"""

    def increment_year(self):
        self.puf.increment_year()
        self.parameters.increment_year()

    @property
    def current_year(self):
        return self.parameters.current_year

"""class Calculator(object):

    def __init__(self, data, default_year=2013):
        self.tax_data = data
        self.DEFAULT_YR = default_year"""


def calculator(data, mods="", **kwargs):
    if mods:
        import json
        dd = json.loads(mods)
        dd = {k:np.array(v) for k,v in dd.items() if type(v) == list}
        kwargs.update(dd)

    calc = Calculator(data)
    if kwargs:
        calc.__dict__.update(kwargs)
    return calc
