import os
import pytest
import sys

from taxcalc.filings.forms import US6251, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US6251(2012)
    form = US6251(2013)
    form = US6251(2014)
    form = US6251(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US6251(2016)


def test_direct():
    form = US6251(2013, {'line32': '62900'})
    assert form.to_evars_direct() == {'e62900': 62900}
