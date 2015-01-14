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
        ItemDed(self.parameters, self.puf)
        EI_FICA(self.parameters, self.puf)
        StdDed(self.parameters, self.puf)
        XYZD(self.parameters, self.puf)
        NonGain(self.parameters, self.puf)
        TaxGains(self.parameters, self.puf)
        MUI(self.parameters, self.puf)
        AMTI(self.parameters, self.puf)
        F2441(self.parameters, self.puf)
        DepCareBen(self.parameters, self.puf)
        ExpEarnedInc(self.parameters, self.puf)
        RateRed(self.parameters, self.puf)
        NumDep(self.parameters, self.puf)
        ChildTaxCredit(self.parameters, self.puf)
        AmOppCr(self.parameters, self.puf)
        LLC(self.parameters, self.puf)
        RefAmOpp(self.parameters, self.puf)
        NonEdCr(self.parameters, self.puf)
        AddCTC(self.parameters, self.puf)
        F5405(self.parameters, self.puf)
        C1040(self.parameters, self.puf)
        DEITC(self.parameters, self.puf)
        SOIT(self.parameters, self.puf)

    def increment_year(self):
        self.puf.increment_year()
        self.parameters.increment_year()

    @property
    def current_year(self):
        return self.parameters.current_year


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
