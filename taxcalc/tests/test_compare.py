"""
Compares Tax-Calculator PUF and CPS results with historical information.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_compare.py
# pylint --disable=locally-disabled test_compare.py

from __future__ import print_function
import os
import sys
import pytest
import numpy as np
# pylint: disable=import-error,pointless-string-statement
from taxcalc import Policy, Records, Calculator, nonsmall_diffs
from taxcalc import add_income_table_row_variable, SOI_AGI_BINS


"""
2015 IRS-SOI amounts by AGI category are from "Table 3.3 All Returns: Tax
Liability, Tax Credits, and Tax Payments by Size of Adjusted Gross Income,
Tax Year 2015" which is available as a spreadsheet at this URL:
<https://www.irs.gov/statistics/soi-tax-stats-individual-
statistical-tables-by-size-of-adjusted-gross-income>
The IRS-SOI amounts are from 19 rows in the spreadsheet numbered from
11 (AGI under one dollar) through 29 (AGI $10M or more).
Dollar IRS-SOI amounts are expressed in billions of dollars and rounded
to the nearest one-tenth of a million dollars.
"""
ITAX = {
    '0:EITC': {
        # Full earned income credit
        # in 2015 using the IRS-SOI information described above.
        # EITC is column (37) in the Table 3.3 spreadsheet,
        # which is the sum of columns (47), (75) and (97).
        'SOI': [0.2104,
                1.1843,
                7.1562,
                16.5927,
                15.8799,
                11.1025,
                7.5150,
                7.4528,
                1.3936,
                0.0375,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000],
        'TC': ['eitc']
    },

    '1:FCTC': {
        # Full (basic and additional, refundable and nonrefundable) child tax
        # credit in 2015 using the IRS-SOI information described above.
        # FCTC is sum of columns (13) and (39) in the Table 3.3 spreadsheet.
        'SOI': [0.1301,
                0.0793,
                1.4740,
                4.2580,
                5.2104,
                4.6582,
                4.3166,
                7.2320,
                5.2848,
                9.4151,
                6.4075,
                5.2222,
                0.0018,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000],
        'TC': ['c07220',  # FCTC that is nonrefundable
               'c11070']  # FCTC that isrefundable
    },

    '2:NIIT': {
        # Net investment income tax
        # in 2015 using the IRS-SOI information described above.
        # NIIT is column (53) in the Table 3.3 spreadsheet.
        # NIIT is included in Tax-Calculator individual income tax liability.
        'SOI': [0.0004,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0000,
                0.0001,
                0.0000,
                0.0000,
                0.0014,
                0.0005,
                0.0213,
                2.6397,
                3.1356,
                1.6715,
                1.0775,
                3.1267,
                2.0949,
                8.2730],
        'TC': ['niit']
    },

    '3:ITAX': {
        # Total income tax liability
        # in 2015 using the IRS-SOI information described above.
        # ITAX is column (55) in the Table 3.3 spreadsheet,
        # which includes NIIT and is after all credits.
        'SOI': [0.2425,
                0.0409,
                0.3680,
                1.3813,
                3.5238,
                6.1911,
                8.7526,
                25.1677,
                32.5302,
                99.7918,
                105.9015,
                316.3496,
                299.8322,
                154.3888,
                66.3236,
                39.6716,
                101.4885,
                56.3344,
                139.6113],
        'TC': ['iitax']
    },

    '4:SETAX': {
        # Self-employment tax
        # in 2015 using the IRS-SOI information described above.
        # SETAX is column (59) in the Table 3.3 spreadsheet,
        # which is not part of ITAX but is part of total payroll taxes.
        'SOI': [0.6557,
                0.5554,
                1.8956,
                3.5143,
                2.8228,
                1.9959,
                1.8020,
                3.3598,
                2.8199,
                5.9579,
                5.2751,
                12.1488,
                9.6864,
                3.4864,
                1.1938,
                0.6432,
                1.2527,
                0.4698,
                0.6383],
        'TC': ['setax']
    },

    '5:AMTAX': {
        # Additional Medicare tax
        # in 2015 using the IRS-SOI information described above.
        # AMTAX is column (71) in the Table 3.3 spreadsheet,
        # which is not part of ITAX but is part of total payroll taxes.
        'SOI': [0.0225,
                0.0003,
                0.0000,
                0.0002,
                0.0002,
                0.0004,
                0.0002,
                0.0041,
                0.0071,
                0.0057,
                0.0026,
                0.0372,
                1.8356,
                2.0214,
                0.8602,
                0.4898,
                1.1730,
                0.5805,
                0.9787],
        'TC': ['ptax_amc']
    }
}


def comparison(cname, calc, cmpdata, ofile):
    """
    Write comparison results for cname to ofile.
    """
    # pylint: disable=too-many-locals
    # generate compare table for cvarname
    vardf = calc.dataframe(['s006', 'c00100'])  # weight and AGI
    # add compare variable to vardf
    cvar = np.zeros(calc.array_len)
    for var in cmpdata[cname]['TC']:
        cvar += calc.array(var)
    vardf['cvar'] = cvar
    # construct AGI table
    vardf = add_income_table_row_variable(vardf, 'c00100', SOI_AGI_BINS)
    gbydf = vardf.groupby('table_row', as_index=False)
    # write AGI table with ALL row at bottom to ofile
    ofile.write('TABLE for {}\n'.format(cname.split(':')[1]))
    results = '{:23s}\t{:8.3f}\t{:8.3f}\t{:+6.1f}\n'
    colhead = '{:23s}\t{:>8s}\t{:>8s}\t{:>6s}\n'
    ofile.write(colhead.format('AGI category', 'T-C', 'SOI', '%diff'))
    txc_tot = 0.
    soi_tot = 0.
    idx = 0
    for gname, grp in gbydf:
        txc = (grp['cvar'] * grp['s006']).sum() * 1e-9
        soi = cmpdata[cname]['SOI'][idx]
        txc_tot += txc
        soi_tot += soi
        if soi > 0:
            pct_diff = 100. * ((txc / soi) - 1.)
        else:
            pct_diff = np.nan
        ofile.write(results.format(gname, txc, soi, pct_diff))
        idx += 1
    pct_diff = 100. * ((txc_tot / soi_tot) - 1.)
    ofile.write(results.format('ALL', txc_tot, soi_tot, pct_diff))


def differences(afilename, efilename):
    """
    Check for differences between results in afilename and efilename files.
    """
    with open(afilename, 'r') as afile:
        actres = afile.read()
    with open(efilename, 'r') as efile:
        expres = efile.read()
    diffs = nonsmall_diffs(actres.splitlines(True),
                           expres.splitlines(True), 0.0)
    if diffs:
        afname = os.path.basename(afilename)
        efname = os.path.basename(efilename)
        msg = 'COMPARE RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN {} FILE ---\n'
        msg += '--- if new OK, copy {} to  ---\n'
        msg += '---                 {}     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg.format(afname, afname, efname))
    else:
        os.remove(afilename)


@pytest.mark.skipif(sys.version_info > (3, 0),
                    reason='remove skipif after migration to Python 3.6')
@pytest.mark.pre_release
@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('using_puf', [True, False])
def test_itax_compare(tests_path, using_puf, puf_fullsample, cps_fullsample):
    """
    Conduct income tax comparisons using ITAX data.
    """
    # generate 2015 estimates by AGI category using Tax-Calculator
    if using_puf:
        recs = Records(data=puf_fullsample)
    else:
        recs = Records.cps_constructor(data=cps_fullsample, no_benefits=True)
    calc = Calculator(policy=Policy(), records=recs, verbose=False)
    calc.advance_to_year(2015)
    calc.calc_all()
    # open actual output file
    if using_puf:
        afilename = os.path.join(tests_path, 'cmpi_puf_actual.txt')
    else:
        afilename = os.path.join(tests_path, 'cmpi_cps_actual.txt')
    afile = open(afilename, 'w')
    # write compare results to afile
    for cname in sorted(ITAX.keys()):
        comparison(cname, calc, ITAX, afile)
    # close actual output file
    afile.close()
    # check for differences between actual and expect output files
    efilename = afilename.replace('actual', 'expect')
    differences(afilename, efilename)
