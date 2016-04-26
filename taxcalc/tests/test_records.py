import os
import sys
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator, Growth
from taxcalc import imputed_cmbtp_itemizer

# use 1991 PUF-like data to emulate current puf.csv, which is private
TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91taxdata.csv.gz')
TAXDATA = pd.read_csv(TAXDATA_PATH, compression='gzip')
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91weights.csv.gz')
WEIGHTS = pd.read_csv(WEIGHTS_PATH, compression='gzip')


def test_create_records():
    recs = Records(data=TAXDATA, weights=WEIGHTS, start_year=Records.PUF_YEAR)
    assert recs
    assert np.any(recs.MARS != 0)


def test_blow_up():
    tax_dta = pd.read_csv(TAXDATA_PATH, compression='gzip')
    parms = Policy()
    parms_start_year = parms.current_year
    recs = Records(data=tax_dta, start_year=Records.PUF_YEAR)
    assert recs.current_year == Records.PUF_YEAR
    # r.current_year == PUF_YEAR ==> Calculator ctor will call r.blowup()
    calc = Calculator(policy=parms, records=recs)
    assert calc.current_year == parms_start_year


def test_imputation_of_cmbtp_itemizer():
    e17500 = np.array([20., 4.4, 5.])
    e00100 = np.array([40., 8.1, 90.1])
    e18400 = np.array([25., 34., 10.])
    e62100 = np.array([75., 12.4, 84.])
    e00700 = np.array([43.3, 34.1, 3.4])
    p04470 = np.array([21.2, 12., 13.1])
    e21040 = np.array([45.9, 3., 45.])
    e18500 = np.array([33.1, 18.2, 39.])
    e20800 = np.array([0.9, 32., 52.1])
    cmbtp_itemizer = np.array([85.4, -31.0025, -45.7])
    """
    Test case values:
    x = max(0., e17500 - max(0., e00100) * 0.075) = [17., 3.7925, 0.]
    medical_adjustment = min(x, 0.025 * max(0.,e00100)) = [-1., -.2025, 0.]
    state_adjustment = max(0, e18400) = [42., 34., 49.]
    _cmbtp_itemizer = (e62100 - medical_adjustment + e00700 + p04470 + e21040
                       - z - e00100 - e18500 - e20800)
                    = [68.4, -31.0025 ,-84.7]
    """
    test_itemizer = imputed_cmbtp_itemizer(e17500, e00100, e18400,
                                           e62100, e00700, p04470,
                                           e21040, e18500, e20800)
    assert np.allclose(cmbtp_itemizer, test_itemizer)


def test_for_duplicate_names():
    varnames = set()
    for varname in Records.VALID_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.CALCULATED_VARS
    varnames = set()
    for varname in Records.CALCULATED_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.VALID_READ_VARS
    varnames = set()
    for varname in Records.INTEGER_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname in Records.VALID_READ_VARS


def test_default_rates_and_those_implied_by_blowup_factors():
    """
    Check that default GDP growth rates, default wage growth rates, and
    default price inflation rates, are consistent with the rates embedded
    in the Records blowup factors (BF).
    """
    record = Records(TAXDATA_PATH)  # contains the blowup factors
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


def test_var_labels_txt_contents():
    """
    Check that every Records variable used by taxcalc is in var_labels.txt
    and that all variables in var_labels.txt are used by taxcalc.
    """
    # read variables in var_labels.txt file (checking for duplicates)
    var_labels_path = os.path.join(CUR_PATH, '..', 'var_labels.txt')
    var_labels_set = set()
    with open(var_labels_path, 'r') as input:
        for line in input:
            var = (line.split())[0]
            if var in var_labels_set:
                msg = 'DUPLICATE_IN_VAR_LABELS.TXT: {}\n'.format(var)
                sys.stdout.write(msg)
                assert False
            else:
                var_labels_set.add(var)
    # change all VALID variables to uppercase
    var_used_set = set()
    for var in Records.VALID_READ_VARS:
        var_used_set.add(var.upper())
    # check for no extra var_used variables
    used_less_labels = var_used_set - var_labels_set
    assert len(used_less_labels) == 0
    # check for no extra var_labels variables
    labels_less_used = var_labels_set - var_used_set
    assert len(labels_less_used) == 0
