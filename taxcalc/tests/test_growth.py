import os
import sys
import numpy as np
from numpy.testing import assert_array_equal
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import pandas as pd
from taxcalc import Policy, Records, Calculator, behavior, Behavior, Growth
from taxcalc import adjustment, target


WEIGHTS_FILENAME = "../../WEIGHTS_testing.csv"
WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
WEIGHTS = pd.read_csv(WEIGHTS_PATH)

TAX_DTA_PATH = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")
TAX_DTA = pd.read_csv(TAX_DTA_PATH, compression='gzip')
# data fix-up: midr needs to be type int64 to match PUF
TAX_DTA['MIDR'] = TAX_DTA['MIDR'].astype('int64')


def test_make_calculator_with_growth():
    # create a Records and Params object
    records_x = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    records_y = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    policy_x = Policy()
    policy_y = Policy()

    # create two Calculators
    growth_x = Growth()
    growth_y = Growth()
    calc_x = Calculator(policy=policy_x, records=records_x,
                        growth=growth_x)
    calc_y = Calculator(policy=policy_y, records=records_y,
                        growth=growth_y)

    assert calc_x.current_year == 2013
    assert isinstance(calc_x, Calculator)
    assert isinstance(calc_y, Calculator)


def test_update_growth():

    records_x = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    records_y = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    policy_x = Policy()
    policy_y = Policy()

    # change growth adjustment/target
    growth_x = Growth()
    factor_x = {2015: {'_factor_target': [0.04]}}
    growth_x.update_economic_growth(factor_x)

    growth_y = Growth()
    factor_y = {2015: {'_factor_adjustment': [0.01]}}
    growth_y.update_economic_growth(factor_y)

    # create two Calculators
    calc_x = Calculator(policy=policy_x, records=records_x,
                        growth=growth_x)
    calc_y = Calculator(policy=policy_y, records=records_y,
                        growth=growth_y)

    assert_array_equal(calc_x.growth.factor_target,
                       growth_x.factor_target)
    assert_array_equal(calc_x.growth._factor_target,
                       np.array([0.0244, 0.0118, 0.04, 0.04, 0.04,
                                0.04, 0.04, 0.04, 0.04, 0.04, 0.04,
                                0.04]))

    assert_array_equal(calc_y.growth.factor_adjustment,
                       growth_y.factor_adjustment)
    assert_array_equal(calc_y.growth._factor_adjustment,
                       np.array([0.0, 0.0, 0.01, 0.01, 0.01, 0.01,
                                 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]))


def test_target():
    # Calculator
    records_x = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    policy_x = Policy()
    growth_x = Growth()
    calc_x = Calculator(policy=policy_x, records=records_x,
                        growth=growth_x)

    # set target
    factor_x = {2015: {'_factor_target': [0.04]}}
    growth_x.update_economic_growth(factor_x)

    AGDPN_pre = calc_x.records.BF.AGDPN[2015]
    ATXPY_pre = calc_x.records.BF.ATXPY[2015]

    target(calc_x, growth_x._factor_target, 2015)

    distance = ((growth_x._factor_target[2015 - 2013] -
                 Growth.default_real_GDP_growth_rate(2015 - 2013)) /
                calc_x.records.BF.APOPN[2015])
    AGDPN_post = AGDPN_pre + distance
    ATXPY_post = ATXPY_pre + distance

    assert calc_x.records.BF.AGDPN[2015] == AGDPN_post
    assert calc_x.records.BF.ATXPY[2015] == ATXPY_post


def test_adjustment():
    # make calculator
    records_y = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    policy_y = Policy()
    calc_y = Calculator(policy=policy_y, records=records_y)

    ATXPY_pre = calc_y.records.BF.ATXPY[2015]
    AGDPN_pre = calc_y.records.BF.AGDPN[2015]

    # apply adjustment
    adjustment(calc_y, 0.01, 2015)

    assert calc_y.records.BF.AGDPN[2015] == AGDPN_pre + 0.01
    assert calc_y.records.BF.ATXPY[2015] == ATXPY_pre + 0.01


def test_growth_default_data():
    paramdata = Growth.default_data()
    assert paramdata['_factor_adjustment'] == [0.0]


def test_hard_coded_gdp_growth():
    growth = Growth()
    assert_array_equal(growth._factor_target,
                       np.array(Growth.REAL_GDP_GROWTH_RATES))
