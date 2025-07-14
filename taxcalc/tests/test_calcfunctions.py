"""
Tests for Tax-Calculator calcfunctions.py logic.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_calcfunctions.py
# pylint --disable=locally-disabled test_calcfunctions.py

import os
import re
import ast
import numpy as np
import pytest
from taxcalc.records import Records
from taxcalc import calcfunctions


class GetFuncDefs(ast.NodeVisitor):
    """
    Return information about each function defined in calcfunctions.py file.
    """
    def __init__(self):
        """
        GetFuncDefs class constructor
        """
        self.fname = ''
        self.fnames = []  # function name (fname) list
        self.fargs = {}  # lists of function arguments indexed by fname
        self.cvars = {}  # lists of calc vars in function indexed by fname
        self.rvars = {}  # lists of function return vars indexed by fname

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
        if node.name == 'SchXYZ':
            return  # skipping SchXYZ function that has multiple returns
        self.fname = node.name
        self.fnames.append(self.fname)
        self.fargs[self.fname] = []
        for anode in ast.iter_child_nodes(node.args):
            self.fargs[self.fname].append(anode.arg)
        self.cvars[self.fname] = []
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


@pytest.mark.calc_and_used_vars
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
    with open(funcpath, 'r', encoding='utf-8') as funcfile:
        funcfile_text = funcfile.read()
    gfd = GetFuncDefs()
    fnames, fargs, cvars, rvars = gfd.visit(ast.parse(funcfile_text))
    # Test (1):
    # .. create set of vars that are actually calculated in calcfunctions.py
    all_cvars = set()
    for fname in fnames:
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
            msg1 += f'VAR NOT CALCULATED: {var}\n'
    # Test (2):
    faux_functions = ['EITCamount', 'SchXYZ', 'BenefitPrograms']
    found_error2 = False
    msg2 = 'calculated & returned variables are not function arguments\n'
    for fname in fnames:
        if fname in faux_functions:
            continue  # because fname is not a genuine function
        crvars_set = set(cvars[fname]) & set(rvars[fname])
        if not crvars_set <= set(fargs[fname]):
            found_error2 = True
            for var in crvars_set - set(fargs[fname]):
                msg2 += f'FUNCTION,VARIABLE: {fname} {var}\n'
    # Report errors for the two tests:
    if found_error1 and found_error2:
        raise ValueError(f'{msg1}\n{msg2}')
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
    with open(funcfilename, 'r', encoding='utf-8') as funcfile:
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
            msg += f'{fcode}\n'
            msg += '--------------------------------------------------------\n'
            raise ValueError(msg)
        fname = match.group(1)
        fargs = match.group(2).split(',')  # list of function arguments
        fbody = match.group(3)
        for farg in fargs:
            arg = farg.strip()
            if fbody.find(arg) < 0:
                found_error = True
                msg += f'FUNCTION,ARGUMENT= {fname} {arg}\n'
    if found_error:
        raise ValueError(msg)


# pylint: disable=invalid-name,unused-argument


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
Charity_max_in = [300, 600, 300, 300, 300]
tuple1 = (0, 1000, STD_in, 45, 44, STD_Aged_in, 1000, 2, 0, 0, 0, 2,
          False, 0, 0, 0, Charity_max_in)
tuple2 = (0, 1000, STD_in, 66, 44, STD_Aged_in, 1000, 2, 0, 1, 1, 2,
          True, 200, 100000, 1, Charity_max_in)
tuple3 = (0, 1000, STD_in, 44, 66, STD_Aged_in, 1000, 2, 0, 0, 0, 2,
          True, 700, 100000, 1, Charity_max_in)
tuple4 = (0, 1200, STD_in, 66, 67, STD_Aged_in, 1000, 2, 0, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
tuple5 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 1, 0, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
tuple6 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 1, 0, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
tuple7 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 3, 1, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
tuple8 = (1, 200, STD_in, 44, 0, STD_Aged_in, 1000, 3, 0, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
tuple9 = (1, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 3, 0, 0, 0, 2,
          True, 0, 100000, 1, Charity_max_in)
expected = [12000, 15800, 13800, 14400, 6000, 6000, 0, 1000, 1350]


@pytest.mark.stded
@pytest.mark.parametrize(
    'test_tuple,expected_value', [
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
    avalue = calcfunctions.StdDed(*test_tuple)
    assert np.allclose(avalue, expected_value), f"{avalue} != {expected_value}"


tuple1 = (120000, 10000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 99999999999,
          400, 0, 0, 0, 0, 0, 0, None, None, None, None, None, None,
          None, None, None, None, None)
tuple2 = (120000, 10000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 99999999999,
          400, 2000, 0, 10000, 0, 0, 3000, None, None, None, None, None,
          None, None, None, None, None, None)
tuple3 = (120000, 150000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 99999999999,
          400, 2000, 0, 10000, 0, 0, 3000, None, None, None, None, None,
          None, None, None, None, None, None)
tuple4 = (120000, 500000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 400000,
          400, 2000, 0, 10000, 0, 0, 3000, None, None, None, None, None,
          None, None, None, None, None, None)
tuple5 = (120000, 10000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 99999999999,
          400, 300, 0, 0, 0, 0, 0, None, None, None, None, None,
          None, None, None, None, None, None)
tuple6 = (120000, 10000, 15000, 100, 2000,
          0.06, 0.06, 0.015, 0.015, 0, 99999999999,
          400, 0, 0, 0, 0, -40000, 0, None, None, None, None, None,
          None, None, None, None, None, None)
expected1 = (0, 4065, 4065, 0, 0, 3252, 25000, 10000, 15000, 10100,
             17000)
expected2 = (15000, 4065, 4065, 2081.25, 1040.625, 4917, 38959.375,
             21167.5, 17791.875, 21380, 19820)
expected3 = (15000, 21453, 21453, 749.25, 374.625, 16773, 179625.375,
             161833.5, 17791.875, 161380, 19820)
expected4 = (15000, 45318.6, 31953, 749.25, 374.625, 30138.6,
             529625.375, 511833.5, 17791.875, 511380, 19820)
expected5 = (300, 4065, 4065, 0, 0, 3285.3, 25300, 10279.1875, 15000,
             10382, 17000)
expected6 = (-40000, 4065, 4065, 0, 0, 3252, 0, 0, 15000, 10100, 17000)


@pytest.mark.parametrize(
    'test_input, expected_output', [
        (tuple1, expected1),
        (tuple2, expected2),
        (tuple3, expected3),
        (tuple4, expected4),
        (tuple5, expected5),
        (tuple6, expected6)], ids=[
            'case 1', 'case 2', 'case 3', 'case 4', 'case 5', 'case 6'])
def test_EI_PayrollTax(test_input, expected_output, skip_jit):
    """
    Tests the EI_PayrollTax function
    """
    actual_output = calcfunctions.EI_PayrollTax(*test_input)
    if not np.allclose(actual_output, expected_output):
        print('*INPUT:', test_input)
        print('ACTUAL:', actual_output)
        print('EXPECT:', expected_output)
        assert False, 'ERROR: ACTUAL != EXPECT'


def test_AfterTaxIncome(skip_jit):
    '''
    Tests the AfterTaxIncome function
    '''
    test_tuple = (1000, 5000, 4000)
    test_value = calcfunctions.AfterTaxIncome(*test_tuple)
    expected_value = 4000
    assert np.allclose(test_value, expected_value)


def test_ExpandIncome(skip_jit):
    '''
    Tests the ExpandIncome function
    '''
    test_tuple = (10000, 1000, 500, 100, 200, 300, 400, 20, 500, 50, 250, 10,
                  20, 30, 40, 60, 70, 80, 1500, 2000, 16380)
    test_value = calcfunctions.ExpandIncome(*test_tuple)
    expected_value = 16380
    assert np.allclose(test_value, expected_value)


tuple1 = (1, 1, 2, 0, 0, 1000)
tuple2 = (0, 1, 2, 0, 0, 1000)
tuple3 = (1, 1, 2, 100, 0, 1000)
tuple4 = (0, 2, 1, 100, 200, 1000)
tuple5 = (0, 1, 3, 100, 300, 1000)
expected1 = (0, 1000)
expected2 = (0, 1000)
expected3 = (0, 1000)
expected4 = (200, 1200)
expected5 = (300, 1300)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple1, expected1), (tuple2, expected2), (tuple3, expected3),
        (tuple4, expected4), (tuple5, expected5)])
def test_LumpSumTax(test_tuple, expected_value, skip_jit):
    '''
    Tests LumpSumTax function
    '''
    test_value = calcfunctions.LumpSumTax(*test_tuple)
    assert np.allclose(test_value, expected_value)


FST_AGI_thd_lo_in = [1000000, 1000000, 500000, 1000000, 1000000]
FST_AGI_thd_hi_in = [2000000, 2000000, 1000000, 2000000, 2000000]
tuple1 = (1100000, 1, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple2 = (2100000, 1, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple3 = (1100000, 1, 1000, 100, 100, 0, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple4 = (1100000, 2, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple5 = (2100000, 2, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple6 = (1100000, 2, 1000, 100, 100, 0, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple7 = (510000, 3, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple8 = (1100000, 3, 1000, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple9 = (510000, 3, 1000, 100, 100, 0, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
expected1 = (10915, 11115, 12915, 11215)
expected2 = (209150, 209350, 211150, 209450)
expected3 = (0, 200, 2000, 300)
expected4 = (10915, 11115, 12915, 11215)
expected5 = (209150, 209350, 211150, 209450)
expected6 = (0, 200, 2000, 300)
expected7 = (1003, 1203, 3003, 1303)
expected8 = (109150, 109350, 111150, 109450)
expected9 = (0, 200, 2000, 300)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple1, expected1), (tuple2, expected2), (tuple3, expected3),
        (tuple4, expected4), (tuple5, expected5), (tuple6, expected6),
        (tuple7, expected7), (tuple8, expected8), (tuple9, expected9)])
def test_FairShareTax(test_tuple, expected_value, skip_jit):
    '''
    Tests FairShareTax function
    '''
    test_value = calcfunctions.FairShareTax(*test_tuple)
    assert np.allclose(test_value, expected_value)


II_credit_ARPA = [0, 0, 0, 0, 0]
II_credit_ps_ARPA = [0, 0, 0, 0, 0]
II_credit_nr_ARPA = [0, 0, 0, 0, 0]
II_credit_nr_ps_ARPA = [0, 0, 0, 0, 0]
RRC_ps_ARPA = [75000, 150000, 75000, 112500, 150000]
RRC_pe_ARPA = [80000, 160000, 80000, 120000, 160000]
RRC_c_unit_ARPA = [0, 0, 0, 0, 0]
II_credit_CARES = [0, 0, 0, 0, 0]
II_credit_ps_CARES = [0, 0, 0, 0, 0]
II_credit_nr_CARES = [0, 0, 0, 0, 0]
II_credit_nr_ps_CARES = [0, 0, 0, 0, 0]
RRC_ps_CARES = [75000, 150000, 75000, 112500, 75000]
RRC_pe_CARES = [0, 0, 0, 0, 0]
RRC_c_unit_CARES = [1200, 2400, 1200, 1200, 1200]
tuple1 = (1, 50000, 1, 0, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple2 = (1, 76000, 1, 0, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple3 = (1, 90000, 1, 0, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple4 = (2, 50000, 3, 1, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple5 = (2, 155000, 4, 2, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple6 = (2, 170000, 4, 2, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple7 = (4, 50000, 2, 1, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple8 = (4, 117000, 1, 0, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple9 = (4, 130000, 1, 0, II_credit_ARPA, II_credit_ps_ARPA, 0,
          II_credit_nr_ARPA, II_credit_nr_ps_ARPA, 0, 1400, RRC_ps_ARPA,
          RRC_pe_ARPA, 0, 0, RRC_c_unit_ARPA, 0, 0, 0)
tuple10 = (1, 50000, 1, 0, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple11 = (1, 97000, 2, 1, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple12 = (1, 150000, 2, 1, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple13 = (2, 50000, 4, 2, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple14 = (2, 160000, 5, 3, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple15 = (2, 300000, 2, 0, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple16 = (4, 50000, 3, 2, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple17 = (4, 130000, 2, 1, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
tuple18 = (4, 170000, 3, 2, II_credit_CARES, II_credit_ps_CARES, 0,
           II_credit_nr_CARES, II_credit_nr_ps_CARES, 0, 0, RRC_ps_CARES,
           RRC_pe_CARES, 0.05, 500, RRC_c_unit_CARES, 0, 0, 0)
expected1 = (0, 0, 1400)
expected2 = (0, 0, 1120)
expected3 = (0, 0, 0)
expected4 = (0, 0, 4200)
expected5 = (0, 0, 2800)
expected6 = (0, 0, 0)
expected7 = (0, 0, 2800)
expected8 = (0, 0, 560)
expected9 = (0, 0, 0)
expected10 = (0, 0, 1200)
expected11 = (0, 0, 600)
expected12 = (0, 0, 0)
expected13 = (0, 0, 3400)
expected14 = (0, 0, 3400)
expected15 = (0, 0, 0)
expected16 = (0, 0, 2200)
expected17 = (0, 0, 825)
expected18 = (0, 0, 0)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple1, expected1), (tuple2, expected2), (tuple3, expected3),
        (tuple4, expected4), (tuple5, expected5), (tuple6, expected6),
        (tuple7, expected7), (tuple8, expected8), (tuple9, expected9),
        (tuple10, expected10), (tuple11, expected11), (tuple12, expected12),
        (tuple13, expected13), (tuple14, expected14), (tuple15, expected15),
        (tuple16, expected16), (tuple17, expected17), (tuple18, expected18)])
def test_PersonalTaxCredit(test_tuple, expected_value, skip_jit):
    """
    Tests the PersonalTaxCredit function
    """
    test_value = calcfunctions.PersonalTaxCredit(*test_tuple)
    assert np.allclose(test_value, expected_value)


# MARS = 4
# Kids = 3+
basic_frac = 0.0
phasein_rate = 0.45
earnings = 19330
max_amount = 6660
phaseout_start = 19330
agi = 19330
phaseout_rate = 0.2106
tuple1 = (basic_frac, phasein_rate, earnings, max_amount,
          phaseout_start, agi, phaseout_rate)
expected1 = 6660


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple1, expected1)])
def test_EITCamount(test_tuple, expected_value, skip_jit):
    '''
    Tests FairShareTax function
    '''
    test_value = calcfunctions.EITCamount(*test_tuple)
    assert np.allclose(test_value, expected_value)


MARS = 4
DSI = 0
EIC = 3
c00100 = 19330
e00300 = 0
e00400 = 0
e00600 = 0
c01000 = 0
e02000 = 0
e26270 = 0
age_head = 0
age_spouse = 0
earned = 19330
earned_p = 19330
earned_s = 0
EITC_ps = [8790, 19330, 19330, 19330]
EITC_MinEligAge = 25
EITC_MaxEligAge = 64
EITC_ps_MarriedJ = [5890, 5890, 5890, 5890]
EITC_rt = [0.0765, 0.34, 0.4, 0.45]
EITC_c = [538, 3584, 5920, 6660]
EITC_prt = [0.0765, 0.1598, 0.2106, 0.2106]
EITC_basic_frac = 0.0
EITC_InvestIncome_c = 3650
EITC_excess_InvestIncome_rt = 9e+99
EITC_indiv = False
EITC_sep_filers_elig = False
e02300 = 10200
UI_thd = [150000, 150000, 150000, 150000, 150000]
UI_em = 10200
c59660 = 0  # this will be 6660 after the EITC calculation
tuple1 = (MARS, DSI, EIC, c00100, e00300, e00400, e00600, c01000,
          e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s,
          EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_MarriedJ,
          EITC_rt, EITC_c, EITC_prt, EITC_basic_frac,
          EITC_InvestIncome_c, EITC_excess_InvestIncome_rt,
          EITC_indiv, EITC_sep_filers_elig, c59660)
expected1 = 6660


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple1, expected1)])
def test_EITC(test_tuple, expected_value, skip_jit):
    '''
    Tests FairShareTax function
    '''
    test_value = calcfunctions.EITC(*test_tuple)
    assert np.allclose(test_value, expected_value)


# Parameter values for tests
PT_qbid_rt = 0.2
PT_qbid_limited = True
PT_qbid_taxinc_thd = [160700.0, 321400.0, 160725.0, 160700.0, 321400.0]
PT_qbid_taxinc_gap = [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]
PT_qbid_w2_wages_rt = 0.5
PT_qbid_alt_w2_wages_rt = 0.25
PT_qbid_alt_property_rt = 0.025
PT_qbid_ps = [9e99, 9e99, 9e99, 9e99, 9e99]
PT_qbid_prt = 0.0
PT_qbid_min_ded = 400.0  # OBBBA value in 2026
PT_qbid_min_qbi = 1000.0  # OBBBA value in 2026

# Input variable values for tests
c00100 = [527860.66, 337675.10, 603700.00, 90700.00]
standard = [0.00, 0.00, 24400.00, 0.00]
c04470 = [37000.00, 49000.00, 0.00, 32000.00]
c04600 = [0.00, 0.00, 0.00, 0.00]
MARS = [2, 2, 2, 4]
e00900 = [352000.00, 23000.00, 0.00, 0.00]
c03260 = [13516.17, 1624.90, 0.00, 0.00]
e26270 = [0.00, 0.00, 11000.00, 6000.00]
e02100 = [0.00, 0.00, 0.00, 0.00]
e27200 = [0.00, 0.00, 0.00, 0.00]
e00650 = [5000.00, 8000.00, 3000.00, 9000.00]
c01000 = [7000.00, 4000.00, -3000.00, -3000.00]
senior_deduction = [0.00, 0.00, 1000.00, 0.00]
auto_loan_interest_deduction = [0.00, 0.00, 0.00, 1000.00]
PT_SSTB_income = [0, 1, 1, 1]
PT_binc_w2_wages = [0.00, 0.00, 0.00, 0.00]
PT_ubia_property = [0.00, 0.00, 0.00, 0.00]
c04800 = [0.0, 0.0, 0.0, 0.0]  # calculated by function
qbided = [0.0, 0.0, 0.0, 0.0]  # calculated by function

tuple0 = (
    c00100[0], standard[0], c04470[0], c04600[0], MARS[0], e00900[0],
    c03260[0], e26270[0],
    e02100[0], e27200[0], e00650[0], c01000[0],
    senior_deduction[0], auto_loan_interest_deduction[0], PT_SSTB_income[0],
    PT_binc_w2_wages[0], PT_ubia_property[0], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[0], qbided[0])
expected0 = (490460.66, 400.00)
tuple1 = (
    c00100[1], standard[1], c04470[1], c04600[1], MARS[1], e00900[1],
    c03260[1], e26270[1],
    e02100[1], e27200[1], e00650[1], c01000[1],
    senior_deduction[1], auto_loan_interest_deduction[1], PT_SSTB_income[1],
    PT_binc_w2_wages[1], PT_ubia_property[1], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[1], qbided[1])
expected1 = (284400.08, 4275.02)
tuple2 = (
    c00100[2], standard[2], c04470[2], c04600[2], MARS[2], e00900[2],
    c03260[2], e26270[2],
    e02100[2], e27200[2], e00650[2], c01000[2],
    senior_deduction[2], auto_loan_interest_deduction[2], PT_SSTB_income[2],
    PT_binc_w2_wages[2], PT_ubia_property[2], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[2], qbided[2])
expected2 = (577900.00, 400.00)
tuple3 = (
    c00100[3], standard[3], c04470[3], c04600[3], MARS[3], e00900[3],
    c03260[3], e26270[3],
    e02100[3], e27200[3], e00650[3], c01000[3],
    senior_deduction[3], auto_loan_interest_deduction[3], PT_SSTB_income[3],
    PT_binc_w2_wages[3], PT_ubia_property[3], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[3], qbided[3])
expected3 = (56500.00, 1200)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple0, expected0),
        (tuple1, expected1),
        (tuple2, expected2),
        (tuple3, expected3)])
def test_TaxInc(test_tuple, expected_value, skip_jit):
    """
    Tests the TaxInc function
    """
    test_value = calcfunctions.TaxInc(*test_tuple)
    assert np.allclose(test_value, expected_value)


# parameterization represents 2021 law
age_head = 45
age_spouse = 0
nu18 = 0
n24 = 0
MARS = 4
c00100 = 1000
XTOT = 3
num = 1
c05800 = 0
e07260 = 0
CR_ResidentialEnergy_hc = 0.0
e07300 = 0
CR_ForeignTax_hc = 0.0
c07180 = 0
c07230 = 0
e07240 = 0
CR_RetirementSavings_hc = 0.0
c07200 = 0
CTC_c = 2000
CTC_ps = [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]
CTC_prt = 0.05
exact = False
ODC_c = 500
CTC_c_under6_bonus = 0.0
nu06 = 0
CTC_refundable = True
CTC_include17 = True
c07220 = 0  # actual value will be returned from function
odc = 0  # actual value will be returned from function
codtc_limited = 0  # actual value will be returned from function
tuple0 = (
    age_head, age_spouse, nu18, n24, MARS, c00100, XTOT, num,
    c05800, e07260, CR_ResidentialEnergy_hc,
    e07300, CR_ForeignTax_hc,
    c07180,
    c07230,
    e07240, CR_RetirementSavings_hc,
    c07200,
    CTC_c, CTC_ps, CTC_prt, exact, ODC_c,
    CTC_c_under6_bonus, nu06,
    CTC_refundable, CTC_include17,
    c07220, odc, codtc_limited)
# output tuple is : (c07220, odc, codtc_limited)
expected0 = (0, 1000, 0)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [(tuple0, expected0)]
)
def test_ChildDepTaxCredit_2021(test_tuple, expected_value, skip_jit):
    """
    Tests the ChildDepTaxCredit function
    """
    test_value = calcfunctions.ChildDepTaxCredit(*test_tuple)
    assert np.allclose(test_value, expected_value)


# parameterization represents 2022 law
age_head = 45
age_spouse = 0
nu18 = 0
n24 = 0
MARS = 4
c00100 = 1000
XTOT = 3
num = 1
c05800 = 0
e07260 = 0
CR_ResidentialEnergy_hc = 0.0
e07300 = 0
CR_ForeignTax_hc = 0.0
c07180 = 0
c07230 = 0
e07240 = 0
CR_RetirementSavings_hc = 0.0
c07200 = 0
CTC_c = 2000
CTC_ps = [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]
CTC_prt = 0.05
exact = False
ODC_c = 500
CTC_c_under6_bonus = 0.0
nu06 = 0
CTC_refundable = False
CTC_include17 = False
c07220 = 0  # actual value will be returned from function
odc = 0  # actual value will be returned from function
codtc_limited = 0  # actual value will be returned from function
tuple0 = (
    age_head, age_spouse, nu18, n24, MARS, c00100, XTOT, num,
    c05800, e07260, CR_ResidentialEnergy_hc,
    e07300, CR_ForeignTax_hc,
    c07180,
    c07230,
    e07240, CR_RetirementSavings_hc,
    c07200,
    CTC_c, CTC_ps, CTC_prt, exact, ODC_c,
    CTC_c_under6_bonus, nu06,
    CTC_refundable, CTC_include17,
    c07220, odc, codtc_limited)
# output tuple is : (c07220, odc, codtc_limited)
expected0 = (0, 0, 1000)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple0, expected0)])
def test_ChildDepTaxCredit_2022(test_tuple, expected_value, skip_jit):
    """
    Tests the ChildDepTaxCredit function
    """
    test_value = calcfunctions.ChildDepTaxCredit(*test_tuple)
    assert np.allclose(test_value, expected_value)


# parameterization represents 2021 law
CTC_new_c = 1000
CTC_new_rt = 0
CTC_new_c_under6_bonus = 600
CTC_new_ps = [75000, 150000, 75000, 125000, 150000]
CTC_new_prt = 0.05
CTC_new_for_all = True
CTC_include17 = True
CTC_new_refund_limited = False
CTC_new_refund_limit_payroll_rt = 0.0
CTC_new_refund_limited_all_payroll = False
payrolltax = 0
exact = 0
n24 = 0
nu06 = 0
age_head = 45
age_spouse = 0
nu18 = 0
num = 1
c00100 = 1000
MARS = 4
ptax_oasdi = 0
c09200 = 0
ctc_new = 0  # actual value will be returned from function
tuple0 = (
    CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
    CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17,
    CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
    CTC_new_refund_limited_all_payroll, payrolltax, exact,
    n24, nu06, age_head, age_spouse, nu18, c00100, MARS, ptax_oasdi,
    c09200, ctc_new)
# output tuple is : (ctc_new)
expected0 = 0


@pytest.mark.parametrize(
    'test_tuple,expected_value', [
        (tuple0, expected0)])
def test_CTCnew_2021(test_tuple, expected_value, skip_jit):
    """
    Tests the CTCnew function
    """
    test_value = calcfunctions.CTC_new(*test_tuple)
    assert np.allclose(test_value, expected_value)


# parameterization represents 2022 law
CTC_new_c = 0
CTC_new_rt = 0
CTC_new_c_under6_bonus = 0
CTC_new_ps = [0, 0, 0, 0, 0]
CTC_new_prt = 0
CTC_new_for_all = False
CTC_include17 = False
CTC_new_refund_limited = False
CTC_new_refund_limit_payroll_rt = 0.0
CTC_new_refund_limited_all_payroll = False
payrolltax = 0
exact = 0
n24 = 0
nu06 = 0
age_head = 45
age_spouse = 0
nu18 = 0
num = 1
c00100 = 1000
MARS = 4
ptax_oasdi = 0
c09200 = 0
ctc_new = 0  # actual value will be returned from function
tuple0 = (
    CTC_new_c, CTC_new_rt, CTC_new_c_under6_bonus,
    CTC_new_ps, CTC_new_prt, CTC_new_for_all, CTC_include17,
    CTC_new_refund_limited, CTC_new_refund_limit_payroll_rt,
    CTC_new_refund_limited_all_payroll, payrolltax, exact,
    n24, nu06, age_head, age_spouse, nu18, c00100, MARS, ptax_oasdi,
    c09200, ctc_new)
# output tuple is : (ctc_new)
expected0 = 0


@pytest.mark.parametrize(
    'test_tuple,expected_value', [(tuple0, expected0)]
)
def test_CTCnew_2022(test_tuple, expected_value, skip_jit):
    """
    Tests the CTCnew function
    """
    test_value = calcfunctions.CTC_new(*test_tuple)
    assert np.allclose(test_value, expected_value)


# parameters for next test
ymod1 = 19330 + 10200
c02500 = 0
c02900 = 0
XTOT = 0
MARS = 4
sep = 1
DSI = 0
exact = False
nu18 = 0
taxable_ubi = 0
II_em = 0.0
II_em_ps = [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]
II_prt = 0.02
II_no_em_nu18 = False
e02300 = 10200
UI_thd = [150000, 150000, 150000, 150000, 150000]
UI_em = 10200
c00100 = 0  # calculated in function
pre_c04600 = 0  # calculated in functio
c04600 = 0  # calculated in functio

tuple0 = (
    ymod1, c02500, c02900, XTOT, MARS, sep, DSI, exact, nu18, taxable_ubi,
    II_em, II_em_ps, II_prt, II_no_em_nu18,
    e02300, UI_thd, UI_em, c00100, pre_c04600, c04600)
# returned tuple is (c00100, pre_c04600, c04600)
expected0 = (19330, 0, 0)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [(tuple0, expected0)]
)
def test_AGI(test_tuple, expected_value, skip_jit):
    """
    Tests the TaxInc function
    """
    test_value = calcfunctions.AGI(*test_tuple)
    print('Returned from agi function: ', test_value)
    assert np.allclose(test_value, expected_value)


# parameters for next test
e03150 = 0
e03210 = 0
c03260 = 0
e03270 = 0
e03300 = 0
e03400 = 0
e03500 = 0
e00800 = 0
e03220 = 0
e03230 = 0
e03240 = 0
e03290 = 0
care_deduction = 0
ALD_StudentLoan_hc = 0
ALD_SelfEmp_HealthIns_hc = 0
ALD_KEOGH_SEP_hc = 0
ALD_EarlyWithdraw_hc = 0
ALD_AlimonyPaid_hc = 0
ALD_AlimonyReceived_hc = 0
ALD_EducatorExpenses_hc = 0
ALD_HSADeduction_hc = 0
ALD_IRAContributions_hc = 0
ALD_DomesticProduction_hc = 0
ALD_Tuition_hc = 0
MARS = 1
earned = 200000
overtime_income = 13000
ALD_OvertimeIncome_hc = 0.
ALD_OvertimeIncome_c = [12500, 25000, 12500, 12500, 12500]
ALD_OvertimeIncome_ps = [150000, 300000, 150000, 150000, 150000]
ALD_OvertimeIncome_prt = 0.10
tip_income = 30000
ALD_TipIncome_hc = 0.
ALD_TipIncome_c = [25000, 25000, 25000, 25000, 25000]
ALD_TipIncome_ps = [150000, 300000, 150000, 150000, 150000]
ALD_TipIncome_prt = 0.10
c02900 = 0  # calculated in function
ALD_OvertimeIncome = 0  # calculated in function
ALD_TipIncome = 0  # calculated in function

tuple0 = (
    e03150, e03210, c03260,
    e03270, e03300, e03400, e03500, e00800,
    e03220, e03230, e03240, e03290, care_deduction,
    ALD_StudentLoan_hc, ALD_SelfEmp_HealthIns_hc, ALD_KEOGH_SEP_hc,
    ALD_EarlyWithdraw_hc, ALD_AlimonyPaid_hc, ALD_AlimonyReceived_hc,
    ALD_EducatorExpenses_hc, ALD_HSADeduction_hc, ALD_IRAContributions_hc,
    ALD_DomesticProduction_hc, ALD_Tuition_hc,
    MARS, earned,
    overtime_income, ALD_OvertimeIncome_hc, ALD_OvertimeIncome_c,
    ALD_OvertimeIncome_ps, ALD_OvertimeIncome_prt,
    tip_income, ALD_TipIncome_hc, ALD_TipIncome_c,
    ALD_TipIncome_ps, ALD_TipIncome_prt,
    c02900, ALD_OvertimeIncome, ALD_TipIncome
)
ovr = 12500 - (200000 - 150000) * 0.10
tip = 25000 - (200000 - 150000) * 0.10
c02900 = 0 + ovr + tip
expected0 = (c02900, ovr, tip)


@pytest.mark.parametrize(
    'test_tuple,expected_value', [(tuple0, expected0)]
)
def test_Adj(test_tuple, expected_value, skip_jit):
    """
    Tests the Adj function ALD_OvertimeIncome and ALD_TipIncome code
    """
    test_value = calcfunctions.Adj(*test_tuple)
    print('Returned from Adj function: ', test_value)
    assert np.allclose(test_value, expected_value)
