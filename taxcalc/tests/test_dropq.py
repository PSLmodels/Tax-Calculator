import os
import json
import tempfile
import numpy as np
import numpy.testing as npt
import pandas as pd
from pandas import DataFrame, Series
import pytest
from taxcalc.dropq.dropq_utils import *
from taxcalc.dropq import *
from taxcalc import Policy, Records, Calculator
from taxcalc import multiyear_diagnostic_table


REFORM_CONTENTS = """
// Specify AGI exclusion of some fraction of investment income
{
  "policy": {
    // specify fraction of investment income that can be excluded from AGI
    "_ALD_InvInc_ec_rt": {"2016": [0.50]},

    // specify "investment income" base to mean the sum of three things:
    // taxable interest (e00300), qualified dividends (e00650), and
    // long-term capital gains (p23250) [see functions.py for other
    // types of investment income that can be included in the base]
    "param_code": {"ALD_InvInc_ec_base_code":
                   ||returned_value = e00300 + e00650 + p23250||},

    "_ALD_InvInc_ec_base_code_active": {"2016": [true]}
    // the dollar exclusion is the product of the base defined by code
    // and the fraction defined above
  },
  "behavior": {
    "_BE_sub": {"2016": [0.25]}
  },
  "consumption": {
    "_MPC_e20400": {"2016": [0.01]}
  },
  "growth": {
  }
}
"""


ASSUMP_CONTENTS = """
{
  "behavior": {
    "_BE_sub": {"2016": [0.25]}
  },
  "consumption": {
    "_MPC_e20400": {"2016": [0.01]}
  },
  "growth": {
  }
}
"""


@pytest.yield_fixture
def reform_file():
    """
    Temporary reform file for testing dropq functions with reform file.
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


@pytest.yield_fixture
def assump_file():
    """
    Temporary assump file for testing dropq functions with assump file.
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


@pytest.fixture(scope='session')
def puf_path(tests_path):
    """
    The path to the puf.csv taxpayer data file at repo root
    """
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.mark.parametrize("is_strict, rjson, growth_params, behavior_params",
                         [(True, False, False, False),
                          (False, False, False, False),
                          (True, True, False, True),
                          (False, True, True, True)])
def test_run_dropq_nth_year(is_strict, rjson, growth_params,
                            behavior_params, puf_1991_path):
    myvars = {}
    myvars['_II_em_cpi'] = False
    myvars['_II_rt4'] = [0.39, 0.40, 0.41]
    myvars['_II_rt3'] = [0.31, 0.32, 0.33]
    if growth_params:
        myvars['_factor_adjustment'] = [0.01]
    if behavior_params:
        myvars['_BE_inc'] = [0.8]
    if is_strict:
        myvars['unknown_param'] = [0.01]
    first = 2016
    user_mods = {first: myvars}

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)

    if is_strict:
        with pytest.raises(ValueError):
            dropq.run_models(tax_data, start_year=first,
                             is_strict=is_strict, user_mods=user_mods,
                             return_json=rjson, num_years=3)
    else:
        (_, _, _, _, _, _, _, _,
         _, _, fiscal_tots) = dropq.run_models(tax_data,
                                               start_year=first,
                                               is_strict=is_strict,
                                               user_mods=user_mods,
                                               return_json=rjson,
                                               num_years=3)
        assert fiscal_tots is not None


@pytest.mark.parametrize("is_strict", [True, False])
def test_run_dropq_nth_year_from_file(is_strict, puf_1991_path,
                                      reform_file, assump_file):

    user_reform = Calculator.read_json_param_files(reform_file.name,
                                                   assump_file.name)
    user_mods = user_reform

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)
    first = 2016
    rjson = True

    (_, _, _, _, _, _, _, _,
     _, _, fiscal_tots) = dropq.run_models(tax_data,
                                           start_year=first,
                                           is_strict=is_strict,
                                           user_mods=user_mods,
                                           return_json=rjson,
                                           num_years=3)

    assert fiscal_tots is not None


def test_run_dropq_nth_year_mtr_from_file(puf_1991_path, reform_file):

    user_reform = Calculator.read_json_param_files(reform_file.name, None)
    first_year = 2016
    elast_params = {'elastic_gdp': [.54, .56, .58]}
    user_reform[0][first_year].update(elast_params)

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)

    ans = dropq.run_gdp_elast_models(tax_data, start_year=first_year,
                                     is_strict=True,
                                     user_mods=user_reform,
                                     return_json=True,
                                     num_years=3)

    assert len(ans) == 2  # num_years-1 calculations done


@pytest.mark.requires_pufcsv
def test_full_dropq_puf(puf_path):

    myvars = {}
    myvars['_II_rt4'] = [0.39, 0.40, 0.41]
    myvars['_PT_rt4'] = [0.39, 0.40, 0.41]
    myvars['_II_rt3'] = [0.31, 0.32, 0.33]
    myvars['_PT_rt3'] = [0.31, 0.32, 0.33]
    first = 2016
    user_mods = {first: myvars}

    nyrs = 2

    # Create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    clp.implement_reform(user_mods)
    # Create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_path)
    # Create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=rec)
    calc.increment_year()
    calc.increment_year()
    calc.increment_year()
    # Create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = multiyear_diagnostic_table(calc, nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    assert taxes_fullsample is not None
    # Create a Public Use File object
    tax_data = pd.read_csv(puf_path)
    (mY_dec, _, _, _, _, _, _, _,
     _, _, fiscal_tots) = dropq.run_models(tax_data,
                                           start_year=first,
                                           user_mods=user_mods,
                                           return_json=False,
                                           num_years=nyrs)
    pure_reform_revenue = taxes_fullsample.loc[first]
    dropq_reform_revenue = mY_dec['_combined_dec_0'].loc['sums']
    dropq_reform_revenue *= 1e-9  # convert to billions of dollars
    diff = abs(pure_reform_revenue - dropq_reform_revenue)
    # Assert that dropq revenue is similar to the "pure" calculation
    assert diff / pure_reform_revenue < 0.01
    # Assert that Reform - Baseline = Reported Delta
    delta_yr0 = fiscal_tots[0]
    baseline_yr0 = fiscal_tots[1]
    reform_yr0 = fiscal_tots[2]
    diff_yr0 = (reform_yr0.loc['combined_tax'] -
                baseline_yr0.loc['combined_tax']).values
    delta_yr0 = delta_yr0.loc['combined_tax'].values
    npt.assert_allclose(diff_yr0, delta_yr0)


@pytest.mark.parametrize("is_strict, rjson, growth_params, no_elast",
                         [(True, True, False, False), (True, True, True, True),
                          (False, False, False, False),
                          (False, True, True, False)])
def test_run_dropq_nth_year_mtr(is_strict, rjson, growth_params, no_elast,
                                puf_1991_path):
    myvars = {}
    myvars['_STD'] = [[12600, 25200, 12600, 18600, 25300, 12600]]
    myvars['_AMT_rt1'] = [.0]
    myvars['_AMT_rt2'] = [.0]
    myvars['elastic_gdp'] = [.54, .56]
    if growth_params:
        myvars['_factor_adjustment'] = [0.01]
    if is_strict:
        myvars['unknown_param'] = [0.01]
    if no_elast:
        del myvars['elastic_gdp']
    first_year = 2016
    user_mods = {first_year: myvars}

    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)

    if is_strict or no_elast:
        with pytest.raises(ValueError):
            dropq.run_gdp_elast_models(tax_data, start_year=first_year,
                                       is_strict=is_strict,
                                       user_mods=user_mods,
                                       return_json=rjson,
                                       num_years=3)
    else:
        dropq.run_gdp_elast_models(tax_data, start_year=first_year,
                                   is_strict=is_strict,
                                   user_mods=user_mods,
                                   return_json=rjson,
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
    final_ans = []
    for a in ans.values():
        final_ans += a
    exp = set(["NOGOOD_cpi", "NO", "ELASTICITY_GDP_WRT_AMTR"])
    assert set(final_ans) == exp


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
    diff_table = format_macro_results(data)

    x = {'GDP': ['0.002', '0.002', '0.002', '0.002', '0.002', '0.002',
                 '0.002', '0.002', '0.002', '0.002', '0.002', '0.003'],
         'Consumption': ['0.000', '0.000', '0.001', '0.001', '0.001',
                         '0.001', '0.001', '0.001', '0.001', '0.001', '0.001',
                         '0.002'],
         'Interest Rates': ['0.004', '0.003',
                            '0.003', '0.002', '0.001', '0.001', '0.000',
                            '0.000', '-0.000', '-0.001', '0.001', '-0.003'],
         'Total Taxes': ['-0.026', '-0.025', '-0.025', '-0.025', '-0.024',
                         '-0.024', '-0.024', '-0.024', '-0.023', '-0.023',
                         '-0.024', '-0.023'],
         'Wages': ['-0.001', '-0.001',
                   '-0.001', '-0.000', '-0.000', '-0.000', '-0.000',
                   '-0.000', '0.000', '0.000', '-0.000', '0.001'],
         'Investment': ['0.006', '0.006', '0.006', '0.005', '0.005', '0.005',
                        '0.005', '0.005', '0.005', '0.005', '0.005', '0.004'],
         'Hours Worked': ['0.003', '0.003', '0.003', '0.003', '0.003', '0.002',
                          '0.002', '0.002', '0.002', '0.002', '0.003',
                          '0.002']}

    assert diff_table == x

    diff_df = format_macro_results(data, return_json=False)

    assert diff_df.equals(DataFrame(data))


def test_create_json_blob():
    _types = [int] * 3
    df = DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                   columns=['a', 'b', 'c'])
    ans = create_json_blob(df, column_types=_types)
    exp = {'0': {'a': '1', 'b': '2', 'c': '3'},
           '1': {'a': '4', 'b': '5', 'c': '6'},
           '2': {'a': '7', 'b': '8', 'c': '9'}}
    assert ans == json.dumps(exp)


def test_create_json_blob_column_names():
    _types = [int] * 3
    df = DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                   columns=['a', 'b', 'c'])
    ans = create_json_blob(df, column_names=['d', 'e', 'f'],
                           column_types=_types)
    exp = {'0': {'d': '1', 'e': '2', 'f': '3'},
           '1': {'d': '4', 'e': '5', 'f': '6'},
           '2': {'d': '7', 'e': '8', 'f': '9'}}
    assert ans == json.dumps(exp)


def test_create_json_blob_row_names():
    _types = [int] * 3
    df = DataFrame(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                   columns=['a', 'b', 'c'])
    ans = create_json_blob(df, row_names=['4', '5', '6'],
                           column_types=_types)
    exp = {'4': {'a': '1', 'b': '2', 'c': '3'},
           '5': {'a': '4', 'b': '5', 'c': '6'},
           '6': {'a': '7', 'b': '8', 'c': '9'}}
    assert ans == json.dumps(exp)


def test_create_json_blob_float():
    df = DataFrame(data=[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]],
                   columns=['a', 'b', 'c'])
    ans = create_json_blob(df)
    exp = {'0': {'a': '1.00', 'b': '2.00', 'c': '3.00'},
           '1': {'a': '4.00', 'b': '5.00', 'c': '6.00'},
           '2': {'a': '7.00', 'b': '8.00', 'c': '9.00'}}
    assert ans == json.dumps(exp)


def test_create_json_table():
    df = DataFrame(data=[[1., 2, 3], [4, 5, 6], [7, 8, 9]],
                   columns=['a', 'b', 'c'])
    ans = create_json_table(df)
    exp = {'0': ['1.00', '2', '3'],
           '1': ['4.00', '5', '6'],
           '2': ['7.00', '8', '9']}
    assert ans == exp


def test_chooser():
    sr = Series(data=[False] * 100, name="name")
    with pytest.raises(ValueError):
        chooser(sr)

    sr[0:3] = True
    chooser(sr)


def test_format_print_not_implemented():
    x = np.array([1], dtype='i2')
    with pytest.raises(NotImplementedError):
        format_print(x[0], x.dtype, 2)


@pytest.mark.parametrize("groupby, result_type",
                         [("small_income_bins", "weighted_sum"),
                          ("large_income_bins", "weighted_sum"),
                          ("large_income_bins", "weighted_avg"),
                          ("other_income_bins", "weighted_avg"),
                          ("large_income_bins", "other_avg")])
def test_create_dropq_dist_table_groupby_options(groupby, result_type,
                                                 puf_1991_path):
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

    _, df2 = drop_records(soit_baseline, soit_reform, mask)

    if groupby == "other_income_bins" or result_type == "other_avg":
        with pytest.raises(ValueError):
            create_dropq_distribution_table(df2, groupby=groupby,
                                            result_type=result_type,
                                            suffix=suffix)
    else:
        create_dropq_distribution_table(df2, groupby=groupby,
                                        result_type=result_type, suffix=suffix)


@pytest.mark.parametrize("groupby, res_col",
                         [("weighted_deciles", "tax_diff"),
                          ("webapp_income_bins", "tax_diff"),
                          ("small_income_bins", "tax_diff"),
                          ("large_income_bins", "tax_diff"),
                          ("other_deciles", "tax_diff")])
def test_create_dropq_diff_table_groupby_options(groupby, res_col,
                                                 puf_1991_path):
    year_n = 0
    start_year = 2016
    is_strict = False
    # Create a Public Use File object
    tax_data = pd.read_csv(puf_1991_path)
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
