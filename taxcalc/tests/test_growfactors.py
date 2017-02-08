import os
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
from io import StringIO
from taxcalc import Growfactors


@pytest.mark.one
def test_incorrect_Growfactors_usage():
    with pytest.raises(ValueError):
        gf = Growfactors(dict())
    gf = Growfactors()
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2000, 2099)
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2009, 2099)
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2021, 2013)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2000, 2099)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2009, 2099)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2021, 2013)
    with pytest.raises(ValueError):
        val = gf.factor_value('BADNAME', 2020)
    with pytest.raises(ValueError):
        val = gf.factor_value('AWAGE', 2000)
    with pytest.raises(ValueError):
        val = gf.factor_value('AWAGE', 2099)
