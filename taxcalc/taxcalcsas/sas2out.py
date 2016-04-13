"""
Script that takes specified CSV-formatted output file, which is generated
by the TAXCALC SAS program, and translates that information into a file that
has an Internet-TAXSIM output format.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 sas2out.py
# pylint --disable=locally-disabled sas2out.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import os
import sys
import argparse
import pandas as pd
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import SimpleTaxIO  # pylint: disable=import-error


def main(infilename, outfilename):
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into a Pandas DataFrame
    inputdf = pd.read_csv(infilename)

    # translate INPUT variables into OUTPUT lines
    olines = ''
    for idx in range(0, inputdf.shape[0]):
        rec = inputdf.xs(idx)
        odict = extract_output(rec)
        olines += SimpleTaxIO.construct_output_line(odict)

    # write OUTPUT lines to OUTPUT file
    with open(outfilename, 'w') as outfile:
        outfile.write(olines)

    # return no-error exit code
    return 0
# end of main function code


def extract_output(rec):
    """
    Extracts tax output from tax filing unit rec.

    Parameters
    ----------
    rec: Pandas Series indexed by variable names in EXPECTED_INPUT_VARS set.

    Returns
    -------
    ovar: dictionary of output variables indexed from 1 to SimpleTaxIO.OVAR_NUM

    Notes
    -----
    The value of each output variable is stored in the ovar dictionary,
    which is indexed as Internet-TAXSIM output variables are (where the
    index begins with one).
    """
    ovar = {}
    ovar[1] = int(rec['RECID'])  # id for tax filing unit
    ovar[2] = 2013  # year for which taxes are calculated
    ovar[3] = 0  # state code is always zero
    ovar[4] = rec['_nbertax']  # federal income tax liability
    ovar[5] = 0.0  # no state income tax calculation
    ovar[6] = 0.0  # NOT IN TAXCALC.SAS : FICA taxes (ee+er) for OASDI+HI
    ovar[7] = 0.0  # marginal federal income tax rate as percent
    ovar[8] = 0.0  # no state income tax calculation
    ovar[9] = 0.0  # marginal FICA tax rate as percent
    ovar[10] = rec['c00100']  # federal AGI
    ovar[11] = 0.0  # UI benefits in AGI
    ovar[12] = rec['c02500']  # OASDI benefits in AGI
    ovar[13] = 0.0  # always set zero-bracket amount to zero
    # pre_phase_out_pe = rec['_prexmp']
    # post_phase_out_pe = rec['c04600']
    # phased_out_pe = pre_phase_out_pe - post_phase_out_pe
    ovar[14] = 0.0  # post_phase_out_pe  # post-phase-out personal exemption
    ovar[15] = 0.0  # phased_out_pe  # personal exemption that is phased out
    # ovar[16] can be positive for non-itemizer:
    ovar[16] = rec['c21040']  # itemized deduction that is phased out
    # ovar[17] is zero for non-itemizer:
    ovar[17] = rec['c04470']  # post-phase-out itemized deduction
    ovar[18] = rec['c04800']  # federal regular taxable income
    ovar[19] = rec['c05200']  # regular tax on taxable income
    ovar[20] = 0.0  # always set exemption surtax to zero
    ovar[21] = 0.0  # always set general tax credit to zero
    ovar[22] = rec['c07220']  # child tax credit (adjusted)
    ovar[23] = rec['c11070']  # extra child tax credit (refunded)
    ovar[24] = rec['c07180']  # child care credit
    ovar[25] = rec['c59660']  # federal EITC amount
    ovar[26] = 0.0  # rec['c62100']  # federal AMT taxable income ?_everybody?
    amt_liability = rec['c09600']  # federal AMT liability
    ovar[27] = amt_liability
    # ovar[28] is federal income tax before credits; the variable
    # rec['c05800'] is this concept but includes AMT liability while
    # Internet-TAXSIM ovar[28] explicitly excludes AMT liability, so
    # we have the following:
    ovar[28] = rec['c05800'] - amt_liability
    return ovar
# end of extract_output function code


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        prog='python sas2out.py',
        description=('Reads CSV-formatted INPUT file containing '
                     'TAXCALC SAS output results and writes an '
                     'OUTPUT file with Internet-TAXSIM output format.'))
    PARSER.add_argument('INPUT',
                        help=('INPUT is name of required file that contains '
                              'CSV-formatted TAXCALC SAS output results.'))
    PARSER.add_argument('OUTPUT',
                        help=('OUTPUT is name of required file that contains '
                              'output results in Internet-TAXSIM format.'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.INPUT, ARGS.OUTPUT))
