"""
Command-line interface (CLI) to Tax-Calculator,
which can be accessed as 'tc' from an installed taxcalc conda package.
"""
# CODING-STYLE CHECKS:
# pep8 tc.py
# pylint --disable=locally-disabled tc.py

import os
import sys
import argparse
import difflib
import taxcalc as tc


TEST_INPUT_FILENAME = 'test.csv'
TEST_TAXYEAR = 2018


def cli_tc_main():
    """
    Contains command-line interface (CLI) to Tax-Calculator TaxCalcIO class.
    """
    # pylint: disable=too-many-statements
    # parse command-line arguments:
    usage_str = 'tc INPUT TAXYEAR {}{}{}{}{}{}{}'.format(
        '[--baseline BASELINE]\n',
        '          ',
        '[--reform REFORM] [--assump  ASSUMP]\n',
        '          ',
        '[--exact] [--tables] [--graphs] [--ceeu] [--dump] [--sqldb]\n',
        '          ',
        '[--outdir] [--test] [--version] [--help]')
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Writes to a file the federal income and payroll tax '
                     'OUTPUT for each filing unit specified in the INPUT '
                     'file, with the OUTPUT computed from the INPUT for the '
                     'TAXYEAR using Tax-Calculator. The OUTPUT file is a '
                     'CSV-formatted file that contains tax information for '
                     'each INPUT filing unit under the reform(s).'))
    parser.add_argument('INPUT', nargs='?',
                        help=('INPUT is name of CSV-formatted file that '
                              'contains for each filing unit variables used '
                              'to compute taxes for TAXYEAR. Specifying '
                              '"cps.csv" uses CPS input files included in '
                              'the taxcalc package.'),
                        default='')
    parser.add_argument('TAXYEAR', nargs='?',
                        help=('TAXYEAR is calendar year for which taxes '
                              'are computed.'),
                        type=int,
                        default=0)
    parser.add_argument('--baseline',
                        help=('BASELINE is name of optional JSON reform file. '
                              'No --baseline implies baseline policy is '
                              'current-law policy.'),
                        default=None)
    parser.add_argument('--reform',
                        help=('REFORM is name of optional JSON reform file. '
                              'A compound reform can be specified using two '
                              'file names separated by a plus (+) character. '
                              'No --reform implies a "null" reform (that is, '
                              'current-law policy).'),
                        default=None)
    parser.add_argument('--assump',
                        help=('ASSUMP is name of optional JSON economic '
                              'assumptions file.  No --assump implies use '
                              'of no customized assumptions.'),
                        default=None)
    parser.add_argument('--exact',
                        help=('optional flag that suppresses the smoothing of '
                              '"stair-step" provisions in the tax law that '
                              'complicate marginal-tax-rate calculations.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--tables',
                        help=('optional flag that causes distributional '
                              'tables to be written to a text file.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--graphs',
                        help=('optional flag that causes graphs to be written '
                              'to HTML files for viewing in browser.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--ceeu',
                        help=('optional flag that causes normative welfare '
                              'statistics, including certainty-equivalent '
                              'expected-utility (ceeu) of after-tax income '
                              'values for different '
                              'constant-relative-risk-aversion parameter '
                              'values, to be written to stdout.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--dump',
                        help=('optional flag that causes OUTPUT to contain '
                              'all INPUT variables (extrapolated to TAXYEAR) '
                              'and all calculated tax variables for the '
                              'reform, where all the variables are named '
                              'using their internal Tax-Calculator names. '
                              'No --dump option implies OUTPUT contains '
                              'minimal tax output for the reform.  NOTE: '
                              'use the --dvars option to point to a file '
                              'containing a custom set of dump variables.'
                              ''),
                        default=False,
                        action="store_true")
    parser.add_argument('--dvars',
                        help=('DVARS is name of optional file containing a '
                              'space-delimited list of variables to include '
                              'in a partial dump OUTPUT file.  No --dvars '
                              'implies a full dump containing all variables.'),
                        default=None)
    parser.add_argument('--sqldb',
                        help=('optional flag that writes SQLite database '
                              'with dump table containing same output as '
                              'produced by --dump option.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--outdir',
                        help=('OUTDIR is name of optional output directory '
                              'in which all output files are written. '
                              'No --outdir implies output files are written '
                              'in the current directory.'),
                        default=None)
    parser.add_argument('--test',
                        help=('optional flag that conducts installation '
                              'test, writes test result to stdout, '
                              'and quits.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--version',
                        help=('optional flag that writes Tax-Calculator '
                              'release version to stdout and quits.'),
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    # show Tsx-Calculator version and quit if --version option specified
    if args.version:
        sys.stdout.write('Tax-Calculator {}\n'.format(tc.__version__))
        return 0
    # write test input and expected output files if --test option specified
    if args.test:
        _write_expected_test_output()
        inputfn = TEST_INPUT_FILENAME
        taxyear = TEST_TAXYEAR
    else:
        inputfn = args.INPUT
        taxyear = args.TAXYEAR
    # instantiate taxcalcio object and do tax analysis
    tcio = tc.TaxCalcIO(input_data=inputfn, tax_year=taxyear,
                        baseline=args.baseline,
                        reform=args.reform, assump=args.assump,
                        outdir=args.outdir)
    if tcio.errmsg:
        sys.stderr.write(tcio.errmsg)
        sys.stderr.write('USAGE: tc --help\n')
        return 1
    aging = inputfn.endswith('puf.csv') or inputfn.endswith('cps.csv')
    tcio.init(input_data=inputfn, tax_year=taxyear,
              baseline=args.baseline,
              reform=args.reform, assump=args.assump,
              growdiff_response=None,
              aging_input_data=aging,
              exact_calculations=args.exact)
    if tcio.errmsg:
        sys.stderr.write(tcio.errmsg)
        sys.stderr.write('USAGE: tc --help\n')
        return 1
    dumpvar_set = None
    if args.dvars and (args.dump or args.sqldb):
        if os.path.exists(args.dvars):
            with open(args.dvars) as dfile:
                dump_vars_str = dfile.read()
            dumpvar_set = tcio.custom_dump_variables(dump_vars_str)
            if tcio.errmsg:
                sys.stderr.write(tcio.errmsg)
                sys.stderr.write('USAGE: tc --help\n')
                return 1
        else:
            msg = 'ERROR: DVARS file {} does not exist\n'
            sys.stderr.write(msg.format(args.dvars))
            sys.stderr.write('USAGE: tc --help\n')
            return 1
    tcio.analyze(writing_output_file=True,
                 output_tables=args.tables,
                 output_graphs=args.graphs,
                 output_ceeu=args.ceeu,
                 dump_varset=dumpvar_set,
                 output_dump=args.dump,
                 output_sqldb=args.sqldb)
    # compare test output with expected test output if --test option specified
    if args.test:
        retcode = _compare_test_output_files()
    else:
        retcode = 0
    # return exit code
    return retcode
# end of cli_tc_main function code


EXPECTED_TEST_OUTPUT_FILENAME = 'test-{}-out.csv'.format(str(TEST_TAXYEAR)[2:])
ACTUAL_TEST_OUTPUT_FILENAME = 'test-{}-#-#-#.csv'.format(str(TEST_TAXYEAR)[2:])


def _write_expected_test_output():
    """
    Private function that writes tc --test input and expected output files.
    """
    input_data = (
        'RECID,MARS,XTOT,EIC,e00200,e00200p,e00200s,p23250,e18400,e19800\n'
        '1,       2,   3,  1, 40000,  40000,      0,     0,  3000,  4000\n'
        '2,       2,   3,  1,200000, 200000,      0,     0, 15000, 20000\n'
    )
    with open(TEST_INPUT_FILENAME, 'w') as ifile:
        ifile.write(input_data)
    expected_output_data = (
        'RECID,YEAR,WEIGHT,INCTAX,LSTAX,PAYTAX\n'
        '1,2018,0.00,123.51,0.00,6120.00\n'
        '2,2018,0.00,28879.00,0.00,22167.43\n'
    )
    with open(EXPECTED_TEST_OUTPUT_FILENAME, 'w') as ofile:
        ofile.write(expected_output_data)


def _compare_test_output_files():
    """
    Private function that compares expected and actual tc --test output files;
    returns 0 if pass test, otherwise returns 1.
    """
    explines = open(EXPECTED_TEST_OUTPUT_FILENAME, 'U').readlines()
    actlines = open(ACTUAL_TEST_OUTPUT_FILENAME, 'U').readlines()
    if ''.join(explines) == ''.join(actlines):
        sys.stdout.write('PASSED TEST\n')
        retcode = 0
    else:
        retcode = 1
        sys.stdout.write('FAILED TEST\n')
        diff = difflib.unified_diff(explines, actlines,
                                    fromfile=EXPECTED_TEST_OUTPUT_FILENAME,
                                    tofile=ACTUAL_TEST_OUTPUT_FILENAME, n=0)
        sys.stdout.writelines(diff)
    return retcode


if __name__ == '__main__':
    sys.exit(cli_tc_main())
