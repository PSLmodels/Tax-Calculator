"""
Command-line interface (CLI) to Tax-Calculator,
which can be accessed as 'tc' from an installed taxcalc package.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 tc.py
# pylint --disable=locally-disabled tc.py

import sys
import argparse
from taxcalc import TaxCalcIO


def main():
    """
    Contains command-line interface (CLI) to Tax-Calculator TaxCalcIO class.
    """
    # parse command-line arguments:
    usage_str = 'tc INPUT TAXYEAR {}{}{}'.format(
        '[--reform REFORM] [--assump  ASSUMP]\n',
        '                        ',
        '[--exact] [--tables] [--graphs] [--ceeu] [--dump]')
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
    parser.add_argument('--tables',
                        help=('optional flag that causes distributional '
                              'tables to be written to a text file.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--graphs',
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
    # instantiate TaxCalcIO object and do tax analysis
    tcio = TaxCalcIO(input_data=args.INPUT,
                     tax_year=args.TAXYEAR,
                     reform=args.reform,
                     assump=args.assump)
    if len(tcio.errmsg) > 0:
        sys.stderr.write(tcio.errmsg)
        sys.stderr.write('USAGE: tc --help\n')
        return 1
    aging = args.INPUT.endswith('puf.csv') or args.INPUT.endswith('cps.csv')
    tcio.init(input_data=args.INPUT,
              tax_year=args.TAXYEAR,
              reform=args.reform,
              assump=args.assump,
              growdiff_response=None,
              aging_input_data=aging,
              exact_calculations=args.exact)
    if len(tcio.errmsg) > 0:
        sys.stderr.write(tcio.errmsg)
        sys.stderr.write('USAGE: tc --help\n')
        return 1
    tcio.analyze(writing_output_file=True,
                 output_tables=args.tables,
                 output_graphs=args.graphs,
                 output_ceeu=args.ceeu,
                 output_dump=args.dump)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
