import os
import sys
import json
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import tempfile
import pytest
from taxcalc import Parameters, Records, Calculator, expand_array
from taxcalc import create_distribution_table, create_difference_table


# use 1991 PUF-like data to emulate current PUF, which is private
TAX_DTA_PATH = os.path.join(CUR_PATH, '../../tax_all1991_puf.gz')
TAX_DTA = pd.read_csv(TAX_DTA_PATH, compression='gzip')
# PUF-fix-up: MIdR needs to be type int64 to match PUF
TAX_DTA['midr'] = TAX_DTA['midr'].astype('int64')
# specify WEIGHTS appropriate for 1991 data
WEIGHTS_FILENAME = '../../WEIGHTS_testing.csv'
WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
WEIGHTS = pd.read_csv(WEIGHTS_PATH)

IRATES = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024}


@pytest.yield_fixture
def paramsfile():

    txt = """{"_almdep": {"value": [7150, 7250, 7400]},
             "_almsep": {"value": [40400, 41050]},
             "_rt5": {"value": [0.33 ]},
             "_rt7": {"value": [0.396]}}"""

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(txt + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def run():
    parm = Parameters()
    assert parm.current_year == 2013
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(params=parm, records=recs)
    assert calc.current_year == 2013
    totaldf = calc.calc_all_test()
    totaldf = totaldf.T.groupby(level=0).first().T  # drop duplicates
    exp_results_file = os.path.join(CUR_PATH, '../../exp_results.csv.gz')
    exp_results = pd.read_csv(exp_results_file, compression='gzip')
    exp_set = set(exp_results.columns)  # fix-up to bad colname in exp_results
    cur_set = set(totaldf.columns)
    assert exp_set == cur_set
    for label in exp_results.columns:
        lhs = exp_results[label].values.reshape(len(exp_results))
        rhs = totaldf[label].values.reshape(len(exp_results))
        res = np.allclose(lhs, rhs, atol=1e-02)
        if not res:
            print('Problem found in: ', label)


def test_sequence():
    run()


def test_make_Calculator():
    parm = Parameters()
    assert parm.current_year == 2013
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(params=parm, records=recs)
    assert calc.current_year == 2013


def test_make_Calculator_deepcopy():
    import copy
    parm = Parameters()
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(params=parm, records=recs)
    calc2 = copy.deepcopy(calc1)
    assert isinstance(calc2, Calculator)


def test_make_Calculator_files_to_ctor(paramsfile):
    with open(paramsfile.name) as pfile:
        params = json.load(pfile)
    ppo = Parameters(parameter_dict=params, start_year=1991,
                     num_years=len(IRATES), inflation_rates=IRATES)
    calc = Calculator(params=ppo, records=TAX_DTA_PATH,
                      start_year=1991, inflation_rates=IRATES)
    assert calc


def test_make_Calculator_with_policy_reform():
    # create a Parameters object and apply a policy reform
    params2 = Parameters()
    reform2 = {2013: {'_II_em': np.array([4000]), '_II_em_cpi': False,
                      '_STD_Aged': [[1600, 1300, 1300, 1600, 1600, 1300]],
                      "_STD_Aged_cpi": False}}
    params2.implement_reform(reform2)
    # create a Calculator object using this policy-reform
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(params=params2, records=puf)
    # check that Parameters object embedded in Calculator object is correct
    assert calc2.current_year == 2013
    assert calc2.params.II_em == 4000
    assert_array_equal(calc2.params._II_em, np.array([4000] * 12))
    exp_STD_Aged = [[1600, 1300, 1300, 1600, 1600, 1300]] * 12
    assert_array_equal(calc2.params._STD_Aged, np.array(exp_STD_Aged))
    assert_array_equal(calc2.params.STD_Aged,
                       np.array([1600, 1300, 1300, 1600, 1600, 1300]))


def test_make_Calculator_with_multiyear_reform():
    # create a Parameters object and apply a policy reform
    params3 = Parameters()
    reform3 = {2015: {}}
    reform3[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform3[2015]['_II_em'] = [5000, 6000]  # reform values for 2015 and 2016
    reform3[2015]['_II_em_cpi'] = False
    params3.implement_reform(reform3)
    # create a Calculator object using this policy-reform
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc3 = Calculator(params=params3, records=puf)
    # check that Parameters object embedded in Calculator object is correct
    assert calc3.current_year == 2013
    assert calc3.params.II_em == 3900
    assert calc3.params.num_years == 12
    exp_II_em = [3900, 3950, 5000] + [6000] * 9
    assert_array_equal(calc3.params._II_em, np.array(exp_II_em))
    calc3.increment_year()
    calc3.increment_year()
    assert calc3.current_year == 2015
    assert_array_equal(calc3.params.STD_Aged,
                       np.array([1600, 1300, 1600, 1300, 1600, 1300]))


def test_make_Calculator_with_reform_after_start_year():
    # create Parameters object using custom indexing rates
    irates = {2013: 0.01, 2014: 0.01, 2015: 0.02, 2016: 0.01, 2017: 0.03}
    parm = Parameters(start_year=2013, num_years=len(irates),
                      inflation_rates=irates)
    # specify reform in 2015, which is two years after Parameters start_year
    reform = {2015: {}, 2016: {}}
    reform[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform[2015]['_II_em'] = [5000]
    reform[2016]['_II_em'] = [6000]
    reform[2016]['_II_em_cpi'] = False
    parm.implement_reform(reform)
    tax_dta = pd.read_csv(TAX_DTA_PATH, compression='gzip')
    recs = Records(data=tax_dta, weights=WEIGHTS, start_year=2009)
    calc = Calculator(params=parm, records=recs)
    # compare actual and expected parameter values over all years
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_array_equal(calc.params._STD_Aged, exp_STD_Aged)
    assert_array_equal(calc.params._II_em, exp_II_em)
    # compare actual and expected values for 2015
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2015
    exp_2015_II_em = 5000
    assert_array_equal(calc.params.II_em, exp_2015_II_em)
    exp_2015_STD_Aged = np.array([1600, 1300, 1600, 1300, 1600, 1300])
    assert_array_equal(calc.params.STD_Aged, exp_2015_STD_Aged)


def test_make_Calculator_user_mods_with_cpi_flags(paramsfile):
    with open(paramsfile.name) as pfile:
        params = json.load(pfile)
    ppo = Parameters(parameter_dict=params, start_year=1991,
                     num_years=len(IRATES), inflation_rates=IRATES)
    calc = Calculator(params=ppo, records=TAX_DTA_PATH, start_year=1991,
                      inflation_rates=IRATES)
    user_mods = {1991: {"_almdep": [7150, 7250, 7400],
                        "_almdep_cpi": True,
                        "_almsep": [40400, 41050],
                        "_almsep_cpi": False,
                        "_rt5": [0.33],
                        "_rt7": [0.396]}}
    calc.params.implement_reform(user_mods)

    inf_rates = [IRATES[1991 + i] for i in range(0, 12)]
    exp_almdep = expand_array(np.array([7150, 7250, 7400]), inflate=True,
                              inflation_rates=inf_rates, num_years=12)
    act_almdep = getattr(calc.params, '_almdep')
    assert_array_equal(act_almdep, exp_almdep)
    exp_almsep_values = [40400] + [41050] * 11
    exp_almsep = np.array(exp_almsep_values)
    act_almsep = getattr(calc.params, '_almsep')
    assert_array_equal(act_almsep, exp_almsep)


def test_make_Calculator_raises_on_no_params():
    rec = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2013)
    with pytest.raises(ValueError):
        calc = Calculator(records=rec)


def test_Calculator_attr_access_to_params():
    params = Parameters()
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(params=params, records=puf)
    assert hasattr(calc.records, 'c01000')
    assert hasattr(calc.params, '_AMT_Child_em')
    assert hasattr(calc, 'params')


def test_Calculator_create_distribution_table():
    params = Parameters()
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(params=params, records=puf)
    calc.calc_all()
    dist_labels = ['Returns', 'AGI', 'Standard Deduction Filers',
                   'Standard Deduction', 'Itemizers',
                   'Itemized Deduction', 'Personal Exemption',
                   'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers',
                   'AMT', 'Tax before Credits', 'Non-refundable Credits',
                   'Tax before Refundable Credits', 'Refundable Credits',
                   'Revenue']
    dt1 = create_distribution_table(calc, groupby="weighted_deciles",
                                    result_type="weighted_sum")
    dt1.columns = dist_labels
    dt2 = create_distribution_table(calc, groupby="small_income_bins",
                                    result_type="weighted_avg")
    assert isinstance(dt1, pd.DataFrame)
    assert isinstance(dt2, pd.DataFrame)


def test_Calculator_calculate_mtr():
    # Create a Parameters object
    params = Parameters(start_year=1991, inflation_rates=irates)

    # Create a Public Use File object
    puf = Records(tax_dta)

    # Create a Calculator
    calc = Calculator(params=params, records=puf)

    mtr = calc.mtr('e00200')
    assert type(mtr) == np.ndarray


def test_Calculator_create_difference_table():
    # create current-law Parameters object and use to create Calculator calc1
    params1 = Parameters()
    puf1 = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(params=params1, records=puf1)
    calc1.calc_all()
    # create policy-reform Parameters object and use to create Calculator calc2
    params2 = Parameters()
    reform = {2013: {'_II_rt7': [0.45]}}
    params2.implement_reform(reform)
    puf2 = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(params=params2, records=puf2)
    # create difference table and check that it is a Pandas DataFrame
    dtable = create_difference_table(calc1, calc2, groupby="weighted_deciles")
    assert isinstance(dtable, pd.DataFrame)


def test_diagnostic_table():
    params = Parameters()
    TAX_DTA.flpdyr += 18  # flpdyr==2009 so that Records ctor will apply blowup
    puf = Records(data=TAX_DTA, weights=WEIGHTS)
    calc = Calculator(params=params, records=puf)
    calc.diagnostic_table()


def test_make_Calculator_increment_years_first():
    # create Parameters object with custom indexing rates and policy reform
    irates = {2013: 0.01, 2014: 0.01, 2015: 0.02, 2016: 0.01, 2017: 0.03}
    params = Parameters(start_year=2013, inflation_rates=irates,
                        num_years=len(irates))
    reform = {2015: {}, 2016: {}}
    reform[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform[2015]['_II_em'] = [5000]
    reform[2016]['_II_em'] = [6000]
    reform[2016]['_II_em_cpi'] = False
    params.implement_reform(reform)
    # create Records object by reading 1991 data and saying it is 2009 data
    tax_dta = pd.read_csv(TAX_DTA_PATH, compression='gzip')
    puf = Records(tax_dta, weights=WEIGHTS, start_year=2009)
    # create Calculator object with Parameters object as modified by reform
    calc = Calculator(params=params, records=puf)
    # compare expected policy parameter values with those embedded in calc
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_array_equal(calc.params._STD_Aged, exp_STD_Aged)
    assert_array_equal(calc.params._II_em, exp_II_em)


class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
