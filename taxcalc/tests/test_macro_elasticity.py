"""
Tests of proportional_change_in_gdp function.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_macro_elasticity.py
# pylint --disable=locally-disabled test_macro_elasticity.py

import pytest
from taxcalc import (Policy, Records,  # pylint: disable=import-error
                     Calculator, proportional_change_in_gdp)


def test_proportional_change_in_gdp(cps_subsample):
    """
    Test correct and incorrect calls to proportional_change_in_gdp function.
    """
    rec1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=Policy(), records=rec1)
    rec2 = Records.cps_constructor(data=cps_subsample)
    pol2 = Policy()
    reform = {2015: {'_II_em': [0.0]}}  # reform increases taxes and MTRs
    pol2.implement_reform(reform)
    calc2 = Calculator(policy=pol2, records=rec2)
    assert calc1.current_year == 2014  # because using CPS data
    gdpc = proportional_change_in_gdp(2014, calc1, calc2, elasticity=0.36)
    assert gdpc == 0.0  # no effect for first data year
    gdpc = proportional_change_in_gdp(2015, calc1, calc2, elasticity=0.36)
    assert gdpc == 0.0  # no effect in first year of reform
    calc1.increment_year()
    calc2.increment_year()
    assert calc1.current_year == 2015
    gdpc = proportional_change_in_gdp(2016, calc1, calc2, elasticity=0.36)
    assert gdpc < 0.0  # higher average MTR implies reduction in GDP
    # skip calc?.increment_year to 2016, so calc?.current_year is still 2015
    with pytest.raises(ValueError):
        gdpc = proportional_change_in_gdp(2017, calc1, calc2, elasticity=0.36)
