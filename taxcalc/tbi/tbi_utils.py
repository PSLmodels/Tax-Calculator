"""
Private utility functions used only by public functions in the tbi.py file.
"""
# CODING-STYLE CHECKS:
# pep8 tbi_utils.py
# pylint --disable=locally-disabled tbi_utils.py

from __future__ import print_function
import os
import time
import hashlib
import numpy as np
import pandas as pd
from taxcalc import (Policy, Records, Calculator,
                     Consumption, Behavior, Growfactors, Growdiff)
from taxcalc.utils import (add_income_table_row_variable,
                           add_quantile_table_row_variable,
                           create_difference_table, create_distribution_table,
                           DIST_VARIABLES, DIST_TABLE_COLUMNS,
                           STANDARD_INCOME_BINS, read_egg_csv)


def check_years_return_first_year(year_n, start_year, use_puf_not_cps):
    """
    Ensure year_n and start_year values are valid given input data used.
    Return value of first year, which is maximum of first records data year
    and first policy parameter year.
    """
    if year_n < 0:
        msg = 'year_n={} < 0'
        raise ValueError(msg.format(year_n))
    if use_puf_not_cps:
        first_data_year = Records.PUFCSV_YEAR
    else:
        first_data_year = Records.CPSCSV_YEAR
    first_year = max(Policy.JSON_START_YEAR, first_data_year)
    if start_year < first_year:
        msg = 'start_year={} < first_year={}'
        raise ValueError(msg.format(start_year, first_year))
    if (start_year + year_n) > Policy.LAST_BUDGET_YEAR:
        msg = '(start_year={} + year_n={}) > Policy.LAST_BUDGET_YEAR={}'
        raise ValueError(msg.format(start_year, year_n,
                                    Policy.LAST_BUDGET_YEAR))
    return first_year


def check_user_mods(user_mods):
    """
    Ensure specified user_mods is properly structured.
    """
    if not isinstance(user_mods, dict):
        raise ValueError('user_mods is not a dictionary')
    actual_keys = set(list(user_mods.keys()))
    expected_keys = set(['policy', 'consumption', 'behavior',
                         'growdiff_baseline', 'growdiff_response'])
    if actual_keys != expected_keys:
        msg = 'actual user_mod keys not equal to expected keys\n'
        msg += '  actual: {}\n'.format(actual_keys)
        msg += '  expect: {}'.format(expected_keys)
        raise ValueError(msg)


def calculate(year_n, start_year,
              use_puf_not_cps,
              use_full_sample,
              user_mods,
              behavior_allowed):
    """
    The calculate function assumes the specified user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    The function returns (calc1, calc2, mask) where
      calc1 is pre-reform Calculator object calculated for year_n,
      calc2 is post-reform Calculator object calculated for year_n, and
      mask is boolean array marking records with reform-induced iitax diffs
    Set behavior_allowed to False when generating static results or
      set behavior_allowed to True when generating dynamic results.
    """
    # pylint: disable=too-many-arguments,too-many-locals
    # pylint: disable=too-many-branches,too-many-statements

    check_user_mods(user_mods)

    # specify Consumption instance
    consump = Consumption()
    consump_assumptions = user_mods['consumption']
    consump.update_consumption(consump_assumptions)

    # specify growdiff_baseline and growdiff_response
    growdiff_baseline = Growdiff()
    growdiff_response = Growdiff()
    growdiff_base_assumps = user_mods['growdiff_baseline']
    growdiff_resp_assumps = user_mods['growdiff_response']
    growdiff_baseline.update_growdiff(growdiff_base_assumps)
    growdiff_response.update_growdiff(growdiff_resp_assumps)

    # create pre-reform and post-reform Growfactors instances
    growfactors_pre = Growfactors()
    growdiff_baseline.apply_to(growfactors_pre)
    growfactors_post = Growfactors()
    growdiff_baseline.apply_to(growfactors_post)
    growdiff_response.apply_to(growfactors_post)

    # create sample pd.DataFrame from specified input file and sampling scheme
    stime = time.time()
    tbi_path = os.path.abspath(os.path.dirname(__file__))
    if use_puf_not_cps:
        # first try TaxBrain deployment path
        input_path = 'puf.csv.gz'
        if not os.path.isfile(input_path):
            # otherwise try local Tax-Calculator deployment path
            input_path = os.path.join(tbi_path, '..', '..', 'puf.csv')
        sampling_frac = 0.05
        sampling_seed = 180
    else:  # if using cps input not puf input
        # first try Tax-Calculator code path
        input_path = os.path.join(tbi_path, '..', 'cps.csv.gz')
        if not os.path.isfile(input_path):
            # otherwise read from taxcalc package "egg"
            input_path = None  # pragma: no cover
            full_sample = read_egg_csv('cps.csv.gz')  # pragma: no cover
        sampling_frac = 0.03
        sampling_seed = 180
    if input_path:
        full_sample = pd.read_csv(input_path)
    if use_full_sample:
        sample = full_sample
    else:
        sample = full_sample.sample(  # pylint: disable=no-member
            frac=sampling_frac,
            random_state=sampling_seed
        )
    if use_puf_not_cps:
        print('puf-read-time= {:.1f}'.format(time.time() - stime))
    else:
        print('cps-read-time= {:.1f}'.format(time.time() - stime))

    # create pre-reform Calculator instance
    if use_puf_not_cps:
        recs1 = Records(data=sample,
                        gfactors=growfactors_pre)
    else:
        recs1 = Records.cps_constructor(data=sample,
                                        gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=recs1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    calc1.calc_all()
    assert calc1.current_year == start_year

    # compute mask array
    res1 = calc1.dataframe(DIST_VARIABLES)
    if use_puf_not_cps:
        # create pre-reform Calculator instance with extra income
        recs1p = Records(data=sample, gfactors=growfactors_pre)
        # add one dollar to the income of each filing unit to determine
        # which filing units undergo a resulting change in tax liability
        recs1p.e00200 += 1.0  # pylint: disable=no-member
        recs1p.e00200p += 1.0  # pylint: disable=no-member
        policy1p = Policy(gfactors=growfactors_pre)
        # create Calculator with recs1p and calculate for start_year
        calc1p = Calculator(policy=policy1p, records=recs1p,
                            consumption=consump)
        while calc1p.current_year < start_year:
            calc1p.increment_year()
        calc1p.calc_all()
        assert calc1p.current_year == start_year
        # compute mask showing which of the calc1 and calc1p results differ;
        # mask is true if a filing unit's income tax liability changed after
        # a dollar was added to the filing unit's wage and salary income
        res1p = calc1p.dataframe(DIST_VARIABLES)
        mask = np.logical_not(  # pylint: disable=no-member
            np.isclose(res1.iitax, res1p.iitax, atol=0.001, rtol=0.0)
        )
        assert np.any(mask)
        # delete intermediate objects
        del recs1p
        del policy1p
        del calc1p
        del res1p
    else:  # if use_puf_not_cps is False
        # indicate that fuzzing of reform results is not required
        mask = np.full(res1.shape, False)
    del res1

    # specify Behavior instance
    behv = Behavior()
    behavior_assumps = user_mods['behavior']
    behv.update_behavior(behavior_assumps)

    # always prevent both behavioral response and growdiff response
    if behv.has_any_response() and growdiff_response.has_any_response():
        msg = 'BOTH behavior AND growdiff_response HAVE RESPONSE'
        raise ValueError(msg)

    # optionally prevent behavioral response
    if behv.has_any_response() and not behavior_allowed:
        msg = 'A behavior RESPONSE IS NOT ALLOWED'
        raise ValueError(msg)

    # create post-reform Calculator instance
    if use_puf_not_cps:
        recs2 = Records(data=sample,
                        gfactors=growfactors_post)
    else:
        recs2 = Records.cps_constructor(data=sample,
                                        gfactors=growfactors_post)
    policy2 = Policy(gfactors=growfactors_post)
    policy_reform = user_mods['policy']
    policy2.implement_reform(policy_reform)
    calc2 = Calculator(policy=policy2, records=recs2,
                       consumption=consump, behavior=behv)
    while calc2.current_year < start_year:
        calc2.increment_year()
    assert calc2.current_year == start_year

    # delete objects now embedded in calc1 and calc2
    del sample
    del full_sample
    del consump
    del growdiff_baseline
    del growdiff_response
    del growfactors_pre
    del growfactors_post
    del behv
    del recs1
    del recs2
    del policy1
    del policy2

    # increment Calculator objects for year_n years and calculate
    for _ in range(0, year_n):
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    if calc2.behavior_has_response():
        calc2 = Behavior.response(calc1, calc2)
    else:
        calc2.calc_all()

    # return calculated Calculator objects and mask
    return (calc1, calc2, mask)


def random_seed(user_mods):
    """
    Compute random seed based on specified user_mods, which is a
    dictionary returned by the Calculator.read_json_parameter_files()
    function with an extra key:value pair that is specified as
    'gdp_elasticity': {'value': <float_value>}.
    """
    ans = 0
    for subdict_name in user_mods:
        if subdict_name != 'gdp_elasticity':
            ans += random_seed_from_subdict(user_mods[subdict_name])
    return ans % np.iinfo(np.uint32).max  # pylint: disable=no-member


def random_seed_from_subdict(subdict):
    """
    Compute random seed from one user_mods subdictionary.
    """
    assert isinstance(subdict, dict)
    all_vals = []
    for year in sorted(subdict.keys()):
        all_vals.append(str(year))
        params = subdict[year]
        for param in sorted(params.keys()):
            try:
                tple = tuple(params[param])
            except TypeError:
                # params[param] is not an iterable value; make it so
                tple = tuple((params[param],))
            all_vals.append(str((param, tple)))
    txt = u''.join(all_vals).encode('utf-8')
    hsh = hashlib.sha512(txt)
    seed = int(hsh.hexdigest(), 16)
    return seed % np.iinfo(np.uint32).max  # pylint: disable=no-member


NUM_TO_FUZZ = 3  # when using dropq algorithm on puf.csv results


def chooser(agg):
    """
    This is a transformation function that should be called on each group
    (that is, each cell in a table).  It is assumed that the chunk 'agg' is
    a chunk of the 'mask' column.  This chooser selects NUM_TO_FUZZ of those
    mask indices with the output for those NUM_TO_FUZZ indices being zero and
    the output for all the other indices being one.
    """
    # select indices of records with change in tax liability after
    # a one dollar increase in income
    indices = np.where(agg)
    if len(indices[0]) >= NUM_TO_FUZZ:
        choices = np.random.choice(indices[0],  # pylint: disable=no-member
                                   size=NUM_TO_FUZZ, replace=False)
    else:
        msg = ('Not enough differences in income tax when adding '
               'one dollar for chunk with name: {}')
        raise ValueError(msg.format(agg.name))
    # mark the records chosen to be fuzzed (ans=0)
    ans = [1] * len(agg)
    for idx in choices:
        ans[idx] = 0
    return ans


def create_results_columns(df1, df2, mask):
    """
    Create columns in df2 results dataframe and possibly
    modify df2 results by adding random fuzz for data privacy.

    Parameters
    ----------
    df1: Pandas DataFrame
        contains results for the baseline plan

    df2: Pandas DataFrame
        contains results for the reform plan

    mask: boolean numpy array
        contains info about whether or not units have reform-induced tax diffs
        (if mask contains all False values, then no results fuzzing is done)

    Returns
    -------
    expanded and possibly fuzzed df2: Pandas DataFrame

    Notes
    -----
    When doing the fuzzing for puf.csv results, this
    function groups both DataFrames based on the web application's
    income groupings (both decile and income bins), and then randomly
    selects NUM_TO_FUZZ records to fuzz within each bin.  The fuzzing
    involves overwriting df2 columns in cols_to_fuzz with df1 values.
    """
    # nested function that does the fuzzing
    def create(df1, df2, bin_type, imeasure, suffix, cols_to_fuzz, do_fuzzing):
        """
        Create additional df2 columns.  If do_fuzzing is True, also
        fuzz some df2 records in each bin defined by bin_type and imeasure
        with the fuzzed records having their post-reform tax results (in df2)
        set to their pre-reform tax results (in df1).
        """
        # pylint: disable=too-many-arguments
        assert bin_type == 'dec' or bin_type == 'bin' or bin_type == 'agg'
        if bin_type == 'dec':
            df2 = add_quantile_table_row_variable(df2, imeasure, 10)
        elif bin_type == 'bin':
            df2 = add_income_table_row_variable(df2, imeasure,
                                                bins=STANDARD_INCOME_BINS)
        else:
            df2 = add_quantile_table_row_variable(df2, imeasure, 1)
        gdf2 = df2.groupby('table_row')
        if do_fuzzing:
            df2['nofuzz'] = gdf2['mask'].transform(chooser)
        else:  # never do any results fuzzing
            df2['nofuzz'] = np.ones(df2.shape[0], dtype=np.int8)
        for col in cols_to_fuzz:
            df2[col + suffix] = (df2[col] * df2['nofuzz'] -
                                 df1[col] * df2['nofuzz'] + df1[col])
    # main logic of create_results_columns function
    skips = set(['num_returns_ItemDed',
                 'num_returns_StandardDed',
                 'num_returns_AMT',
                 's006'])
    columns_to_create = (set(DIST_TABLE_COLUMNS) |
                         set(DIST_VARIABLES)) - skips
    do_fuzzing = np.any(mask)
    if do_fuzzing:
        df2['mask'] = mask
    df2['expanded_income_baseline'] = df1['expanded_income']
    create(df1, df2, 'dec', 'expanded_income_baseline', '_xdec',
           columns_to_create, do_fuzzing)
    create(df1, df2, 'bin', 'expanded_income_baseline', '_xbin',
           columns_to_create, do_fuzzing)
    create(df1, df2, 'agg', 'expanded_income_baseline', '_agg',
           columns_to_create, do_fuzzing)
    return df2


AGGR_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']


def summary(df1, df2, mask):
    """
    df1 contains raw results for baseline plan
    df2 contains raw results for reform plan
    mask is the boolean array specifying records with reform-induced tax diffs
    returns dictionary of summary results DataFrames
    """
    # pylint: disable=too-many-statements,too-many-locals

    df2 = create_results_columns(df1, df2, mask)

    summ = dict()

    # tax difference totals between reform and baseline
    tdiff = df2['iitax_agg'] - df1['iitax']
    aggr_itax_d = (tdiff * df2['s006']).sum()
    tdiff = df2['payrolltax_agg'] - df1['payrolltax']
    aggr_ptax_d = (tdiff * df2['s006']).sum()
    tdiff = df2['combined_agg'] - df1['combined']
    aggr_comb_d = (tdiff * df2['s006']).sum()
    aggrd = [aggr_itax_d, aggr_ptax_d, aggr_comb_d]
    summ['aggr_d'] = pd.DataFrame(data=aggrd, index=AGGR_ROW_NAMES)

    # totals for baseline
    aggr_itax_1 = (df1['iitax'] * df1['s006']).sum()
    aggr_ptax_1 = (df1['payrolltax'] * df1['s006']).sum()
    aggr_comb_1 = (df1['combined'] * df1['s006']).sum()
    aggr1 = [aggr_itax_1, aggr_ptax_1, aggr_comb_1]
    summ['aggr_1'] = pd.DataFrame(data=aggr1, index=AGGR_ROW_NAMES)

    # totals for reform
    aggr_itax_2 = (df2['iitax_agg'] * df2['s006']).sum()
    aggr_ptax_2 = (df2['payrolltax_agg'] * df2['s006']).sum()
    aggr_comb_2 = (df2['combined_agg'] * df2['s006']).sum()
    aggr2 = [aggr_itax_2, aggr_ptax_2, aggr_comb_2]
    summ['aggr_2'] = pd.DataFrame(data=aggr2, index=AGGR_ROW_NAMES)

    # create difference tables grouped by xdec
    df2['iitax'] = df2['iitax_xdec']
    summ['diff_itax_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='iitax')

    df2['payrolltax'] = df2['payrolltax_xdec']
    summ['diff_ptax_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='payrolltax')

    df2['combined'] = df2['combined_xdec']
    summ['diff_comb_xdec'] = \
        create_difference_table(df1, df2,
                                groupby='weighted_deciles',
                                income_measure='expanded_income',
                                tax_to_diff='combined')

    # create difference tables grouped by xbin
    df2['iitax'] = df2['iitax_xbin']
    diff_itax_xbin = \
        create_difference_table(df1, df2,
                                groupby='standard_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='iitax')
    summ['diff_itax_xbin'] = diff_itax_xbin

    df2['payrolltax'] = df2['payrolltax_xbin']
    diff_ptax_xbin = \
        create_difference_table(df1, df2,
                                groupby='standard_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='payrolltax')
    summ['diff_ptax_xbin'] = diff_ptax_xbin

    df2['combined'] = df2['combined_xbin']
    diff_comb_xbin = \
        create_difference_table(df1, df2,
                                groupby='standard_income_bins',
                                income_measure='expanded_income',
                                tax_to_diff='combined')
    summ['diff_comb_xbin'] = diff_comb_xbin

    # create distribution tables grouped by xdec
    summ['dist1_xdec'] = \
        create_distribution_table(df1, groupby='weighted_deciles',
                                  income_measure='expanded_income',
                                  result_type='weighted_sum')

    suffix = '_xdec'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['expanded_income_baseline'] = df1['expanded_income']
    summ['dist2_xdec'] = \
        create_distribution_table(df2, groupby='weighted_deciles',
                                  income_measure='expanded_income_baseline',
                                  result_type='weighted_sum')

    # create distribution tables grouped by xbin
    dist1_xbin = \
        create_distribution_table(df1, groupby='standard_income_bins',
                                  income_measure='expanded_income',
                                  result_type='weighted_sum')
    summ['dist1_xbin'] = dist1_xbin

    suffix = '_xbin'
    df2_cols_with_suffix = [c for c in list(df2) if c.endswith(suffix)]
    for col in df2_cols_with_suffix:
        root_col_name = col.replace(suffix, '')
        df2[root_col_name] = df2[col]
    df2['expanded_income_baseline'] = df1['expanded_income']
    dist2_xbin = \
        create_distribution_table(df2, groupby='standard_income_bins',
                                  income_measure='expanded_income_baseline',
                                  result_type='weighted_sum')
    summ['dist2_xbin'] = dist2_xbin

    # return dictionary of summary results
    return summ


def create_dict_table(dframe, row_names=None, column_types=None,
                      num_decimals=2):
    """
    Create and return dictionary with JSON-like content from specified dframe.
    """
    # embedded formatted_string function
    def formatted_string(val, _type, num_decimals):
        """
        Return formatted conversion of number val into a string.
        """
        float_types = [float, np.dtype('f8')]
        int_types = [int, np.dtype('i8')]
        frmat_str = "0:.{num}f".format(num=num_decimals)
        frmat_str = "{" + frmat_str + "}"
        try:
            if _type in float_types or _type is None:
                return frmat_str.format(val)
            elif _type in int_types:
                return str(int(val))
            elif _type == str:
                return str(val)
            else:
                raise NotImplementedError()
        except ValueError:
            # try making it a string - good luck!
            return str(val)
    # high-level create_dict_table function logic
    out = dict()
    if row_names is None:
        row_names = [str(x) for x in list(dframe.index)]
    else:
        assert len(row_names) == len(dframe.index)
    if column_types is None:
        column_types = [dframe[col].dtype for col in dframe.columns]
    else:
        assert len(column_types) == len(dframe.columns)
    for idx, row_name in zip(dframe.index, row_names):
        row_out = out.get(row_name, [])
        for col, dtype in zip(dframe.columns, column_types):
            row_out.append(formatted_string(dframe.loc[idx, col],
                                            dtype, num_decimals))
        out[row_name] = row_out
    return out
