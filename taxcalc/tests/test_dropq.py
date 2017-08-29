"""
test_dropq.py uses only PUF input data because the dropq algorithm
is designed to work exclusively with private IRS-SOI PUF input data.
"""
import six
import numpy as np
import pandas as pd
import pytest
from taxcalc.dropq.dropq_utils import *
from taxcalc.dropq import *
from taxcalc import (Policy, Records, Calculator,
                     create_difference_table,
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
    'gdp_elasticity': {
    }
}


@pytest.mark.parametrize('start_year, year_n',
                         [(2000, 0),
                          (2013, -1),
                          (2017, 10)])
def test_check_years_errors(start_year, year_n):
    with pytest.raises(ValueError):
        check_years(start_year, year_n)


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
def test_run_nth_year_value_errors(puf_subsample):
    usermods = USER_MODS
    usermods['growdiff_response'] = {2018: {'_AINTS': [0.02]}}
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013, puf_subsample, usermods, False)
    usermods['growdiff_response'] = dict()
    with pytest.raises(ValueError):
        run_nth_year_gdp_elast_model(1, 2013, puf_subsample, usermods, False)


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('resjson', [True, False])
def test_run_tax_calc_model(puf_subsample, resjson):
    usermods = USER_MODS
    res = run_nth_year_tax_calc_model(2, 2016, puf_subsample, usermods,
                                      return_json=resjson)
    assert len(res) == 13
    for idx in range(0, len(res)):
        if resjson:
            assert isinstance(res[idx], dict)
        else:
            assert isinstance(res[idx], pd.DataFrame)


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('resjson', [True, False])
def test_run_gdp_elast_model(puf_subsample, resjson):
    usermods = USER_MODS
    usermods['behavior'] = dict()
    usermods['gdp_elasticity'] = {'value': 0.36}
    res = run_nth_year_gdp_elast_model(2, 2016, puf_subsample, usermods,
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


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('groupby, result_type',
                         [('small_income_bins', 'weighted_sum'),
                          ('large_income_bins', 'weighted_sum'),
                          ('large_income_bins', 'weighted_avg'),
                          ('other_income_bins', 'weighted_avg'),
                          ('large_income_bins', 'other_avg')])
def test_dropq_dist_table(groupby, result_type, puf_subsample):
    calc = Calculator(policy=Policy(), records=Records(data=puf_subsample))
    calc.calc_all()
    res = results(calc.records)
    mask = np.ones(len(res.index))
    (res, _) = drop_records(res, res, mask)
    if groupby == 'other_income_bins' or result_type == 'other_avg':
        with pytest.raises(ValueError):
            dropq_dist_table(res, groupby=groupby,
                             result_type=result_type, suffix='_bin')
    else:
        dropq_dist_table(res, groupby=groupby,
                         result_type=result_type, suffix='_bin')


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('groupby, tax_to_diff',
                         [('weighted_deciles', 'iitax'),
                          ('webapp_income_bins', 'payrolltax'),
                          ('other_deciles', 'combined')])
def test_dropq_diff_table(groupby, tax_to_diff, puf_subsample):
    recs1 = Records(data=puf_subsample)
    calc1 = Calculator(policy=Policy(), records=recs1)
    recs2 = Records(data=puf_subsample)
    pol2 = Policy()
    pol2.implement_reform(USER_MODS['policy'])
    calc2 = Calculator(policy=pol2, records=recs2)
    calc1.calc_all()
    calc2.calc_all()
    res1 = results(calc1.records)
    res2 = results(calc2.records)
    assert len(res1.index) == len(res2.index)
    mask = np.ones(len(res1.index))
    (res1, res2) = drop_records(res1, res2, mask)
    if groupby == 'other_deciles':
        with pytest.raises(ValueError):
            dropq_diff_table(res1, res2, groupby=groupby,
                             income_measure='expanded_income',
                             tax_to_diff=tax_to_diff)
    else:
        diffs = dropq_diff_table(res1, res2, groupby=groupby,
                                 income_measure='expanded_income',
                                 tax_to_diff=tax_to_diff)
        assert isinstance(diffs, pd.DataFrame)


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
    usermods['gdp_elasticity'] = {}
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
    # create a Public Use File object
    tax_data = puf_fullsample
    # call run_nth_year_tax_calc_model function
    restuple = run_nth_year_tax_calc_model(year_n, start_year,
                                           tax_data, usermods,
                                           return_json=True)
    total = restuple[len(restuple) - 1]  # the last of element of the tuple
    dropq_reform_revenue = float(total['combined_tax_9'])
    dropq_reform_revenue *= 1e-9  # convert to billions of dollars
    # assert that dropq revenue is similar to the fullsample calculation
    diff = abs(fulls_reform_revenue - dropq_reform_revenue)
    proportional_diff = diff / fulls_reform_revenue
    frmt = 'f,d,adiff,pdiff=  {:.4f}  {:.4f}  {:.4f}  {}'
    print(frmt.format(fulls_reform_revenue, dropq_reform_revenue,
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


@pytest.mark.requires_pufcsv
def test_dropq_diff_vs_util_diff(puf_subsample):
    recs1 = Records(data=puf_subsample)
    calc1 = Calculator(policy=Policy(), records=recs1)
    recs2 = Records(data=puf_subsample)
    pol2 = Policy()
    pol2.implement_reform(USER_MODS['policy'])
    calc2 = Calculator(policy=pol2, records=recs2)
    calc1.advance_to_year(2016)
    calc2.advance_to_year(2016)
    calc1.calc_all()
    calc2.calc_all()
    # generate diff table using utility function
    udf = create_difference_table(calc1.records, calc2.records,
                                  groupby='weighted_deciles',
                                  income_measure='expanded_income',
                                  tax_to_diff='iitax')
    assert isinstance(udf, pd.DataFrame)
    # generate diff table using dropq functions without dropping any records
    res1 = results(calc1.records)
    res2 = results(calc2.records)
    """
    res2['iitax_dec'] = res2['iitax']  # TODO: ??? drop ???
    res2['tax_diff_dec'] = res2['iitax'] - res1['iitax']  # TODO: ??? drop ???
    """
    qdf = dropq_diff_table(res1, res2,
                           groupby='weighted_deciles',
                           income_measure='expanded_income',
                           tax_to_diff='iitax')
    assert isinstance(qdf, pd.DataFrame)
    # check that each element in the two DataFrames are the same
    if 'perc_aftertax' not in list(qdf):
        qdf = qdf.assign(perc_aftertax=['-0.00%',
                                        '0.00%',
                                        '0.00%',
                                        '0.00%',
                                        '0.00%',
                                        '0.00%',
                                        '0.34%',
                                        '0.90%',
                                        '1.51%',
                                        '2.69%',
                                        'n/a'])
    assert udf.shape[0] == qdf.shape[0]  # same number of rows
    assert udf.shape[1] == qdf.shape[1]  # same number of cols
    for col in list(qdf):
        for row in range(0, qdf.shape[0]):
            same = False
            qel_str_type = isinstance(qdf[col][row], six.string_types)
            uel_str_type = isinstance(udf[col][row], six.string_types)
            assert qel_str_type == uel_str_type
            if qel_str_type:
                same = qdf[col][row] == udf[col][row]
            else:
                qel_flt_type = isinstance(qdf[col][row], float)
                uel_flt_type = isinstance(udf[col][row], float)
                assert qel_flt_type == uel_flt_type
                if qel_flt_type:
                    same = np.allclose([qdf[col][row]], [udf[col][row]])
            if not same:
                msg = '{} {} : [{}] {} [{}] {}'.format(col, row,
                                                       qdf[col][row],
                                                       type(qdf[col][row]),
                                                       udf[col][row],
                                                       type(udf[col][row]))
                assert msg == 'qdf element not equal to udf element'
    # TODO: remove the following debugging statements:
    # for col in sorted(list(udf)):
    #     print udf[col]
    # assert 1 == 2
