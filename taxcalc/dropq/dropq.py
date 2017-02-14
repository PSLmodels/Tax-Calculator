from __future__ import print_function
from .. import (Calculator, Growfactors, Records,
                Policy, Consumption, Behavior, Growdiff,
                TABLE_LABELS, TABLE_COLUMNS, STATS_COLUMNS, DIFF_TABLE_LABELS)
import numpy as np
from pandas import DataFrame
import pandas as pd
import hashlib
import copy
import time
import collections
from .dropq_utils import create_dropq_difference_table as dropq_diff_table
from .dropq_utils import create_dropq_distribution_table as dropq_dist_table
from .dropq_utils import *

planY_column_types = [float] * len(TABLE_LABELS)

diff_column_names = DIFF_TABLE_LABELS

diff_column_types = [int, int, int, float, float, str, str, str]

decile_row_names = ["perc0-10", "perc10-20", "perc20-30", "perc30-40",
                    "perc40-50", "perc50-60", "perc60-70", "perc70-80",
                    "perc80-90", "perc90-100", "all"]

bin_row_names = ["less_than_10", "ten_twenty", "twenty_thirty", "thirty_forty",
                 "forty_fifty", "fifty_seventyfive", "seventyfive_hundred",
                 "hundred_twohundred", "twohundred_fivehundred",
                 "fivehundred_thousand", "thousand_up", "all"]

total_row_names = ["ind_tax", "payroll_tax", "combined_tax"]


GDP_elast_row_names = ["gdp_elasticity"]

ogusa_row_names = ["GDP", "Consumption", "Investment", "Hours Worked", "Wages",
                   "Interest Rates", "Total Taxes"]

NUM_YEARS_DEFAULT = 1


def call_over_iterable(fn):
    """
    A modifier for the only_* functions in this module. The idea is that
    these functions may be passed a tuple of reform dictionaries, instead
    of just a dictionary (since file-based reforms can result in a tuple
    of reform dictionaries. In that case, this decorator will call its
    wrapped function for each dictionary in the tuple, then collect
    and return the results
    """
    def wrapper(user_mods, start_year, **kwargs):
        if isinstance(user_mods, tuple):
            ans = [fn(mod, start_year, **kwargs) for mod in user_mods]
            params = ans[0]
            for a in ans:
                params.update(a)
            return params
        else:
            return fn(user_mods, start_year, **kwargs)

    return wrapper


@call_over_iterable
def only_growdiff_assumptions(user_mods, start_year):
    """
    Extract any user_mods parameters pertinent to growdiff assumptions
    """
    growdiff_dd = Growdiff.default_data(start_year=start_year)
    ga = {}
    for year, reforms in user_mods.items():
        overlap = set(growdiff_dd.keys()) & set(reforms.keys())
        if overlap:
            ga[year] = {param: reforms[param] for param in overlap}
    return ga


@call_over_iterable
def only_behavior_assumptions(user_mods, start_year):
    """
    Extract any user_mods parameters pertinent to behavior assumptions
    """
    beh_dd = Behavior.default_data(start_year=start_year)
    ba = {}
    for year, reforms in user_mods.items():
        overlap = set(beh_dd.keys()) & set(reforms.keys())
        if overlap:
            ba[year] = {param: reforms[param] for param in overlap}
    return ba


@call_over_iterable
def only_consumption_assumptions(user_mods, start_year):
    """
    Extract any user_mods parameters pertinent to consumption assumptions
    """
    con_dd = Consumption.default_data(start_year=start_year)
    ca = {}
    for year, reforms in user_mods.items():
        overlap = set(con_dd.keys()) & set(reforms.keys())
        if overlap:
            ca[year] = {param: reforms[param] for param in overlap}
    return ca


@call_over_iterable
def only_reform_mods(user_mods, start_year):
    """
    Extract any user_mods parameters pertinent to policy reforms
    """
    pol_refs = {}
    con_dd = Consumption.default_data(start_year=start_year)
    beh_dd = Behavior.default_data(start_year=start_year)
    growdiff_dd = Growdiff.default_data(start_year=start_year)
    policy_dd = Policy.default_data(start_year=start_year)
    param_code_names = Policy.VALID_PARAM_CODE_NAMES
    for year, reforms in user_mods.items():
        all_cpis = {p for p in reforms.keys() if p.endswith("_cpi") and
                    p[:-4] in policy_dd.keys()}
        pols = (set(reforms.keys()) -
                set(con_dd.keys()) -
                set(beh_dd.keys()) -
                set(growdiff_dd.keys()))
        pols &= set(policy_dd.keys()) | param_code_names
        pols ^= all_cpis
        if pols:
            pol_refs[year] = {param: reforms[param] for param in pols}
    return pol_refs


@call_over_iterable
def get_unknown_parameters(user_mods, start_year, additional=None):
    """
    Returns any parameters that are not known to Tax-Calculator.
    Subtract out any behavior, growth, policy, or consumptions parameters,
    plus any additional parameters passed by the user. The results are
    considered unknown and returned
    """
    consump_dd = Consumption.default_data(start_year=start_year)
    beh_dd = Behavior.default_data(start_year=start_year)
    growdiff_dd = Growdiff.default_data(start_year=start_year)
    policy_dd = Policy.default_data(start_year=start_year)
    param_code_names = Policy.VALID_PARAM_CODE_NAMES
    unknown_params = collections.defaultdict(list)
    if additional is None:
        additional = set()
    for year, reforms in user_mods.items():
        everything = set(reforms.keys())
        all_cpis = {p for p in reforms.keys() if p.endswith("_cpi")}
        all_good_cpis = {p for p in reforms.keys() if p.endswith("_cpi") and
                         p[:-4] in policy_dd.keys()}
        bad_cpis = all_cpis - all_good_cpis
        remaining = everything - all_cpis
        if bad_cpis:
            unknown_params['bad_cpis'] += list(bad_cpis)
        pols = (remaining - set(beh_dd.keys()) - set(growdiff_dd.keys()) -
                set(policy_dd.keys()) - set(consump_dd.keys()) -
                param_code_names - additional)
        if pols:
            unknown_params['policy'] += list(pols)
    return unknown_params


def elasticity_of_gdp_year_n(user_mods, start_year, year_n):
    """
    Extract elasticity of GDP parameter for the proper year
    """
    if isinstance(user_mods, tuple):
        # file-based reforms have policy parameters in first item of tuple
        user_mods = user_mods[0]
    # Sorted list of all years (0 is used for parameter code expressions)
    allyears = sorted(filter(lambda x: x != 0, user_mods.keys()))
    elasticity_list = []
    elasticity_specified = False
    for year in allyears:
        reforms = user_mods[year]
        if 'elastic_gdp' in reforms:
            elasticity_list += reforms['elastic_gdp']
            elasticity_specified = True
        else:
            elasticity_list += [0.0]

    if not elasticity_specified:
        raise ValueError("user_mods should specify elastic_gdp")
    if year_n >= len(elasticity_list):
        return elasticity_list[-1]
    else:
        return elasticity_list[year_n]


def random_seed_from_plan(user_mods):
    """
    Handles the case of getting a tuple of reform mods
    """

    if isinstance(user_mods, tuple):
        ans = 0
        for mod in user_mods:
            ans += _random_seed_from_plan(mod)
        return ans % np.iinfo(np.uint32).max
    else:
        return _random_seed_from_plan(user_mods)


def _random_seed_from_plan(user_mods):
    """
    Handles the case of getting a single reform mod dictionary
    """
    all_vals = []
    for year in sorted(user_mods.keys()):
        all_vals.append(str(year))
        reform = user_mods[year]
        for param in sorted(reform.keys()):
            try:
                tple = tuple(reform[param])
            except TypeError:
                # Not iterable value
                tple = tuple((reform[param],))
            all_vals.append(str((param, tple)))

    txt = u"".join(all_vals).encode("utf-8")
    hsh = hashlib.sha512(txt)
    seed = int(hsh.hexdigest(), 16)
    return seed % np.iinfo(np.uint32).max


def chooser(agg):
    """
    This is a transformation function that should be called on each group.
    It is assumed that the chunk 'agg' is a chunk of the 'mask' column.
    This chooser selects three of those mask indices. the output at that
    index is zero. all other outputs for each index is 1.
    """
    indices = np.where(agg)

    if len(indices[0]) > 2:
        choices = np.random.choice(indices[0], size=3, replace=False)
    else:
        msg = ("Not enough difference in taxable income when adding 1 dollar"
               "for chunk with name: " + agg.name)
        raise ValueError(msg)

    ans = [1] * len(agg)
    for ix in choices:
        ans[ix] = 0
    return ans


def drop_records(df1, df2, mask):
    """
    Modify datasets df1 and df2 by adding statistical 'fuzz'.
    df1 is the standard plan X and X'
    df2 is the user-specified plan (Plan Y)
    mask is the boolean mask where X and X' match
    This function groups both datasets based on the web application's
    income groupings (both weighted decile and income bins), and then
    pseudo-randomly picks three records to 'drop' within each bin.
    We keep track of the three dropped records in both group-by
    strategies and then use these 'flag' columns to modify all
    columns of interest, creating new '*_dec' columns for later
    statistics based on weighted deciles and '*_bin' columns
    for statitistics based on grouping by income bins.
    in each bin in two group-by actions. Lastly we calculate
    individual income tax differences, payroll tax differences, and
    combined tax differences between the baseline and reform
    for the two groupings.
    """
    # perform all statistics on (Y + X') - X

    # Group first
    df2['mask'] = mask
    df1['mask'] = mask

    df2 = add_weighted_income_bins(df2)
    df1 = add_weighted_income_bins(df1)
    gp2_dec = df2.groupby('bins')

    income_bins = WEBAPP_INCOME_BINS

    df2 = add_income_bins(df2, bins=income_bins)
    df1 = add_income_bins(df1, bins=income_bins)
    gp2_bin = df2.groupby('bins')

    # Transform to get the 'flag' column (3 choices to drop in each bin)
    df2['flag_dec'] = gp2_dec['mask'].transform(chooser)
    df2['flag_bin'] = gp2_bin['mask'].transform(chooser)

    # first calculate all of X'
    COLUMNS_TO_MAKE_NOISY = set(TABLE_COLUMNS) | set(STATS_COLUMNS)
    # these don't exist yet
    COLUMNS_TO_MAKE_NOISY.remove('num_returns_ItemDed')
    COLUMNS_TO_MAKE_NOISY.remove('num_returns_StandardDed')
    COLUMNS_TO_MAKE_NOISY.remove('num_returns_AMT')
    for col in COLUMNS_TO_MAKE_NOISY:
        df2[col + '_dec'] = (df2[col] * df2['flag_dec'] -
                             df1[col] * df2['flag_dec'] + df1[col])
        df2[col + '_bin'] = (df2[col] * df2['flag_bin'] -
                             df1[col] * df2['flag_bin'] + df1[col])

    # Difference in plans
    # Positive values are the magnitude of the tax increase
    # Negative values are the magnitude of the tax decrease
    df2['tax_diff_dec'] = df2['_iitax_dec'] - df1['_iitax']
    df2['tax_diff_bin'] = df2['_iitax_bin'] - df1['_iitax']
    df2['payrolltax_diff_dec'] = df2['_payrolltax_dec'] - df1['_payrolltax']
    df2['payrolltax_diff_bin'] = df2['_payrolltax_bin'] - df1['_payrolltax']
    df2['combined_diff_dec'] = df2['_combined_dec'] - df1['_combined']
    df2['combined_diff_bin'] = df2['_combined_bin'] - df1['_combined']

    return df1, df2


def groupby_means_and_comparisons(df1, df2, mask, debug=False):
    """
    df1 is the standard plan X and X'
    df2 is the user-specified plan (Plan Y)
    mask is the boolean mask where X and X' match
    """

    df1, df2 = drop_records(df1, df2, mask)

    # Totals for diff between baseline and reform
    dec_sum = (df2['tax_diff_dec'] * df2['s006']).sum()
    bin_sum = (df2['tax_diff_bin'] * df2['s006']).sum()
    pr_dec_sum = (df2['payrolltax_diff_dec'] * df2['s006']).sum()
    pr_bin_sum = (df2['payrolltax_diff_bin'] * df2['s006']).sum()
    combined_dec_sum = (df2['combined_diff_dec'] * df2['s006']).sum()
    combined_bin_sum = (df2['combined_diff_bin'] * df2['s006']).sum()

    # Totals for baseline
    sum_baseline = (df1['_iitax'] * df1['s006']).sum()
    pr_sum_baseline = (df1['_payrolltax'] * df1['s006']).sum()
    combined_sum_baseline = (df1['_combined'] * df1['s006']).sum()

    # Totals for reform
    sum_reform = (df2['_iitax_dec'] * df2['s006']).sum()
    pr_sum_reform = (df2['_payrolltax_dec'] * df2['s006']).sum()
    combined_sum_reform = (df2['_combined_dec'] * df2['s006']).sum()

    # Totals for reform

    # Create Difference tables, grouped by deciles and bins
    diffs_dec = dropq_diff_table(df1, df2,
                                 groupby="weighted_deciles",
                                 res_col='tax_diff',
                                 diff_col='_iitax',
                                 suffix="_dec", wsum=dec_sum)

    diffs_bin = dropq_diff_table(df1, df2,
                                 groupby="webapp_income_bins",
                                 res_col='tax_diff',
                                 diff_col='_iitax',
                                 suffix="_bin", wsum=bin_sum)

    pr_diffs_dec = dropq_diff_table(df1, df2,
                                    groupby="weighted_deciles",
                                    res_col='payrolltax_diff',
                                    diff_col='_payrolltax',
                                    suffix="_dec", wsum=pr_dec_sum)

    pr_diffs_bin = dropq_diff_table(df1, df2,
                                    groupby="webapp_income_bins",
                                    res_col='payrolltax_diff',
                                    diff_col='_payrolltax',
                                    suffix="_bin", wsum=pr_bin_sum)

    comb_diffs_dec = dropq_diff_table(df1, df2,
                                      groupby="weighted_deciles",
                                      res_col='combined_diff',
                                      diff_col='_combined',
                                      suffix="_dec", wsum=combined_dec_sum)

    comb_diffs_bin = dropq_diff_table(df1, df2,
                                      groupby="webapp_income_bins",
                                      res_col='combined_diff',
                                      diff_col='_combined',
                                      suffix="_bin", wsum=combined_bin_sum)

    mX_dec = create_distribution_table(df1, groupby='weighted_deciles',
                                       result_type='weighted_sum')

    mY_dec = dropq_dist_table(df2, groupby='weighted_deciles',
                              result_type='weighted_sum', suffix='_dec')

    mX_bin = create_distribution_table(df1, groupby='webapp_income_bins',
                                       result_type='weighted_sum')

    mY_bin = dropq_dist_table(df2, groupby='webapp_income_bins',
                              result_type='weighted_sum', suffix='_bin')

    return (mY_dec, mX_dec, diffs_dec, pr_diffs_dec, comb_diffs_dec,
            mY_bin, mX_bin, diffs_bin, pr_diffs_bin, comb_diffs_bin,
            dec_sum, pr_dec_sum, combined_dec_sum, sum_baseline,
            pr_sum_baseline, combined_sum_baseline, sum_reform,
            pr_sum_reform, combined_sum_reform)


def results(c):
    outputs = []
    for col in STATS_COLUMNS:
        outputs.append(getattr(c.records, col))

    return DataFrame(data=np.column_stack(outputs), columns=STATS_COLUMNS)


def run_nth_year_mtr_calc(year_n, start_year, is_strict, tax_dta,
                          user_mods="", return_json=True):
    # Only makes sense to run for budget years 1 through n-1 (not for year 0)
    assert year_n > 0

    # Specify elasticity_gdp and check for unknown parameters in user_mods
    elasticity_gdp = elasticity_of_gdp_year_n(user_mods, start_year, year_n)
    if is_strict:
        unknown_params = get_unknown_parameters(user_mods, start_year,
                                                additional={'elastic_gdp'})
        if unknown_params:
            raise ValueError('Unknown parameters: {}'.format(unknown_params))

    # Specify Consumption instance
    consump = Consumption()
    consump_assumptions = only_consumption_assumptions(user_mods, start_year)
    if consump_assumptions:
        consump.update_consumption(consump_assumptions)

    # Specify growdiff_baseline and growdiff_response
    growdiff_baseline = Growdiff()
    growdiff_response = Growdiff()
    # PROBLEM: dropq makes no distinction between the two Growdiff instances
    # PROBLEM: code here is using growdiff_baseline assumptions
    # PROBLEM: code here is missing growdiff_response assumptions
    growdiff_baseline_assumptions = only_growdiff_assumptions(user_mods,
                                                              start_year)
    growdiff_response_assumptions = None  # PROBLEM: temporary "fix"

    # Create pre-reform and post-reform Growfactors instances
    growfactors_pre = Growfactors()
    growfactors_post = Growfactors()
    if growdiff_baseline_assumptions:
        growdiff_baseline.update_growdiff(growdiff_baseline_assumptions)
        growdiff_baseline.apply_to(growfactors_pre)
        growdiff_baseline.apply_to(growfactors_post)
    if growdiff_response_assumptions:
        growdiff_response.update_growdiff(growdiff_response_assumptions)
        growdiff_response.apply_to(growfactors_post)

    # Create pre-reform Calculator instance
    records1 = Records(data=tax_dta.copy(deep=True),
                       gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=records1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    assert calc1.current_year == start_year

    # Create post-reform Calculator instance
    records2 = Records(data=tax_dta.copy(deep=True),
                       gfactors=growfactors_post)
    policy2 = Policy(gfactors=growfactors_post)
    policy_reform = only_reform_mods(user_mods, start_year)
    policy2.implement_reform(policy_reform)
    calc2 = Calculator(policy=policy2, records=records2, consumption=consump)
    while calc2.current_year < start_year:
        calc2.increment_year()
    assert calc2.current_year == start_year

    # Get a random seed based on user specified plan
    seed = random_seed_from_plan(user_mods)
    np.random.seed(seed)
    for i in range(0, year_n - 1):
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    calc2.calc_all()

    mtr_fica_x, mtr_iit_x, mtr_combined_x = calc1.mtr()
    mtr_fica_y, mtr_iit_y, mtr_combined_y = calc2.mtr()

    # Assert that the current year is one behind the year we are calculating
    assert (calc1.current_year + 1) == (start_year + year_n)
    assert (calc2.current_year + 1) == (start_year + year_n)

    after_tax_mtr_x = 1 - ((mtr_combined_x * calc1.records.c00100 *
                            calc1.records.s006).sum() /
                           (calc1.records.c00100 * calc1.records.s006).sum())

    after_tax_mtr_y = 1 - ((mtr_combined_y * calc2.records.c00100 *
                            calc2.records.s006).sum() /
                           (calc2.records.c00100 * calc2.records.s006).sum())

    diff_avg_mtr_combined_y = after_tax_mtr_y - after_tax_mtr_x
    percent_diff_mtr = diff_avg_mtr_combined_y / after_tax_mtr_x

    gdp_effect_y = percent_diff_mtr * elasticity_gdp

    gdp_df = pd.DataFrame(data=[gdp_effect_y], columns=["col0"])

    if not return_json:
        return gdp_effect_y

    gdp_elast_names_i = [x + '_' + str(year_n) for x in GDP_elast_row_names]

    gdp_elast_total = create_json_table(gdp_df, row_names=gdp_elast_names_i,
                                        num_decimals=5)

    # Make the one-item lists of strings just strings
    gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())

    return gdp_elast_total


def calculate_baseline_and_reform(year_n, start_year, is_strict,
                                  tax_dta="", user_mods=""):
    # Check user_mods for unknown parameters
    if is_strict:
        unknown_params = get_unknown_parameters(user_mods, start_year)
        if unknown_params:
            raise ValueError("Unknown parameters: {}".format(unknown_params))

    # Specify Consumption instance
    consump = Consumption()
    consump_assumptions = only_consumption_assumptions(user_mods, start_year)
    if consump_assumptions:
        consump.update_consumption(consump_assumptions)

    # Specify growdiff_baseline and growdiff_response
    growdiff_baseline = Growdiff()
    growdiff_response = Growdiff()
    # PROBLEM: dropq makes no distinction between the two Growdiff instances
    # PROBLEM: code here is using growdiff_baseline assumptions
    # PROBLEM: code here is missing growdiff_response assumptions
    growdiff_baseline_assumptions = only_growdiff_assumptions(user_mods,
                                                              start_year)
    growdiff_response_assumptions = None  # PROBLEM: temporary "fix"

    # Create pre-reform and post-reform Growfactors instances
    growfactors_pre = Growfactors()
    growfactors_post = Growfactors()
    if growdiff_baseline_assumptions:
        growdiff_baseline.update_growdiff(growdiff_baseline_assumptions)
        growdiff_baseline.apply_to(growfactors_pre)
        growdiff_baseline.apply_to(growfactors_post)
    if growdiff_response_assumptions:
        growdiff_response.update_growdiff(growdiff_response_assumptions)
        growdiff_response.apply_to(growfactors_post)

    # Create pre-reform Calculator instance
    recs1 = Records(data=tax_dta.copy(deep=True),
                    gfactors=growfactors_pre)
    policy1 = Policy(gfactors=growfactors_pre)
    calc1 = Calculator(policy=policy1, records=recs1, consumption=consump)
    while calc1.current_year < start_year:
        calc1.increment_year()
    calc1.calc_all()
    assert calc1.current_year == start_year

    # Create pre-reform Calculator instance with extra income
    recs1p = Records(data=tax_dta.copy(deep=True),
                     gfactors=growfactors_pre)
    recs1p.e00200 += 1.0  # add $1 to total wages&salaries of each filing unit
    policy1p = Policy(gfactors=growfactors_pre)
    calc1p = Calculator(policy=policy1p, records=recs1p, consumption=consump)
    while calc1p.current_year < start_year:
        calc1p.increment_year()
    calc1p.calc_all()
    assert calc1p.current_year == start_year

    # Construct mask to show which of the calc1 and calc1p results differ
    soit1 = results(calc1)
    soit1p = results(calc1p)
    mask = (soit1._iitax != soit1p._iitax)

    # Specify Behavior instance
    behv = Behavior()
    behavior_assumptions = only_behavior_assumptions(user_mods, start_year)
    if behavior_assumptions:
        behv.update_behavior(behavior_assumptions)

    # Prevent both behavioral response and growdiff response
    if behv.has_any_response() and growdiff_response.has_any_response():
        msg = 'BOTH behavior AND growdiff_response HAVE RESPONSE'
        raise ValueError(msg)

    # Create post-reform Calculator instance with behavior
    recs2 = Records(data=tax_dta.copy(deep=True),
                    gfactors=growfactors_post)
    policy2 = Policy(gfactors=growfactors_post)
    policy_reform = only_reform_mods(user_mods, start_year)
    policy2.implement_reform(policy_reform)
    calc2 = Calculator(policy=policy2, records=recs2, consumption=consump,
                       behavior=behv)
    while calc2.current_year < start_year:
        calc2.increment_year()
    calc2.calc_all()
    assert calc2.current_year == start_year

    # Get a random seed based on user_mods and calc_all() for nth year
    seed = random_seed_from_plan(user_mods)
    np.random.seed(seed)
    for i in range(0, year_n):
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    if calc2.behavior.has_response():
        calc2 = Behavior.response(calc1, calc2)
    else:
        calc2.calc_all()

    # Return results and mask
    soit1 = results(calc1)
    soit2 = results(calc2)
    return soit1, soit2, mask


def run_nth_year(year_n, start_year, is_strict, tax_dta="", user_mods="",
                 return_json=True):

    start_time = time.time()
    soit_baseline, soit_reform, mask = calculate_baseline_and_reform(
        year_n, start_year, is_strict, tax_dta, user_mods)

    # Means of plan Y by decile
    # diffs of plan Y by decile
    # Means of plan Y by income bin
    # diffs of plan Y by income bin
    (mY_dec, mX_dec, df_dec, pdf_dec, cdf_dec, mY_bin, mX_bin, df_bin,
        pdf_bin, cdf_bin, diff_sum, payrolltax_diff_sum, combined_diff_sum,
        sum_baseline, pr_sum_baseline, combined_sum_baseline, sum_reform,
        pr_sum_reform,
        combined_sum_reform) = groupby_means_and_comparisons(soit_baseline,
                                                             soit_reform, mask)

    elapsed_time = time.time() - start_time
    print("elapsed time for this run: ", elapsed_time)
    start_year += 1

    tots = [diff_sum, payrolltax_diff_sum, combined_diff_sum]
    fiscal_tots_diff = pd.DataFrame(data=tots, index=total_row_names)

    tots_baseline = [sum_baseline, pr_sum_baseline, combined_sum_baseline]
    fiscal_tots_baseline = pd.DataFrame(data=tots_baseline,
                                        index=total_row_names)

    tots_reform = [sum_reform, pr_sum_reform, combined_sum_reform]
    fiscal_tots_reform = pd.DataFrame(data=tots_reform,
                                      index=total_row_names)

    # Get rid of negative incomes
    df_bin.drop(df_bin.index[0], inplace=True)
    pdf_bin.drop(pdf_bin.index[0], inplace=True)
    cdf_bin.drop(cdf_bin.index[0], inplace=True)
    mY_bin.drop(mY_bin.index[0], inplace=True)
    mX_bin.drop(mX_bin.index[0], inplace=True)

    def append_year(x):
        x.columns = [str(col) + "_{}".format(year_n) for col in x.columns]
        return x

    if not return_json:
        return (append_year(mY_dec), append_year(mX_dec), append_year(df_dec),
                append_year(pdf_dec), append_year(cdf_dec),
                append_year(mY_bin), append_year(mX_bin), append_year(df_bin),
                append_year(pdf_bin), append_year(cdf_bin),
                append_year(fiscal_tots_diff),
                append_year(fiscal_tots_baseline),
                append_year(fiscal_tots_reform))

    decile_row_names_i = [x + '_' + str(year_n) for x in decile_row_names]

    bin_row_names_i = [x + '_' + str(year_n) for x in bin_row_names]

    total_row_names_i = [x + '_' + str(year_n) for x in total_row_names]

    mY_dec_table_i = create_json_table(mY_dec,
                                       row_names=decile_row_names_i,
                                       column_types=planY_column_types)

    mX_dec_table_i = create_json_table(mX_dec,
                                       row_names=decile_row_names_i,
                                       column_types=planY_column_types)

    df_dec_table_i = create_json_table(df_dec,
                                       row_names=decile_row_names_i,
                                       column_types=diff_column_types)

    pdf_dec_table_i = create_json_table(pdf_dec,
                                        row_names=decile_row_names_i,
                                        column_types=diff_column_types)

    cdf_dec_table_i = create_json_table(cdf_dec,
                                        row_names=decile_row_names_i,
                                        column_types=diff_column_types)

    mY_bin_table_i = create_json_table(mY_bin,
                                       row_names=bin_row_names_i,
                                       column_types=planY_column_types)

    mX_bin_table_i = create_json_table(mX_bin,
                                       row_names=bin_row_names_i,
                                       column_types=planY_column_types)

    df_bin_table_i = create_json_table(df_bin,
                                       row_names=bin_row_names_i,
                                       column_types=diff_column_types)

    pdf_bin_table_i = create_json_table(pdf_bin,
                                        row_names=bin_row_names_i,
                                        column_types=diff_column_types)

    cdf_bin_table_i = create_json_table(cdf_bin,
                                        row_names=bin_row_names_i,
                                        column_types=diff_column_types)

    fiscal_yr_total_df = create_json_table(fiscal_tots_diff,
                                           row_names=total_row_names_i)

    fiscal_yr_total_bl = create_json_table(fiscal_tots_baseline,
                                           row_names=total_row_names_i)

    fiscal_yr_total_rf = create_json_table(fiscal_tots_reform,
                                           row_names=total_row_names_i)

    # Make the one-item lists of strings just strings
    fiscal_yr_total_df = dict((k, v[0]) for k, v in fiscal_yr_total_df.items())
    fiscal_yr_total_bl = dict((k, v[0]) for k, v in fiscal_yr_total_bl.items())
    fiscal_yr_total_rf = dict((k, v[0]) for k, v in fiscal_yr_total_rf.items())

    return (mY_dec_table_i, mX_dec_table_i, df_dec_table_i, pdf_dec_table_i,
            cdf_dec_table_i, mY_bin_table_i, mX_bin_table_i, df_bin_table_i,
            pdf_bin_table_i, cdf_bin_table_i, fiscal_yr_total_df,
            fiscal_yr_total_bl, fiscal_yr_total_rf)


def run_models(tax_dta, start_year, is_strict=False, user_mods="",
               return_json=True, num_years=NUM_YEARS_DEFAULT):
    num_fiscal_year_totals = list()
    mY_dec_table = dict()
    mX_dec_table = dict()
    df_dec_table = dict()
    pdf_dec_table = dict()
    cdf_dec_table = dict()
    mY_bin_table = dict()
    mX_bin_table = dict()
    df_bin_table = dict()
    pdf_bin_table = dict()
    cdf_bin_table = dict()
    for year_n in range(0, num_years):
        json_tables = run_nth_year(year_n, start_year=start_year,
                                   is_strict=is_strict,
                                   tax_dta=tax_dta,
                                   user_mods=user_mods,
                                   return_json=return_json)
        # map json_tables to named tables
        (mY_dec_table_i, mX_dec_table_i, df_dec_table_i, pdf_dec_table_i,
         cdf_dec_table_i, mY_bin_table_i, mX_bin_table_i, df_bin_table_i,
         pdf_bin_table_i, cdf_bin_table_i, num_fiscal_year_total,
         num_fiscal_year_total_bl, num_fiscal_year_total_rf) = json_tables
        # update list and dictionaries
        num_fiscal_year_totals.append(num_fiscal_year_total)
        num_fiscal_year_totals.append(num_fiscal_year_total_bl)
        num_fiscal_year_totals.append(num_fiscal_year_total_rf)
        mY_dec_table.update(mY_dec_table_i)
        mX_dec_table.update(mX_dec_table_i)
        df_dec_table.update(df_dec_table_i)
        pdf_dec_table.update(pdf_dec_table_i)
        cdf_dec_table.update(cdf_dec_table_i)
        mY_bin_table.update(mY_bin_table_i)
        mX_bin_table.update(mX_bin_table_i)
        df_bin_table.update(df_bin_table_i)
    return (mY_dec_table, mX_dec_table, df_dec_table, pdf_dec_table,
            cdf_dec_table, mY_bin_table, mX_bin_table, df_bin_table,
            pdf_bin_table, cdf_bin_table, num_fiscal_year_totals)


def run_gdp_elast_models(tax_dta, start_year, is_strict=False, user_mods="",
                         return_json=True, num_years=NUM_YEARS_DEFAULT):
    gdp_elasticity_totals = []
    for year_n in range(1, num_years):
        gdp_elast_i = run_nth_year_mtr_calc(year_n, start_year=start_year,
                                            is_strict=is_strict,
                                            tax_dta=tax_dta,
                                            user_mods=user_mods,
                                            return_json=return_json)
        gdp_elasticity_totals.append(gdp_elast_i)
    return gdp_elasticity_totals


def format_macro_results(diff_data, return_json=True):
    ogusadf = pd.DataFrame(diff_data)
    if not return_json:
        return ogusadf
    column_types = [float] * diff_data.shape[1]
    df_ogusa_table = create_json_table(ogusadf,
                                       row_names=ogusa_row_names,
                                       column_types=column_types,
                                       num_decimals=3)
    return df_ogusa_table
