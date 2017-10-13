from taxcalc import Policy, Records, Calculator, proportional_change_gdp


def test_proportional_change_gdp(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    reform = {2013: {'_II_em': [0.0]}}  # reform increases taxes and MTRs
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    calc1.advance_to_year(2014)
    calc2.advance_to_year(2014)
    gdp_pchg = 100.0 * proportional_change_gdp(calc1, calc2, elasticity=0.36)
    exp_pchg = -0.6  # higher MTRs imply negative expected GDP percent change
    abs_diff_pchg = abs(gdp_pchg - exp_pchg)
    assert abs_diff_pchg < 0.05
