"""
Test functions in taxcalc/tbi directory using both puf.csv and cps.csv input.

All the tests in this file, and only these tests, can be executed this way:
Tax-Calculator$ cd taxcalc ; pytest -n4 -k tests/test_tbi.py ; cd ..
"""
# CODING-STYLE CHECKS:
# pycodestyle test_tbi.py

import json
import numpy as np
import pandas as pd
import pytest
from taxcalc.tbi import *
from taxcalc import Policy, Records, Calculator, Behavior


USER_MODS = {
    'policy': {
        2016: {'_II_rt3': [0.33],
               '_PT_rt3': [0.33],
               '_II_rt4': [0.33],
               '_PT_rt4': [0.33]}
    },
    'consumption': {
        2016: {'_MPC_e20400': [0.01]}
    },
    'behavior': {
        2016: {'_BE_sub': [0.25]}
    },
    'growdiff_baseline': {
    },
    'growdiff_response': {
    },
    'growmodel': {
    }
}


@pytest.mark.parametrize('start_year, year_n',
                         [(2000, 0),
                          (2013, -1),
                          (2018, 10)])
def test_check_years_errors(start_year, year_n):
    with pytest.raises(ValueError):
        check_years_return_first_year(year_n, start_year, use_puf_not_cps=True)


def test_check_user_mods_errors():
    check_user_mods(USER_MODS)
    seed1 = random_seed(USER_MODS)
    with pytest.raises(ValueError):
        check_user_mods(list())
    usermods = USER_MODS
    behavior_subdict = usermods.pop('behavior')
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods['behavior'] = behavior_subdict
    usermods['unknown_key'] = dict()
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods.pop('unknown_key')
    seed2 = random_seed(usermods)
    assert seed1 == seed2


@pytest.mark.requires_pufcsv
def test_run_nth_year_value_errors():
    usermods = USER_MODS
    # test for growdiff_response not allowed error
    usermods['growdiff_response'] = {2018: {'_AINTS': [0.02]}}
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013,
                                     use_puf_not_cps=True,
                                     use_full_sample=False,
                                     user_mods=usermods,
                                     gdp_elasticity=0.36,
                                     return_dict=False)
    usermods['growdiff_response'] = dict()
    # test for behavior not allowed error
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013,
                                     use_puf_not_cps=True,
                                     use_full_sample=False,
                                     user_mods=usermods,
                                     gdp_elasticity=0.36,
                                     return_dict=False)


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('resdict', [True, False])
def test_run_gdp_elast_model_1(resdict):
    usermods = USER_MODS
    usermods['behavior'] = dict()
    res = run_nth_year_gdp_elast_model(2, 2016,
                                       use_puf_not_cps=True,
                                       use_full_sample=False,
                                       user_mods=usermods,
                                       gdp_elasticity=0.36,
                                       return_dict=resdict)
    if resdict:
        assert isinstance(res, dict)
    else:
        assert isinstance(res, float)


def test_run_gdp_elast_model_2():
    usermods = USER_MODS
    usermods['behavior'] = dict()
    res = run_nth_year_gdp_elast_model(0, 2014,  # forces automatic zero
                                       use_puf_not_cps=False,
                                       use_full_sample=False,
                                       user_mods=usermods,
                                       gdp_elasticity=0.36,
                                       return_dict=False)
    assert res == 0.0


def test_run_gdp_qelast_model_3():
    usermods = USER_MODS
    usermods['behavior'] = dict()
    res = run_nth_year_gdp_elast_model(0, 2017,  # forces automatic zero
                                       use_puf_not_cps=False,
                                       use_full_sample=False,
                                       user_mods=usermods,
                                       gdp_elasticity=0.36,
                                       return_dict=False)
    assert res == 0.0


def test_create_dict_table():
    # test correct usage
    dframe = pd.DataFrame(data=[[1., 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])
    ans = create_dict_table(dframe, num_decimals=2)
    exp = {'0': ['1.00', '2', '3'],
           '1': ['4.00', '5', '6'],
           '2': ['7.00', '8', '9']}
    assert ans == exp
    # test incorrect usage
    dframe = pd.DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'], dtype='i2')
    with pytest.raises(NotImplementedError):
        create_dict_table(dframe)


@pytest.mark.requires_pufcsv
def test_with_pufcsv(puf_fullsample):
    # specify usermods dictionary in code
    start_year = 2017
    reform_year = start_year
    analysis_year = 2026
    year_n = analysis_year - start_year
    reform = {
        '_FICA_ss_trt': [0.2]
    }
    usermods = dict()
    usermods['policy'] = {reform_year: reform}
    usermods['consumption'] = {}
    usermods['behavior'] = {}
    usermods['growdiff_baseline'] = {}
    usermods['growdiff_response'] = {}
    usermods['growmodel'] = {}
    seed = random_seed(usermods)
    assert seed == 580419828
    # create a Policy object (pol) containing reform policy parameters
    pol = Policy()
    pol.implement_reform(usermods['policy'])
    # create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_fullsample)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=pol, records=rec)
    while calc.current_year < analysis_year:
        calc.increment_year()
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(1)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    assert taxes_fullsample is not None
    fulls_reform_revenue = float(taxes_fullsample.loc[analysis_year])
    # call run_nth_year_tax_calc_model function
    resdict = run_nth_year_taxcalc_model(year_n, start_year,
                                         use_puf_not_cps=True,
                                         use_full_sample=True,
                                         user_mods=usermods,
                                         return_dict=True)
    total = resdict['aggr_2']
    tbi_reform_revenue = float(total['combined_tax_9'])
    # assert that tbi revenue is similar to the fullsample calculation
    diff = abs(fulls_reform_revenue - tbi_reform_revenue)
    proportional_diff = diff / fulls_reform_revenue
    frmt = 'f,d,adiff,pdiff=  {:.4f}  {:.4f}  {:.4f}  {}'
    print(frmt.format(fulls_reform_revenue, tbi_reform_revenue,
                      diff, proportional_diff))
    assert proportional_diff < 0.0001  # one-hundredth of one percent
    # assert 1 == 2  # uncomment to force test failure with above print out


def test_reform_warnings_errors():
    msg_dict = reform_warnings_errors(USER_MODS, using_puf=True)
    assert len(msg_dict['policy']['warnings']) == 0
    assert len(msg_dict['policy']['errors']) == 0
    bad1_mods = {
        'policy': {2020: {'_II_rt3': [1.4]},
                   2021: {'_ID_Charity_crt_all': [0.7]}},
        'consumption': {},
        'behavior': {},
        'growdiff_baseline': {},
        'growdiff_response': {},
        'growmodel': {}
    }
    msg_dict = reform_warnings_errors(bad1_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) > 0
    assert len(msg_dict['policy']['errors']) > 0
    bad2_mods = {
        'policy': {2020: {'_II_rt33': [0.4]}},
        'consumption': {},
        'behavior': {},
        'growdiff_baseline': {},
        'growdiff_response': {},
        'growmodel': {}
    }
    msg_dict = reform_warnings_errors(bad2_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) == 0
    assert len(msg_dict['policy']['errors']) > 0
    bad3_mods = dict(USER_MODS, **{'behavior': {2017: {'_BE_inc': [0.8]}}})
    msg_dict = reform_warnings_errors(bad3_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) == 0
    assert len(msg_dict['policy']['errors']) == 0
    assert len(msg_dict['behavior']['warnings']) == 0
    assert len(msg_dict['behavior']['errors']) > 0


@pytest.mark.pre_release
@pytest.mark.tbi_vs_std_behavior
@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('use_puf_not_cps', [True, False])
def test_behavioral_response(use_puf_not_cps, puf_subsample, cps_fullsample):
    """
    Test that behavioral-response results are the same
    when generated from standard Tax-Calculator calls and
    when generated from tbi.run_nth_year_taxcalc_model() calls
    """
    # specify reform and assumptions
    reform_json = """
    {"policy": {
        "_II_rt5": {"2020": [0.25]},
        "_II_rt6": {"2020": [0.25]},
        "_II_rt7": {"2020": [0.25]},
        "_PT_rt5": {"2020": [0.25]},
        "_PT_rt6": {"2020": [0.25]},
        "_PT_rt7": {"2020": [0.25]},
        "_II_em": {"2020": [1000]}
    }}
    """
    assump_json = """
    {"behavior": {"_BE_sub": {"2013": [0.25]}},
     "growdiff_baseline": {},
     "growdiff_response": {},
     "consumption": {},
     "growmodel": {}
    }
    """
    params = Calculator.read_json_param_objects(reform_json, assump_json)
    # specify keyword arguments used in tbi function call
    kwargs = {
        'start_year': 2019,
        'year_n': 0,
        'use_puf_not_cps': use_puf_not_cps,
        'use_full_sample': False,
        'user_mods': {
            'policy': params['policy'],
            'behavior': params['behavior'],
            'growdiff_baseline': params['growdiff_baseline'],
            'growdiff_response': params['growdiff_response'],
            'consumption': params['consumption'],
            'growmodel': params['growmodel']
        },
        'return_dict': False
    }
    # generate aggregate results two ways: using tbi and standard calls
    num_years = 9
    std_res = dict()
    tbi_res = dict()
    if use_puf_not_cps:
        rec = Records(data=puf_subsample)
    else:
        # IMPORTANT: must use same subsample as used in test_cpscsv.py because
        #            that is the subsample used by run_nth_year_taxcalc_model
        std_cps_subsample = cps_fullsample.sample(frac=0.03, random_state=180)
        rec = Records.cps_constructor(data=std_cps_subsample)
    for using_tbi in [True, False]:
        for year in range(0, num_years):
            cyr = year + kwargs['start_year']
            if using_tbi:
                kwargs['year_n'] = year
                tables = run_nth_year_taxcalc_model(**kwargs)
                tbi_res[cyr] = dict()
                for tbl in ['aggr_1', 'aggr_2', 'aggr_d']:
                    tbi_res[cyr][tbl] = tables[tbl]
            else:
                pol = Policy()
                calc1 = Calculator(policy=pol, records=rec)
                pol.implement_reform(params['policy'])
                assert not pol.parameter_errors
                beh = Behavior()
                beh.update_behavior(params['behavior'])
                calc2 = Calculator(policy=pol, records=rec, behavior=beh)
                assert calc2.behavior_has_response()
                calc1.advance_to_year(cyr)
                calc2.advance_to_year(cyr)
                calc2 = Behavior.response(calc1, calc2)
                std_res[cyr] = dict()
                for tbl in ['aggr_1', 'aggr_2', 'aggr_d']:
                    if tbl.endswith('_1'):
                        itax = calc1.weighted_total('iitax')
                        ptax = calc1.weighted_total('payrolltax')
                        ctax = calc1.weighted_total('combined')
                    elif tbl.endswith('_2'):
                        itax = calc2.weighted_total('iitax')
                        ptax = calc2.weighted_total('payrolltax')
                        ctax = calc2.weighted_total('combined')
                    elif tbl.endswith('_d'):
                        itax = (calc2.weighted_total('iitax') -
                                calc1.weighted_total('iitax'))
                        ptax = (calc2.weighted_total('payrolltax') -
                                calc1.weighted_total('payrolltax'))
                        ctax = (calc2.weighted_total('combined') -
                                calc1.weighted_total('combined'))
                    cols = ['0_{}'.format(year)]
                    rows = ['ind_tax', 'payroll_tax', 'combined_tax']
                    datalist = [itax, ptax, ctax]
                    std_res[cyr][tbl] = pd.DataFrame(data=datalist,
                                                     index=rows,
                                                     columns=cols)
                    for col in std_res[cyr][tbl].columns:
                        val = std_res[cyr][tbl][col] * 1e-9
                        std_res[cyr][tbl][col] = round(val, 3)

    # compare the two sets of results
    # NOTE that the PUF tbi results have been "fuzzed" for privacy reasons,
    #      so there is no expectation that those results should be identical.
    no_diffs = True
    cps_dump = False  # setting to True produces dump output and test failure
    if use_puf_not_cps:
        reltol = 0.004  # std and tbi differ if more than 0.4 percent different
        dataset = 'PUF'
        dumping = False
    else:  # CPS results are not "fuzzed", so
        reltol = 1e-9  # std and tbi should be virtually identical
        dataset = 'CPS'
        dumping = cps_dump
    for year in range(0, num_years):
        cyr = year + kwargs['start_year']
        do_dump = bool(dumping and cyr >= 2019 and cyr <= 2020)
        col = '0_{}'.format(year)
        for tbl in ['aggr_1', 'aggr_2', 'aggr_d']:
            tbi = tbi_res[cyr][tbl][col]
            if do_dump:
                txt = 'DUMP of {} {} table for year {}:'
                print(txt.format(dataset, tbl, cyr))
                print(tbi)
            std = std_res[cyr][tbl][col]
            if not np.allclose(tbi, std, atol=0.0, rtol=reltol):
                no_diffs = False
                txt = '***** {} diff in {} table for year {} (year_n={}):'
                print(txt.format(dataset, tbl, cyr, year))
                print('TBI RESULTS:')
                print(tbi)
                print('STD RESULTS:')
                print(std)
    assert no_diffs
    assert not dumping
