"""
Command-line interface to Tax-Calculator for DYNAMIC tax analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 tcdyn.py
# pylint --disable=locally-disabled tcdyn.py

import argparse
import sys
from taxcalc import TaxCalcIO


def main():
    """
    Contains DYNAMIC command-line interface (CLI) to TaxCalcIO class.
    """
    # pylint: disable=too-many-return-statements
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        prog='python tcdyn.py',
        description=('Writes to a file the federal income and payroll tax '
                     'OUTPUT for each filing unit specified in the INPUT '
                     'file, with the OUTPUT computed from the INPUT for the '
                     'TAXYEAR using Tax-Calculator operating under DYNAMIC '
                     'analysis assumptions. The OUTPUT file is a '
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
                              'assumption file.  No --assump implies use of '
                              'static analysis assumptions.'),
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
    parser.add_argument('--dump',
                        help=('optional flag that causes OUTPUT to contain '
                              'all INPUT variables (possibly aged to TAXYEAR) '
                              'and all calculated tax variables, where all '
                              'the variables are named using their internal '
                              'Tax-Calculator names.'),
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    arg_errors = False
    # check INPUT file name
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name;\n')
        arg_errors = True
    # check TAXYEAR value
    if args.TAXYEAR == 0:
        sys.stderr.write('ERROR: must specify TAXYEAR >= 2013;\n')
        arg_errors = True
    # check that --reform option used
    if not args.reform:
        sys.stderr.write('ERROR: must use --reform\n')
        arg_errors = True
    # check consistency of --reform and --graph options
    if args.graph and not args.reform:
        sys.stderr.write('ERROR: cannot specify --graph without --reform\n')
        arg_errors = True
    # check consistency of --exact and --graph options
    if args.exact and args.graph:
        sys.stderr.write('ERROR: cannot specify both --exact and --graph\n')
        arg_errors = True
    if arg_errors:
        sys.stderr.write('USAGE: python tcdyn.py --help\n')
        return 1
    # do DYNAMIC tax analysis
    aging = args.INPUT.endswith('puf.csv') or args.INPUT.endswith('cps.csv')
    TaxCalcIO.dynamic_analysis(input_data=args.INPUT,
                               tax_year=args.TAXYEAR,
                               reform=args.reform,
                               assump=args.assump,
                               aging_input_data=aging,
                               exact_calculations=args.exact,
                               # extra parameters go here
                               writing_output_file=True,
                               output_graph=args.graph,
                               output_dump=args.dump)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
