"""
Tests of Tax-Calculator using puf.csv input.

Note that the puf.csv file that is required to run this program has
been constructed by the Tax-Calculator development team by merging
information from the most recent publicly available IRS SOI PUF file
and from the Census CPS file for the corresponding year.  If you have
acquired from IRS the most recent SOI PUF file and want to execute
this program, contact the Tax-Calculator development team to discuss
your options.

Read tax-calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_pufcsv_agg.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy \
#        test_pufcsv_agg.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
PUFCSV_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
import pytest
import difflib
import numpy as np


EXPECTED_AGG_RESULTS = (
    '                                   2013     2014     2015     2016'
    '     2017     2018     2019     2020     2021     2022\n'
    'Returns (#m)                      147.4    149.1    151.4    153.5'
    '    155.4    156.7    157.6    158.7    159.8    160.9\n'
    'AGI ($b)                        9,217.8  9,676.6 10,233.9 10,744.0'
    ' 11,287.4 11,823.1 12,365.5 12,926.8 13,501.3 14,099.1\n'
    'Itemizers (#m)                     42.3     42.9     43.7     44.6'
    '     45.3     46.0     46.6     47.2     47.8     48.3\n'
    'Itemized Deduction ($b)         1,109.4  1,151.9  1,214.2  1,288.7'
    '  1,366.8  1,447.3  1,527.1  1,612.1  1,699.2  1,789.5\n'
    'Standard Deduction Filers (#m)    101.9    102.9    104.2    105.5'
    '    106.6    107.2    107.5    108.0    108.5    109.0\n'
    'Standard Deduction ($b)           877.3    901.0    928.1    958.9'
    '    989.5  1,016.8  1,043.3  1,073.6  1,105.9  1,140.0\n'
    'Personal Exemption ($b)         1,089.7  1,109.7  1,133.1  1,166.7'
    '  1,199.7  1,231.8  1,264.3  1,299.6  1,337.8  1,377.5\n'
    'Taxable income ($b)             6,516.1  6,918.8  7,379.1  7,760.7'
    '  8,169.2  8,568.7  8,978.5  9,396.5  9,821.9 10,265.5\n'
    'Regular Tax ($b)                1,422.5  1,533.0  1,654.8  1,740.9'
    '  1,833.4  1,922.8  2,016.3  2,112.5  2,208.8  2,309.3\n'
    'AMT income ($b)                 2,601.3  2,824.5  3,066.3  3,220.1'
    '  3,395.4  3,576.0  3,763.7  3,949.2  4,141.9  4,338.8\n'
    'AMT amount ($b)                    31.2     32.5     34.6     37.1'
    '     39.6     42.3     44.9     47.6     50.4     53.6\n'
    'AMT number (#m)                     4.1      4.3      4.5      4.7'
    '      5.0      5.2      5.5      5.7      5.9      6.0\n'
    'Tax before credits ($b)         1,354.0  1,436.0  1,539.8  1,625.2'
    '  1,714.8  1,800.5  1,889.3  1,980.9  2,072.6  2,168.4\n'
    'refundable credits ($b)           115.4    116.8    117.8    119.6'
    '    120.9    107.4    108.7    109.9    111.7    113.7\n'
    'nonrefundable credits ($b)         70.6     70.0     71.6     73.2'
    '     74.5     62.3     63.2     64.5     65.6     66.5\n'
    'Misc. Surtax ($b)                   0.0      0.0      0.0      0.0'
    '      0.0      0.0      0.0      0.0      0.0      0.0\n'
    'Ind inc tax ($b)                1,245.9  1,334.2  1,440.7  1,524.5'
    '  1,613.8  1,727.5  1,816.5  1,908.2  1,999.6  2,095.0\n'
    'Payroll tax ($b)                  919.3    956.7    997.4  1,048.3'
    '  1,102.9  1,157.7  1,211.8  1,267.2  1,324.3  1,383.8'
)  # note lack of '\n' character at end of last line


@pytest.mark.requires_pufcsv
def test_agg():
    """
    Test Tax-Calculator aggregate taxes with no policy reform using puf.csv
    """
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    # create a Records object (puf) containing puf.csv input records
    puf = Records(data=PUFCSV_PATH)
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(num_years=10)
    # convert adt results to a string
    adtstr = adt.to_string()
    # generate differences between actual and expected results
    actual = adtstr.splitlines(True)
    expected = EXPECTED_AGG_RESULTS.splitlines(True)
    diff = difflib.unified_diff(expected, actual,
                                fromfile='expected', tofile='actual', n=0)
    # convert diff generator into a list of lines:
    diff_lines = list()
    for line in diff:
        diff_lines.append(line)
    # test failure if there are any diff_lines
    if len(diff_lines) > 0:
        for line in diff_lines:
            sys.stdout.write(line)
        assert False


EXPECTED_MTR_RESULTS = """
MTR computed using POSITIVE finite_diff.
Total number of data records = 219814
FICA mtr histogram bin edges:
     [0.0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 1.0]
IIT mtr histogram bin edges:
     [-1.0, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
FICA and IIT mtr histogram bin counts for e00200p:
219814 :      0  31950      0      0      0      0      0 183680   4184      0
219814 :   4585    105   1757  14219  39076  62494  47355  27220  22328    675
FICA and IIT mtr histogram bin counts for e00900p:
219814 :  14116  29235      0      0      0   1343      0 175120      0      0
219814 :   4583    107   1757  14132  43916  59968  52749  24172  18106    324
FICA and IIT mtr histogram bin counts for e00300:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0      0  59959  63615  43215  26412  25930    682
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
FICA and IIT mtr histogram bin counts for e00400:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0      0 206435   7602   5640     97     33      6
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
FICA and IIT mtr histogram bin counts for e00600:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0      0  59967  63607  43252  26375  25930    682
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
FICA and IIT mtr histogram bin counts for e00650:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0  17796 106853  43515  50587    636    405     21
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
FICA and IIT mtr histogram bin counts for e01400:
219814 : 219814      0      0      0      0      0      0      0      0      0
219814 :      0      0      0      0  60004  63594  46897  26883  21768    668
FICA and IIT mtr histogram bin counts for e01700:
219814 : 219814      0      0      0      0      0      0      0      0      0
219814 :      0      0      0      0  60014  63584  46902  26876  21770    668
FICA and IIT mtr histogram bin counts for e02000:
219814 : 219814      0      0      0      0      0      0      0      0      0
219814 :      0      0      0      0  60048  63546  43754  26150  25638    678
FICA and IIT mtr histogram bin counts for e02400:
219814 : 219814      0      0      0      0      0      0      0      0      0
219814 :      0      0      0      0  99155  39924  50828  29046    762     99
FICA and IIT mtr histogram bin counts for p22250:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0     21  82444  61370  41814  19040  14709    415
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
FICA and IIT mtr histogram bin counts for p23250:
219814 : 219814      0      0      0      0      0      0      0      0      0
219813 :      0      0      0  17260 125466  38066  33979   2071   2925     46
WARNING: sum of bin counts is too low
         max(mtr)=12612.69
         mtr=12612.69 for recid=1264520
"""
MTR_TAX_YEAR = 2013
MTR_NEG_DIFF = False  # set True to subtract (rather than add) small amount
# specify FICA mtr histogram bin boundaries (or edges):
FICA_MTR_BIN_EDGES = [0.0, 0.02, 0.04, 0.06, 0.08,
                      0.10, 0.12, 0.14, 0.16, 0.18, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries
# specify IIT mtr histogram bin boundaries (or edges):
IIT_MTR_BIN_EDGES = [-1.0, -0.30, -0.20, -0.10, 0.0,
                     0.10, 0.20, 0.30, 0.40, 0.50, 1.0]
#        the bin boundaries above are arbitrary, so users
#        may want to experiment with alternative boundaries


def mtr_bin_counts(mtr_data, bin_edges, recid):
    """
    Compute mtr histogram bin counts and return results as a string.
    """
    res = ''
    (bincount, _) = np.histogram(mtr_data, bins=bin_edges)
    sum_bincount = np.sum(bincount)
    res += '{} :'.format(sum_bincount)
    for idx in range(len(bin_edges) - 1):
        res += ' {:6d}'.format(bincount[idx])
    res += '\n'
    if sum_bincount < mtr_data.size:
        res += 'WARNING: sum of bin counts is too low\n'
        recinfo = '         mtr={:.2f} for recid={}\n'
        mtr_min = mtr_data.min()
        mtr_max = mtr_data.max()
        bin_min = min(bin_edges)
        bin_max = max(bin_edges)
        if mtr_min < bin_min:
            res += '         min(mtr)={:.2f}\n'.format(mtr_min)
            for idx in range(mtr_data.size):
                if mtr_data[idx] < bin_min:
                    res += recinfo.format(mtr_data[idx], recid[idx])
        if mtr_max > bin_max:
            res += '         max(mtr)={:.2f}\n'.format(mtr_max)
            for idx in range(mtr_data.size):
                if mtr_data[idx] > bin_max:
                    res += recinfo.format(mtr_data[idx], recid[idx])
    return res


@pytest.mark.requires_pufcsv
def test_mtr():
    """
    Test Tax-Calculator marginal tax rates with no policy reform using puf.csv

    Compute histograms for each marginal tax rate income type using
    sample input from the puf.csv file and writing output to a string,
    which is then compared for differences with EXPECTED_MTR_RESULTS.
    """
    assert len(FICA_MTR_BIN_EDGES) == len(IIT_MTR_BIN_EDGES)
    # construct actual results string, res
    res = ''
    if MTR_NEG_DIFF:
        res += 'MTR computed using NEGATIVE finite_diff.\n'
    else:
        res += 'MTR computed using POSITIVE finite_diff.\n'
    # create a Policy object (clp) containing current-law policy parameters
    clp = Policy()
    clp.set_year(MTR_TAX_YEAR)
    # create a Records object (puf) containing puf.csv input records
    puf = Records(data=PUFCSV_PATH)
    recid = puf.RECID  # pylint: disable=no-member
    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)
    res += '{} = {}\n'.format('Total number of data records', puf.dim)
    res += 'FICA mtr histogram bin edges:\n'
    res += '     {}\n'.format(FICA_MTR_BIN_EDGES)
    res += 'IIT mtr histogram bin edges:\n'
    res += '     {}\n'.format(IIT_MTR_BIN_EDGES)
    inctype_header = 'FICA and IIT mtr histogram bin counts for'
    # compute marginal tax rate (mtr) histograms for each mtr income type
    for inctype in Calculator.MTR_VALID_INCOME_TYPES:
        (mtr_fica, mtr_iit, _) = calc.mtr(income_type_str=inctype,
                                          negative_finite_diff=MTR_NEG_DIFF,
                                          wrt_full_compensation=False)
        res += '{} {}:\n'.format(inctype_header, inctype)
        res += mtr_bin_counts(mtr_fica, FICA_MTR_BIN_EDGES, recid)
        res += mtr_bin_counts(mtr_iit, IIT_MTR_BIN_EDGES, recid)
    # generate differences between actual and expected results
    actual = res.splitlines(True)
    expected = EXPECTED_MTR_RESULTS[1:].splitlines(True)  # removes leading EOL
    diff = difflib.unified_diff(expected, actual,
                                fromfile='expected', tofile='actual', n=0)
    # convert diff generator into a list of lines:
    diff_lines = list()
    for line in diff:
        diff_lines.append(line)
    # test failure if there are any diff_lines
    if len(diff_lines) > 0:
        for line in diff_lines:
            sys.stdout.write(line)
        assert False
