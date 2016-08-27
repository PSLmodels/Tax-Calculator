"""
Tax-Calculator validation script that adds more variables to a specified
CSV-formatted inctax.py input file and writes the augmented CSV-formatted
input file to stdout.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 more_in.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy more_in.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import sys
import os
import pandas as pd
import numpy as np


def add_vars(input_filename):
    """
    Adds extra input variables to specified input file and
    writes augmented input file to stdout.
    """
    # read input file into a DataFrame
    if not os.path.isfile(input_filename):
        msg = 'INPUT file named {} could not be found'.format(input_filename)
        sys.stderr.write('ERROR: {}\n'.format(msg))
        return 1
    idf = pd.read_csv(input_filename)
    # add extra variables to idf DataFrame
    # ...
    # write augmented idf DataFrame to a CSV string and write string to stdout
    csv_str = idf.to_csv(index=False)
    sys.stdout.write('{}'.format(csv_str))
    return 0


def main():
    """
    Reads command-line arguments and calls add_vars() function.
    """
    # parse command-line arguments:
    parser = argparse.ArgumentParser(
        prog='python more_in.py',
        description=('Adds more variables to a specified CSV-formatted '
                     'inctax.py input file and writes the augmented '
                     'CSV-formatted input file to stdout.'))
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of input file that is going to '
                              'be augmented; the file must be in CSV format.'))
    args = parser.parse_args()
    # check INPUT filename
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name\n')
        sys.stderr.write('USAGE: python more_in.py --help\n')
        return 1
    # instantiate SimpleTaxIO object and do tax calculations
    rcode = add_vars(input_filename=args.INPUT)
    # return rcode as exit code
    return rcode
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
