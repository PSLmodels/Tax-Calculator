import pytest
from taxcalc.filings.util import trace_map_func
from taxcalc.filings.util.form_mapper import \
    FormMapper, cast_field_to_rvar, cast_rvar_to_field


def test_cast_field_to_rvar():
    # It ensures the results of all field mappings end up as strings,
    # so their interpretation is comparable to that of records csv data.
    assert cast_field_to_rvar('', 1) == '1'


def test_cast_rvar_to_field():
    # It ensures the results of all rvar mappings end up as strings,
    # which is the native type of form data.
    assert cast_rvar_to_field('', 47) == '47'
    return


def test_form_mapper():
    # It requires a year to be initialized
    child_class = type("SomeChild", (FormMapper,), {})
    with pytest.raises(TypeError):
        child_class()

    # The child class must define how to read and write its store
    child_class = type("SomeChild2", (FormMapper,), {})
    subject = child_class(1)
    with pytest.raises(NotImplementedError):
        subject.read_rvars()
    with pytest.raises(NotImplementedError):
        subject.write_rvars({})

    # It allows child classes to declare mapping dicts and functions that
    # are incorporated into maps cached on init and exposed to read/write.
    # Values are formatted using predefined field and rvar formatters.
    read_dict = {'line1': 'a'}
    write_dict = {'b': 'line2'}

    @trace_map_func(['10'], 'q')
    def read_func(x):
        return {'q': x.get('line100') * 2}

    @trace_map_func('z', ['line21'])
    def write_func(x):
        return {'line21': x.get('z') + 1}

    store = {'line1': 1, 'line100': 100}

    def read_store(self):
        return store

    def write_store(self, data):
        store.update(data)

    child_class = type("SomeChild", (FormMapper,), {
        '_READ_DICTS_BY_YEAR': {2016: read_dict},
        '_READ_FUNCS_BY_YEAR': {2016: [read_func]},
        '_WRITE_DICTS_BY_YEAR': {2016: write_dict},
        '_WRITE_FUNCS_BY_YEAR': {2016: [write_func]},
        '_read_store': read_store,
        '_write_store': write_store
    })

    assert child_class.fields_read(2016) == {'line1', '10'}
    assert child_class.rvars_generated(2016) == {'a', 'q'}
    assert child_class.rvars_used(2016) == {'b', 'z'}
    assert child_class.fields_written(2016) == {'line2', 'line21'}

    subject = child_class(2016)
    assert subject.read_rvars() == {'a': '1', 'q': '200'}
    subject.write_rvars({'b': 2, 'z': 20})
    assert store == {
        'line1': 1,
        'line2': '2',
        'line100': 100,
        'line21': '21'
    }
