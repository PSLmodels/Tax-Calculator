"""
Tests for functions in behresp.py file.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_behresp.py
# pylint --disable=locally-disabled test_behresp.py

from io import StringIO
import numpy as np
import pandas as pd
import pytest
import taxcalc as tc
from taxcalc.behresp import response, quantity_response, labor_response


def test_default_response_function(cps_subsample):
    """
    Test that default behavior parameters produce static results.
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
    """
    # ... specify Records object and policy reform
    rec = tc.Records.cps_constructor(data=cps_subsample)
    refyear = 2020
    reform = {'II_em': {refyear: 1500}}
    # ... specify non-default1 response elasticities
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


def test_alternative_behavior_parameters(cps_subsample):
    """
    Test alternative behavior parameters to improve code coverage.
    Also, test response function's dump argument.
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


@pytest.mark.skip
@pytest.mark.parametrize('stcg',
                         [-3600,
                          -2400,
                          -1200,
                          0,
                          1200,
                          2400,
                          3600,
                          4800])
def test_sub_effect_independence(stcg):
    """
    Ensure that LTCG amount does not affect magnitude of substitution effect.
    """
    # pylint: disable=too-many-locals
    # specify reform that raises top-bracket marginal tax rate
    refyear = 2020
    reform = {'II_rt7': {refyear: 0.70}}
    # specify a substitution effect behavioral response elasticity
    elasticities_dict = {'sub': 0.25}
    # specify several high-earning filing units
    num_recs = 9
    input_csv = ('RECID,MARS,e00200,e00200p,p22250,p23250\n'
                 '1,2,1000000,1000000,stcg,    0\n'
                 '2,2,1000000,1000000,stcg, 4800\n'
                 '3,2,1000000,1000000,stcg, 3600\n'
                 '4,2,1000000,1000000,stcg, 2400\n'
                 '5,2,1000000,1000000,stcg, 1200\n'
                 '6,2,1000000,1000000,stcg,    0\n'
                 '7,2,1000000,1000000,stcg,-1200\n'
                 '8,2,1000000,1000000,stcg,-2400\n'
                 '9,2,1000000,1000000,stcg,-3600\n')
    inputcsv = input_csv.replace('stcg', str(stcg))
    input_dataframe = pd.read_csv(StringIO(inputcsv))
    assert len(input_dataframe.index) == num_recs
    recs = tc.Records(data=input_dataframe,
                      start_year=refyear,
                      gfactors=None, weights=None)
    pol = tc.Policy()
    calc1 = tc.Calculator(records=recs, policy=pol)
    assert calc1.current_year == refyear
    pol.implement_reform(reform)
    calc2 = tc.Calculator(records=recs, policy=pol)
    assert calc2.current_year == refyear
    del pol
    df1, df2 = response(calc1, calc2, elasticities_dict)
    del calc1
    del calc2
    # compute change in taxable income for each of the filing units
    chg_funit = {}
    for rid in range(1, num_recs + 1):
        idx = rid - 1
        chg_funit[rid] = df2['c04800'][idx] - df1['c04800'][idx]
    del df1
    del df2
    # confirm reform reduces taxable income when assuming substitution effect
    emsg = ''
    for rid in range(1, num_recs + 1):
        if not chg_funit[rid] < 0:
            txt = '\nFAIL: stcg={} : chg[{}]={:.2f} is not negative'
            emsg += txt.format(stcg, rid, chg_funit[rid])
    # confirm change in taxable income is same for all filing units
    for rid in range(2, num_recs + 1):
        if not np.allclose(chg_funit[rid], chg_funit[1]):
            txt = '\nFAIL: stcg={} : chg[{}]={:.2f} != chg[1]={:.2f}'
            emsg += txt.format(stcg, rid, chg_funit[rid], chg_funit[1])
    del chg_funit
    if emsg:
        raise ValueError(emsg)
