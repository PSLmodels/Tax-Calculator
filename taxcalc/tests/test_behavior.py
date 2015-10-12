import os
import sys
import numpy as np
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import pandas as pd
from taxcalc import Policy, Records, Calculator, behavior, Behavior, Growth


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
    policy_x = Policy()
    policy_y = Policy()
    # create two Calculators
    behavior_y = Behavior()
    calc_x = Calculator(policy=policy_x, records=records_x)
    calc_y = Calculator(policy=policy_y, records=records_y,
                        behavior=behavior_y)
    # Implement a plan Y reform
    reform = {
        2013: {
            "_II_rt7": [0.496]
        }
    }
    policy_y.implement_reform(reform)

    # Update behavior from defaults
    new_behavior = {
        2013: {
            "_BE_sub": [0.4],
            "_BE_inc": [0.15]
        }
    }

    behavior_y.update_behavior(new_behavior)

    # Create behavioral calculators and vary substitution and income effects.
    calc_y_behavior1 = behavior(calc_x, calc_y)

    new_behavior = {
        2013: {
            "_BE_sub": [0.5],
            "_BE_inc": [0.15]
        }
    }

    behavior_y.update_behavior(new_behavior)

    calc_y_behavior2 = behavior(calc_x, calc_y)

    new_behavior = {
        2013: {
            "_BE_sub": [0.4],
            "_BE_inc": [0.0]
        }
    }

    behavior_y.update_behavior(new_behavior)
    calc_y_behavior3 = behavior(calc_x, calc_y)

    assert (calc_y_behavior1.records._ospctax.sum() !=
            calc_y_behavior2.records._ospctax.sum() !=
            calc_y_behavior3.records._ospctax.sum())


def test_update_behavior():
    b = Behavior(start_year=2013)
    b.update_behavior({2014: {'_BE_sub': [0.5], '_II_rt7': [0.3]}})
    should_be = np.full((12,), 0.5)
    should_be[0] = 0.0
    assert np.allclose(b._BE_sub, should_be, rtol=0.0)
    assert np.allclose(b._BE_inc, np.zeros((12,)), rtol=0.0)
    b.set_year(2015)
    assert b.current_year == 2015
    assert b.BE_sub == 0.5
    assert b.BE_inc == 0.0
