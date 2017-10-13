"""
Test functions in taxcalc/tbi directory using both puf.csv and cps.csv input.
"""
import numpy as np
import pandas as pd
import pytest
from taxcalc.tbi.tbi_utils import *
from taxcalc.tbi import *
from taxcalc import (Policy, Records, Calculator,
                     multiyear_diagnostic_table, results)


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
}


@pytest.mark.parametrize('start_year, year_n',
                         [(2000, 0),
                          (2013, -1),
                          (2017, 10)])
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
def test_run_tax_calc_model(resdict):
    res = run_nth_year_tax_calc_model(2, 2016,
                                      use_puf_not_cps=resdict,
                                      use_full_sample=False,
                                      user_mods=USER_MODS,
                                      return_dict=resdict)
    assert isinstance(res, dict)
    dump = False  # set to True in order to dump returned results and fail test
    for tbl in sorted(res.keys()):
        if resdict:
            assert isinstance(res[tbl], dict)
        else:
            assert isinstance(res[tbl], pd.DataFrame)
        if dump:
            if resdict:
                cols = sorted(res[tbl].keys())
            else:
                cols = sorted(list(res[tbl]))
            for col in cols:
                print('<<tbl={}:col={}>>'.format(tbl, col))
                print(res[tbl][col])
    assert not dump


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('resdict', [True, False])
def test_run_gdp_elast_model(resdict):
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


def test_random_seed_from_subdict():
    """
    Test except logic in try statement in random_seed_from_subdict function.
    """
    dct = {
        2014: {'param1': [0.11]},
        2016: {'param1': [0.13]}
    }
    seed1 = random_seed_from_subdict(dct)
    dct[2016] = {'param1': 0.13}
    seed2 = random_seed_from_subdict(dct)
    assert seed1 == seed2


def test_chooser_error():
    dframe = pd.DataFrame(data=[[0, 1], [0, 2], [0, 3],
                                [0, 4], [0, 5], [0, 6],
                                [0, 7], [0, 8], [0, 9]],
                          columns=['zeros', 'positives'])
    choices = chooser(dframe['positives'])
    assert isinstance(choices, list)
    assert len(choices) == dframe['positives'].size
    with pytest.raises(ValueError):
        chooser(dframe['zeros'])


def test_create_dict_table():
    # test correct usage
    dframe = pd.DataFrame(data=[[1., 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])
    ans = create_dict_table(dframe)
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
    seed = random_seed(usermods)
    assert seed == 1574318062
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
    adt = multiyear_diagnostic_table(calc, 1)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    assert taxes_fullsample is not None
    fulls_reform_revenue = float(taxes_fullsample.loc[analysis_year])
    # call run_nth_year_tax_calc_model function
    resdict = run_nth_year_tax_calc_model(year_n, start_year,
                                          use_puf_not_cps=True,
                                          use_full_sample=True,
                                          user_mods=usermods,
                                          return_dict=True)
    total = resdict['aggr_2']
    tbi_reform_revenue = float(total['combined_tax_9']) * 1e-9
    # assert that tbi revenue is similar to the fullsample calculation
    diff = abs(fulls_reform_revenue - tbi_reform_revenue)
    proportional_diff = diff / fulls_reform_revenue
    frmt = 'f,d,adiff,pdiff=  {:.4f}  {:.4f}  {:.4f}  {}'
    print(frmt.format(fulls_reform_revenue, tbi_reform_revenue,
                      diff, proportional_diff))
    assert proportional_diff < 0.0001  # one-hundredth of one percent
    # assert 1 == 2  # uncomment to force test failure with above print out


def test_reform_warnings_errors():
    msg_dict = reform_warnings_errors(USER_MODS)
    assert len(msg_dict['warnings']) == 0
    assert len(msg_dict['errors']) == 0
    bad1_mods = {
        'policy': {2020: {'_II_rt3': [1.4]}, 2021: {'_STD_Dep': [0]}},
        'consumption': {},
        'behavior': {},
        'growdiff_baseline': {},
        'growdiff_response': {}
    }
    msg_dict = reform_warnings_errors(bad1_mods)
    assert len(msg_dict['warnings']) > 0
    assert len(msg_dict['errors']) > 0
    bad2_mods = {
        'policy': {2020: {'_II_rt33': [0.4]}, 2021: {'_STD_Dep': [0]}},
        'consumption': {},
        'behavior': {},
        'growdiff_baseline': {},
        'growdiff_response': {}
    }
    msg_dict = reform_warnings_errors(bad2_mods)
    assert len(msg_dict['warnings']) == 0
    assert len(msg_dict['errors']) > 0
