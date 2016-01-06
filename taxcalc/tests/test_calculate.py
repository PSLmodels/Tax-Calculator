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
from taxcalc import Policy, Records, Calculator, Growth
from taxcalc import create_distribution_table, create_difference_table


# use 1991 PUF-like data to emulate current PUF, which is private
TAX_DTA_PATH = os.path.join(CUR_PATH, '../../tax_all1991_puf.gz')
TAX_DTA = pd.read_csv(TAX_DTA_PATH, compression='gzip')
# PUF-fix-up: MIdR needs to be type int64 to match PUF
TAX_DTA['MIDR'] = TAX_DTA['MIDR'].astype('int64')
# specify WEIGHTS appropriate for 1991 data
WEIGHTS_FILENAME = '../../WEIGHTS_testing.csv'
WEIGHTS_PATH = os.path.join(CUR_PATH, WEIGHTS_FILENAME)
WEIGHTS = pd.read_csv(WEIGHTS_PATH)

IRATES = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024, 2003: 0.024, 2004: 0.024}

WRATES = {1991: 0.0276, 1992: 0.0419, 1993: 0.0465, 1994: 0.0498,
          1995: 0.0507, 1996: 0.0481, 1997: 0.0451, 1998: 0.0441,
          1999: 0.0437, 2000: 0.0435, 2001: 0.0430, 2002: 0.0429,
          2003: 0.0429, 2004: 0.0429}


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


def run():
    parm = Policy()
    assert parm.current_year == 2013
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=parm, records=recs)
    assert calc.current_year == 2013
    calc.calc_all()
    rshape = calc.records.e00100.shape
    totaldf = pd.DataFrame()
    for attr in dir(calc.records):
        value = getattr(calc.records, attr)
        if hasattr(value, "shape"):
            if (value.shape == rshape):
                totaldf[attr] = value
    Col_names = ['EICYB1', 'EICYB2', 'EICYB3', 'NIIT', '_addamt', '_addtax',
                 '_agep', '_ages', '_agierr', '_alminc', '_amed', '_amt15pc',
                 '_amt20pc', '_amt25pc', '_amt5pc', '_amtfei', '_amtsepadd',
                 '_amtstd', '_avail', '_cglong', '_cmbtp', '_comb',
                 '_combined', '_ctc1', '_ctc2', '_ctcagi', '_ctctax', '_dclim',
                 '_dwks12', '_dwks16', '_dwks17', '_dwks21', '_dwks25',
                 '_dwks26', '_dwks28', '_dwks31', '_dwks5', '_dwks9', '_dy',
                 '_earned', '_eitc', '_exocrd', '_expanded_income', '_feided',
                 '_feitax', '_fica', '_hasgain', '_ieic', 'c03260',
                 '_limitratio', '_line17', '_line19', '_line22', '_line30',
                 '_line31', '_line32', '_line33', '_line34', '_line35',
                 '_line36', '_modagi', '_nctcr', '_ncu13', '_ngamty', '_noncg',
                 '_nonlimited', '_num', '_numextra', '_oldfei', '_othadd',
                 '_othded', '_othertax', '_othtax', '_parents', '_phase2_i',
                 '_posagi', '_precrd', '_preeitc', '_prexmp', '_refund',
                 '_regcrd', '_s1291', '_sep', '_sey', 'c09400', 'c03260',
                 '_seywage', '_standard', '_statax', '_tamt2', '_taxbc',
                 '_taxinc', '_taxspecial', '_tratio', '_txpyers',
                 '_val_rtbase', '_val_rtless', '_val_ymax', '_xyztax', '_ymod',
                 '_ymod1', '_ymod2', '_ymod3', '_ywossbc', '_ywossbe',
                 'c00100', 'c01000', 'c02500', 'c02650', 'c02700', 'c02900',
                 'c04100', 'c04200', 'c04470', 'c04500', 'c04600', 'c04800',
                 'c05100', 'c05200', 'c05700', 'c05750', 'c05800', 'c07100',
                 'c07150', 'c07180', 'c07220', 'c07230', 'c07240', 'c07300',
                 'c07600', 'c07970', 'c08795', 'c08800', 'c09200', 'c09600',
                 'c10300', 'c10950', 'c10960', 'c11055', 'c11070', 'c15100',
                 'c15200', 'c17000', 'c17750', 'c18300', 'c19200', 'c19700',
                 'c20400', 'c20500', 'c20750', 'c20800', 'c21040', 'c21060',
                 'c23650', 'c24505', 'c24510', 'c24516', 'c24517', 'c24520',
                 'c24530', 'c24534', 'c24540', 'c24550', 'c24560', 'c24570',
                 'c24580', 'c24597', 'c24598', 'c24610', 'c24615', 'c32800',
                 'c32840', 'c32880', 'c32890', 'c33000', 'c33200', 'c33400',
                 'c33465', 'c33470', 'c33475', 'c33480', 'c37703', 'c59430',
                 'c59450', 'c59460', 'c59485', 'c59490', 'c59560', 'c59660',
                 'c59680', 'c59700', 'c59720', 'c60000', 'c60130', 'c60200',
                 'c60220', 'c60240', 'c60260', 'c62100', 'c62100_everyone',
                 'c62600', 'c62700', 'c62720', 'c62730', 'c62740', 'c62745',
                 'c62747', 'c62755', 'c62760', 'c62770', 'c62780', 'c62800',
                 'c62900', 'c63000', 'c63100', 'c82880', 'c82885', 'c82890',
                 'c82900', 'c82905', 'c82910', 'c82915', 'c82920', 'c82925',
                 'c82930', 'c82935', 'c82937', 'c82940', 'c87482', 'c87483',
                 'c87487', 'c87488', 'c87492', 'c87493', 'c87497', 'c87498',
                 'c87521', 'c87530', 'c87540', 'c87550', 'c87560', 'c87570',
                 'c87580', 'c87590', 'c87600', 'c87610', 'c87620', 'c87654',
                 'c87656', 'c87658', 'c87660', 'c87662', 'c87664', 'c87666',
                 'c87668', 'c87681', 'e00650', 'e02500', 'e08795', 'h82880',
                 'x04500', 'x07100', 'y07100', 'y62745']
    df = totaldf[Col_names]
    exp_results_file = os.path.join(CUR_PATH, '../../exp_results.csv.gz')
    exp_results = pd.read_csv(exp_results_file, compression='gzip')
    exp_set = set(exp_results.columns)  # fix-up to bad colname in exp_results
    cur_set = set(df.columns)

    assert(exp_set == cur_set)

    for label in exp_results.columns:
        lhs = exp_results[label].values.reshape(len(exp_results))
        rhs = totaldf[label].values.reshape(len(exp_results))
        res = np.allclose(lhs, rhs, atol=1e-02)
        if not res:
            print('Problem found in: ', label)


def test_sequence():
    run()


def test_make_Calculator():
    parm = Policy()
    assert parm.current_year == 2013
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=parm, records=recs)
    assert calc.current_year == 2013


def test_make_Calculator_deepcopy():
    import copy
    parm = Policy()
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
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
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(policy=policy2, records=puf)
    # check that Policy object embedded in Calculator object is correct
    assert calc2.current_year == 2013
    assert calc2.policy.II_em == 4000
    assert_array_equal(calc2.policy._II_em,
                       np.array([4000] * policy2.DEFAULT_NUM_YEARS))
    exp_STD_Aged = [[1600, 1300, 1300,
                     1600, 1600, 1300]] * policy2.DEFAULT_NUM_YEARS
    assert_array_equal(calc2.policy._STD_Aged, np.array(exp_STD_Aged))
    assert_array_equal(calc2.policy.STD_Aged,
                       np.array([1600, 1300, 1300, 1600, 1600, 1300]))


def test_make_Calculator_with_multiyear_reform():
    # create a Policy object and apply a policy reform
    policy3 = Policy()
    reform3 = {2015: {}}
    reform3[2015]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600, 1300]]
    reform3[2015]['_II_em'] = [5000, 6000]  # reform values for 2015 and 2016
    reform3[2015]['_II_em_cpi'] = False
    policy3.implement_reform(reform3)
    # create a Calculator object using this policy-reform
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc3 = Calculator(policy=policy3, records=puf)
    # check that Policy object embedded in Calculator object is correct
    assert calc3.current_year == 2013
    assert calc3.policy.II_em == 3900
    assert calc3.policy.num_years == policy3.DEFAULT_NUM_YEARS
    exp_II_em = [3900, 3950, 5000] + [6000] * (policy3.DEFAULT_NUM_YEARS - 3)
    assert_array_equal(calc3.policy._II_em, np.array(exp_II_em))
    calc3.increment_year()
    calc3.increment_year()
    assert calc3.current_year == 2015
    assert_array_equal(calc3.policy.STD_Aged,
                       np.array([1600, 1300, 1600, 1300, 1600, 1300]))


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
    recs = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=parm, records=recs)
    # compare actual and expected parameter values over all years
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_array_equal(calc.policy._STD_Aged, exp_STD_Aged)
    assert_array_equal(calc.policy._II_em, exp_II_em)
    # compare actual and expected values for 2015
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2015
    exp_2015_II_em = 5000
    assert_array_equal(calc.policy.II_em, exp_2015_II_em)
    exp_2015_STD_Aged = np.array([1600, 1300, 1600, 1300, 1600, 1300])
    assert_array_equal(calc.policy.STD_Aged, exp_2015_STD_Aged)


def test_make_Calculator_user_mods_with_cpi_flags(policyfile):
    with open(policyfile.name) as pfile:
        policy = json.load(pfile)
    ppo = Policy(parameter_dict=policy, start_year=1991,
                 num_years=len(IRATES), inflation_rates=IRATES,
                 wage_growth_rates=WRATES)
    rec = Records(data=TAX_DTA, start_year=1991)
    calc = Calculator(policy=ppo, records=rec)
    user_mods = {1991: {"_almdep": [7150, 7250, 7400],
                        "_almdep_cpi": True,
                        "_almsep": [40400, 41050],
                        "_almsep_cpi": False,
                        "_rt5": [0.33],
                        "_rt7": [0.396]}}
    calc.policy.implement_reform(user_mods)
    # compare actual and expected values
    inf_rates = [IRATES[1991 + i] for i in range(0, ppo.DEFAULT_NUM_YEARS)]
    exp_almdep = Policy.expand_array(np.array([7150, 7250, 7400]),
                                     inflate=True,
                                     inflation_rates=inf_rates,
                                     num_years=ppo.DEFAULT_NUM_YEARS)
    act_almdep = getattr(calc.policy, '_almdep')
    assert_array_equal(act_almdep, exp_almdep)
    exp_almsep_values = [40400] + [41050] * (ppo.DEFAULT_NUM_YEARS - 1)
    exp_almsep = np.array(exp_almsep_values)
    act_almsep = getattr(calc.policy, '_almsep')
    assert_array_equal(act_almsep, exp_almsep)


def test_make_Calculator_raises_on_no_policy():
    rec = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2013)
    with pytest.raises(ValueError):
        calc = Calculator(records=rec)


def test_Calculator_attr_access_to_policy():
    policy = Policy()
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    assert hasattr(calc.records, 'c01000')
    assert hasattr(calc.policy, '_AMT_Child_em')
    assert hasattr(calc, 'policy')


def test_Calculator_create_distribution_table():
    policy = Policy()
    puf = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
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


def test_calculate_mtr():
    policy = Policy()
    puf = Records(TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc = Calculator(policy=policy, records=puf)
    (mtr_FICA, mtr_IIT, mtr) = calc.mtr()
    assert type(mtr) == np.ndarray
    assert np.array_equal(mtr, mtr_FICA) == False
    assert np.array_equal(mtr_FICA, mtr_IIT) == False


def test_Calculator_create_difference_table():
    # create current-law Policy object and use to create Calculator calc1
    policy1 = Policy()
    puf1 = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc1 = Calculator(policy=policy1, records=puf1)
    calc1.calc_all()
    # create policy-reform Policy object and use to create Calculator calc2
    policy2 = Policy()
    reform = {2013: {'_II_rt7': [0.45]}}
    policy2.implement_reform(reform)
    puf2 = Records(data=TAX_DTA, weights=WEIGHTS, start_year=2009)
    calc2 = Calculator(policy=policy2, records=puf2)
    # create difference table and check that it is a Pandas DataFrame
    dtable = create_difference_table(calc1, calc2, groupby="weighted_deciles")
    assert isinstance(dtable, pd.DataFrame)


def test_diagnostic_table():
    policy = Policy()
    TAX_DTA.FLPDYR += 18  # flpdyr==2009 so that Records ctor will apply blowup
    puf = Records(data=TAX_DTA, weights=WEIGHTS)
    calc = Calculator(policy=policy, records=puf)
    calc.diagnostic_table()


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
    puf = Records(TAX_DTA, weights=WEIGHTS, start_year=2009)
    # create Calculator object with Policy object as modified by reform
    calc = Calculator(policy=policy, records=puf)
    # compare expected policy parameter values with those embedded in calc
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1550, 1200],
                             [1600, 1300, 1600, 1300, 1600, 1300],
                             [1632, 1326, 1632, 1326, 1632, 1326],
                             [1648, 1339, 1648, 1339, 1648, 1339]])
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert_array_equal(calc.policy._STD_Aged, exp_STD_Aged)
    assert_array_equal(calc.policy._II_em, exp_II_em)


class TaxCalcError(Exception):
    '''I've stripped this down to a simple extension of the basic Exception for
    now. We can add functionality later as we see fit.
    '''
    pass
