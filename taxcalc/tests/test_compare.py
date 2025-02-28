"""
Compares Tax-Calculator PUF and CPS results with historical information.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_compare.py
# pylint --disable=locally-disabled test_compare.py

import os
import pytest
import numpy as np
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator
from taxcalc.utils import add_income_table_row_variable, SOI_AGI_BINS


# 2015 IRS-SOI amounts by AGI category are from "Table 3.3 All Returns: Tax
# Liability, Tax Credits, and Tax Payments by Size of Adjusted Gross Income,
# Tax Year 2015" which is available as a spreadsheet at this URL:
# <https://www.irs.gov/statistics/soi-tax-stats-individual-
#  statistical-tables-by-size-of-adjusted-gross-income>
# The IRS-SOI amounts are from 19 rows in the spreadsheet numbered from
# 11 (AGI under one dollar) through 29 (AGI $10M or more).
# Dollar IRS-SOI amounts are expressed in billions of dollars and rounded
# to the nearest one-tenth of a million dollars.
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
    gbydf = vardf.groupby('table_row', as_index=False, observed=True)
    # write AGI table with ALL row at bottom of ofile
    ofile.write(f'TABLE for {cname.split(":")[1]}\n')
    results = '{:23s}\t{:8.3f}\t{:8.3f}\t{:+6.1f}\n'
    colhead = f'{"AGIcategory":23s}\t{"T-C":>8s}\t{"SOI":>8s}\t{"%diff":>6s}\n'
    ofile.write(colhead)
    # pylint: disable=consider-using-f-string
    txc_tot = 0.
    soi_tot = 0.
    idx = 0
    for grp_interval, grp in gbydf:
        txc = (grp['cvar'] * grp['s006']).sum() * 1e-9
        soi = cmpdata[cname]['SOI'][idx]
        txc_tot += txc
        soi_tot += soi
        if soi > 0:
            pct_diff = 100. * ((txc / soi) - 1.)
        else:
            pct_diff = np.nan
        glabel = f'[{grp_interval.left:.8g}, {grp_interval.right:.8g})'
        ofile.write(results.format(glabel, txc, soi, pct_diff))
        idx += 1
    pct_diff = 100. * ((txc_tot / soi_tot) - 1.)
    ofile.write(results.format('ALL', txc_tot, soi_tot, pct_diff))
    # pylint: enable=consider-using-f-string


def nonsmall_diffs(linelist1, linelist2, small=0.0):
    """
    Return True if line lists differ significantly; otherwise return False.
    Significant numerical difference means one or more numbers differ (between
    linelist1 and linelist2) by more than the specified small amount.
    """
    # embedded function used only in nonsmall_diffs function
    def isfloat(value):
        """
        Return True if value can be cast to float; otherwise return False.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    # begin nonsmall_diffs logic
    assert isinstance(linelist1, list)
    assert isinstance(linelist2, list)
    if len(linelist1) != len(linelist2):
        return True
    assert 0.0 <= small <= 1.0
    epsilon = 1e-6
    smallamt = small + epsilon
    for line1, line2 in zip(linelist1, linelist2):
        if line1 == line2:
            continue
        tokens1 = line1.replace(',', '').split()
        tokens2 = line2.replace(',', '').split()
        for tok1, tok2 in zip(tokens1, tokens2):
            tok1_isfloat = isfloat(tok1)
            tok2_isfloat = isfloat(tok2)
            if tok1_isfloat and tok2_isfloat:
                if abs(float(tok1) - float(tok2)) <= smallamt:
                    continue
                return True
            if not tok1_isfloat and not tok2_isfloat:
                if tok1 == tok2:
                    continue
                return True
            return True
        return False


def differences(afilename, efilename):
    """
    Check for differences between results in afilename and efilename files.
    """
    with open(afilename, 'r', encoding='utf-8') as afile:
        actres = afile.read()
    with open(efilename, 'r', encoding='utf-8') as efile:
        expres = efile.read()
    diffs = nonsmall_diffs(actres.splitlines(True),
                           expres.splitlines(True), 0.0)
    if diffs:
        afname = os.path.basename(afilename)
        efname = os.path.basename(efilename)
        msg = 'COMPARE RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += f'--- NEW RESULTS IN {afname} FILE   ---\n'
        msg += f'--- if new OK, copy {afname} to    ---\n'
        msg += f'---                 {efname}       ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    os.remove(afilename)


@pytest.mark.pre_release
@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('using_puf', [True, False])
def test_itax_compare(tests_path, using_puf, puf_fullsample, cps_fullsample):
    """
    Conduct income tax comparisons using ITAX data.
    """
    using_puf_adjust_ratios = True
    # generate 2015 estimates by AGI category using Tax-Calculator
    if using_puf:
        if using_puf_adjust_ratios:
            recs = Records(data=puf_fullsample)
        else:
            recs = Records(data=puf_fullsample, adjust_ratios=None)
    else:
        recs = Records.cps_constructor(data=cps_fullsample)
    calc = Calculator(policy=Policy(), records=recs, verbose=False)
    calc.advance_to_year(2015)
    calc.calc_all()
    # open actual output file
    if using_puf:
        afilename = os.path.join(tests_path, 'cmpi_puf_actual.txt')
    else:
        afilename = os.path.join(tests_path, 'cmpi_cps_actual.txt')
    with open(afilename, 'w', encoding='utf-8') as afile:
        # write compare results to afile
        for cname in sorted(ITAX.keys()):
            comparison(cname, calc, ITAX, afile)
    # check for differences between actual and expect output files
    efilename = afilename.replace('actual', 'expect')
    differences(afilename, efilename)
