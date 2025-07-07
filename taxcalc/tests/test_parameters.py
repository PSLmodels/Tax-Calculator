"""
Tests for Tax-Calculator Parameters class and JSON parameter files.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_parameters.py
# pylint --disable=locally-disabled test_parameters.py

import copy
import os
import json
import math
import tempfile
import numpy as np
import pytest
import paramtools
from taxcalc.parameters import Parameters, is_paramtools_format
from taxcalc.policy import Policy
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff
from taxcalc.growfactors import GrowFactors


# Test specification and use of simple Parameters-derived class that has
# no vector parameters and has no (wage or price) indexed parameters.
# This derived class is called Params and it contains one of each of the
# four types of parameters.
#
# The following pytest fixture specifies the JSON DEFAULTS file for the
# Params class, which is defined in the test_params_class function.


PARAMS_JSON = json.dumps({
    "schema": {
        "labels": {
            "year": {
                "type": "int",
                "validators": {"range": {"min": 2001, "max": 2010}}
            },
            "label": {
                "type": "str",
                "validators": {"choice": {"choices": ["label1", "label2"]}}
            }
        },
        "operators": {
            "array_first": True,
            "label_to_extend": "year"
        }
    },
    "real_param": {
        "title": "Real (float) parameter",
        "description": "",
        "type": "float",
        "value": 0.5,
        "validators": {"range": {"min": 0, "max": 1}}
    },
    "int_param": {
        "title": "Integer parameter",
        "description": "",
        "type": "int",
        "value": 2,
        "validators": {"range": {"min": 0, "max": 9}}
    },
    "bool_param": {
        "title": "Boolean parameter",
        "description": "",
        "type": "bool",
        "value": True,
    },
    "str_param": {
        "title": "String parameter",
        "description": "",
        "type": "str",
        "value": "linear",
        "validators": {"choice": {"choices": ["linear", "nonlinear", "cubic"]}}
    },
    "label_param": {
        "title": "Parameter that uses labels.",
        "description": "",
        "type": "int",
        "value": [
            {"label": "label1", "year": 2001, "value": 2},
            {"label": "label2", "year": 2001, "value": 3}
        ],
        "validators": {"range": {"min": 0, "max": 9}}
    }
})


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
    ({"int_param": {2004: [3]}}, "raise"),
    ({"label_param": {2004: [1, 2]}}, "noerror"),
    ({"label_param": {2004: [[1, 2]]}}, "raise"),
    ({"label_param": {2004: [1, 2, 3]}}, "raise"),
    ({'bool_param': {2004: [4.9]}}, "raise"),
    ({'str_param': {2004: [9]}}, "raise"),
    ({'str_param': {2004: 'nonlinear'}}, "noerror"),
    ({'str_param': {2004: 'unknownvalue'}}, "error"),
    ({'str_param': {2004: ['nonlinear']}}, "raise"),
    ({'real_param': {2004: 'linear'}}, "raise"),
    ({'real_param': {2004: [0.2, 0.3]}}, "raise"),
    ({'removed_param': {2004: 0.1}}, "raise"),
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
        # pylint: disable=abstract-method

        DEFAULTS_FILE_NAME = params_json_file.name
        DEFAULTS_FILE_PATH = ''
        START_YEAR = 2001
        LAST_YEAR = 2010
        NUM_YEARS = LAST_YEAR - START_YEAR + 1
        REMOVED_PARAMS = {
            'removed_param': 'has been removed'
        }

        def __init__(self):
            super().__init__()
            self.initialize(Params.START_YEAR, Params.NUM_YEARS)

        def update_params(self, revision,
                          print_warnings=True, raise_errors=True):
            """
            Update parameters given specified revision dictionary.
            """
            self._update(revision, print_warnings, raise_errors)

        # intentionally do not define a set_rates(self) method

    # test Params class
    prms = Params()

    with pytest.raises(NotImplementedError):
        prms.set_rates()

    if revision == {}:
        assert isinstance(prms, Params)
        assert prms.start_year == 2001
        assert prms.current_year == 2001
        assert prms.end_year == 2010
        assert prms.inflation_rates() == []
        assert prms.wage_growth_rates() == []
        prms.set_year(2010)
        assert prms.current_year == 2010
        with pytest.raises(paramtools.ValidationError):
            prms.set_year(2011)
        return

    if expect == 'raise':
        with pytest.raises(paramtools.ValidationError):
            prms.update_params(revision)
    elif expect == 'noerror':
        prms.update_params(revision)
        assert not prms.errors
    elif expect == 'error':
        with pytest.raises(paramtools.ValidationError):
            prms.update_params(revision)
        assert prms.errors
    elif expect == 'warn':
        with pytest.raises(paramtools.ValidationError):
            prms.update_params(revision)
        assert prms.warnings


@pytest.mark.parametrize("fname",
                         [("consumption.json"),
                          ("policy_current_law.json"),
                          ("growdiff.json")])
def test_json_file_contents(tests_path, fname):
    """
    Check contents of JSON parameter files in Tax-Calculator/taxcalc directory.
    """
    # pylint: disable=too-many-locals,too-many-branches
    first_year = Policy.JSON_START_YEAR
    last_known_year = Policy.LAST_KNOWN_YEAR  # for indexed parameter values
    known_years = set(range(first_year, last_known_year + 1))
    # check elements in each parameter sub-dictionary
    failures = ''
    path = os.path.join(tests_path, "..", fname)
    with open(path, 'r', encoding='utf-8') as f:
        allparams = json.loads(f.read())
    for pname in allparams:
        if pname == "schema":
            continue
        # check that param contains required keys
        param = allparams[pname]
        # check that indexable and indexed are False in many files
        if fname != 'policy_current_law.json':
            assert param.get('indexable', False) is False
            assert param.get('indexed', False) is False
        # check that indexable is True when indexed is True
        if param.get('indexed', False) and not param.get('indexable', False):
            msg = (
                f'param:<{pname}>; '
                f'indexed={param.get("indexed", False)}; '
                f'indexable={param.get("indexable", False)}\n'
            )
            failures += msg
        # check that indexable param has value_type float
        if param.get('indexable', False) and param['type'] != 'float':
            msg = (
                f'param:<{pname}>; '
                f'type={param["type"]}; '
                f'indexable={param.get("indexable", False)}\n'
            )
            failures += msg
        # ensure that indexable is False when value_type is not real
        if param.get('indexable', False) and param['type'] != 'float':
            msg = (
                f'param:<{pname}>; '
                f'indexable={param.get("indexable", False)}; '
                f'type={param["value_type"]}\n'
            )
            failures += msg
    o = None
    if fname == "consumption.json":
        o = Consumption()
    elif fname == "policy_current_law.json":
        o = Policy()
    elif fname == "growdiff.json":
        o = GrowDiff()
    param_list = []
    for k in o:
        if k[0].isupper():  # find parameters by case of first letter
            param_list.append(k)
    for param in param_list:
        for y in known_years:
            o.set_year(y)
            if np.isnan(getattr(o, param)).any():
                msg = f'param:<{param}>; not found in year={y}\n'
                failures += msg
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
    with open(path, 'r', encoding='utf-8') as pfile:
        allparams = json.load(pfile)
    assert isinstance(allparams, dict)
    # read PYTHON code file text
    # pylint: disable=consider-using-join
    if pfname == 'consumption.py':
        # consumption.py does not explicitly name the parameters
        code_text = ''
        for var in Consumption.RESPONSE_VARS:
            code_text += f'MPC_{var}\n'
        for var in Consumption.BENEFIT_VARS:
            code_text += f'BEN_{var}_value\n'
    elif pfname == 'growdiff.py':
        # growdiff.py does not explicitly name the parameters
        code_text = ''
        for var in GrowFactors.VALID_NAMES:
            code_text += f'{var}\n'
    else:
        # parameters are explicitly named in PYTHON file
        path = os.path.join(tests_path, '..', pfname)
        with open(path, 'r', encoding='utf-8') as pfile:
            code_text = pfile.read()
    # check that each param (without leading _) is mentioned in code text
    for pname in allparams:
        if pname == "schema":
            continue
        assert pname[1:] in code_text


# following tests access private methods, so pylint: disable=protected-access


class ArrayParams(Parameters):
    """ArrayParams class"""
    defaults = {
        "schema": {
            "labels": {
                "year": {
                    "type": "int",
                    "validators": {"range": {"min": 2013, "max": 2028}}
                },
                "MARS": {
                    "type": "str",
                    "validators": {
                        "choice": {
                            "choices": [
                                "single",
                                "joint",
                                "mseparate",
                                "headhh",
                                "widow",
                                # test value of II_brk2 has 6 columns
                                "extra",
                            ]
                        }
                    }
                },
                "EIC": {
                    "type": "str",
                    "validators": {
                        "choice": {
                            "choices": [
                                "0kids",
                                "1kid",
                                "2kids",
                                "3+kids"
                            ]
                        }
                    }
                }
            },
            "additional_members": {
                "indexable": {
                    "type": "bool"
                },
                "indexed": {
                    "type": "bool"
                },
            },
            "operators": {
                "array_first": True,
                "label_to_extend": "year"
            }
        },
        "one_dim": {
            "title": "One dimensional parameter",
            "description": "",
            "type": "float",
            "indexed": True,
            "indexable": True,
            "value": [{"year": 2013, "value": 5}]
        },
        "EITC_c": {
            "title": "Two dimensional parameter",
            "description": "",
            "type": "float",
            "indexed": True,
            "indexable": True,
            "value": [
                {"year": 2013, "EIC": "0kids", "value": 1},
                {"year": 2013, "EIC": "1kid", "value": 2},
                {"year": 2013, "EIC": "2kids", "value": 3},
                {"year": 2013, "EIC": "3+kids", "value": 4}
            ]
        },
        "II_brk2": {
            "title": "II_brk2",
            "description": "",
            "type": "float",
            "indexed": True,
            "indexable": True,
            "value": [
                {"year": 2013, "MARS": "single", "value": 1},
                {"year": 2013, "MARS": "joint", "value": 2},
                {"year": 2013, "MARS": "mseparate", "value": 3},
                {"year": 2013, "MARS": "headhh", "value": 2},
                {"year": 2013, "MARS": "widow", "value": 3},
                {"year": 2013, "MARS": "extra", "value": 3},
            ]
        }
    }

    # These will be controlled directly through the extend method.
    label_to_extend = None
    array_first = False

    START_YEAR = 2013
    LAST_YEAR = 2035
    NUM_YEARS = LAST_YEAR - START_YEAR + 1

    def __init__(self, **kwargs):
        super().__init__(
            ArrayParams.START_YEAR,
            ArrayParams.NUM_YEARS,
            **kwargs
        )
        self._gfactors = GrowFactors()
        self._inflation_rates = [0.02] * self.num_years
        self._wage_growth_rates = [0.03] * self.num_years

    def update_params(self, revision,
                      print_warnings=True, raise_errors=True):
        """
        Update parameters given specified revision dictionary.
        """
        self._update(revision, print_warnings, raise_errors)

    def set_rates(self):
        """Method docstring"""


def test_expand_xd_errors():
    """
    One of several _expand_?D tests.
    """
    params = ArrayParams(label_to_extend=None, array_first=False)
    with pytest.raises(paramtools.ValidationError):
        params.extend(label="year", label_values=[1, 2, 3])


def test_expand_empty():
    """Test docstring"""
    params = ArrayParams(label_to_extend=None, array_first=False)
    params.sort_values()
    one_dim = copy.deepcopy(params.one_dim)

    params.extend(label="year", label_values=[])

    params.sort_values()
    assert params.one_dim == one_dim


def test_expand_1d_scalar():
    """Test docstring"""
    yrs = 12
    val = 10.0
    exp = np.array([val * math.pow(1.02, i) for i in range(0, yrs)])

    yrslist = list(range(2013, 2013 + 12))
    params = ArrayParams(label_to_extend=None, array_first=False)
    params.adjust({"one_dim": val})
    params.extend(params=["one_dim"], label="year", label_values=yrslist)
    res = params.to_array("one_dim", year=yrslist)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)

    params = ArrayParams(label_to_extend=None, array_first=False)
    params.adjust({"one_dim": val})
    params.extend(params=["one_dim"], label="year", label_values=[2013])
    res = params.to_array("one_dim", year=2013)
    assert np.allclose(np.array([val]), res, atol=0.01, rtol=0.0)


def test_expand_2d_short_array():
    """
    One of several _expand_?D tests.
    """
    val = np.array([1., 2., 3., 4.])
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1., 2., 3., 4.])
    exp = np.zeros((5, 4))
    exp[:1] = exp1
    exp[1:] = exp2

    params = ArrayParams(array_first=False, label_to_extend=None)
    years = [2013, 2014, 2015, 2016, 2017]
    params.extend(
        params=["EITC_c"],
        label="year",
        label_values=years,
    )
    res = params.to_array("EITC_c", year=years)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)


def test_expand_2d_variable_rates():
    """
    One of several _expand_?D tests.
    """
    ary = np.array([[1., 2., 3., 4.]])
    cur = np.array([1., 2., 3., 4.])
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]
    exp2 = []
    for i in range(0, 4):
        idx = i + len(ary) - 1
        cur = np.array(cur * (1.0 + irates[idx]))
        print('cur is ', cur)
        exp2.append(cur)
    exp1 = np.array([1., 2., 3., 4.])
    exp = np.zeros((5, 4))
    exp[:1] = exp1
    exp[1:] = exp2

    params = ArrayParams(array_first=False, label_to_extend=None)
    params._inflation_rates = irates
    years = [2013, 2014, 2015, 2016, 2017]
    params.extend(params=["EITC_c"], label="year", label_values=years)
    res = params.to_array("EITC_c", year=years)
    assert np.allclose(exp, res, atol=0.01, rtol=0.0)


def test_expand_2d_already_filled():
    """
    One of several _expand_?D tests.
    """
    ii_brk2 = [[36000., 72250., 36500., 48600., 72500., 36250.],
               [38000., 74000., 36900., 49400., 73800., 36900.],
               [40000., 74900., 37450., 50200., 74900., 37450.]]

    years = [2013, 2014, 2015]
    params = ArrayParams(
        array_first=False,
        label_to_extend=None,
    )
    params.adjust({
        "II_brk2": params.from_array("II_brk2", np.array(ii_brk2), year=years)
    })

    params.extend(
        params=["II_brk2"], label="year", label_values=years
    )
    res = params.to_array("II_brk2", year=years)
    assert np.allclose(res, np.array(ii_brk2), atol=0.01, rtol=0.0)


def test_expand_2d_partial_expand():
    """
    One of several _expand_?D tests.
    """
    ii_brk2 = [
        [36000.0, 72250.0, 36500.0, 48600.0, 72500.0, 36250.0],
        [38000.0, 74000.0, 36900.0, 49400.0, 73800.0, 36900.0],
        [40000.0, 74900.0, 37450.0, 50200.0, 74900.0, 37450.0],
    ]
    # We have three years worth of data, need 4 years worth,
    # but we only need the inflation rate for year 3 to go
    # from year 3 to year 4
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

    years = [2013, 2014, 2015]
    params = ArrayParams(array_first=False, label_to_extend=None)
    params.adjust({
        "II_brk2": params.from_array("II_brk2", np.array(ii_brk2), year=years)
    })
    params._inflation_rates[:3] = inf_rates
    params.extend(
        params=["II_brk2"], label="year", label_values=years + [2016]
    )
    res = params.to_array("II_brk2", year=years + [2016])
    assert np.allclose(res, exp, atol=0.01, rtol=0.0)


TAXCALC_REVISION = """
{
    "consumption": {"BEN_mcaid_value": {"2013": 0.9}}
}
"""

PARAMTOOLS_REVISION = """
{
    "consumption": {"BEN_mcaid_value": [{"year": "2013", "value": 0.9}]}
}
"""

PARAMTOOLS_REVISION2 = """
{
    "consumption": {"BEN_mcaid_value": 0.9}
}
"""


@pytest.mark.parametrize("good_revision", [
    TAXCALC_REVISION,
    PARAMTOOLS_REVISION,
])
def test_read_json_revision(good_revision):
    """
    Check _read_json_revision logic.
    """
    # pllint: disable=private-method
    with pytest.raises(TypeError):
        # error because first obj argument is neither None nor a string
        Parameters._read_json_revision([], '')
    with pytest.raises(ValueError):
        # error because second topkey argument must be a string
        Parameters._read_json_revision(good_revision, 999)
    with pytest.raises(ValueError):
        # error because second topkey argument is not in good_revision
        Parameters._read_json_revision(good_revision, 'unknown_topkey')


@pytest.mark.parametrize("params,is_paramtools", [
    (TAXCALC_REVISION, False),
    (PARAMTOOLS_REVISION, True),
    (PARAMTOOLS_REVISION2, True),
])
def test_read_json_revision_foramts(params, is_paramtools):
    """
    Check _read_json_revision for ParamTools and Tax-Calculator
    styled parameters.
    """
    result = Parameters._read_json_revision(params, "consumption")
    assert is_paramtools_format(result) is is_paramtools
    if is_paramtools:
        assert result == json.loads(params)["consumption"]
