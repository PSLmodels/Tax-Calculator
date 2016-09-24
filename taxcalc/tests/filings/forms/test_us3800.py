import os
import pytest
import sys

from taxcalc.filings.forms import US3800, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US3800(2012)
    form = US3800(2013)
    form = US3800(2014)
    form = US3800(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US3800(2016)


def test_direct():
    form = US3800(2013, {'line17': '7400'})
    assert form.to_evars_direct() == {'e07400': 7400}
