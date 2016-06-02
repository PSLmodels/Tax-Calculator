import os
import sys
import json
import numpy as np
from numpy.testing import assert_allclose
import pandas as pd
import tempfile
import pytest
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator
from taxcalc import create_distribution_table, create_difference_table

# use 1991 PUF-like data to emulate current puf.csv, which is private
TAXDATA_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91taxdata.csv.gz')
TAXDATA = pd.read_csv(TAXDATA_PATH, compression='gzip')
WEIGHTS_PATH = os.path.join(CUR_PATH, '..', 'altdata', 'puf91weights.csv.gz')
WEIGHTS = pd.read_csv(WEIGHTS_PATH, compression='gzip')

IRATES = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024, 2003: 0.024, 2004: 0.024}

WRATES = {1991: 0.0276, 1992: 0.0419, 1993: 0.0465, 1994: 0.0498,
          1995: 0.0507, 1996: 0.0481, 1997: 0.0451, 1998: 0.0441,
          1999: 0.0437, 2000: 0.0435, 2001: 0.0430, 2002: 0.0429,
          2003: 0.0429, 2004: 0.0429}

RAWINPUTFILE_FUNITS = 4
RAWINPUTFILE_YEAR = 2015
RAWINPUTFILE_CONTENTS = (
    'RECID,MARS\n'
    '1,2\n'
    '2,1\n'
    '3,4\n'
    '4,6\n'
)


@pytest.yield_fixture
def rawinputfile():
    """
    Temporary input file that contains minimum required input varaibles.
    """
    ifile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    ifile.write(RAWINPUTFILE_CONTENTS)
    ifile.close()
    # must close and then yield for Windows platform
    yield ifile
    if os.path.isfile(ifile.name):
        try:
            os.remove(ifile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


@pytest.yield_fixture
def policyfile():
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


def test_make_Calculator():
    parm = Policy()
    assert parm.current_year == 2013
    recs = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=parm, records=recs)
    assert calc.current_year == 2013


def test_make_Calculator_deepcopy():
    import copy
    parm = Policy()
    recs = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(policy=parm, records=recs)
    calc2 = copy.deepcopy(calc1)
    assert isinstance(calc2, Calculator)


def test_make_Calculator_with_policy_reform():
    # create a Policy object and apply a policy reform
    policy2 = Policy()
    reform2 = {2013: {'_II_em': np.array([4000]), '_II_em_cpi': False,
                      '_STD_Aged': [[1600, 1300, 1300, 1600, 1600, 1300]],
                      "_STD_Aged_cpi": False}}
    policy2.implement_reform(reform2)
    # create a Calculator object using this policy-reform
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(policy=policy2, records=puf)
    # check that Policy object embedded in Calculator object is correct
    assert calc2.current_year == 2013
    assert calc2.policy.II_em == 4000
    assert_allclose(calc2.policy._II_em,
                    np.array([4000] * Policy.DEFAULT_NUM_YEARS),
                    atol=0.01, rtol=0.0)
    exp_STD_Aged = [[1600, 1300, 1300,
                     1600, 1600, 1300]] * Policy.DEFAULT_NUM_YEARS
    assert_allclose(calc2.policy._STD_Aged, np.array(exp_STD_Aged),
                    atol=0.01, rtol=0.0)
    assert_allclose(calc2.policy.STD_Aged,
                    np.array([1600, 1300, 1300, 1600, 1600, 1300]),
                    atol=0.01, rtol=0.0)


def test_make_Calculator_with_multiyear_reform():
    # create a Policy object and apply a policy reform
    policy3 = Policy()
    reform3 = {2015: {}}
    reform3[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform3[2015]['_II_em'] = [5000, 6000]  # reform values for 2015 and 2016
    reform3[2015]['_II_em_cpi'] = False
    policy3.implement_reform(reform3)
    # create a Calculator object using this policy-reform
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc3 = Calculator(policy=policy3, records=puf)
    # check that Policy object embedded in Calculator object is correct
    assert calc3.current_year == 2013
    assert calc3.policy.II_em == 3900
    assert calc3.policy.num_years == Policy.DEFAULT_NUM_YEARS
    exp_II_em = [3900, 3950, 5000] + [6000] * (Policy.DEFAULT_NUM_YEARS - 3)
    assert_allclose(calc3.policy._II_em, np.array(exp_II_em),
                    atol=0.01, rtol=0.0)
    calc3.increment_year()
    calc3.increment_year()
    assert calc3.current_year == 2015
    assert_allclose(calc3.policy.STD_Aged,
                    np.array([1600, 1300, 1600, 1300, 1600, 1300]),
                    atol=0.01, rtol=0.0)


def test_make_Calculator_with_reform_after_start_year():
    # create Policy object using custom indexing rates
    irates = {2013: 0.01, 2014: 0.01, 2015: 0.02, 2016: 0.01, 2017: 0.03}
    parm = Policy(start_year=2013, num_years=len(irates),
                  inflation_rates=irates)
    # specify reform in 2015, which is two years after Policy start_year
    reform = {2015: {}, 2016: {}}
    reform[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform[2015]['_II_em'] = [5000]
    reform[2016]['_II_em'] = [6000]
    reform[2016]['_II_em_cpi'] = False
    parm.implement_reform(reform)
    recs = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=parm, records=recs)
    # compare actual and expected parameter values over all years
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_allclose(calc.policy._STD_Aged, exp_STD_Aged, atol=0.5, rtol=0.0)
    assert_allclose(calc.policy._II_em, exp_II_em, atol=0.001, rtol=0.0)
    # compare actual and expected values for 2015
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2015
    exp_2015_II_em = 5000
    assert_allclose(calc.policy.II_em, exp_2015_II_em,
                    atol=0.0, rtol=0.0)
    exp_2015_STD_Aged = np.array([1600, 1300, 1600, 1300, 1600, 1300])
    assert_allclose(calc.policy.STD_Aged, exp_2015_STD_Aged,
                    atol=0.0, rtol=0.0)


def test_Calculator_advance_to_year():
    policy = Policy()
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    calc.advance_to_year(2016)
    assert calc.current_year == 2016
    with pytest.raises(ValueError):
        calc.advance_to_year(2015)


def test_make_Calculator_user_mods_with_cpi_flags(policyfile):
    with open(policyfile.name) as pfile:
        policy = json.load(pfile)
    ppo = Policy(parameter_dict=policy, start_year=1991,
                 num_years=len(IRATES), inflation_rates=IRATES,
                 wage_growth_rates=WRATES)
    rec = Records(data=TAXDATA, start_year=1991)
    calc = Calculator(policy=ppo, records=rec)
    user_mods = {1991: {"_almdep": [7150, 7250, 7400],
                        "_almdep_cpi": True,
                        "_almsep": [40400, 41050],
                        "_almsep_cpi": False,
                        "_rt5": [0.33],
                        "_rt7": [0.396]}}
    calc.policy.implement_reform(user_mods)
    # compare actual and expected values
    inf_rates = [IRATES[1991 + i] for i in range(0, Policy.DEFAULT_NUM_YEARS)]
    exp_almdep = Policy.expand_array(np.array([7150, 7250, 7400]),
                                     inflate=True,
                                     inflation_rates=inf_rates,
                                     num_years=Policy.DEFAULT_NUM_YEARS)
    act_almdep = getattr(calc.policy, '_almdep')
    assert_allclose(act_almdep, exp_almdep, atol=0.01, rtol=0.0)
    exp_almsep_values = [40400] + [41050] * (Policy.DEFAULT_NUM_YEARS - 1)
    exp_almsep = np.array(exp_almsep_values)
    act_almsep = getattr(calc.policy, '_almsep')
    assert_allclose(act_almsep, exp_almsep, atol=0.01, rtol=0.0)


def test_make_Calculator_raises_on_no_policy():
    rec = Records(data=TAXDATA, weights=WEIGHTS, start_year=2013)
    with pytest.raises(ValueError):
        calc = Calculator(records=rec)


def test_Calculator_attr_access_to_policy():
    policy = Policy()
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    assert hasattr(calc.records, 'c01000')
    assert hasattr(calc.policy, '_AMT_Child_em')
    assert hasattr(calc, 'policy')


def test_Calculator_create_distribution_table():
    policy = Policy()
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    calc.calc_all()
    dist_labels = ['Returns', 'AGI', 'Standard Deduction Filers',
                   'Standard Deduction', 'Itemizers',
                   'Itemized Deduction', 'Personal Exemption',
                   'Taxable Income', 'Regular Tax', 'AMTI', 'AMT Filers',
                   'AMT', 'Tax before Credits', 'Non-refundable Credits',
                   'Tax before Refundable Credits', 'Refundable Credits',
                   'Individual Income Tax Liabilities',
                   'Payroll Tax Liablities',
                   'Combined Payroll and Individual Income Tax Liabilities']
    dt1 = create_distribution_table(calc, groupby="weighted_deciles",
                                    result_type="weighted_sum")
    dt1.columns = dist_labels
    dt2 = create_distribution_table(calc, groupby="small_income_bins",
                                    result_type="weighted_avg")
    assert isinstance(dt1, pd.DataFrame)
    assert isinstance(dt2, pd.DataFrame)


def test_Calculator_mtr():
    policy = Policy()
    puf = Records(TAXDATA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    (mtr_FICA, mtr_IIT, mtr) = calc.mtr()
    assert type(mtr) == np.ndarray
    assert np.array_equal(mtr, mtr_FICA) is False
    assert np.array_equal(mtr_FICA, mtr_IIT) is False


def test_Calculator_create_difference_table():
    # create current-law Policy object and use to create Calculator calc1
    policy1 = Policy()
    puf1 = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(policy=policy1, records=puf1)
    calc1.calc_all()
    # create policy-reform Policy object and use to create Calculator calc2
    policy2 = Policy()
    reform = {2013: {'_II_rt7': [0.45]}}
    policy2.implement_reform(reform)
    puf2 = Records(data=TAXDATA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(policy=policy2, records=puf2)
    # create difference table and check that it is a Pandas DataFrame
    dtable = create_difference_table(calc1, calc2, groupby="weighted_deciles")
    assert isinstance(dtable, pd.DataFrame)


def test_Calculator_diagnostic_table():
    policy = Policy()
    puf = Records(data=TAXDATA, weights=WEIGHTS, start_year=Records.PUF_YEAR)
    calc = Calculator(policy=policy, records=puf)
    calc.diagnostic_table()


def test_Calculator_diagnostic_table_no_mutation():
    policy_x = Policy()
    record_x = Records(data=TAXDATA, weights=WEIGHTS,
                       start_year=Records.PUF_YEAR)
    policy_y = Policy()
    record_y = Records(data=TAXDATA, weights=WEIGHTS,
                       start_year=Records.PUF_YEAR)
    calc_x = Calculator(policy=policy_x, records=record_x)
    calc_y = Calculator(policy=policy_y, records=record_y)
    x_start = calc_x.current_year
    y_start = calc_y.current_year
    calc_y.diagnostic_table(base_calc=calc_x)
    assert calc_y.current_year == y_start
    assert calc_x.current_year == x_start


def test_make_Calculator_increment_years_first():
    # create Policy object with custom indexing rates and policy reform
    irates = {2013: 0.01, 2014: 0.01, 2015: 0.02, 2016: 0.01, 2017: 0.03}
    policy = Policy(start_year=2013, inflation_rates=irates,
                    num_years=len(irates))
    reform = {2015: {}, 2016: {}}
    reform[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform[2015]['_II_em'] = [5000]
    reform[2016]['_II_em'] = [6000]
    reform[2016]['_II_em_cpi'] = False
    policy.implement_reform(reform)
    # create Records object by reading 1991 data and saying it is 2009 data
    puf = Records(TAXDATA, weights=WEIGHTS, start_year=2009)
    # create Calculator object with Policy object as modified by reform
    calc = Calculator(policy=policy, records=puf)
    # compare expected policy parameter values with those embedded in calc
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_allclose(calc.policy._STD_Aged, exp_STD_Aged, atol=0.5, rtol=0.0)
    assert_allclose(calc.policy._II_em, exp_II_em, atol=0.5, rtol=0.0)


def test_Calculator_using_nonstd_input(rawinputfile):
    # check Calculator handling of raw, non-standard input data with no aging
    policy = Policy()
    policy.set_year(RAWINPUTFILE_YEAR)  # set policy params to input data year
    nonpuf = Records(data=rawinputfile.name,
                     start_year=RAWINPUTFILE_YEAR,  # set raw input data year
                     consider_blowup=False)  # keeps raw data unchanged
    assert nonpuf.dim == RAWINPUTFILE_FUNITS
    calc = Calculator(policy=policy,
                      records=nonpuf,
                      sync_years=False)  # keeps raw data unchanged
    assert calc.current_year == RAWINPUTFILE_YEAR
    calc.calc_all()
    exp_iitax = np.zeros((nonpuf.dim,))
    assert_allclose(nonpuf._iitax, exp_iitax)
    mtr_fica, _, _ = calc.mtr(wrt_full_compensation=False)
    exp_mtr_fica = np.zeros((nonpuf.dim,))
    exp_mtr_fica.fill(0.153)
    assert_allclose(mtr_fica, exp_mtr_fica)


class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
