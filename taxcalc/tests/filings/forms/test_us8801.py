import os
import pytest
import sys

from taxcalc.filings.forms import US8801, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US8801(2012)
    form = US8801(2013)
    form = US8801(2014)
    form = US8801(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US8801(2016)


def test_direct():
    form = US8801(2013, {'line25': '7600'})
    assert form.to_evars_direct() == {'e07600': 7600}
