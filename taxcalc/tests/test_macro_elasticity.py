from taxcalc import Policy, Records, Calculator, proportional_change_gdp


def test_proportional_change_gdp(cps_subsample):
    rec1 = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=Policy(), records=rec1)
    rec2 = Records.cps_constructor(data=cps_subsample)
    pol2 = Policy()
    reform = {2013: {'_II_em': [0.0]}}  # reform increases taxes and MTRs
    pol2.implement_reform(reform)
    calc2 = Calculator(policy=pol2, records=rec2)
    calc1.advance_to_year(2014)
    calc2.advance_to_year(2014)
    gdp_pchg = 100.0 * proportional_change_gdp(calc1, calc2, elasticity=0.36)
    exp_pchg = -0.6  # higher MTRs imply negative expected GDP percent change
    abs_diff_pchg = abs(gdp_pchg - exp_pchg)
    assert abs_diff_pchg < 0.05
