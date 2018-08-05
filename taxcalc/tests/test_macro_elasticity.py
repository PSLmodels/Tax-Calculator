"""
Tests of proportional_change_in_gdp function.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_macro_elasticity.py
# pylint --disable=locally-disabled test_macro_elasticity.py

import pytest
from taxcalc import (Policy, Records,  # pylint: disable=import-error
                     Calculator, proportional_change_in_gdp)


def test_proportional_change_in_gdp(cps_subsample):
    """
    Test correct and incorrect calls to proportional_change_in_gdp function.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    reform = {2015: {'_II_em': [0.0]}}  # reform increases taxes and MTRs
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    assert calc1.current_year == calc2.current_year
    assert calc1.current_year == 2014  # because using CPS data
    gdpc = proportional_change_in_gdp(2014, calc1, calc2, elasticity=0.36)
    assert gdpc == 0.0  # no effect for first data year
    gdpc = proportional_change_in_gdp(2015, calc1, calc2, elasticity=0.36)
    assert gdpc == 0.0  # no effect in first year of reform
    calc1.increment_year()
    calc2.increment_year()
    assert calc1.current_year == 2015
    gdp_pchg = 100.0 * proportional_change_in_gdp(2016, calc1, calc2,
                                                  elasticity=0.36)
    exp_pchg = -0.49  # higher MTRs imply negative expected GDP percent change
    abs_diff_pchg = abs(gdp_pchg - exp_pchg)
    if abs_diff_pchg > 0.01:
        msg = 'year,gdp_pchg,exp_pchg= {} {:.3f} {:.3f}'.format(2016,
                                                                gdp_pchg,
                                                                exp_pchg)
        assert msg == 'ERROR: gdp_pchg not close to exp_pchg'
    # skip calcN.increment_year to 2016, so calcN.current_year is still 2015
    with pytest.raises(ValueError):
        proportional_change_in_gdp(2017, calc1, calc2, elasticity=0.36)
