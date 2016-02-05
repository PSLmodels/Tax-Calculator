import os
import sys
import numpy as np
import pandas as pd
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator, behavior, Behavior

# use 1991 PUF-like data to emulate current puf.csv, which is private
TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'tax_all1991_puf.gz')
TAXDATA = pd.read_csv(TAXDATA_PATH, compression='gzip')

# specify WEIGHTS appropriate for 1991 data
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'WEIGHTS_testing.csv')
WEIGHTS = pd.read_csv(WEIGHTS_PATH)


def test_make_behavioral_Calculator():
    # create Records objects
    records_x = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    records_y = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    # create Policy objects
    policy_x = Policy()
    policy_y = Policy()
    # implement policy_y reform
    reform = {
        2013: {
            "_II_rt7": [0.496]
        }
    }
    policy_y.implement_reform(reform)
    # create two Calculator objects
    behavior_y = Behavior()
    calc_x = Calculator(policy=policy_x, records=records_x)
    calc_y = Calculator(policy=policy_y, records=records_y,
                        behavior=behavior_y)
    # create behavioral calculators and vary substitution and income effects
    behavior1 = {
        2013: {
            "_BE_sub": [0.4],
            "_BE_inc": [0.15]
        }
    }
    behavior_y.update_behavior(behavior1)
    calc_y_behavior1 = behavior(calc_x, calc_y)
    behavior2 = {
        2013: {
            "_BE_sub": [0.5],
            "_BE_inc": [0.15]
        }
    }
    behavior_y.update_behavior(behavior2)
    calc_y_behavior2 = behavior(calc_x, calc_y)
    behavior3 = {
        2013: {
            "_BE_sub": [0.4],
            "_BE_inc": [0.0]
        }
    }
    behavior_y.update_behavior(behavior3)
    calc_y_behavior3 = behavior(calc_x, calc_y)
    # check that total income tax liability differs across the three behaviors
    assert (calc_y_behavior1.records._iitax.sum() !=
            calc_y_behavior2.records._iitax.sum() !=
            calc_y_behavior3.records._iitax.sum())


def test_update_behavior():
    beh = Behavior(start_year=2013)
    beh.update_behavior({2014: {'_BE_sub': [0.5]},
                         2015: {'_BE_CG_per': [1.2]}})
    policy = Policy()
    should_be = np.full((Behavior.DEFAULT_NUM_YEARS,), 0.5)
    should_be[0] = 0.0
    assert np.allclose(beh._BE_sub, should_be, rtol=0.0)
    assert np.allclose(beh._BE_inc,
                       np.zeros((Behavior.DEFAULT_NUM_YEARS,)),
                       rtol=0.0)
    beh.set_year(2015)
    assert beh.current_year == 2015
    assert beh.BE_sub == 0.5
    assert beh.BE_inc == 0.0
    assert beh.BE_CG_per == 1.2


def test_behavior_default_data():
    paramdata = Behavior.default_data()
    assert paramdata['_BE_sub'] == [0.0]
