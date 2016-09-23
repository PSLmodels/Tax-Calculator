import os
import pytest
import sys

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..', '..', '..'))

from taxcalc.filings.forms import US1040, UnsupportedFormYearError

test_direct_fields_2013 = {
    'line6d': '1',
    'line7': '200',
    'line8a': '300',
    'line8b': '400',
    'line9a': '600',
    'line9b': '650',
    'line10': '700',
    'line11': '800',
    'line12': '900',
    'line14': '1200',
    'line15b': '1400',
    'line16a': '1500',
    'line16b': '1700',
    'line17': '2000',
    'line18': '2100',
    'line19': '2300',
    'line20a': '2400',
    'line23': '3220',
    'line25': '3290',
    'line28': '3300',
    'line29': '3270',
    'line30': '3400',
    'line31a': '3500',
    'line32': '3150',
    'line33': '3210',
    'line34': '3230',
    'line35': '3240',
    'line47': '7300',
    'line50': '7240',
    'line52': '7260',
    'line53': '8000',
    'line58': '9900',
    'line63': '11200',
    'line65': '11070',
}
test_direct_fields_2014_2015 = {
    'line6d': '1',
    'line7': '200',
    'line8a': '300',
    'line8b': '400',
    'line9a': '600',
    'line9b': '650',
    'line10': '700',
    'line11': '800',
    'line12': '900',
    'line14': '1200',
    'line15b': '1400',
    'line16a': '1500',
    'line16b': '1700',
    'line17': '2000',
    'line18': '2100',
    'line19': '2300',
    'line20a': '2400',
    'line23': '3220',
    'line25': '3290',
    'line28': '3300',
    'line29': '3270',
    'line30': '3400',
    'line31a': '3500',
    'line32': '3150',
    'line33': '3210',
    'line34': '3230',
    'line35': '3240',
    'line48': '7300',
    'line51': '7240',
    'line53': '7260',
    'line54': '8000',
    'line59': '9900',
    'line65': '11200',
    'line67': '11070',
}
test_direct_evars = {
    'XTOT': 1,
    'e00200': 200,
    'e00300': 300,
    'e00400': 400,
    'e00600': 600,
    'e00650': 650,
    'e00700': 700,
    'e00800': 800,
    'e00900': 900,
    'e01200': 1200,
    'e01400': 1400,
    'e01500': 1500,
    'e01700': 1700,
    'e02000': 2000,
    'e02100': 2100,
    'e02300': 2300,
    'e02400': 2400,
    'e03220': 3220,
    'e03290': 3290,
    'e03300': 3300,
    'e03270': 3270,
    'e03400': 3400,
    'e03500': 3500,
    'e03150': 3150,
    'e03210': 3210,
    'e03230': 3230,
    'e03240': 3240,
    'e07300': 7300,
    'e07240': 7240,
    'e07260': 7260,
    'p08000': 8000,
    'e09900': 9900,
    'e11200': 11200,
    'e11070': 11070,
}


def test_year_support():
    with pytest.raises(UnsupportedFormYearError):
        form = US1040(2012)
    form = US1040(2013)
    form = US1040(2014)
    form = US1040(2015)
    with pytest.raises(UnsupportedFormYearError):
        form = US1040(2016)


def test_direct_2013():
    form = US1040(2013, test_direct_fields_2013)
    assert form.to_evars_direct() == test_direct_evars


def test_direct_2014_2015():
    form = US1040(2014, test_direct_fields_2014_2015)
    assert form.to_evars_direct() == test_direct_evars


def test_indirect_mars():
    form = US1040(2013, {'line1': ''})
    assert not form.to_evars()
    form = US1040(2013, {'line1': 'Checked'})
    assert form.to_evars() == {'MARS': 1}
    form = US1040(2014, {'line2': 'X'})
    assert form.to_evars() == {'MARS': 2}
    form = US1040(2015, {'line3': 'Foo'})
    assert form.to_evars() == {'MARS': 3}
    form = US1040(2013, {'line4': 'Bar'})
    assert form.to_evars() == {'MARS': 4}
    form = US1040(2014, {'line5': '47'})
    assert form.to_evars() == {'MARS': 5}


def test_indirect_dsi():
    form = US1040(2013, {'line6a': 'X'})
    assert form.to_evars() == {'DSI': 0}
    form = US1040(2013, {'line6a': ''})
    assert form.to_evars() == {'DSI': 1}


def test_indirect_e0110():
    form = US1040(2013, {'line13': '110', 'line13_no_sch_d': ''})
    assert not form.to_evars()
    form = US1040(2013, {'line13': '110', 'line13_no_sch_d': 'X'})
    assert form.to_evars() == {'e01100': 110}


def test_indirect_blind():
    form = US1040(2013, {'line39a_blind': '', 'line39a_blind_spouse': ''})
    assert form.to_evars() == {'blind_head': 0, 'blind_spouse': 0}
    form = US1040(2013, {'line39a_blind': 'X', 'line39a_blind_spouse': 'Foo'})
    assert form.to_evars() == {'blind_head': 1, 'blind_spouse': 1}


def test_indirect_midr():
    form = US1040(2013, {'line39b': ''})
    assert form.to_evars() == {'MIDR': 0}
    form = US1040(2013, {'line39b': 'X'})
    assert form.to_evars() == {'MIDR': 1}


def test_indirect_e07600_2013():
    form = US1040(2013, {
        'line53': '7600', 'line53a': '', 'line53b': '', 'line53c': ''})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2013, {
        'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': 'X'})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2013, {
        'line53': '7600', 'line53a': 'X', 'line53b': 'X', 'line53c': ''})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2013, {
        'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': 'X'})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2013, {
        'line53': '7600', 'line53a': '', 'line53b': 'X', 'line53c': ''})
    assert form.to_evars() == {'e07600': 7600, 'p08000': 7600}


def test_indirect_e07600_2014_2015():
    form = US1040(2014, {
        'line54': '7600', 'line54a': '', 'line54b': '', 'line54c': ''})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2014, {
        'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': 'X'})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2014, {
        'line54': '7600', 'line54a': 'X', 'line54b': 'X', 'line54c': ''})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2014, {
        'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': 'X'})
    assert form.to_evars() == {'p08000': 7600}
    form = US1040(2014, {
        'line54': '7600', 'line54a': '', 'line54b': 'X', 'line54c': ''})
    assert form.to_evars() == {'e07600': 7600, 'p08000': 7600}


def test_indirect_e09800_2013():
    form = US1040(2013, {
        'line57': '9800', 'line57a': '', 'line57b': ''})
    assert not form.to_evars()
    form = US1040(2013, {
        'line57': '9800', 'line57a': 'X', 'line57b': 'X'})
    assert not form.to_evars()
    form = US1040(2013, {
        'line57': '9800', 'line57a': 'X', 'line57b': ''})
    assert form.to_evars() == {'e09800': 9800}


def test_indirect_e09800_2014_2015():
    form = US1040(2014, {
        'line58': '9800', 'line58a': '', 'line58b': ''})
    assert not form.to_evars()
    form = US1040(2014, {
        'line58': '9800', 'line58a': 'X', 'line58b': 'X'})
    assert not form.to_evars()
    form = US1040(2014, {
        'line58': '9800', 'line58a': 'X', 'line58b': ''})
    assert form.to_evars() == {'e09800': 9800}
