import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US4952, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US4952(2012)
    form = US4952(2013)
    form = US4952(2014)
    form = US4952(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US4952(2016)


def test_direct():
    form = US4952(2013, {'line4g': '58990'})
    assert form.to_evars_direct() == {'e58990': 58990}
