"""
Tests for Tax-Calculator calcfunctions.py logic.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_calcfunctions.py
# pylint --disable=locally-disabled test_calcfunctions.py

import os
import re
import ast
from taxcalc import Records  # pylint: disable=import-error
from taxcalc import calcfunctions
import numpy as np
import pytest


class GetFuncDefs(ast.NodeVisitor):
    """
    Return information about each function defined in the functions.py file.
    """
    def __init__(self):
        """
        GetFuncDefs class constructor
        """
        self.fname = ''
        self.fnames = list()  # function name (fname) list
        self.fargs = dict()  # lists of function arguments indexed by fname
        self.cvars = dict()  # lists of calc vars in function indexed by fname
        self.rvars = dict()  # lists of function return vars indexed by fname

    def visit_Module(self, node):  # pylint: disable=invalid-name
        """
        visit the specified Module node
        """
        self.generic_visit(node)
        return (self.fnames, self.fargs, self.cvars, self.rvars)

    def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
        """
        visit the specified FunctionDef node
        """
        self.fname = node.name
        self.fnames.append(self.fname)
        self.fargs[self.fname] = list()
        for anode in ast.iter_child_nodes(node.args):
            self.fargs[self.fname].append(anode.arg)
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
        """
        visit the specified Return node
        """
        if isinstance(node.value, ast.Tuple):
            self.rvars[self.fname] = [r_v.id for r_v in node.value.elts]
        elif isinstance(node.value, ast.BinOp):
            self.rvars[self.fname] = []  # no vars returned; only an expression
        else:
            self.rvars[self.fname] = [node.value.id]
        self.generic_visit(node)


def test_calc_and_used_vars(tests_path):
    """
    Runs two kinds of tests on variables used in the calcfunctions.py file:

    (1) Checks that each var in Records.CALCULATED_VARS is actually calculated

    If test (1) fails, a variable in Records.CALCULATED_VARS was not
    calculated in any function in the calcfunctions.py file.  With the
    exception of a few variables listed in this test, all
    Records.CALCULATED_VARS must be calculated in the calcfunctions.py file.

    (2) Check that each variable that is calculated in a function and
    returned by that function is an argument of that function.
    """
    # pylint: disable=too-many-locals
    funcpath = os.path.join(tests_path, '..', 'calcfunctions.py')
    gfd = GetFuncDefs()
    fnames, fargs, cvars, rvars = gfd.visit(ast.parse(open(funcpath).read()))
    # Test (1):
    # .. create set of vars that are actually calculated in calcfunctions.py
    all_cvars = set()
    for fname in fnames:
        if fname == 'BenefitSurtax':
            continue  # because BenefitSurtax is not really a function
        all_cvars.update(set(cvars[fname]))
    # .. add to all_cvars set variables calculated in Records class
    all_cvars.update(set(['num', 'sep', 'exact']))
    # .. add to all_cvars set variables calculated elsewhere
    all_cvars.update(set(['mtr_paytax', 'mtr_inctax']))
    all_cvars.update(set(['benefit_cost_total', 'benefit_value_total']))
    # .. check that each var in Records.CALCULATED_VARS is in the all_cvars set
    records_varinfo = Records(data=None)
    found_error1 = False
    if not records_varinfo.CALCULATED_VARS <= all_cvars:
        msg1 = ('all Records.CALCULATED_VARS not calculated '
                'in calcfunctions.py\n')
        for var in records_varinfo.CALCULATED_VARS - all_cvars:
            found_error1 = True
            msg1 += 'VAR NOT CALCULATED: {}\n'.format(var)
    # Test (2):
    faux_functions = ['EITCamount', 'ComputeBenefit', 'BenefitPrograms',
                      'BenefitSurtax', 'BenefitLimitation']
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
    if found_error1:
        raise ValueError(msg1)
    if found_error2:
        raise ValueError(msg2)


def test_function_args_usage(tests_path):
    """
    Checks each function argument in calcfunctions.py for use in its
    function body.
    """
    funcfilename = os.path.join(tests_path, '..', 'calcfunctions.py')
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


def test_DependentCare(skip_jit):
    """
    Tests the DependentCare function
    """

    test_tuple = (3, 2, 100000, 1, [250000, 500000, 250000, 500000, 250000],
                  .2, 7165, 5000, 0)
    test_value = calcfunctions.DependentCare(*test_tuple)
    expected_value = 25196

    assert np.allclose(test_value, expected_value)


STD_in = [6000, 12000, 6000, 12000, 12000]
STD_Aged_in = [1500, 1200, 1500, 1500, 1500]
tuple1 = (0, 1000, STD_in, 45, 44, STD_Aged_in, 1000, 2, 0, 0, 0, 2, 0,
          False, 0)
tuple2 = (0, 1000, STD_in, 66, 44, STD_Aged_in, 1000, 2, 0, 1, 1, 2,
          200, True, 300)
tuple3 = (0, 1000, STD_in, 44, 66, STD_Aged_in, 1000, 2, 0, 0, 0, 2,
          400, True, 300)
tuple4 = (0, 1200, STD_in, 66, 67, STD_Aged_in, 1000, 2, 0, 0, 0, 2, 0,
          True, 0)
tuple5 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 1, 0, 0, 0, 2, 0,
          True, 0)
tuple6 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 1, 0, 0, 0, 2, 0,
          True, 0)
tuple7 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 3, 1, 0, 0, 2, 0,
          True, 0)
tuple8 = (1, 200, STD_in, 44, 0, STD_Aged_in, 1000, 3, 0, 0, 0, 2, 0,
          True, 0)
tuple9 = (1, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 3, 0, 0, 0, 2, 0,
          True, 0)
expected = [12000, 15800, 13500, 14400, 6000, 6000, 0, 1000, 1350]


@pytest.mark.parametrize(
    'test_tuple,expected_value',[
        (tuple1, expected[0]), (tuple2, expected[1]),
        (tuple3, expected[2]), (tuple4, expected[3]),
        (tuple5, expected[4]), (tuple6, expected[5]),
        (tuple7, expected[6]), (tuple8, expected[7]),
        (tuple9, expected[8])], ids=[
            'Married, young', 'Married, allow charity',
            'Married, allow charity, over limit',
            'Married, two old', 'Single 1', 'Single 2', 'Married, Single',
            'Marrid, Single, dep, under earn',
            'Married, Single, dep, over earn'])
def test_StdDed(test_tuple, expected_value, skip_jit):
    """
    Tests the StdDed function
    """
    test_value = calcfunctions.StdDed(*test_tuple)

    assert np.allclose(test_value, expected_value)
