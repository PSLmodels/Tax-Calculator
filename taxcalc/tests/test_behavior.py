import os
import sys
import json
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import tempfile
import pytest
from taxcalc import *
import copy

WEIGHTS_FILENAME = "../../WEIGHTS_testing.csv"
weights_path = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
weights = pd.read_csv(weights_path)

all_cols = set()
tax_dta_path = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")
tax_dta = pd.read_csv(tax_dta_path, compression='gzip')

# Fix-up. MIdR needs to be type int64 to match PUF
tax_dta['midr'] = tax_dta['midr'].astype('int64')
tax_dta['s006'] = np.arange(0, len(tax_dta['s006']))

irates = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024}


def test_make_behavioral_Calculator():
    # Create a Records and Params object
    records_x = Records(tax_dta)
    records_y = Records(tax_dta)
    params_x = Parameters(start_year=1991, inflation_rates=irates)
    params_y = Parameters(start_year=1991, inflation_rates=irates)
    # Create two Calculators
    calcX = Calculator(params_x, records_x)
    calcY = Calculator(params_y, records_y)
    # Implement a plan Y reform
    reform = {1991: {"_II_rt7": [0.496],
                     "_BE_sub": [0.4],
                     "_BE_inc": [0.15]}}
    params_y.implement_reform(reform)
    # Create behavioral calculators and vary both kwargs.
    calcY_behavior1 = behavior(calcX, calcY)
    reform = {1991: {
                     "_II_rt7": [0.496],
                     "_BE_sub": [0.5],
                     "_BE_inc": [0.15]
              }}
    params_y.implement_reform(reform)
    calcY_behavior2 = behavior(calcX, calcY)
    reform = {1991: {"_II_rt7": [0.496],
                     "_BE_sub": [0.4],
                     "_BE_inc": [0.0]}}
    params_y.implement_reform(reform)
    calcY_behavior3 = behavior(calcX, calcY)
    assert (calcY_behavior1.records._ospctax.sum() !=
            calcY_behavior2.records._ospctax.sum() !=
            calcY_behavior3.records._ospctax.sum())
