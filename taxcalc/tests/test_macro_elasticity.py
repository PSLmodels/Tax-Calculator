from taxcalc import Policy, Records, Calculator, proportional_change_gdp


def test_proportional_change_gdp(cps_subsample):
    rec1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=Policy(), records=rec1)
    rec2 = Records.cps_constructor(data=cps_subsample)
    pol2 = Policy()
    reform = {2013: {'_II_em': [0.0]}}  # reform increases taxes and MTRs
    pol2.implement_reform(reform)
    calc2 = Calculator(policy=pol2, records=rec2)
    gdp_diff = proportional_change_gdp(calc1, calc2, elasticity=0.36)
    assert gdp_diff < 0.  # higher MTRs imply negative GDP effect
