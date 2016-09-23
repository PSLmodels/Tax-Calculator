import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US2441, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US2441(2012)
    form = US2441(2013)
    form = US2441(2014)
    form = US2441(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US2441(2016)


def test_direct():
    form = US2441(2013, {'line3': '32800'})
    assert form.to_evars_direct() == {'e32800': 32800}


def test_indirect_p25370():
    form = US2441(2013)
    assert form.to_evars() == {'f2441': 0}
    form = US2441(2013, {'line2b_1': '', 'line2b_2': ''})
    assert form.to_evars() == {'f2441': 0}
    form = US2441(2013, {'line2b_1': '123', 'line2b_2': ''})
    assert form.to_evars() == {'f2441': 1}
    form = US2441(2013, {'line2b_1': '123', 'line2b_2': '456'})
    assert form.to_evars() == {'f2441': 2}
