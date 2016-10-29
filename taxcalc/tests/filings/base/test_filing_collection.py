import os
import pytest
from taxcalc import Records
from taxcalc.filings.base import FilingCollection, Form
from taxcalc.utils import write_json_to_file


def test_filing_collection_init(filing_class_1):
    with pytest.raises(ValueError):
        FilingCollection(None)
    subject = FilingCollection(filing_class_1)
    assert subject.filings == {}


def test_filing_collection_add_form(filing_class_1, form_1, form_2):
    subject = FilingCollection(filing_class_1)
    with pytest.raises(ValueError):
        subject.add_form(None)
    subject.add_form(form_1)
    filing = subject.filings[1999]['0']
    assert isinstance(filing, filing_class_1)
    assert filing.forms['form1'] == form_1
    subject.add_form(form_2)
    assert filing.forms['form2'] == form_2


def test_filing_collection_add_filing(filing_class_1, filing_class_2):
    subject = FilingCollection(filing_class_1)
    with pytest.raises(ValueError):
        subject.add_filing(filing_class_2(2000, '0'))
    filing_2 = filing_class_1(2000, '0')
    subject.add_filing(filing_2)
    assert subject.filings[2000]['0'] == filing_2
    with pytest.raises(ValueError):
        subject.add_filing(filing_class_2(2000, '0'))


def test_filing_collection_to_from_dir(filing_class_1,
                                       form_class_1, form_class_2,
                                       form_1, form_2,
                                       tmpdir):
    subject = FilingCollection(filing_class_1)
    subject.add_form(form_1)
    subject.add_form(form_2)
    path = tmpdir.strpath
    form_registry = {'form1': form_class_1, 'form2': form_class_2}

    # to dir
    subject.to_dir(path)
    form_1_path = os.path.join(path, '1999', '0', 'form1.json')
    form_2_path = os.path.join(path, '1999', '0', 'form2.json')
    parsed_1 = Form.parse(form_1_path, form_registry)
    parsed_2 = Form.parse(form_2_path, form_registry)
    assert form_1.to_dict() == parsed_1.to_dict()
    assert form_2.to_dict() == parsed_2.to_dict()

    # from dir
    with pytest.raises(ValueError):
        FilingCollection.from_dir(None, filing_class_1)
    write_json_to_file({'trash': True}, os.path.join(path, 'trash.json'))
    read = FilingCollection.from_dir(path, filing_class_1, verbose=True)
    filing = read.filings[1999]['0']
    assert filing.forms['form1'].to_dict() == form_1.to_dict()
    assert filing.forms['form2'].to_dict() == form_2.to_dict()


def test_filing_collection_example(filing_class_1):
    subject = FilingCollection.example(filing_class_1, 1999)
    expect_filing = filing_class_1.example(1999)
    result_filing = subject.filings[expect_filing.year][expect_filing.filer_id]
    for form_id, form in result_filing.forms.items():
        assert expect_filing.forms[form_id].to_dict() == form.to_dict()
