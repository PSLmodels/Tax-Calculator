"""
Command-line interface (CLI) to Tax-Calculator,
which can be accessed as 'tc' from an installed taxcalc package.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 tc.py
# pylint --disable=locally-disabled tc.py

import os
import sys
import argparse
from taxcalc import TaxCalcIO, Policy


def main():
    """
    Contains command-line interface (CLI) to Tax-Calculator TaxCalcIO class.
    """
    # parse command-line arguments:
    usage_str = 'tc INPUT TAXYEAR {}{}{}'.format(
        '[--reform REFORM] [--assump  ASSUMP]\n',
        '                        ',
        '[--exact] [--graph] [--ceeu] [--dump]')
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Writes to a file the federal income and payroll tax '
                     'OUTPUT for each filing unit specified in the INPUT '
                     'file, with the OUTPUT computed from the INPUT for the '
                     'TAXYEAR using Tax-Calculator. The OUTPUT file is a '
                     'CSV-formatted file that contains tax information for '
                     'each INPUT filing unit.'))
    parser.add_argument('INPUT', nargs='?',
                        help=('INPUT is name of CSV-formatted file that '
                              'contains for each filing unit variables used '
                              'to compute taxes for TAXYEAR.'),
                        default='')
    parser.add_argument('TAXYEAR', nargs='?',
                        help=('TAXYEAR is calendar year for which taxes '
                              'are computed.'),
                        type=int,
                        default=0)
    parser.add_argument('--reform',
                        help=('REFORM is name of optional JSON reform file. '
                              'No --reform implies use of current-law '
                              'policy.'),
                        default=None)
    parser.add_argument('--assump',
                        help=('ASSUMP is name of optional JSON economic '
                              'assumptions file.  No --assump implies use '
                              'of no customized assumptions.'),
                        default=None)
    parser.add_argument('--exact',
                        help=('optional flag that suppresses the smoothing of '
                              '"stair-step" provisions in the tax law that '
                              'complicate marginal-tax-rate calculations.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--graph',
                        help=('optional flag that causes graphs to be written '
                              'to HTML files for viewing in browser.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--ceeu',
                        help=('optional flag that causes normative welfare '
                              'statistics, including certainty-equivalent '
                              'expected-utility (ceeu) of after-tax income '
                              'values for different '
                              'constant-relative-risk-aversion parameter '
                              'values, to be written to screen.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--dump',
                        help=('optional flag that causes OUTPUT to contain '
                              'all INPUT variables (possibly extrapolated '
                              'to TAXYEAR) and all calculated tax variables, '
                              'where all the variables are named using their '
                              'internal Tax-Calculator names.  No --dump '
                              'option implies OUTPUT contains minimal tax '
                              'output.'),
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    arg_errors = False
    # check INPUT file name
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name\n')
        arg_errors = True
    else:
        if not args.INPUT.endswith('.csv'):
            sys.stderr.write('ERROR: INPUT file name does not end in .csv\n')
            arg_errors = True
        elif not os.path.isfile(args.INPUT):
            sys.stderr.write('ERROR: INPUT file could not be found\n')
            arg_errors = True
    # check TAXYEAR value
    first_taxyear = Policy.JSON_START_YEAR
    last_taxyear = Policy.LAST_BUDGET_YEAR
    if args.TAXYEAR < first_taxyear:
        sys.stderr.write('ERROR: TAXYEAR < {}\n'.format(first_taxyear))
        arg_errors = True
    elif args.TAXYEAR > last_taxyear:
        sys.stderr.write('ERROR: TAXYEAR > {}\n'.format(last_taxyear))
        arg_errors = True
    # check REFORM value
    if args.reform is not None:
        if not args.reform.endswith('.json'):
            sys.stderr.write('ERROR: REFORM file name does not end in .json\n')
            arg_errors = True
        elif not os.path.isfile(args.reform):
            sys.stderr.write('ERROR: REFORM file could not be found\n')
            arg_errors = True
    # check ASSUMP value
    if args.assump is not None:
        if not args.assump.endswith('.json'):
            sys.stderr.write('ERROR: ASSUMP file name does not end in .json\n')
            arg_errors = True
        elif not os.path.isfile(args.assump):
            sys.stderr.write('ERROR: ASSUMP file could not be found\n')
            arg_errors = True
    # exit if any argument errors
    if arg_errors:
        sys.stderr.write('USAGE: tc --help\n')
        return 1
    # instantiate TaxCalcIO object and do tax analysis
    aging = args.INPUT.endswith('puf.csv') or args.INPUT.endswith('cps.csv')
    tcio = TaxCalcIO(input_data=args.INPUT,
                     tax_year=args.TAXYEAR,
                     reform=args.reform,
                     assump=args.assump,
                     growdiff_response=None,
                     aging_input_data=aging,
                     exact_calculations=args.exact)
    tcio.analyze(writing_output_file=True,
                 output_graph=args.graph,
                 output_ceeu=args.ceeu,
                 output_dump=args.dump)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
