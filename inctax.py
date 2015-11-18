"""
INCome tax input-output capabilities for TAX-calculator.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 inctax.py
# pylint --disable=locally-disabled inctax.py

import argparse
import sys
from taxcalc import IncomeTaxIO


def main():
    """
    Contains command-line interface to the Tax-Calculator IncomeTaxIO class.
    """
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        description=('Writes to a file the federal income tax OUTPUT for the '
                     'tax filing units specified in the INPUT file with the '
                     'OUTPUT computed from the INPUT for the TAXYEAR using '
                     'the Tax-Calculator. '
                     'The INPUT file is a CSV-formatted file that includes '
                     'a subset of IRS-SOI PUF variables. The OUTPUT file uses '
                     'Internet-TAXSIM format.  The OUTPUT filename is the '
                     'INPUT filename (excluding the .csv suffix) followed by '
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
                              'variable definitions and exit without trying '
                              'to read the INPUT file, so INPUT and TAXYEAR '
                              'can be any meaningless pair of character (as '
                              'long as the second character is a digit) '
                              '(e.g., "i 0" or "x 1" or ". 9")'),
                        default=False,
                        action="store_true")
    parser.add_argument('--reform',
                        help=('REFORM is name of optional file that contains '
                              'tax reform provisions; the provisions are '
                              'specified using JSON that may include '
                              '//-comments. No REFORM filename implies use '
                              'of current-law policy.'),
                        default=None)
    parser.add_argument('INPUT',
                        help=('INPUT is name of required CSV file that '
                              'contains a subset of IRS-SOI PUF variables.'))
    parser.add_argument('TAXYEAR',
                        help=('TAXYEAR is calendar year for which income '
                              'taxes are computed (e.g., 2013).'),
                        type=int)
    args = parser.parse_args()
    # optionally show INPUT and OUTPUT variable definitions and exit
    if args.iohelp:
        IncomeTaxIO.show_iovar_definitions()
        return 0
    # instantiate IncometaxIO object and do tax calculations
    inctax = IncomeTaxIO(input_filename=args.INPUT,
                         tax_year=args.TAXYEAR,
                         reform_filename=args.reform)
    inctax.calculate()
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
