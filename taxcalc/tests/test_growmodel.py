# CODING-STYLE CHECKS:
# pycodestyle test_growmodel.py

import os
import json
import numpy as np
import pytest
from taxcalc import GrowModel


def test_incorrect_growmodel_instantiation():
    with pytest.raises(ValueError):
        GrowModel(start_year=2012)
    with pytest.raises(ValueError):
        GrowModel(num_years=0)
    with pytest.raises(FloatingPointError):
        np.divide(1., 0.)


def test_correct_update_growmodel():
    gmod = GrowModel()
    gmod.update_growmodel({})
    assert not gmod.is_ever_active()
    start_cyr = gmod.start_year
    active_cyr = 2018
    gmod.update_growmodel({active_cyr: {'_active': [True]}})
    for cyr in range(start_cyr, active_cyr):
        assert not gmod._active[cyr - start_cyr]
    for cyr in range(active_cyr, gmod.end_year + 1):
        assert gmod._active[cyr - start_cyr]
    assert gmod.is_ever_active()
    gmod.set_year(active_cyr - 1)
    assert not gmod.is_active()


def test_incorrect_update_growmodel():
    with pytest.raises(ValueError):
        GrowModel().update_growmodel([])
    with pytest.raises(ValueError):
        GrowModel().update_growmodel({2013: {'_active': [2]}})
    with pytest.raises(ValueError):
        GrowModel().update_growmodel({2013: {'_active': [0.2]}})
    with pytest.raises(ValueError):
        GrowModel().update_growmodel({2013: {'_activexxx': [True]}})
    # year in update must be no less than start year
    gmod = GrowModel(start_year=2014)
    with pytest.raises(ValueError):
        gmod.update_growmodel({2013: {'_active': [True]}})
    # year in update must be no less than current year
    gmod = GrowModel(start_year=2014)
    gmod.set_year(2015)
    with pytest.raises(ValueError):
        gmod.update_growmodel({2014: {'_active': [True]}})
    # year in update must be no greater than end_year
    with pytest.raises(ValueError):
        GrowModel().update_growmodel({2040: {'_active': [True]}})
    # invalid start year
    with pytest.raises(ValueError):
        GrowModel().update_growmodel({'notayear': {'_active': [True]}})


"""
def test_validate_param_values_errors():
    behv0 = GrowModel()
    specs0 = {2020: {'_BE_cg': [0.2]}}
    with pytest.raises(ValueError):
        behv0.update_growmodel(specs0)
    behv1 = GrowModel()
    specs1 = {2022: {'_BE_sub': [-0.2]}}
    with pytest.raises(ValueError):
        behv1.update_growmodel(specs1)
    behv2 = GrowModel()
    specs2 = {
        2020: {
            '_BE_subinc_wrt_earnings': [True],
            '_BE_cg': [-0.2],
            '_BE_sub': [0.3]
        }
    }
    behv2.update_growmodel(specs2)
"""


"""
def test_future_update_growmodel():
    behv = GrowModel()
    assert behv.current_year == behv.start_year
    assert behv.has_response() is False
    assert behv.has_any_response() is False
    cyr = 2020
    behv.set_year(cyr)
    behv.update_growmodel({cyr: {'_BE_cg': [-1.0]}})
    assert behv.current_year == cyr
    assert behv.has_response() is True
    behv.set_year(cyr - 1)
    assert behv.has_response() is False
    assert behv.has_any_response() is True
"""


def test_boolean_value_infomation(tests_path):
    """
    Check consistency of boolean_value in growmodel.json file.
    """
    # read growmodel.json file into a dictionary
    path = os.path.join(tests_path, '..', 'growmodel.json')
    with open(path, 'r') as behfile:
        beh = json.load(behfile)
    for param in beh.keys():
        val = beh[param]['value']
        if isinstance(val, list):
            val = val[0]
            if isinstance(val, list):
                val = val[0]
        valstr = str(val)
        if valstr == 'True' or valstr == 'False':
            val_is_boolean = True
        else:
            val_is_boolean = False
        if beh[param]['boolean_value'] != val_is_boolean:
            print('param,boolean_value,val,val_is_boolean=',
                  str(param),
                  beh[param]['boolean_value'],
                  val,
                  val_is_boolean)
            assert beh[param]['boolean_value'] == val_is_boolean
