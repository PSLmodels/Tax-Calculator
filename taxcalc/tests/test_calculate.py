import os
import json
from io import StringIO
import tempfile
import copy
import six
import pytest
import numpy as np
import pandas as pd
from taxcalc import Policy, Records, Calculator, Behavior, Consumption
from taxcalc import create_distribution_table
from taxcalc import create_difference_table
from taxcalc import create_diagnostic_table


RAWINPUTFILE_FUNITS = 4
RAWINPUTFILE_YEAR = 2015
RAWINPUTFILE_CONTENTS = (
    'RECID,MARS\n'
    '1,2\n'
    '2,1\n'
    '3,4\n'
    '4,3\n'
)


@pytest.fixture(scope='module', name='rawinputfile')
def fixture_rawinputfile():
    """
    Temporary input file that contains the minimum required input varaibles.
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


@pytest.fixture(scope='module', name='policyfile')
def fixture_policyfile():
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


def test_make_Calculator(cps_subsample):
    parm = Policy(start_year=2014, num_years=9)
    assert parm.current_year == 2014
    recs = Records.cps_constructor(data=cps_subsample)
    consump = Consumption()
    consump.update_consumption({2014: {'_MPC_e20400': [0.05]}})
    assert consump.current_year == 2013
    calc = Calculator(policy=parm, records=recs, consumption=consump,
                      behavior=Behavior())
    assert calc.current_year == 2014
    # test incorrect Calculator instantiation:
    with pytest.raises(ValueError):
        calc = Calculator(policy=None, records=recs)
    with pytest.raises(ValueError):
        calc = Calculator(policy=parm, records=None)
    with pytest.raises(ValueError):
        calc = Calculator(policy=parm, records=recs, behavior=list())
    with pytest.raises(ValueError):
        calc = Calculator(policy=parm, records=recs, consumption=list())


def test_make_Calculator_deepcopy(cps_subsample):
    parm = Policy()
    recs = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=parm, records=recs)
    calc2 = copy.deepcopy(calc1)
    assert isinstance(calc2, Calculator)


def test_make_Calculator_with_policy_reform(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    year = recs.current_year
    # create a Policy object and apply a policy reform
    pol = Policy()
    reform = {2013: {'_II_em': np.array([4000]), '_II_em_cpi': False,
                     '_STD_Aged': [[1600, 1300, 1300, 1600, 1600]],
                     "_STD_Aged_cpi": False}}
    pol.implement_reform(reform)
    # create a Calculator object using this policy reform
    calc = Calculator(policy=pol, records=recs)
    # check that Policy object embedded in Calculator object is correct
    assert calc.current_year == year
    assert calc.policy.II_em == 4000
    assert np.allclose(calc.policy._II_em,
                       np.array([4000] * Policy.DEFAULT_NUM_YEARS))
    exp_STD_Aged = [[1600, 1300, 1300,
                     1600, 1600]] * Policy.DEFAULT_NUM_YEARS
    assert np.allclose(calc.policy._STD_Aged,
                       np.array(exp_STD_Aged))
    assert np.allclose(calc.policy.STD_Aged,
                       np.array([1600, 1300, 1300, 1600, 1600]))


def test_make_Calculator_with_multiyear_reform(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    year = recs.current_year
    # create a Policy object and apply a policy reform
    pol = Policy()
    reform = {2015: {}, 2016: {}}
    reform[2015]['_II_em'] = [5000, 6000]  # reform values for 2015 and 2016
    reform[2015]['_II_em_cpi'] = False
    reform[2016]['_STD_Aged'] = [[1600, 1300, 1600, 1300, 1600]]
    pol.implement_reform(reform)
    # create a Calculator object using this policy-reform
    calc = Calculator(policy=pol, records=recs)
    # check that Policy object embedded in Calculator object is correct
    assert calc.current_year == year
    assert calc.policy.II_em == 3950
    assert calc.policy.num_years == Policy.DEFAULT_NUM_YEARS
    exp_II_em = [3900, 3950, 5000] + [6000] * (Policy.DEFAULT_NUM_YEARS - 3)
    assert np.allclose(calc.policy._II_em,
                       np.array(exp_II_em))
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2016
    assert np.allclose(calc.policy.STD_Aged,
                       np.array([1600, 1300, 1600, 1300, 1600]))


def test_Calculator_advance_to_year(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc = Calculator(policy=pol, records=rec)
    calc.advance_to_year(2016)
    assert calc.current_year == 2016
    with pytest.raises(ValueError):
        calc.advance_to_year(2015)


def test_make_Calculator_raises_on_no_policy(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    with pytest.raises(ValueError):
        calc = Calculator(records=rec)


def test_Calculator_attr_access_to_policy(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    assert hasattr(calc.records, 'c01000')
    assert hasattr(calc.policy, '_AMT_Child_em')
    assert hasattr(calc, 'policy')


def test_Calculator_current_law_version(cps_subsample):
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    reform = {2013: {'_II_rt7': [0.45]}}
    pol.implement_reform(reform)
    calc = Calculator(policy=pol, records=rec)
    calc_clp = calc.current_law_version()
    assert isinstance(calc_clp, Calculator)
    assert calc.policy.II_rt6 == calc_clp.policy.II_rt6
    assert calc.policy.II_rt7 != calc_clp.policy.II_rt7


def test_Calculator_create_distribution_table(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
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
    dt1 = create_distribution_table(calc.records,
                                    groupby="weighted_deciles",
                                    income_measure='expanded_income',
                                    result_type="weighted_sum")
    dt1.columns = dist_labels
    dt2 = create_distribution_table(calc.records,
                                    groupby="small_income_bins",
                                    income_measure='expanded_income',
                                    result_type="weighted_avg")
    assert isinstance(dt1, pd.DataFrame)
    assert isinstance(dt2, pd.DataFrame)


def test_Calculator_mtr(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    recs_pre_e00200p = copy.deepcopy(calc.records.e00200p)
    (mtr_ptx, mtr_itx, mtr_combined) = calc.mtr(variable_str='e00200p',
                                                zero_out_calculated_vars=True)
    recs_post_e00200p = copy.deepcopy(calc.records.e00200p)
    assert np.allclose(recs_post_e00200p, recs_pre_e00200p)
    assert type(mtr_combined) == np.ndarray
    assert np.array_equal(mtr_combined, mtr_ptx) is False
    assert np.array_equal(mtr_ptx, mtr_itx) is False
    with pytest.raises(ValueError):
        (_, _, mtr_combined) = calc.mtr(variable_str='bad_income_type')
    (_, _, mtr_combined) = calc.mtr(variable_str='e00200s')
    assert type(mtr_combined) == np.ndarray
    (_, _, mtr_combined) = calc.mtr(variable_str='e00650',
                                    negative_finite_diff=True)
    assert type(mtr_combined) == np.ndarray
    (_, _, mtr_combined) = calc.mtr(variable_str='e00900p')
    assert type(mtr_combined) == np.ndarray
    (_, _, mtr_combined) = calc.mtr(variable_str='e01700')
    assert type(mtr_combined) == np.ndarray
    (_, _, mtr_combined) = calc.mtr(variable_str='e26270')
    assert type(mtr_combined) == np.ndarray


def test_Calculator_mtr_when_PT_rates_differ():
    reform = {2013: {'_II_rt1': [0.40],
                     '_II_rt2': [0.40],
                     '_II_rt3': [0.40],
                     '_II_rt4': [0.40],
                     '_II_rt5': [0.40],
                     '_II_rt6': [0.40],
                     '_II_rt7': [0.40],
                     '_PT_rt1': [0.30],
                     '_PT_rt2': [0.30],
                     '_PT_rt3': [0.30],
                     '_PT_rt4': [0.30],
                     '_PT_rt5': [0.30],
                     '_PT_rt6': [0.30],
                     '_PT_rt7': [0.30]}}
    funit = (
        u'RECID,MARS,FLPDYR,e00200,e00200p,e00900,e00900p,extraneous\n'
        u'1,    1,   2009,  200000,200000, 100000,100000, 9999999999\n'
    )
    pol1 = Policy()
    rec1 = Records(pd.read_csv(StringIO(funit)))
    calc1 = Calculator(policy=pol1, records=rec1)
    (_, mtr1, _) = calc1.mtr(variable_str='p23250')
    pol2 = Policy()
    pol2.implement_reform(reform)
    rec2 = Records(pd.read_csv(StringIO(funit)))
    calc2 = Calculator(policy=pol2, records=rec2)
    (_, mtr2, _) = calc2.mtr(variable_str='p23250')
    assert np.allclose(mtr1, mtr2, rtol=0.0, atol=1e-06)


def test_Calculator_create_difference_table(cps_subsample):
    # create current-law Policy object and use to create Calculator calc1
    cps1 = Records.cps_constructor(data=cps_subsample)
    year = cps1.current_year
    calc1 = Calculator(policy=Policy(), records=cps1)
    calc1.calc_all()
    # create policy-reform Policy object and use to create Calculator calc2
    policy2 = Policy()
    reform = {year: {'_II_rt7': [0.45]}}
    policy2.implement_reform(reform)
    cps2 = Records.cps_constructor(data=cps_subsample)
    calc2 = Calculator(policy=policy2, records=cps2)
    calc2.calc_all()
    # create difference table and check that it is a Pandas DataFrame
    dtable = create_difference_table(calc1.records, calc2.records,
                                     groupby='weighted_deciles',
                                     income_measure='expanded_income',
                                     tax_to_diff='payrolltax')
    assert isinstance(dtable, pd.DataFrame)


def test_Calculator_create_diagnostic_table(cps_subsample):
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    calc.calc_all()
    adt = create_diagnostic_table(calc)
    assert isinstance(adt, pd.DataFrame)


def test_make_Calculator_increment_years_first(cps_subsample):
    # create Policy object with policy reform
    syr = 2013
    pol = Policy(start_year=syr, num_years=5)
    reform = {2015: {}, 2016: {}}
    std5 = 2000
    reform[2015]['_STD_Aged'] = [[std5, std5, std5, std5, std5]]
    reform[2015]['_II_em'] = [5000]
    reform[2016]['_II_em'] = [6000]
    reform[2016]['_II_em_cpi'] = False
    pol.implement_reform(reform)
    # create Calculator object with Policy object as modified by reform
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=pol, records=recs)
    # compare expected policy parameter values with those embedded in calc
    irates = pol.inflation_rates()
    irate2015 = irates[2015 - syr]
    irate2016 = irates[2016 - syr]
    std6 = std5 * (1.0 + irate2015)
    std7 = std6 * (1.0 + irate2016)
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1500],
                             [1550, 1200, 1200, 1550, 1550],
                             [std5, std5, std5, std5, std5],
                             [std6, std6, std6, std6, std6],
                             [std7, std7, std7, std7, std7]])
    assert np.allclose(calc.policy._STD_Aged, exp_STD_Aged)
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    assert np.allclose(calc.policy._II_em, exp_II_em)


def test_ID_HC_vs_BS(cps_subsample):
    """
    Test that complete haircut of itemized deductions produces same
    results as a 100% benefit surtax with no benefit deduction.
    """
    # specify complete-haircut reform policy and Calculator object
    hc_reform = {2013: {'_ID_Medical_hc': [1.0],
                        '_ID_StateLocalTax_hc': [1.0],
                        '_ID_RealEstate_hc': [1.0],
                        '_ID_Casualty_hc': [1.0],
                        '_ID_Miscellaneous_hc': [1.0],
                        '_ID_InterestPaid_hc': [1.0],
                        '_ID_Charity_hc': [1.0]}}
    hc_policy = Policy()
    hc_policy.implement_reform(hc_reform)
    hc_recs = Records.cps_constructor(data=cps_subsample)
    hc_calc = Calculator(policy=hc_policy, records=hc_recs)
    # specify benefit-surtax reform policy and Calculator object
    bs_reform = {2013: {'_ID_BenefitSurtax_crt': [0.0],
                        '_ID_BenefitSurtax_trt': [1.0]}}
    bs_policy = Policy()
    bs_policy.implement_reform(bs_reform)
    bs_recs = Records.cps_constructor(data=cps_subsample)
    bs_calc = Calculator(policy=bs_policy, records=bs_recs)
    # compare calculated tax results generated by the two reforms
    hc_calc.calc_all()
    bs_calc.calc_all()
    assert np.allclose(hc_calc.records.payrolltax,
                       bs_calc.records.payrolltax)
    assert np.allclose(hc_calc.records.iitax,
                       bs_calc.records.iitax)


def test_Calculator_using_nonstd_input(rawinputfile):
    # check Calculator handling of raw, non-standard input data with no aging
    policy = Policy()
    policy.set_year(RAWINPUTFILE_YEAR)  # set policy params to input data year
    nonpuf = Records(data=rawinputfile.name,
                     gfactors=None,  # keeps raw data unchanged
                     weights=None,
                     start_year=RAWINPUTFILE_YEAR)  # set raw input data year
    assert nonpuf.dim == RAWINPUTFILE_FUNITS
    calc = Calculator(policy=policy,
                      records=nonpuf,
                      sync_years=False)  # keeps raw data unchanged
    assert calc.current_year == RAWINPUTFILE_YEAR
    calc.calc_all()
    exp_iitax = np.zeros((nonpuf.dim,))
    assert np.allclose(nonpuf.iitax, exp_iitax)
    mtr_ptax, _, _ = calc.mtr(wrt_full_compensation=False)
    exp_mtr_ptax = np.zeros((nonpuf.dim,))
    exp_mtr_ptax.fill(0.153)
    assert np.allclose(mtr_ptax, exp_mtr_ptax)


REFORM_CONTENTS = """
// Example of a reform file suitable for read_json_param_objects().
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within each "policy" object, the primary keys are parameters and
// the secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
// Parameter code in the policy object is enclosed inside a pair of double
// pipe characters (||).
{
  "policy": {
    "_AMT_brk1": // top of first AMT tax bracket
    {"2015": [200000],
     "2017": [300000]
    },
    "_EITC_c": // maximum EITC amount by number of qualifying kids (0,1,2,3+)
    {"2016": [[ 900, 5000,  8000,  9000]],
     "2019": [[1200, 7000, 10000, 12000]]
    },
    "_II_em": // personal exemption amount (see indexing changes below)
    {"2016": [6000],
     "2018": [7500],
     "2020": [9000]
    },
    "_II_em_cpi": // personal exemption amount indexing status
    {"2016": false, // values in future years are same as this year value
     "2018": true   // values in future years indexed with this year as base
    },
    "_SS_Earnings_c": // social security (OASDI) maximum taxable earnings
    {"2016": [300000],
     "2018": [500000],
     "2020": [700000]
    },
    "_AMT_em_cpi": // AMT exemption amount indexing status
    {"2017": false, // values in future years are same as this year value
     "2020": true   // values in future years indexed with this year as base
    }
  }
}
"""


@pytest.fixture(scope='module', name='reform_file')
def fixture_reform_file():
    """
    Temporary reform file for read_json_param_objects() function.
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(REFORM_CONTENTS)
    rfile.close()
    # must close and then yield for Windows platform
    yield rfile
    if os.path.isfile(rfile.name):
        try:
            os.remove(rfile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


ASSUMP_CONTENTS = """
// Example of assump file suitable for the read_json_param_objects().
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within each "behavior", "consumption" and "growth" object, the
// primary keys are parameters and the secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
  "consumption": { "_MPC_e18400": {"2018": [0.05]} },
  "behavior": {},
  "growdiff_baseline": {},
  "growdiff_response": {}
}
"""


@pytest.fixture(scope='module', name='assump_file')
def fixture_assump_file():
    """
    Temporary assumption file for read_json_params_files() function.
    """
    afile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    afile.write(ASSUMP_CONTENTS)
    afile.close()
    # must close and then yield for Windows platform
    yield afile
    if os.path.isfile(afile.name):
        try:
            os.remove(afile.name)
        except OSError:
            pass  # sometimes we can't remove a generated temporary file


def test_read_json_reform_file_two_ways(reform_file, assump_file):
    """
    Test when using filename/contents in read_json_param_objects()
    """
    pd1 = Calculator.read_json_param_objects(reform_file.name,
                                             assump_file.name,
                                             arrays_not_lists=False)
    pd2 = Calculator.read_json_param_objects(REFORM_CONTENTS,
                                             ASSUMP_CONTENTS,
                                             arrays_not_lists=False)
    assert pd1 == pd2


@pytest.mark.parametrize("set_year", [False, True])
def test_read_json_reform_file_and_implement_reform(reform_file,
                                                    assump_file,
                                                    set_year):
    """
    Test reading and translation of reform file into a reform dictionary
    that is then used to call implement_reform method and Calculate.calc_all()
    NOTE: implement_reform called when policy.current_year == policy.start_year
    """
    policy = Policy()
    if set_year:
        policy.set_year(2015)
    param_dict = Calculator.read_json_param_objects(reform_file.name,
                                                    assump_file.name)
    policy.implement_reform(param_dict['policy'])
    syr = policy.start_year
    amt_brk1 = policy._AMT_brk1
    assert amt_brk1[2015 - syr] == 200000
    assert amt_brk1[2016 - syr] > 200000
    assert amt_brk1[2017 - syr] == 300000
    assert amt_brk1[2018 - syr] > 300000
    ii_em = policy._II_em
    assert ii_em[2016 - syr] == 6000
    assert ii_em[2017 - syr] == 6000
    assert ii_em[2018 - syr] == 7500
    assert ii_em[2019 - syr] > 7500
    assert ii_em[2020 - syr] == 9000
    assert ii_em[2021 - syr] > 9000
    amt_em = policy._AMT_em
    assert amt_em[2016 - syr, 0] > amt_em[2015 - syr, 0]
    assert amt_em[2017 - syr, 0] > amt_em[2016 - syr, 0]
    assert amt_em[2018 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2019 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2020 - syr, 0] == amt_em[2017 - syr, 0]
    assert amt_em[2021 - syr, 0] > amt_em[2020 - syr, 0]
    assert amt_em[2022 - syr, 0] > amt_em[2021 - syr, 0]
    add4aged = policy._ID_Medical_frt_add4aged
    assert add4aged[2015 - syr] == -0.025
    assert add4aged[2016 - syr] == -0.025
    assert add4aged[2017 - syr] == 0.0
    assert add4aged[2022 - syr] == 0.0


@pytest.fixture(scope='module', name='bad1reformfile')
def fixture_bad1reformfile():
    # specify JSON text for reform
    txt = """
    {
      "policy": { // example of incorrect JSON because 'x' must be "x"
        'x': {"2014": [4000]}
      }
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.fixture(scope='module', name='bad2reformfile')
def fixture_bad2reformfile():
    # specify JSON text for reform
    txt = """
    {
      "title": "",
      "policyx": { // example of reform file not containing "policy" key
        "_SS_Earnings_c": {"2018": [9e99]}
      }
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.fixture(scope='module', name='bad3reformfile')
def fixture_bad3reformfile():
    # specify JSON text for reform
    txt = """
    {
      "title": "",
      "policy": {
        "_SS_Earnings_c": {"2018": [9e99]}
      },
      "behavior": { // example of misplaced "behavior" key
      }
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_read_bad_json_reform_file(bad1reformfile, bad2reformfile,
                                   bad3reformfile):
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(bad1reformfile.name, None)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(bad2reformfile.name, None)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(bad3reformfile.name, None)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(list(), None)


@pytest.fixture(scope='module', name='bad1assumpfile')
def fixture_bad1assumpfile():
    # specify JSON text for assumptions
    txt = """
    {
      "consumption": {},
      "behavior": { // example of incorrect JSON because 'x' must be "x"
        'x': {"2014": [0.25]}
      },
      "growdiff_baseline": {},
      "growdiff_response": {}
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.fixture(scope='module', name='bad2assumpfile')
def fixture_bad2assumpfile():
    # specify JSON text for assumptions
    txt = """
    {
      "consumption": {},
      "behaviorx": {}, // example of assump file not containing "behavior" key
      "growdiff_baseline": {},
      "growdiff_response": {}
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.fixture(scope='module', name='bad3assumpfile')
def fixture_bad3assumpfile():
    # specify JSON text for assump
    txt = """
    {
      "consumption": {},
      "behavior": {},
      "growdiff_baseline": {},
      "growdiff_response": {},
      "policy": { // example of misplaced policy key
        "_SS_Earnings_c": {"2018": [9e99]}
      }
    }
    """
    f = tempfile.NamedTemporaryFile(mode='a', delete=False)
    f.write(txt + '\n')
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_read_bad_json_assump_file(bad1assumpfile, bad2assumpfile,
                                   bad3assumpfile):
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, bad1assumpfile.name)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, bad2assumpfile.name)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, bad3assumpfile.name)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, 'unknown_file_name')
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, list())


def test_convert_parameter_dict():
    with pytest.raises(ValueError):
        rdict = Calculator._convert_parameter_dict({2013: {'2013': [40000]}},
                                                   arrays_not_lists=True)
    with pytest.raises(ValueError):
        rdict = Calculator._convert_parameter_dict({'_II_em': {2013: [40000]}},
                                                   arrays_not_lists=True)
    with pytest.raises(ValueError):
        rdict = Calculator._convert_parameter_dict({4567: {2013: [40000]}},
                                                   arrays_not_lists=True)
    with pytest.raises(ValueError):
        rdict = Calculator._convert_parameter_dict({'_II_em': 40000},
                                                   arrays_not_lists=True)
    rdict = Calculator._convert_parameter_dict({'_II_em': {'2013': [40000]}},
                                               arrays_not_lists=False)
    assert isinstance(rdict, dict)


def test_calc_all(reform_file, rawinputfile):
    cyr = 2016
    policy = Policy()
    param_dict = Calculator.read_json_param_objects(reform_file.name, None)
    policy.implement_reform(param_dict['policy'])
    policy.set_year(cyr)
    nonpuf = Records(data=rawinputfile.name, gfactors=None,
                     weights=None, start_year=cyr)
    assert nonpuf.dim == RAWINPUTFILE_FUNITS
    calc = Calculator(policy=policy,
                      records=nonpuf,
                      sync_years=False)  # keeps raw data unchanged
    assert calc.current_year == cyr
    calc.calc_all()


def test_translate_json_reform_suffixes_mars_indexed():
    # test read_json_param_objects()
    # using MARS-indexed parameter suffixes
    json1 = """{"policy": {
      "_II_em": {"2020": [20000], "2015": [15000]},
      "_STD_single": {"2018": [18000], "2016": [16000]},
      "_STD_widow": {"2017": [17000], "2019": [19000]}
    }}"""
    assump_json = """{
      "consumption": {},
      "behavior": {},
      "growdiff_baseline": {
        "_ACPIU": {"2013": [0.01]},
        "_AWAGE": {"2013": [0.01]}},
      "growdiff_response": {}
    }"""
    pdict1 = Calculator.read_json_param_objects(reform=json1,
                                                assump=assump_json,
                                                arrays_not_lists=True)
    rdict1 = pdict1['policy']
    json2 = """{"policy": {
      "_STD": {"2016": [[16000.00, 12600.00, 6300.00,  9300.00, 12600.00]],
               "2017": [[16524.80, 13013.28, 6506.64,  9605.04, 17000.00]],
               "2018": [[18000.00, 13432.31, 6716.15,  9914.32, 17547.40]],
               "2019": [[18592.20, 13874.23, 6937.11, 10240.50, 19000.00]]},
      "_II_em": {"2020": [20000], "2015": [15000]}
    }}"""
    pdict2 = Calculator.read_json_param_objects(reform=json2,
                                                assump=assump_json,
                                                arrays_not_lists=True)
    rdict2 = pdict2['policy']
    assert len(rdict2) == len(rdict1)
    for year in rdict2.keys():
        if '_II_em' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_II_em'],
                               rdict2[year]['_II_em'],
                               atol=0.01, rtol=0.0)
        if '_STD' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_STD'],
                               rdict2[year]['_STD'],
                               atol=0.01, rtol=0.0)


def test_translate_json_reform_suffixes_mars_non_indexed():
    # test read_json_param_objects()
    # using MARS-indexed parameter suffixes
    json1 = """{"policy": {
      "_II_em": {"2020": [20000], "2015": [15000]},
      "_AMEDT_ec_joint": {"2018": [400000], "2016": [300000]},
      "_AMEDT_ec_separate": {"2017": [150000], "2019": [200000]}
    }}"""
    pdict1 = Calculator.read_json_param_objects(reform=json1,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict1 = pdict1['policy']
    json2 = """{"policy": {
      "_AMEDT_ec": {"2016": [[200000, 300000, 125000, 200000, 200000]],
                    "2017": [[200000, 300000, 150000, 200000, 200000]],
                    "2018": [[200000, 400000, 150000, 200000, 200000]],
                    "2019": [[200000, 400000, 200000, 200000, 200000]]},
      "_II_em": {"2015": [15000], "2020": [20000]}
    }}"""
    pdict2 = Calculator.read_json_param_objects(reform=json2,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict2 = pdict2['policy']
    assert len(rdict2) == len(rdict1)
    for year in rdict2.keys():
        if '_II_em' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_II_em'],
                               rdict2[year]['_II_em'],
                               atol=0.01, rtol=0.0)
        if '_AMEDT_ec' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_AMEDT_ec'],
                               rdict2[year]['_AMEDT_ec'],
                               atol=0.01, rtol=0.0)


def test_translate_json_reform_suffixes_eic():
    # test read_json_param_objects(...)
    # using EIC-indexed parameter suffixes
    json1 = """{"policy": {
      "_II_em": {"2020": [20000], "2015": [15000]},
      "_EITC_c_0kids": {"2018": [510], "2019": [510]},
      "_EITC_c_1kid": {"2019": [3400], "2018": [3400]},
      "_EITC_c_2kids": {"2018": [5616], "2019": [5616]},
      "_EITC_c_3+kids": {"2019": [6318], "2018": [6318]}
    }}"""
    pdict1 = Calculator.read_json_param_objects(reform=json1,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict1 = pdict1['policy']
    json2 = """{"policy": {
      "_EITC_c": {"2019": [[510, 3400, 5616, 6318]],
                  "2018": [[510, 3400, 5616, 6318]]},
      "_II_em": {"2020": [20000], "2015": [15000]}
    }}"""
    pdict2 = Calculator.read_json_param_objects(reform=json2,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict2 = pdict2['policy']
    assert len(rdict2) == len(rdict1)
    for year in rdict2.keys():
        if '_II_em' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_II_em'],
                               rdict2[year]['_II_em'],
                               atol=0.01, rtol=0.0)
        if '_EITC_c' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_EITC_c'],
                               rdict2[year]['_EITC_c'],
                               atol=0.01, rtol=0.0)


def test_translate_json_reform_suffixes_idedtype():
    # test read_json_param_objects(...)
    # using idedtype-indexed parameter suffixes
    json1 = """{"policy": {
      "_ID_BenefitCap_rt": {"2019": [0.2]},
      "_ID_BenefitCap_Switch_medical": {"2019": [false]},
      "_ID_BenefitCap_Switch_casualty": {"2019": [false]},
      "_ID_BenefitCap_Switch_misc": {"2019": [false]},
      "_ID_BenefitCap_Switch_interest": {"2019": [false]},
      "_ID_BenefitCap_Switch_charity": {"2019": [false]},
      "_II_em": {"2020": [20000], "2015": [15000]}
    }}"""
    pdict1 = Calculator.read_json_param_objects(reform=json1,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict1 = pdict1['policy']
    json2 = """{"policy": {
      "_II_em": {"2020": [20000], "2015": [15000]},
      "_ID_BenefitCap_Switch": {
        "2019": [[false, true, true, false, false, false, false]]
      },
      "_ID_BenefitCap_rt": {"2019": [0.2]}
    }}"""
    pdict2 = Calculator.read_json_param_objects(reform=json2,
                                                assump=None,
                                                arrays_not_lists=True)
    rdict2 = pdict2['policy']
    assert len(rdict2) == len(rdict1)
    for year in rdict2.keys():
        if '_II_em' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_II_em'],
                               rdict2[year]['_II_em'],
                               atol=0.01, rtol=0.0)
        if '_ID_BenefitCap_rt' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_ID_BenefitCap_rt'],
                               rdict2[year]['_ID_BenefitCap_rt'],
                               atol=0.01, rtol=0.0)
        if '_ID_BenefitCap_Switch' in rdict2[year].keys():
            assert np.allclose(rdict1[year]['_ID_BenefitCap_Switch'],
                               rdict2[year]['_ID_BenefitCap_Switch'],
                               atol=0.01, rtol=0.0)


def test_read_json_param_with_suffixes_and_errors():
    # test interaction of policy parameter suffixes and reform errors
    # (fails without 0.10.2 bug fix as reported by Hank Doupe in PB PR#641)
    reform = {
        u'policy': {
            u'_II_brk4_separate': {u'2017': [5000.0]},
            u'_STD_separate': {u'2017': [8000.0]},
            u'_STD_single': {u'2018': [1000.0]},
            u'_II_brk2_headhousehold': {u'2017': [1000.0]},
            u'_II_brk4_single': {u'2017': [500.0]},
            u'_STD_joint': {u'2017': [10000.0], u'2020': [150.0]},
            u'_II_brk2_separate': {u'2017': [1000.0]},
            u'_II_brk2_single': {u'2017': [1000.0]},
            u'_II_brk2_joint': {u'2017': [1000.0]},
            u'_FICA_ss_trt': {u'2017': [-1.0], u'2019': [0.1]},
            u'_II_brk4_headhousehold': {u'2017': [500.0]},
            u'_STD_headhousehold': {u'2017': [10000.0], u'2020': [150.0]},
            u'_II_brk4_joint': {u'2017': [500.0]},
            u'_ID_BenefitSurtax_Switch_medical': {u'2017': [True]}
        }
    }
    json_reform = json.dumps(reform)
    params = Calculator.read_json_param_objects(json_reform, None)
    assert isinstance(params, dict)
    pol = Policy()
    pol.implement_reform(params['policy'])
    assert len(pol.reform_errors) > 0
    assert len(pol.reform_warnings) > 0

@pytest.mark.one
def test_create_reform_documentation():
    reform_json = """
    {"policy": {
       "_II_em": {"2018": [4000],
                  "2020": [5000],
                  "2022": [6000]},
       "_II_em_cpi": {"2018": false,
                      "2020": true},
       "_STD_Aged": {"2018": [[1600, 1300, 1300, 1600, 1600]]},
       "_STD_Aged_cpi": {"2018": false}
    }}
    """
    assump_json = """
    {
    "consumption": {},
    "behavior": {},
    // increase baseline inflation rate by one percentage beginning in 2014
    "growdiff_baseline": {"_ACPIU": {"2014": [0.01]}},
    "growdiff_response": {}
    }
    """
    params = Calculator.read_json_param_objects(reform_json, assump_json,
                                                arrays_not_lists=False)
    assert isinstance(params, dict)
    doc = Calculator.create_reform_documentation(params)
    assert isinstance(doc, six.string_types)
    assert doc == ''  # TODO: complete test
