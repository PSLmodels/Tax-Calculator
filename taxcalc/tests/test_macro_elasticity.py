import pandas as pd
import sys
import os
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator
from taxcalc.macro_elasticity import *

TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91taxdata.csv.gz')
TAXDATA = pd.read_csv(TAXDATA_PATH, compression='gzip')
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91weights.csv.gz')
WEIGHTS = pd.read_csv(WEIGHTS_PATH, compression='gzip')


def test_percentage_change_gdp():
    policy1 = Policy()
    records1 = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(policy=policy1, records=records1)
    calc1.calc_all()

    reform = {2013: 
        {"_STD": [[12600, 25200, 12600, 18600, 25300, 12600, 2100]],
         "_AMT_trt1": [0.0],
         "_AMT_trt2": [0.0]}}
        
    policy2 = Policy()
    policy2.implement_reform(reform)

    records2 = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(policy=policy2, records=records2)
    calc2.calc_all()

    gdp_diff = percentage_change_gdp(calc1, calc2, elasticity=0.36)
    assert gdp_diff > 0
