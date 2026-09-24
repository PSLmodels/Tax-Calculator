"""
Tests for Tax-Calculator calcfunctions.py logic.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_calcfunctions.py
# pylint --disable=locally-disabled test_calcfunctions.py

# pylint: disable=too-many-lines

import os
import re
import ast
import numpy as np
import pytest
from taxcalc import Policy, Records, calcfunctions


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
    all_cvars.update(set(['num', 'sep', 'exact', 'credit_claim_urn']))
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
Charity_max_zero = [0, 0, 0, 0, 0]
Charity_max_in = [300, 600, 300, 300, 300]
tuple1 = (0, 1000, STD_in, 45, 44, STD_Aged_in, 1000, 350, 2, 0, 0, 0, 2,
          0, Charity_max_zero)
tuple2 = (0, 1000, STD_in, 66, 44, STD_Aged_in, 1000, 350, 2, 0, 1, 1, 2,
          200, Charity_max_in)
tuple3 = (0, 1000, STD_in, 44, 66, STD_Aged_in, 1000, 350, 2, 0, 0, 0, 2,
          700, Charity_max_in)
tuple4 = (0, 1200, STD_in, 66, 67, STD_Aged_in, 1000, 350, 2, 0, 0, 0, 2,
          0, Charity_max_in)
tuple5 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 350, 1, 0, 0, 0, 2,
          0, Charity_max_in)
tuple6 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 350, 1, 0, 0, 0, 2,
          0, Charity_max_in)
tuple7 = (0, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 350, 3, 1, 0, 0, 2,
          0, Charity_max_in)
tuple8 = (1, 200, STD_in, 44, 0, STD_Aged_in, 1000, 350, 3, 0, 0, 0, 2,
          0, Charity_max_in)
tuple9 = (1, 1000, STD_in, 44, 0, STD_Aged_in, 1000, 350, 3, 0, 0, 0, 2,
          0, Charity_max_in)
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
# In each expected tuple the third and fourth values are ptax_er_p and
# ptax_er_s; their sum equals the single payrolltax_er value that these
# tests expected before that variable was split into taxpayer and spouse
# components.  All other expected values are unchanged.
expected1 = (0, 4065, 757.5, 1275, 4065, 0, 0, 3252, 25000, 10000, 15000)
expected2 = (15000, 4065, 757.5, 1275, 4065, 2081.25, 1040.625, 4917,
             38959.375, 21167.5, 17791.875)
expected3 = (15000, 21453, 9451.5, 1275, 21453, 749.25, 374.625, 16773,
             179625.375, 161833.5, 17791.875)
expected4 = (15000, 43965.0, 20707.5, 1275.0, 31953.0, 749.25, 374.625,
             28785.0, 529625.375, 511833.5, 17791.875)
expected5 = (300, 4065, 757.5, 1275, 4065, 0, 0, 3252, 25300, 10300, 15000)
expected6 = (-40000, 4065, 757.5, 1275, 4065, 0, 0, 3252, 0, 0, 15000)


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


def ei_ptax_tuple(sch_c):
    """
    Returns an EI_PayrollTax argument tuple with no wages or pension
    contributions, 2025 current-law FICA rates, SS_Earnings_c and
    SECA_Earnings_thd, and with sch_c, a (taxpayer, spouse) pair of
    Sch C net profit/loss, as the only self-employment income.
    Sch SE (2025) line 4c keeps 0.9235 of that income.
    """
    return (176100., 0., 0., 0., 0.,
            0.062, 0.062, 0.0145, 0.0145, 0., 99999999999, 400.,
            sch_c[0], sch_c[1], 0., 0., 0., 0.,
            None, None, None, None, None, None, None, None, None, None, None)


# indexes of setax, ptax_oasdi, earned_p and earned_s in the tuple
# returned by EI_PayrollTax
SETAX, PTAX_OASDI, EARNED_P, EARNED_S = 5, 7, 9, 10


@pytest.mark.parametrize(
    'sch_c, expected_setax', [
        # each spouse's line 4c is 277.05, below $400, so neither owes
        # SE tax even though their combined line 4c amounts exceed $400
        ((300., 300.), 0.),
        # only the taxpayer owes: 0.153 * (10000 * 0.9235)
        ((10000., 300.), 1412.955),
        # the spouse loss does not offset the taxpayer profit:
        # 0.153 * (1000 * 0.9235)
        ((1000., -900.), 141.2955),
        # a line 4c amount of exactly $400 is not less than $400
        ((400. / 0.9235, 0.), 61.2)], ids=[
            'both spouses below floor', 'one spouse below floor',
            'spouse loss', 'line 4c at floor'])
def test_EI_PayrollTax_floor_per_spouse(sch_c, expected_setax, skip_jit):
    """
    Tests that the Sch SE (2025) line 4c $400 floor is applied to each
    spouse separately, because each spouse files a separate Sch SE,
    rather than to the filing unit's combined self-employment income.
    """
    actual = calcfunctions.EI_PayrollTax(*ei_ptax_tuple(sch_c))
    assert np.allclose(actual[SETAX], expected_setax), \
        f'{actual[SETAX]} != {expected_setax}'


def test_EI_PayrollTax_below_floor_outputs_agree(skip_jit):
    """
    Tests that a spouse below the Sch SE (2025) line 4c $400 floor has
    no SE tax in any output: setax, the OASDI part of it in ptax_oasdi,
    and the deductible half of it subtracted from earned_p and
    earned_s must all be zero, so that earned income equals Sch C
    profit.
    """
    actual = calcfunctions.EI_PayrollTax(*ei_ptax_tuple((400., 300.)))
    assert np.allclose(actual[SETAX], 0.), f'{actual[SETAX]} != 0'
    assert np.allclose(actual[PTAX_OASDI], 0.), \
        f'{actual[PTAX_OASDI]} != 0'
    assert np.allclose(actual[EARNED_P], 400.), \
        f'{actual[EARNED_P]} != 400'
    assert np.allclose(actual[EARNED_S], 300.), \
        f'{actual[EARNED_S]} != 300'


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
                  20, 30, 40, 60, 70, 80, 500, 250, 2000, 16380)
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
tuple1 = (1100000, 1, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple2 = (2100000, 1, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple3 = (1100000, 1, 1000, 300, 200, 100, 100, 0, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple4 = (1100000, 2, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple5 = (2100000, 2, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple6 = (1100000, 2, 1000, 300, 200, 100, 100, 0, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple7 = (510000, 3, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple8 = (1100000, 3, 1000, 300, 200, 100, 100, 0.1, FST_AGI_thd_lo_in,
          FST_AGI_thd_hi_in, 100, 200, 2000, 300)
tuple9 = (510000, 3, 1000, 300, 200, 100, 100, 0, FST_AGI_thd_lo_in,
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


eitc_claim_prob_min = 0
eitc_claim_prob_scale = 9e99
credit_claim_urn = 0.33
MARS = 4
DSI = 0
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
EIC = 3
EITC_ps = [8790, 19330, 19330, 19330]
EITC_MinEligAge = 25
EITC_MaxEligAge = 64
EITC_ps_addon_MarriedJ = [5890, 5890, 5890, 5890]
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
tuple1 = (eitc_claim_prob_min, eitc_claim_prob_scale, credit_claim_urn,
          MARS, DSI, c00100, e00300, e00400, e00600, c01000,
          e02000, e26270, age_head, age_spouse, earned, earned_p, earned_s,
          EIC,
          EITC_ps, EITC_MinEligAge, EITC_MaxEligAge, EITC_ps_addon_MarriedJ,
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
e03270 = [0.00, 0.00, 0.00, 0.00]
e03300 = [0.00, 0.00, 0.00, 0.00]
e26270 = [0.00, 0.00, 11000.00, 6000.00]
e02100 = [0.00, 0.00, 0.00, 0.00]
e27200 = [0.00, 0.00, 0.00, 0.00]
e00650 = [5000.00, 8000.00, 3000.00, 9000.00]
p22250 = [0.00, 0.00, 0.00, 0.00]
p23250 = [7000.00, 4000.00, -3000.00, -3000.00]
senior_deduction = [0.00, 0.00, 1000.00, 0.00]
overtime_income_deduction = [0.00, 0.00, 0.00, 0.00]
tip_income_deduction = [0.00, 0.00, 0.00, 0.00]
auto_loan_interest_deduction = [0.00, 0.00, 0.00, 1000.00]
PT_SSTB_income = [0, 1, 1, 1]
PT_binc_w2_wages = [0.00, 0.00, 0.00, 0.00]
PT_ubia_property = [0.00, 0.00, 0.00, 0.00]
c04800 = [0.0, 0.0, 0.0, 0.0]  # calculated by function
qbided = [0.0, 0.0, 0.0, 0.0]  # calculated by function

tuple0 = (
    c00100[0], standard[0], c04470[0], c04600[0], MARS[0],
    e00900[0], c03260[0], e03270[0], e03300[0], e26270[0],
    e02100[0], e27200[0],
    e00650[0], p22250[0], p23250[0],
    senior_deduction[0],
    overtime_income_deduction[0],
    tip_income_deduction[0],
    auto_loan_interest_deduction[0],
    PT_SSTB_income[0],
    PT_binc_w2_wages[0], PT_ubia_property[0], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[0], qbided[0])
expected0 = (490460.66, 400.00)
tuple1 = (
    c00100[1], standard[1], c04470[1], c04600[1], MARS[1],
    e00900[1], c03260[1], e03270[1], e03300[1], e26270[1],
    e02100[1], e27200[1],
    e00650[1], p22250[1], p23250[1],
    senior_deduction[1],
    overtime_income_deduction[1],
    tip_income_deduction[1],
    auto_loan_interest_deduction[1],
    PT_SSTB_income[1],
    PT_binc_w2_wages[1], PT_ubia_property[1], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[1], qbided[1])
expected1 = (284400.08, 4275.02)
tuple2 = (
    c00100[2], standard[2], c04470[2], c04600[2], MARS[2],
    e00900[2], c03260[2], e03270[2], e03300[2], e26270[2],
    e02100[2], e27200[2],
    e00650[2], p22250[2], p23250[2],
    senior_deduction[2],
    overtime_income_deduction[2],
    tip_income_deduction[2],
    auto_loan_interest_deduction[2],
    PT_SSTB_income[2],
    PT_binc_w2_wages[2], PT_ubia_property[2], PT_qbid_rt, PT_qbid_limited,
    PT_qbid_taxinc_thd, PT_qbid_taxinc_gap, PT_qbid_w2_wages_rt,
    PT_qbid_alt_w2_wages_rt, PT_qbid_alt_property_rt,
    PT_qbid_ps, PT_qbid_prt, PT_qbid_min_ded, PT_qbid_min_qbi,
    c04800[2], qbided[2])
expected2 = (577900.00, 400.00)
tuple3 = (
    c00100[3], standard[3], c04470[3], c04600[3], MARS[3],
    e00900[3], c03260[3], e03270[3], e03300[3], e26270[3],
    e02100[3], e27200[3],
    e00650[3], p22250[3], p23250[3],
    senior_deduction[3],
    overtime_income_deduction[3],
    tip_income_deduction[3],
    auto_loan_interest_deduction[3],
    PT_SSTB_income[3],
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


# parameters for test_AGI
ymod1 = 19330 + 10200
c02500 = 0
c02900 = 0
XTOT = 0
MARS = 4
DSI = 0
exact = False
nu18 = 0
taxable_ubi = 0
II_em = 0.0
II_em_ps = [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]
II_em_po_step_size = [2500, 2500, 1250, 2500, 2500]
II_prt = 0.02
II_no_em_nu18 = False
e02300 = 10200
UI_thd = [150000, 150000, 150000, 150000, 150000]
UI_em = 10200
c00100 = 0  # calculated in function
pre_c04600 = 0  # calculated in function
c04600 = 0  # calculated in function

tuple0 = (
    ymod1, c02500, c02900, XTOT, MARS, DSI, exact, nu18, taxable_ubi,
    II_em, II_em_ps, II_em_po_step_size, II_prt, II_no_em_nu18,
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
    print('Returned from AGI function: ', test_value)
    assert np.allclose(test_value, expected_value)


# parameters for test_MiscDed
age_head = 66
age_spouse = 65
MARS = 2
c00100 = 320_000
exact_false = False
exact_true = True
SeniorDed_c = 6_000
SeniorDed_ps = [75_000, 150_000, 75_000, 75_000, 75_000]
SeniorDed_prt = 0.06
overtime_income = 30_000
OvertimeIncomeDed_c = [12_500, 25_000, 12_500, 12_500, 12_500]
OvertimeIncomeDed_ps = [150_000, 300_000, 150_000, 150_000, 150_000]
OvertimeIncomeDed_po_step_size = 1_000
OvertimeIncomeDed_po_rate_per_step = 0.1
tip_income = 30_000
TipIncomeDed_c = 25_000
TipIncomeDed_ps = [150_000, 300_000, 150_000, 150_000, 150_000]
TipIncomeDed_po_step_size = 1_000
TipIncomeDed_po_rate_per_step = 0.1
auto_loan_interest = 12_000
AutoLoanInterestDed_c = 10_000
AutoLoanInterestDed_ps = [100_000, 200_000, 100_000, 100_000, 200_000]
AutoLoanInterestDed_po_step_size = 1_000
AutoLoanInterestDed_po_rate_per_step = 0.2
senior_deduction = 0  # calculated in MiscDed function
overtime_income_deduction = 0  # calculated in MiscDed function
tip_income_deduction = 0  # calculated in MiscDed function
auto_loan_interest_deduction = 0  # calculated in MiscDed function

tuple0 = (age_head, age_spouse, MARS, c00100, exact_false,
          SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
          overtime_income,
          OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
          OvertimeIncomeDed_po_step_size,
          OvertimeIncomeDed_po_rate_per_step,
          tip_income,
          TipIncomeDed_c, TipIncomeDed_ps,
          TipIncomeDed_po_step_size,
          TipIncomeDed_po_rate_per_step,
          auto_loan_interest,
          AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
          AutoLoanInterestDed_po_step_size,
          AutoLoanInterestDed_po_rate_per_step,
          senior_deduction,
          overtime_income_deduction,
          tip_income_deduction,
          auto_loan_interest_deduction)
# returned tuple is (senior_deduction, overtime_income_deduction,
#                    tip_income_deduction,auto_loan_interest_deduction)
expected0 = (0, 23_000, 23_000, 0)

tuple1 = (age_head, age_spouse, MARS, c00100, exact_true,
          SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
          overtime_income,
          OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
          OvertimeIncomeDed_po_step_size,
          OvertimeIncomeDed_po_rate_per_step,
          tip_income,
          TipIncomeDed_c, TipIncomeDed_ps,
          TipIncomeDed_po_step_size,
          TipIncomeDed_po_rate_per_step,
          auto_loan_interest,
          AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
          AutoLoanInterestDed_po_step_size,
          AutoLoanInterestDed_po_rate_per_step,
          senior_deduction,
          overtime_income_deduction,
          tip_income_deduction,
          auto_loan_interest_deduction)
# returned tuple is (senior_deduction, overtime_income_deduction,
#                    tip_income_deduction,auto_loan_interest_deduction)
expected1 = (0, 23_000, 23_000, 0)

tuple2 = (age_head, 0, 3, c00100, exact_true,
          SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
          overtime_income,
          OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
          OvertimeIncomeDed_po_step_size,
          OvertimeIncomeDed_po_rate_per_step,
          tip_income,
          TipIncomeDed_c, TipIncomeDed_ps,
          TipIncomeDed_po_step_size,
          TipIncomeDed_po_rate_per_step,
          auto_loan_interest,
          AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
          AutoLoanInterestDed_po_step_size,
          AutoLoanInterestDed_po_rate_per_step,
          senior_deduction,
          overtime_income_deduction,
          tip_income_deduction,
          auto_loan_interest_deduction)
# returned tuple is (senior_deduction, overtime_income_deduction,
#                    tip_income_deduction,auto_loan_interest_deduction)
expected2 = (0, 0, 0, 0)

tuple3 = (age_head, 0, 3, 120_000, exact_false,
          SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
          0,
          OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
          OvertimeIncomeDed_po_step_size,
          OvertimeIncomeDed_po_rate_per_step,
          0,
          TipIncomeDed_c, TipIncomeDed_ps,
          TipIncomeDed_po_step_size,
          TipIncomeDed_po_rate_per_step,
          5_000,
          AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
          AutoLoanInterestDed_po_step_size,
          AutoLoanInterestDed_po_rate_per_step,
          senior_deduction,
          overtime_income_deduction,
          tip_income_deduction,
          auto_loan_interest_deduction)
# returned tuple is (senior_deduction, overtime_income_deduction,
#                    tip_income_deduction,auto_loan_interest_deduction)
expected3 = (0, 0, 0, 1_000)

tuple4 = (age_head, age_spouse, 2, 180_000, exact_false,
          SeniorDed_c, SeniorDed_ps, SeniorDed_prt,
          0,
          OvertimeIncomeDed_c, OvertimeIncomeDed_ps,
          OvertimeIncomeDed_po_step_size,
          OvertimeIncomeDed_po_rate_per_step,
          0,
          TipIncomeDed_c, TipIncomeDed_ps,
          TipIncomeDed_po_step_size,
          TipIncomeDed_po_rate_per_step,
          0,
          AutoLoanInterestDed_c, AutoLoanInterestDed_ps,
          AutoLoanInterestDed_po_step_size,
          AutoLoanInterestDed_po_rate_per_step,
          senior_deduction,
          overtime_income_deduction,
          tip_income_deduction,
          auto_loan_interest_deduction)
# elderly MFJ couple with AGI=180_000 above po_start=150_000, which implies
# excess=30_000, po_amount=1_800, per_person_ded=4_200, and ded total=8_400
# returned tuple is (senior_deduction, overtime_income_deduction,
#                    tip_income_deduction, auto_loan_interest_deduction)
expected4 = (8_400, 0, 0, 0)


@pytest.mark.parametrize(
    'test_tuple,expected_value',
    [(tuple0, expected0), (tuple1, expected1),
     (tuple2, expected2), (tuple3, expected3), (tuple4, expected4)]
)
def test_MiscDed(test_tuple, expected_value, skip_jit):
    """
    Tests the MiscDed function
    """
    test_value = calcfunctions.MiscDed(*test_tuple)
    print('Returned from MiscDed function: ', test_value)
    assert np.allclose(test_value, expected_value)


def test_SchXYZ():
    """
    Tests the SchXYZ function for a single (MARS==1) tax unit that has
    2026 taxable income of $100 million under a 2026 policy reform that
    sets the top bracket threshold (II_brk7) to $20 million for all
    filers and the top marginal tax rate (II_rt8) to 0.44, leaving all
    other policy parameters at their 2026 current-law values.
    """
    pol = Policy()
    pol.set_year(2026)
    # current-law 2026 rate and (upper) bracket-threshold parameters
    rates = [float(getattr(pol, f'II_rt{i}')[0]) for i in range(1, 9)]
    brks = [np.array(getattr(pol, f'II_brk{i}')[0]) for i in range(1, 8)]
    # apply 2026 reform: II_brk7 = $20M for all filers and II_rt8 = 0.44
    brks[6] = np.array([20e6] * 5)
    rates[7] = 0.44
    # expected income tax liability computed independently of SchXYZ:
    # a single (MARS==1) filer with $100M of taxable income is taxed at
    # each bracket rate on the income falling within that bracket
    taxable_income = 100e6
    upper = [brks[b][0] for b in range(7)] + [taxable_income]
    lower = 0.0
    expect = 0.0
    for rate, top in zip(rates, upper):
        expect += rate * (min(taxable_income, top) - lower)
        lower = min(taxable_income, top)
    assert np.allclose(expect, 42555957.25)
    actual = calcfunctions.SchXYZ(
        taxable_income, 1,
        rates[0], rates[1], rates[2], rates[3],
        rates[4], rates[5], rates[6], rates[7],
        brks[0], brks[1], brks[2], brks[3],
        brks[4], brks[5], brks[6])
    print(f'Actual value returned from SchXYZ function = {actual:.2f}')
    assert np.allclose(actual, expect), f'{actual:.2f} != {expect:.2f}'


# Sch D (2025) line 21 net-capital-loss limits by MARS.  Values are
# Capital_loss_limitation under 2025 current law; the parameter is not
# inflation-indexed and is unchanged since its single 2013 entry.
CAPITAL_LOSS_LIMITATION = [3000., 3000., 1500., 3000., 3000.]
# CapGainsLoss argument tuples:
# (p22250, p23250, Capital_loss_limitation, MARS, c23650, c01000)
CGL_GAIN = (1000., 4000., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)
CGL_UNDER_CAP = (-1000., -500., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)
CGL_AT_CAP = (-2000., -1000., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)
CGL_OVER_CAP = (-5000., -3000., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)
CGL_OVER_CAP_MFS = (-5000., -3000., CAPITAL_LOSS_LIMITATION, 3, 0., 0.)
CGL_AT_CAP_MFS = (-1000., -500., CAPITAL_LOSS_LIMITATION, 3, 0., 0.)
CGL_ST_LOSS_LT_GAIN = (-10000., 4000., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)
CGL_LT_LOSS_ST_GAIN = (4000., -10000., CAPITAL_LOSS_LIMITATION, 1, 0., 0.)


@pytest.mark.parametrize(
    'test_tuple, expected_value', [
        # net gain: Sch D (2025) line 21 leaves it unchanged
        (CGL_GAIN, (5000., 5000.)),
        # net loss below the cap: deducted in full
        (CGL_UNDER_CAP, (-1500., -1500.)),
        # net loss exactly at the $3,000 cap: still deducted in full
        (CGL_AT_CAP, (-3000., -3000.)),
        # net loss above the cap: limited to $3,000 when not filing
        # separately
        (CGL_OVER_CAP, (-8000., -3000.)),
        # the same loss when married filing separately: $1,500
        (CGL_OVER_CAP_MFS, (-8000., -1500.)),
        # net loss exactly at the $1,500 married-filing-separately cap
        (CGL_AT_CAP_MFS, (-1500., -1500.)),
        # short-term loss netted against long-term gain before the cap
        (CGL_ST_LOSS_LT_GAIN, (-6000., -3000.)),
        # long-term loss netted against short-term gain before the cap
        (CGL_LT_LOSS_ST_GAIN, (-6000., -3000.))], ids=[
            'net gain', 'loss under cap', 'loss at cap', 'loss over cap',
            'loss over cap MFS', 'loss at cap MFS',
            'ST loss vs LT gain', 'LT loss vs ST gain'])
def test_CapGainsLoss(test_tuple, expected_value, skip_jit):
    """
    Tests the CapGainsLoss function against Sch D (2025) of Form 1040:
    the Part III netting of short-term and long-term gains and losses
    (line 16) and the MARS-indexed cap on a net loss (line 21).  The
    returned pair is (c23650, c01000), the net gain/loss before and
    after that cap.
    """
    actual_value = calcfunctions.CapGainsLoss(*test_tuple)
    assert np.allclose(actual_value, expected_value), \
        f'{actual_value} != {expected_value}'


# Form 8959 (2025) line 5 (= line 9) thresholds by MARS and the
# line 7 (= line 13) rate.  Values are AMEDT_ec and AMEDT_rt under 2025
# current law; neither is inflation-indexed and both are unchanged
# since their single 2013 entries.  Note AMEDT_ec treats a qualifying
# surviving spouse (MARS 5) like a single filer at $200,000, whereas
# NIIT_thd below treats MARS 5 like a joint filer at $250,000; the two
# lists agree everywhere else.
AMEDT_EC = [200000., 250000., 125000., 200000., 200000.]
AMEDT_RT = 0.009
# FICA_ss_trt_* and FICA_mc_trt_* under 2025 current law.  Sch SE
# (2025) line 4c keeps 1 - 0.5 * (sum of the four rates) of
# self-employment earnings.
FICA_SS_TRT_EMPLOYER = 0.062
FICA_SS_TRT_EMPLOYEE = 0.062
FICA_MC_TRT_EMPLOYER = 0.0145
FICA_MC_TRT_EMPLOYEE = 0.0145
SECA_FRAC = 1. - 0.5 * (FICA_SS_TRT_EMPLOYER + FICA_SS_TRT_EMPLOYEE +
                        FICA_MC_TRT_EMPLOYER + FICA_MC_TRT_EMPLOYEE)
assert np.allclose(SECA_FRAC, 0.9235)
# SECA_Earnings_thd under 2025 current law (Sch SE (2025) line 4c floor)
SECA_EARNINGS_THD = 400.


def amedt_tuple(mars, wages, sch_c=(0., 0.), sch_f=(0., 0.),
                k1bx14=(0., 0.), pencon=(0., 0.)):
    """
    Returns an AdditionalMedicareTax argument tuple.  Each of sch_c,
    sch_f and k1bx14 is a (taxpayer, spouse) pair feeding the
    per-spouse Sch SE (2025) line 6 amounts; pencon is a (taxpayer,
    spouse) pair of pension contributions that, with wages, make up the
    Form 8959 (2025) line 1 Medicare wages.
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    return (mars, wages, pencon[0], pencon[1],
            sch_c[0], sch_c[1], sch_f[0], sch_f[1],
            k1bx14[0], k1bx14[1],
            FICA_SS_TRT_EMPLOYER, FICA_SS_TRT_EMPLOYEE,
            FICA_MC_TRT_EMPLOYER, FICA_MC_TRT_EMPLOYEE,
            SECA_EARNINGS_THD, AMEDT_EC, AMEDT_RT, 0.)


@pytest.mark.parametrize(
    'test_tuple, expected_value', [
        # 0.009 * (300000 - 200000)
        (amedt_tuple(1, 300000.), 900.),
        # 0.009 * (300000 - 250000)
        (amedt_tuple(2, 300000.), 450.),
        # 0.009 * (300000 - 125000)
        (amedt_tuple(3, 300000.), 1575.),
        # 0.009 * (300000 - 200000)
        (amedt_tuple(4, 300000.), 900.),
        # MARS 5 uses the $200,000 single amount, not the $250,000
        # joint amount that Form 8960 (2025) gives a surviving spouse
        (amedt_tuple(5, 300000.), 900.),
        # wages at the threshold produce no tax
        (amedt_tuple(1, 200000.), 0.)], ids=[
            'single', 'joint', 'separate', 'head of household',
            'surviving spouse', 'wages at threshold'])
def test_AdditionalMedicareTax_wages(test_tuple, expected_value, skip_jit):
    """
    Tests Form 8959 (2025) Part I, lines 1-7: the tax is 0.9% of the
    wages above the MARS-indexed line 5 threshold, and zero at it.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(*test_tuple)
    assert np.allclose(actual_value, expected_value), \
        f'{actual_value} != {expected_value}'


def test_AdditionalMedicareTax_se_uses_remaining_threshold(skip_jit):
    """
    Tests Form 8959 (2025) Part II, lines 8-13: wages use part of the
    line 9 threshold, so line 11 leaves only the remainder and just the
    self-employment earnings above that remainder are taxed.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(1, 150000., sch_c=(100000., 0.)))
    # line 8 = 100000 * 0.9235 = 92350; line 11 = 200000 - 150000;
    # line 13 = 0.009 * (92350 - 50000)
    assert np.allclose(actual_value, 381.15), f'{actual_value} != 381.15'


def test_AdditionalMedicareTax_both_parts(skip_jit):
    """
    Tests that Form 8959 (2025) line 18 adds Part I and Part II rather
    than taking either alone: wages above the line 5 threshold leave
    line 11 at zero, so all of the self-employment earnings are taxed
    as well.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(1, 300000., sch_c=(100000., 0.)))
    # line 7 = 0.009 * (300000 - 200000) = 900;
    # line 13 = 0.009 * (100000 * 0.9235) = 831.15
    assert np.allclose(actual_value, 1731.15), f'{actual_value} != 1731.15'


def test_AdditionalMedicareTax_sey_components(skip_jit):
    """
    Tests that every per-spouse component of Sch SE (2025) line 6
    reaches Form 8959 (2025) line 8: Sch C profit, Sch F profit and
    Sch K-1 box 14 earnings, for taxpayer and spouse alike.

    Wages equal the joint line 9 threshold so that line 11 is zero and
    the whole of line 8 is taxed.  The six inputs are distinct, so
    dropping or duplicating any one of them changes the result.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(2, 250000., sch_c=(10000., 1000.),
                     sch_f=(20000., 2000.), k1bx14=(30000., 3000.)))
    # line 8 = (60000 + 6000) * 0.9235 = 60951;
    # line 13 = 0.009 * 60951
    assert np.allclose(actual_value, 548.559), f'{actual_value} != 548.559'


def test_AdditionalMedicareTax_floors_each_spouse(skip_jit):
    """
    Tests that each spouse's Sch SE (2025) line 6 amount is floored at
    zero before the joint Form 8959 (2025) line 8 total is formed.

    Sch SE is filed separately by each spouse, so one spouse's loss
    does not offset the other's profit.  The taxpayer here has
    $300,000 of Sch C profit and the spouse a $100,000 loss, with wages
    at the $250,000 joint threshold so that line 11 is zero.  The
    result must therefore equal the result for the same taxpayer
    profit and no spouse self-employment income at all; summing the
    spouses before flooring would tax only 200000 * 0.9235 and give
    $1,662.30 instead.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(2, 250000., sch_c=(300000., -100000.)))
    # line 8 = 300000 * 0.9235 = 277050; line 13 = 0.009 * 277050
    assert np.allclose(actual_value, 2493.45), f'{actual_value} != 2493.45'
    without_spouse_loss = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(2, 250000., sch_c=(300000., 0.)))
    assert np.allclose(actual_value, without_spouse_loss), \
        'a spouse loss must not offset the other spouse SE earnings'


def test_AdditionalMedicareTax_pension_contributions(skip_jit):
    """
    Tests that Form 8959 (2025) line 1 Medicare wages (W-2 box 5)
    include the pension contributions (elective deferrals) of both
    spouses, which the e00200 wages (W-2 box 1) exclude.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(2, 230000., pencon=(15000., 10000.)))
    # line 1 = 230000 + 15000 + 10000 = 255000;
    # line 7 = 0.009 * (255000 - 250000)
    assert np.allclose(actual_value, 45.), f'{actual_value} != 45'


def test_AdditionalMedicareTax_se_floor_per_spouse(skip_jit):
    """
    Tests that a spouse whose Sch SE (2025) line 4c amount is less than
    $400 has no self-employment income on Form 8959 (2025) line 8,
    while the other spouse's self-employment income is unaffected.
    Wages equal the joint line 9 threshold so that line 11 is zero.
    """
    actual_value = calcfunctions.AdditionalMedicareTax(
        *amedt_tuple(2, 250000., sch_c=(10000., 300.)))
    # line 8 = 10000 * 0.9235 = 9235 (spouse's 277.05 is below $400);
    # line 13 = 0.009 * 9235
    assert np.allclose(actual_value, 83.115), f'{actual_value} != 83.115'


# Form 8960 (2025) line 14 thresholds by MARS and the line 17 rate.
# Values are NIIT_thd and NIIT_rt under 2025 current law; neither is
# inflation-indexed and both are unchanged since their single 2013
# entries.  Note NIIT_thd treats a qualifying surviving spouse
# (MARS 5) like a joint filer at $250,000, whereas AMEDT_ec above
# treats MARS 5 like a single filer at $200,000; the two lists agree
# everywhere else.
NIIT_THD = [200000., 250000., 125000., 200000., 250000.]
NIIT_RT = 0.038
# NetInvIncTax argument tuples: (e00300, e00600, e02000, e26270,
# c01000, c00100, NIIT_thd, MARS, NIIT_PT_taxed, NIIT_rt, niit).
# e02000 and e26270 differ so that the line 4b adjustment is nonzero.
NIIT_BELOW_EXCESS = (10000., 5000., 20000., 5000., 15000., 300000.,
                     NIIT_THD, 1, False, NIIT_RT, 0.)
NIIT_PT_IN_BASE = (10000., 5000., 20000., 5000., 15000., 300000.,
                   NIIT_THD, 1, True, NIIT_RT, 0.)
NIIT_AT_THRESHOLD = (10000., 5000., 20000., 5000., 15000., 200000.,
                     NIIT_THD, 1, False, NIIT_RT, 0.)
NIIT_EXCESS_BINDS = (10000., 5000., 20000., 5000., 15000., 210000.,
                     NIIT_THD, 1, False, NIIT_RT, 0.)
NIIT_NEGATIVE = (0., 0., -50000., 0., -3000., 300000.,
                 NIIT_THD, 1, False, NIIT_RT, 0.)
NIIT_JOINT = (10000., 5000., 20000., 5000., 15000., 270000.,
              NIIT_THD, 2, False, NIIT_RT, 0.)
NIIT_SURVIVING_SPOUSE = (10000., 5000., 20000., 5000., 15000., 270000.,
                         NIIT_THD, 5, False, NIIT_RT, 0.)
NIIT_SEPARATE = (10000., 5000., 20000., 5000., 15000., 150000.,
                 NIIT_THD, 3, False, NIIT_RT, 0.)


@pytest.mark.parametrize(
    'test_tuple, expected_value', [
        # line 12 = 45000 below line 15 = 100000, so line 16 = line 12
        (NIIT_BELOW_EXCESS, 1710.),
        # NIIT_PT_taxed drops the line 4b adjustment, so line 12 rises
        # by e26270 and the tax by 0.038 * 5000
        (NIIT_PT_IN_BASE, 1900.),
        # modified AGI at the line 14 threshold: line 15 is zero, so
        # no tax however large the investment income
        (NIIT_AT_THRESHOLD, 0.),
        # line 15 = 10000 below line 12 = 45000, so line 16 = line 15
        (NIIT_EXCESS_BINDS, 380.),
        # negative investment income is floored at zero by line 12
        (NIIT_NEGATIVE, 0.),
        # joint filers use the $250,000 threshold: line 15 = 20000
        (NIIT_JOINT, 760.),
        # MARS 5 uses the $250,000 joint amount, not the $200,000
        # single amount that Form 8959 (2025) gives a surviving spouse
        (NIIT_SURVIVING_SPOUSE, 760.),
        # married filing separately uses $125,000: line 15 = 25000
        (NIIT_SEPARATE, 950.)], ids=[
            'nii below excess', 'pt taxed', 'magi at threshold',
            'excess below nii', 'negative nii', 'joint threshold',
            'surviving spouse threshold', 'separate threshold'])
def test_NetInvIncTax(test_tuple, expected_value, skip_jit):
    """
    Tests the NetInvIncTax function against Form 8960 (2025)
    lines 12-17: the tax is the line 17 rate applied to the lesser of
    net investment income (line 12) and the excess of modified AGI
    over the MARS-indexed line 14 threshold (line 15).
    """
    actual_value = calcfunctions.NetInvIncTax(*test_tuple)
    assert np.allclose(actual_value, expected_value), \
        f'{actual_value} != {expected_value}'
