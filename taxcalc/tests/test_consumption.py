import os
import sys
import numpy as np
import pandas as pd
import pytest
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator, Consumption

# use 1991 PUF-like data to emulate current puf.csv, which is private
TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91taxdata.csv.gz')
TAXDATA = pd.read_csv(TAXDATA_PATH, compression='gzip')
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91weights.csv.gz')
WEIGHTS = pd.read_csv(WEIGHTS_PATH, compression='gzip')


def test_incorrect_Consumption_instantiation():
    with pytest.raises(ValueError):
        consump = Consumption(consumption_dict=list())
    with pytest.raises(ValueError):
        consump = Consumption(num_years=0)


def test_correct_but_not_recommended_Consumption_instantiation():
    consump = Consumption(consumption_dict={})
    assert consump


def test_correct_update_consumption():
    consump = Consumption(start_year=2013)
    consump.update_consumption({2014: {'_MPC_xxx': [0.05]},
                                2015: {'_MPC_xxx': [0.06]}})
    should_be = np.full((Consumption.DEFAULT_NUM_YEARS,), 0.06)
    should_be[0] = 0.0
    should_be[1] = 0.05
    assert np.allclose(consump._MPC_xxx, should_be, rtol=0.0)
    assert np.allclose(consump._MPC_yyy,
                       np.zeros((Consumption.DEFAULT_NUM_YEARS,)),
                       rtol=0.0)
    consump.set_year(2015)
    assert consump.current_year == 2015
    assert consump.MPC_xxx == 0.06
    assert consump.MPC_yyy == 0.0


def test_incorrect_update_consumption():
    consump = Consumption()
    with pytest.raises(ValueError):
        consump.update_consumption({2016: {'_MPC_xxx': [-0.02]}})
    with pytest.raises(ValueError):
        consump.update_consumption({2017: {'_MPC_xxx': [1.02]}})
    with pytest.raises(ValueError):
        consump.update_consumption({2014: {'_MPC_xxx': [0.8],
                                           '_MPC_yyy': [0.3]}})


def test_future_update_consumption():
    consump = Consumption()
    assert consump.current_year == consump.start_year
    assert consump.has_response() is False
    cyr = 2020
    consump.set_year(cyr)
    consump.update_consumption({cyr: {'_MPC_xxx': [0.01]}})
    assert consump.current_year == cyr
    assert consump.has_response() is True
    consump.set_year(cyr - 1)
    assert consump.has_response() is False


def test_consumption_default_data():
    paramdata = Consumption.default_data()
    for param in paramdata:
        assert paramdata[param] == [0.0]
