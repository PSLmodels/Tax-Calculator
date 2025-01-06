"""
Tests of Tax-Calculator GrowFactors class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_growfactors.py
# pylint --disable=locally-disabled test_growfactors.py

import os
import tempfile
import pytest
from taxcalc.growfactors import GrowFactors
from taxcalc.policy import Policy
from taxcalc.records import Records


@pytest.fixture(scope='module', name='bad_gf_file')
def fixture_bad_gf_file():
    """
    Fixture for invalid growfactors file.
    """
    txt = ('YEAR,AWAGE,ACPIU,ABADNAME,ASOCSEC\n'
           '2015,1.000,1.000,1.000000,1.00000\n')
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as tfile:
        tfile.write(txt)
    yield tfile
    os.remove(tfile.name)


def test_improper_usage(bad_gf_file):
    """
    Tests of improper usage of GrowFactors object.
    """
    with pytest.raises(ValueError):
        gfo = GrowFactors({})
    with pytest.raises(ValueError):
        gfo = GrowFactors('non_existent_file.csv')
    with pytest.raises(ValueError):
        gfo = GrowFactors(bad_gf_file.name)
    gfo = GrowFactors()
    fyr = gfo.first_year
    lyr = gfo.last_year
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(fyr - 1, lyr)
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(fyr, lyr + 1)
    with pytest.raises(ValueError):
        gfo.price_inflation_rates(lyr, fyr)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(fyr - 1, lyr)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(fyr, lyr + 1)
    with pytest.raises(ValueError):
        gfo.wage_growth_rates(lyr, fyr)
    with pytest.raises(ValueError):
        gfo.factor_value('BADNAME', fyr)
    with pytest.raises(ValueError):
        gfo.factor_value('AWAGE', fyr - 1)
    with pytest.raises(ValueError):
        gfo.factor_value('AWAGE', lyr + 1)


def test_update_after_use():
    """
    Test of improper update after GrowFactors object has been used.
    """
    gfo = GrowFactors()
    gfo.price_inflation_rates(gfo.first_year, gfo.last_year)
    with pytest.raises(ValueError):
        gfo.update('AWAGE', 2013, 0.01)


def test_proper_usage():
    """
    Test proper usage of GrowFactors object.
    """
    gfo = GrowFactors()
    pir = gfo.price_inflation_rates(2013, 2020)
    assert len(pir) == 8
    wgr = gfo.wage_growth_rates(2013, 2021)
    assert len(wgr) == 9
    val = gfo.factor_value('AWAGE', 2013)
    assert val > 1.0


def test_growfactors_csv_values():
    """
    Test numerical contents of growfactors.csv file.
    """
    gfo = GrowFactors()
    min_data_year = min(Records.PUFCSV_YEAR, Records.CPSCSV_YEAR)
    if min_data_year < Policy.JSON_START_YEAR:
        for gfname in GrowFactors.VALID_NAMES:
            val = gfo.factor_value(gfname, min_data_year)
            assert val == 1
