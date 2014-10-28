import os
import sys
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
from numba import jit, vectorize, guvectorize
from taxcalc import *


def test_make_Calculator():
    tax_dta = pd.read_csv("../../puf2.csv")
    calc = Calculator(tax_dta)


def test_make_Calculator_mods():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta = pd.read_csv(os.path.join(cur_path, "../../puf2.csv"))
    calc1 = calculator(tax_dta)
    calc2 = calculator(tax_dta, _amex=np.array([4000]))
    update_calculator_from_module(calc2, constants)
    update_globals_from_calculator(calc2)
    assert all(calc2._amex == np.array([4000]))
