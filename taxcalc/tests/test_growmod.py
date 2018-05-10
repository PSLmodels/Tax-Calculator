# CODING-STYLE CHECKS:
# pycodestyle test_growmod.py

import os
import json
from numpy.testing import assert_allclose
import pytest
from taxcalc import Growmod, Policy


def test_year_consistency():
    assert Growmod.JSON_START_YEAR == Policy.JSON_START_YEAR
    assert Growmod.DEFAULT_NUM_YEARS == Policy.DEFAULT_NUM_YEARS


def test_incorrect_growmod_ctor():
    with pytest.raises(ValueError):
        gdiff = Growmod(growmod_dict=list())
    with pytest.raises(ValueError):
        gdiff = Growmod(num_years=0)


def test_correct_but_not_useful_growmod_ctor():
    gdiff = Growmod(growmod_dict={})
    assert gdiff


def test_update_and_apply_growmod():
    syr = 2013
    nyrs = 5
    lyr = syr + nyrs - 1
    # update Growmod instanace with empty dictionary
    gmod = Growmod(start_year=syr, num_years=nyrs)
    mods = {}
    gmod.update_growmod(mods)
    assert not gmod.is_ever_active()
    # update Growmod instance
    gmod = Growmod(start_year=syr, num_years=nyrs)
    mods = {2014: {'_active': [True]}}
    gmod.update_growmod(mods)
    assert gmod.is_ever_active()
    # apply growmod to GrowModel instance
    # growmodel = GrowModel()  # TODO: activate this statement
    # gmod.apply_to(growmodel)  # TODO: activate this statement


def test_incorrect_update_growmod():
    with pytest.raises(ValueError):
        Growmod().update_growmod([])
    with pytest.raises(ValueError):
        Growmod().update_growmod({'xyz': {'_active': [True]}})
    with pytest.raises(ValueError):
        Growmod().update_growmod({2012: {'_active': [True]}})
    with pytest.raises(ValueError):
        Growmod().update_growmod({2052: {'_active': [True]}})
    with pytest.raises(ValueError):
        Growmod().update_growmod({2014: {'_actixxx': [True]}})
    # TODO: revise following test to have correct type but out-of-range value
    """
    with pytest.raises(ValueError):
        Growmod().update_growmod({2014: {'_active': [1]}})
    """


def test_description_punctuation(tests_path):
    """
    Check that each description ends in a period.
    """
    # read JSON file into a dictionary
    path = os.path.join(tests_path, '..', 'growmod.json')
    with open(path, 'r') as jsonfile:
        dct = json.load(jsonfile)
    all_desc_ok = True
    for param in dct.keys():
        if not dct[param]['description'].endswith('.'):
            all_desc_ok = False
            print('param,description=',
                  str(param),
                  dct[param]['description'])
    assert all_desc_ok


def test_boolean_value_infomation(tests_path):
    """
    Check consistency of boolean_value in growmod.json file.
    """
    # read growmod.json file into a dictionary
    path = os.path.join(tests_path, '..', 'growmod.json')
    with open(path, 'r') as gmdfile:
        gmd = json.load(gmdfile)
    for param in gmd.keys():
        val = gmd[param]['value']
        if isinstance(val, list):
            val = val[0]
            if isinstance(val, list):
                val = val[0]
        valstr = str(val)
        if valstr == 'True' or valstr == 'False':
            val_is_boolean = True
        else:
            val_is_boolean = False
        if gmd[param]['boolean_value'] != val_is_boolean:
            print('param,boolean_value,val,val_is_boolean=',
                  str(param),
                  gmd[param]['boolean_value'],
                  val,
                  val_is_boolean)
            assert gmd[param]['boolean_value'] == val_is_boolean
