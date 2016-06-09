import os
import sys
import numpy as np
import pytest
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import ParametersBase


def test_ParametersBase_instantiation_and_usage():
    pbase = ParametersBase()
    assert pbase
    assert pbase.inflation_rates() is None
    assert pbase.wage_growth_rates() is None
    pbase.initialize(start_year=2000, num_years=10)
    with pytest.raises(ValueError):
        pbase.set_year(1999)
    with pytest.raises(NotImplementedError):
        pbase._params_dict_from_json_file()
    with pytest.raises(ValueError):
        pbase._update([])
    with pytest.raises(ValueError):
        pbase._update({})
    with pytest.raises(ValueError):
        pbase._update({2099: {}})
    with pytest.raises(ValueError):
        pbase._update({2013: []})
    with pytest.raises(ValueError):
        ParametersBase.expand_array({}, True, [0.02], 1)
    threedarray = np.array([[[1, 1]], [[1, 1]], [[1, 1]]])
    with pytest.raises(ValueError):
        ParametersBase.expand_array(threedarray, True, [0.02, 0.02], 2)
