"""
Python script that uses Tax-Calculator to analyze the tax revenue implications
of specified earnings-shifting assumptions under the Trump2017.json tax reform.

The concept of earnings-shifting is the transformation of wage and
salary income into pass-through self-employment earnings from a
newly-created personal limited-liability company (LLC) as described in
several articles, including Neil Irwin, "Under the Trump Tax Plan, We
Might All Want to Become Corporations," New York Times, April 28, 2017.

Script requirements:
(1) conda package for taxcalc version 0.9.1 or higher installed on computer
(2) proprietary puf.csv file used by TaxBrain located in current directory
(3) Trump2017.json reform file located in current directory

Note: taxcalc package is installed from command line as follows:
$ conda install -c ospc taxcalc
With puf.csv and Trump2017.json in current directory, proceed as follows:
$ python earnings_shifting.py --help
for details on the required command-line arguments used by the script.

Also, read the earnings_shifting.sh bash script (and its results in the
earnings_shifting.sum text file) for examples of how to use the
earnings_shifting.py Python script.  Some of the results in the
earnings_shifting.sum file are discussed at this URL:
<https://github.com/open-source-economics/Tax-Calculator/pull/1464
#issuecomment-315616386>.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 earnings_shifting.py

import sys
import argparse

# pylint: disable=wildcard-import,unused-wildcard-import
from taxcalc import *

REFORM = 'Trump2017.json'


def main():
    """
    Contains high-level logic of the script.
    """
    # pylint: disable=too-many-statements,too-many-locals

    # read CLI arguments to get probability parameter values dictionary
    param = get_cli_parameters()
    write_parameters(param)
    taxyear = param['year']
    fatal_error = False
    if taxyear < 2017:
        msg = 'ERROR: YEAR={} before first reform year 2017\n'
        sys.stdout.write(msg.format(taxyear))
        fatal_error = True
    if param['wage_amt'] < 0.0 or param['wage_amt'] >= 1e5:
        msg = 'ERROR: WAGE_AMT={} not in [0.0, 100000.0) range\n'
        sys.stdout.write(msg.format(param['wage_amt']))
        fatal_error = True
    if param['min_wage_frac'] < 0.0 or param['min_wage_frac'] > 1.0:
        msg = 'ERROR: MIN_WAGE_FRAC={} not in [0.0, 1.0] range\n'
        sys.stdout.write(msg.format(param['min_wage_frac']))
        fatal_error = True
    if param['min_earnings'] < 0.0:
        msg = 'ERROR: MIN_EARNINGS={} < 0.0\n'
        sys.stdout.write(msg.format(param['min_earnings']))
        fatal_error = True
    if param['min_savings'] < 0.0:
        msg = 'ERROR: MIN_SAVINGS={} < 0.0\n'
        sys.stdout.write(msg.format(param['min_savings']))
        fatal_error = True
    if param['shift_prob'] < 0.0 or param['shift_prob'] > 1.0:
        msg = 'ERROR: SHIFT_PROB={} not in [0.0, 1.0] range\n'
        sys.stdout.write(msg.format(param['shift_prob']))
        fatal_error = True
    if fatal_error:
        return 1
    else:
        sys.stdout.write('\n')

    # create calc1, current-law Calculator object
    calc1 = Calculator(policy=Policy(), records=Records(), verbose=False)

    # create calc2, reform Calculator object with
    #               static response assumptions and
    #               no earnings-shifting
    records2 = Records()
    policy2 = Policy()
    pdict = Calculator.read_json_param_files(reform_filename=REFORM,
                                             assump_filename=None)
    policy2.implement_reform(pdict['policy'])
    calc2 = Calculator(policy=policy2, records=records2, verbose=False)

    # advance calc1 and calc2 to TAXYEAR and conduct tax calculations
    while calc1.current_year < taxyear:
        calc1.increment_year()
        calc2.increment_year()
    calc1.calc_all()
    calc2.calc_all()

    # write calc1 results and write calc2 vs calc1 results
    sys.stdout.write('==> CALC1 in {}:\n'.format(taxyear))
    write_tables(calc1, None)
    sys.stdout.write('\n==> CALC2 vs CALC1 in {}:\n'.format(taxyear))
    write_tables(calc2, calc1)

    # create calc3, reform Calculator object with
    #               static response assumptions and
    #               all earnings-shifting in TAXYEAR
    # create calc3p for taxpayer earnings shifting and
    # create calc3b for both taxpayer and spouse earnings shifting
    pdict = Calculator.read_json_param_files(reform_filename=REFORM,
                                             assump_filename=None)
    records3p = Records()
    policy3p = Policy()
    policy3p.implement_reform(pdict['policy'])
    calc3p = Calculator(policy=policy3p, records=records3p, verbose=False)
    while calc3p.current_year < taxyear:
        calc3p.increment_year()
    calc3p.records = all_earnings_shift(calc3p.records, param,
                                        taxpayer_only=True)
    calc3p.calc_all()
    records3b = Records()
    policy3b = Policy()
    policy3b.implement_reform(pdict['policy'])
    calc3b = Calculator(policy=policy3b, records=records3b, verbose=False)
    while calc3b.current_year < taxyear:
        calc3b.increment_year()
    calc3b.records = all_earnings_shift(calc3b.records, param,
                                        taxpayer_only=False)
    calc3b.calc_all()

    # write calc3 vs calc2 results
    sys.stdout.write('\n==> CALC3 vs CALC2 in {}:\n'.format(taxyear))
    write_tables(calc3b, calc2)

    # create calc4, reform Calculator object with
    #               static response assumptions and
    #               some earnings-shifting in TAXYEAR based on
    #               the shifting probabilities generated by the
    #               probability function below
    records4 = Records()
    policy4 = Policy()
    pdict = Calculator.read_json_param_files(reform_filename=REFORM,
                                             assump_filename=None)
    policy4.implement_reform(pdict['policy'])
    calc4 = Calculator(policy=policy4, records=records4, verbose=False)

    # advance calc4 to TAXYEAR, do shifting, and conduct tax calculations
    while calc4.current_year < taxyear:
        calc4.increment_year()
    calc4.records = some_earnings_shift(calc4.records, calc3p.records,
                                        calc3b.records, calc2.records,
                                        param)
    calc4.calc_all()

    # write calc4 vs calc2 results
    sys.stdout.write('\n==> CALC4 vs CALC2 in {}:\n'.format(taxyear))
    write_tables(calc4, calc2)

    # write calc4 vs calc1 results
    sys.stdout.write('\n==> CALC4 vs CALC1 in {}:\n'.format(taxyear))
    write_tables(calc4, calc1)

    # normal return code
    return 0
# end of main function


def get_cli_parameters():
    """
    Return CLI arguments in parameter dictionary.
    """
    # parse command-line arguments
    usage_str = ('python earnings_shifting.py {}'.format(
        'YEAR WAGE_AMT MIN_WAGE_FRAC MIN_EARNINGS MIN_SAVINGS SHIFT_PROB'))
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Writes to stdout the tax revenue implications of '
                     'the creation of personal LLCs (to shift earnings '
                     'into pass-through income) under the '
                     'Trump2017.json tax reform.'))
    parser.add_argument('YEAR', nargs='?',
                        help=('YEAR is calendar year for which taxes '
                              'are computed.'),
                        type=int,
                        default=0)
    parser.add_argument('WAGE_AMT', nargs='?',
                        help=('WAGE_AMT is amount of individual annual '
                              'earnings voluntarily not converted into '
                              'pass-through income in order to take '
                              'advantage of low regular tax rates.'),
                        type=float,
                        default=-9.9)
    parser.add_argument('MIN_WAGE_FRAC', nargs='?',
                        help=('MIN_WAGE_FRAC is the minimum fraction of '
                              'shifted earnings that are paid as wages '
                              'rather than pass-through income by each '
                              'new personal LLC; zero specifies no '
                              'regulatory constraint.'),
                        type=float,
                        default=9.9)
    parser.add_argument('MIN_EARNINGS', nargs='?',
                        help=('MIN_EARNINGS is minimum individual annual '
                              'earnings for earnings-shifting to occur with '
                              'probability SHIFT_PROB.'),
                        type=float,
                        default=-9.9)
    parser.add_argument('MIN_SAVINGS', nargs='?',
                        help=('MIN_SAVINGS is minimum individual annual '
                              'income+payroll tax savings from '
                              'earnings-shifting for earnings-shifting to '
                              'occur with probability SHIFT_PROB.'),
                        type=float,
                        default=-9.9)
    parser.add_argument('SHIFT_PROB', nargs='?',
                        help=('SHIFT_PROB is probability of '
                              'earnings-shifting for individuals that '
                              'have at least MIN_EARNINGS and at least '
                              'MIN_SAVINGS from shifting earnings; '
                              'probability is zero for individuals '
                              'below MIN_EARNINGS or below MIN_SAVINGS.'),
                        type=float,
                        default=9.9)
    args = parser.parse_args()
    # store args in returned dictionary
    param = dict()
    param['year'] = args.YEAR
    param['wage_amt'] = args.WAGE_AMT
    param['min_wage_frac'] = args.MIN_WAGE_FRAC
    param['min_earnings'] = args.MIN_EARNINGS
    param['min_savings'] = args.MIN_SAVINGS
    param['shift_prob'] = args.SHIFT_PROB
    return param


def write_parameters(param):
    """
    Write parameter values to stdout.
    """
    pnames = ('PARAMS: YEAR WAGE_AMT MIN_WAGE_FRAC '
              'MIN_EARNINGS MIN_SAVINGS SHIFT_PROB\n')
    sys.stdout.write(pnames)
    frmt = 'PARAMS: {:4d} {:8.2f} {:12.3f} {:12.2f} {:11.2f} {:10.3f}\n'
    sys.stdout.write(frmt.format(param['year'],
                                 param['wage_amt'],
                                 param['min_wage_frac'],
                                 param['min_earnings'],
                                 param['min_savings'],
                                 param['shift_prob']))


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
    dfx = add_quantile_bins(dfx, 'expanded_income', 10,
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


def shift_earnings(recs, does_p, does_s, param):
    """
    Return Records object with wages and salaries in recs shifted to
    corporate pass-through self-employment earnings for taxpayers in
    filing units with True in does_p array and for spouses in filing
    units with True in does_s array.
    """
    wage_amt = param['wage_amt']
    # shift earnings of taxpayers
    vol_residual = np.where(recs.e00200p < wage_amt, recs.e00200p, wage_amt)
    required = recs.e00200p * param['min_wage_frac']
    residual = np.where(vol_residual < required, required, vol_residual)
    shifted = recs.e00200p - residual
    recs.e02000 = np.where(does_p, recs.e02000 + shifted, recs.e02000)
    recs.e26270 = np.where(does_p, recs.e26270 + shifted, recs.e26270)
    recs.k1bx14p = np.where(does_p, recs.k1bx14p + shifted, recs.k1bx14p)
    recs.e00200 = np.where(does_p, recs.e00200 - shifted, recs.e00200)
    recs.e00200p = np.where(does_p, recs.e00200p - shifted, recs.e00200p)
    # shift earnings of spouses
    vol_residual = np.where(recs.e00200s < wage_amt, recs.e00200s, wage_amt)
    required = recs.e00200s * param['min_wage_frac']
    residual = np.where(vol_residual < required, required, vol_residual)
    shifted = recs.e00200s - residual
    recs.e02000 = np.where(does_s, recs.e02000 + shifted, recs.e02000)
    recs.e26270 = np.where(does_s, recs.e26270 + shifted, recs.e26270)
    recs.k1bx14s = np.where(does_s, recs.k1bx14s + shifted, recs.k1bx14s)
    recs.e00200 = np.where(does_s, recs.e00200 - shifted, recs.e00200)
    recs.e00200s = np.where(does_s, recs.e00200s - shifted, recs.e00200s)
    return recs


def all_earnings_shift(recs, param, taxpayer_only):
    """
    Return Records object with wages and salaries in recs shifted to
    corporate pass-through self-employment earnings.
    Note that the k1bx14 amounts are included in the e26270 amount, which is,
    in turn, included in the e02000 amount.
    Earnings shift is done for taxpayers only when taxpayer_only=True and
    done for BOTH taxpayers and spouses when taxpayer_only=False.
    In all cases, individuals voluntarily keep as much as param['wage_amt']
    in wages and salaries in order to take advantage of low tax rates on
    small amounts of earnings.
    """
    dump = False
    cols = ['s006', 'e00200', 'e00200p', 'e00200s', 'e02000', 'e26270',
            'k1bx14p', 'k1bx14s']
    if dump:
        data = [getattr(recs, col) for col in cols]
        pdf = pd.DataFrame(data=np.column_stack(data), columns=cols)
        msg = 'DUMP-BEFORE-SHIFT {} {}\n'
        for col in cols:
            sys.stdout.write(msg.format(col, weighted_sum(pdf, col)))
    # do earnnigs shift for all taxpayers
    does = recs.MARS > 0  # True for every filing unit
    noes = recs.MARS < 0  # False for every filing unit
    recs = shift_earnings(recs, does, noes, param)
    if taxpayer_only is False:
        # also do earnnigs shift for all spouses
        recs = shift_earnings(recs, noes, does, param)
    if dump:
        data = [getattr(recs, col) for col in cols]
        pdf = pd.DataFrame(data=np.column_stack(data), columns=cols)
        msg = 'DUMP--AFTER-SHIFT {} {}\n'
        for col in cols:
            sys.stdout.write(msg.format(col, weighted_sum(pdf, col)))
    return recs


def some_earnings_shift(recs, recs_all_p, recs_all_b, recs_noes, param):
    """
    Return Records object with some wages and salaries in recs shifted to
    corporate pass-through self-employment earnings depending on tax savings
    of all shifting (recs_all_p and recs_all_b) relative to no earnings
    shifting (recs_noes).  The recs_all_p records object contains results
    when all taxpayers, but not spouses in MARS==2 filing units, all do
    earnings-shifting; the recs_all_b records object contains results
    when all taxpayers, and all spouses in MARS==2 filing units, all do
    earnings-shifting.
    Note that the k1bx14 amounts are included in the e26270 amount, which is,
    in turn, included in the e02000 amount.
    """
    # pylint: disable=too-many-locals
    urn_seed = 123456
    np.random.seed(urn_seed)  # pylint: disable=no-member
    # first handle taxpayer decision to shift earnings
    potential_savings = recs_noes.combined - recs_all_p.combined
    prob = probability(param, recs.e00200p, potential_savings)
    urn = np.random.random(recs.MARS.shape)
    does = urn < prob
    numshifters_p = recs_noes.s006[does].sum()
    ernshifters_p = (recs_noes.s006[does] * recs_noes.e00200p[does]).sum()
    noes = recs.MARS < 0  # False for all filing units
    recs = shift_earnings(recs, does, noes, param)
    # then handle spouse (in MARS==2 filing units) decision to shift earnings
    potential_savings = recs_all_p.combined - recs_all_b.combined
    prob = probability(param, recs.e00200s, potential_savings)
    urn = np.random.random(recs.MARS.shape)
    does = urn < prob
    numshifters_s = recs.s006[does].sum()
    ernshifters_s = (recs_noes.s006[does] * recs_noes.e00200s[does]).sum()
    recs = shift_earnings(recs, noes, does, param)
    # write number of shifters and earnings shifted for taxpayers and spouses
    sys.stdout.write('\n')
    msg = '==> CALC4 in {}   number of taxpayer shifters (#m): {:.3f}\n'
    sys.stdout.write(msg.format(param['year'], numshifters_p * 1e-6))
    msg = '==> CALC4 in {} earnings of taxpayer shifters ($b): {:.3f}\n'
    sys.stdout.write(msg.format(param['year'], ernshifters_p * 1e-9))
    msg = '==> CALC4 in {}   number of   spouse shifters (#m): {:.3f}\n'
    sys.stdout.write(msg.format(param['year'], numshifters_s * 1e-6))
    msg = '==> CALC4 in {} earnings of   spouse shifters ($b): {:.3f}\n'
    sys.stdout.write(msg.format(param['year'], ernshifters_s * 1e-9))
    # finally return modified Records object, recs
    return recs


def probability(param, indiv_earnings, tax_savings):
    """
    Return array containing earnings-shifting probability for each individual.
    """
    # pylint: disable=no-member
    prob = np.where(np.logical_and(indiv_earnings >= param['min_earnings'],
                                   tax_savings >= param['min_savings']),
                    param['shift_prob'], 0.0)
    return prob


if __name__ == '__main__':
    sys.exit(main())
