import os
import sys
import filecmp
import tempfile
cur_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(cur_path, "../../"))
sys.path.append(os.path.join(cur_path, "../"))
import numpy as np
import pandas as pd
import pytest
import numpy.testing as npt
from pandas import DataFrame, Series
from pandas.util.testing import assert_frame_equal
from pandas.util.testing import assert_series_equal
from numba import jit, vectorize, guvectorize
from taxcalc import *
from csv_to_ascii import ascii_output


data = [[1.0, 2, 'a'],
        [-1.0, 4, 'a'],
        [3.0, 6, 'a'],
        [2.0, 4, 'b'],
        [3.0, 6, 'b']]

data_float = [[1.0, 2, 'a'],
              [-1.0, 4, 'a'],
              [0.0000000001, 3, 'a'],
              [-0.0000000001, 1, 'a'],
              [3.0, 6, 'a'],
              [2.0, 4, 'b'],
              [0.0000000001, 3, 'b'],
              [-0.0000000001, 1, 'b'],
              [3.0, 6, 'b']]

irates = {1991: 0.015, 1992: 0.020, 1993: 0.022, 1994: 0.020, 1995: 0.021,
          1996: 0.022, 1997: 0.023, 1998: 0.024, 1999: 0.024, 2000: 0.024,
          2001: 0.024, 2002: 0.024}


def test_expand_1D_short_array():
    x = np.array([4, 5, 9], dtype='i4')
    exp2 = np.array([9.0 * math.pow(1.02, i) for i in range(1, 8)])
    exp1 = np.array([4, 5, 9])
    exp = np.zeros(10)
    exp[:3] = exp1
    exp[3:] = exp2
    res = expand_1D(x, inflate=True, inflation_rates=[0.02] * 10, num_years=10)
    assert(np.allclose(exp.astype(x.dtype, casting='unsafe'), res))


def test_expand_1D_variable_rates():
    x = np.array([4, 5, 9], dtype='f4')
    irates = [0.02, 0.02, 0.03, 0.035]
    exp2 = []
    cur = 9.0
    exp = np.array([4, 5, 9, 9 * 1.03, 9 * 1.03 * 1.035])
    res = expand_1D(x, inflate=True, inflation_rates=irates, num_years=5)
    assert(np.allclose(exp.astype('f4', casting='unsafe'), res))


def test_expand_1D_scalar():
    x = 10.0
    exp = np.array([10.0 * math.pow(1.02, i) for i in range(0, 10)])
    res = expand_1D(x, inflate=True, inflation_rates=[0.02] * 10, num_years=10)
    assert(np.allclose(exp, res))


def test_expand_1D_accept_None():
    x = [4., 5., None]
    irates = [0.02, 0.02, 0.03, 0.035]
    exp = []
    cur = 5.0 * 1.02
    exp = [4., 5., cur]
    cur *= 1.03
    exp.append(cur)
    cur *= 1.035
    exp.append(cur)
    exp = np.array(exp)
    res = expand_array(x, inflate=True, inflation_rates=irates, num_years=5)
    assert(np.allclose(exp.astype('f4', casting='unsafe'), res))


def test_expand_2D_short_array():
    x = np.array([[1, 2, 3]], dtype='f8')
    val = np.array([1, 2, 3], dtype='f8')
    exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, inflate=True, inflation_rates=[0.02] * 5, num_years=5)
    assert(np.allclose(exp, res))


def test_expand_2D_variable_rates():
    x = np.array([[1, 2, 3]], dtype='f8')
    cur = np.array([1, 2, 3], dtype='f8')
    irates = [0.02, 0.02, 0.02, 0.03, 0.035]

    exp2 = []
    for i in range(0, 4):
        idx = i + len(x) - 1
        cur = np.array(cur * (1.0 + irates[idx]))
        print("cur is ", cur)
        exp2.append(cur)

    # exp2 = np.array([val * math.pow(1.02, i) for i in range(1, 5)])
    exp1 = np.array([1, 2, 3], dtype='f8')
    exp = np.zeros((5, 3))
    exp[:1] = exp1
    exp[1:] = exp2
    res = expand_2D(x, inflate=True, inflation_rates=irates, num_years=5)
    npt.assert_array_equal(res, np.array(exp).astype('f8', casting='unsafe'))
    assert(np.allclose(exp, res))


def test_create_tables():
    # Default Plans
    # Create a Public Use File object
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta_path = os.path.join(cur_path, "../../tax_all1991_puf.gz")
    # Create a default Parameters object
    params1 = Parameters(start_year=1991, inflation_rates=irates)
    records1 = Records(tax_dta_path)
    # Create a Calculator
    calc1 = Calculator(params=params1, records=records1)
    calc1.calc_all()

    # User specified Plans
    user_mods = '{"1991": {"_II_rt4": [0.56]}}'
    params2 = Parameters(start_year=1991, inflation_rates=irates)
    records2 = Records(tax_dta_path)
    # Create a Calculator
    calc2 = calculator(params=params2, records=records2, mods=user_mods)

    calc2.calc_all()

    t2 = create_distribution_table(calc2, groupby="small_income_bins",
                                   result_type="weighted_sum")
    # make large income bins table
    tdiff = create_difference_table(calc1, calc2, groupby="large_income_bins")
    # make webapp income bins table
    tdiff_webapp = create_difference_table(calc1, calc2,
                                           groupby="webapp_income_bins")


def test_weighted_count_lt_zero():
    df1 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = DataFrame(data=data_float, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_lt_zero, 'tax_diff')
    exp = Series(data=[4, 0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count_gt_zero():
    df1 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df1.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)
    df2 = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df2.groupby('label')
    diffs = grped.apply(weighted_count_gt_zero, 'tax_diff')
    exp = Series(data=[8, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_count():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_count)
    exp = Series(data=[12, 10], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_mean():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_mean, 'tax_diff')
    exp = Series(data=[16.0 / 12.0, 26.0 / 10.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_sum():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_sum, 'tax_diff')
    exp = Series(data=[16.0, 26.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_inc():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_inc, 'tax_diff')
    exp = Series(data=[8. / 12., 1.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_perc_dec():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_perc_dec, 'tax_diff')
    exp = Series(data=[4. / 12., 0.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_weighted_share_of_total():
    df = DataFrame(data=data, columns=['tax_diff', 's006', 'label'])
    grped = df.groupby('label')
    diffs = grped.apply(weighted_share_of_total, 'tax_diff', 42.0)
    exp = Series(data=[16.0 / 42., 26.0 / 42.0], index=['a', 'b'])
    exp.index.name = 'label'
    assert_series_equal(exp, diffs)


def test_add_income_bins():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])
    bins = [-1e14, 0, 9999, 19999, 29999, 39999, 49999, 74999, 99999,
            200000, 1e14]
    df = add_income_bins(df, compare_with="tpc", bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, compare_with="tpc", bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_soi():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])

    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 24999, 29999, 39999,
            49999, 74999, 99999, 199999, 499999, 999999, 1499999,
            1999999, 4999999, 9999999, 1e14]

    df = add_income_bins(df, compare_with="soi", bins=None)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, compare_with="soi", bins=None, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_specify_bins():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])

    bins = [-1e14, 0, 4999, 9999, 14999, 19999, 29999, 32999, 43999,
            1e14]

    df = add_income_bins(df, bins=bins)
    grpd = df.groupby('bins')
    grps = [grp for grp in grpd]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + "]")

    grpdl = add_income_bins(df, bins=bins, right=False)
    grpdl = grpdl.groupby('bins')
    grps = [grp for grp in grpdl]

    for g, num in zip(grps, bins[1:-1]):
        assert g[0].endswith(str(num) + ")")


def test_add_income_bins_raises():
    data = np.arange(1, 1e6, 5000)
    df = DataFrame(data=data, columns=['_expanded_income'])

    with pytest.raises(ValueError):
        df = add_income_bins(df, compare_with="stuff")


def test_add_weighted_decile_bins():
    df = DataFrame(data=data, columns=['_expanded_income', 's006', 'label'])
    df = add_weighted_decile_bins(df)
    assert 'bins' in df


def test_dist_table_sum_row():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta_path = os.path.join(cur_path, "../../tax_all1991_puf.gz")
    # Create a default Parameters object
    params1 = Parameters(start_year=1991, inflation_rates=irates)
    records1 = Records(tax_dta_path)
    # Create a Calculator
    calc1 = Calculator(params=params1, records=records1)
    calc1.calc_all()
    t1 = create_distribution_table(calc1, groupby="small_income_bins",
                                   result_type="weighted_sum")
    t2 = create_distribution_table(calc1, groupby="large_income_bins",
                                   result_type="weighted_sum")
    assert(np.allclose(t1[-1:], t2[-1:]))

    t3 = create_distribution_table(calc1, groupby="small_income_bins",
                                   result_type="weighted_avg")
#    for col in t3:
#        assert(t3.loc['sums', col] == 'n/a')


def test_diff_table_sum_row():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    tax_dta_path = os.path.join(cur_path, "../../tax_all1991_puf.gz")
    # Create a default Parameters object
    params1 = Parameters(start_year=1991, inflation_rates=irates)
    records1 = Records(tax_dta_path)
    # Create a Calculator
    calc1 = Calculator(params=params1, records=records1)
    calc1.calc_all()

    # User specified Plans
    user_mods = '{"1991": {"_II_rt4": [0.56]}}'
    params2 = Parameters(start_year=1991, inflation_rates=irates)
    records2 = Records(tax_dta_path)
    # Create a Calculator
    calc2 = calculator(params=params2, records=records2, mods=user_mods)
    calc2.calc_all()

    tdiff1 = create_difference_table(calc1, calc2, groupby="small_income_bins")
    tdiff2 = create_difference_table(calc1, calc2, groupby="large_income_bins")

    non_digit_cols = ['mean', 'perc_inc', 'perc_cut', 'share_of_change']
    digit_cols = [x for x in tdiff1.columns.tolist() if
                  x not in non_digit_cols]

    assert(np.allclose(tdiff1[digit_cols][-1:], tdiff2[digit_cols][-1:]))
    assert(np.array_equal(tdiff1[non_digit_cols][-1:],
           tdiff2[non_digit_cols][-1:]))


def test_expand_2D_already_filled():

    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450]]

    res = expand_2D(_II_brk2, inflate=True, inflation_rates=[0.02] * 5,
                    num_years=3)

    npt.assert_array_equal(res, np.array(_II_brk2))


def test_expand_2D_partial_expand():

    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450]]

    # We have three years worth of data, need 4 years worth,
    # but we only need the inflation rate for year 3 to go
    # from year 3 -> year 4
    inf_rates = [0.02, 0.02, 0.03]

    exp1 = 40000 * 1.03
    exp2 = 74900 * 1.03
    exp3 = 37450 * 1.03
    exp4 = 50200 * 1.03
    exp5 = 74900 * 1.03
    exp6 = 37450 * 1.03

    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [exp1, exp2, exp3, exp4, exp5, exp6]]

    exp = np.array(exp).astype('i4', casting='unsafe')

    res = expand_2D(_II_brk2, inflate=True, inflation_rates=inf_rates,
                    num_years=4)

    npt.assert_array_equal(res, exp)


def test_strip_Nones():

    x = [None, None]
    assert strip_Nones(x) == []

    x = [1, 2, None]
    assert strip_Nones(x) == [1, 2]

    x = [[1, 2, 3], [4, None, None]]
    assert strip_Nones(x) == [[1, 2, 3], [4, -1, -1]]


def test_expand_2D_accept_None():

    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450],
                [41000, None, None, None, None, None]]

    exp1 = 74900 * 1.02
    exp2 = 37450 * 1.02
    exp3 = 50200 * 1.02
    exp4 = 74900 * 1.02
    exp5 = 37450 * 1.02

    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [41000, exp1, exp2, exp3, exp4, exp5]]

    exp = np.array(exp).astype('i4', casting='unsafe')

    res = expand_array(_II_brk2, inflate=True, inflation_rates=[0.02] * 5,
                       num_years=4)

    npt.assert_array_equal(res, exp)


def test_expand_2D_accept_None_additional_row():

    _II_brk2 = [[36000, 72250, 36500, 48600, 72500, 36250],
                [38000, 74000, 36900, 49400, 73800, 36900],
                [40000, 74900, 37450, 50200, 74900, 37450],
                [41000, None, None, None, None, None],
                [43000, None, None, None, None, None]]

    exp1 = 74900 * 1.02
    exp2 = 37450 * 1.02
    exp3 = 50200 * 1.02
    exp4 = 74900 * 1.02
    exp5 = 37450 * 1.02

    exp6 = exp1 * 1.03
    exp7 = exp2 * 1.03
    exp8 = exp3 * 1.03
    exp9 = exp4 * 1.03
    exp10 = exp5 * 1.03

    exp = [[36000, 72250, 36500, 48600, 72500, 36250],
           [38000, 74000, 36900, 49400, 73800, 36900],
           [40000, 74900, 37450, 50200, 74900, 37450],
           [41000, exp1, exp2, exp3, exp4, exp5],
           [43000, exp6, exp7, exp8, exp9, exp10]]

    exp = np.array(exp).astype('i4', casting='unsafe')

    inflation_rates = [0.015, 0.02, 0.02, 0.03]

    res = expand_array(_II_brk2, inflate=True, inflation_rates=inflation_rates,
                       num_years=5)

    npt.assert_array_equal(res, exp)


@pytest.yield_fixture
def csvfile():

    txt = ("A,B,C,D,EFGH\n"
           "1,2,3,4,0\n"
           "5,6,7,8,0\n"
           "9,10,11,12,0\n"
           "100,200,300,400,500\n"
           "123.45,678.912,000.000,87,92")

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(txt + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


@pytest.yield_fixture
def asciifile():

    x = ("A              \t1              \t100            \t123.45         \n"
         "B              \t2              \t200            \t678.912        \n"
         "C              \t3              \t300            \t000.000        \n"
         "D              \t4              \t400            \t87             \n"
         "EFGH           \t0              \t500            \t92             "
         )

    f = tempfile.NamedTemporaryFile(mode="a", delete=False)
    f.write(x + "\n")
    f.close()
    # Must close and then yield for Windows platform
    yield f
    os.remove(f.name)


def test_csv_to_ascii(csvfile, asciifile):

    output_test = tempfile.NamedTemporaryFile(mode="a", delete=False)
    ascii_output(csv_results=csvfile.name, ascii_results=output_test.name)
    assert(filecmp.cmp(output_test.name, asciifile.name))
    output_test.close()
    os.remove(output_test.name)
