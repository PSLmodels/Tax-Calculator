import os
import pytest
import sys

from taxcalc.filings.forms import US1040SA, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SA(2012)
    form = US1040SA(2013)
    form = US1040SA(2014)
    form = US1040SA(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SA(2016)


def test_direct():
    form = US1040SA(2013, {
        'line1': '17500',
        'line6': '18500',
        'line15': '19200',
        'line16': '19800',
        'line17': '20100',
        'line20': '20500',
        'line24': '20400',
    })
    assert form.to_evars_direct() == {
        'e17500': 17500,
        'e18500': 18500,
        'e19200': 19200,
        'e19800': 19800,
        'e20100': 20100,
        'e20500': 20500,
        'e20400': 20400,
    }


def test_us1040_indirect_e18400():
    form = US1040SA(2013, {'line5': '18400', 'line5a': '', 'line5b': ''})
    assert not form.to_evars()
    form = US1040SA(2013, {'line5': '18400', 'line5a': 'X', 'line5b': 'X'})
    assert not form.to_evars()
    form = US1040SA(2013, {'line5': '18400', 'line5a': '', 'line5b': 'X'})
    assert not form.to_evars()
    form = US1040SA(2013, {'line5': '18400', 'line5a': 'X', 'line5b': ''})
    assert form.to_evars() == {'e18400': 18400}
