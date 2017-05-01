import os
import numpy as np
import pandas as pd
import pytest
from taxcalc.dropq.dropq_utils import *
from taxcalc.dropq import *
from taxcalc import Policy, Records, Calculator, multiyear_diagnostic_table


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
    'gdp_elasticity': {
    }
}


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
    'gdp_elasticity': {
    }
}


@pytest.fixture(scope='session')
def puf_path(tests_path):
    """
    The path to the puf.csv taxpayer data file at repo root
    """
    return os.path.join(tests_path, '..', '..', 'puf.csv')


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


def test_run_nth_year_value_errors(puf_1991_path):
    recs = pd.read_csv(puf_1991_path)
    usermods = USER_MODS
    usermods['growdiff_response'] = {2018: {'_AINTS': [0.02]}}
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013, recs, usermods, False)
    usermods['growdiff_response'] = dict()
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013, recs, usermods, False)


@pytest.mark.parametrize('resjson', [True, False])
def test_run_tax_calc_model(puf_1991_path, resjson):
    recs = pd.read_csv(puf_1991_path)
    usermods = USER_MODS
    res = run_nth_year_tax_calc_model(2, 2016, recs, usermods,
                                      return_json=resjson)
    assert len(res) == 13
    for idx in range(0, len(res)):
        if resjson:
            assert isinstance(res[idx], dict)
        else:
            assert isinstance(res[idx], pd.DataFrame)


@pytest.mark.parametrize('resjson', [True, False])
def test_run_gdp_elast_model(puf_1991_path, resjson):
    usermods = USER_MODS
    usermods['behavior'] = dict()
    usermods['gdp_elasticity'] = {'value': 0.36}
    recs = pd.read_csv(puf_1991_path)
    res = run_nth_year_gdp_elast_model(2, 2016, recs, usermods,
                                       return_json=resjson)
    if resjson:
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


def test_create_json_table():
    # test correct usage
    dframe = pd.DataFrame(data=[[1., 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])
    ans = create_json_table(dframe)
    exp = {'0': ['1.00', '2', '3'],
           '1': ['4.00', '5', '6'],
           '2': ['7.00', '8', '9']}
    assert ans == exp
    # test incorrect usage
    dframe = pd.DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'], dtype='i2')
    with pytest.raises(NotImplementedError):
        create_json_table(dframe)


@pytest.mark.parametrize('groupby, result_type',
                         [('small_income_bins', 'weighted_sum'),
                          ('large_income_bins', 'weighted_sum'),
                          ('large_income_bins', 'weighted_avg'),
                          ('other_income_bins', 'weighted_avg'),
                          ('large_income_bins', 'other_avg')])
def test_dropq_dist_table(groupby, result_type, puf_1991_path):
    calc = Calculator(policy=Policy(),
                      records=Records(data=pd.read_csv(puf_1991_path)))
    calc.calc_all()
    res = results(calc)
    mask = np.ones(len(res.index))
    (res, _) = drop_records(res, res, mask)
    if groupby == 'other_income_bins' or result_type == 'other_avg':
        with pytest.raises(ValueError):
            dropq_dist_table(res, groupby=groupby,
                             result_type=result_type, suffix='_bin')
    else:
        dropq_dist_table(res, groupby=groupby,
                         result_type=result_type, suffix='_bin')


@pytest.mark.parametrize('groupby, res_column',
                         [('weighted_deciles', 'tax_diff'),
                          ('webapp_income_bins', 'tax_diff'),
                          ('small_income_bins', 'tax_diff'),
                          ('large_income_bins', 'tax_diff'),
                          ('other_deciles', 'tax_diff')])
def test_dropq_diff_table(groupby, res_column, puf_1991_path):
    recs1 = Records(data=pd.read_csv(puf_1991_path))
    calc1 = Calculator(policy=Policy(), records=recs1)
    recs2 = Records(data=pd.read_csv(puf_1991_path))
    pol2 = Policy()
    pol2.implement_reform(USER_MODS['policy'])
    calc2 = Calculator(policy=pol2, records=recs2)
    calc1.calc_all()
    calc2.calc_all()
    res1 = results(calc1)
    res2 = results(calc2)
    assert len(res1.index) == len(res2.index)
    mask = np.ones(len(res1.index))
    (res1, res2) = drop_records(res1, res2, mask)
    dec_sum = (res2['tax_diff_dec'] * res2['s006']).sum()
    if groupby == 'other_deciles':
        with pytest.raises(ValueError):
            dropq_diff_table(res1, res2, groupby=groupby,
                             res_col=res_column, diff_col='iitax',
                             suffix='_dec', wsum=dec_sum)
    else:
        dropq_diff_table(res1, res2, groupby=groupby,
                         res_col=res_column, diff_col='iitax',
                         suffix='_dec', wsum=dec_sum)


@pytest.mark.requires_pufcsv
def test_with_pufcsv(puf_path):  # pylint: disable=redefined-outer-name
    # pylint: disable=too-many-locals
    # specify usermods dictionary in code
    start_year = 2016
    reform_year = start_year + 1
    reforms = dict()
    reforms['_II_rt3'] = [0.33]
    reforms['_PT_rt3'] = [0.33]
    reforms['_II_rt4'] = [0.33]
    reforms['_PT_rt4'] = [0.33]
    usermods = dict()
    usermods['policy'] = {reform_year: reforms}
    usermods['consumption'] = {}
    usermods['behavior'] = {}
    usermods['growdiff_baseline'] = {}
    usermods['growdiff_response'] = {}
    usermods['gdp_elasticity'] = {}
    seed = random_seed(usermods)
    assert seed == 3047708076
    # create a Policy object (pol) containing reform policy parameters
    pol = Policy()
    pol.implement_reform(usermods['policy'])
    # create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_path)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=pol, records=rec)
    while calc.current_year < reform_year:
        calc.increment_year()
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    years = reform_year - Policy.JSON_START_YEAR + 1
    adt = multiyear_diagnostic_table(calc, years)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    assert taxes_fullsample is not None
    fulls_reform_revenue = taxes_fullsample.loc[reform_year]
    # create a Public Use File object
    tax_data = pd.read_csv(puf_path)
    # call run_nth_year_tax_calc_model function
    restuple = run_nth_year_tax_calc_model(1, start_year,
                                           tax_data, usermods,
                                           return_json=True)
    total = restuple[len(restuple) - 1]  # the last of element of the tuple
    dropq_reform_revenue = float(total['combined_tax_1'])
    dropq_reform_revenue *= 1e-9  # convert to billions of dollars
    diff = abs(fulls_reform_revenue - dropq_reform_revenue)
    # assert that dropq revenue is similar to the fullsample calculation
    proportional_diff = diff / fulls_reform_revenue
    frmt = 'f,d,adiff,pdiff=  {:.4f}  {:.4f}  {:.4f}  {}'
    print(frmt.format(fulls_reform_revenue, dropq_reform_revenue,
                      diff, proportional_diff))
    assert proportional_diff < 0.0001  # one-hundredth of one percent
    # assert 1 == 2  # uncomment to force test failure with above print out
