"""
Tests for functions in behresp.py file.

Several tests below compare aggregate income tax liability against
hard-coded expected values.  Those values are weighted totals of the
iitax variable, expressed in billions of dollars, for the specified
refyear using the cps_subsample input data.  They are not analytically
derived, so they must be regenerated whenever the input data, the tax
logic, or the response logic changes.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_behresp.py
# pylint --disable=locally-disabled test_behresp.py

import numpy as np
import pytest
import taxcalc as tc
from taxcalc.behresp import response, quantity_response, labor_response


def test_default_response_function(cps_subsample):
    """
    Test that default behavior parameters produce static results.
    That is, test that an empty elasticities dictionary (which implies
    all three elasticities are zero) generates the same aggregate income
    tax liability as a conventional static calc_all() calculation.
    Also, test the response function's dump=True argument.
    """
    # ... specify Records object and policy reform
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    assert refyear >= 2018
    reform = {'II_em': {refyear: 1500}}
    # ... construct pre-reform calculator
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    calc1.advance_to_year(refyear)
    # ... construct two post-reform calculators
    pol.implement_reform(reform)
    calc2s = tc.Calculator(records=rec, policy=pol)  # for static assumptions
    calc2s.advance_to_year(refyear)
    calc2d = tc.Calculator(records=rec, policy=pol)  # for default behavior
    calc2d.advance_to_year(refyear)
    del pol
    # ... calculate aggregate inctax using static assumptions
    calc2s.calc_all()
    df2s = calc2s.dataframe(['iitax', 's006'])
    itax2s = round((df2s['iitax'] * df2s['s006']).sum() * 1e-9, 3)
    # ... calculate aggregate inctax using zero response elasticities
    _, df2d = response(calc1, calc2d, elasticities={}, dump=True)
    itax2d = round((df2d['iitax'] * df2d['s006']).sum() * 1e-9, 3)
    assert np.allclose(itax2d, itax2s)
    # ... clean up
    del calc1
    del calc2s
    del calc2d
    del df2s
    del df2d


@pytest.mark.parametrize('be_inc', [-0.1, 0.0])
def test_nondefault_response_function(be_inc, cps_subsample):
    """
    Test that non-default behavior parameters produce expected results.
    All three response channels are active, and the be_inc parametrization
    covers both a zero and a non-zero income elasticity while the
    substitution elasticity is non-zero.
    """
    # ... specify Records object and policy reform
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    reform = {'II_em': {refyear: 1500}}
    # ... specify non-default1 response elasticities
    # Note: the 'cg' value is a semi-elasticity, not the tax-rate
    # elasticity usually reported in the literature; -0.79 is used here
    # only as a test magnitude, not as a recommended assumption.  Also
    # note that the 'cg' value has no effect on the expected results
    # below, because the cps.csv input data contain no long-term capital
    # gains (p23250 is zero for every filing unit); the capital-gains
    # response logic is tested in test_capital_gains_effect_only.
    elasticities_dict = {'sub': 0.25, 'inc': be_inc, 'cg': -0.79}
    # ... calculate behavioral response to reform
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    pol.implement_reform(reform)
    calc2 = tc.Calculator(records=rec, policy=pol)
    del pol
    calc1.advance_to_year(refyear)
    calc2.advance_to_year(refyear)
    df1, df2 = response(calc1, calc2, elasticities_dict)
    del calc1
    del calc2
    itax1 = round((df1['iitax'] * df1['s006']).sum() * 1e-9, 3)
    itax2 = round((df2['iitax'] * df2['s006']).sum() * 1e-9, 3)
    del df1
    del df2
    if be_inc == 0.0:
        assert np.allclose([itax1, itax2], [1037.310, 984.848])
    elif be_inc == -0.1:
        assert np.allclose([itax1, itax2], [1037.310, 983.694])


def test_income_effect_only(cps_subsample):
    """
    Test a non-zero income elasticity with a zero substitution elasticity,
    which covers the response function branch in which the substitution
    effect is set to zeros but earnings marginal tax rates are still
    computed because the income elasticity is non-zero.
    """
    # ... specify Records object and policy reform
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    reform = {'II_em': {refyear: 1500}}
    # ... specify non-default response elasticities
    elasticities_dict = {'inc': -0.1}
    # ... calculate behavioral response to reform
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    pol.implement_reform(reform)
    calc2 = tc.Calculator(records=rec, policy=pol)
    del pol
    calc1.advance_to_year(refyear)
    calc2.advance_to_year(refyear)
    df1, df2 = response(calc1, calc2, elasticities_dict)
    del calc1
    del calc2
    itax1 = round((df1['iitax'] * df1['s006']).sum() * 1e-9, 3)
    itax2 = round((df2['iitax'] * df2['s006']).sum() * 1e-9, 3)
    del df1
    del df2
    assert np.allclose([itax1, itax2], [1037.310, 981.565])


def test_capital_gains_effect_only(cps_subsample):
    """
    Test a non-zero capital-gains semi-elasticity with zero substitution
    and income elasticities, which covers the response function branch in
    which no earnings marginal tax rates are computed (because both the
    substitution and income elasticities are zero) but a non-zero
    long-term capital-gains response is nevertheless applied.

    Note that the cps.csv input data contain no long-term capital gains
    (p23250 is zero for every filing unit), so synthetic gains are
    assigned to the two Calculator objects below in order to have a
    capital-gains response to test.
    """
    # ... specify Records object and policy reform
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    reform = {  # raise all LTCG tax rates
        'CG_rt1': {refyear: 0.10},
        'CG_rt2': {refyear: 0.25},
        'CG_rt3': {refyear: 0.30},
    }
    # ... construct baseline and reform calculators
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    pol.implement_reform(reform)
    calc2 = tc.Calculator(records=rec, policy=pol)
    del pol
    calc1.advance_to_year(refyear)
    calc2.advance_to_year(refyear)
    # ... assign synthetic long-term capital gains to both calculators
    #     (each Calculator object has its own copy of the input data)
    for calc in (calc1, calc2):
        calc.array('p23250', 0.5 * calc.array('e00200'))
    # ... calculate reform results with zero elasticities (static)
    _, df2s = response(calc1, calc2, {'sub': 0.0, 'inc': 0.0, 'cg': 0.0})
    itax2s = round((df2s['iitax'] * df2s['s006']).sum() * 1e-9, 3)
    del df2s
    # ... calculate reform results with only a capital-gains response
    # Note: -3.45 is the semi-elasticity that corresponds to the JCT-CBO
    # tax-rate elasticity estimate of -0.792.
    _, df2b = response(calc1, calc2, {'cg': -3.45})
    itax2b = round((df2b['iitax'] * df2b['s006']).sum() * 1e-9, 3)
    del df2b
    del calc1
    del calc2
    # ... the capital-gains response must reduce realizations, and hence
    #     income tax liability, relative to the static reform estimate
    assert itax2b < itax2s


def test_response_function_asserts(cps_subsample):
    """
    Test that the response function rejects wrongly-signed elasticities
    and mismatched Calculator objects.
    """
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    pol.implement_reform({'II_em': {refyear: 1500}})
    calc2 = tc.Calculator(records=rec, policy=pol)
    del pol
    calc1.advance_to_year(refyear)
    calc2.advance_to_year(refyear)
    # ... substitution elasticity must be zero or positive
    with pytest.raises(AssertionError):
        response(calc1, calc2, {'sub': -0.25})
    # ... income elasticity must be zero or negative
    with pytest.raises(AssertionError):
        response(calc1, calc2, {'inc': 0.1})
    # ... capital-gains semi-elasticity must be zero or negative
    with pytest.raises(AssertionError):
        response(calc1, calc2, {'cg': 3.45})
    # ... elasticities argument must be a dictionary
    with pytest.raises(AssertionError):
        response(calc1, calc2, [0.25, 0.0, 0.0])
    # ... the two Calculator objects must be in the same year
    calc2.increment_year()
    with pytest.raises(AssertionError):
        response(calc1, calc2, {'sub': 0.25})
    del calc1
    del calc2


def test_no_response_for_nonpositive_agi(cps_subsample):
    """
    Test that filing units with non-positive AGI minus itemized deductions
    have no ordinary-income response, as documented in the response
    function, while other filing units do have a response.
    """
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    pol = tc.Policy()
    calc1 = tc.Calculator(records=rec, policy=pol)
    pol.implement_reform({'II_em': {refyear: 1500}})
    calc2 = tc.Calculator(records=rec, policy=pol)
    del pol
    calc1.advance_to_year(refyear)
    calc2.advance_to_year(refyear)
    df1, df2 = response(calc1, calc2, {'sub': 0.25}, dump=True)
    del calc1
    del calc2
    # ... identify filing units with non-positive agi minus itemized ded
    ided = np.where(df1['c04470'] < df1['standard'], 0., df1['c04470'])
    nopos = np.array((df1['c00100'] - ided) <= 0., dtype=bool)
    assert nopos.sum() > 0  # ensure this test is testing something
    # ... those filing units must have unchanged wage and salary income
    assert np.allclose(df1['e00200'][nopos], df2['e00200'][nopos])
    # ... but some other filing units must have changed earnings
    assert not np.allclose(df1['e00200'][~nopos], df2['e00200'][~nopos])
    del df1
    del df2


def test_quantity_response():
    """
    Test quantity_response function.
    """
    quantity = np.array([1.0] * 10)
    res = quantity_response(quantity)
    assert np.allclose(res, np.zeros(quantity.shape))
    one = np.ones(quantity.shape)
    res = quantity_response(quantity,
                            price_elasticity=-0.2,
                            aftertax_price1=one,
                            aftertax_price2=one,
                            income_elasticity=0.1,
                            aftertax_income1=one,
                            aftertax_income2=one + one)
    assert not np.allclose(res, np.zeros(quantity.shape))


def test_labor_response():
    """
    Test that labor_response produces the same result as quantity_response
    where mtr* = 1 - aftertax_price*, using default earnings/quantity=1.
    """
    res_lr = labor_response(substitution_eti=1, mtr1=0.4, mtr2=0.5)
    res_qr = quantity_response(price_elasticity=1, aftertax_price1=0.6,
                               aftertax_price2=0.5)
    assert np.allclose(res_lr, res_qr)
