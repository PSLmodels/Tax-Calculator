"""
Test Records class and its methods.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_records.py
# pylint --disable=locally-disabled test_records.py

import os
import json
from io import StringIO
import numpy as np
import pandas as pd
import pytest
from taxcalc import GrowFactors, Policy, Records


def test_incorrect_records_instantiation(cps_subsample, cps_fullsample):
    """Test docstring"""
    with pytest.raises(ValueError):
        _ = Records(data=[])
    with pytest.raises(ValueError):
        _ = Records(data=cps_subsample, gfactors=[])
    with pytest.raises(ValueError):
        _ = Records(data=cps_subsample, gfactors=None, weights=[])
    with pytest.raises(ValueError):
        _ = Records(data=cps_subsample, gfactors=None, weights=None,
                    start_year=[])
    with pytest.raises(ValueError):
        _ = Records(data=cps_subsample, gfactors=None, weights=None,
                    adjust_ratios=[])
    # test error raise when num of records is greater than num of weights
    cps_weights_path = os.path.join(Records.CODE_PATH, 'cps_weights.csv.gz')
    weights = pd.read_csv(cps_weights_path)
    some_wghts = weights[:100]
    with pytest.raises(ValueError):
        _ = Records(data=cps_fullsample, weights=some_wghts, start_year=2020)


def test_invalid_variable_values_1(cps_subsample):
    """Test docstring"""
    dta = cps_subsample.copy()
    dta['PT_SSTB_income'] = 2
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['e01700'] = 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['e00650'] = 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['k1bx14s'] = 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['e02100'] = dta['e02100p'] + dta['e02100s'] + 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['e00900'] = dta['e00900p'] + dta['e00900s'] + 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['e00200'] = dta['e00200p'] + dta['e00200s'] + 1000
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['EIC'] = 4
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta['MARS'] = 0
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)


def test_invalid_variable_values_2():
    """Test docstring"""
    dta = pd.DataFrame(
        {
            'RECID': [1],
            'MARS': [1],
            'e00200p': [8e4],
            'e00200s': [1e4],
            'e00200': [9e4],
        }
    )
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta = pd.DataFrame(
        {
            'RECID': [1],
            'MARS': [1],
            'e00900p': [8e4],
            'e00900s': [1e4],
            'e00900': [9e4],
        }
    )
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)
    dta = pd.DataFrame(
        {
            'RECID': [1],
            'MARS': [1],
            'e02100p': [8e4],
            'e02100s': [1e4],
            'e02100': [9e4],
        }
    )
    with pytest.raises(ValueError):
        _ = Records(data=dta, start_year=2000)


def test_correct_records_instantiation(cps_subsample):
    """Test docstring"""
    rec1 = Records.cps_constructor(data=cps_subsample, gfactors=None)
    assert rec1
    assert np.all(getattr(rec1, 'MARS') != 0)
    assert getattr(rec1, 'current_year') == getattr(rec1, 'data_year')
    sum_e00200_in_cps_year = getattr(rec1, 'e00200').sum()
    rec1.increment_year()
    sum_e00200_in_cps_year_plus_one = getattr(rec1, 'e00200').sum()
    assert sum_e00200_in_cps_year_plus_one == sum_e00200_in_cps_year
    wghts_path = os.path.join(Records.CODE_PATH, 'cps_weights.csv.gz')
    wghts_df = pd.read_csv(wghts_path)
    rec2 = Records(data=cps_subsample,
                   start_year=Records.CPSCSV_YEAR,
                   gfactors=GrowFactors(),
                   weights=wghts_df,
                   adjust_ratios=None,
                   exact_calculations=False,
                   weights_scale=0.01)
    assert rec2
    assert np.all(getattr(rec2, 'MARS') != 0)
    assert getattr(rec2, 'current_year') == getattr(rec2, 'data_year')


def test_read_cps_data(cps_fullsample):
    """Test docstring"""
    data = Records.read_cps_data()
    assert data.equals(cps_fullsample)


@pytest.mark.parametrize('csv', [
    (
        'RECID,MARS,e00200,e00200p,e00200s\n'
        '1,    2,   200000, 200000,   0.03\n'
    ),
    (
        'RECID,MARS,e00900,e00900p,e00900s\n'
        '1,    2,   200000, 200000,   0.03\n'
    ),
    (
        'RECID,MARS,e02100,e02100p,e02100s\n'
        '1,    2,   200000, 200000,   0.03\n'
    ),
    (
        'RECID,MARS,e00200,e00200p,e00200s\n'
        '1,    4,   200000, 100000, 100000\n'
    ),
    (
        'RECID,MARS,e00900,e00900p,e00900s\n'
        '1,    4,   200000, 100000, 100000\n'
    ),
    (
        'RECID,MARS,e02100,e02100p,e02100s\n'
        '1,    4,   200000, 100000, 100000\n'
    ),
    (
        'RECID,MARS,k1bx14s\n'
        '1,    4,   0.03\n'
    ),
    (
        'RxCID,MARS\n'
        '1,    2\n'
    ),
    (
        'RECID,e00300\n'
        '1,    456789\n'
    ),
    (
        'RECID,MARS\n'
        '1,    6\n'
    ),
    (
        'RECID,MARS,EIC\n'
        '1,    5,   4\n'
    ),
    (
        'RECID,MARS,e00600,e00650\n'
        '1,    1,        8,     9\n'
    ),
    (
        'RECID,MARS,e01500,e01700\n'
        '1,    1,        6,     7\n'
    ),
    (
        'RECID,MARS,PT_SSTB_income\n'
        '1,    1,   2\n'
    )
])
def test_read_data(csv):
    """Test docstring"""
    df = pd.read_csv(StringIO(csv))
    with pytest.raises(ValueError):
        Records(data=df)


def test_for_duplicate_names():
    """Test docstring"""
    records_varinfo = Records(data=None)
    num_vars = 0
    varnames = set()
    for varname in records_varinfo.USABLE_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in records_varinfo.CALCULATED_VARS
    num_vars += len(varnames)
    varnames = set()
    for varname in records_varinfo.CALCULATED_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in records_varinfo.USABLE_READ_VARS
    num_vars += len(varnames)
    varnames = set()
    for varname in records_varinfo.INTEGER_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname in records_varinfo.USABLE_READ_VARS
    assert num_vars == 211  # number of vars in records_variables.json


def test_records_variables_content(tests_path):
    """
    Check completeness and consistency of records_variables.json content.
    """
    # pylint: disable=too-many-locals

    # specify test information
    reqkeys = ['type', 'desc', 'form']
    first_year = Policy.JSON_START_YEAR
    last_form_year = 2017
    # read JSON variable file into a dictionary
    path = os.path.join(tests_path, '..', 'records_variables.json')
    with open(path, 'r', encoding='utf-8') as vfile:
        allvars = json.load(vfile)
    assert isinstance(allvars, dict)
    # check elements in each variable dictionary
    for iotype in ['read', 'calc']:
        for vname in allvars[iotype]:
            variable = allvars[iotype][vname]
            assert isinstance(variable, dict)
            # check that variable contains required keys
            for key in reqkeys:
                assert key in variable
            # check that required is true if it is present
            if 'required' in variable:
                assert variable['required'] is True
            # check that forminfo is dictionary with sensible year ranges
            forminfo = variable['form']
            assert isinstance(forminfo, dict)
            yranges = sorted(forminfo.keys())
            num_yranges = len(yranges)
            prior_eyr = first_year - 1
            yrange_num = 0
            for yrange in yranges:
                yrange_num += 1
                yrlist = yrange.split('-')
                fyr = int(yrlist[0])
                if yrlist[1] == '20??':
                    indefinite_yrange = True
                    assert yrange_num == num_yranges
                else:
                    indefinite_yrange = False
                    eyr = int(yrlist[1])
                    if fyr != (prior_eyr + 1):
                        msg1 = f'{vname} fyr {fyr}'
                        msg2 = f'!= prior_eyr_1 {prior_eyr + 1}'
                        assert msg1 == msg2
                    if eyr > last_form_year:
                        msg1 = f'{vname} eyr {eyr}'
                        msg2 = f'> last_form_year {last_form_year}'
                        assert msg1 == msg2
                    prior_eyr = eyr
            if not indefinite_yrange and len(yranges) > 0:
                prior_ey_ok = prior_eyr in (last_form_year, last_form_year - 1)
                if not prior_ey_ok:
                    msg1 = f'{vname} prior_eyr {prior_eyr}'
                    msg2 = f'!= last_form_year {last_form_year}'
                    assert msg1 == msg2


def test_csv_input_vars_md_contents(tests_path):
    """
    Check CSV_INPUT_VARS.md contents against Records.USABLE_READ_VARS
    """
    # read variable names in CSV_INPUT_VARS.md file (checking for duplicates)
    civ_path = os.path.join(tests_path, '..', 'validation',
                            'CSV_INPUT_VARS.md')
    civ_set = set()
    with open(civ_path, 'r', encoding='utf-8') as civfile:
        msg = 'DUPLICATE VARIABLE(S) IN CSV_INPUT_VARS.MD FILE:\n'
        found_duplicates = False
        for line in civfile:
            str_list = line.split('|', 2)
            if len(str_list) != 3:
                continue  # because line is not part of the markdown table
            assert str_list[0] == ''  # because line starts with | character
            var = (str_list[1]).strip()  # remove surrounding whitespace
            if var == 'Var-name' or var[0] == ':':
                continue  # skip two lines that are the table head
            if var in civ_set:
                found_duplicates = True
                msg += f'VARIABLE= {var}\n'
            else:
                civ_set.add(var)
        if found_duplicates:
            raise ValueError(msg)
    # check that civ_set is a subset of Records.USABLE_READ_VARS set
    records_varinfo = Records(data=None)
    if not civ_set.issubset(records_varinfo.USABLE_READ_VARS):
        valid_less_civ = records_varinfo.USABLE_READ_VARS - civ_set
        msg = 'VARIABLE(S) IN USABLE_READ_VARS BUT NOT CSV_INPUT_VARS.MD:\n'
        for var in valid_less_civ:
            msg += f'VARIABLE= {var}\n'  # pylint: disable=consider-using-join
        raise ValueError(msg)


def test_cps_availability(tests_path, cps_data_path):
    """
    Cross-check records_variables.json data with variables in cps.csv file.
    """
    # make set of variable names that are in the cps.csv file
    cpsdf = pd.read_csv(cps_data_path)
    cpsvars = set(sorted(list(cpsdf)))
    # make set of variable names that are marked as cps available in r_v.json
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r', encoding='utf-8') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_cps' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that cpsvars and recvars sets are the same
    assert (cpsvars - recvars) == set()
    assert (recvars - cpsvars) == set()


@pytest.mark.requires_puf
def test_puf_availability(tests_path, puf_data_path):
    """
    Cross-check records_variables.json data with variables in puf.csv file
    """
    # make set of variable names that are in the puf.csv file
    pufdf = pd.read_csv(puf_data_path)
    pufvars = set(sorted(list(pufdf)))
    # make set of variable names that are marked as puf available in r_v.json
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r', encoding='utf-8') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_puf' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that pufvars and recvars sets are the same
    assert (pufvars - recvars) == set()
    assert (recvars - pufvars) == set()


@pytest.mark.requires_tmd
def test_tmd_availability(tests_path, tmd_data_path):
    """
    Cross-check records_variables.json data with variables in tmd.csv file
    """
    # make set of variable names that are in the tmd.csv file
    tmddf = pd.read_csv(tmd_data_path)
    tmdvars = set(sorted(list(tmddf)))
    # make set of variable names that are marked as tmd available in r_v.json
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r', encoding='utf-8') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxmicrodata_tmd' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that tmdvars and recvars sets are the same
    assert (tmdvars - recvars) == set()
    assert (recvars - tmdvars) == set()
