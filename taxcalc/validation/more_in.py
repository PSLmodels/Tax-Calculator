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


MAX_VARSET = 1


def add_vars(input_filename, varset_id):
    """
    Adds extra input variables indicated by varset_id value to the specified
    input file and writes augmented CSV-formatted input file to stdout.
    """
    # read CSV-formatted input file into a DataFrame
    idf = pd.read_csv(input_filename)
    # add extra variables to idf DataFrame as indicated by value of varset_id
    if varset_id == 1:
        rcode = add_varset_1(idf)
    # elif varset_id == 2:
    #    rcode = add_varset_2(idf)
    if rcode != 0:
        return rcode
    # write augmented idf DataFrame to a CSV string and write string to stdout
    csv_str = idf.to_csv(index=False)
    sys.stdout.write('{}'.format(csv_str))
    return 0


def add_varset_1(idf):
    """
    Add to idf DataFrame variables in VARSET 1:
    e00900, e00900p, e00900s (Schedule C self-employment income)
    [farm income (e02100, e02100p, e02100s) is equivalent to SchC income]
    ... add more variables ...
    """
    nobs = len(idf['RECID'])
    rints_p = np.random.random_integers(-1, 2, nobs) * 70000
    rints_s = np.random.random_integers(-1, 2, nobs) * 70000
    idf['e00900'] = pd.Series(rints_p + rints_s)
    idf['e00900p'] = pd.Series(rints_p)
    idf['e00900s'] = pd.Series(rints_s)
    # ... add more variables ...
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
    parser.add_argument('VARSET', nargs='?', type=int, default=0,
                        help=('VARSET is the integer number of the set of '
                              'additional input variables that will be added '
                              'to the INPUT file; must be greater than zero.'))
    args = parser.parse_args()
    # check for invalid command-line parameters
    args_error = False
    if args.INPUT == '' or not os.path.isfile(args.INPUT):
        errmsg = 'INPUT file "{}" could not be found'.format(args.INPUT)
        sys.stderr.write('ERROR: {}\n'.format(errmsg))
        args_error = True
    if args.VARSET < 1 or args.VARSET > MAX_VARSET:
        rangestr = '[1,{}] range'.format(MAX_VARSET)
        sys.stderr.write('ERROR: VARSET {} not in {}\n'.format(args.VARSET,
                                                               rangestr))
        args_error = True
    if args_error:
        sys.stderr.write('USAGE: python more_in.py --help\n')
        return 1
    # specify random-number seed
    np.random.seed(12345)
    # call add_vars() function
    rcode = add_vars(input_filename=args.INPUT, varset_id=args.VARSET)
    # return rcode as exit code
    return rcode
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
