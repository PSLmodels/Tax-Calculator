"""
Marginal tax rate test program for Calculator class logic that
uses 'puf.csv' records and writes mtr histograms to stdout.

COMMAND-LINE USAGE: python testmtr.py

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 testmtr.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy testmtr.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import sys
import numpy as np
from taxcalc import Policy, Records, Calculator


def run():
    """
    Compute histograms for each marginal tax rate income type using
    sample input from the 'puf.csv' file and writing output to stdout.
    """
    # create a Policy object containing current-law policy (clp) parameters
    clp = Policy()

    # create a Records object (puf) containing puf.csv input records
    puf = Records()

    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)

    # compute marginal tax rate (mtr) histograms for each mtr income type
    mtr_income_types = ['e00200p', 'e00900p',
                        'e00300', 'e01700', 'e02400', 'e23250']
    # . . . specify FICA mtr histogram bin boundaries (or edges):
    fica_bin_edges = [0.0, 0.02, 0.04, 0.06, 0.08,
                      0.10, 0.12, 0.14, 0.16, 0.18, 1.0]
    #                the bin boundaries above are arbitrary, so users
    #                may want to experiment with alternative boundaries
    # . . . specify IIT mtr histogram bin boundaries (or edges):
    iit_bin_edges = [-1.0, -0.30, -0.20, -0.10, 0.0,
                     0.10, 0.20, 0.30, 0.40, 0.50, 1.0]
    #                the bin boundaries above are arbitrary, so users
    #                may want to experiment with alternative boundaries
    assert len(fica_bin_edges) == len(iit_bin_edges)
    sys.stdout.write('{} = {}\n'.format('Total number of data records',
                                        puf.dim))
    sys.stdout.write('FICA mtr histogram bin edges:\n')
    sys.stdout.write('     {}\n'.format(fica_bin_edges))
    sys.stdout.write('IIT mtr histogram bin edges:\n')
    sys.stdout.write('     {}\n'.format(iit_bin_edges))
    inctype_header = 'FICA and IIT mtr histogram bin counts for'
    for inctype in mtr_income_types:
        (mtr_fica, mtr_iit, _) = calc.mtr(income_type_str=inctype,
                                          wrt_full_compensation=False)
        sys.stdout.write('{} {}:\n'.format(inctype_header, inctype))
        write_mtr_bin_counts(mtr_fica, fica_bin_edges)
        write_mtr_bin_counts(mtr_iit, iit_bin_edges)


def write_mtr_bin_counts(mtr_data, bin_edges):
    """
    Calculate and write to stdout mtr histogram bin counts.
    """
    (bincount, _) = np.histogram(mtr_data, bins=bin_edges)
    sum_bincount = np.sum(bincount)
    sys.stdout.write('{} :'.format(sum_bincount))
    for idx in range(len(bin_edges) - 1):
        sys.stdout.write(' {:6d}'.format(bincount[idx]))
    sys.stdout.write('\n')
    if sum_bincount < mtr_data.size:
        sys.stdout.write('WARNING: sum of bin counts is too low:')
        mtr_min = mtr_data.min()
        mtr_max = mtr_data.max()
        if mtr_min < min(bin_edges):
            sys.stdout.write(' min(mtr)={:.2f} '.format(mtr_min))
        if mtr_max > max(bin_edges):
            sys.stdout.write(' max(mtr)={:.2f} '.format(mtr_max))
        sys.stdout.write('\n')


if __name__ == '__main__':
    run()
