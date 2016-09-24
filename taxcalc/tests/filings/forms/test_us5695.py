import os
import pytest
import sys

from taxcalc.filings.forms import US5695, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US5695(2012)
    form = US5695(2013)
    form = US5695(2014)
    form = US5695(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US5695(2016)


def test_direct():
    form = US5695(2013, {'line15': '7260'})
    assert form.to_evars_direct() == {'e07260': 7260}
