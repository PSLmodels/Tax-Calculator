"""
Tests for Tax-Calculator Parameters class and JSON parameter files.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_parameters.py
# pylint --disable=locally-disabled test_parameters.py

import os
import json
import math
import tempfile
import numpy as np
import pytest
# pylint: disable=import-error
from taxcalc import Parameters, Policy, Consumption


def test_instantiation_and_usage():
    """
    Test Parameters instantiation and usage.
    """
    pbase = Parameters()
    assert isinstance(pbase, Parameters)
    assert pbase.inflation_rates() is None
    assert pbase.wage_growth_rates() is None
    syr = 2010
    nyrs = 10
    pbase.initialize(start_year=syr, num_years=nyrs)
    with pytest.raises(ValueError):
        pbase.set_default_vals(known_years=list())
    # pylint: disable=protected-access
    with pytest.raises(ValueError):
        pbase.set_year(syr - 1)
    with pytest.raises(NotImplementedError):
        pbase._params_dict_from_json_file()
    with pytest.raises(ValueError):
        pbase._update([])
    with pytest.raises(ValueError):
        pbase._update({})
    with pytest.raises(ValueError):
        pbase._update({(syr + nyrs): {}})
    with pytest.raises(ValueError):
        pbase._update({syr: []})
    # pylint: disable=no-member
    with pytest.raises(ValueError):
        Parameters._expand_array({}, 'real', True, [0.02], 1)
    arr3d = np.array([[[1, 1]], [[1, 1]], [[1, 1]]])
    with pytest.raises(AssertionError):
        Parameters._expand_array(arr3d, 'real', True, [0.02], 1)


@pytest.mark.parametrize("fname",
                         [("consumption.json"),
                          ("policy_current_law.json"),
                          ("growdiff.json")])
def test_json_file_contents(tests_path, fname):
    """
    Check contents of JSON parameter files.
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    # specify test information
    required_keys = ['long_name', 'description',
                     'section_1', 'section_2', 'notes',
                     'row_var', 'row_label',
                     'start_year', 'cpi_inflated', 'cpi_inflatable',
                     'col_var', 'col_label',
                     'value_type', 'value', 'valid_values']
    valid_value_types = ['boolean', 'integer', 'real', 'string']
    invalid_keys = ['invalid_minmsg', 'invalid_maxmsg', 'invalid_action']
    first_year = Policy.JSON_START_YEAR
    last_known_year = Policy.LAST_KNOWN_YEAR  # for indexed parameter values
    num_known_years = last_known_year - first_year + 1
    long_params = ['_II_brk1', '_II_brk2', '_II_brk3', '_II_brk4',
                   '_II_brk5', '_II_brk6', '_II_brk7',
                   '_PT_brk1', '_PT_brk2', '_PT_brk3', '_PT_brk4',
                   '_PT_brk5', '_PT_brk6', '_PT_brk7',
                   '_PT_excl_wagelim_thd',
                   '_ALD_BusinessLosses_c',
                   '_STD', '_II_em',
                   '_AMT_em', '_AMT_em_ps', '_AMT_em_pe',
                   '_ID_ps', '_ID_AllTaxes_c']
    long_known_years = 2026 - first_year + 1  # for TCJA-reverting long_params
    # read JSON parameter file into a dictionary
    path = os.path.join(tests_path, '..', fname)
    pfile = open(path, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)
    # check elements in each parameter sub-dictionary
    failures = ''
    for pname in allparams:
        # all parameter names should be strings
        assert isinstance(pname, str)
        # check that param contains required keys
        param = allparams[pname]
        assert isinstance(param, dict)
        for key in required_keys:
            assert key in param
        if param['value_type'] == 'string':
            for key in invalid_keys:
                assert key not in param
            assert isinstance(param['valid_values']['options'], list)
        else:
            for key in invalid_keys:
                assert key in param
            assert param['invalid_action'] in ['stop', 'warn']
        # check for non-empty long_name and description strings
        assert isinstance(param['long_name'], str)
        if not param['long_name']:
            assert '{} long_name'.format(pname) == 'empty string'
        assert isinstance(param['description'], str)
        if not param['description']:
            assert '{} description'.format(pname) == 'empty string'
        # check that row_var is FLPDYR
        assert param['row_var'] == 'FLPDYR'
        # check that start_year equals first_year
        syr = param['start_year']
        assert isinstance(syr, int) and syr == first_year
        # check that cpi_inflatable and cpi_inflated are boolean
        assert isinstance(param['cpi_inflatable'], bool)
        assert isinstance(param['cpi_inflated'], bool)
        # check that cpi_inflatable and cpi_inflated are False in many files
        if fname != 'policy_current_law.json':
            assert param['cpi_inflatable'] is False
            assert param['cpi_inflated'] is False
        # check that cpi_inflatable is True when cpi_inflated is True
        if param['cpi_inflated'] and not param['cpi_inflatable']:
            msg = 'param:<{}>; cpi_inflated={}; cpi_inflatable={}'
            fail = msg.format(pname, param['cpi_inflated'],
                              param['cpi_inflatable'])
            failures += fail + '\n'
        # check that value_type is correct string
        if not param['value_type'] in valid_value_types:
            msg = 'param:<{}>; value_type={}'
            fail = msg.format(pname, param['value_type'])
            failures += fail + '\n'
        # check that cpi_inflatable param has value_type real
        if param['cpi_inflatable'] and param['value_type'] != 'real':
            msg = 'param:<{}>; value_type={}; cpi_inflatable={}'
            fail = msg.format(pname, param['value_type'],
                              param['cpi_inflatable'])
            failures += fail + '\n'
        # ensure that cpi_inflatable is False when value_type is not real
        if param['cpi_inflatable'] and param['value_type'] != 'real':
            msg = 'param:<{}>; cpi_inflatable={}; value_type={}'
            fail = msg.format(pname, param['cpi_inflatable'],
                              param['value_type'])
            failures += fail + '\n'
        # check that row_label is list
        rowlabel = param['row_label']
        assert isinstance(rowlabel, list)
        # check all row_label values
        cyr = first_year
        for rlabel in rowlabel:
            assert int(rlabel) == cyr
            cyr += 1
        # check type and dimension of value
        value = param['value']
        assert isinstance(value, list)
        assert len(value) == len(rowlabel)
        # check that col_var and col_label are consistent
        cvar = param['col_var']
        assert isinstance(cvar, str)
        clab = param['col_label']
        if cvar == '':
            assert isinstance(clab, str) and clab == ''
        else:
            assert isinstance(clab, list)
            # check different possible col_var values
            if cvar == 'MARS':
                assert len(clab) == 5
            elif cvar == 'EIC':
                assert len(clab) == 4
            elif cvar == 'idedtype':
                assert len(clab) == 7
            elif cvar == 'c00100':
                pass
            else:
                assert cvar == 'UNKNOWN col_var VALUE'
            # check length of each value row
            for valuerow in value:
                assert len(valuerow) == len(clab)
        # check that indexed parameters have all known years in rowlabel list
        # form_parameters are those whose value is available only on IRS form
        form_parameters = []
        if param['cpi_inflated']:
            error = False
            known_years = num_known_years
            if pname in long_params:
                known_years = long_known_years
            if pname in form_parameters:
                if len(rowlabel) != (known_years - 1):
                    error = True
            else:
                if len(rowlabel) != known_years:
                    error = True
            if error:
                msg = 'param:<{}>; len(rowlabel)={}; known_years={}'
                fail = msg.format(pname, len(rowlabel), known_years)
                failures += fail + '\n'
    if failures:
        raise ValueError(failures)


@pytest.mark.parametrize("jfname, pfname",
                         [("consumption.json", "consumption.py"),
                          ("policy_current_law.json", "calcfunctions.py"),
                          ("growdiff.json", "growdiff.py")])
def test_parameters_mentioned(tests_path, jfname, pfname):
    """
    Make sure each JSON parameter is mentioned in PYTHON code file.
    """
    # read JSON parameter file into a dictionary
    path = os.path.join(tests_path, '..', jfname)
    pfile = open(path, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)
    # read PYTHON code file text
    if pfname == 'consumption.py':
        # consumption.py does not explicitly name the parameters
        code_text = ''
        for var in Consumption.RESPONSE_VARS:
            code_text += 'MPC_{}\n'.format(var)
        for var in Consumption.BENEFIT_VARS:
            code_text += 'BEN_{}_value\n'.format(var)
    else:
        # parameters are explicitly named in PYTHON file
        path = os.path.join(tests_path, '..', pfname)
        pfile = open(path, 'r')
        code_text = pfile.read()
        pfile.close()
    # check that each param (without leading _) is mentioned in code text
    for pname in allparams:
        assert pname[1:] in code_text


# following tests access private methods, so pylint: disable=protected-access


def test_expand_xd_errors():
    """
    One of several _expand_?D tests.
    """
    dct = dict()
    with pytest.raises(ValueError):
        Parameters._expand_1d(dct, inflate=False, inflation_rates=[],
                              num_years=10)
    with pytest.raises(ValueError):
        Parameters._expand_2d(dct, inflate=False, inflation_rates=[],
                              num_years=10)


def test_expand_1d_scalar():
    """
    One of several _expand_?D tests.
    """
    yrs = 12
    val = 10.0
    exp = np.array([val * math.pow(1.02, i) for i in range(0, yrs)])
    res = Parameters._expand_1d(np.array([val]),
                                inflate=True, inflation_rates=[0.02] * yrs,
                                num_years=yrs)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)
    res = Parameters._expand_1d(np.array([val]),
                                inflate=True, inflation_rates=[0.02] * yrs,
                                num_years=1)
    assert np.allclose(np.array([val]), res, atol=0.01, rtol=0.0)


def test_expand_2d_short_array():
    """
    One of several _expand_?D tests.
    """
    ary = np.array([[1., 2., 3.]])
    val = np.array([1., 2., 3.])
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1., 2., 3.])
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = Parameters._expand_2d(ary, inflate=True,
                                inflation_rates=[0.02] * 5, num_years=5)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)


def test_expand_2d_variable_rates():
    """
    One of several _expand_?D tests.
    """
    ary = np.array([[1., 2., 3.]])
    cur = np.array([1., 2., 3.])
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]
    exp2 = []
    for i in range(0, 4):
        idx = i + len(ary) - 1
        cur = np.array(cur * (1.0 + irates[idx]))
        print('cur is ', cur)
        exp2.append(cur)
    exp1 = np.array([1., 2., 3.])
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = Parameters._expand_2d(ary, inflate=True,
                                inflation_rates=irates, num_years=5)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)


def test_expand_2d_already_filled():
    """
    One of several _expand_?D tests.
    """
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
    _II_brk2 = [[36000., 72250., 36500., 48600., 72500., 36250.],
                [38000., 74000., 36900., 49400., 73800., 36900.],
                [40000., 74900., 37450., 50200., 74900., 37450.]]
    res = Parameters._expand_2d(np.array(_II_brk2),
                                inflate=True, inflation_rates=[0.02] * 5,
                                num_years=3)
    np.allclose(res, np.array(_II_brk2), atol=0.01, rtol=0.0)


def test_expand_2d_partial_expand():
    """
    One of several _expand_?D tests.
    """
    # pylint doesn't like caps in var name, so  pylint: disable=invalid-name
    _II_brk2 = [[36000.0, 72250.0, 36500.0, 48600.0, 72500.0, 36250.0],
                [38000.0, 74000.0, 36900.0, 49400.0, 73800.0, 36900.0],
                [40000.0, 74900.0, 37450.0, 50200.0, 74900.0, 37450.0]]
    # We have three years worth of data, need 4 years worth,
    # but we only need the inflation rate for year 3 to go
    # from year 3 -> year 4
    inf_rates = [0.02, 0.02, 0.03]
    exp1 = 40000. * 1.03
    exp2 = 74900. * 1.03
    exp3 = 37450. * 1.03
    exp4 = 50200. * 1.03
    exp5 = 74900. * 1.03
    exp6 = 37450. * 1.03
    exp = [[36000.0, 72250.0, 36500.0, 48600.0, 72500.0, 36250.0],
           [38000.0, 74000.0, 36900.0, 49400.0, 73800.0, 36900.0],
           [40000.0, 74900.0, 37450.0, 50200.0, 74900.0, 37450.0],
           [exp1, exp2, exp3, exp4, exp5, exp6]]
    res = Parameters._expand_2d(np.array(_II_brk2),
                                inflate=True, inflation_rates=inf_rates,
                                num_years=4)
    assert np.allclose(res, exp, atol=0.01, rtol=0.0)


@pytest.mark.parametrize('json_filename',
                         ['policy_current_law.json',
                          'consumption.json',
                          'growdiff.json'])
def test_bool_int_value_info(tests_path, json_filename):
    """
    Check consistency of boolean and integer info in JSON parameter files.
    """
    path = os.path.join(tests_path, '..', json_filename)
    with open(path, 'r') as pfile:
        pdict = json.load(pfile)
    maxint = np.iinfo(np.int16).max
    for param in sorted(pdict.keys()):
        # find param type based on value
        val = pdict[param]['value']
        while isinstance(val, list):
            val = val[0]
        valstr = str(val)
        val_is_boolean = valstr in ('True', 'False')
        val_is_integer = (not bool('.' in valstr or abs(val) > maxint) and
                          not val_is_boolean)
        # check that val_is_integer is consistent with integer type
        integer_type = pdict[param]['value_type'] == 'integer'
        if val_is_integer != integer_type:
            msg = 'param,value_type,valstr= {} {} {}'
            msg = msg.format(str(param),
                             pdict[param]['value_type'],
                             valstr)
            assert msg == 'ERROR: integer_value param has non-integer value'
        # check that val_is_boolean is consistent with boolean_value
        boolean_type = pdict[param]['value_type'] == 'boolean'
        if val_is_boolean != boolean_type:
            msg = 'param,value_type,valstr= {} {} {}'
            msg = msg.format(str(param),
                             pdict[param]['value_type'],
                             valstr)
            assert msg == 'ERROR: boolean_value param has non-boolean value'


def test_param_dict_for_year():
    """
    Check logic of param_dict_for_year staticmethod.
    """
    param_info = {
        'pname1': {
            'default_value': 0.0,
            'minimum_value': 0.0,
            'maximum_value': 9e99
        },
        'pname2': {
            'default_value': 0.0,
            'minimum_value': -9e99,
            'maximum_value': 0.0
        }
    }
    param_dict = {
        2019: {'pname1': 0.05},
        2021: {'pname2': -0.5},
        2023: {'pname2': 0.5}
    }
    ydict = Parameters.param_dict_for_year(2018, param_dict, param_info)
    assert ydict['pname1'] == 0.0
    assert ydict['pname2'] == 0.0
    ydict = Parameters.param_dict_for_year(2020, param_dict, param_info)
    assert ydict['pname1'] == 0.05
    assert ydict['pname2'] == 0.0
    ydict = Parameters.param_dict_for_year(2022, param_dict, param_info)
    assert ydict['pname1'] == 0.05
    assert ydict['pname2'] == -0.5
    with pytest.raises(AssertionError):
        Parameters.param_dict_for_year(2024, param_dict, param_info)


@pytest.fixture(scope='module', name='defaults_json_file')
def fixture_defaultsjsonfile():
    """
    Define alternative JSON assumption parameter defaults file.
    """
    json_text = """
{
"_param2": {
    "value_type": "integer",
    "value": [2, 2, 2],
    "valid_values": {"min": 0, "max": 9},
    "invalid_minmsg": "",
    "invalid_maxmsg": "",
    "invalid_action": "stop"
},
"_param3": {
    "value_type": "boolean",
    "value": [true, true, true],
    "valid_values": {"min": false, "max": true},
    "invalid_minmsg": "",
    "invalid_maxmsg": "",
    "invalid_action": "stop"
},
"_param4": {
    "value_type": "string",
    "value": ["linear", "linear", "linear"],
    "valid_values": {"options": ["linear", "nonlinear", "cubic"]}
}
}
"""
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as pfile:
        pfile.write(json_text + '\n')
    pfile.close()
    yield pfile
    os.remove(pfile.name)


def test_alternative_defaults_file(defaults_json_file):
    """
    Test Parameter._validate_values method using
    alternative Parameters.DEFAULTS_FILE_NAME.
    """
    # pylint: disable=too-many-statements
    class Params(Parameters):
        """
        Params is a subclass of the Parameter class.
        """
        DEFAULTS_FILE_NAME = defaults_json_file.name
        DEFAULTS_FILE_PATH = ''
        JSON_START_YEAR = Policy.JSON_START_YEAR
        LAST_KNOWN_YEAR = Policy.LAST_KNOWN_YEAR
        LAST_BUDGET_YEAR = Policy.LAST_BUDGET_YEAR
        DEFAULT_NUM_YEARS = LAST_BUDGET_YEAR - JSON_START_YEAR + 1

        def __init__(self):
            super().__init__()
            # read default parameters and initialize
            self._vals = self._params_dict_from_json_file()
            self.initialize(Params.JSON_START_YEAR, Params.DEFAULT_NUM_YEARS)
            # specify no parameter indexing rates
            self._inflation_rates = None
            self._wage_growth_rates = None
            # specify warning/error handling variables
            self.parameter_warnings = ''
            self.parameter_errors = ''
            self._ignore_errors = False
        # end of Params class definition

    prms = Params()
    assert isinstance(prms, Params)
    assert prms.start_year == 2013
    assert prms.current_year == 2013
    paramsreform = {2014: {'_param4': [9]}}
    prms._validate_names_types(paramsreform)
    assert prms.parameter_errors
    del prms
    del paramsreform
    prms = Params()
    paramsreform = {2014: {'_param2': [3.6]}}
    prms._validate_names_types(paramsreform)
    assert prms.parameter_errors
    del prms
    del paramsreform
    prms = Params()
    paramsreform = {2014: {'_param3': [3.6]}}
    prms._validate_names_types(paramsreform)
    assert prms.parameter_errors
