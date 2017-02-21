import numpy as np
import pytest
from taxcalc import ParametersBase


def test_ParametersBase_instantiation_and_usage():
    pbase = ParametersBase()
    assert pbase
    assert pbase.inflation_rates() is None
    assert pbase.wage_growth_rates() is None
    syr = 2010
    nyrs = 10
    pbase.initialize(start_year=syr, num_years=nyrs)
    with pytest.raises(ValueError):
        pbase.set_year(syr - 1)
    with pytest.raises(NotImplementedError):
        pbase._params_dict_from_json_file()
    with pytest.raises(ValueError):
        pbase._update([])
    with pytest.raises(ValueError):
        pbase._update({})
    with pytest.raises(ValueError):
        pbase._update({(syr + nyrs): {}})
    with pytest.raises(ValueError):
        pbase._update({syr: []})
    with pytest.raises(ValueError):
        ParametersBase.expand_array({}, True, [0.02], 1)
    threedarray = np.array([[[1, 1]], [[1, 1]], [[1, 1]]])
    with pytest.raises(ValueError):
        ParametersBase.expand_array(threedarray, True, [0.02, 0.02], 2)
