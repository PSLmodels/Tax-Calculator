import os
import pytest
from taxcalc.filings.base import Form, Filing
from taxcalc.filings.util import FormMapper


def test_filing_properties():
    subject = Filing(1999, '47')
    assert subject.filer_id == '47'
    assert subject.year == 1999


def test_filing_add_form(form_class_1):
    subject = Filing(1999, '0')
    # wrong year
    with pytest.raises(ValueError):
        subject.add_form(form_class_1(2000, fields={'ssn': '0'}))
    # wrong filer
    with pytest.raises(ValueError):
        subject.add_form(form_class_1(1999, fields={'ssn': '47'}))
    # ok!
    subject.add_form(form_class_1(1999, fields={'ssn': '0'}))
    # can't add another instance of the same form class
    with pytest.raises(ValueError):
        subject.add_form(form_class_1(1999, fields={'ssn': '0'}))


def test_filing_drop_empty(form_1, form_2):
    subject = Filing(1999, '0')
    subject.add_form(form_1)
    form_2.set_field('line1', '')
    subject.add_form(form_2)
    subject.drop_empty_forms()
    assert len(subject._forms) == 1


def test_filing_to_dir(form_1, form_2, form_class_1, form_class_2, tmpdir):
    path = tmpdir.strpath
    subject = Filing(1999, '0')
    subject.add_form(form_1)
    subject.add_form(form_2)
    subject.to_dir(path)
    results = {}
    registry = {'form1': form_class_1, 'form2': form_class_2}
    for filename in os.listdir(path):
        parsed = Form.parse(os.path.join(path, filename), registry)
        results[parsed.form_id()] = parsed

    assert results['form1'].to_dict() == form_1.to_dict()
    assert results['form2'].to_dict() == form_2.to_dict()


def test_filing_extends_mapper(form_class_1, form_class_2, filing_class_1):
    # It inherits from FormMapper
    assert issubclass(filing_class_1, FormMapper)
    assert filing_class_1.fields_read(1999) == {'form1': {'line3', 'line4'}}
    assert filing_class_1.rvars_generated(1999) == \
        {'filer_id', 'year', 'weight', 'c', 'd'}
    assert filing_class_1.rvars_used(1999) == {'cc', 'dd'}
    assert filing_class_1.fields_written(1999) == {'form2': {'line3', 'line4'}}

    # It provides a store for FormMapper using fields from stored forms
    subject = filing_class_1(1999, '0')
    fields = {'ssn': '0', 'line3': '3', 'line4': '4'}
    form_1 = form_class_1(1999, fields=fields)
    form_2 = form_class_2(1999, fields=fields)
    subject.add_form(form_1)
    subject.add_form(form_2)
    assert subject.read_rvars() == \
        {'filer_id': '0', 'year': '1999', 'weight': '1', 'c': '3', 'd': '4'}
    subject.write_rvars({'cc': '7', 'dd': '47'})
    assert form_1.fields == fields
    assert form_2.fields == {'ssn': '0', 'line3': '7', 'line4': '47'}


def test_filing_example(filing_class_1):
    # It uses FormMapper to provide input fields from forms in examples
    subject = filing_class_1.example(1999, all_inputs=True)
    assert subject.forms['form1'].fields == \
        {'ssn': '0', 'line1': '0', 'line2': '0', 'line3': '0', 'line4': '0'}
    assert subject.forms['form2'].fields == {'ssn': '0'}

    # It can optionally drop forms that didn't have input fields in examples
    subject = filing_class_1.example(1999, all_inputs=True, drop_empty=True)
    assert 'form1' in subject.forms
    assert 'form2' not in subject.forms


def test_filing_with_forms(form_class_mapped_1, form_class_mapped_2,
                           filing_class_1):
    # It provides helpers to combine its Mapper output with that of its forms
    assert filing_class_1.fields_read_with_forms(1999) == \
        {'form1': {'line1', 'line2', 'line3', 'line4'}, 'form2': set()}
    assert filing_class_1.fields_written_with_forms(1999) == \
        {'form1': set(), 'form2': {'line1', 'line2', 'line3', 'line4'}}
    assert filing_class_1.rvars_generated_with_forms(1999) == \
        {'filer_id', 'year', 'weight', 'a', 'b', 'c', 'd'}
    assert filing_class_1.rvars_used_with_forms(1999) == \
        {'aa', 'bb', 'cc', 'dd'}

    subject = filing_class_1.example(1999, all_inputs=True)
    subject.forms['form1'].set_fields(
        {'line1': '1', 'line2': '2', 'line3': '3', 'line4': '4'})
    assert subject.read_rvars_with_forms() == {
        'filer_id': '0', 'year': '1999', 'weight': '1',
        'a': '1', 'b': '2', 'c': '3', 'd': '4'
    }
    subject.write_rvars_with_forms(
        {'aa': '0', 'bb': '1', 'cc': '7', 'dd': '47'})
    assert subject.forms['form1'].fields == \
        {'ssn': '0', 'line1': '1', 'line2': '2', 'line3': '3', 'line4': '4'}
    assert subject.forms['form2'].fields == \
        {'ssn': '0', 'line1': '0', 'line2': '1', 'line3': '7', 'line4': '47'}


def test_ensure_written_forms_available(filing_class_1):
    subject = filing_class_1(1999, '0')
    assert subject.forms == {}
    subject.ensure_written_forms_available()
    assert 'form1' in subject.forms
    assert 'form2' in subject.forms
