"""
SIMple input-output capabilities for TAX-calculator.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 simtax.py
# pylint --disable=locally-disabled simtax.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import sys
from taxcalc import SimpleTaxIO


def main():
    """
    Contains command-line interface to the Tax-Calculator SimpleTaxIO class.
    """
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        prog='python simtax.py',
        description=('Writes to a file the federal tax OUTPUT for the tax '
                     'filing units specified in the INPUT file with the '
                     'OUTPUT computed from the INPUT using the Tax-Calculator.'
                     ' Both the INPUT and OUTPUT files use Internet-TAXSIM '
                     'format.  The OUTPUT filename is the INPUT filename '
                     'with the ".out-simtax" string appended if no --reform '
                     'option is specified; otherwise the OUTPUT filename is '
                     'the INPUT filename with the ".out-simtax-REFORM" string '
                     'appended (excluding any ".json" ending to the REFORM '
                     'filename).  The OUTPUT file contains the first 28 '
                     'Internet-TAXSIM output variables.  Use --iohelp flag '
                     'for more information.  For details on Internet-TAXSIM '
                     'version 9.3 INPUT and OUTPUT formats, go to '
                     'http://users.nber.org/~taxsim/taxsim-calc9/'))
    parser.add_argument('--iohelp',
                        help=('optional flag to show INPUT and OUTPUT '
                              'variable definitions and exit'),
                        default=False,
                        action="store_true")
    parser.add_argument('--reform',
                        help=('REFORM is name of optional file that contains '
                              'tax reform "policy" parameters (any "behavior" '
                              'or "growth" parameters are ignored); the '
                              'REFORM file is specified using JSON that may '
                              'include //-comments. No --reform implies use '
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
    parser.add_argument('--taxsim2441',
                        help=('optional flag to emulate the Internet-TAXSIM '
                              'practice of approximating the number of '
                              'children eligible for the child care expense '
                              'credit on Form 2441 by the total number of '
                              'dependents of any age.  The default practice '
                              'is to approximate with the number of '
                              'dependents under age 17.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--records',
                        help=('optional flag that causes the output file to '
                              'be a CSV-formatted file containing for each '
                              'INPUT filing unit the TAXYEAR values of each '
                              'variable in the Records.USABLE_READ_VARS set. '
                              'If the --records option is specified, the '
                              'output file name will be the same as if the '
                              'option was not specified, except that the '
                              '".out-simtax" part is replaced by ".records"'),
                        default=False,
                        action="store_true")
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of required file that contains '
                              'tax-filing-unit information in Internet-TAXSIM '
                              'format.'))
    args = parser.parse_args()
    # optionally show INPUT and OUTPUT variable definitions and exit
    if args.iohelp:
        SimpleTaxIO.show_iovar_definitions()
        return 0
    # check INPUT filename
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name;\n')
        sys.stderr.write('USAGE: python simtax.py --help\n')
        return 1
    # instantiate SimpleTaxIO object and do tax calculations
    simtax = SimpleTaxIO(input_filename=args.INPUT,
                         reform=args.reform,
                         exact_calculations=args.exact,
                         emulate_taxsim_2441_logic=args.taxsim2441,
                         output_records=args.records)
    simtax.calculate(writing_output_file=True, exact_output=args.exact)
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
