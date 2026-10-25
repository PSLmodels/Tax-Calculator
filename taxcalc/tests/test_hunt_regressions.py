"""
Regression tests for three IRS-form discrepancies (single-household cases).
Expected values come from the 2025 IRS forms/instructions computed by hand:
  * Schedule D Tax Worksheet lines 19-21 (2025 Instructions for Schedule D)
  * Form 6251 "Line 4" married-filing-separately add-on (2025 Instr. 6251)
  * Form 6251 Exemption Worksheet, which has no child cap after 2017
    (IRC 55(d)(4)(A)(iii): "subsection (j) of section 59 shall not apply")
"""
import pandas as pd
import pytest
import taxcalc as tc


def _calc(year, **v):
    d = {'RECID': 1, 'MARS': 1}
    d.update(v)
    d['e00200p'] = d.get('e00200', 0.)
    recs = tc.Records(data=pd.DataFrame([d]), start_year=year,
                      gfactors=None, weights=None)
    calc = tc.Calculator(policy=tc.Policy(), records=recs, verbose=False)
    calc.calc_all()
    return calc


@pytest.mark.parametrize('gainvar', ['e24515', 'e24518'])
def test_schd_tw_line19_24pct_bracket(gainvar):
    # single, taxable income 140,000 = 60,000 ordinary + 80,000 LTCG of
    # which 30,000 is 25%/28%-rate gain.  Sch D TW line 21 = 90,000, so the
    # 30,000 is taxed at 22% (ordinary) rather than 25%/28%:
    # tax(90,000) = 14,714 plus 15% of 50,000 = 7,500 -> 22,214
    calc = _calc(2025, e00200=75750., p23250=80000., **{gainvar: 30000.})
    assert calc.array('c04800')[0] == pytest.approx(140000.)
    assert calc.array('taxbc')[0] == pytest.approx(22214.)


def test_amt_mfs_line4_addon():
    # MFS, AMTI before add-on 1,200,000 >= 1,174,350, so add 68,500:
    # line 4 = 1,268,500; exemption 0; TMT = 0.28 * 1,268,500 - 2,391
    calc = _calc(2025, MARS=3, e00200=400000., cmbtp=800000.)
    assert calc.array('c62100')[0] == pytest.approx(1268500.)
    tmt = 0.28 * 1268500. - 2391.
    assert calc.array('c09600')[0] == pytest.approx(
        tmt - calc.array('taxbc')[0])


def test_no_child_amt_exemption_cap_after_2017():
    # 17-year-old dependent, 10,000 wages + 30,000 interest: AMTI 40,000
    # is below the 88,100 exemption, so there is no AMT
    calc = _calc(2025, age_head=17, DSI=1, e00200=10000., e00300=30000.)
    assert calc.array('c09600')[0] == pytest.approx(0.)


def test_amt_em_pe_2026_rev_proc_2025_32():
    pol = tc.Policy()
    pol.set_year(2026)
    # Rev. Proc. 2025-32 sec. 3.10: MFS complete phaseout amount $640,200
    assert pol.AMT_em_pe.ravel()[0] == pytest.approx(640200.)
