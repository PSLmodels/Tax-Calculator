"""
Tax-Calculator validation script that identifies tax differences in two
CSV-formatted files that contain variables like those included in tc.py
--dump files.  Variables not in both files are skipped, but the two
files being compared must contain output for the same set of input records.
This means that the RECID variable must be in both files and RECID values
must exactly match in the two files being compared.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 csv_taxdiffs.py
# pylint --disable=locally-disabled csv_taxdiffs.py

import argparse
import sys
import os
import numpy as np
import pandas as pd


def main(file1name, file2name):
    """
    Contains high-level logic of the script.
    """
    # read file contents into Pandas DataFrames
    df1 = pd.read_csv(file1name)
    df1_vars = set(list(df1))
    df2 = pd.read_csv(file2name)
    df2_vars = set(list(df2))

    # check that both files contain required tax variables
    required_tax_vars = set(['RECID', '_iitax', '_payrolltax'])
    required_vars_str = '"RECID" "_iitax" "_payrolltax"'
    if not required_tax_vars.issubset(df1_vars):
        msg = 'ERROR: FILE1 does not include required variables: {}\n'
        sys.stderr.write(msg.format(required_vars_str))
        return 1
    if not required_tax_vars.issubset(df2_vars):
        msg = 'ERROR: FILE2 does not include required variables: {}\n'
        sys.stderr.write(msg.format(required_vars_str))
        return 1

    # check that RECID variable is same in both files
    if not df1['RECID'].equals(df2['RECID']):
        msg = 'ERROR: RECID not the same in both FILE1 and FILE2\n'
        sys.stderr.write(msg)
        return 1

    # compare variable values when variable is in both files
    tax_vars = ['_iitax',       # income tax
                '_payrolltax',  # payroll tax
                'c00100',       # AGI
                'e02300',       # UI benefits in AGI
                'c02500',       # OASDI benefits in AGI
                'pre_c04600',   # pre-phase-out personal exemption
                'c04600',       # post-phase-out personal exemption
                'c04470',       # post-phase-out itemized deduction
                'c04800',       # regular taxable income
                '_taxbc',       # regular tax on regular taxable income
                'c07220',       # child tax credit (adjusted)
                'c11070',       # extra child tax credit (refunded)
                'c07180',       # child care credit
                '_eitc',        # EITC
                'c62100',       # AMT taxable income
                'c09600',       # AMT liability
                'c05800']       # total income tax before credits
    rounding_error = 0.01
    for var in tax_vars:
        if var in df1_vars and var in df2_vars:
            compare_var(var, df1[var], df2[var], rounding_error, df1['RECID'])
            
    # normal return code
    return 0
# end of main function code


def compare_var(varname, array1, array2, rounding_error, idarray):
    """
    Summarize differences between array1 and array2.
    """
    diff = array1 - array2
    absdiff = np.abs(diff)
    max_absdiff = np.amax(absdiff)
    if max_absdiff <= rounding_error:
        return  # array1 and array2 are equal apart from rounding error
    realdiff = np.where(absdiff > rounding_error, 1, 0)
    numdiffs = np.sum(realdiff)
    idx = np.where(absdiff >= max_absdiff)[0][0]
    recid = idarray[idx]
    sdiff = diff[idx]
    out = 'TAXDIFF:var,#diffs,maxdiff[RECID]= {:12s} {:6d} {:12.2f} [{}]\n'
    sys.stdout.write(out.format(varname, numdiffs, sdiff, recid))


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python csv_taxdiffs.py',
        description=('Identifies differences in tax output between two '
                     'CSV-formatted files.'))
    PARSER.add_argument('FILE1', nargs='?', default='',
                        help=('Name of first file; must end with ".csv".'))
    PARSER.add_argument('FILE2', nargs='?', default='',
                        help=('Name of second file; must end with ".csv".'))
    ARGS = PARSER.parse_args()
    # check for invalid command-line argument values
    ARGS_ERROR = False
    if ARGS.FILE1 == '':
        sys.stderr.write('ERROR: FILE1 must be specified\n')
        ARGS_ERROR = True
    if ARGS.FILE2 == '':
        sys.stderr.write('ERROR: FILE2 must be specified\n')
        ARGS_ERROR = True
    if not os.path.isfile(ARGS.FILE1):
        MSG = 'ERROR: FILE1 [{}] does not exist\n'
        sys.stderr.write(MSG.format(ARGS.FILE1))
        ARGS_ERROR = True
    if not ARGS.FILE1.endswith('.csv'):
        MSG = 'ERROR: FILE1 [{}] does not end with ".csv"\n'
        sys.stderr.write(MSG.format(ARGS.FILE1))
        ARGS_ERROR = True
    if not os.path.isfile(ARGS.FILE2):
        MSG = 'ERROR: FILE2 [{}] does not exist\n'
        sys.stderr.write(MSG.format(ARGS.FILE2))
        ARGS_ERROR = True
    if not ARGS.FILE2.endswith('.csv'):
        MSG = 'ERROR: FILE2 [{}] does not end with ".csv"\n'
        sys.stderr.write(MSG.format(ARGS.FILE2))
        ARGS_ERROR = True
    if ARGS_ERROR:
        sys.stderr.write('USAGE: python csv_taxdiffs.py --help\n')
        RCODE = 1
    else:
        RCODE = main(ARGS.FILE1, ARGS.FILE2)
    sys.exit(RCODE)
