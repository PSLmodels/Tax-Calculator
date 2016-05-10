"""
Script that transforms puf.csv file into a CSV-formatted file suitable
for input into the TAXCALC SAS program.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 pufprep.py
# pylint --disable=locally-disabled pufprep.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import sys
import argparse
import pandas as pd


def main(infilename, outfilename):
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into a Pandas DataFrame
    vardf = pd.read_csv(infilename)

    # modify vardf in several ways to account for logic
    # differences between Tax-Calculator and taxcalc.sas
    # (a) zero out self-employment income (SEY) and FICA taxes on SEY:
    vardf['e00900'] = 0
    vardf['e02100'] = 0
    vardf['e09400'] = 0
    vardf['e03260'] = 0

    # write vardf to OUTPUT file
    vardf.to_csv(outfilename, index=False)

    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        prog='python pufprep.py',
        description=('Reads CSV-formatted INPUT file and writes a '
                     'modified CSV-formatted OUTPUT file.'))
    PARSER.add_argument('INPUT',
                        help=('INPUT is name of required file that contains '
                              'CSV-formatted Tax-Calculator input variables.'))
    PARSER.add_argument('OUTPUT',
                        help=('OUTPUT is name of required file that contains '
                              'CSV-formatted variables suitable for '
                              'taxcalc.sas input.'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.INPUT, ARGS.OUTPUT))
