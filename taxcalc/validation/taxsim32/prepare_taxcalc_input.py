"""
Translates TAXSIM-32 input file to Tax-Calculator tc input file.
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
        description=('Translates TAXSIM-32 input file into a Tax-Calculator '
                     'CSV-formatted tc input file. '
                     'Any pre-existing OUTPUT file contents are overwritten. '
                     'For details on Internet TAXSIM version 32 INPUT '
                     'format, go to '
                     'https://users.nber.org/~taxsim/taxsim32/'))
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of file that contains '
                              'TAXSIM-32 input.'))
    parser.add_argument('OUTPUT', nargs='?', default='',
                        help=('OUTPUT is name of file that will contain '
                              'CSV-formatted Tax-Calculator tc input.'))
    args = parser.parse_args()
    # check INPUT filename
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name\n')
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
        return 1
    if not os.path.isfile(args.INPUT):
        emsg = 'INPUT file named {} does not exist'.format(args.INPUT)
        sys.stderr.write('ERROR: {}\n'.format(emsg))
        return 1
    # check OUTPUT filename
    if args.OUTPUT == '':
        sys.stderr.write('ERROR: must specify OUTPUT file name\n')
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
        return 1
    if os.path.isfile(args.OUTPUT):
        os.remove(args.OUTPUT)
    # read TAXSIM-32 INPUT file into a pandas DataFrame
    ivar = pd.read_csv(args.INPUT, delim_whitespace=True,
                       header=0, index_col=False, names=range(1, 33))
    # Drop 'idtl' – used to generate detailed output
    ivar.drop(columns=32)
    # translate INPUT variables into OUTPUT variables
    invar = translate(ivar)
    # write OUTPUT file containing Tax-Calculator input variables
    invar.to_csv(args.OUTPUT, index=False)
    # return no-error exit code
    return 0
# end of main function code


def translate(ivar):
    """
    Translate TAXSIM-32 input variables into Tax-Calculator input variables.
    Both ivar and returned invar are pandas DataFrame objects.
    """
    assert isinstance(ivar, pd.DataFrame)
    invar = pd.DataFrame()
    invar['RECID'] = ivar.loc[:, 1]
    invar['FLPDYR'] = ivar.loc[:, 2]
    # no Tax-Calculator use of TAXSIM variable 3, state code
    mstat = ivar.loc[:, 4]
    assert np.all(np.logical_or(mstat == 1, mstat == 2))
    invar['age_head'] = ivar.loc[:, 5]
    invar['age_spouse'] = ivar.loc[:, 6]
    num_deps = ivar.loc[:, 7]
    mars = np.where(mstat == 1, np.where(num_deps > 0, 4, 1), 2)
    assert np.all(np.logical_or(mars == 1,
                                np.logical_or(mars == 2, mars == 4)))
    invar['MARS'] = mars
    invar['f2441'] = ivar.loc[:, 8]
    invar['n24'] = ivar.loc[:, 9]
    num_eitc_qualified_kids = ivar.loc[:, 10]
    invar['EIC'] = np.minimum(num_eitc_qualified_kids, 3)
    num_taxpayers = np.where(mars == 2, 2, 1)
    invar['XTOT'] = num_taxpayers + num_deps
    invar['e00200p'] = ivar.loc[:, 11]
    invar['e00200s'] = ivar.loc[:, 12]
    invar['e00200'] = invar['e00200p'] + invar['e00200s']
    invar['e00650'] = ivar.loc[:, 13]
    invar['e00600'] = invar['e00650']
    invar['e00300'] = ivar.loc[:, 14]
    invar['p22250'] = ivar.loc[:, 15]
    invar['p23250'] = ivar.loc[:, 16]
    invar['e02000'] = ivar.loc[:, 17]
    invar['e00800'] = ivar.loc[:, 18]
    invar['e01700'] = ivar.loc[:, 19]
    invar['e01500'] = invar['e01700']
    invar['e02400'] = ivar.loc[:, 20]
    invar['e02300'] = ivar.loc[:, 21]
    # no Tax-Calculator use of TAXSIM variable 22, non-taxable transfers
    # no Tax-Calculator use of TAXSIM variable 23, rent paid
    invar['e18500'] = ivar.loc[:, 24]
    invar['e18400'] = ivar.loc[:, 25]
    invar['e32800'] = ivar.loc[:, 26]
    invar['e19200'] = ivar.loc[:, 27]
    invar['e26270'] = ivar.loc[:, 28]
    invar['e00900p'] = ivar.loc[:, 29]
    invar['e00900s'] = ivar.loc[:, 31]
    invar['e00900'] = invar['e00900p'] + invar['e00900s']

    pprofinc = ivar.loc[:, 30]
    sprofinc = ivar.loc[:, 32]

    invar['PT_SSTB_income'] = np.where(pprofinc + sprofinc > 0, 1, 0)
    invar['PT_SSTB_income'] = np.where(invar['e26270'] > 0, 1, invar['PT_SSTB_income'])

    return invar


if __name__ == '__main__':
    sys.exit(main())
