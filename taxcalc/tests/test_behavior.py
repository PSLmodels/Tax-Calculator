import numpy as np
import pytest
from taxcalc import Policy, Records, Calculator, Behavior


def test_incorrect_Behavior_instantiation():
    with pytest.raises(ValueError):
        Behavior(behavior_dict=list())
    bad_behv_dict = {
        '_BE_bad': {'start_year': 2013, 'value': [0.0]}
    }
    with pytest.raises(ValueError):
        Behavior(behavior_dict=bad_behv_dict)
    with pytest.raises(ValueError):
        Behavior(num_years=0)
    with pytest.raises(FloatingPointError):
        np.divide(1., 0.)
    with pytest.raises(ValueError):
        Behavior(behavior_dict={})
    bad_behv_dict = {
        '_BE_subinc_wrt_earnings': {'start_year': 2013, 'value': [True]}
    }
    with pytest.raises(ValueError):
        Behavior(behavior_dict=bad_behv_dict)
    bad_behv_dict = {
        '_BE_subinc_wrt_earnings': {'start_year': 2013, 'value': [True]},
        '_BE_sub': {'start_year': 2017, 'value': [0.25]}
    }
    with pytest.raises(ValueError):
        Behavior(behavior_dict=bad_behv_dict)
    bad_behv_dict = {
        54321: {'start_year': 2013, 'value': [0.0]}
    }
    with pytest.raises(ValueError):
        Behavior(behavior_dict=bad_behv_dict)


def test_behavioral_response_Calculator(cps_subsample):
    # create Records objects
    records_x = Records.cps_constructor(data=cps_subsample)
    records_y = Records.cps_constructor(data=cps_subsample)
    year = records_x.current_year
    # create Policy objects
    policy_x = Policy()
    policy_y = Policy()
    # implement policy_y reform
    reform = {year: {'_II_rt7': [0.496],
                     '_PT_rt7': [0.496]}}
    policy_y.implement_reform(reform)
    # create two Calculator objects
    behavior_y = Behavior()
    calc_x = Calculator(policy=policy_x, records=records_x)
    calc_y = Calculator(policy=policy_y, records=records_y,
                        behavior=behavior_y)
    # test incorrect use of Behavior._mtr_xy method
    with pytest.raises(ValueError):
        behv = Behavior._mtr_xy(calc_x, calc_y,
                                mtr_of='e00200p',
                                tax_type='nonsense')
    # vary substitution and income effects in calc_y
    behavior0 = {year: {'_BE_sub': [0.0],
                        '_BE_cg': [0.0],
                        '_BE_charity': [[0.0, 0.0, 0.0]]}}
    behavior_y.update_behavior(behavior0)
    calc_y_behavior0 = Behavior.response(calc_x, calc_y)
    behavior1 = {year: {'_BE_sub': [0.3], '_BE_inc': [-0.1], '_BE_cg': [0.0],
                        '_BE_subinc_wrt_earnings': [True]}}
    behavior_y.update_behavior(behavior1)
    assert behavior_y.has_response() is True
    epsilon = 1e-9
    assert abs(behavior_y.BE_sub - 0.3) < epsilon
    assert abs(behavior_y.BE_inc - -0.1) < epsilon
    assert abs(behavior_y.BE_cg - 0.0) < epsilon
    calc_y_behavior1 = Behavior.response(calc_x, calc_y)
    behavior2 = {year: {'_BE_sub': [0.5], '_BE_cg': [-0.8]}}
    behavior_y.update_behavior(behavior2)
    calc_y_behavior2 = Behavior.response(calc_x, calc_y)
    behavior3 = {year: {'_BE_inc': [-0.2], '_BE_cg': [-0.8]}}
    behavior_y.update_behavior(behavior3)
    calc_y_behavior3 = Behavior.response(calc_x, calc_y)
    behavior4 = {year: {'_BE_cg': [-0.8]}}
    behavior_y.update_behavior(behavior4)
    calc_y_behavior4 = Behavior.response(calc_x, calc_y)
    behavior5 = {year: {'_BE_charity': [[-0.5, -0.5, -0.5]]}}
    behavior_y.update_behavior(behavior5)
    calc_y_behavior5 = Behavior.response(calc_x, calc_y)
    # check that total income tax liability differs across the
    # six sets of behavioral-response elasticities
    assert (calc_y_behavior0.records.iitax.sum() !=
            calc_y_behavior1.records.iitax.sum() !=
            calc_y_behavior2.records.iitax.sum() !=
            calc_y_behavior3.records.iitax.sum() !=
            calc_y_behavior4.records.iitax.sum() !=
            calc_y_behavior5.records.iitax.sum())
    # test incorrect _mtr_xy() usage
    with pytest.raises(ValueError):
        Behavior._mtr_xy(calc_x, calc_y, mtr_of='e00200p', tax_type='?')


def test_correct_update_behavior():
    beh = Behavior(start_year=2013)
    beh.update_behavior({2014: {'_BE_sub': [0.5]},
                         2015: {'_BE_cg': [-1.2]},
                         2016: {'_BE_charity':
                         [[-0.5, -0.5, -0.5]]}})
    should_be = np.full((Behavior.DEFAULT_NUM_YEARS,), 0.5)
    should_be[0] = 0.0
    assert np.allclose(beh._BE_sub, should_be, rtol=0.0)
    assert np.allclose(beh._BE_inc,
                       np.zeros((Behavior.DEFAULT_NUM_YEARS,)),
                       rtol=0.0)
    beh.set_year(2017)
    assert beh.current_year == 2017
    assert beh.BE_sub == 0.5
    assert beh.BE_inc == 0.0
    assert beh.BE_cg == -1.2
    assert beh.BE_charity.tolist() == [-0.5, -0.5, -0.5]


def test_incorrect_update_behavior():
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_inc': [+0.2]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_sub': [-0.2]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2017: {'_BE_subinc_wrt_earnings': [2]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2020: {'_BE_subinc_wrt_earnings': [True]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_charity': [[0.2, -0.2, 0.2]]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_cg': [+0.8]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_xx': [0.0]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_xx_cpi': [True]}})


def test_future_update_behavior():
    behv = Behavior()
    assert behv.current_year == behv.start_year
    assert behv.has_response() is False
    assert behv.has_any_response() is False
    cyr = 2020
    behv.set_year(cyr)
    behv.update_behavior({cyr: {'_BE_cg': [-1.0]}})
    assert behv.current_year == cyr
    assert behv.has_response() is True
    behv.set_year(cyr - 1)
    assert behv.has_response() is False
    assert behv.has_any_response() is True


def test_behavior_default_data():
    paramdata = Behavior.default_data()
    assert paramdata['_BE_inc'] == [0.0]
    assert paramdata['_BE_sub'] == [0.0]
    assert paramdata['_BE_cg'] == [0.0]
