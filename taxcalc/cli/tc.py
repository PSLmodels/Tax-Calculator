"""
Command-line interface (CLI) to Tax-Calculator,
which can be accessed as 'tc' from an installed taxcalc package.
"""
# CODING-STYLE CHECKS:
# pycodestyle tc.py
# pylint --disable=locally-disabled tc.py

import os
import sys
import time
import sqlite3
import argparse
import difflib
import taxcalc as tc


TEST_INPUT_FILENAME = 'test.csv'
TEST_TAXYEAR = 2018


def cli_tc_main():
    """
    Contains command-line interface (CLI) to Tax-Calculator TaxCalcIO class.
    """
    # pylint: disable=too-many-statements,too-many-branches
    # pylint: disable=too-many-return-statements,too-many-locals

    start_time = time.time()

    # parse command-line arguments:
    usage_str = 'tc INPUT TAXYEAR {}{}{}{}'.format(
        '[--help] [--numyears N]\n',
        (
            '          '
            '[--baseline BASELINE] [--reform REFORM] '
            '[--assump ASSUMP] [--exact]\n'
        ),
        (
            '          '
            '[--params] [--tables] [--graphs] '
            '[--dumpdb] [--dumpvars DUMPVARS]\n'
        ),
        (
            '          '
            '[--runid N] [--silent] [--test] [--version] [--usage]'
        )
    )
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Writes several output files computed from the INPUT '
                     'for the TAXYEAR using Tax-Calculator.'))
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
    parser.add_argument('--numyears', metavar='N',
                        help=('N is an integer indicating for how many '
                              'years taxes are calculated. No --numyears '
                              'implies calculations are done only for '
                              'TAXYEAR. N greater than one implies output '
                              'is written to separate files for each year '
                              'beginning with TAXYEAR.'),
                        type=int,
                        default=1)
    parser.add_argument('--baseline',
                        help=('BASELINE is name of optional JSON reform file. '
                              'A compound reform can be specified using 2+ '
                              'file names connected by plus (+) character(s). '
                              'No --baseline implies baseline policy is '
                              'current-law policy.'),
                        default=None)
    parser.add_argument('--reform',
                        help=('REFORM is name of optional JSON reform file. '
                              'A compound reform can be specified using 2+ '
                              'file names connected by plus (+) character(s). '
                              'No --reform implies reform policy is '
                              'current-law policy).'),
                        default=None)
    parser.add_argument('--assump',
                        help=('ASSUMP is name of optional JSON economic '
                              'assumptions file. No --assump implies use '
                              'of no customized assumptions.'),
                        default=None)
    parser.add_argument('--exact',
                        help=('optional flag that suppresses the smoothing of '
                              '"stair-step" provisions in the tax law that '
                              'complicate marginal-tax-rate calculations.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--params',
                        help=('optional flag that causes policy parameter '
                              'values for baseline and reform to be written '
                              'to separate text files.'),
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
    parser.add_argument('--dumpdb',
                        help=('optional flag that causes TAXYEAR variable '
                              'values for each tax-unit under both '
                              'baseline and reform policies to be written '
                              'to a SQLite database (where the variables '
                              'included in the database are controlled by '
                              'the --dumpvars option).'),
                        default=False,
                        action="store_true")
    parser.add_argument('--dumpvars',
                        help=('DUMPVARS is name of optional file containing a '
                              'space-delimited list of variables to include '
                              'in the dump database. No --dumpvars implies '
                              'a minimal set of variables.  Valid variable '
                              'names include all variables in the '
                              'records_variables.json file plus mtr_itax and '
                              'mtr_ptax (MTRs wrt taxpayer earnings).'),
                        default=None)
    parser.add_argument('--runid', metavar='N',
                        help=('N is a positive integer run id that is used '
                              'to construct simpler output file names. '
                              'No --runid implies legacy output file names '
                              'are used.'),
                        type=int,
                        default=0)
    parser.add_argument('--silent',
                        help=('optional flag that suppresses messages about '
                              'input and output actions.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--test',
                        help=('optional flag that conducts installation '
                              'test, writes test result to stdout, '
                              'and quits leaving the test-related files.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--version',
                        help=('optional flag that writes Tax-Calculator '
                              'release version to stdout and quits.'),
                        default=False,
                        action="store_true")
    parser.add_argument('--usage',
                        help=('optional flag that writes short usage '
                              'reminder to stdout and quits.'),
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    using_error_file = args.silent and args.runid != 0
    efilename = f'run{args.runid}.errors'
    # check Python version
    pyv = sys.version_info
    pymin = tc.__min_python3_version__
    pymax = tc.__max_python3_version__
    if pyv[0] != 3 or pyv[1] < pymin or pyv[1] > pymax:  # pragma: no cover
        pyreq = f'at least Python 3.{pymin} and at most Python 3.{pymax}'
        msg = (
            f'ERROR: Tax-Calculator requires {pyreq}\n'
            f'       but Python {pyv[0]}.{pyv[1]} is installed\n'
        )
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
        return 1
    # show Tax-Calculator version and quit if --version option is specified
    if args.version:
        pyver = f'Python 3.{pyv[1]}'
        sys.stdout.write(f'Tax-Calculator {tc.__version__} on {pyver}\n')
        return 0
    # show short usage reminder and quit if --usage option is specified
    if args.usage:
        sys.stdout.write(f'USAGE: {usage_str}\n')
        return 0
    # write test input and expected output files if --test option is specified
    if args.test:
        _write_test_files()
        inputfn = TEST_INPUT_FILENAME
        taxyear = TEST_TAXYEAR
        args.numyears = 1
        args.dumpdb = True
    else:
        inputfn = args.INPUT
        taxyear = args.TAXYEAR
    # check taxyear value
    if taxyear > tc.Policy.LAST_BUDGET_YEAR:
        msg = f'ERROR: TAXYEAR is greater than {tc.Policy.LAST_BUDGET_YEAR}\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    # check numyears value
    if args.numyears < 1:
        msg = 'ERROR: --numyears parameter N is less than one\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    max_numyears = tc.Policy.LAST_BUDGET_YEAR - taxyear + 1
    if args.numyears > max_numyears:
        msg = f'ERROR: --numyears parameter N is greater than {max_numyears}\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    # specify if aging input data
    aging_data = (
        inputfn.endswith('puf.csv') or
        inputfn.endswith('cps.csv') or
        inputfn.endswith('tmd.csv')
    )
    # check args.dumpdb and args.dumpvars consistency
    if not args.dumpdb and args.dumpvars:
        msg = 'ERROR: DUMPVARS file specified without --dumpdb option\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    # specify dumpvars_str from args.dumpvars file
    dumpvars_str = ''
    if args.dumpvars:
        if os.path.exists(args.dumpvars):
            with open(args.dumpvars, 'r', encoding='utf-8') as dfile:
                dumpvars_str = dfile.read()
        else:
            msg = f'ERROR: DUMPVARS file {args.dumpvars} does not exist\n'
            if using_error_file:
                with open(efilename, 'w', encoding='utf-8') as efile:
                    efile.write(msg)
            else:
                sys.stderr.write(msg)
                sys.stderr.write('USAGE: tc --help\n')
            return 1
    if args.runid < 0:
        msg = 'ERROR: --runid parameter N is less than zero\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    # do calculations for taxyear
    # ... initialize TaxCalcIO object for taxyear
    tcio = tc.TaxCalcIO(
        input_data=inputfn,
        tax_year=taxyear,
        baseline=args.baseline,
        reform=args.reform,
        assump=args.assump,
        runid=args.runid,
        silent=args.silent,
    )
    if tcio.errmsg:
        msg = tcio.errmsg
        if not msg.endswith('\n'):
            msg += '\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    tcio.init(
        input_data=inputfn,
        tax_year=taxyear,
        baseline=args.baseline,
        reform=args.reform,
        assump=args.assump,
        aging_input_data=aging_data,
        exact_calculations=args.exact,
    )
    if tcio.errmsg:
        msg = tcio.errmsg
        if not msg.endswith('\n'):
            msg += '\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    # ... conduct tax analysis for taxyear
    dumpvars_list = tcio.dump_variables(dumpvars_str)
    if tcio.errmsg:
        msg = tcio.errmsg
        if not msg.endswith('\n'):
            msg += '\n'
        if using_error_file:
            with open(efilename, 'w', encoding='utf-8') as efile:
                efile.write(msg)
        else:
            sys.stderr.write(msg)
            sys.stderr.write('USAGE: tc --help\n')
        return 1
    tcio.analyze(
        output_params=args.params,
        output_tables=args.tables,
        output_graphs=args.graphs,
        output_dump=args.dumpdb,
        dump_varlist=dumpvars_list,
    )
    # compare test output with expected test output if --test option specified
    if args.test:
        retcode = _compare_test_output_files()
        return retcode
    # quit if args.numyears is equal to one
    if args.numyears == 1:
        if not args.silent:
            print(  # pragma: no cover
                f'Execution time is {(time.time() - start_time):.1f} seconds'
            )
        return 0
    # analyze years after taxyear if args.numyears is greater than one
    for xyear in range(1, args.numyears):
        tcio.advance_to_year(taxyear + xyear, aging_data)
        tcio.analyze(
            output_params=args.params,
            output_tables=args.tables,
            output_graphs=args.graphs,
            output_dump=args.dumpdb,
            dump_varlist=dumpvars_list,
        )
    if not args.silent:
        print(  # pragma: no cover
            f'Execution time is {(time.time() - start_time):.1f} seconds'
        )
    return 0
# end of cli_tc_main function code


TEST_INPUT_DATA = (
    'RECID,MARS,XTOT,EIC,e00200,e00200p,e00200s,p23250,e18400,e19800,s006\n'
    '1,       2,   3,  1, 40000,  40000,      0,     0,  3000,  4000, 1e7\n'
    '2,       2,   3,  1,200000, 200000,      0,     0, 15000, 20000, 1e7\n'
)
EXPECTED_TEST_FILENAME = f'test-{str(TEST_TAXYEAR)[2:]}.exp'
EXPECTED_TEST_OUTPUT = (
    'id|itax\n'
    '1|131.88\n'
    '2|28879.00\n'
)
TEST_DUMPDB_FILENAME = f'test-{str(TEST_TAXYEAR)[2:]}-#-#-#.dumpdb'
TEST_SQLITE_QUERY = """
SELECT
  RECID           AS id,
  ROUND(iitax, 2) AS itax
FROM baseline;
"""
ACTUAL_TEST_FILENAME = f'test-{str(TEST_TAXYEAR)[2:]}.act'
TEST_TABULATE_FILENAME = 'test-tabulate.sql'
TEST_TABULATE_SQLCODE = (
    f'-- USAGE: sqlite3 {TEST_DUMPDB_FILENAME} < {TEST_TABULATE_FILENAME}\n'
    '\n'
    '-- sepecify base.income_group values\n'
    'UPDATE base SET income_group =\n'
    '  CASE  -- specify the income_group brackets as desired\n'
    '    WHEN expanded_income <   0.0   THEN 0\n'
    '    WHEN expanded_income <  50.0e3 THEN 1\n'
    '    WHEN expanded_income < 100.0e3 THEN 2\n'
    '    WHEN expanded_income < 500.0e3 THEN 3\n'
    '    WHEN expanded_income <   1.0e6 THEN 4\n'
    '    ELSE                                5\n'
    '  END;\n'
    '\n'
    '-- tabulate baseline and reform iitax for joint filers by income_group\n'
    '.separator "\t"\n'
    '.headers on\n'
    'SELECT\n'
    '  income_group                     AS g,\n'
    '  COUNT(*)                         AS units,\n'
    '  ROUND(SUM(b.iitax*s006)*1e-9, 3) AS b_iitax,\n'
    '  ROUND(SUM(r.iitax*s006)*1e-9, 3) AS r_iitax\n'
    'FROM base JOIN baseline AS b USING(RECID) JOIN reform AS r USING(RECID)\n'
    'WHERE MARS == 2\n'
    'GROUP BY income_group;\n'
    '.headers off\n'
    'SELECT\n'
    "  'A'                              AS g,\n"
    '  COUNT(*)                         AS units,\n'
    '  ROUND(SUM(b.iitax*s006)*1e-9, 3) AS b_iitax,\n'
    '  ROUND(SUM(r.iitax*s006)*1e-9, 3) AS r_iitax\n'
    'FROM base JOIN baseline AS b USING(RECID) JOIN reform AS r USING(RECID)\n'
    'WHERE MARS == 2;\n'
    '\n'
    '-- Documentation on the sqlite3 CLI program is available at\n'
    '-- https://sqlite.org/cli.html\n'
)


def _write_test_files():
    """
    Private function that writes tc --test input and expected output files.
    """
    with open(TEST_INPUT_FILENAME, 'w', encoding='utf-8') as ifile:
        ifile.write(TEST_INPUT_DATA)
    with open(EXPECTED_TEST_FILENAME, 'w', encoding='utf-8') as ofile:
        ofile.write(EXPECTED_TEST_OUTPUT)
    with open(TEST_TABULATE_FILENAME, 'w', encoding='utf-8') as tfile:
        tfile.write(TEST_TABULATE_SQLCODE)


def _compare_test_output_files():
    """
    Private function that compares expected and actual tc --test results;
    returns 0 if pass test, otherwise returns 1.
    """
    # use TEST_SQLITE_QUERY to extract results from TEST_DUMPDB_FILENAME
    with sqlite3.connect(TEST_DUMPDB_FILENAME) as connection:
        cursor = connection.cursor()
        cursor.execute(TEST_SQLITE_QUERY)
        results = cursor.fetchall()
        with open(ACTUAL_TEST_FILENAME, 'w', encoding='utf-8') as afile:
            afile.write('id|itax\n')
            for row in results:
                afile.write(f'{row[0]}|{row[1]:.2f}\n')
    # compare results in ACTUAL_TEST_FILENAME and in EXPECTED_TEST_FILENAME
    with open(EXPECTED_TEST_FILENAME, 'r', encoding='utf-8') as efile:
        explines = efile.readlines()
    with open(ACTUAL_TEST_FILENAME, 'r', encoding='utf-8') as afile:
        actlines = afile.readlines()
    if ''.join(explines) == ''.join(actlines):
        sys.stdout.write('PASSED TEST\n')
        retcode = 0
    else:
        retcode = 1
        sys.stdout.write('FAILED TEST\n')
        diff = difflib.unified_diff(explines, actlines,
                                    fromfile=EXPECTED_TEST_FILENAME,
                                    tofile=ACTUAL_TEST_FILENAME, n=0)
        sys.stdout.writelines(diff)
    return retcode


if __name__ == '__main__':
    sys.exit(cli_tc_main())
