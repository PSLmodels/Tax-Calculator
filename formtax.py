"""
CLI to taxcalc/filings
"""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from taxcalc.filings import USFilingCollection
from taxcalc.utils import get_tc_version, resolve_paths_with_cwd


DESCRIPTION = """
Provides tasks to run Tax Calculator using JSON tax forms as Records data:

example
Write an example of tax form files to DST.

calc
Read all tax form files in SRC recursively.
Read the taxcalc config files POLICY and ECON or use defaults.
Calculate taxes for each year.
Write the completed forms to DST.
Print the total tax liabilities.

compare
Read all tax form files in SRC recursively.
Read the taxcalc config files POLICY and ECON or use defaults.
Read the taxcalc config files POLICY-BASE and ECON-BASE or use defaults.
Calculate taxes for each year and config set.
Write the delta as form files to DST.
Print the total tax liability difference.
"""
VERSION = get_tc_version()


def main():
    """
    Parses provided args and runs specified task
    """

    parser = ArgumentParser(
        description=DESCRIPTION,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument(
        'task',
        choices=['calc', 'compare', 'example'],
        help='the task to run, see above',
        metavar='TASK',
    )
    parser.add_argument(
        '-s', '--src',
        help='path to input dir, defaults to cwd',
        default='.',
    )
    parser.add_argument(
        '-d', '--dst',
        help='path to output dir, defaults to cwd',
        default='.',
    )
    parser.add_argument(
        '-p', '--policy',
        help='path to a policy config file, defaults to baseline',
    )
    parser.add_argument(
        '-e', '--econ',
        help='path to an economic factors config file, defaults to baseline',
    )
    parser.add_argument(
        '-pb', '--policy-base',
        help='path to policy config to compare against, defaults to baseline',
    )
    parser.add_argument(
        '-eb', '--econ-base',
        help='path to econ config to compare against, defaults to baseline',
    )

    args = parser.parse_args()
    task = args.task
    src, dst, policy, econ, policy_b, econ_b = resolve_paths_with_cwd([
        args.src, args.dst,
        args.policy, args.econ,
        args.policy_base, args.econ_base
    ])

    if task == 'calc':
        USFilingCollection\
            .from_dir(src)\
            .calc_all(policy=policy, econ=econ, verbose=True)\
            .to_dir(dst)

    elif task == 'compare':
        calc_a = USFilingCollection\
            .from_dir(src)\
            .calc_all(policy=policy, econ=econ, verbose=True)
        calc_b = USFilingCollection\
            .from_dir(src)\
            .calc_all(policy=policy_b, econ=econ_b, verbose=True)
        calc_a.compare_to(calc_b).to_dir(dst)

    elif task == 'example':
        USFilingCollection.example(2015, all_inputs=True).to_dir(dst)

    # return exit code OK
    return 0

if __name__ == '__main__':
    sys.exit(main())
