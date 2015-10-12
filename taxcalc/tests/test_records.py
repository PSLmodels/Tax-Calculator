import os
import sys
import numpy as np
import pandas as pd
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
from taxcalc import Records, imputed_cmbtp_itemizer, Policy, Calculator

# use 1991 PUF-like data to emulate current PUF, which is private
TAX_DTA_PATH = os.path.join(CUR_PATH, '../../tax_all1991_puf.gz')
TAX_DTA = pd.read_csv(TAX_DTA_PATH, compression='gzip')
# PUF-fix-up: MIdR needs to be type int64 to match PUF
TAX_DTA['midr'] = TAX_DTA['midr'].astype('int64')
# specify WEIGHTS appropriate for 1991 data
WEIGHTS_FILENAME = '../../WEIGHTS_testing.csv'
WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
WEIGHTS = pd.read_csv(WEIGHTS_PATH)


def test_create_records_with_correct_start_year():
    recs = Records(data=TAX_DTA, weights=WEIGHTS,
                   start_year=Records.PUF_YEAR)
    assert recs
    assert np.any(recs._numextra != 0)


def test_create_records_with_wrong_start_year():
    recs = Records(data=TAX_DTA, weights=WEIGHTS,
                   start_year=2001)
    assert recs
    assert np.all(recs._numextra == 0)
    # absence of non-zero values for imputed recs._numextra variable will raise
    # an error when Calculator.calc_all() is called, guarding
    # against accidentally specifying wrong start_year


def test_create_records_from_file():
    recs = Records.from_file(TAX_DTA_PATH, weigths=WEIGHTS,
                             start_year=Records.PUF_YEAR)
    assert recs
    assert hasattr(recs, '_numextra') == True


def test_blow_up():
    tax_dta = pd.read_csv(TAX_DTA_PATH, compression='gzip')
    extra_years = Records.PUF_YEAR - 1991
    tax_dta.flpdyr += extra_years
    parms = Policy()
    parms_start_year = parms.current_year
    recs = Records(data=tax_dta)
    assert recs.current_year == Records.PUF_YEAR
    # r.current_year == PUF_YEAR implies Calculator ctor will call r.blowup()
    calc = Calculator(policy=parms, records=recs)
    assert calc.current_year == parms_start_year
    # have e aliases of p variables been maintained after several blowups?
    assert calc.records.e23250.sum() == calc.records.p23250.sum()
    assert calc.records.e22250.sum() == calc.records.p22250.sum()


def test_imputation_of_cmbtp_itemizer():
    e17500 = np.array([20., 4.4, 5.])
    e00100 = np.array([40., 8.1, 90.1])
    e18400 = np.array([25., 34., 10.])
    e62100 = np.array([75., 12.4, 84.])
    e00700 = np.array([43.3, 34.1, 3.4])
    e04470 = np.array([21.2, 12., 13.1])
    e21040 = np.array([45.9, 3., 45.])
    e18500 = np.array([33.1, 18.2, 39.])
    e20800 = np.array([0.9, 32., 52.1])
    cmbtp_itemizer = np.array([85.4, -31.0025, -45.7])
    """
    Test case values:
    x = max(0., e17500 - max(0., e00100) * 0.075) = [17., 3.7925, 0.]
    medical_adjustment = min(x, 0.025 * max(0.,e00100)) = [-1., -.2025, 0.]
    state_adjustment = max(0, e18400) = [42., 34., 49.]
    _cmbtp_itemizer = (e62100 - medical_adjustment + e00700 + e04470 + e21040
                       - z - e00100 - e18500 - e20800)
                    = [68.4, -31.0025 ,-84.7]
    """
    test_itemizer = imputed_cmbtp_itemizer(e17500, e00100, e18400,
                                           e62100, e00700, e04470,
                                           e21040, e18500, e20800)
    assert np.allclose(cmbtp_itemizer, test_itemizer)


def test_for_duplicate_names():
    var_names = set()
    inp_names = set()
    for var_name, inp_name in Records.NAMES:
        assert var_name not in var_names
        var_names.add(var_name)
        assert inp_name not in inp_names
        inp_names.add(inp_name)
    zero_names = set()
    for zero_name in Records.ZEROED_NAMES:
        assert zero_name not in zero_names
        zero_names.add(zero_name)
