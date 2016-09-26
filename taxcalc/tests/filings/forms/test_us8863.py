import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US8863, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US8863(2012)
    form = US8863(2013)
    form = US8863(2014)
    form = US8863(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US8863(2016)


def test_direct():
    form = US8863(2013, {
        'line4': '87530',
        'line7': '87521',
        'line30': '87482',
    })
    assert form.to_evars_direct() == {
        'e87530': 87530,
        'p87521': 87521,
        'P87482': 87482,
    }
