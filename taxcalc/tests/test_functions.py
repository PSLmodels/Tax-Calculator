"""
Tests for Tax-Calculator functions.py logic.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_functions.py
# pylint --disable=locally-disabled test_functions.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import re
import ast
from io import StringIO
import tempfile
import six
import pytest
import pandas as pd
from taxcalc import IncomeTaxIO, Records  # pylint: disable=import-error


# for fixture args, pylint: disable=redefined-outer-name


class GetFuncDefs(ast.NodeVisitor):
    """
    Return information about each function defined in the functions.py file.
    """
    def __init__(self):
        """class constructor"""
        self.fname = ''
        self.fnames = list()  # function name (fname) list
        self.fargs = dict()  # lists of function arguments indexed by fname
        self.cvars = dict()  # lists of calc vars in function indexed by fname
        self.rvars = dict()  # lists of function return vars indexed by fname

    def visit_Module(self, node):  # pylint: disable=invalid-name
        """visit the one Module node"""
        self.generic_visit(node)
        return (self.fnames, self.fargs, self.cvars, self.rvars)

    def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
        """visit FunctionDef node"""
        self.fname = node.name
        self.fnames.append(self.fname)
        self.fargs[self.fname] = list()
        for anode in ast.iter_child_nodes(node.args):
            if six.PY3:
                self.fargs[self.fname].append(anode.arg)
            else:  # in Python 2 anode is a Name node
                self.fargs[self.fname].append(anode.id)
        self.cvars[self.fname] = list()
        for bodynode in node.body:
            if isinstance(bodynode, ast.Return):
                continue  # skip function's Return node
            for bnode in ast.walk(bodynode):
                if isinstance(bnode, ast.Name):
                    if isinstance(bnode.ctx, ast.Store):
                        if bnode.id not in self.cvars[self.fname]:
                            self.cvars[self.fname].append(bnode.id)
        self.generic_visit(node)

    def visit_Return(self, node):  # pylint: disable=invalid-name
        """visit Return node"""
        if isinstance(node.value, ast.Tuple):
            self.rvars[self.fname] = [r_v.id for r_v in node.value.elts]
        elif isinstance(node.value, ast.BinOp):
            self.rvars[self.fname] = []  # no vars returned; only an expression
        else:
            self.rvars[self.fname] = [node.value.id]
        self.generic_visit(node)


def test_calc_and_used_vars(tests_path):
    """
    Runs two kinds of tests on variables used in the functions.py file:

    (1) Checks that each var in Records.CALCULATED_VARS is actually calculated

    If test (1) fails, a variable in Records.CALCULATED_VARS was not
    calculated in any function in the functions.py file.  With the exception
    of a few variables listed in this test, all Records.CALCULATED_VARS
    must be calculated in the functions.py file.

    (2) Check that each variable that is calculated in a function and
    returned by that function is an argument of that function.
    """
    # pylint: disable=too-many-locals
    funcpath = os.path.join(tests_path, '..', 'functions.py')
    gfd = GetFuncDefs()
    fnames, fargs, cvars, rvars = gfd.visit(ast.parse(open(funcpath).read()))
    # Test (1):
    # .. create set of vars that are actually calculated in functions.py file
    all_cvars = set()
    for fname in fnames:
        if fname == 'BenefitSurtax':
            continue  # because BenefitSurtax is not really a function
        all_cvars.update(set(cvars[fname]))
    # .. add to all_cvars set some variables calculated in Records class
    all_cvars.update(set(['ID_Casualty_frt_in_pufcsv_year',
                          '_num', '_sep', '_exact']))
    # .. add to all_cvars set variables calculated only in *_code functions
    all_cvars.update(set([]))
    # .. check that each var in Records.CALCULATED_VARS is in the all_cvars set
    found_error1 = False
    if not Records.CALCULATED_VARS <= all_cvars:
        msg1 = 'all Records.CALCULATED_VARS not calculated in functions.py\n'
        for var in Records.CALCULATED_VARS - all_cvars:
            found_error1 = True
            msg1 += 'VAR NOT CALCULATED: {}\n'.format(var)
    # Test (2):
    faux_functions = ['EITCamount', 'ComputeBenefit',
                      'BenefitSurtax', 'BenefitLimitation',
                      'ALD_InvInc_ec_base_code', 'CTC_new_code']
    found_error2 = False
    msg2 = 'calculated & returned variables are not function arguments\n'
    for fname in fnames:
        if fname in faux_functions:
            continue  # because fname is not a genuine function
        crvars_set = set(cvars[fname]) & set(rvars[fname])
        if not crvars_set <= set(fargs[fname]):
            found_error2 = True
            for var in crvars_set - set(fargs[fname]):
                msg2 += 'FUNCTION,VARIABLE: {} {}\n'.format(fname, var)
    # Report errors for the two tests:
    if found_error1 and found_error2:
        raise ValueError('{}\n{}'.format(msg1, msg2))
    elif found_error1:
        raise ValueError(msg1)
    elif found_error2:
        raise ValueError(msg2)


def test_function_args_usage(tests_path):
    """
    Checks each function argument in functions.py for use in its function body.
    """
    funcfilename = os.path.join(tests_path, '..', 'functions.py')
    with open(funcfilename, 'r') as funcfile:
        fcontent = funcfile.read()
    fcontent = re.sub('#.*', '', fcontent)  # remove all '#...' comments
    fcontent = re.sub('\n', ' ', fcontent)  # replace EOL character with space
    funcs = fcontent.split('def ')  # list of function text
    msg = 'FUNCTION ARGUMENT(S) NEVER USED:\n'
    found_error = False
    for func in funcs[1:]:  # skip first item in list, which is imports, etc.
        fcode = func.split('return ')[0]  # fcode is between def and return
        match = re.search(r'^(.+?)\((.*?)\):(.*)$', fcode)
        if match is None:
            msg = ('Could not find function name, arguments, '
                   'and code portions in the following text:\n')
            msg += '--------------------------------------------------------\n'
            msg += '{}\n'.format(fcode)
            msg += '--------------------------------------------------------\n'
            raise ValueError(msg)
        else:
            fname = match.group(1)
            fargs = match.group(2).split(',')  # list of function arguments
            fbody = match.group(3)
        if fname == 'Taxes':
            continue  # because Taxes has part of fbody in return statement
        for farg in fargs:
            arg = farg.strip()
            if fbody.find(arg) < 0:
                found_error = True
                msg += 'FUNCTION,ARGUMENT= {} {}\n'.format(fname, arg)
    if found_error:
        raise ValueError(msg)


@pytest.yield_fixture
def reformfile1():
    """
    specify JSON text for reform
    """
    txt = """
    {
        "policy": {
            "_SS_Earnings_c": {"2015": [100000]},
            "_FICA_ss_trt": {"2015": [0.124]},
            "_FICA_mc_trt": {"2015": [0.029]}
        }
    }
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(txt + '\n')
    rfile.close()
    # Must close and then yield for Windows platform
    yield rfile
    os.remove(rfile.name)


def test_1(reformfile1):
    """
    Test calculation of AGI adjustment for half of Self-Employment Tax,
    which is the payroll tax on self-employment income.
    """
    agi_ovar_num = 10
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
                         reform=reformfile1.name,
                         assump=None,
                         exact_calculations=False,
                         blowup_input_data=False,
                         adjust_input_data=False,
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


@pytest.yield_fixture
def reformfile2():
    """
    specify JSON text for implausible reform to make hand calcs easier
    """
    txt = """
    {
        "policy": {
            "_ACTC_Income_thd": {"2015": [35000]},
            "_SS_Earnings_c": {"2015": [53000]}
        }
    }
    """
    rfile = tempfile.NamedTemporaryFile(mode='a', delete=False)
    rfile.write(txt + '\n')
    rfile.close()
    # Must close and then yield for Windows platform
    yield rfile
    os.remove(rfile.name)


def test_2(reformfile2):
    """
    Test calculation of Additional Child Tax Credit (CTC) when at least one
    of taxpayer and spouse have wage-and-salary income above the FICA maximum
    taxable earnings.
    """
    ctc_ovar_num = 22
    actc_ovar_num = 23
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
                         reform=reformfile2.name,
                         assump=None,
                         exact_calculations=False,
                         blowup_input_data=False,
                         adjust_input_data=False,
                         output_weights=False,
                         output_records=False,
                         csv_dump=False)
    output = inctax.calculate()
    output_vars_list = output.split()
    ctc = output_vars_list[ctc_ovar_num - 1]
    actc = output_vars_list[actc_ovar_num - 1]
    assert ctc == expected_ctc
    assert actc == expected_actc
