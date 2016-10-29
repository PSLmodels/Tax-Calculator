import os
import pytest
from taxcalc.filings.base import Form
from taxcalc.filings.util import FormMapper
from taxcalc.filings.base.errors import *
from taxcalc.utils import write_json_to_file


def test_form_class(tmpdir):
    # identifiers
    assert Form.form_id() == 'form'
    assert Form.full_name() == 'Form : A Basic Form'
    assert Form.supported_years() == set()

    # check_year_support
    with pytest.raises(UnsupportedFormYearError):
        Form.ensure_year_supported(2016)

    # valid_fields
    with pytest.raises(UnsupportedFormYearError):
        Form.valid_fields(2016)

    # instantiation not possible
    with pytest.raises(UnsupportedFormYearError):
        Form(1999)

    # from_registry
    registry = {'form': Form}
    with pytest.raises(ValueError):
        Form.from_registry('form', 2016, {})
    with pytest.raises(UnsupportedFormError):
        Form.from_registry('other_form', 2016, registry)
    with pytest.raises(UnsupportedFormYearError):
        Form.from_registry('form', 2016, registry)

    # from_dict
    as_dict = {'form_id': 'form', 'filing_year': None, 'fields': {}}
    with pytest.raises(ValueError):
        Form.from_dict({}, registry)
    with pytest.raises(UnsupportedFormYearError):
        Form.from_dict(as_dict, registry)

    # from_pdf
    with pytest.raises(NotImplementedError):
        Form.from_pdf('path', registry)

    # parse
    with pytest.raises(UnsupportedFormYearError):
        assert Form.parse(as_dict, registry)
    with pytest.raises(NotImplementedError):
        assert Form.parse('file.pdf', registry)
    with pytest.raises(ValueError):
        assert Form.parse('file.pdf', registry, ext='.json')
    with pytest.raises(ValueError):
        assert Form.parse(None, registry)

    path = os.path.join(tmpdir.strpath, 'parse_test.json')
    write_json_to_file(as_dict, path)
    with pytest.raises(UnsupportedFormYearError):
        assert Form.parse(path, registry)

    # example
    with pytest.raises(UnsupportedFormYearError):
        assert Form.example(2016)


def test_form_child_class(tmpdir):
    child_class = type("TestForm", (Form,), {
        '_TITLE': 'title',
        '_DESCRIPTION': 'description',
        '_VALID_FIELDS_BY_YEAR': {1999: ['line1', 'ssn']},
        '_FILER_ID_FIELD': 'ssn'
    })
    fields = {'line1': '1000', 'ssn': '123'}
    as_dict = {
        'form_id': 'testform',
        'filing_year': 1999,
        'fields': fields
    }
    registry = {'testform': child_class}

    # identifiers
    assert child_class.form_id() == 'testform'
    assert child_class.full_name() == 'title : description'
    assert child_class.supported_years() == {1999}

    # check_year_support()
    child_class.ensure_year_supported(1999)
    with pytest.raises(UnsupportedFormYearError):
        child_class.ensure_year_supported(1998)
    with pytest.raises(UnsupportedFormYearError):
        child_class.ensure_year_supported(2000)

    # valid_fields()
    assert child_class.valid_fields(1999) == ['line1', 'ssn']
    with pytest.raises(UnsupportedFormYearError):
        child_class.valid_fields(2000)

    # from_registry
    subject = Form.from_registry(
        'testform', 1999, registry, fields=fields
    )
    assert subject.year == 1999
    assert subject.filer_id == '123'

    # from_dict
    subject = Form.from_dict(as_dict, registry)
    assert subject.year == 1999
    assert subject.fields == fields
    assert subject.filer_id == '123'

    # parse
    instance = child_class(1999)
    assert Form.parse(instance, registry) == instance

    subject = Form.parse(as_dict, registry)
    assert subject.year == 1999
    assert subject.fields == fields
    assert subject.filer_id == '123'

    path = os.path.join(tmpdir.strpath, 'parse_test.json')
    write_json_to_file(as_dict, path)
    subject = Form.parse(path, registry)
    assert subject.year == 1999
    assert subject.fields == fields
    assert subject.filer_id == '123'

    # example
    subject = child_class.example(1999)
    assert subject.year == 1999
    assert subject.fields == {'ssn': '0'}
    assert subject.filer_id == '0'

    subject = child_class.example(1999, all_valid=True, filer_id='47')
    assert subject.year == 1999
    assert subject.fields == {'line1': '0', 'ssn': '47'}
    assert subject.filer_id == '47'


def test_form_child_instance(tmpdir):
    child_class = type("TestForm", (Form,), {
        '_TITLE': 'title',
        '_DESCRIPTION': 'description',
        '_VALID_FIELDS_BY_YEAR': {1999: ['line1', 'ssn']},
        '_FILER_ID_FIELD': 'ssn'
    })
    registry = {'testform': child_class}

    subject = child_class(1999)
    assert subject.year == 1999
    assert subject.filer_id is None
    assert subject.is_empty

    subject = child_class(1999, filer_id='47')
    assert subject.filer_id == '47'
    assert subject.is_empty

    with pytest.raises(ValueError):
        subject.set_field('unknown_field', '1')

    subject.set_field('line1', '1000')
    assert not subject.is_empty

    subject.set_fields({'ssn': '47', 'line1': '1000'})
    assert subject.filer_id == '47'

    assert subject.to_dict() == {
        'form_id': 'testform',
        'filing_year': 1999,
        'fields': {'ssn': '47', 'line1': '1000'},
    }

    with pytest.raises(NotImplementedError):
        subject.to_pdf_file('path')

    path = os.path.join(tmpdir.strpath, 'parse_test.json')
    subject.to_json_file(path)
    subject = Form.parse(path, registry)
    assert subject.year == 1999
    assert subject.filer_id == '47'
    assert not subject.is_empty


def test_form_extends_form_mapper():
    read_dict = {'line1': 'a'}
    write_dict = {'b': 'line2'}
    child_class = type("TestForm", (Form,), {
        '_READ_DICTS_BY_YEAR': {1999: read_dict},
        '_WRITE_DICTS_BY_YEAR': {1999: write_dict},
        '_VALID_FIELDS_BY_YEAR': {1999: ['line1', 'line2', 'line3', 'ssn']},
        '_FILER_ID_FIELD': 'ssn'
    })

    # It inherits from FormMapper
    subject = child_class(1999)
    assert isinstance(subject, FormMapper)

    # It provides a store for FormMapper using fields
    subject = child_class(1999, fields={'line1': '1', 'line3': '3'})
    assert subject.read_rvars() == {'a': '1'}
    subject.write_rvars({'b': '2'})
    assert subject.fields == {'line1': '1', 'line2': '2', 'line3': '3'}

    # It uses FormMapper to provide input fields in examples
    subject = child_class.example(1999, all_inputs=True, filer_id='47')
    assert subject.fields == {'ssn': '47', 'line1': '0'}
