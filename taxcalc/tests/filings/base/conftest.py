import pytest
from taxcalc.filings import Form, trace_map_func, Filing


@pytest.fixture()
def form_class_config():
    return {
        '_TITLE': 'title',
        '_DESCRIPTION': 'description',
        '_VALID_FIELDS_BY_YEAR': {
            1999: ['ssn', 'line1', 'line2', 'line3', 'line4', 'line5'],
            2000: ['ssn', 'line1', 'line2', 'line3', 'line4', 'line5']
        },
        '_FILER_ID_FIELD': 'ssn'
    }


@pytest.fixture()
def form_class_1(form_class_config):
    return type("Form1", (Form,), form_class_config)


@pytest.fixture()
def form_class_2(form_class_config):
    return type("Form2", (Form,), form_class_config)


@pytest.fixture()
def form_1(form_class_1):
    return form_class_1(1999, fields={'ssn': '0'})


@pytest.fixture()
def form_2(form_class_2):
    return form_class_2(1999, fields={'ssn': '0'})


@pytest.fixture()
def form_class_mapped_1(form_class_1):
    read_dict = {'line1': 'a'}

    @trace_map_func('line2', 'b')
    def read_func(x):
        return {'b': x.get('line2')}

    setattr(form_class_1, '_READ_DICTS_BY_YEAR', {1999: read_dict})
    setattr(form_class_1, '_READ_FUNCS_BY_YEAR', {1999: [read_func]})
    return form_class_1


@pytest.fixture()
def form_class_mapped_2(form_class_2):
    write_dict = {'aa': 'line1'}

    @trace_map_func('bb', 'line2')
    def write_func(x):
        return {'line2': x.get('bb')}

    setattr(form_class_2, '_WRITE_DICTS_BY_YEAR', {1999: write_dict})
    setattr(form_class_2, '_WRITE_FUNCS_BY_YEAR', {1999: [write_func]})
    return form_class_2


@pytest.fixture()
def filing_class_1(form_class_mapped_1, form_class_mapped_2):
    read_dict = {'form1/line3': 'c'}
    write_dict = {'cc': 'form2/line3'}

    @trace_map_func('form1/line4', 'd')
    def read_func(x):
        return {'d': x.get('form1/line4')}

    @trace_map_func('dd', 'form2/line4')
    def write_func(x):
        return {'form2/line4': x.get('dd')}

    return type("TestFiling", (Filing,), {
        '_READ_DICTS_BY_YEAR': {1999: read_dict},
        '_READ_FUNCS_BY_YEAR': {1999: [read_func]},
        '_WRITE_DICTS_BY_YEAR': {1999: write_dict},
        '_WRITE_FUNCS_BY_YEAR': {1999: [write_func]},
        'FORM_CLASSES_BY_ID': {
            'form1': form_class_mapped_1, 'form2': form_class_mapped_2
        },
        'FILER_ID_RVAR': 'filer_id',
        'FILING_YEAR_RVAR': 'year',
        'WEIGHT_RVAR': 'weight',
    })


@pytest.fixture()
def filing_class_2():
    return type("TestFiling", (Filing,), {})
