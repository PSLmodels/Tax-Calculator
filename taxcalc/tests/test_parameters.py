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
from taxcalc import Parameters, Policy, Consumption, GrowFactors


# Test specification and use of simple Parameters-derived class that has
# no vector parameters and has no (wage or price) indexed parameters.
# This derived class is called Params and it contains one of each of the
# four types of parameters.
#
# The following pytest fixture specifies the JSON DEFAULTS file for the
# Params class, which is defined in the test_params_class function.


PARAMS_JSON = """
{
"real_param": {
    "value_type": "real",
    "value_yrs": [2001, 2002, 2003],
    "value": [0.5, 0.5, 0.5],
    "valid_values": {"min": 0, "max": 1}
},
"int_param": {
    "value_type": "integer",
    "value_yrs": [2001, 2002, 2003],
    "value": [2, 2, 2],
    "valid_values": {"min": 0, "max": 9}
},
"bool_param": {
    "value_type": "boolean",
    "value_yrs": [2001, 2002, 2003],
    "value": [true, true, true],
    "valid_values": {"min": false, "max": true}
},
"str_param": {
    "value_type": "string",
    "value_yrs": [2001, 2002, 2003],
    "value": ["linear", "linear", "linear"],
    "valid_values": {"options": ["linear", "nonlinear", "cubic"]}
}
}
"""


@pytest.fixture(scope='module', name='params_json_file')
def fixture_params_json_file():
    """
    Define JSON DEFAULTS file for Parameters-derived Params class.
    """
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as pfile:
        pfile.write(PARAMS_JSON + '\n')
    pfile.close()
    yield pfile
    os.remove(pfile.name)


@pytest.mark.parametrize("revision, expect", [
    ({}, ""),
    ({'real_param': {2004: 1.9}}, "error"),
    ({'int_param': {2004: [3.6]}}, "raise"),
    ({'bool_param': {2004: [4.9]}}, "raise"),
    ({'str_param': {2004: [9]}}, "raise"),
    ({'str_param': {2004: 'nonlinear'}}, "noerror"),
    ({'str_param': {2004: 'unknownvalue'}}, "error"),
    ({'str_param': {2004: ['nonlinear']}}, "raise"),
    ({'real_param': {2004: 'linear'}}, "raise"),
    ({'real_param-indexed': {2004: True}}, "raise"),
    ({'unknown_param-indexed': {2004: False}}, "raise")
])
def test_params_class(revision, expect, params_json_file):
    """
    Specifies Params class and tests it.
    """

    class Params(Parameters):
        """
        The Params class is derived from the abstract base Parameter class.
        """
        DEFAULTS_FILE_NAME = params_json_file.name
        DEFAULTS_FILE_PATH = ''
        START_YEAR = 2001
        LAST_YEAR = 2010
        NUM_YEARS = LAST_YEAR - START_YEAR + 1

        def __init__(self):
            super().__init__()
            self.initialize(Params.START_YEAR, Params.NUM_YEARS)

        def update_params(self, revision,
                          print_warnings=True, raise_errors=True):
            """
            Update parameters given specified revision dictionary.
            """
            self._update(revision, print_warnings, raise_errors)

    # test Params class
    prms = Params()
    if revision == {}:
        assert isinstance(prms, Params)
        assert prms.start_year == 2001
        assert prms.current_year == 2001
        assert prms.end_year == 2010
        assert prms.inflation_rates() == list()
        assert prms.wage_growth_rates() == list()
        prms.set_year(2010)
        assert prms.current_year == 2010
        with pytest.raises(ValueError):
            prms.set_year(2011)
        return
    if expect == 'raise':
        with pytest.raises(ValueError):
            prms.update_params(revision,
                               print_warnings=False,
                               raise_errors=False)
    elif expect == 'noerror':
        prms.update_params(revision, print_warnings=False, raise_errors=False)
        assert not prms.parameter_errors
    elif expect == 'error':
        prms.update_params(revision, print_warnings=False, raise_errors=False)
        assert prms.parameter_errors
    elif expect == 'warn':
        prms.update_params(revision, print_warnings=False, raise_errors=False)
        assert prms.parameter_warnings


@pytest.mark.parametrize("fname",
                         [("consumption.json"),
                          ("policy_current_law.json"),
                          ("growdiff.json")])
def test_json_file_contents(tests_path, fname):
    """
    Check contents of JSON parameter files in Tax-Calculator/taxcalc directory.
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    # specify test information
    required_keys = ['long_name', 'description',
                     'value_type', 'value_yrs', 'value', 'valid_values']
    valid_value_types = ['boolean', 'integer', 'real', 'string']
    if fname == 'policy_current_law.json':
        invalid_keys = ['invalid_minmsg', 'invalid_maxmsg', 'invalid_action']
    else:
        invalid_keys = []
    first_year = Policy.JSON_START_YEAR
    last_known_year = Policy.LAST_KNOWN_YEAR  # for indexed parameter values
    num_known_years = last_known_year - first_year + 1
    long_params = ['II_brk1', 'II_brk2', 'II_brk3', 'II_brk4',
                   'II_brk5', 'II_brk6', 'II_brk7',
                   'PT_brk1', 'PT_brk2', 'PT_brk3', 'PT_brk4',
                   'PT_brk5', 'PT_brk6', 'PT_brk7',
                   'PT_qbid_taxinc_thd',
                   'ALD_BusinessLosses_c',
                   'STD', 'II_em', 'II_em_ps',
                   'AMT_em', 'AMT_em_ps', 'AMT_em_pe',
                   'ID_ps', 'ID_AllTaxes_c']
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
            assert param.get('invalid_action', 'stop') in ['stop', 'warn']
        # check for non-empty long_name and description strings
        assert isinstance(param['long_name'], str)
        if not param['long_name']:
            assert '{} long_name'.format(pname) == 'empty string'
        assert isinstance(param['description'], str)
        if not param['description']:
            assert '{} description'.format(pname) == 'empty string'
        # check that indexable and indexed are boolean
        assert isinstance(param.get('indexable', False), bool)
        assert isinstance(param.get('indexed', False), bool)
        # check that indexable and indexed are False in many files
        if fname != 'policy_current_law.json':
            assert param.get('indexable', False) is False
            assert param.get('indexed', False) is False
        # check that indexable is True when indexed is True
        if param.get('indexed', False) and not param.get('indexable', False):
            msg = 'param:<{}>; indexed={}; indexable={}'
            fail = msg.format(pname,
                              param.get('indexed', False),
                              param.get('indexable', False))
            failures += fail + '\n'
        # check that value_type is correct string
        if not param['value_type'] in valid_value_types:
            msg = 'param:<{}>; value_type={}'
            fail = msg.format(pname, param['value_type'])
            failures += fail + '\n'
        # check that indexable param has value_type real
        if param.get('indexable', False) and param['value_type'] != 'real':
            msg = 'param:<{}>; value_type={}; indexable={}'
            fail = msg.format(pname, param['value_type'],
                              param.get('indexable', False))
            failures += fail + '\n'
        # ensure that indexable is False when value_type is not real
        if param.get('indexable', False) and param['value_type'] != 'real':
            msg = 'param:<{}>; indexable={}; value_type={}'
            fail = msg.format(pname,
                              param.get('indexable', False),
                              param['value_type'])
            failures += fail + '\n'
        # check that value_yrs is list
        valueyrs = param['value_yrs']
        assert isinstance(valueyrs, list)
        # check all value_yrs values
        cyr = first_year
        for vyr in valueyrs:
            assert vyr == cyr
            cyr += 1
        # check type and dimension of value
        value = param['value']
        assert isinstance(value, list)
        assert len(value) == len(valueyrs)
        # check that vi_name and vi_vals are consistent
        viname = param.get('vi_name', '')
        assert isinstance(viname, str)
        vivals = param.get('vi_vals', [])
        if viname == '':
            assert vivals == []
        else:
            assert isinstance(vivals, list)
            # check different possible vi_name values
            if viname == 'MARS':
                assert len(vivals) == 5
            elif viname == 'EIC':
                assert len(vivals) == 4
            elif viname == 'idedtype':
                assert len(vivals) == 7
            elif viname == 'c00100':
                pass
            else:
                assert viname == 'UNKNOWN vi_name VALUE'
            # check length of each value row
            for valuerow in value:
                assert len(valuerow) == len(vivals)
        # check that indexed parameters have all known years in value_yrs list
        # (form_parameters are those whose value is available only on IRS form)
        form_parameters = []
        if param.get('indexed', False):
            error = False
            known_years = num_known_years
            if pname in long_params:
                known_years = long_known_years
            if pname in form_parameters:
                if len(valueyrs) != (known_years - 1):
                    error = True
            else:
                if len(valueyrs) != known_years:
                    error = True
            if error:
                msg = 'param:<{}>; len(value_yrs)={}; known_years={}'
                fail = msg.format(pname, len(valueyrs), known_years)
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
    elif pfname == 'growdiff.py':
        # growdiff.py does not explicitly name the parameters
        code_text = ''
        for var in GrowFactors.VALID_NAMES:
            code_text += '{}\n'.format(var)
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


def test_read_json_revision():
    """
    Check _read_json_revision logic.
    """
    good_revision = """
    {
      "consumption": {"BEN_mcaid_value": {"2013": 0.9}}
    }
    """
    # pllint: disable=private-method
    with pytest.raises(ValueError):
        # error because first obj argument is neither None nor a string
        Parameters._read_json_revision(list(), '')
    with pytest.raises(ValueError):
        # error because second topkey argument must be a string
        Parameters._read_json_revision(good_revision, 999)
    with pytest.raises(ValueError):
        # error because second topkey argument is not in good_revision
        Parameters._read_json_revision(good_revision, 'unknown_topkey')
