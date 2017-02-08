import os
import tempfile
import pytest
from taxcalc import Growfactors


@pytest.yield_fixture
def bad_gf_file():
    txt = (u'YEAR,AWAGE,ACPIU,ABADNAME,ASOCSEC\n'
           u'2015,1.000,1.000,1.000000,1.00000\n')
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt)
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_incorrect_Growfactors_usage(bad_gf_file):
    with pytest.raises(ValueError):
        gf = Growfactors(dict())
    with pytest.raises(ValueError):
        gf = Growfactors(bad_gf_file.name)
    gf = Growfactors()
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2000, 2099)
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2009, 2099)
    with pytest.raises(ValueError):
        pir = gf.price_inflation_rates(2021, 2013)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2000, 2099)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2009, 2099)
    with pytest.raises(ValueError):
        wgr = gf.wage_growth_rates(2021, 2013)
    with pytest.raises(ValueError):
        val = gf.factor_value('BADNAME', 2020)
    with pytest.raises(ValueError):
        val = gf.factor_value('AWAGE', 2000)
    with pytest.raises(ValueError):
        val = gf.factor_value('AWAGE', 2099)


def test_correct_Growfactors_usage():
    gf = Growfactors()
    pir = gf.price_inflation_rates(2013, 2020)
    assert len(pir) == 8
    wgr = gf.wage_growth_rates(2013, 2021)
    assert len(wgr) == 9
    val = gf.factor_value('AWAGE', 2013)
    assert val > 1.0
