"""
Private utility functions used only by public functions in the tbi.py file.
"""
# CODING-STYLE CHECKS:
# pycodestyle tbi_utils.py
# pylint --disable=locally-disabled tbi_utils.py

from __future__ import print_function
import os
import time
import copy
import hashlib
import numpy as np
import pandas as pd
from taxcalc import (Policy, Records, Calculator,
                     Consumption, Behavior, Growfactors, Growdiff)
from taxcalc.utils import (add_income_table_row_variable,
                           add_quantile_table_row_variable,
                           create_difference_table, create_distribution_table,
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
    The function returns (calc1, calc2) where
      calc1 is pre-reform Calculator object calculated for year_n, and
      calc2 is post-reform Calculator object calculated for year_n.
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

    # return calculated Calculator objects
    return (calc1, calc2)


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


def fuzzed(df1, df2, reform_affected, table_row_type):
    """
    Create fuzzed df2 dataframe and corresponding unfuzzed df1 dataframe.

    Parameters
    ----------
    df1: Pandas DataFrame
        contains results variables for the baseline policy, which are not
        changed by this function

    df2: Pandas DataFrame
        contains results variables for the reform policy, which are not
        changed by this function

    reform_affected: boolean numpy array (not changed by this function)
        True for filing units with a reform-induced combined tax difference;
        otherwise False

    table_row_type: string
        valid values are 'aggr', 'xbin', and 'xdec'

    Returns
    -------
    df1, df2: Pandas DataFrames
        where copied df2 is fuzzed to maintain data privacy and
        where copied df1 has same filing unit order as has the fuzzed df2
    """
    assert (table_row_type == 'aggr' or
            table_row_type == 'xbin' or
            table_row_type == 'xdec')
    assert len(df1.index) == len(df2.index)
    assert reform_affected.size == len(df1.index)
    df1 = copy.deepcopy(df1)
    df2 = copy.deepcopy(df2)
    # add copy of reform_affected to df2
    df2['reform_affected'] = copy.deepcopy(reform_affected)
    # construct table rows, for which filing units in each row must be fuzzed
    if table_row_type == 'xbin':
        df1 = add_income_table_row_variable(df1, 'expanded_income',
                                            STANDARD_INCOME_BINS)
        df2['expanded_income_baseline'] = df1['expanded_income']
        df2 = add_income_table_row_variable(df2, 'expanded_income_baseline',
                                            STANDARD_INCOME_BINS)
        del df2['expanded_income_baseline']
    elif table_row_type == 'xdec':
        df1 = add_quantile_table_row_variable(df1, 'expanded_income',
                                              10, decile_details=True)
        df2['expanded_income_baseline'] = df1['expanded_income']
        df2 = add_quantile_table_row_variable(df2, 'expanded_income_baseline',
                                              10, decile_details=True)
        del df2['expanded_income_baseline']
    elif table_row_type == 'aggr':
        df1['table_row'] = np.ones(reform_affected.shape, dtype=int)
        df2['table_row'] = df1['table_row']
    gdf1 = df1.groupby('table_row', sort=False)
    gdf2 = df2.groupby('table_row', sort=False)
    del df1['table_row']
    del df2['table_row']
    # fuzz up to NUM_TO_FUZZ filing units randomly chosen in each group
    # (or table row), where fuzz means to replace the reform (2) results
    # with the baseline (1) results for each chosen filing unit
    pd.options.mode.chained_assignment = None
    group_list = list()
    for name, group2 in gdf2:
        indices = np.where(group2['reform_affected'])
        num = min(len(indices[0]), NUM_TO_FUZZ)
        if num > 0:
            choices = np.random.choice(indices[0],  # pylint: disable=no-member
                                       size=num, replace=False)
            group1 = gdf1.get_group(name)
            for idx in choices:
                group2.iloc[idx] = group1.iloc[idx]
        group_list.append(group2)
    df2 = pd.concat(group_list)
    del df2['reform_affected']
    pd.options.mode.chained_assignment = 'warn'
    # reinstate index order of df1 and df2 and return
    df1.sort_index(inplace=True)
    df2.sort_index(inplace=True)
    return (df1, df2)


AGGR_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']


def summary_aggregate(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # tax difference totals between reform and baseline
    aggr_itax_d = ((df2['iitax'] - df1['iitax']) * df2['s006']).sum()
    aggr_ptax_d = ((df2['payrolltax'] - df1['payrolltax']) * df2['s006']).sum()
    aggr_comb_d = ((df2['combined'] - df1['combined']) * df2['s006']).sum()
    aggrd = [aggr_itax_d, aggr_ptax_d, aggr_comb_d]
    res['aggr_d'] = pd.DataFrame(data=aggrd, index=AGGR_ROW_NAMES)
    del aggrd
    # tax totals for baseline
    aggr_itax_1 = (df1['iitax'] * df1['s006']).sum()
    aggr_ptax_1 = (df1['payrolltax'] * df1['s006']).sum()
    aggr_comb_1 = (df1['combined'] * df1['s006']).sum()
    aggr1 = [aggr_itax_1, aggr_ptax_1, aggr_comb_1]
    res['aggr_1'] = pd.DataFrame(data=aggr1, index=AGGR_ROW_NAMES)
    del aggr1
    # tax totals for reform
    aggr_itax_2 = (df2['iitax'] * df2['s006']).sum()
    aggr_ptax_2 = (df2['payrolltax'] * df2['s006']).sum()
    aggr_comb_2 = (df2['combined'] * df2['s006']).sum()
    aggr2 = [aggr_itax_2, aggr_ptax_2, aggr_comb_2]
    res['aggr_2'] = pd.DataFrame(data=aggr2, index=AGGR_ROW_NAMES)
    del aggr2
    # return res dictionary
    return res


def summary_dist_xbin(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # create distribution tables grouped by xbin
    res['dist1_xbin'] = \
        create_distribution_table(df1, 'standard_income_bins',
                                  'expanded_income')
    df2['expanded_income_baseline'] = df1['expanded_income']
    res['dist2_xbin'] = \
        create_distribution_table(df2, 'standard_income_bins',
                                  'expanded_income_baseline')
    del df2['expanded_income_baseline']
    # return res dictionary
    return res


def summary_diff_xbin(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # create difference tables grouped by xbin
    res['diff_itax_xbin'] = \
        create_difference_table(df1, df2, 'standard_income_bins', 'iitax')
    res['diff_ptax_xbin'] = \
        create_difference_table(df1, df2, 'standard_income_bins', 'payrolltax')
    res['diff_comb_xbin'] = \
        create_difference_table(df1, df2, 'standard_income_bins', 'combined')
    # return res dictionary
    return res


def summary_dist_xdec(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # create distribution tables grouped by xdec
    res['dist1_xdec'] = \
        create_distribution_table(df1, 'weighted_deciles',
                                  'expanded_income')
    df2['expanded_income_baseline'] = df1['expanded_income']
    res['dist2_xdec'] = \
        create_distribution_table(df2, 'weighted_deciles',
                                  'expanded_income_baseline')
    del df2['expanded_income_baseline']
    # return res dictionary
    return res


def summary_diff_xdec(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # create difference tables grouped by xdec
    res['diff_itax_xdec'] = \
        create_difference_table(df1, df2, 'weighted_deciles', 'iitax')
    res['diff_ptax_xdec'] = \
        create_difference_table(df1, df2, 'weighted_deciles', 'payrolltax')
    res['diff_comb_xdec'] = \
        create_difference_table(df1, df2, 'weighted_deciles', 'combined')
    # return res dictionary
    return res


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
