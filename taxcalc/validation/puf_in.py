"""
Tax-Calculator validation script that adds random positive amounts to each
positive dollar variable in the puf.csv input file, which must be located
in the top-level directory of the Tax-Calculator source code tree.
The resulting input file is xYY.csv, where YY denotes the tax year.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 puf_in.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy puf_in.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import sys
import os
import pandas as pd
import numpy as np
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Records  # pylint: disable=import-error

MAX_YEAR = 2023  # maximum tax year allowed for tax calculations
MAX_SEED = 999999999  # maximum allowed seed for random-number generator
MAX_SIZE = 100000  # maximum size of sample to draw from puf.csv

DROP_VARS = set(['e11070', 'e11550'])  # those slated for removal from puf.csv


def add_to_variables_and_sample(xdf, taxyear, rnseed, ssize):
    """
    DOCSTRING GOES HERE.
    """
    return 0


def main(taxyear, rnseed, ssize):
    """
    Contains the high-level logic of the script.
    """
    # read puf.csv file into a Pandas DataFrame
    pufcsv_filename = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
    if not os.path.isfile(pufcsv_filename):
        msg = 'ERROR: puf.csv file [{}] not found'.format(pufcsv_filename)
        sys.stderr.write(msg + '\n')
        return 1
    xdf = pd.read_csv(pufcsv_filename)

    # remove xdf variables scheduled for removal from VALID_READ_VARS set
    print xdf.shape
    for var in DROP_VARS:
        if var not in Records.VALID_READ_VARS:
            msg = 'ERROR: variable {} already dropped'.format(var)
            sys.stderr.write(msg + '\n')
            return 1
        xdf.drop(var, axis=1, inplace=True)
    print xdf.shape

    # add random amounts to dollar variable and sample xdf to get SSIZE
    rtncode = add_to_variables_and_sample(xdf, taxyear, rnseed, ssize)
    if rtncode != 0:
        return rtncode

    # write modified xdf to xYY.csv file
    xdf.to_csv('x{}.csv'.format(taxyear % 100), index=False)

    # normal return code
    return 0
# end of main function code


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python puf_in.py',
        description=('Adds random amounts to certain postive variables in '
                     'puf.csv input file and writes the randomized '
                     'CSV-formatted input file to xYY.csv file.'))
    PARSER.add_argument('YEAR', nargs='?', type=int, default=0,
                        help=('YEAR is tax year; '
                              'must be in [2013,{}] range.'.format(MAX_YEAR)))
    PARSER.add_argument('SEED', nargs='?', type=int, default=0,
                        help=('SEED is random-number seed; '
                              'must be in [1,{}] range.'.format(MAX_SEED)))
    PARSER.add_argument('SIZE', nargs='?', type=int, default=0,
                        help=('SIZE is sample size; '
                              'must be in [1,{}] range.'.format(MAX_SIZE)))
    ARGS = PARSER.parse_args()
    # check for invalid command-line parameter values
    ARGS_ERROR = False
    if ARGS.YEAR < 2013 or ARGS.YEAR > MAX_YEAR:
        RSTR = '[2013,{}] range'.format(MAX_YEAR)
        sys.stderr.write('ERROR: YEAR {} not in {}\n'.format(ARGS.YEAR, RSTR))
        ARGS_ERROR = True
    if ARGS.SEED < 1 or ARGS.SEED > MAX_SEED:
        RSTR = '[1,{}] range'.format(MAX_SEED)
        sys.stderr.write('ERROR: SEED {} not in {}\n'.format(ARGS.SEED, RSTR))
        ARGS_ERROR = True
    if ARGS.SIZE < 1 or ARGS.SIZE > MAX_SIZE:
        RSTR = '[1,{}] range'.format(MAX_SIZE)
        sys.stderr.write('ERROR: SIZE {} not in {}\n'.format(ARGS.SIZE, RSTR))
        ARGS_ERROR = True
    if ARGS_ERROR:
        sys.stderr.write('USAGE: python puf_in.py --help\n')
        RCODE = 1
    else:
        RCODE = main(ARGS.YEAR, ARGS.SEED, ARGS.SIZE)
    sys.exit(RCODE)
