import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US1040SE, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SE(2012)
    form = US1040SE(2013)
    form = US1040SE(2014)
    form = US1040SE(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SE(2016)


def test_direct():
    form = US1040SE(2013, {
        'line32': '26270',
        'line40': '27200',
    })
    assert form.to_evars_direct() == {
        'e26270': 26270,
        'e27200': 27200,
    }


def test_indirect_p25470():
    form = US1040SE(2013)
    assert not form.to_evars()
    form = US1040SE(2013, {'line18a': ''})
    assert form.to_evars() == {'p25470': 0}
    form = US1040SE(2013, {'line18a': '1', 'line18b': '2', 'line18c': '4'})
    assert form.to_evars() == {'p25470': 7}
