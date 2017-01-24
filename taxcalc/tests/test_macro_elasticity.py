from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
from taxcalc import proportional_change_gdp  # pylint: disable=import-error


def test_proportional_change_gdp(puf_1991, weights_1991, adjust_1991):
    policy1 = Policy()
    recs1 = Records(data=puf_1991, weights=weights_1991,
                    adjust_factors=adjust_1991, start_year=2009)
    calc1 = Calculator(policy=policy1, records=recs1)
    policy2 = Policy()
    reform = {2013: {'_II_em': [0.0]}}
    policy2.implement_reform(reform)
    recs2 = Records(data=puf_1991, weights=weights_1991,
                    adjust_factors=adjust_1991, start_year=2009)
    calc2 = Calculator(policy=policy2, records=recs2)
    gdp_diff = proportional_change_gdp(calc1, calc2, elasticity=0.36)
    assert gdp_diff > 0
