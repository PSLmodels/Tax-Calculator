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
from taxcalc import Policy, Records, Calculator


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
    'growdiff_baseline': {
    },
    'growdiff_response': {
    }
}


@pytest.mark.parametrize('start_year, year_n',
                         [(2000, 0),
                          (2013, -1),
                          (2018, 11)])
def test_check_years_errors(start_year, year_n):
    with pytest.raises(ValueError):
        check_years_return_first_year(year_n, start_year, use_puf_not_cps=True)


def test_check_user_mods_errors():
    check_user_mods(USER_MODS)
    seed1 = random_seed(USER_MODS)
    with pytest.raises(ValueError):
        check_user_mods(list())
    usermods = USER_MODS
    consumption_subdict = usermods.pop('consumption')
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods['consumption'] = consumption_subdict
    usermods['unknown_key'] = dict()
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods['unknown_key'] = dict()
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods.pop('unknown_key')
    seed2 = random_seed(usermods)
    assert seed1 == seed2


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
    usermods['growdiff_baseline'] = {}
    usermods['growdiff_response'] = {}
    seed = random_seed(usermods)
    assert seed == 2568216296
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
        'growdiff_baseline': {},
        'growdiff_response': {}
    }
    msg_dict = reform_warnings_errors(bad1_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) > 0
    assert len(msg_dict['policy']['errors']) > 0
    bad2_mods = {
        'policy': {2020: {'_II_rt33': [0.4]}},
        'consumption': {},
        'growdiff_baseline': {},
        'growdiff_response': {}
    }
    msg_dict = reform_warnings_errors(bad2_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) == 0
    assert len(msg_dict['policy']['errors']) > 0
    bad3_mods = dict(USER_MODS,
                     **{'consumption': {2017: {'_MPC_e00200': [0.1]}}})
    msg_dict = reform_warnings_errors(bad3_mods, using_puf=True)
    assert len(msg_dict['policy']['warnings']) == 0
    assert len(msg_dict['policy']['errors']) == 0
    assert len(msg_dict['consumption']['warnings']) == 0
    assert len(msg_dict['consumption']['errors']) > 0
