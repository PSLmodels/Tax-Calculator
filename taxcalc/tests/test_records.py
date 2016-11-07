import os
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
from io import StringIO
from taxcalc import Policy, Records, Calculator, Growth


def test_incorrect_Records_instantiation(puf_1991):
    with pytest.raises(ValueError):
        recs = Records(data=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, blowup_factors=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, blowup_factors=None, weights=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, blowup_factors=None, weights=None,
                       start_year=list())


def test_correct_Records_instantiation(puf_1991, puf_1991_path, weights_1991):
    rec1 = Records(data=puf_1991_path, blowup_factors=None,
                   weights=weights_1991)
    assert rec1
    assert np.all(rec1.MARS != 0)
    assert rec1.current_year == Records.PUF_YEAR
    sum_e00200_in_puf_year = rec1.e00200.sum()
    rec1.set_current_year(Records.PUF_YEAR + 1)
    sum_e00200_in_puf_year_plus_one = rec1.e00200.sum()
    assert sum_e00200_in_puf_year_plus_one == sum_e00200_in_puf_year
    bf_df = pd.read_csv(Records.BLOWUP_FACTORS_PATH)
    rec2 = Records(data=puf_1991, blowup_factors=bf_df, weights=None)
    assert rec2
    assert np.all(rec2.MARS != 0)
    assert rec2.current_year == Records.PUF_YEAR


def test_correct_Records_instantiation_sample(puf_1991, weights_1991):
    sample = puf_1991.sample(frac=0.10)
    rec1 = Records(data=sample, blowup_factors=None, weights=weights_1991)
    assert rec1
    assert np.all(rec1.MARS != 0)
    assert rec1.current_year == Records.PUF_YEAR
    sum_e00200_in_puf_year = rec1.e00200.sum()
    rec1.set_current_year(Records.PUF_YEAR + 1)
    sum_e00200_in_puf_year_plus_one = rec1.e00200.sum()
    assert sum_e00200_in_puf_year_plus_one == sum_e00200_in_puf_year
    bf_df = pd.read_csv(Records.BLOWUP_FACTORS_PATH)
    rec2 = Records(data=sample, blowup_factors=bf_df, weights=None)
    assert rec2
    assert np.all(rec2.MARS != 0)
    assert rec2.current_year == Records.PUF_YEAR


@pytest.mark.parametrize("csv", [
    (
        u'RECID,MARS,e00200,e00200p,e00200s\n'
        u'1,    2,   200000, 200000,   0.01\n'
    ),
    (
        u'RECID,MARS,e00900,e00900p,e00900s\n'
        u'1,    2,   200000, 200000,   0.01\n'
    ),
    (
        u'RECID,MARS,e02100,e02100p,e02100s\n'
        u'1,    2,   200000, 200000,   0.01\n'
    ),
    (
        u'RxCID,MARS\n'
        u'1,    2\n'
    ),
    (
        u'RECID,e00300\n'
        u'1,    456789\n'
    ),
    (
        u'RECID,MARS,e00600,e00650\n'
        u'1,    1,        8,     9\n'
    )
])
def test_read_data(csv):
    df = pd.read_csv(StringIO(csv))
    with pytest.raises(ValueError):
        Records(data=df)


def test_blowup(puf_1991, weights_1991):
    pol1 = Policy()
    assert pol1.current_year == Policy.JSON_START_YEAR
    rec1 = Records(data=puf_1991, weights=weights_1991)
    assert rec1.current_year == Records.PUF_YEAR
    calc1 = Calculator(policy=pol1, records=rec1, sync_years=True)
    assert calc1.records.current_year == Policy.JSON_START_YEAR
    pol2 = Policy()
    assert pol2.current_year == Policy.JSON_START_YEAR
    rec2 = Records(data=puf_1991, weights=weights_1991)
    assert rec2.current_year == Records.PUF_YEAR
    rec2.set_current_year(Policy.JSON_START_YEAR)
    assert rec2.current_year == Policy.JSON_START_YEAR
    calc2 = Calculator(policy=pol2, records=rec2, sync_years=False)
    assert calc2.policy.current_year == Policy.JSON_START_YEAR
    assert calc2.records.current_year == Policy.JSON_START_YEAR


def test_for_duplicate_names():
    varnames = set()
    for varname in Records.USABLE_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.CALCULATED_VARS
    varnames = set()
    for varname in Records.CALCULATED_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.USABLE_READ_VARS
    varnames = set()
    for varname in Records.INTEGER_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname in Records.USABLE_READ_VARS


def test_default_rates_and_those_implied_by_blowup_factors(puf_1991):
    """
    Check that default GDP growth rates, default wage growth rates, and
    default price inflation rates, are consistent with the rates embedded
    in the Records blowup factors (BF).
    """
    record = Records(data=puf_1991)  # contains the blowup factors
    policy = Policy()  # contains the default indexing rates
    syr = Policy.JSON_START_YEAR
    endyr = Policy.LAST_BUDGET_YEAR
    nyrs = endyr - syr

    # back out original stage I GDP growth rates from blowup factors
    record.BF.AGDPN[Records.PUF_YEAR] = 1
    for year in range(Records.PUF_YEAR + 1, endyr + 1):
        record.BF.AGDPN[year] = (record.BF.AGDPN[year] *
                                 record.BF.AGDPN[year - 1] *
                                 record.BF.APOPN[year])

    # calculate nominal GDP growth rates from original GDP growth rates
    nominal_rates = np.zeros(nyrs)
    for year in range(syr + 1, endyr):
        irate = policy._inflation_rates[year - syr]
        nominal_rates[year - syr] = (record.BF.AGDPN[year] /
                                     record.BF.AGDPN[year - 1] - 1 - irate)

    # check that nominal_rates are same as default GDP growth rates
    nominal_rates = np.round(nominal_rates, 4)
    assert_array_equal(nominal_rates[1:], Growth.REAL_GDP_GROWTH_RATES[1:-1])

    # back out stage I inflation rates from blowup factors
    cpi_u = np.zeros(nyrs)
    for year in range(syr, endyr):
        cpi_u[year - syr] = record.BF.ACPIU[year] - 1

    # check that blowup rates are same as default inflation rates
    cpi_u = np.round(cpi_u, 4)
    assert_array_equal(cpi_u, policy._inflation_rates[:-1])

    # back out original stage I wage growth rates from blowup factors
    record.BF.AWAGE[Records.PUF_YEAR] = 1
    for year in range(Records.PUF_YEAR + 1, endyr):
        record.BF.AWAGE[year] = (record.BF.AWAGE[year] *
                                 record.BF.AWAGE[year - 1] *
                                 record.BF.APOPN[year])

    # calculate nominal wage growth rates from original wage growth rates
    wage_growth_rates = np.zeros(nyrs)
    for year in range(syr + 1, endyr):
        wage_growth_rates[year - syr] = (record.BF.AWAGE[year] /
                                         record.BF.AWAGE[year - 1] - 1)

    # check that blowup rates are same as default wage growth rates
    wage_growth_rates = np.round(wage_growth_rates, 4)
    assert_array_equal(wage_growth_rates[1:], policy._wage_growth_rates[1:-1])


def test_var_labels_txt_contents(tests_path):
    """
    Check that every Records variable used by taxcalc is in var_labels.txt
    and that all variables in var_labels.txt are used by taxcalc.
    """
    # read variables in var_labels.txt file (checking for duplicates)
    var_labels_path = os.path.join(tests_path, '..', 'var_labels.txt')
    var_labels_set = set()
    with open(var_labels_path, 'r') as varlabels:
        msg = 'DUPLICATE VARIABLE(S) IN VAR_LABELS.TXT:\n'
        found_duplicates = False
        for line in varlabels:
            var = (line.split())[0]
            if var in var_labels_set:
                found_duplicates = True
                msg += 'VARIABLE= {}\n'.format(var)
            else:
                var_labels_set.add(var)
        if found_duplicates:
            raise ValueError(msg)
    # change all Records.USABLE_READ_VARS variables to uppercase
    var_valid_set = set()
    for var in Records.USABLE_READ_VARS:
        var_valid_set.add(var.upper())
    # check for no extra var_valid variables
    valid_less_labels = var_valid_set - var_labels_set
    if len(valid_less_labels) > 0:
        msg = 'VARIABLE(S) IN USABLE_READ_VARS BUT NOT VAR_LABELS.TXT:\n'
        for var in valid_less_labels:
            msg += 'VARIABLE= {}\n'.format(var)
        raise ValueError(msg)
    # check for no extra var_labels variables
    labels_less_valid = var_labels_set - var_valid_set
    if len(labels_less_valid) > 0:
        msg = 'VARIABLE(S) IN VAR_LABELS.TXT BUT NOT USABLE_READ_VARS:\n'
        for var in labels_less_valid:
            msg += 'VARIABLE= {}\n'.format(var)
        raise ValueError(msg)


def test_csv_input_vars_md_contents(tests_path):
    """
    Check CSV_INPUT_VARS.md contents against Records.USABLE_READ_VARS
    """
    # read variable names in CSV_INPUT_VARS.md file (checking for duplicates)
    civ_path = os.path.join(tests_path, '..', 'validation',
                            'CSV_INPUT_VARS.md')
    civ_set = set()
    with open(civ_path, 'r') as civfile:
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
                msg += 'VARIABLE= {}\n'.format(var)
            else:
                civ_set.add(var)
        if found_duplicates:
            raise ValueError(msg)
    # check that civ_set is a subset of Records.USABLE_READ_VARS set
    if not civ_set.issubset(Records.USABLE_READ_VARS):
        valid_less_civ = Records.USABLE_READ_VARS - civ_set
        msg = 'VARIABLE(S) IN USABLE_READ_VARS BUT NOT CSV_INPUT_VARS.MD:\n'
        for var in valid_less_civ:
            msg += 'VARIABLE= {}\n'.format(var)
        raise ValueError(msg)
