import os
import pytest
import sys

from taxcalc.filings.forms import US1040SEIC, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SEIC(2012)
    form = US1040SEIC(2013)
    form = US1040SEIC(2014)
    form = US1040SEIC(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SEIC(2016)


def test_indirect_p25370():
    form = US1040SEIC(2013)
    assert form.to_evars() == {'EIC': 0}
    form = US1040SEIC(2013, {
        'line2_child1': '', 'line2_child2': '', 'line2_child3': ''})
    assert form.to_evars() == {'EIC': 0}
    form = US1040SEIC(2013, {
        'line2_child1': '123', 'line2_child2': '', 'line2_child3': ''})
    assert form.to_evars() == {'EIC': 1}
    form = US1040SEIC(2013, {
        'line2_child1': '123', 'line2_child2': '456', 'line2_child3': ''})
    assert form.to_evars() == {'EIC': 2}
    form = US1040SEIC(2013, {
        'line2_child1': '123', 'line2_child2': '456', 'line2_child3': '789'})
    assert form.to_evars() == {'EIC': 3}
