import os
import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame

from taxcalc.dropq.utils import *
from taxcalc.dropq import *
import json


@pytest.fixture(scope='session')
def puf_path(tests_path):
    """
    The path to the puf.csv taxpayer data file at repo root
    """
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.mark.parametrize("is_strict, return_json, growth_params",
                         [(True, False, False), (False, False, False),
                          (True, True, False), (False, True, True)])
def test_run_dropq_nth_year(is_strict, return_json, growth_params,
                            puf_1991_path):
    myvars = {}
    myvars['_II_em_cpi'] = False
    myvars['_II_rt4'] = [0.39, 0.40, 0.41]
    myvars['_II_rt3'] = [0.31, 0.32, 0.33]
    if growth_params:
        myvars['_factor_adjustment'] = [0.01]
    first_year = 2016
    user_mods = {first_year: myvars}

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)
    (mY_dec, mX_dec, df_dec, pdf_dec, cdf_dec, mY_bin, mX_bin, df_bin,
     pdf_bin, cdf_bin, fiscal_tots) = dropq.run_models(tax_data,
                                                       start_year=first_year,
                                                       is_strict=is_strict,
                                                       user_mods=user_mods,
                                                       return_json=return_json,
                                                       num_years=3)


@pytest.mark.parametrize("return_json", [True, False])
def test_run_dropq_nth_year_mtr(return_json, puf_1991_path):
    myvars = {}
    myvars['_STD'] = [[12600, 25200, 12600, 18600, 25300, 12600, 2100]]
    myvars['_AMT_trt1'] = [.0]
    myvars['_AMT_trt2'] = [.0]
    myvars['elastic_gdp'] = [.54]
    first_year = 2016
    user_mods = {first_year: myvars}

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)

    dropq.run_gdp_elast_models(tax_data, start_year=first_year,
                               user_mods=user_mods,
                               return_json=return_json,
                               num_years=3)


def test_only_growth_assumptions():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    myvars['_BE_inc'] = [0.8]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = only_growth_assumptions(user_mods, 2015)
    exp = {first_year: {'_factor_target': [0.02]}}
    assert ans == exp


def test_only_behavior_assumptions():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    myvars['_BE_inc'] = [0.8]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = only_behavior_assumptions(user_mods, 2015)
    exp = {first_year: {'_BE_inc': [0.8]}}
    assert ans == exp


def test_only_reform_mods():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    myvars['_BE_inc'] = [0.8]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = only_reform_mods(user_mods, 2015)
    exp = {first_year: {'_FICA_ss_trt': [0.15], '_II_em': [4700.0]}}
    assert ans == exp


def test_only_reform_mods2():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    myvars['_BE_inc'] = [0.8]
    myvars['ELASTICITY_GDP_WRT_AMTR'] = [.54]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = only_reform_mods(user_mods, 2015)
    exp = {first_year: {'_FICA_ss_trt': [0.15], '_II_em': [4700.0]}}
    assert ans == exp


def test_only_reform_mods_with_cpi():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    # A known CPI flag
    myvars['_II_em_cpi'] = False
    # A unknown CPI flag
    myvars['NOGOOD_cpi'] = False
    # A small parameter name
    myvars['NO'] = [0.42]
    myvars['_BE_inc'] = [0.8]
    myvars['ELASTICITY_GDP_WRT_AMTR'] = [.54]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = only_reform_mods(user_mods, 2015)
    exp = {first_year: {'_FICA_ss_trt': [0.15], '_II_em': [4700.0],
                        '_II_em_cpi': False}}
    assert ans == exp


def test_unknown_parameters_with_cpi():
    myvars = {}
    myvars['_FICA_ss_trt'] = [0.15]
    myvars['_factor_target'] = [0.02]
    myvars['_II_em'] = [4700.0]
    # A known CPI flag
    myvars['_II_em_cpi'] = False
    # A unknown CPI flag
    myvars['NOGOOD_cpi'] = False
    # A small parameter name
    myvars['NO'] = [0.42]
    myvars['_BE_inc'] = [0.8]
    myvars['ELASTICITY_GDP_WRT_AMTR'] = [.54]
    first_year = 2013
    user_mods = {first_year: myvars}
    ans = get_unknown_parameters(user_mods, 2015)
    exp = set(["NOGOOD_cpi", "NO", "ELASTICITY_GDP_WRT_AMTR"])
    assert set(ans) == exp


def test_format_macro_results():

    data = [[ 1.875e-03, 1.960e-03, 2.069e-03, 2.131e-03, 2.179e-03, 2.226e-03,
                2.277e-03, 2.324e-03, 2.375e-03, 2.426e-03, 2.184e-03, 2.806e-03],
            [ 2.538e-04, 4.452e-04, 6.253e-04, 7.886e-04, 9.343e-04, 1.064e-03,
                1.180e-03, 1.284e-03, 1.378e-03, 1.463e-03, 9.419e-04, 2.224e-03],
            [ 5.740e-03, 5.580e-03, 5.524e-03, 5.347e-03, 5.161e-03, 5.011e-03,
                4.907e-03, 4.818e-03, 4.768e-03, 4.739e-03, 5.160e-03, 4.211e-03],
            [ 2.883e-03, 2.771e-03, 2.721e-03, 2.620e-03, 2.520e-03, 2.440e-03,
                2.384e-03, 2.337e-03, 2.309e-03, 2.292e-03, 2.528e-03, 2.051e-03],
            [ -1.012e-03, -8.141e-04, -6.552e-04, -4.912e-04, -3.424e-04, -2.150e-04,
            -1.081e-04, -1.372e-05, 6.513e-05, 1.336e-04, -3.450e-04, 7.538e-04],
            [ 3.900e-03, 3.143e-03, 2.532e-03, 1.900e-03, 1.325e-03, 8.325e-04,
                4.189e-04, 5.315e-05, -2.525e-04, -5.180e-04, 1.337e-03, -2.917e-03],
            [ -2.577e-02, -2.517e-02, -2.507e-02, -2.464e-02, -2.419e-02, -2.388e-02,
            -2.368e-02, -2.350e-02, -2.342e-02, -2.341e-02, -2.427e-02, -2.275e-02]]

    data = np.array(data)
    diff_table = format_macro_results(data)

    x = {'GDP': ['0.002', '0.002', '0.002', '0.002', '0.002', '0.002',
                 '0.002', '0.002', '0.002', '0.002', '0.002', '0.003'],
         'Consumption': ['0.000', '0.000', '0.001', '0.001', '0.001',
                     '0.001', '0.001', '0.001', '0.001', '0.001', '0.001',
                     '0.002'], 'Interest Rates': ['0.004', '0.003', '0.003',
                     '0.002', '0.001', '0.001', '0.000', '0.000', '-0.000',
                     '-0.001', '0.001', '-0.003'],
         'Total Taxes': ['-0.026', '-0.025', '-0.025', '-0.025', '-0.024',
                         '-0.024', '-0.024', '-0.024', '-0.023', '-0.023',
                         '-0.024', '-0.023'], 'Wages': ['-0.001', '-0.001',
                         '-0.001', '-0.000', '-0.000', '-0.000', '-0.000',
                         '-0.000', '0.000', '0.000', '-0.000', '0.001'],
        'Investment': ['0.006', '0.006', '0.006', '0.005', '0.005', '0.005',
                       '0.005', '0.005', '0.005', '0.005', '0.005', '0.004'],
        'Hours Worked': ['0.003', '0.003', '0.003', '0.003', '0.003', '0.002',
                         '0.002', '0.002', '0.002', '0.002', '0.003', '0.002']}

    assert diff_table == x


def test_create_json_blob():
    _types = [int] * 3
    df = DataFrame(data=[[1,2,3],[4,5,6],[7,8,9]], columns=['a','b','c'])
    ans = create_json_blob(df, column_types=_types)
    exp = {'0': {'a': '1', 'b': '2', 'c': '3'},
           '1': {'a': '4', 'b': '5', 'c': '6'},
           '2': {'a': '7', 'b': '8', 'c': '9'}}
    assert ans == json.dumps(exp)


def test_create_json_blob_column_names():
    _types = [int] * 3
    df = DataFrame(data=[[1,2,3],[4,5,6],[7,8,9]], columns=['a','b','c'])
    ans = create_json_blob(df, column_names=['d', 'e', 'f'],
                           column_types=_types)
    exp = {'0': {'d': '1', 'e': '2', 'f': '3'},
           '1': {'d': '4', 'e': '5', 'f': '6'},
           '2': {'d': '7', 'e': '8', 'f': '9'}}
    assert ans == json.dumps(exp)

def test_create_json_blob_row_names():
    _types = [int] * 3
    df = DataFrame(data=[[1,2,3],[4,5,6],[7,8,9]], columns=['a','b','c'])
    ans = create_json_blob(df, row_names=['4', '5', '6'],
                           column_types=_types)
    exp = {'4': {'a': '1', 'b': '2', 'c': '3'},
           '5': {'a': '4', 'b': '5', 'c': '6'},
           '6': {'a': '7', 'b': '8', 'c': '9'}}
    assert ans == json.dumps(exp)

def test_create_json_blob_float():
    df = DataFrame(data=[[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]], columns=['a','b','c'])
    ans = create_json_blob(df)
    exp = {'0': {'a': '1.00', 'b': '2.00', 'c': '3.00'},
           '1': {'a': '4.00', 'b': '5.00', 'c': '6.00'},
           '2': {'a': '7.00', 'b': '8.00', 'c': '9.00'}}
    assert ans == json.dumps(exp)

def test_create_json_table():
    df = DataFrame(data=[[1.,2,3],[4.,5,6],[7,8,9]], columns=['a','b','c'])
    ans = create_json_table(df)
    exp = {'0': ['1.00', '2', '3'],
           '1': ['4.00', '5', '6'],
           '2': ['7.00', '8', '9']}
    assert ans == exp

def test_format_print_not_implemented():
    x = np.array([1], dtype='i4')
    with pytest.raises(NotImplementedError):
        format_print(x[0], x.dtype, 2)

@pytest.mark.parametrize("groupby, result_type",
                         [("small_income_bins", "weighted_sum"),
                          ("large_income_bins", "weighted_sum"), 
                          ("large_income_bins", "weighted_avg"), 
                          ("other_income_bins", "weighted_avg"),
                          ("large_income_bins", "other_avg")] )
def test_create_dropq_dist_table_groupby_options(groupby, result_type, puf_1991_path):
    year_n = 0
    start_year = 2016
    is_strict = False
    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)
    suffix = '_bin'
    myvars = {}
    myvars['_II_em_cpi'] = False
    myvars['_II_rt4'] = [0.39, 0.40, 0.41]
    myvars['_II_rt3'] = [0.31, 0.32, 0.33]
    first_year = start_year
    user_mods = {first_year: myvars}

    soit_baseline, soit_reform, mask = calculate_baseline_and_reform(
        year_n, start_year, is_strict, tax_data, user_mods)

    df1, df2 = drop_records(soit_baseline, soit_reform, mask)
    dec_sum = (df2['tax_diff_dec'] * df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin'] * df2['s006']).sum()
    pr_dec_sum = (df2['payrolltax_diff_dec'] * df2['s006']).sum()
    pr_bin_sum = (df2['payrolltax_diff_bin'] * df2['s006']).sum()
    combined_dec_sum = (df2['combined_diff_dec'] * df2['s006']).sum()
    combined_bin_sum = (df2['combined_diff_bin'] * df2['s006']).sum()

    if groupby == "other_income_bins" or result_type == "other_avg":
        with pytest.raises(ValueError):
            create_dropq_distribution_table(df2, groupby=groupby,
                                            result_type=result_type,
                                            suffix=suffix)
    else:
        create_dropq_distribution_table(df2, groupby=groupby,
                                        result_type=result_type, suffix=suffix)

    #create_dropq_distribution_table(df2, groupby=groupby, result_type=result_type, suffix='_bin')
    #create_dropq_distribution_table(df2, groupby="large_income_bins", result_type, suffix)
    #create_dropq_distribution_table(calc, groupby="large_income_bins", result_type="weighted_average", suffix)
    #with pytest.raises(NotImplementedError):
    #    create_dropq_distribution_table(calc, groupby="other_income_bins", result_type, suffix)"""


@pytest.mark.parametrize("groupby, res_col",
                         [("weighted_deciles", "tax_diff"),
                          ("webapp_income_bins", "tax_diff"), 
                          ("webapp_income_bins", "tax_diff"), 
                          ("webapp_income_bins", "tax_diff"),
                          ("other_deciles", "tax_diff")] )
def test_create_dropq_diff_table_groupby_options(groupby, res_col, puf_1991_path):
    year_n = 0
    start_year = 2016
    is_strict = False
    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)
    suffix = '_bin'
    myvars = {}
    myvars['_II_em_cpi'] = False
    myvars['_II_rt4'] = [0.39, 0.40, 0.41]
    myvars['_II_rt3'] = [0.31, 0.32, 0.33]
    first_year = start_year
    user_mods = {first_year: myvars}

    soit_baseline, soit_reform, mask = calculate_baseline_and_reform(
        year_n, start_year, is_strict, tax_data, user_mods)

    df1, df2 = drop_records(soit_baseline, soit_reform, mask)
    dec_sum = (df2['tax_diff_dec'] * df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin'] * df2['s006']).sum()
    pr_dec_sum = (df2['payrolltax_diff_dec'] * df2['s006']).sum()
    pr_bin_sum = (df2['payrolltax_diff_bin'] * df2['s006']).sum()
    combined_dec_sum = (df2['combined_diff_dec'] * df2['s006']).sum()
    combined_bin_sum = (df2['combined_diff_bin'] * df2['s006']).sum()

    if groupby == "other_deciles":
        with pytest.raises(ValueError):
            create_dropq_difference_table(df1, df2, groupby=groupby,
                                          res_col=res_col, diff_col='_iitax',
                                          suffix='_dec',
                                          wsum=dec_sum)
    else:
        create_dropq_difference_table(df1, df2, groupby=groupby,
                                      res_col=res_col, diff_col='_iitax',
                                      suffix='_dec',
                                      wsum=dec_sum)
