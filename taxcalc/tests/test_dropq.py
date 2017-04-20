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
  "title": "",
  "author": "",
  "date": "",
  "policy": {
    // specify fraction of investment income that can be excluded from AGI
    "_ALD_InvInc_ec_rt": {"2016": [0.50]}
  }
}
"""


ASSUMP_CONTENTS = """
{
  "title": "",
  "author": "",
  "date": "",
  "consumption": {
    "_MPC_e20400": {"2016": [0.01]}
  },
  "behavior": {
    "_BE_sub": {"2016": [0.25]}
  },
  "growdiff_baseline": {
  },
  "growdiff_response": {
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


def test_check_user_mods(puf_1991_path, reform_file, assump_file):
    usermods = list()
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods = Calculator.read_json_param_files(reform_file.name,
                                                assump_file.name)
    with pytest.raises(ValueError):
        check_user_mods(usermods)
    usermods['gdp_elasticity'] = dict()
    check_user_mods(usermods)
    usermods['unknown_key'] = dict()
    with pytest.raises(ValueError):
        check_user_mods(usermods)


@pytest.mark.parametrize("rjson", [(True), (False)])
def test_run_model_with_usermods_from_code(puf_1991_path, rjson):
    fyr = 2016
    usermods = dict()
    reform = dict()
    reform['_II_em_cpi'] = False
    reform['_II_rt4'] = [0.39, 0.40, 0.41]
    reform['_II_rt3'] = [0.31, 0.32, 0.33]
    usermods['policy'] = {fyr: reform}
    usermods['consumption'] = {fyr: {'_MPC_e18400': [0.05]}}
    usermods['behavior'] = {}
    usermods['growdiff_baseline'] = {fyr: {'_ABOOK': [0.01]}}
    usermods['growdiff_response'] = {fyr: {'_AINTS': [0.02]}}
    usermods['gdp_elasticity'] = {'value': 0.0}
    # for this usermods the computed seed = 3195176465
    tax_data = pd.read_csv(puf_1991_path)
    (_, _, _, _, _, _, _, _,
     _, _, fiscal_tots) = dropq.run_model(tax_data,
                                          start_year=fyr,
                                          user_mods=usermods,
                                          return_json=rjson,
                                          num_years=3)
    assert fiscal_tots is not None


def test_run_model_with_usermods_from_files(puf_1991_path,
                                            reform_file, assump_file):
    usermods = Calculator.read_json_param_files(reform_file.name,
                                                assump_file.name)
    usermods['gdp_elasticity'] = dict()
    # for this usermods the computed seed = 4109528928
    fyr = 2016
    tax_data = pd.read_csv(puf_1991_path)
    (_, _, _, _, _, _, _, _,
     _, _, fiscal_tots) = dropq.run_model(tax_data,
                                          start_year=fyr,
                                          user_mods=usermods,
                                          return_json=True,
                                          num_years=3)
    assert fiscal_tots is not None


def test_calculate_baseline_and_reform_error(puf_1991_path,
                                             reform_file, assump_file):
    usermods = Calculator.read_json_param_files(reform_file.name,
                                                assump_file.name)
    usermods['behavior'] = {2016: {'_BE_sub': [0.20]}}
    usermods['growdiff_response'] = {2020: {'_ABOOK': [0.01]}}
    usermods['gdp_elasticity'] = dict()
    tax_data = pd.read_csv(puf_1991_path)
    with pytest.raises(ValueError):
        calculate_baseline_and_reform(2, 2015, tax_data, usermods)


def test_run_nth_year_model(puf_1991_path, reform_file, assump_file):
    usermods = Calculator.read_json_param_files(reform_file.name,
                                                assump_file.name)
    usermods['gdp_elasticity'] = dict()
    tax_data = pd.read_csv(puf_1991_path)
    year_n = 2
    start_year = 2016
    non_json_results = dropq.run_nth_year_model(year_n, start_year,
                                                tax_data, usermods,
                                                return_json=False)
    assert len(non_json_results) == 13


@pytest.mark.parametrize("rjson", [True, False])
def test_run_gdp_elast_model(puf_1991_path, rjson,
                             reform_file, assump_file):
    usermods = Calculator.read_json_param_files(reform_file.name,
                                                assump_file.name)
    usermods['gdp_elasticity'] = {'value': 0.36}
    fyr = 2016
    nyrs = 3
    tax_data = pd.read_csv(puf_1991_path)
    ans = dropq.run_gdp_elast_model(tax_data, start_year=fyr,
                                    user_mods=usermods,
                                    return_json=rjson,
                                    num_years=nyrs)
    assert len(ans) == (nyrs - 1)  # number of annual calculations done


@pytest.mark.requires_pufcsv
def test_dropq_with_full_puf(puf_path):
    # specify usermods dictionary in code
    fyr = 2016
    reforms = dict()
    reforms['_II_rt4'] = [0.39, 0.40, 0.41]
    reforms['_PT_rt4'] = [0.39, 0.40, 0.41]
    reforms['_II_rt3'] = [0.31, 0.32, 0.33]
    reforms['_PT_rt3'] = [0.31, 0.32, 0.33]
    usermods = dict()
    usermods['policy'] = {fyr: reforms}
    usermods['consumption'] = {}
    usermods['behavior'] = {}
    usermods['growdiff_baseline'] = {}
    usermods['growdiff_response'] = {}
    usermods['gdp_elasticity'] = {}
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    clp.implement_reform(usermods['policy'])
    # create a Records object (rec) containing all puf.csv input records
    rec = Records(data=puf_path)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=rec)
    calc.increment_year()
    calc.increment_year()
    calc.increment_year()
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    nyrs = 2
    adt = multiyear_diagnostic_table(calc, nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    assert taxes_fullsample is not None
    # create a Public Use File object
    tax_data = pd.read_csv(puf_path)
    # call dropq.run_model
    (mY_dec, _, _, _, _, _, _, _,
     _, _, fiscal_tots) = dropq.run_model(tax_data,
                                          start_year=fyr,
                                          user_mods=usermods,
                                          return_json=False,
                                          num_years=nyrs)
    fulls_reform_revenue = taxes_fullsample.loc[fyr]
    dropq_reform_revenue = mY_dec['combined_dec_0'].loc['sums']
    dropq_reform_revenue *= 1e-9  # convert to billions of dollars
    diff = abs(fulls_reform_revenue - dropq_reform_revenue)
    # assert that dropq revenue is similar to the fullsample calculation
    assert diff / fulls_reform_revenue < 0.01
    # assert that Reform - Baseline = Reported Delta
    delta_yr0 = fiscal_tots[0]
    baseline_yr0 = fiscal_tots[1]
    reform_yr0 = fiscal_tots[2]
    diff_yr0 = (reform_yr0.loc['combined_tax'] -
                baseline_yr0.loc['combined_tax']).values
    delta_yr0 = delta_yr0.loc['combined_tax'].values
    npt.assert_allclose(diff_yr0, delta_yr0)


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
    start_year = 2016
    year_n = 0
    reforms = dict()
    reforms['_II_em_cpi'] = False
    reforms['_II_rt4'] = [0.39, 0.40, 0.41]
    reforms['_II_rt3'] = [0.31, 0.32, 0.33]
    usermods = dict()
    usermods['policy'] = {start_year: reforms}
    usermods['consumption'] = dict()
    usermods['behavior'] = dict()
    usermods['growdiff_baseline'] = dict()
    usermods['growdiff_response'] = dict()
    usermods['gdp_elasticity'] = dict()
    tax_data = pd.read_csv(puf_1991_path)
    (soit_baseline, soit_reform,
     mask) = calculate_baseline_and_reform(year_n, start_year,
                                           tax_data, usermods)
    _, df2 = drop_records(soit_baseline, soit_reform, mask)
    if groupby == "other_income_bins" or result_type == "other_avg":
        with pytest.raises(ValueError):
            create_dropq_distribution_table(df2, groupby=groupby,
                                            result_type=result_type,
                                            suffix='_bin')
    else:
        create_dropq_distribution_table(df2, groupby=groupby,
                                        result_type=result_type,
                                        suffix='_bin')


@pytest.mark.parametrize("groupby, res_col",
                         [("weighted_deciles", "tax_diff"),
                          ("webapp_income_bins", "tax_diff"),
                          ("small_income_bins", "tax_diff"),
                          ("large_income_bins", "tax_diff"),
                          ("other_deciles", "tax_diff")])
def test_create_dropq_diff_table_groupby_options(groupby, res_col,
                                                 puf_1991_path):
    start_year = 2016
    year_n = 0
    reforms = dict()
    reforms['_II_em_cpi'] = False
    reforms['_II_rt4'] = [0.39, 0.40, 0.41]
    reforms['_II_rt3'] = [0.31, 0.32, 0.33]
    usermods = dict()
    usermods['policy'] = {start_year: reforms}
    usermods['consumption'] = dict()
    usermods['behavior'] = dict()
    usermods['growdiff_baseline'] = dict()
    usermods['growdiff_response'] = dict()
    usermods['gdp_elasticity'] = dict()
    tax_data = pd.read_csv(puf_1991_path)
    (soit_baseline, soit_reform,
     mask) = calculate_baseline_and_reform(year_n, start_year,
                                           tax_data, usermods)
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
