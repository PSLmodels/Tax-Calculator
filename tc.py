"""
Command-line interface to Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 tc.py
# pylint --disable=locally-disabled tc.py

import argparse
import sys
from taxcalc import TaxCalcIO


def main():
    """
    Contains command-line interface to the Tax-Calculator TaxCalcIO class.
    """
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        prog='python tc.py',
        description=('Writes to a file the federal income and payroll tax '
                     'OUTPUT for each filing unit specified in the INPUT '
                     'file, with the OUTPUT computed from the INPUT for the '
                     'TAXYEAR using Tax-Calculator. The OUTPUT file is a '
                     'CSV-formatted file that contains tax information for '
                     'each INPUT filing unit.'))
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of CSV-formatted file that '
                              'contains for each filing unit variables used '
                              'to compute taxes for TAXYEAR.'))
    parser.add_argument('TAXYEAR', nargs='?', default=0,
                        help=('TAXYEAR is calendar year for which taxes '
                              'are computed.'),
                        type=int)
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
                        help=('optional flag to suppress smoothing in income '
                              'tax calculations that eliminate marginal-tax-'
                              'rate-complicating "stair-steps".  The default '
                              'is to smooth, and therefore, not to do the '
                              'exact calculations called for on tax forms.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--graph',
                        help=('optional flag that causes HTML graphs to be '
                              'generated.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--ceeu',
                        help=('optional flag that causes normative welfare '
                              'statistics, including certainty-equivalent '
                              'expected-utility of after-tax income values '
                              'for different constant-relative-risk-aversion '
                              'parameter values, to be written to screen.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--dump',
                        help=('optional flag that causes OUTPUT to contain '
                              'all INPUT variables (possibly aged to TAXYEAR) '
                              'and all calculated tax variables, where the '
                              'variables are named using their internal '
                              'Tax-Calculator names.'),
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    # check INPUT file name
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name;\n')
        sys.stderr.write('USAGE: python tc.py --help\n')
        return 1
    # check TAXYEAR value
    if args.TAXYEAR == 0:
        sys.stderr.write('ERROR: must specify TAXYEAR >= 2013;\n')
        sys.stderr.write('USAGE: python tc.py --help\n')
        return 1
    # check consistency of --reform and --assump options
    if args.assump and not args.reform:
        sys.stderr.write('ERROR: cannot use --assump without --reform\n')
        sys.stderr.write('USAGE: python tc.py --help\n')
        return 1
    # check consistency of --reform and --graph options
    if args.graph and not args.reform:
        sys.stderr.write('ERROR: cannot specify --graph without --reform\n')
        sys.stderr.write('USAGE: python tc.py --help\n')
        return 1
    # check consistency of --reform and --ceeu options
    if args.ceeu and not args.reform:
        sys.stderr.write('ERROR: cannot specify --ceeu without --reform\n')
        sys.stderr.write('USAGE: python tc.py --help\n')
        return 1
    # instantiate TaxCalcIO object and do federal tax calculations
    if args.INPUT == 'puf.csv' or args.INPUT == 'cps.csv':
        aging_input = True
    else:
        aging_input = False
    tcio = TaxCalcIO(input_data=args.INPUT,
                     tax_year=args.TAXYEAR,
                     reform=args.reform,
                     assump=args.assump,
                     aging_input_data=aging_input,
                     exact_calculations=args.exact,
                     output_records=False,
                     csv_dump=False)
    tcio.calculate(writing_output_file=True,
                   exact_output=args.exact,
                   output_weights=True,  # TODO: remove this argument
                   output_mtr_wrt_fullcomp=False,  # TODO: remove this argument
                   output_ceeu=args.ceeu)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
