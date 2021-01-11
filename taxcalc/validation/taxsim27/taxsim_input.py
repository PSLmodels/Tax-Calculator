"""
Generates random sample of tax filing units with attributes such that
generated file can be directly uploaded to Internet TAXSIM version 27.
"""
# CODING-STYLE CHECKS:
# pycodestyle taxsim_input.py
# pylint --disable=locally-disabled taxsim_input.py

import argparse
import sys
import numpy as np
import pandas as pd


VALID_LETTERS = ['a', 'b', 'c']


def main():
    """
    High-level logic.
    """
    # parse command-line arguments:
    usage_str = 'python taxsim_input.py YEAR LETTER [OFFSET] [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Generates random sample of tax filing units with '
                     'attributes and format such that the file can be '
                     'directly uploaded to Internet TAXSIM version 27. '
                     'For details on Internet TAXSIM version 27 INPUT '
                     'format, go to '
                     'https://users.nber.org/~taxsim/taxsim27/'))
    parser.add_argument('YEAR', nargs='?', type=int, default=0,
                        help=('YEAR specifies calendar year assumed in '
                              'generated input data.'))
    parser.add_argument('LETTER', nargs='?', default='',
                        help=('LETTER specifies assumption set '
                              'used to generate input data.'))
    parser.add_argument('OFFSET', nargs='?', type=int, default=0,
                        help=('optional OFFSET alters the '
                              'random-number seed used to generate '
                              'sample of filing units.  Default OFFSET '
                              'value is zero.'))
    args = parser.parse_args()
    # check YEAR value
    if args.YEAR < 2011 or args.YEAR > 2023:
        sys.stderr.write('ERROR: YEAR not in [2011,2023] range\n')
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
        return 1
    # check LETTER value
    if args.LETTER == '':
        sys.stderr.write('ERROR: must specify LETTER\n')
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
        return 1
    if args.LETTER not in VALID_LETTERS:
        sys.stderr.write('ERROR: LETTER not in VALID_LETTERS, where\n')
        sys.stderr.write('       VALID_LETTERS={}\n'.format(VALID_LETTERS))
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
    # check OFFSET value
    if args.OFFSET < 0 or args.OFFSET > 999:
        sys.stderr.write('ERROR: OFFSET not in [0,999] range\n')
        sys.stderr.write('USAGE: {}\n'.format(usage_str))
        return 1
    # get dictionary containing assumption set
    assump = assumption_set(args.YEAR, args.LETTER)
    # generate sample as pandas DataFrame
    sample = sample_dataframe(assump, args.YEAR, args.OFFSET)
    # write sample to input file
    filename = '{}{}.in'.format(args.LETTER, args.YEAR % 100)
    sample.to_csv(filename, sep=' ', header=False, index=False)
    # return no-error exit code
    return 0
# end of main function code


def assumption_set(year, letter):
    """
    Return dictionary containing assumption parameters.
    """
    adict = dict()
    if letter in VALID_LETTERS:  # <===========================================
        # basic assumption parameters for all ?YY.in samples:
        adict['sample_size'] = 100000
        adict['year'] = year  # TAXSIM ivar 2
        # demographic attributes:
        adict['joint_frac'] = 0.60  # fraction of sample with joint MARS
        adict['min_age'] = 17  # TAXSIM ivar 5 (primary taxpayer age)
        adict['max_age'] = 77  # TAXSIM ivar 5 (primary taxpayer age)
        adict['min_age_diff'] = -10  # min spouse age difference
        adict['max_age_diff'] = 10  # max spouse age difference
        adict['max_depx'] = 5  # TAXSIM ivar 7 (total number of dependents)
        adict['max_dep13'] = 4  # TAXSIM ivar 8 (Child/Dependent Care Credit)
        adict['max_dep17'] = 4  # TAXSIM ivar 9 (Child Credit)
        adict['max_dep18'] = 4  # TAXSIM ivar 10 (EITC)
        # labor income:
        adict['max_pwages_yng'] = 500  # TAXSIM ivar 11
        adict['max_pwages_old'] = 30  # TAXSIM ivar 11 (65+ ==> old)
        adict['max_swages_yng'] = 500  # TAXSIM ivar 12
        adict['max_swages_old'] = 30  # TAXSIM ivar 12 (65+ ==> old)
        # non-labor income (all zeros):
        adict['max_divinc'] = 0  # TAXSIM ivar 13
        adict['max_intinc'] = 0  # TAXSIM ivar 14
        adict['min_stcg'] = 0  # TAXSIM ivar 15
        adict['max_stcg'] = 0  # TAXSIM ivar 15
        adict['min_ltcg'] = 0  # TAXSIM ivar 16
        adict['max_ltcg'] = 0  # TAXSIM ivar 16
        adict['max_other_prop_inc'] = 0  # TAXSIM ivar 17
        adict['max_other_nonprop_inc'] = 0  # TAXSIM ivar 18
        adict['max_pnben'] = 0  # TAXSIM ivar 19
        adict['max_ssben'] = 0  # TAXSIM ivar 20
        adict['max_uiben'] = 0  # TAXSIM ivar 21
        # childcare expense amount (all zero):
        adict['max_ccexp'] = 0  # TAXSIM ivar 26
        # itemized expense amounts (all zero):
        adict['max_ided_proptax'] = 0  # TAXSIM ivar 24
        adict['max_ided_nopref'] = 0  # TAXSIM ivar 25
        adict['max_ided_mortgage'] = 0  # TAXSIM ivar 27
        # end if letter in VALID_LETTERS
    if letter in ['b', 'c']:  # <==============================================
        # non-labor income:
        adict['max_divinc'] = 20  # TAXSIM ivar 13
        adict['max_intinc'] = 20  # TAXSIM ivar 14
        adict['min_stcg'] = -10  # TAXSIM ivar 15
        adict['max_stcg'] = 10  # TAXSIM ivar 15
        adict['min_ltcg'] = -10  # TAXSIM ivar 16
        adict['max_ltcg'] = 10  # TAXSIM ivar 16
        adict['max_other_prop_inc'] = 30  # TAXSIM ivar 17
        adict['max_other_nonprop_inc'] = 30  # TAXSIM ivar 18
        adict['max_pnben'] = 60  # TAXSIM ivar 19
        adict['max_ssben'] = 60  # TAXSIM ivar 20
        adict['max_uiben'] = 10  # TAXSIM ivar 21
    if letter == 'c':  # <=====================================================
        # childcare expense amount:
        adict['max_ccexp'] = 10  # TAXSIM ivar 26
        # itemized expense amounts:
        adict['max_ided_proptax'] = 30  # TAXSIM ivar 24
        adict['max_ided_nopref'] = 10  # TAXSIM ivar 25
        adict['max_ided_mortgage'] = 40  # TAXSIM ivar 27
    return adict


def sample_dataframe(assump, year, offset):
    """
    Construct DataFrame containing sample specified by assump and year+offset.
    """
    # pylint: disable=too-many-locals
    np.random.seed(123456789 + year + offset)
    size = assump['sample_size']
    zero = np.zeros(size, dtype=np.int64)
    sdict = dict()
    # (01) RECID
    sdict[1] = range(1, size + 1)
    # (02) YEAR
    sdict[2] = np.full_like(zero, assump['year'], dtype=np.int64)
    # (03) STATE
    sdict[3] = zero
    # (04) MSTAT
    urn = np.random.random(size)
    mstat = np.where(urn < assump['joint_frac'], 2, 1)
    sdict[4] = mstat
    # (05) PAGE
    sdict[5] = np.random.randint(assump['min_age'],
                                 assump['max_age']+1,
                                 size)
    # (06) SAGE
    age_diff = np.random.randint(assump['min_age_diff'],
                                 assump['max_age_diff']+1,
                                 size)
    sage = sdict[5] + age_diff
    sdict[6] = np.where(mstat == 2, np.maximum(sage, assump['min_age']), zero)
    # (07-10) DEPX, DEP13, DEP17, DEP18
    depx = np.random.randint(0, assump['max_depx']+1, size)
    d18 = np.random.randint(0, assump['max_dep18']+1, size)
    dep18 = np.where(d18 <= depx, d18, depx)
    d17 = np.random.randint(0, assump['max_dep17']+1, size)
    dep17 = np.where(d17 <= dep18, d17, dep18)
    d13 = np.random.randint(0, assump['max_dep13']+1, size)
    dep13 = np.where(d13 <= dep17, d13, dep17)
    sdict[7] = depx
    sdict[8] = dep13
    sdict[9] = dep17
    sdict[10] = dep18
    # (11) PWAGES
    pwages_yng = np.random.randint(0, assump['max_pwages_yng']+1, size)
    pwages_old = np.random.randint(0, assump['max_pwages_old']+1, size)
    sdict[11] = np.where(sdict[5] >= 65, pwages_old, pwages_yng) * 1000
    # (12) SWAGES
    swages_yng = np.random.randint(0, assump['max_swages_yng']+1, size)
    swages_old = np.random.randint(0, assump['max_swages_old']+1, size)
    swages = np.where(sdict[6] >= 65, swages_old, swages_yng) * 1000
    sdict[12] = np.where(mstat == 2, swages, zero)
    # (13) DIVIDENDS
    sdict[13] = np.random.randint(0, assump['max_divinc']+1, size) * 1000
    # (14) INTREC
    sdict[14] = np.random.randint(0, assump['max_intinc']+1, size) * 1000
    # (15) STCG
    sdict[15] = np.random.randint(assump['min_stcg'],
                                  assump['max_stcg']+1,
                                  size) * 1000
    # (16) LTCG
    sdict[16] = np.random.randint(assump['min_ltcg'],
                                  assump['max_ltcg']+1,
                                  size) * 1000
    # (17) OTHERPROP
    sdict[17] = np.random.randint(0,
                                  assump['max_other_prop_inc']+1,
                                  size) * 1000
    # (18) NONPROP
    sdict[18] = np.random.randint(0,
                                  assump['max_other_nonprop_inc']+1,
                                  size) * 1000
    # (19) PENSIONS
    sdict[19] = np.random.randint(0, assump['max_pnben']+1, size) * 1000
    # (20) GSSI
    sdict[20] = np.random.randint(0, assump['max_ssben']+1, size) * 1000
    # (21) UI
    sdict[21] = np.random.randint(0, assump['max_uiben']+1, size) * 1000
    # (22) TRANSFERS (non-taxable in federal income tax)
    sdict[22] = zero
    # (23) RENTPAID (used only in some state income tax laws)
    sdict[23] = zero
    # (24) PROPTAX
    sdict[24] = np.random.randint(0,
                                  assump['max_ided_proptax']+1,
                                  size) * 1000
    # (25) OTHERITEM
    sdict[25] = np.random.randint(0,
                                  assump['max_ided_nopref']+1,
                                  size) * 1000
    # (26) CHILDCARE (TAXSIM-27 EXPECTS ZERO IF NO QUALIFYING CHILDRED)
    ccexp = np.random.randint(0, assump['max_ccexp']+1, size) * 1000
    sdict[26] = np.where(dep13 > 0, ccexp, zero)
    # (27) MORTGAGE
    sdict[27] = np.random.randint(0,
                                  assump['max_ided_mortgage']+1,
                                  size) * 1000
    smpl = pd.DataFrame(sdict)
    return smpl


if __name__ == '__main__':
    sys.exit(main())
