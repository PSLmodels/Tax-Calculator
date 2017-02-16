import os
from taxcalc.filings.base import Form
from taxcalc.utils import read_json_from_file, merge_dicts_ex
from .read_funcs import READ_FUNCS_BY_FORM
from .write_funcs import WRITE_FUNCS_BY_FORM


_FILE_PATH = os.path.dirname(__file__)
_VALID_FIELDS_PATH = os.path.join(_FILE_PATH, 'valid_fields.json')
_BASIC_INFO_PATH = os.path.join(_FILE_PATH, 'basic_info.json')
_READ_DICTS_PATH = os.path.join(_FILE_PATH, 'read_dicts.json')
_WRITE_DICTS_PATH = os.path.join(_FILE_PATH, 'write_dicts.json')

_VALID_FIELDS = read_json_from_file(_VALID_FIELDS_PATH)
_BASIC_INFO = read_json_from_file(_BASIC_INFO_PATH)
_READ_DICTS = read_json_from_file(_READ_DICTS_PATH)
_WRITE_DICTS = read_json_from_file(_WRITE_DICTS_PATH)

_READ_FUNCS = READ_FUNCS_BY_FORM
_WRITE_FUNCS = WRITE_FUNCS_BY_FORM


def _get_year_list(source):
    _all = source.get('all_years', [])
    _2013 = source.get('2013', [])
    _2014_2015 = source.get('2014_2015', [])
    return {
        2013: _all + _2013,
        2014: _all + _2014_2015,
        2015: _all + _2014_2015,
    }


def _get_year_dict(source):
    _all = source.get('all_years', {})
    _2013 = source.get('2013', {})
    _2014_2015 = source.get('2014_2015', {})
    return {
        2013: merge_dicts_ex(_all, _2013),
        2014: merge_dicts_ex(_all, _2014_2015),
        2015: merge_dicts_ex(_all, _2014_2015),
    }


def _define_us_form(name):
    form_id = name.lower()
    basic_info = _BASIC_INFO[form_id]
    valid_fields = _VALID_FIELDS[form_id]
    read_dicts = _READ_DICTS.get(form_id, {})
    write_dicts = _WRITE_DICTS.get(form_id, {})
    read_funcs = _READ_FUNCS.get(form_id, {})
    write_funcs = _WRITE_FUNCS.get(form_id, {})

    config = {
        "_TITLE": basic_info['title'],
        "_DESCRIPTION": basic_info['description'],
        "_FILER_ID_FIELD": basic_info['filer_id_field'],
        "_VALID_FIELDS_BY_YEAR": _get_year_list(valid_fields),
        "_READ_DICTS_BY_YEAR": _get_year_dict(read_dicts),
        "_READ_FUNCS_BY_YEAR": _get_year_list(read_funcs),
        "_WRITE_DICTS_BY_YEAR": _get_year_dict(write_dicts),
        "_WRITE_FUNCS_BY_YEAR": _get_year_list(write_funcs),
    }

    '''
    to_write = {
        'title': basic_info['title'],
        'description': basic_info['description'],
        'filer_id_field': basic_info['filer_id_field'],
        'valid_fields': valid_fields
    }

    read_dicts = _READ_DICTS.get(form_id)
    write_dicts = _WRITE_DICTS.get(form_id)
    if read_dicts:
        to_write['fields_to_rvars'] = read_dicts
    if write_dicts:
        to_write['rvars_to_fields'] = write_dicts

    write_json_to_file(
        to_write,
        os.path.join(_FILE_PATH, 'tmp', form_id + '.json'),
        indent=2,
        sort_keys=True
    )
    '''

    return type(name, (Form,), config)


US1040 = _define_us_form('US1040')
US1040SA = _define_us_form('US1040SA')
US1040SB = _define_us_form('US1040SB')
US1040SC = _define_us_form('US1040SC')
US1040SD = _define_us_form('US1040SD')
US1040SE = _define_us_form('US1040SE')
US1040SEIC = _define_us_form('US1040SEIC')
US1040SR = _define_us_form('US1040SR')
US1040SSE = _define_us_form('US1040SSE')
US2441 = _define_us_form('US2441')
US3800 = _define_us_form('US3800')
US4137 = _define_us_form('US4137')
US4255 = _define_us_form('US4255')
US4952 = _define_us_form('US4952')
US5695 = _define_us_form('US5695')
US6251 = _define_us_form('US6251')
US8801 = _define_us_form('US8801')
US8863 = _define_us_form('US8863')

US_FORMS = [
    US1040, US1040SA, US1040SB, US1040SC, US1040SD, US1040SE, US1040SEIC,
    US1040SR, US1040SSE, US2441, US3800, US4137, US4255, US4952, US5695,
    US6251, US8801, US8863
]

US_FORMS_BY_ID = {form.form_id(): form for form in US_FORMS}
