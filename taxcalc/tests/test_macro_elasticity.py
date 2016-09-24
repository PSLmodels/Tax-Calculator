import os
import sys
import pandas as pd
import pytest
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
from taxcalc import proportional_change_gdp  # pylint: disable=import-error

# use 1991 PUF-like data to emulate current puf.csv, which is private
TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91taxdata.csv.gz')
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91weights.csv.gz')


def test_proportional_change_gdp():
    policy1 = Policy()
    recs1 = Records(data=TAXDATA_PATH, weights=WEIGHTS_PATH, start_year=2009)
    calc1 = Calculator(policy=policy1, records=recs1)
    policy2 = Policy()
    reform = {2013: {'_II_em': [0.0]}}
    policy2.implement_reform(reform)
    recs2 = Records(data=TAXDATA_PATH, weights=WEIGHTS_PATH, start_year=2009)
    calc2 = Calculator(policy=policy2, records=recs2)
    gdp_diff = proportional_change_gdp(calc1, calc2, elasticity=0.36)
    assert gdp_diff > 0
