"""
INCome TAX input-output capabilities for Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 inctax.py
# pylint --disable=locally-disabled inctax.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import sys
from taxcalc import IncomeTaxIO


def main():
    """
    Contains command-line interface to the Tax-Calculator IncomeTaxIO class.
    """
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        prog='python inctax.py',
        description=('Writes to a file the federal income tax OUTPUT for the '
                     'tax filing units specified in the INPUT file with the '
                     'OUTPUT computed from the INPUT for the TAXYEAR using '
                     'the Tax-Calculator. '
                     'The INPUT file is a CSV-formatted file that contains '
                     'variable names that include the Records.MUST_READ_VARS '
                     'set plus other variables.  The OUTPUT file is in '
                     'Internet-TAXSIM format.  The OUTPUT filename is the '
                     'INPUT filename (excluding the .csv suffix or '
                     '.gz suffix, or both) followed by '
                     'a string equal to "-YY" (where the YY is the last two '
                     'digits in the TAXYEAR) and all that is followed by a '
                     'trailing string.  The trailing string is ".out-inctax" '
                     'if no --reform option is specified; otherwise the '
                     'trailing string is ".out-inctax-REFORM" (excluding any '
                     '".json" ending to the REFORM filename).  The OUTPUT '
                     'file contains the first 28 Internet-TAXSIM output '
                     'variables.  Use --iohelp flag for more information. '
                     'For details on the Internet-TAXSIM version 9.3 '
                     'OUTPUT format, go to '
                     'http://users.nber.org/~taxsim/taxsim-calc9/'))
    parser.add_argument('--iohelp',
                        help=('optional flag to show INPUT and OUTPUT '
                              'variable definitions and exit'),
                        default=False,
                        action="store_true")
    parser.add_argument('--reform',
                        help=('REFORM is name of optional file that contains '
                              'reform "policy" parameters; the REFORM file '
                              'is specified using JSON that may include '
                              '//-comments. No --reform implies use of '
                              'current-law policy.'),
                        default=None)
    parser.add_argument('--assump',
                        help=('ASSUMP is name of optional file that contains '
                              'economic assumption parameters ("behavior", '
                              '"consumption" and "growth" parameters); the '
                              'ASSUMP file is specified using JSON that may '
                              'include //-comments. No --assump implies use '
                              'of static analysis assumptions.'),
                        default=None)
    parser.add_argument('--exact',
                        help=('optional flag to suppress smoothing in income '
                              'tax calculations that eliminate marginal-tax-'
                              'rate-complicating "stair-steps".  The default '
                              'is to smooth, and therefore, not to do the '
                              ' exact calculations called for in the tax '
                              'law.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--blowup',
                        help=('optional flag that triggers the default '
                              'blowup (or aging) logic built '
                              'into the Tax-Calculator that will age the '
                              'INPUT data from Records.PUF_YEAR to TAXYEAR. '
                              'No --blowup option implies INPUT data are '
                              'considered raw data that are not aged or '
                              'adjusted in any way.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--adjust',
                        help=('optional flag that triggers the default '
                              'adjustment logic built into the Tax-Calculator '
                              'that will adjust the distribution of income.'),
                        default=False,
                        action="store_true")

    parser.add_argument('--weights',
                        help=('optional flag that causes OUTPUT to have an '
                              'additional variable [29] containing the s006 '
                              'sample weight, which will be aged if the '
                              '--blowup option is used'),
                        default=False,
                        action="store_true")
    parser.add_argument('--fullcomp',
                        help=('optional flag that causes OUTPUT to have '
                              'marginal tax rates (MTRs) calculated with '
                              'respect to full compensation (but any '
                              'behavioral-response calculations always use '
                              'MTRs that are calculated with respect to full '
                              'compensation).  No --fullcomp option implies '
                              'MTRs reported in OUTPUT are not calculated '
                              'with respect to full compensation'),
                        default=False,
                        action="store_true")
    parser.add_argument('--ceeu',
                        help=('optional flag that causes normative welfare '
                              'statistics, including certainty-equivalent '
                              'expected-utility of after-tax income values '
                              'for different constant-relative-risk-aversion '
                              'parameter values, to be written to stdout.  '
                              'No --ceeu option implies nothing is written '
                              'to stdout.  Note that --reform  option must '
                              'be specified and aggregate combined taxes '
                              'under that reform must be same as under '
                              'current-law policy for this option to work'),
                        default=False,
                        action="store_true")
    output = parser.add_mutually_exclusive_group(required=False)
    output.add_argument('--records',
                        help=('optional flag that causes the output file to '
                              'be a CSV-formatted file containing for each '
                              'INPUT filing unit the TAXYEAR values of each '
                              'variable in the Records.USABLE_READ_VARS set. '
                              'If the --records option is specified, the '
                              'output file name will be the same as if the '
                              'option was not specified, except that the '
                              '".out-inctax" part is replaced by ".records"'),
                        default=False,
                        action="store_true")
    output.add_argument('--csvdump',
                        help=('optional flag that causes the output file to '
                              'be a CSV-formatted file containing for each '
                              'INPUT filing unit the TAXYEAR values of each '
                              'variable in the Records.USABLE_READ_VARS set '
                              'and in the Records.CALCULATED_VARS set. '
                              'If the --csvdump option is specified, the '
                              'output file name will be the same as if the '
                              'option was not specified, except that the '
                              '".out-inctax" part is replaced by ".csvdump"'),
                        default=False,
                        action="store_true")
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of required CSV file that '
                              'contains a subset of variables included in '
                              'the Records.USABLE_READ_VARS set. '
                              'INPUT must end in ".csv".'))
    parser.add_argument('TAXYEAR', nargs='?', default=0,
                        help=('TAXYEAR is calendar year for which federal '
                              'income taxes are computed (e.g., 2013).'),
                        type=int)
    args = parser.parse_args()
    # optionally show INPUT and OUTPUT variable definitions and exit
    if args.iohelp:
        IncomeTaxIO.show_iovar_definitions()
        return 0
    # check INPUT filename
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name;\n')
        sys.stderr.write('USAGE: python inctax.py --help\n')
        return 1
    # check TAXYEAR value
    if args.TAXYEAR == 0:
        sys.stderr.write('ERROR: must specify TAXYEAR >= 2013;\n')
        sys.stderr.write('USAGE: python inctax.py --help\n')
        return 1
    # check consistency of REFORM and ASSUMP options
    if args.assump and not args.reform:
        sys.stderr.write('ERROR: cannot specify ASSUMP without a REFORM\n')
        sys.stderr.write('USAGE: python inctax.py --help\n')
        return 1
    # instantiate IncometaxIO object and do federal income tax calculations
    inctax = IncomeTaxIO(input_data=args.INPUT,
                         tax_year=args.TAXYEAR,
                         reform=args.reform,
                         assump=args.assump,
                         exact_calculations=args.exact,
                         blowup_input_data=args.blowup,
                         adjust_input_data=args.adjust,
                         output_weights=args.weights,
                         output_records=args.records,
                         csv_dump=args.csvdump)
    if args.records:
        inctax.output_records(writing_output_file=True)
    elif args.csvdump:
        inctax.calculate(writing_output_file=False,
                         exact_output=args.exact,
                         output_weights=args.weights,
                         output_mtr_wrt_fullcomp=args.fullcomp,
                         output_ceeu=args.ceeu)
        inctax.csv_dump(writing_output_file=True)
    else:
        inctax.calculate(writing_output_file=True,
                         exact_output=args.exact,
                         output_weights=args.weights,
                         output_mtr_wrt_fullcomp=args.fullcomp,
                         output_ceeu=args.ceeu)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
