"""
Tax-Calculator validation script that adds random amounts to some
variables in the puf.csv input file, which must be located in the
top-level directory of the Tax-Calculator source code tree.
The resulting input file is xYY.csv, where YY denotes the tax year.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 csv_in.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy csv_in.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import sys
import os
import pandas as pd
import numpy as np
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Records  # pylint: disable=import-error

# specify maximum allowed values for command-line parameters
MAX_YEAR = 2023  # maximum tax year allowed for tax calculations
MAX_SEED = 999999999  # maximum allowed seed for random-number generator
MAX_SIZE = 100000  # maximum size of sample to draw from puf.csv

# specify set of variables slated for removal from puf.csv
DROP1_VARS = set(['e11070', 'e11550'])

# specify set of variables not included in the xYY.csv file
DROP2_VARS = set(['s006', 'filer', 'cmbtp_standard', 'cmbtp_itemizer'])

DROP_VARS = DROP1_VARS | DROP2_VARS

# specify set of variables whose value is to not be randomized
SKIP_VARS = set(['RECID', 'MARS', 'FLPDYR',
                 'age_head', 'age_spouse',
                 'DSI', 'EIC', 'FDED',
                 'f2441', 'f6251',
                 'MIDR',
                 'n24', 'XTOT'])
"""
iMac2:validation mrh$ ~/work/OSPC/csvvars x15.csv
1 age_head
2 age_spouse
3 DSI
4 EIC
5 FDED
6 FLPDYR
7 f2441
8 f6251
9 MARS
10 MIDR
11 n24
12 XTOT
13 e00200
14 e00300
15 e00400
16 e00600
17 e00650
18 e00700
19 e00800
20 e00900
21 e01100
22 e01200
23 e01400
24 e01500
25 e01700
26 e02000
27 e02100
28 e02300
29 e02400
30 e03150
31 e03210
32 e03220
33 e03230
34 e03270
35 e03240
36 e03290
37 e03300
38 e03400
39 e03500
40 e07240
41 e07260
42 e07300
43 e07400
44 e07600
45 p08000
46 e09700
47 e09800
48 e09900
49 e11200
50 e11580
51 e17500
52 e18400
53 e18500
54 e19200
55 e19800
56 e20100
57 e20400
58 e20500
59 p22250
60 p23250
61 e24515
62 e24518
63 p25470
64 e26270
65 e27200
66 e32800
67 e58990
68 e62900
69 p87482
70 p87521
71 e87530
72 RECID
73 s006
74 filer
75 cmbtp_standard
76 cmbtp_itemizer
77 e00200p
78 e00200s
79 e00900p
80 e00900s
81 e02100p
82 e02100s
"""


def randomize_data(xdf, taxyear, rnseed):
    """
    Function randomizes data variables.

    Parameters
    ----------
    xdf: Pandas DataFrame
        contains data to be randomized.

    taxyear: integer
        specifies year for which data is to be randomized.

    rnseed: integer
        specifies random-number seed to use in the randomization.

    Returns
    -------
    return_code: integer
        where zero indicates success and nonzero indicates an error.
    """
    xdf['FLPDYR'] = taxyear
    np.random.seed(rnseed)
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

    # remove xdf variables slated for removal from VALID_READ_VARS set
    print xdf.shape
    for var in DROP_VARS:
        if var not in Records.VALID_READ_VARS:
            msg = 'ERROR: variable {} already dropped'.format(var)
            sys.stderr.write(msg + '\n')
            return 1
        xdf.drop(var, axis=1, inplace=True)
    print xdf.shape

    # add random amounts to xdf variables
    rtncode = randomize_data(xdf, taxyear, rnseed)
    if rtncode != 0:
        return rtncode

    # sample xdf without replacement to get ssize observations
    xxdf = xdf.sample(n=ssize, random_state=rnseed)
    xxdf['RECID'] = [rid + 1 for rid in range(ssize)]

    # write modified xdf to xYY.csv file
    xxdf.to_csv('x{}.csv'.format(taxyear % 100), index=False)

    # normal return code
    return 0
# end of main function code


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python csv_in.py',
        description=('Adds random amounts to certain variables in '
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
        sys.stderr.write('USAGE: python csv_in.py --help\n')
        RCODE = 1
    else:
        RCODE = main(ARGS.YEAR, ARGS.SEED, ARGS.SIZE)
    sys.exit(RCODE)
