import pytest

from taxcalc.filings.forms import TaxForm
from taxcalc.filings.forms import UnsupportedFormYearError
from taxcalc.utils import string_to_number


def test_tax_form_creation_valid():
    TaxForm(1999)
    form = TaxForm(1999, {'field_1': 47})
    assert form.form_id()
    assert form.form_name()
    assert form.year == 1999
    assert form.tax_unit_id == '0'


def test_tax_form_creation_invalid():
    with pytest.raises(ValueError):
        TaxForm('should be an integer')


def test_tax_form_basic_inheritance():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_DESCRIPTIVE_NAME': 'descriptive',
        '_NUMERIC_NAME': 'numeric',
    })
    form = child_class(1999)
    assert form.form_id() == 'testtaxform'
    assert form.form_name() == 'numeric : descriptive'
    assert form.year == 1999


def test_tax_form_year_support():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_SUPPORTED_YEARS': [2014, 2015],
    })
    with pytest.raises(UnsupportedFormYearError):
        child_class(2013)
    child_class(2014)
    child_class(2015)
    with pytest.raises(UnsupportedFormYearError):
        child_class(2016)


def test_tax_form_tax_id():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_TAX_UNIT_ID_FIELD': 'some_id_field'
    })
    form = child_class(1999)
    assert form.tax_unit_id == '0'
    form.set_field('some_id_field', '47')
    assert form.tax_unit_id == '47'


def test_tax_form_evar_mapping_direct():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_EVAR_MAP': {
            'field_1': 'e00001',
            'field_2': 'e00002',
        },
        '_EVAR_MAP_BY_YEAR': {
            1999: {
                'field_3': 'e00003',
            }
        },
    })
    form = child_class(1999)
    assert form.to_evars_direct() == {}
    form.set_fields({
        'field_1': '1',
        'field_2': '2',
        'field_3': '3',
    })
    assert form.to_evars_direct() == {
        'e00001': 1,
        'e00002': 2,
        'e00003': 3,
    }

    child_class = type("EmptyTaxForm", (TaxForm,), {
        '_EVAR_MAP': {}, '_EVAR_MAP_BY_YEAR': {}
    })
    form = child_class(2013, fields={'field_1': 47, 'field_2': 59})
    assert form.to_evars_direct() == {}


def test_tax_form_evar_mapping_direct_conflict():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_EVAR_MAP': {
            'field_1': 'e00001',
            'field_2': 'e00001',
        },
    })
    form = child_class(1999, {'field_1': '1', 'field_2': '2'})
    with pytest.raises(ValueError):
        form.to_evars()


def test_tax_form_evar_mapping_indirect():
    def example_to_evars_indirect(self):
        fields = self._fields
        if 'field_1' in fields and 'field_1_checked' in fields:
            return {'e00001': string_to_number(fields['field_1'])}
        else:
            return None

    child_class = type("TestTaxForm", (TaxForm,), {
        'to_evars_indirect': example_to_evars_indirect
    })
    form = child_class(1999)
    assert not form.to_evars_indirect()
    form.set_fields({
        'field_1': '1',
        'field_1_checked': 'X',
    })
    assert form.to_evars_indirect() == {
        'e00001': 1,
    }


def test_tax_form_evar_mapping_both():
    def example_to_evars_indirect(self):
        fields = self._fields
        if 'field_2' in fields and 'field_2_checked' in fields:
            return {'e00002': string_to_number(fields['field_2'])}
        else:
            return None

    child_class = type("TestTaxForm", (TaxForm,), {
        '_EVAR_MAP': {
            'field_1': 'e00001',
        },
        'to_evars_indirect': example_to_evars_indirect
    })
    form = child_class(1999)
    assert form.to_evars() == {}
    form.set_fields({
        'field_1': '1',
        'field_2': '2',
        'field_2_checked': 'X',
    })
    assert form.to_evars() == {
        'e00001': 1,
        'e00002': 2,
    }


def test_tax_form_evar_mapping_both_conflict():
    child_class = type("TestTaxForm", (TaxForm,), {
        '_EVAR_MAP': {
            'field_1': 'e00001',
        },
        'to_evars_indirect': lambda self: {
            'e00001': self._fields['field_2']
        }
    })
    form = child_class(1999, {'field_1': '1', 'field_2': '2'})
    with pytest.raises(ValueError):
        form.to_evars()


def test_tax_form_to_pdf():
    form = TaxForm(1999)
    with pytest.raises(NotImplementedError):
        form.to_pdf()
