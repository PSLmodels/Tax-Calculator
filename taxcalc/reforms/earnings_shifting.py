"""
Python script that uses Tax-Calculator to analyze the tax revenue implications
of various earnings-shifting assumptions under the Trump2017.json tax reform.

The concept of earnings-shifting is the transformation of wage and
salary income into pass-through income from a newly-created limited-
liability company (LLC) as described in several articles, including
Neil Irwin, "Under the Trump Tax Plan, We Might All Want to Become
Corporations," New York Times, April 28, 2017.

Script requirements:
(1) taxcalc conda package version 0.9.1 or higher installed on computer
(2) proprietary puf.csv file used by TaxBrain located in current directory
(3) Trump2017.json reform file located in current directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 earnings_shifting.py
# pylint --disable=locally-disabled earnings_shifting.py

import sys

# pylint: disable=wildcard-import,unused-wildcard-import
from taxcalc import *

REFORM = 'Trump2017.json'
TAXYEAR = 2017


def earnings_shifting_main():
    """
    Contains high-level logic of the script.
    """
    # create calc1, current-law Calculator object
    calc1 = Calculator(policy=Policy(), records=Records())

    # create calc2, reform Calculator object with
    #               static response assumptions and
    #               no earnings-shifting
    policy2 = Policy()
    pdict = Calculator.read_json_param_files(reform_filename=REFORM,
                                             assump_filename=None)
    policy2.implement_reform(pdict['policy'])
    calc2 = Calculator(policy=policy2, records=Records())

    # advance all Calculator objects to TAXYEAR
    while calc1.current_year < TAXYEAR:
        calc1.increment_year()
        calc2.increment_year()

    # conduct tax calculations for TAXYEAR
    calc1.calc_all()
    calc2.calc_all()

    # write results
    sys.stdout.write('==> CALC1 in {}:\n'.format(TAXYEAR))
    write_tables(calc1, None)
    sys.stdout.write('\n==> CALC2 vs CALC1 in {}:\n'.format(TAXYEAR))
    write_tables(calc2, calc1)

    # normal return code
    return 0
# end of main function


def write_tables(calc, calc_base=None):
    """
    Write tables for specified Calculator object to stdout.
    """
    # pylint: disable=too-many-locals
    nontax_cols = ['s006', 'expanded_income']
    tax_cols = ['iitax', 'payrolltax', 'combined']
    all_cols = nontax_cols + tax_cols
    # create DataFrame with weighted tax totals from calc
    non = [getattr(calc.records, col) for col in nontax_cols]
    ref = [getattr(calc.records, col) for col in tax_cols]
    tot = non + ref
    totdf = pd.DataFrame(data=np.column_stack(tot), columns=all_cols)
    # create DataFrame with weighted tax differences if calc_base!=None
    if calc_base is not None:
        bas = [getattr(calc_base.records, col) for col in tax_cols]
        chg = [(ref[idx] - bas[idx]) for idx in range(0, len(tax_cols))]
        dif = non + chg
        difdf = pd.DataFrame(data=np.column_stack(dif), columns=all_cols)
    # write the distributional table(s)
    title = 'Weighted Tax Totals by Expanded-Income Decile\n'
    sys.stdout.write(title)
    write_decile_table(totdf)
    if calc_base is not None:
        title = 'Weighted Tax Differences by Expanded-Income Decile\n'
        sys.stdout.write(title)
        write_decile_table(difdf)


def write_decile_table(dfx):
    """
    Write to stdout the distributional table specified in dfx DataFrame.
    """
    # create expanded-income decile information
    dfx = add_weighted_income_bins(dfx, num_bins=10,
                                   income_measure='expanded_income',
                                   weight_by_income_measure=False)
    gdfx = dfx.groupby('bins', as_index=False)
    rtns_series = gdfx.apply(unweighted_sum, 's006')
    xinc_series = gdfx.apply(weighted_sum, 'expanded_income')
    itax_series = gdfx.apply(weighted_sum, 'iitax')
    ptax_series = gdfx.apply(weighted_sum, 'payrolltax')
    ctax_series = gdfx.apply(weighted_sum, 'combined')
    # write decile table to stdout
    rowfmt = '{}{}{}{}{}\n'
    row = rowfmt.format('    Returns',
                        '    ExpInc',
                        '    IncTax',
                        '    PayTax',
                        '    AllTax')
    sys.stdout.write(row)
    row = rowfmt.format('       (#m)',
                        '      ($b)',
                        '      ($b)',
                        '      ($b)',
                        '      ($b)')
    sys.stdout.write(row)
    rowfmt = '{:9.1f}{:10.1f}{:10.1f}{:10.1f}{:10.1f}\n'
    for decile in range(0, 10):
        row = '{:2d}'.format(decile)
        row += rowfmt.format(rtns_series[decile] * 1e-6,
                             xinc_series[decile] * 1e-9,
                             itax_series[decile] * 1e-9,
                             ptax_series[decile] * 1e-9,
                             ctax_series[decile] * 1e-9)
        sys.stdout.write(row)
    row = ' A'
    row += rowfmt.format(rtns_series.sum() * 1e-6,
                         xinc_series.sum() * 1e-9,
                         itax_series.sum() * 1e-9,
                         ptax_series.sum() * 1e-9,
                         ctax_series.sum() * 1e-9)
    sys.stdout.write(row)


if __name__ == '__main__':
    sys.exit(earnings_shifting_main())
