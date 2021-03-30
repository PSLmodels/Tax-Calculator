"""
Tests of Calculator class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_calculator.py
# pylint --disable=locally-disabled test_calculator.py
#
# pylint: disable=too-many-lines,invalid-name

import os
from io import StringIO
import copy
import pytest
import numpy as np
import pandas as pd
from taxcalc import Policy, Records, Calculator, Consumption


def test_make_calculator(cps_subsample):
    """
    Test Calculator class ctor.
    """
    start_year = Policy.JSON_START_YEAR
    sim_year = 2018
    pol = Policy()
    assert pol.current_year == start_year
    rec = Records.cps_constructor(data=cps_subsample)
    consump = Consumption()
    consump.update_consumption({'MPC_e20400': {sim_year: 0.05}})
    assert consump.current_year == start_year
    calc = Calculator(policy=pol, records=rec,
                      consumption=consump, verbose=True)
    assert calc.data_year == Records.CPSCSV_YEAR
    assert calc.current_year == Records.CPSCSV_YEAR
    # test incorrect Calculator instantiation:
    with pytest.raises(ValueError):
        Calculator(policy=None, records=rec)
    with pytest.raises(ValueError):
        Calculator(policy=pol, records=None)
    with pytest.raises(ValueError):
        Calculator(policy=pol, records=rec, consumption=list())


def test_make_calculator_deepcopy(cps_subsample):
    """
    Test deepcopy of Calculator object.
    """
    pol = Policy()
    rec = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=pol, records=rec)
    calc2 = copy.deepcopy(calc1)
    assert isinstance(calc2, Calculator)


def test_make_calculator_with_policy_reform(cps_subsample):
    """
    Test Calculator class ctor with policy reform.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    year = rec.current_year
    # create a Policy object and apply a policy reform
    pol = Policy()
    reform = {
        'II_em': {2011: 4000},
        'II_em-indexed': {2011: False},
        'STD_Aged': {2011: [1600, 1300, 1300, 1600, 1600]},
        'STD_Aged-indexed': {2011: False}
    }
    pol.implement_reform(reform)
    # create a Calculator object using this policy reform
    calc = Calculator(policy=pol, records=rec)
    assert calc.reform_warnings == ''
    # check that Policy object embedded in Calculator object is correct
    assert calc.current_year == year
    assert calc.policy_param('II_em') == 4000
    assert np.allclose(calc.policy_param('_II_em'),
                       np.array([4000] * Policy.DEFAULT_NUM_YEARS))
    exp_STD_Aged = [[1600, 1300, 1300,
                     1600, 1600]] * Policy.DEFAULT_NUM_YEARS
    assert np.allclose(calc.policy_param('_STD_Aged'),
                       np.array(exp_STD_Aged))
    assert np.allclose(calc.policy_param('STD_Aged'),
                       np.array([1600, 1300, 1300, 1600, 1600]))


def test_make_calculator_with_multiyear_reform(cps_subsample):
    """
    Test Calculator class ctor with multi-year policy reform.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    year = rec.current_year
    # create a Policy object and apply a policy reform
    pol = Policy()
    reform = {
        'II_em': {2015: 5000, 2016: 6000},
        'II_em-indexed': {2015: False},
        'STD_Aged': {2016: [1600, 1300, 1600, 1300, 1600]}
    }
    pol.implement_reform(reform)
    # create a Calculator object using this policy-reform
    calc = Calculator(policy=pol, records=rec)
    # check that Policy object embedded in Calculator object is correct
    assert pol.num_years == Policy.DEFAULT_NUM_YEARS
    assert calc.current_year == year
    assert calc.policy_param('II_em') == 3950
    exp_II_em = ([3700, 3800, 3900, 3950, 5000] + [6000] *
                 (Policy.DEFAULT_NUM_YEARS - 5))
    assert np.allclose(calc.policy_param('_II_em'),
                       np.array(exp_II_em))
    calc.increment_year()
    calc.increment_year()
    assert calc.current_year == 2016
    assert np.allclose(calc.policy_param('STD_Aged'),
                       np.array([1600, 1300, 1600, 1300, 1600]))


def test_calculator_advance_to_year(cps_subsample):
    """
    Test Calculator advance_to_year method.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc = Calculator(policy=pol, records=rec)
    calc.advance_to_year(2016)
    assert calc.current_year == 2016
    with pytest.raises(ValueError):
        calc.advance_to_year(2015)


def test_make_calculator_raises_on_no_policy(cps_subsample):
    """
    Test Calculator ctor error with no policy argument.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    with pytest.raises(ValueError):
        Calculator(records=rec)


def test_calculator_mtr(cps_subsample):
    """
    Test Calculator mtr method.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    calcx = Calculator(policy=Policy(), records=rec)
    calcx.calc_all()
    combinedx = calcx.array('combined')
    c00100x = calcx.array('c00100')
    calc = Calculator(policy=Policy(), records=rec)
    recs_pre_e00200p = copy.deepcopy(calc.array('e00200p'))
    (mtr_ptx, mtr_itx, mtr_cmb) = calc.mtr(variable_str='e00200p',
                                           zero_out_calculated_vars=True)
    recs_post_e00200p = calc.array('e00200p')
    assert np.allclose(recs_post_e00200p, recs_pre_e00200p)
    assert np.allclose(calc.array('combined'), combinedx)
    assert np.allclose(calc.array('c00100'), c00100x)
    assert np.array_equal(mtr_cmb, mtr_ptx) is False
    assert np.array_equal(mtr_ptx, mtr_itx) is False
    with pytest.raises(ValueError):
        calc.mtr(variable_str='bad_income_type')
    (_, _, mtr_combined) = calc.mtr(variable_str='e00200s',
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='e00650',
                                    negative_finite_diff=True,
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='e00900p',
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='e01700',
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='e26270',
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='k1bx14p',
                                    calc_all_already_called=True)
    assert isinstance(mtr_combined, np.ndarray)
    (_, _, mtr_combined) = calc.mtr(variable_str='e00200p',
                                    calc_all_already_called=True)
    assert np.allclose(mtr_combined, mtr_cmb)
    assert np.allclose(calc.array('combined'), combinedx)
    assert np.allclose(calc.array('c00100'), c00100x)


def test_calculator_mtr_when_PT_rates_differ():
    """
    Test Calculator mtr method in special case.
    """
    reform = {
        'II_rt1': {2013: 0.40},
        'II_rt2': {2013: 0.40},
        'II_rt3': {2013: 0.40},
        'II_rt4': {2013: 0.40},
        'II_rt5': {2013: 0.40},
        'II_rt6': {2013: 0.40},
        'II_rt7': {2013: 0.40},
        'PT_rt1': {2013: 0.30},
        'PT_rt2': {2013: 0.30},
        'PT_rt3': {2013: 0.30},
        'PT_rt4': {2013: 0.30},
        'PT_rt5': {2013: 0.30},
        'PT_rt6': {2013: 0.30},
        'PT_rt7': {2013: 0.30}
    }
    funit = (
        'RECID,MARS,FLPDYR,e00200,e00200p,e00900,e00900p,extraneous\n'
        '1,    1,   2009,  200000,200000, 100000,100000, 9999999999\n'
    )
    rec = Records(pd.read_csv(StringIO(funit)))
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    (_, mtr1, _) = calc1.mtr(variable_str='p23250')
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=rec)
    (_, mtr2, _) = calc2.mtr(variable_str='p23250')
    assert np.allclose(mtr1, mtr2, rtol=0.0, atol=1e-06)


def test_make_calculator_increment_years_first(cps_subsample):
    """
    Test Calculator inflation indexing of policy parameters.
    """
    # pylint: disable=too-many-locals
    # create Policy object with policy reform
    pol = Policy()
    std5 = 2000
    reform = {
        'STD_Aged': {2015: [std5, std5, std5, std5, std5]},
        'II_em': {2015: 5000,
                  2016: 6000},
        'II_em-indexed': {2016: False}
    }
    pol.implement_reform(reform)
    # create Calculator object with Policy object as modified by reform
    rec = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=pol, records=rec)
    # compare expected policy parameter values with those embedded in calc
    irates = pol.inflation_rates()
    syr = Policy.JSON_START_YEAR
    irate2015 = irates[2015 - syr]
    irate2016 = irates[2016 - syr]
    std6 = std5 * (1.0 + irate2015)
    std7 = std6 * (1.0 + irate2016)
    exp_STD_Aged = np.array([[1500, 1200, 1200, 1500, 1200],
                             [1550, 1200, 1200, 1550, 1200],
                             [std5, std5, std5, std5, std5],
                             [std6, std6, std6, std6, std6],
                             [std7, std7, std7, std7, std7]])
    act_STD_Aged = calc.policy_param('_STD_Aged')
    assert np.allclose(act_STD_Aged[2:7], exp_STD_Aged)
    exp_II_em = np.array([3900, 3950, 5000, 6000, 6000])
    act_II_em = calc.policy_param('_II_em')
    assert np.allclose(act_II_em[2:7], exp_II_em)


def test_ID_HC_vs_BS(cps_subsample):
    """
    Test that complete haircut of itemized deductions produces same
    results as a 100% benefit surtax with no benefit deduction.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    # specify complete-haircut reform policy and Calculator object
    hc_policy = Policy()
    hc_reform = {
        'ID_Medical_hc': {2013: 1.0},
        'ID_StateLocalTax_hc': {2013: 1.0},
        'ID_RealEstate_hc': {2013: 1.0},
        'ID_Casualty_hc': {2013: 1.0},
        'ID_Miscellaneous_hc': {2013: 1.0},
        'ID_InterestPaid_hc': {2013: 1.0},
        'ID_Charity_hc': {2013: 1.0}
    }
    hc_policy.implement_reform(hc_reform)
    hc_calc = Calculator(policy=hc_policy, records=recs)
    hc_calc.calc_all()
    hc_taxes = hc_calc.dataframe(['iitax', 'payrolltax'])
    del hc_calc
    # specify benefit-surtax reform policy and Calculator object
    bs_policy = Policy()
    bs_reform = {
        'ID_BenefitSurtax_crt': {2013: 0.0},
        'ID_BenefitSurtax_trt': {2013: 1.0}
    }
    bs_policy.implement_reform(bs_reform)
    bs_calc = Calculator(policy=bs_policy, records=recs)
    bs_calc.calc_all()
    bs_taxes = bs_calc.dataframe([], all_vars=True)
    del bs_calc
    # compare calculated taxes generated by the two reforms
    assert np.allclose(hc_taxes['payrolltax'], bs_taxes['payrolltax'])
    assert np.allclose(hc_taxes['iitax'], bs_taxes['iitax'])


def test_ID_StateLocal_HC_vs_CRT(cps_subsample):
    """
    Test that a cap on state/local income and sales tax deductions at 0 percent
    of AGI is equivalent to a complete haircut on the same state/local tax
    deductions.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    # specify state/local complete haircut reform policy and Calculator object
    hc_policy = Policy()
    hc_reform = {'ID_StateLocalTax_hc': {2013: 1.0}}
    hc_policy.implement_reform(hc_reform)
    hc_calc = Calculator(policy=hc_policy, records=rec)
    hc_calc.calc_all()
    # specify AGI cap reform policy and Calculator object
    crt_policy = Policy()
    crt_reform = {'ID_StateLocalTax_crt': {2013: 0.0}}
    crt_policy.implement_reform(crt_reform)
    crt_calc = Calculator(policy=crt_policy, records=rec)
    crt_calc.calc_all()
    # compare calculated tax results generated by the two reforms
    assert np.allclose(hc_calc.array('payrolltax'),
                       crt_calc.array('payrolltax'))
    assert np.allclose(hc_calc.array('iitax'),
                       crt_calc.array('iitax'))


def test_ID_RealEstate_HC_vs_CRT(cps_subsample):
    """
    Test that a cap on all state, local, and foreign real estate tax deductions
    at 0 percent of AGI is equivalent to a complete haircut on the same real
    estate tax deductions.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    # specify real estate complete haircut reform policy and Calculator object
    hc_policy = Policy()
    hc_reform = {'ID_RealEstate_hc': {2013: 1.0}}
    hc_policy.implement_reform(hc_reform)
    hc_calc = Calculator(policy=hc_policy, records=rec)
    hc_calc.calc_all()
    # specify AGI cap reform policy and Calculator object
    crt_policy = Policy()
    crt_reform = {'ID_RealEstate_crt': {2013: 0.0}}
    crt_policy.implement_reform(crt_reform)
    crt_calc = Calculator(policy=crt_policy, records=rec)
    crt_calc.calc_all()
    # compare calculated tax results generated by the two reforms
    assert np.allclose(hc_calc.array('payrolltax'),
                       crt_calc.array('payrolltax'))
    assert np.allclose(hc_calc.array('iitax'),
                       crt_calc.array('iitax'))


RAWINPUT_FUNITS = 4
RAWINPUT_YEAR = 2015
RAWINPUT_CONTENTS = (
    'RECID,MARS,unknown\n'
    '    1,   2,      9\n'
    '    2,   1,      9\n'
    '    3,   4,      9\n'
    '    4,   3,      9\n'
)


def test_calculator_using_nonstd_input():
    """
    Test Calculator using non-standard input records.
    """
    # check Calculator handling of raw, non-standard input data with no aging
    pol = Policy()
    pol.set_year(RAWINPUT_YEAR)  # set policy params to input data year
    nonstd = Records(data=pd.read_csv(StringIO(RAWINPUT_CONTENTS)),
                     start_year=RAWINPUT_YEAR,  # set raw input data year
                     gfactors=None,  # keeps raw data unchanged
                     weights=None)
    assert nonstd.array_length == RAWINPUT_FUNITS
    calc = Calculator(policy=pol, records=nonstd,
                      sync_years=False)  # keeps raw data unchanged
    assert calc.current_year == RAWINPUT_YEAR
    calc.calc_all()
    assert calc.weighted_total('e00200') == 0
    assert calc.total_weight() == 0
    varlist = ['RECID', 'MARS']
    dframe = calc.dataframe(varlist)
    assert isinstance(dframe, pd.DataFrame)
    assert dframe.shape == (RAWINPUT_FUNITS, len(varlist))
    mars = calc.array('MARS')
    assert isinstance(mars, np.ndarray)
    assert mars.shape == (RAWINPUT_FUNITS,)
    exp_iitax = np.zeros((nonstd.array_length,))
    assert np.allclose(calc.array('iitax'), exp_iitax)
    mtr_ptax, _, _ = calc.mtr(wrt_full_compensation=False)
    exp_mtr_ptax = np.zeros((nonstd.array_length,))
    exp_mtr_ptax.fill(0.153)
    assert np.allclose(mtr_ptax, exp_mtr_ptax)


def test_bad_json_names(tests_path):
    """
    Test that ValueError raised with assump or reform do not end in '.json'
    """
    test_url = (
        'https://raw.githubusercontent.com/PSLmodels/'
        'Tax-Calculator/master/taxcalc/reforms/'
        '2017_law.out.csv'
    )
    csvname = os.path.join(tests_path, '..', 'growfactors.csv')
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(csvname, None)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(test_url, None)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, csvname)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, test_url)


def test_json_assump_url():
    """
    Test reading JSON assumption file using URL.
    """
    assump_str = """
    {
        "consumption": {
            // all BEN_*_value parameters have a default value of one
            "BEN_housing_value": {"2017": 1.0},
            "BEN_snap_value": {"2017": 1.0},
            "BEN_tanf_value": {"2017": 1.0},
            "BEN_vet_value": {"2017": 1.0},
            "BEN_wic_value": {"2017": 1.0},
            "BEN_mcare_value": {"2017": 1.0},
            "BEN_mcaid_value": {"2017": 1.0},
            "BEN_other_value": {"2017": 1.0},
            // all MPC_* parameters have a default value of zero
            "MPC_e17500": {"2017": 0.0},
            "MPC_e18400": {"2017": 0.0},
            "MPC_e19800": {"2017": 0.0},
            "MPC_e20400": {"2017": 0.0}
        },
        "growdiff_baseline": {
            // all growdiff_baseline parameters have a default value of zero
            "ABOOK": {"2017": 0.0},
            "ACGNS": {"2017": 0.0},
            "ACPIM": {"2017": 0.0},
            "ACPIU": {"2017": 0.0},
            "ADIVS": {"2017": 0.0},
            "AINTS": {"2017": 0.0},
            "AIPD": {"2017": 0.0},
            "ASCHCI": {"2017": 0.0},
            "ASCHCL": {"2017": 0.0},
            "ASCHEI": {"2017": 0.0},
            "ASCHEL": {"2017": 0.0},
            "ASCHF": {"2017": 0.0},
            "ASOCSEC": {"2017": 0.0},
            "ATXPY": {"2017": 0.0},
            "AUCOMP": {"2017": 0.0},
            "AWAGE": {"2017": 0.0},
            "ABENOTHER": {"2017": 0.0},
            "ABENMCARE": {"2017": 0.0},
            "ABENMCAID": {"2017": 0.0},
            "ABENSSI": {"2017": 0.0},
            "ABENSNAP": {"2017": 0.0},
            "ABENWIC": {"2017": 0.0},
            "ABENHOUSING": {"2017": 0.0},
            "ABENTANF": {"2017": 0.0},
            "ABENVET": {"2017": 0.0}
        },
        "growdiff_response": {
            // all growdiff_response parameters have a default value of zero
            "ABOOK": {"2017": 0.0},
            "ACGNS": {"2017": 0.0},
            "ACPIM": {"2017": 0.0},
            "ACPIU": {"2017": 0.0},
            "ADIVS": {"2017": 0.0},
            "AINTS": {"2017": 0.0},
            "AIPD": {"2017": 0.0},
            "ASCHCI": {"2017": 0.0},
            "ASCHCL": {"2017": 0.0},
            "ASCHEI": {"2017": 0.0},
            "ASCHEL": {"2017": 0.0},
            "ASCHF": {"2017": 0.0},
            "ASOCSEC": {"2017": 0.0},
            "ATXPY": {"2017": 0.0},
            "AUCOMP": {"2017": 0.0},
            "AWAGE": {"2017": 0.0},
            "ABENOTHER": {"2017": 0.0},
            "ABENMCARE": {"2017": 0.0},
            "ABENMCAID": {"2017": 0.0},
            "ABENSSI": {"2017": 0.0},
            "ABENSNAP": {"2017": 0.0},
            "ABENWIC": {"2017": 0.0},
            "ABENHOUSING": {"2017": 0.0},
            "ABENTANF": {"2017": 0.0},
            "ABENVET": {"2017": 0.0}
        }
    }
    """
    assump_url = ('https://raw.githubusercontent.com/PSLmodels/'
                  'Tax-Calculator/master/taxcalc/assumptions/'
                  'economic_assumptions_template.json')
    params_str = Calculator.read_json_param_objects(None, assump_str)
    assert params_str
    params_url = Calculator.read_json_param_objects(None, assump_url)
    assert params_url
    assert params_url == params_str

    assump_gh_url = (
        "github://PSLmodels:Tax-Calculator@master/taxcalc/assumptions/"
        "economic_assumptions_template.json"
    )
    params_gh_url = Calculator.read_json_param_objects(None, assump_gh_url)
    assert params_gh_url
    assert params_gh_url == params_str


def test_read_bad_json_assump_file():
    """
    Test invalid JSON assumption files.
    """
    badassump1 = """
    {
      "consumption": { // example of incorrect JSON because 'x' must be "x"
        'x': {"2014": 0.25}
      },
      "growdiff_baseline": {},
      "growdiff_response": {}
    }
    """
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, badassump1)
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, 'unknown_file_name')
    with pytest.raises(TypeError):
        Calculator.read_json_param_objects(None, list())


def test_json_doesnt_exist():
    """
    Test JSON file which doesn't exist
    """
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects(None, './reforms/doesnt_exist.json')
    with pytest.raises(ValueError):
        Calculator.read_json_param_objects('./reforms/doesnt_exist.json', None)


def test_calc_all():
    """
    Test calc_all method.
    """
    cyr = 2016
    pol = Policy()
    pol.set_year(cyr)
    nonstd = Records(data=pd.read_csv(StringIO(RAWINPUT_CONTENTS)),
                     start_year=cyr, gfactors=None, weights=None)
    assert nonstd.array_length == RAWINPUT_FUNITS
    calc = Calculator(policy=pol, records=nonstd,
                      sync_years=False)  # keeps raw data unchanged
    assert calc.current_year == cyr


def test_noreform_documentation():
    """
    Test automatic documentation creation.
    """
    reform_json = """
    {
    }
    """
    assump_json = """
    {
    "consumption": {},
    "growdiff_baseline": {},
    "growdiff_response": {}
    }
    """
    params = Calculator.read_json_param_objects(reform_json, assump_json)
    assert isinstance(params, dict)
    actual_doc = Calculator.reform_documentation(params)
    expected_doc = (
        'REFORM DOCUMENTATION\n'
        'Baseline Growth-Difference Assumption Values by Year:\n'
        'none: no baseline GrowDiff assumptions specified\n'
        'Response Growth-Difference Assumption Values by Year:\n'
        'none: no response GrowDiff assumptions specified\n'
        'Policy Reform Parameter Values by Year:\n'
        'none: using current-law policy parameters\n'
    )
    assert actual_doc == expected_doc


def test_reform_documentation():
    """
    Test automatic documentation creation.
    """
    reform_json = """
{
    "II_em-indexed": {
        "2016": false,
        "2018": true
    },
    "II_em": {
        "2016": 5000,
        "2018": 6000,
        "2020": 7000
    },
    "EITC_indiv": {
        "2017": true
    },
    "STD_Aged-indexed": {
        "2016": false
    },
    "STD_Aged": {
        "2016": [1600, 1300, 1300, 1600, 1600],
        "2020": [2000, 2000, 2000, 2000, 2000]
    },
    "ID_BenefitCap_Switch": {
        "2020": [false, false, false, false, false, false, false]
    }
}
"""
    assump_json = """
{
"consumption": {},
// increase baseline inflation rate by one percentage point in 2014+
// (has no effect on known policy parameter values)
"growdiff_baseline": {"ACPIU": {"2014": 0.010}},
"growdiff_response": {"ACPIU": {"2014": 0.015}}
}
"""
    params = Calculator.read_json_param_objects(reform_json, assump_json)
    assert isinstance(params, dict)
    second_reform = {'II_em': {2019: 6500}}
    doc = Calculator.reform_documentation(params, [second_reform])
    assert isinstance(doc, str)
    dump = False  # set to True to print documentation and force test failure
    if dump:
        print(doc)
        assert 1 == 2


def test_distribution_tables(cps_subsample):
    """
    Test distribution_tables method.
    """
    pol = Policy()
    recs = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=pol, records=recs)
    assert calc1.current_year == 2014
    calc1.calc_all()
    dt1, dt2 = calc1.distribution_tables(None, 'weighted_deciles')
    assert isinstance(dt1, pd.DataFrame)
    assert dt2 is None
    dt1, dt2 = calc1.distribution_tables(calc1, 'weighted_deciles')
    assert isinstance(dt1, pd.DataFrame)
    assert isinstance(dt2, pd.DataFrame)
    reform = {
        'UBI_u18': {2014: 1000},
        'UBI_1820': {2014: 1000},
        'UBI_21': {2014: 1000}
    }
    pol.implement_reform(reform)
    assert not pol.parameter_errors
    calc2 = Calculator(policy=pol, records=recs)
    calc2.calc_all()
    dt1, dt2 = calc1.distribution_tables(calc2, 'weighted_deciles')
    assert isinstance(dt1, pd.DataFrame)
    assert isinstance(dt2, pd.DataFrame)


def test_difference_table(cps_subsample):
    """
    Test difference_table method.
    """
    cyr = 2014
    pol = Policy()
    recs = Records.cps_constructor(data=cps_subsample)
    calc1 = Calculator(policy=pol, records=recs)
    assert calc1.current_year == cyr
    reform = {'SS_Earnings_c': {cyr: 9e99}}
    pol.implement_reform(reform)
    calc2 = Calculator(policy=pol, records=recs)
    assert calc2.current_year == cyr
    calc1.calc_all()
    calc2.calc_all()
    diff = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
    assert isinstance(diff, pd.DataFrame)


def test_diagnostic_table(cps_subsample):
    """
    Test diagnostic_table method.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    adt = calc.diagnostic_table(3)
    assert isinstance(adt, pd.DataFrame)


def test_mtr_graph(cps_subsample):
    """
    Test mtr_graph method.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    fig = calc.mtr_graph(calc,
                         mars=2,
                         income_measure='wages',
                         mtr_measure='ptax',
                         pop_quantiles=False)
    assert fig
    fig = calc.mtr_graph(calc,
                         income_measure='agi',
                         mtr_measure='itax',
                         pop_quantiles=True)
    assert fig


def test_atr_graph(cps_subsample):
    """
    Test atr_graph method.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    fig = calc.atr_graph(calc, mars=2, atr_measure='itax')
    assert fig
    fig = calc.atr_graph(calc, atr_measure='ptax')
    assert fig


def test_privacy_of_embedded_objects(cps_subsample):
    """
    Test privacy of objects embedded in Calculator object.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    var1 = var2 = var3 = 0
    # pylint: disable=protected-access
    with pytest.raises(AttributeError):
        var1 = calc.__policy.current_year
    with pytest.raises(AttributeError):
        var2 = calc.__records.s006
    with pytest.raises(AttributeError):
        var3 = calc.__consumption.current_year
    assert var1 == var2 == var3


def test_n65(cps_subsample):
    """
    Test n65 method.
    """
    recs = Records.cps_constructor(data=cps_subsample)
    calc = Calculator(policy=Policy(), records=recs)
    assert calc.n65().sum() > 600


def test_ce_aftertax_income(cps_subsample):
    """
    Test ce_aftertax_income method.
    """
    rec = Records.cps_constructor(data=cps_subsample)
    pol = Policy()
    calc1 = Calculator(policy=pol, records=rec)
    pol.implement_reform({'SS_Earnings_c': {2013: 9e99}})
    calc2 = Calculator(policy=pol, records=rec)
    res = calc1.ce_aftertax_income(calc2)
    assert isinstance(res, dict)


@pytest.mark.itmded_vars
@pytest.mark.pre_release
@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('year, cvname, hcname',
                         [(2018, 'c17000', 'ID_Medical_hc'),
                          (2018, 'c18300', 'ID_AllTaxes_hc'),
                          (2018, 'c19200', 'ID_InterestPaid_hc'),
                          (2018, 'c19700', 'ID_Charity_hc'),
                          (2018, 'c20500', 'ID_Casualty_hc'),
                          (2018, 'c20800', 'ID_Miscellaneous_hc'),
                          (2017, 'c17000', 'ID_Medical_hc'),
                          (2017, 'c18300', 'ID_AllTaxes_hc'),
                          (2017, 'c19200', 'ID_InterestPaid_hc'),
                          (2017, 'c19700', 'ID_Charity_hc'),
                          (2017, 'c20500', 'ID_Casualty_hc'),
                          (2017, 'c20800', 'ID_Miscellaneous_hc')])
def test_itemded_component_amounts(year, cvname, hcname, puf_fullsample):
    """
    Check that all c04470 components are adjusted to reflect the filing
    unit's standard-vs-itemized-deduction decision.  Check for 2018
    (when current law has no Pease phaseout of itemized deductions and
    already has complete haircuts for Casualty and Miscellaneous deductions)
    and 2017 (when current law has a Pease phaseout of itemized deductions
    and has no haircuts).  The calcfunctions.py code makes no attempt to
    adjust the components for the effects of Pease-like phaseout or any other
    type of limitation on total itemized deductions, so the pre-2018 tests
    here use c21060, instead of c04470, as the itemized deductions total.
    """
    # pylint: disable=too-many-locals
    recs = Records(data=puf_fullsample)
    # policy1 such that everybody itemizes deductions and all are allowed
    policy1 = Policy()
    reform1 = {
        'STD_Aged': {year: [0.0, 0.0, 0.0, 0.0, 0.0]},
        'STD': {year: [0.0, 0.0, 0.0, 0.0, 0.0]}
    }
    policy1.implement_reform(reform1)
    assert not policy1.parameter_errors
    # policy2 such that everybody itemizes deductions but one is disallowed
    policy2 = Policy()
    reform2 = {
        'STD_Aged': {year: [0.0, 0.0, 0.0, 0.0, 0.0]},
        'STD': {year: [0.0, 0.0, 0.0, 0.0, 0.0]},
        hcname: {year: 1.0}
    }
    policy2.implement_reform(reform2)
    assert not policy2.parameter_errors
    # compute tax liability in specified year
    calc1 = Calculator(policy=policy1, records=recs, verbose=False)
    calc1.advance_to_year(year)
    calc1.calc_all()
    calc2 = Calculator(policy=policy2, records=recs, verbose=False)
    calc2.advance_to_year(year)
    calc2.calc_all()
    # confirm that nobody is taking the standard deduction
    assert np.allclose(calc1.array('standard'), 0.)
    assert np.allclose(calc2.array('standard'), 0.)
    # calculate different in total itemized deductions
    if year == 2017:
        # pre-Pease limitation total itemized deductions
        itmded1 = calc1.weighted_total('c21060') * 1e-9
        itmded2 = calc2.weighted_total('c21060') * 1e-9
    elif year == 2018:
        # total itemized deductions (no Pease-like limitation)
        itmded1 = calc1.weighted_total('c04470') * 1e-9
        itmded2 = calc2.weighted_total('c04470') * 1e-9
    else:
        raise ValueError('illegal year value = {}'.format(year))
    difference_in_total_itmded = itmded1 - itmded2
    # calculate itemized component amount
    component_amt = calc1.weighted_total(cvname) * 1e-9
    # confirm that component amount is equal to difference in total deductions
    if year == 2017 and cvname == 'c19700':
        atol = 0.016
    elif year == 2017 and cvname == 'c19200':
        atol = 0.010
    elif year == 2017 and cvname == 'c18300':
        atol = 0.009
    else:
        atol = 0.00001
    if not np.allclose(component_amt, difference_in_total_itmded, atol=atol):
        txt = '\n{}={:.3f}  !=  {:.3f}=difference_in_total_itemized_deductions'
        msg = txt.format(cvname, component_amt, difference_in_total_itmded)
        raise ValueError(msg)


def test_qbid_calculation():
    """
    Test Calculator's QBID calculations using the six example filing units
    specified in Table 1 of this TPC publication: "Navigating the New
    Pass-Through Provisions: A Technical Explanation" by William G. Gale
    and Aaron Krupkin (January 31, 2018), which is available at this URL:
      https://www.taxpolicycenter.org/publications/
      navigating-new-pass-through-provisions-technical-explanation/full
    """
    # In constructing the TPC example filing units, assume that the taxpayer
    # has business income in the form of e26270/e02000 income and no earnings,
    # and that the spouse has no business income and only earnings.
    TPC_YEAR = 2018
    TPC_VARS = (
        'RECID,MARS,e00200s,e00200,e26270,e02000,PT_SSTB_income,'
        'PT_binc_w2_wages,PT_ubia_property,pre_qbid_taxinc,qbid\n'
    )
    TPC_FUNITS = (
        '1,2, 99000, 99000,75000,75000,1,20000,90000,150000,15000.00\n'
        '2,2,349000,349000,75000,75000,1,20000,90000,400000, 1612.50\n'
        '3,2,524000,524000,75000,75000,1,20000,90000,575000,    0.00\n'
        '4,2, 99000, 99000,75000,75000,0,20000,90000,150000,15000.00\n'
        '5,2,349000,349000,75000,75000,0,20000,90000,400000,10750.00\n'
        '6,2,524000,524000,75000,75000,0,20000,90000,575000,10000.00\n'
    )
    # generate actual Calculator pre-qbid taxinc and qbid amounts
    tpc_df = pd.read_csv(StringIO(TPC_VARS + TPC_FUNITS))
    recs = Records(data=tpc_df, start_year=TPC_YEAR,
                   gfactors=None, weights=None)
    calc = Calculator(policy=Policy(), records=recs)
    assert calc.current_year == TPC_YEAR
    calc.calc_all()
    varlist = ['RECID', 'c00100', 'standard', 'c04470', 'qbided']
    tc_df = calc.dataframe(varlist)
    # compare actual amounts with expected amounts from TPC publication
    act_taxinc = tc_df.c00100 - np.maximum(tc_df.standard, tc_df.c04470)
    exp_taxinc = tpc_df.pre_qbid_taxinc
    assert np.allclose(act_taxinc, exp_taxinc)
    assert np.allclose(tc_df.qbided, tpc_df.qbid)


def test_qbid_limit_switch():
    """
    Test Calculator's switch to implement wage/capital limitations
    on QBI deduction.
    """
    cy = 2019
    ref = {"PT_qbid_limit_switch": {2019: False}}

    # filing unit has $500,000 in wages and $100,000 in QBI. Since
    # the household is above the taxable income limitation threshold,
    # with full wage/capital limitations, it does not receive a QBI
    # deduction. With sufficent wage/capital to avoid the limitation,
    # the filing unit receives a deduction of:
    # $100,000 * 20% = $20,000.
    VARS = 'RECID,MARS,e00200s,e00200p,e00200,e26270,e02000\n'
    FUNIT = '1,2,250000,250000,500000,100000,100000'

    funit_df = pd.read_csv(StringIO(VARS + FUNIT))
    recs = Records(data=funit_df, start_year=cy,
                   gfactors=None, weights=None)

    calc_base = Calculator(policy=Policy(), records=recs)
    calc_base.calc_all()

    qbid_base = calc_base.array('qbided')
    assert np.equal(qbid_base, 0)

    pol_ref = Policy()
    pol_ref.implement_reform(ref)
    calc_ref = Calculator(policy=pol_ref, records=recs)
    calc_ref.calc_all()

    qbid_ref = calc_ref.array('qbided')
    assert np.equal(qbid_ref, 20000)


def test_calc_all_benefits_amounts(cps_subsample):
    '''
    Testing how benefits are handled in the calc_all method
    '''
    # set a reform with a positive UBI amount
    ubi_ref = {'UBI_21': {2020: 1000}}

    # create baseline calculator
    pol = Policy()
    recs = Records.cps_constructor(data=cps_subsample)
    calc_base = Calculator(pol, recs)
    calc_base.advance_to_year(2020)
    calc_base.calc_all()

    # create reform calculator
    pol_ubi = Policy()
    pol_ubi.implement_reform(ubi_ref)
    calc_ubi = Calculator(pol_ubi, recs)
    calc_ubi.advance_to_year(2020)
    calc_ubi.calc_all()

    # check that differences in benefits totals are equal to diffs in
    # UBI
    ubi_diff = (calc_ubi.weighted_total('ubi') -
                calc_base.weighted_total('ubi')) / 1e9
    benefit_cost_diff = (
        calc_ubi.weighted_total('benefit_cost_total') -
        calc_base.weighted_total('benefit_cost_total')) / 1e9
    benefit_value_diff = (
        calc_ubi.weighted_total('benefit_cost_total') -
        calc_base.weighted_total('benefit_cost_total')) / 1e9

    assert np.allclose(ubi_diff, benefit_cost_diff)
    assert np.allclose(ubi_diff, benefit_value_diff)


def test_cg_top_rate():
    """
    Test top CG bracket and rate.
    """
    cy = 2019

    # set NIIT and STD to zero to isolate CG tax rates
    base = {"NIIT_rt": {2019: 0},
            "STD": {2019: [0, 0, 0, 0, 0]}}

    # create additional top CG bracket and rate
    ref = {"CG_brk3": {2019: [1000000, 1000000, 1000000, 1000000, 1000000]},
           "CG_rt4": {2019: 0.4},
           "NIIT_rt": {2019: 0},
           "STD": {2019: [0, 0, 0, 0, 0]}}

    # create one record just below the top CG bracket and one just above
    VARS = 'RECID,MARS,p23250\n'
    FUNITS = '1,2,999999\n2,2,1000001\n'

    pol_base = Policy()
    pol_base.implement_reform(base)

    pol_ref = Policy()
    pol_ref.implement_reform(ref)

    funit_df = pd.read_csv(StringIO(VARS + FUNITS))
    recs = Records(data=funit_df, start_year=cy,
                   gfactors=None, weights=None)

    calc_base = Calculator(policy=pol_base, records=recs)
    calc_base.calc_all()

    calc_ref = Calculator(policy=pol_ref, records=recs)
    calc_ref.calc_all()

    # calculate MTRs wrt long term gains
    mtr_base = calc_base.mtr(variable_str='p23250',
                             calc_all_already_called=True,
                             wrt_full_compensation=False)
    mtr_itax_base = mtr_base[1]

    cg_rt3 = pol_base.to_array('CG_rt3', year=2019)
    # check that MTR for both records is equal to CG_rt3
    assert np.allclose(mtr_itax_base, cg_rt3)

    # calculate MTRs under reform
    mtr_ref = calc_ref.mtr(variable_str='p23250',
                           calc_all_already_called=True,
                           wrt_full_compensation=False)
    mtr_itax_ref = mtr_ref[1]

    cg_rt3_ref = pol_ref.to_array('CG_rt3', year=2019)
    cg_rt4_ref = pol_ref.to_array(param='CG_rt4', year=2019)

    # check that MTR of houshold below top threshold is equal to
    # CG_rt3
    assert np.allclose(mtr_itax_ref[0], cg_rt3_ref)
    # check that MTR of household above top threshold is equal to
    # CG_rt4
    assert np.allclose(mtr_itax_ref[1], cg_rt4_ref)
