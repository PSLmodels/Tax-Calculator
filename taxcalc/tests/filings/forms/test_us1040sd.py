import os
import pytest
import sys

from taxcalc.filings.forms import US1040SD, UnsupportedFormYearError


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SD(2012)
    form = US1040SD(2013)
    form = US1040SD(2014)
    form = US1040SD(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US1040SD(2016)


def test_direct():
    form = US1040SD(2013, {
        'line7': '22250',
        'line15': '23250',
        'line18': '24518',
        'line19': '24515',
    })
    assert form.to_evars_direct() == {
        'p22250': 22250,
        'p23250': 23250,
        'e24518': 24518,
        'e24515': 24515,
    }
