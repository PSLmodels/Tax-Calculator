"""
Python script that generates marginal-tax-rate results with and without
consumption responses produced by the Tax-Calculator via the taxcalc
package running on this computer.  These results can be compared with
hand-generated results produced by TaxBrain running in the cloud.

COMMAND-LINE USAGE: python consumption.py --help

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 consumption.py
# pylint --disable=locally-disabled --extension-pkg-whitelist=numpy consump.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import os
import sys
import numpy as np
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
PUFCSV_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, Consumption


def main(mpc_e17500, mpc_e18400, mpc_e19800, mpc_e20400):
    """
    Highest-level logic of consumption.py script that produces Tax-Calculator
    marginal-tax-rate results running the taxcalc package on this computer.
    """
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    if not os.path.isfile(PUFCSV_PATH):
        sys.stderr.write('ERROR: file {} does not exist\n'.format(PUFCSV_PATH))
        return 1
    cyr = 2014
    # compute mtr under current-law policy with no consumption response
    recs0 = Records(data=PUFCSV_PATH)
    calc0 = Calculator(policy=Policy(), records=recs0,
                       consumption=None, verbose=False)
    calc0.advance_to_year(cyr)
    wghts = calc0.records.s006
    (mtr0_ptax, mtr0_itax, _) = calc0.mtr(income_type_str='e00200p',
                                          wrt_full_compensation=False)
    # compute mtr under current-law policy with specified consumption response
    consump = Consumption()
    consump_mpc = {cyr: {'_MPC_e17500': [mpc_e17500],
                         '_MPC_e18400': [mpc_e18400],
                         '_MPC_e19800': [mpc_e19800],
                         '_MPC_e20400': [mpc_e20400]}}
    consump.update_consumption(consump_mpc)
    recs1 = Records(data=PUFCSV_PATH)
    calc1 = Calculator(policy=Policy(), records=recs1,
                       consumption=consump, verbose=False)
    calc1.advance_to_year(cyr)
    assert calc1.consumption.current_year == cyr
    (mtr1_ptax, mtr1_itax, _) = calc1.mtr(income_type_str='e00200p',
                                          wrt_full_compensation=False)
    # compare unweighted mtr results with and without consumption response
    epsilon = 1.0e-6  # this would represent a mtr of 0.0001 percent
    assert np.allclose(mtr1_ptax, mtr0_ptax, atol=epsilon, rtol=0.0)
    mtr_raw_diff = mtr1_itax - mtr0_itax
    mtr1_itax = np.where(np.logical_and(mtr_raw_diff > 0.0,
                                        mtr_raw_diff < epsilon),
                         mtr0_itax, mtr1_itax)  # zero out small positive diffs
    num_total = mtr1_itax.size
    num_increases = np.sum(np.greater(mtr1_itax, mtr0_itax))
    num_decreases = np.sum(np.less(mtr1_itax, mtr0_itax))
    num_nochanges = num_total - num_increases - num_decreases
    res = 'unweighted_num_of_mtr_{}_with_consump_response= {:6d} ({:5.1f}%)\n'
    sys.stdout.write(res.format('increases', num_increases,
                                (100.0 * num_increases) / num_total))
    sys.stdout.write(res.format('decreases', num_decreases,
                                (100.0 * num_decreases) / num_total))
    sys.stdout.write(res.format('nochanges', num_nochanges,
                                (100.0 * num_nochanges) / num_total))
    sys.stdout.write(res.format('all_units', num_total, 100.0))
    # compute average size of decreases in mtr_itax
    mtr_pre = mtr0_itax[mtr1_itax < mtr0_itax]
    assert mtr_pre.size == num_decreases
    avg_pre = np.mean(mtr_pre)
    res = 'unweighted_abs_mean_no_c_resp(for_decreases)mtr_itax= {:.4f}\n'
    sys.stdout.write(res.format(avg_pre))
    mtr_diff = mtr1_itax - mtr0_itax
    mtr_neg = mtr_diff[mtr_diff < 0.0]
    assert mtr_neg.size == num_decreases
    avg_neg = np.mean(mtr_neg)
    assert avg_neg < 0.0
    res = 'unweighted_abs_mean_change(for_decreases)in_mtr_itax= {:.4f}\n'
    sys.stdout.write(res.format(-avg_neg))
    res = '   ratio_of_abs_change_in_mtr_itax_and_no_c_resp_mtr_itax= {:.3f}\n'
    sys.stdout.write(res.format(-avg_neg / avg_pre))
    # compare weighted mtr results with and without consumption response
    wghts_pre = wghts[mtr1_itax < mtr0_itax]
    assert wghts_pre.size == num_decreases
    res = 'weighted_percent_of_units_with_mtr_decrease= {:.1f}%\n'
    frac = wghts_pre.sum() / wghts.sum()
    sys.stdout.write(res.format(100.0 * frac))
    res = '   ratio_of_abs_change_in_mtr_itax_and_no_c_resp_mtr_itax= {:.3f}\n'
    w_avg_pre = np.mean((mtr_pre * wghts_pre).sum() / wghts_pre.sum())
    w_avg_neg = np.mean((mtr_neg * wghts_pre).sum() / wghts_pre.sum())
    sys.stdout.write(res.format(-w_avg_neg / w_avg_pre))
    # return no-error exit code
    return 0
# end of main function code


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python consumption.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=('Writes to stdout marginal-tax-rate results --- both '
                     'with and\nwithout consumption responses expressed in '
                     'terms of marginal\npropensities to consume (MPC) on '
                     'itemized-deduction expenses\n--- produced by '
                     'Tax-Calculator via the taxcalc package running\non '
                     'the computer.  These results can be compared with '
                     'hand-\ngenerated results produced by TaxBrain running '
                     'in the cloud.')
    )
    PARSER.add_argument('MPC_MEDS', type=float,
                        help=('MPC for e17500 consumption'))
    PARSER.add_argument('MPC_SLTX', type=float,
                        help=('MPC for e18400 consumption'))
    PARSER.add_argument('MPC_CHAR', type=float,
                        help=('MPC for e19800 consumption'))
    PARSER.add_argument('MPC_MISC', type=float,
                        help=('MPC for e20400 consumption'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.MPC_MEDS, ARGS.MPC_SLTX, ARGS.MPC_CHAR, ARGS.MPC_MISC))
