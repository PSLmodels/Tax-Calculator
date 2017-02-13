from numpy.testing import assert_allclose
import pytest
from taxcalc import Growdiff, Growfactors


def test_incorrect_growdiff_ctor():
    with pytest.raises(ValueError):
        gdiff = Growdiff(growdiff_dict=list())
    with pytest.raises(ValueError):
        gdiff = Growdiff(num_years=0)


def test_correct_but_not_useful_growdiff_ctor():
    gdiff = Growdiff(growdiff_dict={})
    assert gdiff


def test_update_and_apply_growdiff():
    syr = 2013
    nyrs = 5
    lyr = syr + nyrs - 1
    gdiff = Growdiff(start_year=syr, num_years=nyrs)
    # update Growdiff instance
    diffs = {2014: {'_AWAGE': [0.01]},
             2016: {'_AWAGE': [0.02]}}
    gdiff.update_growdiff(diffs)
    expected_wage_diffs = [0.00, 0.01, 0.01, 0.02, 0.02]
    assert_allclose(gdiff._AWAGE, expected_wage_diffs, atol=0.0, rtol=0.0)
    # apply growdiff to Growfactors instance
    gf = Growfactors()
    pir_pre = gf.price_inflation_rates(syr, lyr)
    wgr_pre = gf.wage_growth_rates(syr, lyr)
    gfactors = Growfactors()
    gdiff.apply(gfactors)
    pir_pst = gfactors.price_inflation_rates(syr, lyr)
    wgr_pst = gfactors.wage_growth_rates(syr, lyr)
    expected_wgr_pst = [wgr_pre[i] + expected_wage_diffs[i]
                        for i in range(0, nyrs)]
    assert_allclose(pir_pre, pir_pst, atol=0.0, rtol=0.0)
    assert_allclose(wgr_pst, expected_wgr_pst, atol=1.0e-9, rtol=0.0)
