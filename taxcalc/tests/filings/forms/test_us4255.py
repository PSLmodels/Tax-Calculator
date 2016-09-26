import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US4255, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US4255(2011)
    form = US4255(2012)
    form = US4255(2013)
    form = US4255(2014)
    form = US4255(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US4255(2016)


def test_direct():
    form = US4255(2013, {'line15': '9700'})
    assert form.to_evars_direct() == {'e09700': 9700}
