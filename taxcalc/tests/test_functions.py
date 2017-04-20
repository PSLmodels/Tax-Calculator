"""
Tests for Tax-Calculator functions.py logic.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_functions.py
# pylint --disable=locally-disabled test_functions.py

import os
import re
import ast
import six
# pylint: disable=import-error
from taxcalc import Records


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
                          '_num', '_sep', 'exact']))
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
