"""
Tests for Tax-Calculator ParametersBase class and JSON parameter files.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_parameters.py
# pylint --disable=locally-disabled test_parameters.py

import os
import json
import six
import numpy as np
import pytest
from taxcalc import ParametersBase, Policy  # pylint: disable=import-error


def test_instantiation_and_usage():
    """
    Test ParametersBase instantiation and usage.
    """
    # pylint: disable=protected-access
    pbase = ParametersBase()
    assert pbase
    assert pbase.inflation_rates() is None
    assert pbase.wage_growth_rates() is None
    syr = 2010
    nyrs = 10
    pbase.initialize(start_year=syr, num_years=nyrs)
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
    with pytest.raises(ValueError):
        ParametersBase.expand_array({}, True, [0.02], 1)
    threedarray = np.array([[[1, 1]], [[1, 1]], [[1, 1]]])
    with pytest.raises(ValueError):
        ParametersBase.expand_array(threedarray, True, [0.02, 0.02], 2)


@pytest.mark.parametrize("fname",
                         [("behavior.json"),
                          ("consumption.json"),
                          ("current_law_policy.json"),
                          ("growdiff.json")])
def test_json_file_contents(tests_path, fname):
    """
    Check contents of JSON parameter files.
    """
    # pylint: disable=too-many-locals,too-many-branches
    # specify test information
    reqkeys = ['long_name', 'description', 'notes',
               'row_var', 'row_label',
               'start_year', 'cpi_inflated',
               'col_var', 'col_label',
               'value']
    first_year = Policy.JSON_START_YEAR
    last_known_year = 2017  # for indexed parameters
    num_known_years = last_known_year - first_year + 1
    # read JSON parameter file into a dictionary
    path = os.path.join(tests_path, '..', fname)
    pfile = open(path, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)
    # check elements in each parameter sub-dictionary
    for pname in allparams:
        param = allparams[pname]
        assert isinstance(param, dict)
        # check that param contains required keys
        for key in reqkeys:
            assert key in param
        # check that row_var is FLPDYR
        assert param['row_var'] == 'FLPDYR'
        # check that start_year equals first_year
        syr = param['start_year']
        assert isinstance(syr, int) and syr == first_year
        # check that cpi_inflated is boolean
        assert isinstance(param['cpi_inflated'], bool)
        # check that row_label is list
        rowlabel = param['row_label']
        assert isinstance(rowlabel, list)
        # check all row_label values
        for idx in range(0, len(rowlabel)):
            cyr = first_year + idx
            assert int(rowlabel[idx]) == cyr
        # check type and dimension of value
        value = param['value']
        assert isinstance(value, list)
        assert len(value) == len(rowlabel)
        # check that col_var and col_label are consistent
        cvar = param['col_var']
        assert isinstance(cvar, six.string_types)
        clab = param['col_label']
        if cvar == '':
            assert isinstance(clab, six.string_types) and clab == ''
        else:
            assert isinstance(clab, list)
            # check different possible col_var values
            if cvar == 'MARS':
                assert len(clab) == 5
            elif cvar == 'EIC':
                assert len(clab) == 4
            elif cvar == 'idedtype':
                assert len(clab) == 7
            else:
                assert cvar == 'UNKNOWN col_var VALUE'
            # check length of each value row
            for valuerow in value:
                assert len(valuerow) == len(clab)
        # check that indexed parameters have all known years in rowlabel list
        # form_parameters are those whose value is available only on IRS form
        form_parameters = ['_AMT_em_pe',
                           '_ETC_pe_Single',
                           '_ETC_pe_Married']
        if param['cpi_inflated']:
            if pname in form_parameters:
                assert len(rowlabel) == num_known_years - 1
            else:
                assert len(rowlabel) == num_known_years
