import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import pandas as pd
from taxcalc import Parameters, Records, Calculator, behavior


WEIGHTS_FILENAME = "../../WEIGHTS_testing.csv"
WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
WEIGHTS = pd.read_csv(WEIGHTS_PATH)

TAX_DTA_PATH = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")
TAX_DTA = pd.read_csv(TAX_DTA_PATH, compression='gzip')
# data fix-up: midr needs to be type int64 to match PUF
TAX_DTA['midr'] = TAX_DTA['midr'].astype('int64')


def test_make_behavioral_Calculator():
    # create a Records and Params object
    records_x = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    records_y = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    params_x = Parameters()
    params_y = Parameters()
    # create two Calculators
    calc_x = Calculator(params=params_x, records=records_x)
    calc_y = Calculator(params=params_y, records=records_y)
    # implement a plan Y reform
    reform = {2013: {"_II_rt7": [0.496]}}
    params_y.implement_reform(reform)
    # Create behavioral calculators and vary both kwargs.
    calc_y_behavior1 = behavior(calc_x, calc_y,
                                elast_wrt_atr=0.4, inc_effect=0.15)
    calc_y_behavior2 = behavior(calc_x, calc_y,
                                elast_wrt_atr=0.5, inc_effect=0.15)
    calc_y_behavior3 = behavior(calc_x, calc_y,
                                elast_wrt_atr=0.4, inc_effect=0)
    assert (calc_y_behavior1.records._ospctax.sum() !=
            calc_y_behavior2.records._ospctax.sum() !=
            calc_y_behavior3.records._ospctax.sum())
