import numpy as np
from numpy.testing import assert_array_equal
import pytest
from taxcalc import Policy, Records, Calculator, Growth


def test_make_calculator_with_growth(records_2009):
    grow = Growth()
    calc = Calculator(policy=Policy(), records=records_2009, growth=grow)
    assert calc.current_year == 2013
    assert isinstance(calc, Calculator)
    # test correct Growth instantiation with dictionary
    grow = Growth(growth_dict=dict())
    assert isinstance(grow, Growth)
    # test incorrect Growth instantiation
    with pytest.raises(ValueError):
        grow = Growth(growth_dict=list())
    with pytest.raises(ValueError):
        grow = Growth(num_years=0)


def test_update_growth(puf_1991, weights_1991):
    # try incorrect updates
    grow = Growth()
    with pytest.raises(ValueError):
        grow.update_growth({2013: list()})
    with pytest.raises(ValueError):
        grow.update_growth({2013: {'bad_name': [0.02]}})
    with pytest.raises(ValueError):
        grow.update_growth({2013: {'bad_name_cpi': True}})
    bad_params = {2015: {'_factor_adjustment': [0.01],
                         '_factor_target': [0.08]}}
    with pytest.raises(ValueError):
        grow.update_growth(bad_params)
    # try correct updates
    grow_x = Growth()
    factor_x = {2015: {'_factor_target': [0.04]}}
    grow_x.update_growth(factor_x)
    grow_y = Growth()
    factor_y = {2015: {'_factor_adjustment': [0.01]}}
    grow_y.update_growth(factor_y)
    # create two Calculators
    recs_x = Records(data=puf_1991, weights=weights_1991,
                     adjust_factors=None, start_year=2009)
    recs_y = Records(data=puf_1991, weights=weights_1991,
                     adjust_factors=None, start_year=2009)
    calc_x = Calculator(policy=Policy(), records=recs_x, growth=grow_x)
    calc_y = Calculator(policy=Policy(), records=recs_y, growth=grow_y)
    assert_array_equal(calc_x.growth.factor_target,
                       grow_x.factor_target)
    assert_array_equal(calc_x.growth._factor_target,
                       np.array([0.0247, 0.0115, 0.04, 0.04, 0.04,
                                0.04, 0.04, 0.04, 0.04, 0.04, 0.04,
                                0.04, 0.04, 0.04]))
    assert_array_equal(calc_y.growth.factor_adjustment,
                       grow_y.factor_adjustment)
    assert_array_equal(calc_y.growth._factor_adjustment,
                       np.array([0.0, 0.0, 0.01, 0.01, 0.01, 0.01,
                                 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
                                 0.01, 0.01]))


def test_factor_target(records_2009):
    calc = Calculator(policy=Policy(), records=records_2009, growth=Growth())
    AGDPN_pre = calc.records.BF.AGDPN[2015]
    ATXPY_pre = calc.records.BF.ATXPY[2015]
    # specify _factor_target
    ft2015 = 0.04
    factor_target = {2015: {'_factor_target': [ft2015]}}
    calc.growth.update_growth(factor_target)
    assert calc.current_year == 2013
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2015
    distance = ((ft2015 - calc.growth.default_real_gdp_growth_rate()) /
                calc.records.BF.APOPN[2015])
    AGDPN_post = AGDPN_pre + distance
    ATXPY_post = ATXPY_pre + distance
    assert calc.records.BF.AGDPN[2015] == AGDPN_post
    assert calc.records.BF.ATXPY[2015] == ATXPY_post


def test_factor_adjustment(records_2009):
    calc = Calculator(policy=Policy(), records=records_2009, growth=Growth())
    ATXPY_pre = calc.records.BF.ATXPY[2015]
    AGDPN_pre = calc.records.BF.AGDPN[2015]
    # specify _factor_adjustment
    fa2015 = 0.01
    factor_adj = {2015: {'_factor_adjustment': [fa2015]}}
    calc.growth.update_growth(factor_adj)
    assert calc.current_year == 2013
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2015
    assert calc.records.BF.AGDPN[2015] == AGDPN_pre + fa2015
    assert calc.records.BF.ATXPY[2015] == ATXPY_pre + fa2015


def test_growth_default_data():
    paramdata = Growth.default_data()
    assert paramdata['_factor_adjustment'] == [0.0]


def test_hard_coded_gdp_growth():
    growth = Growth()
    assert_array_equal(growth._factor_target,
                       np.array(Growth.REAL_GDP_GROWTH_RATES))
