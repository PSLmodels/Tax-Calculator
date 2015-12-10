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
                              'variable definitions and exit without trying '
                              'to read the INPUT file, so INPUT can be any '
                              'meaningless character (e.g., x or ?'),
                        default=False,
                        action="store_true")
    parser.add_argument('--reform',
                        help=('REFORM is name of optional file that contains '
                              'tax reform provisions; the provisions are '
                              'specified using JSON that may include '
                              '//-comments. No REFORM filename implies use '
                              'of current-law policy.'),
                        default=None)
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
    parser.add_argument('INPUT',
                        help=('INPUT is name of required file that contains '
                              'tax-filing-unit information in Internet-TAXSIM '
                              'format.'))
    args = parser.parse_args()
    # optionally show INPUT and OUTPUT variable definitions and exit
    if args.iohelp:
        SimpleTaxIO.show_iovar_definitions()
        return 0
    # instantiate SimpleTaxIO object and do tax calculations
    simtax = SimpleTaxIO(input_filename=args.INPUT,
                         reform_filename=args.reform,
                         emulate_taxsim_2441_logic=args.taxsim2441)
    simtax.calculate()
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
