"""
Translates TAXSIM22 (Internet-TAXSIM 9.3) input file to tc input file.
"""
# CODING-STYLE CHECKS:
# pycodestyle prepare_tc_input.py
# pylint --disable=locally-disabled prepare_tc_input.py

import argparse
import os
import sys
import numpy as np
import pandas as pd


def main():
    """
    High-level logic.
    """
    # parse command-line arguments:
    usage_str = 'python prepare_tc_input.py INPUT OUTPUT [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Translates TAXSIM22 (Internet-TAXSIM 9.3) input file '
                     'into a Tax-Calculator CSC-formatted tc input file. '
                     'Any pre-existing OUTPUT file contents are overwritten. '
                     'For details on Internet-TAXSIM version 9.3 INPUT '
                     'format, go to '
                     'http://users.nber.org/~taxsim/taxsim-calc9/'))
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of file that contains '
                              'TAXSIM22 input.'))
    parser.add_argument('OUTPUT', nargs='?', default='',
                        help=('OUTPUT is name of file that will contain '
                              'CSV-formatted Tax-Calculator tc input.'))
    args = parser.parse_args()
    # check INPUT filename
    sname = 'prepare_tc_input.out.py'
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name\n')
        sys.stderr.write('USAGE: python {} --help\n'.format(sname))
        return 1
    if not os.path.isfile(args.INPUT):
        emsg = 'INPUT file named {} does not exist'.format(args.INPUT)
        sys.stderr.write('ERROR: {}\n'.format(emsg))
        return 1
    # check OUTPUT filename
    if args.OUTPUT == '':
        sys.stderr.write('ERROR: must specify OUTPUT file name\n')
        sys.stderr.write('USAGE: python {} --help\n'.format(sname))
        return 1
    if os.path.isfile(args.OUTPUT):
        os.remove(args.OUTPUT)
    # read TAXSIM22 INPUT file into a pandas DataFrame
    ivar = pd.read_csv(args.INPUT, delim_whitespace=True,
                       header=None, names=range(1, 23))
    # translate INPUT variables into OUTPUT variables
    invar = translate(ivar)
    # write OUTPUT file containing Tax-Calculator input variables
    invar.to_csv(args.OUTPUT, index=False)
    # return no-error exit code
    return 0
# end of main function code


def translate(ivar):
    """
    Translate TAXSIM22 input variables into Tax-Calculator input variables.
    Both ivar and returned invar are pandas DataFrame objects.
    """
    assert isinstance(ivar, pd.DataFrame)
    invar = pd.DataFrame()
    invar['RECID'] = ivar.loc[:, 1]
    invar['FLPDYR'] = ivar.loc[:, 2]
    # no use of TAXSIM variable 3, state code
    mars = ivar.loc[:, 4]
    invar['MARS'] = np.where(mars == 3, 4, np.where(mars == 2, 2, 1))
    num_taxpayers = np.where(mars == 3, 1, np.where(mars == 2, 2, 1))
    num_dependents = ivar.loc[:, 5]
    num_eitc_qualified_kids = num_dependents  # simplifying assumption
    invar['EIC'] = np.minimum(num_eitc_qualified_kids, 3)
    total_num_exemptions = num_taxpayers + num_dependents
    invar['XTOT'] = total_num_exemptions
    ages = ivar.loc[:, 6]
    assert np.all(ages >= 3)
    # using new coding of TAXSIM22 input variable 6
    invar['age_head'] = np.floor_divide(ages, 100)  # like Python //
    invar['age_spouse'] = np.remainder(ages, 100)  # like Python %
    invar['e00200p'] = ivar.loc[:, 7]
    invar['e00200s'] = ivar.loc[:, 8]
    invar['e00200'] = invar['e00200p'] + invar['e00200s']
    invar['e00650'] = ivar.loc[:, 9]  # qualified dividend income
    invar['e00600'] = invar['e00650']
    invar['e00300'] = ivar.loc[:, 10]
    invar['e01500'] = ivar.loc[:, 11]  # total pension/annuity income
    invar['e01700'] = invar['e01500']  # all pension/annuity income is taxable
    invar['e02400'] = ivar.loc[:, 12]
    invar['e00400'] = ivar.loc[:, 13]
    # no use of TAXSIM variable 14 because no state income tax calculations
    invar['e18500'] = ivar.loc[:, 15]
    invar['e18400'] = ivar.loc[:, 16]
    invar['e32800'] = ivar.loc[:, 17]
    invar['e02300'] = ivar.loc[:, 18]
    invar['n24'] = ivar.loc[:, 19]  # number dependents under age 17
    # approximate number of Form 2441 qualified persons associated with
    # the child care expenses specified by variable 17. (Note that the exact
    # number is the number of dependents under age 13, but that is not
    # an Internet-TAXSIM input variable; hence the need to approximate.)
    invar['f2441'] = num_dependents  # TODO  OR: = invar['n24'] ???
    invar['e19200'] = ivar.loc[:, 20]
    invar['p22250'] = ivar.loc[:, 21]
    invar['p23250'] = ivar.loc[:, 22]
    return invar


if __name__ == '__main__':
    sys.exit(main())
