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


def test_format_macro_results():
    data = [[1.875e-03, 1.960e-03, 2.069e-03, 2.131e-03, 2.179e-03, 2.226e-03,
             2.277e-03, 2.324e-03, 2.375e-03, 2.426e-03, 2.184e-03, 2.806e-03],
            [2.538e-04, 4.452e-04, 6.253e-04, 7.886e-04, 9.343e-04, 1.064e-03,
             1.180e-03, 1.284e-03, 1.378e-03, 1.463e-03, 9.419e-04, 2.224e-03],
            [5.740e-03, 5.580e-03, 5.524e-03, 5.347e-03, 5.161e-03, 5.011e-03,
             4.907e-03, 4.818e-03, 4.768e-03, 4.739e-03, 5.160e-03, 4.211e-03],
            [2.883e-03, 2.771e-03, 2.721e-03, 2.620e-03, 2.520e-03, 2.440e-03,
             2.384e-03, 2.337e-03, 2.309e-03, 2.292e-03, 2.528e-03, 2.051e-03],
            [-1.012e-03, -8.141e-04, -6.552e-04, -4.912e-04, -3.424e-04,
             -2.150e-04, -1.081e-04, -1.372e-05, 6.513e-05, 1.336e-04,
             -3.450e-04, 7.538e-04],
            [3.900e-03, 3.143e-03, 2.532e-03, 1.900e-03, 1.325e-03, 8.325e-04,
             4.189e-04, 5.315e-05, -2.525e-04, -5.180e-04, 1.337e-03,
             -2.917e-03],
            [-2.577e-02, -2.517e-02, -2.507e-02, -2.464e-02, -2.419e-02,
             -2.388e-02, -2.368e-02, -2.350e-02, -2.342e-02, -2.341e-02,
             -2.427e-02, -2.275e-02]]
    data = np.array(data)
    res_dict = format_macro_results(data, return_json=True)
    exp = {'GDP': ['0.002', '0.002',
                   '0.002', '0.002', '0.002', '0.002', '0.002',
                   '0.002', '0.002', '0.002', '0.002', '0.003'],
           'Consumption': ['0.000', '0.000',
                           '0.001', '0.001', '0.001', '0.001', '0.001',
                           '0.001', '0.001', '0.001', '0.001', '0.002'],
           'Interest Rates': ['0.004', '0.003',
                              '0.003', '0.002', '0.001', '0.001', '0.000',
                              '0.000', '-0.000', '-0.001', '0.001', '-0.003'],
           'Total Taxes': ['-0.026', '-0.025',
                           '-0.025', '-0.025', '-0.024', '-0.024', '-0.024',
                           '-0.024', '-0.023', '-0.023', '-0.024', '-0.023'],
           'Wages': ['-0.001', '-0.001',
                     '-0.001', '-0.000', '-0.000', '-0.000', '-0.000',
                     '-0.000', '0.000', '0.000', '-0.000', '0.001'],
           'Investment': ['0.006', '0.006',
                          '0.006', '0.005', '0.005', '0.005', '0.005',
                          '0.005', '0.005', '0.005', '0.005', '0.004'],
           'Hours Worked': ['0.003', '0.003',
                            '0.003', '0.003', '0.003', '0.002', '0.002',
                            '0.002', '0.002', '0.002', '0.003', '0.002']}
    assert res_dict == exp
    res_df = format_macro_results(data, return_json=False)
    assert res_df.equals(pd.DataFrame(data))


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
    print choices
    assert isinstance(choices, list)
    assert len(choices) == dframe['positives'].size
    with pytest.raises(ValueError):
        chooser(dframe['zeros'])


def test_format_print_error():
    arr = np.array([1], dtype='i2')
    with pytest.raises(NotImplementedError):
        format_print(arr[0], arr.dtype, 2)


def test_create_json_table():
    dframe = pd.DataFrame(data=[[1., 2, 3], [4, 5, 6], [7, 8, 9]],
                          columns=['a', 'b', 'c'])
    ans = create_json_table(dframe)
    exp = {'0': ['1.00', '2', '3'],
           '1': ['4.00', '5', '6'],
           '2': ['7.00', '8', '9']}
    assert ans == exp


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
