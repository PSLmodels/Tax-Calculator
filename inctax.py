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
                     'variable names that are a subset of the '
                     'Records.VALID_READ_VARS set.  The OUTPUT file is in '
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
                              'tax reform provisions; the provisions are '
                              'specified using JSON that may include '
                              '//-comments. No REFORM filename implies use '
                              'of current-law policy.'),
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
                              'imputation and blowup (or aging) logic built '
                              'into the Tax-Calculator that will age the '
                              'INPUT data from Records.PUF_YEAR to TAXYEAR. '
                              'No --blowup option implies INPUT data are '
                              'considered raw data that are not aged or '
                              'adjusted in any way.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--weights',
                        help=('optional flag that causes OUTPUT to have an '
                              'additional variable [29] containing the s006 '
                              'sample weight, which will be aged if the '
                              '--blowup option is used'),
                        default=False,
                        action="store_true")
    output = parser.add_mutually_exclusive_group(required=False)
    output.add_argument('--records',
                        help=('optional flag that causes the output file to '
                              'be a CSV-formatted file containing for each '
                              'INPUT filing unit the TAXYEAR values of each '
                              'variable in the Records.VALID_READ_VARS set. '
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
                              'variable in the Records.VALID_READ_VARS set '
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
                              'the Records.VALID_READ_VARS set. '
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
    # instantiate IncometaxIO object and do federal income tax calculations
    inctax = IncomeTaxIO(input_data=args.INPUT,
                         tax_year=args.TAXYEAR,
                         policy_reform=args.reform,
                         exact_calculations=args.exact,
                         blowup_input_data=args.blowup,
                         output_weights=args.weights,
                         output_records=args.records,
                         csv_dump=args.csvdump)
    if args.records:
        inctax.output_records(writing_output_file=True)
    elif args.csvdump:
        inctax.csv_dump(writing_output_file=True)
    else:
        inctax.calculate(writing_output_file=True, exact_output=args.exact,
                         output_weights=args.weights)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
