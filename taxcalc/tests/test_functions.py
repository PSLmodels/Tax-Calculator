"""
Tests for Tax-Calculator functions.py logic.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_functions.py
# pylint --disable=locally-disabled test_functions.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
import re
from taxcalc import IncomeTaxIO  # pylint: disable=import-error
from io import StringIO
import pandas as pd


def test_function_args_usage():
    """
    Checks each function argument in functions.py for use in its function body.
    """
    cur_path = os.path.abspath(os.path.dirname(__file__))
    funcfilename = os.path.join(cur_path, '..', 'functions.py')
    with open(funcfilename, 'r') as funcfile:
        fcontent = funcfile.read()
    fcontent = re.sub('#.*', '', fcontent)  # remove all '#...' comments
    fcontent = re.sub('\n', ' ', fcontent)  # replace EOL character with space
    funcs = fcontent.split('def ')  # list of function text
    for func in funcs[1:]:  # skip first item in list, which is imports, etc.
        fcode = func.split('return ')[0]  # fcode is between def and return
        match = re.search(r'^(.+?)\((.*?)\):(.*)$', fcode)
        if match is None:
            msg = ('Could not find function name, arguments, '
                   'and code portions in the following text:')
            line = '====================================================='
            sys.stdout.write('{}\n{}\n{}\n{}\n'.format(msg, line, fcode, line))
            assert False
        else:
            fname = match.group(1)
            fargs = match.group(2).split(',')  # list of function arguments
            fbody = match.group(3)
        for farg in fargs:
            arg = farg.strip()
            if fbody.find(arg) < 0:
                msg = '{} function argument {} never used\n'.format(fname, arg)
                sys.stdout.write(msg)
                assert 'argument' == 'UNUSED'


def test_1():
    """
    Test calculation of AGI adjustment for half of Self-Employment Tax,
    which is the FICA payroll tax on self-employment income.
    """
    agi_ovar_num = 10
    # specify a reform that simplifies the hand calculations
    mte = 100000  # lower than current-law to simplify hand calculations
    ssr = 0.124  # current law OASDI ee+er payroll tax rate
    mrr = 0.029  # current law HI ee+er payroll tax rate
    reform = {
        2015: {
            '_SS_Earnings_c': [mte],
            '_FICA_ss_trt': [ssr],
            '_FICA_mc_trt': [mrr]
        }
    }
    funit = (
        u'RECID,MARS,e00200,e00200p,e00900,e00900p,e00900s\n'
        u'1,    2,   200000, 200000,200000,      0, 200000\n'
        u'2,    1,   100000, 100000,200000, 200000,      0\n'
    )
    # ==== Filing unit with RECID=1:
    # The expected AGI for this filing unit is $400,000 minus half of
    # the spouse's Self-Employment Tax (SET), which represents the
    # "employer share" of the SET.  The spouse pays OASDI SET on only
    # $100,000 of self-employment income, which implies a tax of
    # $12,400.  The spouse also pays HI SET on 0.9235 * 200000 * 0.029,
    # which implies a tax of $5,356.30.  So, the spouse's total SET is
    # the sum of the two, which equals $17,756.30.
    # The SET AGI adjustment is one-half of that amount, which is $8,878.15.
    # So, filing unit's AGI is $400,000 less this, which is $391,121.85.
    expected_agi_1 = '391121.85'
    # ==== Filing unit with RECID=2:
    # The expected AGI for this filing unit is $300,000 minus half of
    # the individual's Self-Employment Tax (SET), which represents the
    # "employer share" of the SET.  The individual pays no OASDI SET
    # because wage and salary income was already at the MTE.  So, the
    # only SET the individual pays is for HI, which is a tax equal to
    # 0.9235 * 200000 * 0.029, or $5,356.30.  One half of that amount
    # is $2,678.15, which implies the AGI is $297,321.85.
    expected_agi_2 = '297321.85'
    input_dataframe = pd.read_csv(StringIO(funit))
    inctax = IncomeTaxIO(input_data=input_dataframe,
                         tax_year=2015,
                         policy_reform=reform,
                         exact_calculations=False,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    output_lines_list = output.split('\n')
    output_vars_list = output_lines_list[0].split()
    agi = output_vars_list[agi_ovar_num - 1]
    assert agi == expected_agi_1
    output_vars_list = output_lines_list[1].split()
    agi = output_vars_list[agi_ovar_num - 1]
    assert agi == expected_agi_2


def test_2():
    """
    Test calculation of Additional Child Tax Credit (CTC) when at least one
    of taxpayer and spouse have wage-and-salary income above the FICA maximum
    taxable earnings.
    """
    ctc_ovar_num = 22
    actc_ovar_num = 23
    # specify a contrived example -- implausible policy and a large family ---
    # in order to make the hand calculations easier
    actc_thd = 35000
    mte = 53000
    reform = {
        2015: {
            '_ACTC_Income_thd': [actc_thd],
            '_SS_Earnings_c': [mte],
        }
    }
    funit = (
        u'RECID,MARS,XTOT,n24,e00200,e00200p\n'
        u'1,    2,   9,     7, 60000,  60000\n'
    )
    # The maximum CTC in the above situation is $7,000, but only $1,140 can
    # be paid as a nonrefundable CTC.  Because the family has 3+ kids, they
    # can compute their refundable CTC amount in a way that uses the
    # employee share of FICA taxes paid on wage-and-salary income.  In this
    # case, the employee share is the sum of HI FICA (0.0145*60000) $870 and
    # OASDI FICA (0.062*53000) $3,286, which is $4,156, which is larger than
    # the $3,700 available to smaller families.
    expected_ctc = '1140.00'
    expected_actc = '4156.00'
    input_dataframe = pd.read_csv(StringIO(funit))
    inctax = IncomeTaxIO(input_data=input_dataframe,
                         tax_year=2015,
                         policy_reform=reform,
                         exact_calculations=False,
                         blowup_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    output_vars_list = output.split()
    ctc = output_vars_list[ctc_ovar_num - 1]
    actc = output_vars_list[actc_ovar_num - 1]
    assert ctc == expected_ctc
    assert actc == expected_actc
