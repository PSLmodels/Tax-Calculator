"""
Python script that computes behavioral-response results produced by
Tax-Calculator via the taxcalc package running on this computer.
These results can be compared with hand-generated results produced
by TaxBrain running in the cloud.

COMMAND-LINE USAGE: python behavior.py --help

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 behavior.py
# pylint --disable=locally-disabled behavior.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
PUFCSV_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, Behavior


def main(reform_year, calc_year, sub_elasticity, inc_elasticity):
    """
    Highest-level logic of behavior.py script that produces Tax-Calculator
    behavioral-response results running the taxcalc package on this computer.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=protected-access
    if not os.path.isfile(PUFCSV_PATH):
        sys.stderr.write('ERROR: file {} does not exist\n'.format(PUFCSV_PATH))
        return 1
    # create current-law-policy object
    cur = Policy()
    # specify policy reform
    reform_dict = {reform_year: {'_SS_Earnings_c': [1.0e99]}}
    sys.stdout.write('REFORM: pop-the-cap in {}\n'.format(reform_year))
    # create reform-policy object
    ref = Policy()
    ref.implement_reform(reform_dict)
    # create behavioral-response object
    behv = Behavior()  # default object has all response parameters set to zero
    # create reform-policy Calculator object with/without behavioral responses
    calc_ref = Calculator(policy=ref, verbose=False, behavior=behv,
                          records=Records(data=PUFCSV_PATH))
    # compute no-behavorial-reponse effect on income and fica tax revenues
    cyr = calc_year
    # (a) with all behavioral-reponse parameters set to zero
    itax_s, fica_s = revenue(cyr, calc_ref)
    # (b) with both substitution- and income-effect behavioral-reponse params
    behv_params = {behv.start_year: {'_BE_sub': [sub_elasticity],
                                     '_BE_inc': [inc_elasticity]}}
    behv.update_behavior(behv_params)  # now used by calc_ref object
    itax_d, fica_d = revenue(cyr, calc_ref)  # dynamic analysis
    bhv = '{},SUB_ELASTICITY,INC_ELASTICITY= {} {}\n'
    yridx = cyr - behv.start_year
    sys.stdout.write(bhv.format(cyr, behv._BE_sub[yridx], behv._BE_inc[yridx]))
    res = '{},{},REV_STATIC(S),REV_DYNAMIC(D),D-S= {:.1f} {:.1f} {:.1f}\n'
    sys.stdout.write(res.format(cyr, 'ITAX', itax_s, itax_d, itax_d - itax_s))
    sys.stdout.write(res.format(cyr, 'FICA', fica_s, fica_d, fica_d - fica_s))
    # return no-error exit code
    return 0
# end of main function code


def revenue(year, calc):
    """
    Return aggregate, weighted income and payroll tax revenue (in billions).
    """
    calc.advance_to_year(year)
    calc.calc_all()
    # pylint: disable=protected-access
    itax_rev = (calc.records._iitax * calc.records.s006).sum()
    fica_rev = (calc.records._fica * calc.records.s006).sum()
    return (round(itax_rev * 1.0e-9, 3), round(fica_rev * 1.0e-9, 3))


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python behavior.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=('Writes to stdout behavioral-response results produced '
                     'by Tax-Calculator via\nthe taxcalc package running on '
                     'this computer.  These results can be compared\nwith '
                     'hand-generated results produced by TaxBrain running '
                     'in the cloud.')
    )
    PARSER.add_argument('REFORM_YEAR', type=int,
                        help=('calendar year of pop-the-cap reform'))
    PARSER.add_argument('CALC_YEAR', type=int,
                        help=('calendar year of calculation results'))
    PARSER.add_argument('SUB_ELAST', type=float,
                        help=('substitution elasticity of behavior'))
    PARSER.add_argument('INC_ELAST', type=float,
                        help=('income elasticity of behavior'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.REFORM_YEAR, ARGS.CALC_YEAR,
                  ARGS.SUB_ELAST, ARGS.INC_ELAST))
