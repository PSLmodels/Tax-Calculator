"""
Python script that writes to stdout a reform JSON file suitable for
input into the reforms.py script in this directory.

COMMAND-LINE USAGE: python make_reforms.py > ref.json
          AND THEN: python reforms.py --filename ref.json

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 make_reforms.py
# pylint --disable=locally-disabled make_reforms.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy  # pylint: disable=import-error


START_YEAR = 2016  # year of policy reform
SCALE_FACTOR = 1.10  # multiplicative scaling factor for most policy parameters
PARAMS_NOT_SCALED = set(['_ACTC_ChildNum',
                         '_ID_Charity_crt_Cash',
                         '_ID_Charity_crt_Asset',
                         '_ID_BenefitSurtax_Switch'])
FIRST_YEAR = Policy.JSON_START_YEAR
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
SPC = '    '
TAB = '{}{}{}'.format(SPC, SPC, SPC)


def main():
    """
    Highest-level logic of make_reforms.py script.
    """
    # get current-law-policy parameters for START_YEAR in a Policy object
    clp = Policy()
    clp.set_year(START_YEAR)

    # construct of set of Policy parameter names
    policy_param_names = set(getattr(clp, '_vals').keys())

    # remove names of policy parameters not currently used in TaxBrain
    param_names = policy_param_names - PARAMS_NOT_USED_IN_TAXBRAIN

    # write a JSON entry for each parameter
    sys.stdout.write('{}\n'.format('{'))
    sys.stdout.write('{}"1": {}\n'.format(SPC, '{'))
    sys.stdout.write('{}{}"replications": 1,\n'.format(SPC, SPC))
    sys.stdout.write('{}{}"start_year": {},\n'.format(SPC, SPC, START_YEAR))
    sys.stdout.write('{}{}"specification": {}\n'.format(SPC, SPC, '{'))
    idx = START_YEAR - FIRST_YEAR
    num_names = len(param_names)
    num = 0
    for name in param_names:
        num += 1
        values = getattr(clp, name)
        value = values[idx]
        sys.stdout.write('{}"{}": {}\n'.format(TAB, name, '{'))
        if isinstance(value, float):
            if name in PARAMS_NOT_SCALED:
                val = value
            else:
                val = value * SCALE_FACTOR
        else:
            if name in PARAMS_NOT_SCALED:
                val = value.tolist()
            else:
                val = [v * SCALE_FACTOR for v in value.tolist()]
        sys.stdout.write('{}{}"{}": [{}]\n'.format(TAB, SPC, START_YEAR, val))
        if num == num_names:
            sys.stdout.write('{}{}\n'.format(TAB, '}'))
        else:
            sys.stdout.write('{}{}\n'.format(TAB, '},'))
    sys.stdout.write('{}{}{}\n'.format(SPC, SPC, '}'))
    sys.stdout.write('{}{}\n'.format(SPC, '}'))
    sys.stdout.write('{}\n'.format('}'))

    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
