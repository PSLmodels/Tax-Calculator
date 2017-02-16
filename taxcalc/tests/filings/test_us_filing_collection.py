import pytest
from pandas import DataFrame
from taxcalc import Records
from taxcalc.filings import USFilingCollection, USFiling
from taxcalc.utils import string_to_number


@pytest.fixture()
def filing_1():
    return USFiling.example(2014, all_inputs=True, filer_id='1')


@pytest.fixture()
def filing_2():
    return USFiling.example(2015, all_inputs=True, filer_id='1')


@pytest.fixture()
def filing_3():
    return USFiling.example(2015, all_inputs=True, filer_id='2')


@pytest.fixture()
def collection_with_some_filings(filing_1, filing_2, filing_3):
    result = USFilingCollection()
    result.add_filing(filing_1)
    result.add_filing(filing_2)
    result.add_filing(filing_3)
    return result


def test_us_filing_collection_init():
    # It calls FilingCollection init without the need for a filing class
    assert isinstance(USFilingCollection(), USFilingCollection)


def test_us_filing_collection_example():
    # It calls FilingCollection example without the need for a filing class
    assert isinstance(USFilingCollection.example(2015), USFilingCollection)


def test_us_filing_collection_from_dir(tmpdir):
    # It calls FilingCollection example without the need for a filing class
    assert isinstance(
        USFilingCollection.from_dir(tmpdir.strpath), USFilingCollection
    )


def test_us_filing_collection_to_records(filing_1, filing_2, filing_3,
                                         collection_with_some_filings):
    subject = collection_with_some_filings
    records = subject.to_records()
    assert set(records.keys()) == {2014, 2015}
    assert isinstance(records[2014], Records)
    assert isinstance(records[2015], Records)
    assert records[2014].dim == 1
    assert records[2015].dim == 2

    df_2014 = records[2014].to_df()
    df_2015 = records[2015].to_df()
    df_filing_1 = df_2014.loc[df_2014['RECID'] == '1']
    df_filing_2 = df_2015.loc[df_2015['RECID'] == '1']
    df_filing_3 = df_2015.loc[df_2015['RECID'] == '2']
    dict_filing_1 = list(df_filing_1.to_dict(orient='index').values())[0]
    dict_filing_2 = list(df_filing_2.to_dict(orient='index').values())[0]
    dict_filing_3 = list(df_filing_3.to_dict(orient='index').values())[0]

    for filing, result in [
            (filing_1, dict_filing_1),
            (filing_2, dict_filing_2),
            (filing_3, dict_filing_3)]:

        for key, value in filing.read_rvars_with_forms().items():
            assert string_to_number(result[key]) == string_to_number(value)


def test_us_filing_collection_write_records():
    records = {}
    filers = {'1', '2', '3'}
    example_record_data = [
        {'RECID': filer, 'MARS': '1'}
        for filer in filers
    ]
    _2013_2015 = {2013, 2014, 2015}
    for year in _2013_2015:
        records[year] = Records(
            data=DataFrame(example_record_data),
            start_year=year,
            weights=None,
        )
    subject = USFilingCollection()
    subject.write_records(records)
    assert set(subject.filings.keys()) == _2013_2015
    for year in _2013_2015:
        filings_by_filer = subject.filings[year]
        assert set(filings_by_filer.keys()) == filers
        for filing in filings_by_filer.values():
            fields_expected = filing.fields_written_with_forms(year)
            for form_id, fields in fields_expected.items():
                assert form_id in filing.forms
                form = filing.forms[form_id]
                for field in fields:
                    assert field in form.fields
                    assert form.fields[field]


def test_us_filing_collection_calc_all(collection_with_some_filings):
    subject = collection_with_some_filings
    subject.calc_all(verbose=True)
    for year in subject.filings:
        filings_by_filer = subject.filings[year]
        for filing in filings_by_filer.values():
            fields_expected = filing.fields_written_with_forms(year)
            for form_id, fields in fields_expected.items():
                assert form_id in filing.forms
                form = filing.forms[form_id]
                for field in fields:
                    assert field in form.fields
                    assert form.fields[field]


def test_us_filing_collection_compare():
    subject = USFilingCollection()
    with pytest.raises(NotImplementedError):
        subject.compare_to(None)
