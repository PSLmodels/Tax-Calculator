"""
Python script that writes to stdout a reform JSON file suitable for
input into the reforms.py script in this directory.

COMMAND-LINE USAGE: python make_reforms.py > all.json
          AND THEN: python reforms.py --filename all.json

COMMAND-LINE HELP: python make_reforms.py --help

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 make_reforms.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy make_r*.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
import argparse
import numpy as np
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy  # pylint: disable=import-error


PARAMS_NOT_SCALED = set(['_ACTC_ChildNum',
                         '_ID_Charity_crt_Cash',
                         '_ID_Charity_crt_Asset',
                         '_ID_BenefitSurtax_Switch',
                         '_ID_BenefitSurtax_crt',
                         '_ID_BenefitSurtax_trt'])
PARAMS_NOT_USED_IN_TAXBRAIN = set(['_ACTC_Income_thd',
                                   '_ALD_Interest_ec',
                                   '_AMT_Child_em',
                                   '_AMT_em_pe',
                                   '_AMT_thd_MarriedS',
                                   '_CDCC_crt',
                                   '_CDCC_ps',
                                   '_CTC_additional',
                                   '_CTC_additional_ps',
                                   '_CTC_additional_prt',
                                   '_DCC_c',
                                   '_EITC_ps_MarriedJ',
                                   '_EITC_InvestIncome_c',
                                   '_EITC_MinEligAge',
                                   '_EITC_MaxEligAge',
                                   '_ETC_pe_Single',
                                   '_ETC_pe_Married',
                                   '_ETC_pe_Single',
                                   '_FEI_ec_c',
                                   '_ID_Casualty_HC',
                                   '_ID_Charity_HC',
                                   '_ID_InterestPaid_HC',
                                   '_ID_Medical_HC',
                                   '_ID_Miscellaneous_HC',
                                   '_KT_c_Age',
                                   '_LLC_Expense_c'])
PARAMS_WITHOUT_CPI_BUTTON_IN_TAXBRAIN = set(['_II_credit',
                                             '_II_credit_ps'])
PROVISIONS_ALL_TOGETHER = 1
PROVISIONS_EACH_SEPARATE = 2
FIRST_YEAR = Policy.JSON_START_YEAR
SPC = '    '
TAB = '{}{}{}'.format(SPC, SPC, SPC)


def main(start_year, delay_years, scale_factor, no_indexing, each_separate):
    """
    Highest-level logic of make_reforms.py script.
    """
    # check validity of function arguments
    if start_year < FIRST_YEAR:
        msg = 'ERROR: --year {} sets year before {}\n'
        sys.stderr.write(msg.format(start_year, FIRST_YEAR))
        return 1
    if scale_factor < 1.0:
        msg = 'ERROR: --scale {} sets scale below one\n'
        sys.stderr.write(msg.format(scale_factor))
        return 1
    if each_separate:
        reform = PROVISIONS_EACH_SEPARATE
    else:
        reform = PROVISIONS_ALL_TOGETHER

    # get current-law-policy parameters for start_year in a Policy object
    clp = Policy()
    clp.set_year(start_year)

    # construct of set of Policy parameter names
    policy_param_names = set(getattr(clp, '_vals').keys())

    # remove names of policy parameters not currently used by TaxBrain
    param_names = policy_param_names - PARAMS_NOT_USED_IN_TAXBRAIN

    # add *_cpi parameter names if no_indexing is true
    if no_indexing:
        param_names = param_names | indexed_parameter_names(clp, param_names)

    # remove "null" reform provisions
    if scale_factor == 1.0:
        excluded_names = set()
        for name in param_names:
            if not name.endswith('_cpi'):
                excluded_names.add(name)
        param_names = param_names - excluded_names

    # write a JSON entry for each parameter
    np.random.seed(seed=123456789)
    if reform == PROVISIONS_ALL_TOGETHER:
        write_all_together(param_names, clp,
                           start_year, delay_years,
                           scale_factor)
    elif reform == PROVISIONS_EACH_SEPARATE:
        write_each_separate(param_names, clp,
                            start_year, delay_years,
                            scale_factor)
    else:
        msg = 'ERROR: reform has illegal value {}\n'
        sys.stderr.write(msg.format(reform))
        return 1

    # return no-error exit code
    return 0
# end of main function code


def indexed_parameter_names(policy, param_names):
    """
    Return set of indexing-status parameter names for the parameters in
    specified parameter_name set that are indexed under specified policy.
    """
    indexed_names = set()
    values = getattr(policy, '_vals')
    for name in param_names:
        if values[name]['cpi_inflated']:
            if name not in PARAMS_WITHOUT_CPI_BUTTON_IN_TAXBRAIN:
                indexed_names.add(name + '_cpi')
    return indexed_names


def write_all_together(param_names, clp, start_year,
                       max_reform_delay_years, scale_factor):
    """
    Write JSON for one reform containing all the provisions together.
    """
    sys.stdout.write('{}\n'.format('{'))
    sys.stdout.write('{}"1": {}\n'.format(SPC, '{'))
    sys.stdout.write('{}{}"replications": 1,\n'.format(SPC, SPC))
    sys.stdout.write('{}{}"start_year": {},\n'.format(SPC, SPC, start_year))
    sys.stdout.write('{}{}"specification": {}\n'.format(SPC, SPC, '{'))
    num_names = len(param_names)
    num = 0
    for name in sorted(param_names):
        num += 1
        yrs = np.random.random_integers(0, max_reform_delay_years)
        reform_year = start_year + yrs
        sys.stdout.write('{}"{}": {}\n'.format(TAB, name, '{'))
        if name.endswith('_cpi'):
            sys.stdout.write('{}{}"{}": false\n'.format(TAB, SPC, reform_year))
        else:
            value = new_value(clp, name, reform_year, scale_factor)
            sys.stdout.write('{}{}"{}": [{}]\n'.format(TAB, SPC,
                                                       reform_year, value))
        if num == num_names:
            sys.stdout.write('{}{}\n'.format(TAB, '}'))
        else:
            sys.stdout.write('{}{}\n'.format(TAB, '},'))
    sys.stdout.write('{}{}{}\n'.format(SPC, SPC, '}'))
    sys.stdout.write('{}{}\n'.format(SPC, '}'))
    sys.stdout.write('{}\n'.format('}'))
    return


def write_each_separate(param_names, clp, start_year,
                        max_reform_delay_years, scale_factor):
    """
    Write JSON for many reforms each containing a single provision.
    """
    num_names = len(param_names)
    num = 0
    sys.stdout.write('{}\n'.format('{'))
    for name in sorted(param_names):
        num += 1
        yrs = np.random.random_integers(0, max_reform_delay_years)
        reform_year = start_year + yrs
        sys.stdout.write('{}"{}": {}\n'.format(SPC, num, '{'))
        sys.stdout.write('{}{}"replications": 1,\n'.format(SPC, SPC))
        sys.stdout.write('{}{}"start_year": {},\n'.format(SPC, SPC,
                                                          start_year))
        sys.stdout.write('{}{}"specification": {}\n'.format(SPC, SPC, '{'))
        sys.stdout.write('{}"{}": {}\n'.format(TAB, name, '{'))
        if name.endswith('_cpi'):
            sys.stdout.write('{}{}"{}": false\n'.format(TAB, SPC, reform_year))
        else:
            value = new_value(clp, name, reform_year, scale_factor)
            sys.stdout.write('{}{}"{}": [{}]\n'.format(TAB, SPC,
                                                       reform_year, value))
        sys.stdout.write('{}{}\n'.format(TAB, '}'))
        sys.stdout.write('{}{}{}\n'.format(SPC, SPC, '}'))
        if num == num_names:
            sys.stdout.write('{}{}\n'.format(SPC, '}'))
        else:
            sys.stdout.write('{}{}\n'.format(SPC, '},'))
    sys.stdout.write('{}\n'.format('}'))
    return


def new_value(policy, name, reform_year, scale_factor):
    """
    Return new value for reform_year given policy, name, and scale_factor.
    """
    value = getattr(policy, name)[reform_year - FIRST_YEAR]
    if isinstance(value, float):
        if name in PARAMS_NOT_SCALED:
            val = value
        else:
            val = round(value * scale_factor, 5)
    else:  # value is a list
        if name in PARAMS_NOT_SCALED:
            val = value.tolist()
        else:
            val = [round(v * scale_factor, 5) for v in value.tolist()]
    return val


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python make_reforms.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=('Writes to stdout JSON file suitable for reading by the '
                     'reforms.py script\nusing its --filename FILENAME '
                     'option. '))
    PARSER.add_argument('--year', type=int, default=2016,
                        help=('optional flag to specify TaxBrain start year;\n'
                              'no flag implies start year is 2016.'))
    PARSER.add_argument('--delay', type=int, default=0,
                        help=('optional flag to specify maximum number '
                              'of random years\nreform provisions are '
                              'implemented after the year\nspecified by '
                              '--year option; no flag implies no delay.'))
    PARSER.add_argument('--scale', type=float, default=1.10,
                        help=('optional flag to specify multiplicative '
                              'scaling factor\nused to increase policy '
                              'parameters in each reform provision;\n'
                              'no flag implies use of a scaling factor of '
                              '1.10, which is\na ten percent increase in '
                              'each policy paramter.'))
    PARSER.add_argument('--noindexing', action='store_true',
                        help=('optional flag to specify reform provisions '
                              'that turn off\nall indexing of parameters '
                              'that are indexed under\ncurrent-law policy;\n'
                              'no flag implies indexing status of parameters '
                              'is unchanged.'))
    PARSER.add_argument('--separate', action='store_true',
                        help=('optional flag to specify that each reform '
                              'provision\nshould constitute its own reform;\n'
                              'no flag implies all reform provisions are\n'
                              'combined together into a single reform.'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.year, ARGS.delay, ARGS.scale,
                  ARGS.noindexing, ARGS.separate))
