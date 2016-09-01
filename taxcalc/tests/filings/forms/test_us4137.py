import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US4137, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US4137(2012)
    form = US4137(2013)
    form = US4137(2014)
    form = US4137(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US4137(2016)


def test_direct():
    form = US4137(2013, {'line13': '9800'})
    assert form.to_evars_direct() == {'e09800': 9800}
