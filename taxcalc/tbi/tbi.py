"""
The public API of the TaxBrain Interface (tbi) to Tax-Calculator, which can
be used by other models in the Policy Simulation Library (PSL) collection of
USA tax models.

The tbi functions are used by TaxBrain to call PSL tax models in order
to do distributed processing of TaxBrain runs and in order to maintain
the privacy of the IRS-SOI PUF data being used by TaxBrain.  Maintaining
privacy is done by "fuzzing" reform results for several randomly selected
filing units in each table cell.  The filing units randomly selected
differ for each policy reform and the "fuzzing" involves replacing the
post-reform tax results for the selected units with their pre-reform
tax results.
"""
# CODING-STYLE CHECKS:
# pycodestyle tbi.py
# pylint --disable=locally-disabled tbi.py

import os
import copy
import hashlib
import numpy as np
import pandas as pd
from taxcalc import (Policy, Records, Calculator,
                     Consumption, Behavior, GrowFactors, GrowDiff,
                     DIST_TABLE_LABELS, DIFF_TABLE_LABELS,
                     proportional_change_in_gdp,
                     add_income_table_row_variable,
                     add_quantile_table_row_variable,
                     create_difference_table, create_distribution_table,
                     STANDARD_INCOME_BINS, read_egg_csv)

AGG_ROW_NAMES = ['ind_tax', 'payroll_tax', 'combined_tax']

GDP_ELAST_ROW_NAMES = ['gdp_proportional_change']


def reform_warnings_errors(user_mods, using_puf):
    """
    The reform_warnings_errors function assumes user_mods is a dictionary
    returned by the Calculator.read_json_param_objects() function.

    This function returns a dictionary containing five STR:STR subdictionaries,
    where the dictionary keys are: 'policy', 'behavior', consumption',
    'growdiff_baseline' and 'growdiff_response'; and the subdictionaries are:
    {'warnings': '<empty-or-message(s)>', 'errors': '<empty-or-message(s)>'}.
    Note that non-policy parameters have no warnings, so the 'warnings'
    string for the non-policy parameters is always empty.
    """
    rtn_dict = {'policy': {'warnings': '', 'errors': ''},
                'behavior': {'warnings': '', 'errors': ''},
                'consumption': {'warnings': '', 'errors': ''},
                'growdiff_baseline': {'warnings': '', 'errors': ''},
                'growdiff_response': {'warnings': '', 'errors': ''}}
    # create GrowDiff objects
    gdiff_baseline = GrowDiff()
    try:
        gdiff_baseline.update_growdiff(user_mods['growdiff_baseline'])
    except ValueError as valerr_msg:
        rtn_dict['growdiff_baseline']['errors'] = valerr_msg.__str__()
    gdiff_response = GrowDiff()
    try:
        gdiff_response.update_growdiff(user_mods['growdiff_response'])
    except ValueError as valerr_msg:
        rtn_dict['growdiff_response']['errors'] = valerr_msg.__str__()
    # create Growfactors object
    growfactors = GrowFactors()
    gdiff_baseline.apply_to(growfactors)
    gdiff_response.apply_to(growfactors)
    # create Policy object
    pol = Policy(gfactors=growfactors)
    try:
        pol.implement_reform(user_mods['policy'],
                             print_warnings=False,
                             raise_errors=False)
        if using_puf:
            rtn_dict['policy']['warnings'] = pol.parameter_warnings
        rtn_dict['policy']['errors'] = pol.parameter_errors
    except ValueError as valerr_msg:
        rtn_dict['policy']['errors'] = valerr_msg.__str__()
    # create Behavior object
    behv = Behavior()
    try:
        behv.update_behavior(user_mods['behavior'])
    except ValueError as valerr_msg:
        rtn_dict['behavior']['errors'] = valerr_msg.__str__()
    # create Consumption object
    consump = Consumption()
    try:
        consump.update_consumption(user_mods['consumption'])
    except ValueError as valerr_msg:
        rtn_dict['consumption']['errors'] = valerr_msg.__str__()
    # return composite dictionary of warnings/errors
    return rtn_dict


def run_nth_year_taxcalc_model(year_n, start_year,
                               use_puf_not_cps,
                               use_full_sample,
                               user_mods,
                               return_dict=True):
    """
    The run_nth_year_taxcalc_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-statements
    # pylint: disable=too-many-locals,too-many-branches

    # create calc1 and calc2 calculated for year_n
    check_years(year_n, start_year, use_puf_not_cps)
    calc1, calc2 = calculator_objects(year_n, start_year,
                                      use_puf_not_cps, use_full_sample,
                                      user_mods,
                                      behavior_allowed=True)

    # extract unfuzzed raw results from calc1 and calc2
    dv1 = calc1.distribution_table_dataframe()
    dv2 = calc2.distribution_table_dataframe()

    # delete calc1 and calc2 now that raw results have been extracted
    del calc1
    del calc2

    # construct TaxBrain summary results from raw results
    sres = dict()
    fuzzing = use_puf_not_cps
    if fuzzing:
        # seed random number generator with a seed value based on user_mods
        # (reform-specific seed is used to choose whose results are fuzzed)
        seed = random_seed(user_mods)
        print('fuzzing_seed={}'.format(seed))
        np.random.seed(seed)
        # make bool array marking which filing units are affected by the reform
        reform_affected = np.logical_not(
            np.isclose(dv1['combined'], dv2['combined'], atol=0.01, rtol=0.0)
        )
        agg1, agg2 = fuzzed(dv1, dv2, reform_affected, 'aggr')
        sres = summary_aggregate(sres, agg1, agg2)
        del agg1
        del agg2
        dv1b, dv2b = fuzzed(dv1, dv2, reform_affected, 'xbin')
        sres = summary_dist_xbin(sres, dv1b, dv2b)
        sres = summary_diff_xbin(sres, dv1b, dv2b)
        del dv1b
        del dv2b
        dv1d, dv2d = fuzzed(dv1, dv2, reform_affected, 'xdec')
        sres = summary_dist_xdec(sres, dv1d, dv2d)
        sres = summary_diff_xdec(sres, dv1d, dv2d)
        del dv1d
        del dv2d
        del reform_affected
    else:
        sres = summary_aggregate(sres, dv1, dv2)
        sres = summary_dist_xbin(sres, dv1, dv2)
        sres = summary_diff_xbin(sres, dv1, dv2)
        sres = summary_dist_xdec(sres, dv1, dv2)
        sres = summary_diff_xdec(sres, dv1, dv2)

    # nested function used below
    def append_year(dframe):
        """
        append_year embedded function revises all column names in dframe
        """
        dframe.columns = [str(col) + '_{}'.format(year_n)
                          for col in dframe.columns]
        return dframe

    # optionally return non-JSON-like results
    if not return_dict:
        res = dict()
        for tbl in sres:
            res[tbl] = append_year(sres[tbl])
        return res

    # optionally construct JSON-like results dictionaries for year n
    dec_rownames = list(sres['diff_comb_xdec'].index.values)
    dec_row_names_n = [x + '_' + str(year_n) for x in dec_rownames]
    bin_rownames = list(sres['diff_comb_xbin'].index.values)
    bin_row_names_n = [x + '_' + str(year_n) for x in bin_rownames]
    agg_row_names_n = [x + '_' + str(year_n) for x in AGG_ROW_NAMES]
    dist_column_types = [float] * len(DIST_TABLE_LABELS)
    diff_column_types = [float] * len(DIFF_TABLE_LABELS)
    info = dict()
    for tbl in sres:
        info[tbl] = {'row_names': [], 'col_types': []}
        if 'dec' in tbl:
            info[tbl]['row_names'] = dec_row_names_n
        elif 'bin' in tbl:
            info[tbl]['row_names'] = bin_row_names_n
        else:
            info[tbl]['row_names'] = agg_row_names_n
        if 'dist' in tbl:
            info[tbl]['col_types'] = dist_column_types
        elif 'diff' in tbl:
            info[tbl]['col_types'] = diff_column_types
    res = dict()
    for tbl in sres:
        if 'aggr' in tbl:
            res_table = create_dict_table(sres[tbl],
                                          row_names=info[tbl]['row_names'])
            res[tbl] = dict((k, v[0]) for k, v in res_table.items())
        else:
            res[tbl] = create_dict_table(sres[tbl],
                                         row_names=info[tbl]['row_names'],
                                         column_types=info[tbl]['col_types'])
    return res


def run_nth_year_gdp_elast_model(year_n, start_year,
                                 use_puf_not_cps,
                                 use_full_sample,
                                 user_mods,
                                 gdp_elasticity,
                                 return_dict=True):
    """
    The run_nth_year_gdp_elast_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-locals

    # calculate gdp_effect
    fyear = check_years_return_first_year(year_n, start_year, use_puf_not_cps)
    if year_n > 0 and (start_year + year_n) > fyear:
        # create calc1 and calc2 calculated for year_n - 1
        (calc1, calc2) = calculator_objects((year_n - 1), start_year,
                                            use_puf_not_cps,
                                            use_full_sample,
                                            user_mods,
                                            behavior_allowed=False)
        # compute GDP effect given specified gdp_elasticity
        gdp_effect = proportional_change_in_gdp((start_year + year_n),
                                                calc1, calc2, gdp_elasticity)
    else:
        gdp_effect = 0.0

    # return gdp_effect results
    if return_dict:
        gdp_df = pd.DataFrame(data=[gdp_effect], columns=['col0'])
        gdp_elast_names_n = [x + '_' + str(year_n)
                             for x in GDP_ELAST_ROW_NAMES]
        gdp_elast_total = create_dict_table(gdp_df,
                                            row_names=gdp_elast_names_n,
                                            num_decimals=5)
        gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())
        return gdp_elast_total
    return gdp_effect


# -------------------------------------------------------
# Begin "private" functions used to build functions like
# run_nth_year_taxcalc_model for other models in the USA
# tax collection of the Policy Simulation Library (PSL).
# Any other use of the following functions is suspect.
# -------------------------------------------------------


def check_years(year_n, start_year, use_puf_not_cps):
    """
    Ensure year_n and start_year values are valid given input data used.
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


def check_user_mods(user_mods):
    """
    Ensure specified user_mods is properly structured.
    """
    if not isinstance(user_mods, dict):
        raise ValueError('user_mods is not a dictionary')
    actual_keys = set(list(user_mods.keys()))
    expected_keys = set(['policy', 'consumption', 'behavior',
                         'growdiff_baseline', 'growdiff_response',
                         'growmodel'])
    if actual_keys != expected_keys:
        msg = 'actual user_mod keys not equal to expected keys\n'
        msg += '  actual: {}\n'.format(actual_keys)
        msg += '  expect: {}'.format(expected_keys)
        raise ValueError(msg)


def calculator_objects(year_n, start_year,
                       use_puf_not_cps,
                       use_full_sample,
                       user_mods,
                       behavior_allowed):
    """
    This function assumes that the specified user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    This function returns (calc1, calc2) where
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
    growdiff_baseline = GrowDiff()
    growdiff_response = GrowDiff()
    growdiff_base_assumps = user_mods['growdiff_baseline']
    growdiff_resp_assumps = user_mods['growdiff_response']
    growdiff_baseline.update_growdiff(growdiff_base_assumps)
    growdiff_response.update_growdiff(growdiff_resp_assumps)

    # create pre-reform and post-reform GrowFactors instances
    growfactors_pre = GrowFactors()
    growdiff_baseline.apply_to(growfactors_pre)
    growfactors_post = GrowFactors()
    growdiff_baseline.apply_to(growfactors_post)
    growdiff_response.apply_to(growfactors_post)

    # create sample pd.DataFrame from specified input file and sampling scheme
    tbi_path = os.path.abspath(os.path.dirname(__file__))
    if use_puf_not_cps:
        # first try TaxBrain deployment path
        input_path = 'puf.csv.gz'
        if not os.path.isfile(input_path):
            # otherwise try local Tax-Calculator deployment path
            input_path = os.path.join(tbi_path, '..', '..', 'puf.csv')
        sampling_frac = 0.05
        sampling_seed = 2222
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
        sample = full_sample.sample(frac=sampling_frac,
                                    random_state=sampling_seed)

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


def calculators(year_n, start_year,
                use_puf_not_cps,
                use_full_sample,
                user_mods):
    """
    This function assumes that the specified user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    This function returns (calc1, calc2) where
      calc1 is pre-reform Calculator object for year_n, and
      calc2 is post-reform Calculator object for year_n.
    Neither Calculator object has had the calc_all() method executed.
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements

    check_user_mods(user_mods)

    # specify Consumption instance
    consump = Consumption()
    consump_assumptions = user_mods['consumption']
    consump.update_consumption(consump_assumptions)

    # specify growdiff_baseline and growdiff_response
    growdiff_baseline = GrowDiff()
    growdiff_response = GrowDiff()
    growdiff_base_assumps = user_mods['growdiff_baseline']
    growdiff_resp_assumps = user_mods['growdiff_response']
    growdiff_baseline.update_growdiff(growdiff_base_assumps)
    growdiff_response.update_growdiff(growdiff_resp_assumps)

    # create pre-reform and post-reform GrowFactors instances
    growfactors_pre = GrowFactors()
    growdiff_baseline.apply_to(growfactors_pre)
    growfactors_post = GrowFactors()
    growdiff_baseline.apply_to(growfactors_post)
    growdiff_response.apply_to(growfactors_post)

    # create sample pd.DataFrame from specified input file and sampling scheme
    tbi_path = os.path.abspath(os.path.dirname(__file__))
    if use_puf_not_cps:
        # first try TaxBrain deployment path
        input_path = 'puf.csv.gz'
        if not os.path.isfile(input_path):
            # otherwise try local Tax-Calculator deployment path
            input_path = os.path.join(tbi_path, '..', '..', 'puf.csv')
        sampling_frac = 0.05
        sampling_seed = 2222
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
        sample = full_sample.sample(frac=sampling_frac,
                                    random_state=sampling_seed)

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
    assert calc1.current_year == start_year

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
    calc2 = Calculator(policy=policy2, records=recs2, consumption=consump)
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
    del recs1
    del recs2
    del policy1
    del policy2

    # increment Calculator objects for year_n years
    for _ in range(0, year_n):
        calc1.increment_year()
        calc2.increment_year()

    # return Calculator objects
    return (calc1, calc2)


def random_seed(user_mods):
    """
    Compute random seed based on specified user_mods, which is a
    dictionary returned by Calculator.read_json_parameter_files().
    """
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
        return seed % np.iinfo(np.uint32).max
    # start of random_seed function
    ans = 0
    for subdict_name in user_mods:
        ans += random_seed_from_subdict(user_mods[subdict_name])
    return ans % np.iinfo(np.uint32).max


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
    assert table_row_type in ('aggr', 'xbin', 'xdec')
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
            choices = np.random.choice(indices[0], size=num, replace=False)
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


def summary_aggregate(res, df1, df2):
    """
    res is dictionary of summary-results DataFrames.
    df1 contains results variables for baseline policy.
    df2 contains results variables for reform policy.
    returns augmented dictionary of summary-results DataFrames.
    """
    # pylint: disable=too-many-locals
    # tax difference totals between reform and baseline
    aggr_itax_d = ((df2['iitax'] - df1['iitax']) * df2['s006']).sum()
    aggr_ptax_d = ((df2['payrolltax'] - df1['payrolltax']) * df2['s006']).sum()
    aggr_comb_d = ((df2['combined'] - df1['combined']) * df2['s006']).sum()
    aggrd = [aggr_itax_d, aggr_ptax_d, aggr_comb_d]
    res['aggr_d'] = pd.DataFrame(data=aggrd, index=AGG_ROW_NAMES)
    del aggrd
    # tax totals for baseline
    aggr_itax_1 = (df1['iitax'] * df1['s006']).sum()
    aggr_ptax_1 = (df1['payrolltax'] * df1['s006']).sum()
    aggr_comb_1 = (df1['combined'] * df1['s006']).sum()
    aggr1 = [aggr_itax_1, aggr_ptax_1, aggr_comb_1]
    res['aggr_1'] = pd.DataFrame(data=aggr1, index=AGG_ROW_NAMES)
    del aggr1
    # tax totals for reform
    aggr_itax_2 = (df2['iitax'] * df2['s006']).sum()
    aggr_ptax_2 = (df2['payrolltax'] * df2['s006']).sum()
    aggr_comb_2 = (df2['combined'] * df2['s006']).sum()
    aggr2 = [aggr_itax_2, aggr_ptax_2, aggr_comb_2]
    res['aggr_2'] = pd.DataFrame(data=aggr2, index=AGG_ROW_NAMES)
    del aggr2
    # scale res dictionary elements
    for tbl in ['aggr_d', 'aggr_1', 'aggr_2']:
        for col in res[tbl]:
            res[tbl][col] = round(res[tbl][col] * 1.e-9, 3)
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
            if _type in int_types:
                return str(int(val))
            if _type == str:
                return str(val)
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
