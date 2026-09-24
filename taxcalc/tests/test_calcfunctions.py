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
import pandas as pd
from taxcalc import Policy, Consumption, Records, Calculator, calcfunctions


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


# pylint: disable=invalid-name


# All the tests below (except the BenefitPrograms test, whose function
# takes a Calculator object as its only argument) call calcfunctions
# using the call_calcfunc fixture
# (defined in conftest.py), which supplies 2025 current-law values for
# every policy parameter argument and zero for every other argument not
# specified in the test.  Each expected value is derived, in a comment,
# from 2025 IRS form logic.  Functions that have no 2025 IRS form (because
# they implement reform-only or model-only constructs) are tested under
# 2025 current law (where they are inert) and under a hypothetical reform
# that changes only the reform-only parameters in 2025.


# ----------------------------------------------------------------------
# BenefitPrograms
# ----------------------------------------------------------------------


# BenefitPrograms is a model-only aggregator with no IRS form.  It takes
# a Calculator object as its only argument, so the test constructs a
# one-filing-unit 2025 Calculator object (without extrapolating the
# input data) and calls the function directly.  Under 2025 current law
# no program is repealed and every BEN_*_value consumption parameter is
# 1.0, so the consumption value equals the government cost.  The
# returned tuple is (benefit_cost_total, benefit_value_total).
BEN_AMOUNTS = {
    'housing_ben': 1000., 'ssi_ben': 2000., 'snap_ben': 3000.,
    'tanf_ben': 300., 'vet_ben': 500., 'wic_ben': 600.,
    'mcare_ben': 7000., 'mcaid_ben': 8000., 'e02400': 9000.,
    'e02300': 1100., 'ubi': 1200., 'other_ben': 1300.,
}  # these amounts sum to 35000
BEN_REPEAL_REFORM = {
    'BEN_snap_repeal': {2025: True},
    'BEN_mcaid_repeal': {2025: True},
    'BEN_oasdi_repeal': {2025: True},
}
BEN_VALUE_REVISION = {
    'BEN_housing_value': {2025: 0.5},
    'BEN_mcare_value': {2025: 0.25},
    'BEN_mcaid_value': {2025: 0.75},
}


@pytest.mark.parametrize('reform, revision, expected', [
    # 2025 current law: cost and value both equal the sum of all benefits
    pytest.param(None, None, (35000., 35000.), id='current law'),
    # repealed SNAP, Medicaid, and OASDI benefits are excluded from both
    # totals: 35000 - (3000 + 8000 + 9000)
    pytest.param(BEN_REPEAL_REFORM, None, (15000., 15000.),
                 id='repeal programs'),
    # in-kind benefits are weighted by their consumption value, so value
    # is 35000 - (1 - 0.5) * 1000 - (1 - 0.25) * 7000 - (1 - 0.75) * 8000
    pytest.param(None, BEN_VALUE_REVISION, (35000., 27250.),
                 id='consumption value'),
    # both: cost = 15000 and value is
    # 15000 - (1 - 0.5) * 1000 - (1 - 0.25) * 7000
    pytest.param(BEN_REPEAL_REFORM, BEN_VALUE_REVISION, (15000., 9250.),
                 id='repeal programs and consumption value'),
])
def test_BenefitPrograms(reform, revision, expected):
    """
    Tests the BenefitPrograms function
    """
    pol = Policy()
    if reform:
        pol.implement_reform(reform)
    pol.set_year(2025)
    con = Consumption()
    if revision:
        con.update_consumption(revision)
    idata = {'RECID': [1], 'MARS': [1]}
    idata.update({name: [amt] for name, amt in BEN_AMOUNTS.items()
                  if name != 'ubi'})
    recs = Records(data=pd.DataFrame(idata), start_year=2025,
                   gfactors=None, weights=None)
    calc = Calculator(policy=pol, records=recs, consumption=con,
                      sync_years=False)
    calc.array('ubi', np.array([BEN_AMOUNTS['ubi']]))
    calcfunctions.BenefitPrograms(calc)
    actual = (calc.array('benefit_cost_total')[0],
              calc.array('benefit_value_total')[0])
    assert np.allclose(actual, expected), f'{actual} != {expected}'
    # each repealed program's benefit array is zeroed
    for name in ('snap_ben', 'mcaid_ben', 'e02400'):
        amount = 0. if reform else BEN_AMOUNTS[name]
        assert np.allclose(calc.array(name), amount)


# ----------------------------------------------------------------------
# EI_PayrollTax
# ----------------------------------------------------------------------


# EI_PayrollTax test cases use 2025 current-law values: OASDI maximum
# taxable earnings SS_Earnings_c = 176100, combined OASDI rate
# 0.124 = 2 * 0.062, and combined HI rate 0.029 = 2 * 0.0145.  The 2025
# Sch SE line 4a multiplier is 1 - 0.5 * (0.124 + 0.029) = 0.9235.
# W-2 box 3 and box 5 wages include elective deferrals, so wages subject
# to FICA are e00200p + pencon_p.  The returned tuple is
# (sey, payrolltax, ptax_er_p, ptax_er_s, ptax_was, setax, c03260,
#  ptax_oasdi, earned, earned_p, earned_s).


@pytest.mark.parametrize('rvars, expected', [
    # wages 50000 plus deferrals 5000 = FICA wages 55000:
    # OASDI 0.124 * 55000 = 6820; HI 0.029 * 55000 = 1595;
    # employer share 0.062 * 55000 + 0.0145 * 55000 = 4207.5
    pytest.param({'e00200p': 50000., 'pencon_p': 5000.},
                 (0., 8415., 4207.5, 0., 8415., 0., 0., 6820.,
                  50000., 50000., 0.),
                 id='wages'),
    # FICA wages 200000 above the wage base:
    # OASDI 0.124 * 176100 = 21836.4; HI 0.029 * 200000 = 5800;
    # employer share 0.062 * 176100 + 0.0145 * 200000 = 13818.2
    pytest.param({'e00200p': 200000.},
                 (0., 27636.4, 13818.2, 0., 27636.4, 0., 0., 21836.4,
                  200000., 200000., 0.),
                 id='wages above base'),
    # Sch SE: line 4a = 0.9235 * 100000 = 92350;
    # line 10 = 0.124 * 92350 = 11451.4; line 11 = 0.029 * 92350 =
    # 2678.15; line 12 = 14129.55; line 13 = 0.5 * 14129.55 = 7064.775;
    # earned = 100000 - 7064.775
    pytest.param({'e00900p': 100000.},
                 (100000., 0., 0., 0., 0., 14129.55, 7064.775, 11451.4,
                  92935.225, 92935.225, 0.),
                 id='self-employment'),
    # FICA wages 150000 and Sch C 50000: Sch SE line 4a = 46175;
    # line 9 = 176100 - 150000 = 26100; line 10 = 0.124 * 26100 =
    # 3236.4; line 11 = 0.029 * 46175 = 1339.075; line 12 = 4575.475;
    # line 13 = 2287.7375; wage FICA = 0.153 * 150000 = 22950;
    # employer share = 0.0765 * 150000 = 11475;
    # OASDI = 0.124 * 150000 + 3236.4 = 21836.4
    pytest.param({'e00200p': 150000., 'e00900p': 50000.},
                 (50000., 22950., 11475., 0., 22950., 4575.475, 2287.7375,
                  21836.4, 197712.2625, 197712.2625, 0.),
                 id='wages and self-employment'),
    # joint: taxpayer wages 100000; spouse wages 80000 and Sch C 20000:
    # wage FICA = 0.153 * 180000 = 27540; employer shares are
    # 0.0765 * 100000 = 7650 and 0.0765 * 80000 = 6120;
    # spouse Sch SE line 4a = 18470; line 9 = 96100 is not binding;
    # line 10 = 0.124 * 18470 = 2290.28; line 11 = 0.029 * 18470 =
    # 535.63; line 12 = 2825.91; line 13 = 1412.955;
    # OASDI = 0.124 * 180000 + 2290.28 = 24610.28
    pytest.param({'e00200p': 100000., 'e00200s': 80000.,
                  'e00900s': 20000.},
                 (20000., 27540., 7650., 6120., 27540., 2825.91, 1412.955,
                  24610.28, 198587.045, 100000., 98587.045),
                 id='joint wages and spouse self-employment'),
    # each spouse files a separate Sch SE, so the spouse Sch C loss does
    # not reduce the taxpayer SE tax: taxpayer line 4a = 46175;
    # line 10 = 5725.7; line 11 = 1339.075; line 12 = 7064.775;
    # line 13 = 3532.3875; earned = 40000 - 3532.3875
    pytest.param({'e00900p': 50000., 'e00900s': -10000.},
                 (40000., 0., 0., 0., 0., 7064.775, 3532.3875, 5725.7,
                  36467.6125, 46467.6125, 0.),
                 id='spouse self-employment loss'),
    # each spouse files a separate Sch SE, so the line 4c $400 floor
    # applies per spouse: taxpayer line 4c = 0.9235 * 400 = 369.4 and
    # spouse line 4c = 0.9235 * 300 = 277.05 are each below $400, so
    # neither owes SE tax even though their sum exceeds $400
    pytest.param({'e00900p': 400., 'e00900s': 300.},
                 (700., 0., 0., 0., 0., 0., 0., 0.,
                  700., 400., 300.),
                 id='both spouses below floor'),
    # only the taxpayer owes: taxpayer line 4c = 9235;
    # line 10 = 0.124 * 9235 = 1145.14; line 11 = 0.029 * 9235 =
    # 267.815; line 12 = 1412.955; line 13 = 706.4775;
    # spouse line 4c = 277.05 is below $400
    pytest.param({'e00900p': 10000., 'e00900s': 300.},
                 (10300., 0., 0., 0., 0., 1412.955, 706.4775, 1145.14,
                  9593.5225, 9293.5225, 300.),
                 id='one spouse below floor'),
    # a line 4c amount of exactly $400 is not less than $400:
    # line 10 = 0.124 * 400 = 49.6; line 11 = 0.029 * 400 = 11.6;
    # line 12 = 61.2; line 13 = 30.6
    pytest.param({'e00900p': 400. / 0.9235},
                 (400. / 0.9235, 0., 0., 0., 0., 61.2, 30.6, 49.6,
                  400. / 0.9235 - 30.6, 400. / 0.9235 - 30.6, 0.),
                 id='line 4c at floor'),
])
def test_EI_PayrollTax(call_calcfunc, rvars, expected):
    """
    Tests the EI_PayrollTax function against 2025 FICA and Sch SE logic
    """
    actual = call_calcfunc('EI_PayrollTax', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# DependentCare
# ----------------------------------------------------------------------


# DependentCare is a reform-only above-the-line deduction with no IRS
# form; its parameters are all zero under 2025 current law.
DEPCARE_REFORM = {
    'ALD_Dependents_thd': {2025: [250000, 500000, 250000, 500000, 250000]},
    'ALD_Dependents_hc': {2025: 0.2},
    'ALD_Dependents_Child_c': {2025: 7165},
    'ALD_Dependents_Elder_c': {2025: 5000},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: earned income exceeds the zero threshold
    pytest.param(None, {'MARS': 4, 'nu13': 2, 'earned': 100000.}, 0.,
                 id='current law'),
    # reform: 0.8 * (2 * 7165 + 1 * 5000)
    pytest.param(DEPCARE_REFORM,
                 {'MARS': 4, 'nu13': 2, 'elderly_dependents': 1,
                  'earned': 100000.}, 15464., id='reform below threshold'),
    # reform: earned income at the threshold still qualifies:
    # 0.8 * 7165
    pytest.param(DEPCARE_REFORM,
                 {'MARS': 1, 'nu13': 1, 'earned': 250000.}, 5732.,
                 id='reform at threshold'),
    # reform: the income test is a cliff, not a phaseout
    pytest.param(DEPCARE_REFORM,
                 {'MARS': 1, 'nu13': 1, 'earned': 250001.}, 0.,
                 id='reform above threshold'),
])
def test_DependentCare(call_calcfunc, reform, rvars, expected):
    """
    Tests the DependentCare function
    """
    actual = call_calcfunc('DependentCare', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# Adj
# ----------------------------------------------------------------------


# Adj test cases use 2025 current law, under which every modeled
# 2025 Sch 1 Part II adjustment is fully deductible (its haircut is
# zero), except that alimony paid (line 19a) is not deductible for
# post-2018 divorce instruments, which the model treats as applying to
# all filers (ALD_AlimonyPaid_hc is one).  The legacy tuition-and-fees
# and domestic-production deductions are also not deductible (their
# haircuts are one).  The returned value is c02900 (Sch 1 line 26).
ADJ_SCH1_ITEMS = {
    'e03220': 300.,    # Sch 1 line 11
    'e03290': 4000.,   # Sch 1 line 13
    'c03260': 2000.,   # Sch 1 line 15
    'e03300': 6000.,   # Sch 1 line 16
    'e03270': 5000.,   # Sch 1 line 17
    'e03400': 100.,    # Sch 1 line 18
    'e03150': 7000.,   # Sch 1 line 20
    'e03210': 2500.,   # Sch 1 line 21
}  # these amounts sum to 26900
ADJ_LEGACY_ITEMS = {'e03500': 10000., 'e03230': 4000., 'e03240': 5000.}
ADJ_HAIRCUT_REFORM = {
    'ALD_IRAContributions_hc': {2025: 0.5},
    'ALD_StudentLoan_hc': {2025: 1.0},
}
ADJ_RESTORE_REFORM = {
    'ALD_AlimonyPaid_hc': {2025: 0.0},
    'ALD_Tuition_hc': {2025: 0.0},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # Sch 1 line 26 = sum of lines 11 through 21 (excluding line 19a)
    pytest.param(None, ADJ_SCH1_ITEMS, 26900., id='sch 1 items'),
    # alimony paid, tuition and fees, and domestic production are not
    # deductible under 2025 current law
    pytest.param(None, ADJ_LEGACY_ITEMS, 0., id='legacy items'),
    # all items together: legacy items add nothing to 26900
    pytest.param(None, {**ADJ_SCH1_ITEMS, **ADJ_LEGACY_ITEMS}, 26900.,
                 id='all items'),
    # the reform-only dependent care deduction passes through unchanged
    pytest.param(None, {'care_deduction': 5000.}, 5000.,
                 id='care deduction'),
    # reform: 26900 - 0.5 * 7000 - 1.0 * 2500; the deductible part of
    # self-employment tax (c03260) is not subject to a haircut
    pytest.param(ADJ_HAIRCUT_REFORM, ADJ_SCH1_ITEMS, 20900.,
                 id='reform haircuts'),
    # reform restoring the alimony and tuition deductions: 10000 + 4000,
    # while the domestic production deduction remains not deductible
    pytest.param(ADJ_RESTORE_REFORM, ADJ_LEGACY_ITEMS, 14000.,
                 id='reform restore legacy items'),
])
def test_Adj(call_calcfunc, reform, rvars, expected):
    """
    Tests the Adj function against 2025 Sch 1 Part II logic
    """
    actual = call_calcfunc('Adj', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# ALD_InvInc_ec_base
# ----------------------------------------------------------------------


# ALD_InvInc_ec_base is reform plumbing with no IRS form: it computes the
# investment income base that the reform-only ALD_InvInc_ec_rt parameter
# multiplies in AGIIncome.  The function itself uses no reform-only
# parameters, so it is tested only under 2025 current law, whose capital
# loss limitation matches 2025 Sch D line 21: 3000 (1500 when married
# filing separately).  The base is the sum of taxable interest (Form 1040
# line 2b), ordinary dividends (Form 1040 line 3b), the Sch D line 21
# capped net capital gain or loss, capital gain distributions not
# reported on Sch D, and Form 4797 other gain or loss (Sch 1 line 4).
# The returned value is invinc_ec_base.
INVINC_ITEMS = {
    'e00300': 1000.,   # Form 1040 line 2b
    'e00600': 2000.,   # Form 1040 line 3b
    'e01100': 500.,    # Form 1040 line 7 (no Sch D required)
    'e01200': 300.,    # Sch 1 line 4
}  # these amounts sum to 3800


@pytest.mark.parametrize('rvars, expected', [
    # no investment income
    pytest.param({'MARS': 1}, 0., id='no income'),
    # non-Sch-D items only: 1000 + 2000 + 500 + 300
    pytest.param({'MARS': 1, **INVINC_ITEMS}, 3800., id='non-sch-d items'),
    # net Sch D gain is included in full: 3800 + 1000 + 4000
    pytest.param({'MARS': 1, 'p22250': 1000., 'p23250': 4000.,
                  **INVINC_ITEMS}, 8800., id='net gain'),
    # net Sch D loss under the limit is included in full: 3800 - 1500
    pytest.param({'MARS': 1, 'p22250': -1000., 'p23250': -500.,
                  **INVINC_ITEMS}, 2300., id='loss under cap'),
    # net Sch D loss above the limit is capped at 3000: 3800 - 3000
    pytest.param({'MARS': 1, 'p22250': -5000., 'p23250': -3000.,
                  **INVINC_ITEMS}, 800., id='loss over cap'),
    # the same loss when married filing separately is capped at 1500:
    # 3800 - 1500
    pytest.param({'MARS': 3, 'p22250': -5000., 'p23250': -3000.,
                  **INVINC_ITEMS}, 2300., id='loss over cap MFS'),
    # a Form 4797 loss is not subject to the Sch D line 21 limit:
    # 1000 - 10000
    pytest.param({'MARS': 1, 'e00300': 1000., 'e01200': -10000.},
                 -9000., id='form 4797 loss'),
])
def test_ALD_InvInc_ec_base(call_calcfunc, rvars, expected):
    """
    Tests the ALD_InvInc_ec_base function, including its re-derivation
    of the Sch D line 21 capped net capital gain or loss
    """
    actual = call_calcfunc('ALD_InvInc_ec_base', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# CapGainsLoss
# ----------------------------------------------------------------------


# CapGainsLoss test cases use the 2025 current-law capital loss
# limitation, which matches 2025 Sch D line 21: 3000 (1500 when married
# filing separately).  The returned tuple is (c23650, c01000), the net
# gain or loss before and after that limit.


@pytest.mark.parametrize('rvars, expected', [
    # net gain: Sch D line 21 leaves it unchanged
    pytest.param({'MARS': 1, 'p22250': 1000., 'p23250': 4000.},
                 (5000., 5000.), id='net gain'),
    # net loss below the limit: deducted in full
    pytest.param({'MARS': 1, 'p22250': -1000., 'p23250': -500.},
                 (-1500., -1500.), id='loss under cap'),
    # net loss exactly at the 3000 limit: still deducted in full
    pytest.param({'MARS': 1, 'p22250': -2000., 'p23250': -1000.},
                 (-3000., -3000.), id='loss at cap'),
    # net loss above the limit: limited to 3000
    pytest.param({'MARS': 1, 'p22250': -5000., 'p23250': -3000.},
                 (-8000., -3000.), id='loss over cap'),
    # the same loss when married filing separately: limited to 1500
    pytest.param({'MARS': 3, 'p22250': -5000., 'p23250': -3000.},
                 (-8000., -1500.), id='loss over cap MFS'),
    # net loss exactly at the 1500 married-filing-separately limit
    pytest.param({'MARS': 3, 'p22250': -1000., 'p23250': -500.},
                 (-1500., -1500.), id='loss at cap MFS'),
    # Sch D line 16: short-term loss netted against long-term gain
    pytest.param({'MARS': 1, 'p22250': -10000., 'p23250': 4000.},
                 (-6000., -3000.), id='ST loss vs LT gain'),
    # Sch D line 16: long-term loss netted against short-term gain
    pytest.param({'MARS': 1, 'p22250': 4000., 'p23250': -10000.},
                 (-6000., -3000.), id='LT loss vs ST gain'),
])
def test_CapGainsLoss(call_calcfunc, rvars, expected):
    """
    Tests the CapGainsLoss function against 2025 Sch D logic: the
    Part III netting of short-term and long-term gains and losses
    (line 16) and the MARS-indexed limit on a net loss (line 21)
    """
    actual = call_calcfunc('CapGainsLoss', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AGIIncome
# ----------------------------------------------------------------------


# AGIIncome test cases use 2025 current law, under which alimony
# received is not income (AlimonyReceived_frac_in_AGI is zero) and the
# combined Sch C and Sch E loss is limited by the excess business loss
# limitation (Form 461 line 15): 313000 (626000 when married filing
# jointly or as a surviving spouse).  The reform-only investment income
# and QDCG exclusions are inert under current law.  The returned tuple
# is (ymod, ymod1, invinc_agi_ec), where ymod1 is the sum of the Form
# 1040 income lines (other than taxable social security) and Sch 1
# Part I, and ymod is the Pub. 915 worksheet line 7 modified AGI used
# to compute taxable social security benefits.
AGIINC_ITEMS = {
    'e00200': 50000.,  # Form 1040 line 1
    'e00300': 1000.,   # Form 1040 line 2b
    'e00600': 2000.,   # Form 1040 line 3b
    'e01400': 4000.,   # Form 1040 line 4b
    'e01700': 6000.,   # Form 1040 line 5b
    'c01000': 3000.,   # Form 1040 line 7 (from Sch D)
    'e01100': 500.,    # Form 1040 line 7 (no Sch D required)
    'e00700': 700.,    # Sch 1 line 1
    'e00900': 10000.,  # Sch 1 line 3
    'e01200': 300.,    # Sch 1 line 4
    'e02000': 5000.,   # Sch 1 line 5
    'e02100': 1500.,   # Sch 1 line 6
    'e02300': 2000.,   # Sch 1 line 7
}  # these amounts sum to 86000
INVINC_EXCLUSION_REFORM = {'ALD_InvInc_ec_rt': {2025: 0.5}}
ALIMONY_REFORM = {'AlimonyReceived_frac_in_AGI': {2025: 1.0}}
QDCG_EXCLUSION_REFORM = {
    'CG_nodiff': {2025: True},
    'CG_ec': {2025: 5000},
    'CG_reinvest_ec_rt': {2025: 0.5},
}
QDCG_ITEMS = {
    'e00600': 4000.,   # Form 1040 line 3b
    'e00650': 4000.,   # Form 1040 line 3a
    'c01000': 6000.,   # Form 1040 line 7
}  # QDCG is 4000 + 6000 = 10000


@pytest.mark.parametrize('reform, rvars, expected', [
    # sum of Form 1040 and Sch 1 Part I income items
    pytest.param(None, {'MARS': 1, **AGIINC_ITEMS},
                 (86000., 86000., 0.), id='income items'),
    # alimony received (Sch 1 line 2a) is not income under current law
    pytest.param(None, {'MARS': 1, 'e00800': 12000.},
                 (0., 0., 0.), id='alimony received'),
    # a Sch D loss after the line 21 limit reduces income: 40000 - 3000
    pytest.param(None, {'MARS': 1, 'e00200': 40000., 'c01000': -3000.},
                 (37000., 37000., 0.), id='capital loss'),
    # combined Sch C and Sch E loss is limited to 313000:
    # 600000 - 313000
    pytest.param(None, {'MARS': 1, 'e00200': 600000., 'e00900': -400000.,
                        'e02000': -100000.},
                 (287000., 287000., 0.), id='business loss over cap'),
    # the same loss when married filing jointly is under the 626000
    # limit: 600000 - 500000
    pytest.param(None, {'MARS': 2, 'e00200': 600000., 'e00900': -400000.,
                        'e02000': -100000.},
                 (100000., 100000., 0.), id='business loss under cap MFJ'),
    # Pub. 915 worksheet line 7: 30000 + 2000 + 0.5 * 20000 - 3000
    pytest.param(None, {'MARS': 1, 'e00200': 30000., 'e00400': 2000.,
                        'e02400': 20000., 'c02900': 3000.},
                 (39000., 30000., 0.), id='social security modagi'),
    # Pub. 915 worksheet line 6 excludes the student loan interest
    # deduction (Sch 1 line 21), so the 2500 that Adj included in
    # c02900 is added back; the tuition-and-fees deduction was not
    # deductible and so is not added back: 30000 - 2500 + 2500
    pytest.param(None, {'MARS': 1, 'e00200': 30000., 'e03210': 2500.,
                        'e03230': 4000., 'c02900': 2500.},
                 (30000., 30000., 0.), id='student loan add-back'),
    # reform restoring alimony received as income: 12000
    pytest.param(ALIMONY_REFORM, {'MARS': 1, 'e00800': 12000.},
                 (12000., 12000., 0.), id='reform alimony received'),
    # reform excluding half of investment income: the investment income
    # base is 1000 + 2000 + 500 + 300 = 3800, so the exclusion is
    # 0.5 * 3800 = 1900 and ymod1 is 40000 + 3800 - 1900
    pytest.param(INVINC_EXCLUSION_REFORM,
                 {'MARS': 1, 'e00200': 40000., 'e00300': 1000.,
                  'e00600': 2000., 'e01100': 500., 'e01200': 300.,
                  'invinc_ec_base': 3800.},
                 (41900., 41900., 1900.), id='reform invinc exclusion'),
    # investment income exclusion reform: a negative investment income
    # base yields no exclusion: 40000 - 10000
    pytest.param(INVINC_EXCLUSION_REFORM,
                 {'MARS': 1, 'e00200': 40000., 'e01200': -10000.,
                  'invinc_ec_base': -10000.},
                 (30000., 30000., 0.), id='reform invinc exclusion neg'),
    # reform excluding QDCG when it is taxed at ordinary rates: the
    # exclusion is 5000 + 0.5 * (10000 - 5000) = 7500, so ymod1 is
    # 50000 + 4000 + 6000 - 7500
    pytest.param(QDCG_EXCLUSION_REFORM,
                 {'MARS': 1, 'e00200': 50000., **QDCG_ITEMS},
                 (52500., 52500., 7500.), id='reform qdcg exclusion'),
    # QDCG exclusion reform: ymod1 cannot be negative after the
    # exclusion: max(0, 5000 - 10000 + 4000 + 6000 - 7500)
    pytest.param(QDCG_EXCLUSION_REFORM,
                 {'MARS': 1, 'e00200': 5000., 'e00900': -10000.,
                  **QDCG_ITEMS},
                 (0., 0., 7500.), id='reform qdcg exclusion floor'),
])
def test_AGIIncome(call_calcfunc, reform, rvars, expected):
    """
    Tests the AGIIncome function against 2025 Form 1040, Sch 1 Part I,
    and Pub. 915 worksheet logic
    """
    actual = call_calcfunc('AGIIncome', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# SSBenefits
# ----------------------------------------------------------------------


# SSBenefits test cases use 2025 current-law values, which match the
# 2025 Social Security Benefits Worksheet in the Form 1040 instructions
# (also in Pub. 915): a line 8 base amount of 25000 (32000 when married
# filing jointly), a line 10 amount of 9000 (12000 when married filing
# jointly), a first-tier rate of 0.50 (lines 13 and 14), and a
# second-tier rate of 0.85 (lines 15 and 17).  The model treats every
# married-filing-separately filer as having lived apart from their
# spouse all year, so MARS 3 uses the single base amounts.  The ymod
# argument is worksheet line 7 and e02400 is worksheet line 1.  The
# returned value is c02500 (Form 1040 line 6b, worksheet line 18).
SS_ALL_IN_AGI_REFORM = {'SS_all_in_agi': {2025: True}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # line 9 is negative: 20000 - 25000, so no benefits are taxable
    pytest.param(None, {'MARS': 1, 'ymod': 20000., 'e02400': 15000.},
                 0., id='below base'),
    # line 9 is zero: 25000 - 25000, so no benefits are taxable
    pytest.param(None, {'MARS': 1, 'ymod': 25000., 'e02400': 15000.},
                 0., id='at base'),
    # line 11 is zero: line 12 = 5000; line 13 = 0.5 * 5000;
    # line 14 = min(0.5 * 20000, 2500)
    pytest.param(None, {'MARS': 1, 'ymod': 30000., 'e02400': 20000.},
                 2500., id='first tier'),
    # line 11 is zero: line 12 = 8000; line 13 = 0.5 * 8000;
    # line 14 = min(0.5 * 4000, 4000)
    pytest.param(None, {'MARS': 1, 'ymod': 33000., 'e02400': 4000.},
                 2000., id='first tier benefit limit'),
    # line 11 = 25000 - 9000 = 16000; line 12 = 9000;
    # line 14 = min(0.5 * 30000, 0.5 * 9000) = 4500;
    # line 16 = 0.85 * 16000 + 4500 = 18100; line 17 = 0.85 * 30000;
    # line 18 = min(18100, 25500)
    pytest.param(None, {'MARS': 1, 'ymod': 50000., 'e02400': 30000.},
                 18100., id='second tier'),
    # line 11 = 75000 - 9000 = 66000; line 12 = 9000;
    # line 14 = min(0.5 * 20000, 0.5 * 9000) = 4500;
    # line 16 = 0.85 * 66000 + 4500 = 60600; line 17 = 0.85 * 20000;
    # line 18 = min(60600, 17000)
    pytest.param(None, {'MARS': 1, 'ymod': 100000., 'e02400': 20000.},
                 17000., id='second tier 85 percent limit'),
    # line 11 is zero: line 12 = 40000 - 32000 = 8000;
    # line 14 = min(0.5 * 30000, 0.5 * 8000)
    pytest.param(None, {'MARS': 2, 'ymod': 40000., 'e02400': 30000.},
                 4000., id='first tier MFJ'),
    # line 11 = 28000 - 12000 = 16000; line 12 = 12000;
    # line 14 = min(0.5 * 40000, 0.5 * 12000) = 6000;
    # line 16 = 0.85 * 16000 + 6000 = 19600; line 17 = 0.85 * 40000;
    # line 18 = min(19600, 34000)
    pytest.param(None, {'MARS': 2, 'ymod': 60000., 'e02400': 40000.},
                 19600., id='second tier MFJ'),
    # married filing separately and lived apart all year uses the single
    # amounts: line 12 = 30000 - 25000; line 14 = min(0.5 * 10000, 2500)
    pytest.param(None, {'MARS': 3, 'ymod': 30000., 'e02400': 10000.},
                 2500., id='first tier MFS'),
    # head of household uses the single amounts: line 11 = 16000;
    # line 16 = 0.85 * 16000 + 0.5 * 9000 = 18100;
    # line 18 = min(18100, 0.85 * 30000)
    pytest.param(None, {'MARS': 4, 'ymod': 50000., 'e02400': 30000.},
                 18100., id='second tier HOH'),
    # reform including all benefits in AGI, regardless of ymod
    pytest.param(SS_ALL_IN_AGI_REFORM,
                 {'MARS': 1, 'ymod': 10000., 'e02400': 20000.},
                 20000., id='reform all in AGI'),
])
def test_SSBenefits(call_calcfunc, reform, rvars, expected):
    """
    Tests the SSBenefits function against 2025 Social Security Benefits
    Worksheet logic
    """
    actual = call_calcfunc('SSBenefits', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# UBI
# ----------------------------------------------------------------------


# UBI is a reform-only construct with no IRS form; its per-person benefit
# parameters (UBI_u18, UBI_1820, UBI_21) and its AGI exclusion rate
# (UBI_ecrt) are all zero under 2025 current law.  The returned tuple is
# (ubi, taxable_ubi, nontaxable_ubi).
UBI_REFORM = {
    'UBI_u18': {2025: 1000},
    'UBI_1820': {2025: 2000},
    'UBI_21': {2025: 3000},
}
UBI_EXCLUSION_REFORM = {**UBI_REFORM, 'UBI_ecrt': {2025: 0.25}}
UBI_PEOPLE = {'nu18': 2, 'n1820': 1, 'n21': 2}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no UBI regardless of family composition
    pytest.param(None, UBI_PEOPLE, (0., 0., 0.), id='current law'),
    # reform with no people: no UBI
    pytest.param(UBI_REFORM, {}, (0., 0., 0.), id='reform no people'),
    # reform: 2 * 1000 + 1 * 2000 + 2 * 3000, all of which is taxable
    pytest.param(UBI_REFORM, UBI_PEOPLE, (10000., 10000., 0.),
                 id='reform fully taxable'),
    # reform: 10000 with 0.25 excluded from AGI:
    # taxable = 0.75 * 10000; nontaxable = 10000 - 7500
    pytest.param(UBI_EXCLUSION_REFORM, UBI_PEOPLE, (10000., 7500., 2500.),
                 id='reform partial exclusion'),
    # reform: 10000 fully excluded from AGI
    pytest.param({**UBI_REFORM, 'UBI_ecrt': {2025: 1.0}}, UBI_PEOPLE,
                 (10000., 0., 10000.), id='reform full exclusion'),
])
def test_UBI(call_calcfunc, reform, rvars, expected):
    """
    Tests the UBI function
    """
    actual = call_calcfunc('UBI', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AGI
# ----------------------------------------------------------------------


# AGI test cases use 2025 current law, under which unemployment
# compensation is fully taxable and there are no personal exemptions
# (II_em is zero).  The returned tuple is (c00100, pre_c04600, c04600).
UI_EXCLUSION_REFORM = {
    'UI_em': {2025: 10200},
    'UI_thd': {2025: [150000, 150000, 150000, 150000, 150000]},
}
EXEMPTION_REFORM = {
    'II_em': {2025: 5000},
    'II_em_ps': {2025: [250000, 300000, 150000, 275000, 300000]},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # Form 1040 line 11 = line 9 - line 10
    pytest.param(None,
                 {'MARS': 1, 'ymod1': 60000., 'c02900': 5000.},
                 (55000., 0., 0.), id='adjustments'),
    # taxable social security (line 6b) is part of line 9:
    # 60000 + 10000 - 5000
    pytest.param(None,
                 {'MARS': 1, 'ymod1': 60000., 'c02500': 10000.,
                  'c02900': 5000.},
                 (65000., 0., 0.), id='taxable social security'),
    # unemployment compensation (Sch 1 line 7) is fully taxable
    pytest.param(None,
                 {'MARS': 1, 'ymod1': 30000., 'e02300': 10000.},
                 (30000., 0., 0.), id='unemployment compensation'),
    # no personal exemptions under 2025 current law
    pytest.param(None,
                 {'MARS': 2, 'XTOT': 4, 'ymod1': 100000.},
                 (100000., 0., 0.), id='no exemptions'),
    # 2020-style UI exclusion reform: 40000 - min(15000, 10200)
    pytest.param(UI_EXCLUSION_REFORM,
                 {'MARS': 1, 'ymod1': 40000., 'e02300': 15000.},
                 (29800., 0., 0.), id='reform UI exclusion'),
    # UI exclusion reform: 170000 - 15000 is above 150000
    pytest.param(UI_EXCLUSION_REFORM,
                 {'MARS': 1, 'ymod1': 170000., 'e02300': 15000.},
                 (170000., 0., 0.), id='reform UI exclusion above thd'),
    # pre-TCJA exemption reform: 4 * 5000 below the phase-out start
    pytest.param(EXEMPTION_REFORM,
                 {'MARS': 2, 'XTOT': 4, 'ymod1': 100000.},
                 (100000., 20000., 20000.), id='reform exemptions'),
    # exemption reform, pre-TCJA exemptions worksheet: line 5 = 21000;
    # line 6 = ceil(21000 / 2500) = 9; line 7 = 0.02 * 9 = 0.18;
    # 20000 * (1 - 0.18)
    pytest.param(EXEMPTION_REFORM,
                 {'MARS': 2, 'XTOT': 4, 'ymod1': 321000., 'exact': 1},
                 (321000., 20000., 16400.), id='reform exemptions exact'),
    # exemption reform, smoothed: 20000 * (1 - 0.02 * 21000 / 2500)
    pytest.param(EXEMPTION_REFORM,
                 {'MARS': 2, 'XTOT': 4, 'ymod1': 321000.},
                 (321000., 20000., 16640.),
                 id='reform exemptions smoothed'),
    # exemption reform: dependent filers get no exemptions
    pytest.param(EXEMPTION_REFORM,
                 {'MARS': 1, 'XTOT': 1, 'DSI': 1, 'ymod1': 10000.},
                 (10000., 0., 0.), id='reform dependent'),
])
def test_AGI(call_calcfunc, reform, rvars, expected):
    """
    Tests the AGI function against 2025 Form 1040 line 11 logic
    """
    actual = call_calcfunc('AGI', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# MiscDed
# ----------------------------------------------------------------------


# MiscDed test cases use the 2025 current-law values, which match the
# 2025 Schedule 1-A:
#   Part II tips: 25000 cap, reduced by 100 per 1000 of MAGI above
#     150000 (300000 when married filing jointly);
#   Part III overtime: 12500 cap (25000 when married filing jointly),
#     reduced by 100 per 1000 of MAGI above 150000 (300000 MFJ);
#   Part IV car loan interest: 10000 cap, reduced by 200 per 1000 of
#     MAGI above 100000 (200000 when married filing jointly);
#   Part V seniors: 6000 per person aged 65 or older, reduced by
#     6 percent of MAGI above 75000 (150000 when married filing jointly).
# Married filers must file jointly to claim the Part II, III, and V
# deductions.  The exact flag selects the form's whole-step phase-out
# rounding.  The returned tuple is (senior_deduction,
# overtime_income_deduction, tip_income_deduction,
# auto_loan_interest_deduction).


@pytest.mark.parametrize('rvars, expected', [
    # Part V: MAGI below 75000
    pytest.param({'MARS': 1, 'age_head': 66, 'c00100': 60000.},
                 (6000., 0., 0., 0.), id='senior'),
    # Part V: 6000 - 0.06 * (100000 - 75000)
    pytest.param({'MARS': 1, 'age_head': 66, 'c00100': 100000.},
                 (4500., 0., 0., 0.), id='senior phase-out'),
    # Part V: 2 * (6000 - 0.06 * (180000 - 150000))
    pytest.param({'MARS': 2, 'age_head': 66, 'age_spouse': 65,
                  'c00100': 180000.},
                 (8400., 0., 0., 0.), id='two seniors phase-out'),
    # Part V: only the spouse aged 65 or older qualifies
    pytest.param({'MARS': 2, 'age_head': 60, 'age_spouse': 66,
                  'c00100': 100000.},
                 (6000., 0., 0., 0.), id='one senior joint'),
    # Part V: 6000 - 0.06 * (200000 - 75000) < 0
    pytest.param({'MARS': 4, 'age_head': 70, 'c00100': 200000.},
                 (0., 0., 0., 0.), id='senior phased out'),
    # Part V: married filing separately cannot claim
    pytest.param({'MARS': 3, 'age_head': 66, 'c00100': 50000.},
                 (0., 0., 0., 0.), id='senior separate'),
    # Part II: min(30000, 25000)
    pytest.param({'MARS': 1, 'c00100': 100000., 'tip_income': 30000.},
                 (0., 0., 25000., 0.), id='tips'),
    # Part II: floor(10500 / 1000) = 10 steps; 25000 - 10 * 100
    pytest.param({'MARS': 1, 'c00100': 160500., 'tip_income': 30000.,
                  'exact': 1},
                 (0., 0., 24000., 0.), id='tips phase-out exact'),
    # Part II smoothed: 25000 - 0.1 * 10500
    pytest.param({'MARS': 1, 'c00100': 160500., 'tip_income': 30000.},
                 (0., 0., 23950., 0.), id='tips phase-out smoothed'),
    # Part II: married filing separately cannot claim
    pytest.param({'MARS': 3, 'c00100': 50000., 'tip_income': 10000.},
                 (0., 0., 0., 0.), id='tips separate'),
    # Part III: min(20000, 12500)
    pytest.param({'MARS': 1, 'c00100': 100000.,
                  'overtime_income': 20000.},
                 (0., 12500., 0., 0.), id='overtime'),
    # Part III and Part II joint: overtime min(30000, 25000) and tips
    # min(30000, 25000), each reduced by 0.1 * (320000 - 300000)
    pytest.param({'MARS': 2, 'c00100': 320000.,
                  'overtime_income': 30000., 'tip_income': 30000.},
                 (0., 23000., 23000., 0.), id='overtime and tips joint'),
    # Part III: married filing separately cannot claim
    pytest.param({'MARS': 3, 'c00100': 50000.,
                  'overtime_income': 10000.},
                 (0., 0., 0., 0.), id='overtime separate'),
    # Part IV: min(12000, 10000)
    pytest.param({'MARS': 1, 'c00100': 50000.,
                  'auto_loan_interest': 12000.},
                 (0., 0., 0., 10000.), id='car loan interest'),
    # Part IV: ceil(20500 / 1000) = 21 steps; 10000 - 21 * 200
    pytest.param({'MARS': 1, 'c00100': 120500.,
                  'auto_loan_interest': 12000., 'exact': 1},
                 (0., 0., 0., 5800.), id='car loan phase-out exact'),
    # Part IV smoothed: 10000 - 0.2 * 20500
    pytest.param({'MARS': 1, 'c00100': 120500.,
                  'auto_loan_interest': 12000.},
                 (0., 0., 0., 5900.), id='car loan phase-out smoothed'),
    # Part IV: married filing separately can claim
    pytest.param({'MARS': 3, 'c00100': 60000.,
                  'auto_loan_interest': 3000.},
                 (0., 0., 0., 3000.), id='car loan separate'),
    # Part IV: 10000 - 0.2 * (320000 - 200000) < 0
    pytest.param({'MARS': 2, 'c00100': 320000.,
                  'auto_loan_interest': 12000.},
                 (0., 0., 0., 0.), id='car loan phased out'),
])
def test_MiscDed(call_calcfunc, rvars, expected):
    """
    Tests the MiscDed function against 2025 Schedule 1-A logic
    """
    actual = call_calcfunc('MiscDed', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# ItemDed
# ----------------------------------------------------------------------


# ItemDed test cases use the 2025 current-law values, which match the
# 2025 Schedule A:
#   line 3 medical floor is 7.5 percent of AGI;
#   line 5e SALT cap is 40000 (20000 when married filing separately),
#     reduced by 30 percent of AGI above 500000 (250000 when married
#     filing separately), but not below 10000 (5000 when married filing
#     separately);
#   line 14 charity is limited to 60 percent of AGI, with noncash gifts
#     limited to 30 percent of AGI;
#   line 15 casualty losses and line 16 other deductions are zero under
#     Tax-Calculator current law (ID_Casualty_hc and ID_Miscellaneous_hc
#     are both one).
# The Pease limitation (ID_ps, ID_prt, ID_crt), the top-bracket reduction
# (ID_reduction_rate), and the total cap (ID_c) have no 2025 Schedule A
# counterpart and are inert under 2025 current law.  The returned tuple
# is (c17000, c18300, c19200, c19700, c20500, c20800, c21040, c21060,
# c04470), which are Schedule A lines 4, 7, 10, 14, 15, and 16, the
# Pease reduction, line 17, and the itemized deduction.
ID_PEASE_REFORM = {
    'ID_ps': {2025: [300000., 300000., 300000., 300000., 300000.]},
    'ID_prt': {2025: 0.03},
    'ID_crt': {2025: 0.8},
}
ID_REDUCTION_REFORM = {'ID_reduction_rate': {2025: 0.05}}
ID_CAP_REFORM = {'ID_c': {2025: [25000., 25000., 25000., 25000., 25000.]}}
ID_ALL_ITEMS = {
    'MARS': 1, 'c00100': 100000., 'e17500': 10000., 'e18400': 8000.,
    'e18500': 7000., 'e19200': 12000., 'e19800': 10000., 'e20100': 5000.,
    'g20500': 5000., 'e20400': 5000.,
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # line 4: 10000 - 0.075 * 100000
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e17500': 10000.},
                 (2500., 0., 0., 0., 0., 0., 0., 2500., 2500.),
                 id='medical'),
    # line 4: expenses below the 7.5 percent floor
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e17500': 5000.},
                 (0., 0., 0., 0., 0., 0., 0., 0., 0.),
                 id='medical below floor'),
    # line 4: negative AGI means a zero floor
    pytest.param(None, {'MARS': 1, 'c00100': -5000., 'e17500': 1000.},
                 (1000., 0., 0., 0., 0., 0., 0., 1000., 1000.),
                 id='medical negative AGI'),
    # line 7: 8000 + 7000 is below the 40000 cap
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e18400': 8000.,
                        'e18500': 7000.},
                 (0., 15000., 0., 0., 0., 0., 0., 15000., 15000.),
                 id='SALT below cap'),
    # line 7: min(30000 + 20000, 40000)
    pytest.param(None, {'MARS': 2, 'c00100': 200000., 'e18400': 30000.,
                        'e18500': 20000.},
                 (0., 40000., 0., 0., 0., 0., 0., 40000., 40000.),
                 id='SALT cap'),
    # line 7: min(30000, 20000) when married filing separately
    pytest.param(None, {'MARS': 3, 'c00100': 100000., 'e18400': 30000.},
                 (0., 20000., 0., 0., 0., 0., 0., 20000., 20000.),
                 id='SALT cap separate'),
    # line 7: min(50000, 40000 - 0.3 * (550000 - 500000))
    pytest.param(None, {'MARS': 1, 'c00100': 550000., 'e18400': 50000.},
                 (0., 25000., 0., 0., 0., 0., 0., 25000., 25000.),
                 id='SALT cap phase-out'),
    # line 7: min(50000, max(40000 - 0.3 * (700000 - 500000), 10000))
    pytest.param(None, {'MARS': 1, 'c00100': 700000., 'e18400': 50000.},
                 (0., 10000., 0., 0., 0., 0., 0., 10000., 10000.),
                 id='SALT cap floor'),
    # line 7: min(50000, 20000 - 0.3 * (275000 - 250000))
    pytest.param(None, {'MARS': 3, 'c00100': 275000., 'e18400': 50000.},
                 (0., 12500., 0., 0., 0., 0., 0., 12500., 12500.),
                 id='SALT cap phase-out separate'),
    # line 7: min(50000, max(20000 - 0.3 * (350000 - 250000), 5000))
    pytest.param(None, {'MARS': 3, 'c00100': 350000., 'e18400': 50000.},
                 (0., 5000., 0., 0., 0., 0., 0., 5000., 5000.),
                 id='SALT cap floor separate'),
    # line 10: interest is not limited
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e19200': 12000.},
                 (0., 0., 12000., 0., 0., 0., 0., 12000., 12000.),
                 id='interest'),
    # line 14: 10000 + 5000 is below the AGI limits
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e19800': 10000.,
                        'e20100': 5000.},
                 (0., 0., 0., 15000., 0., 0., 0., 15000., 15000.),
                 id='charity'),
    # line 14: noncash gifts limited to 0.3 * 100000
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e20100': 40000.},
                 (0., 0., 0., 30000., 0., 0., 0., 30000., 30000.),
                 id='charity noncash limit'),
    # line 14: total gifts limited to 0.6 * 100000
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e19800': 80000.},
                 (0., 0., 0., 60000., 0., 0., 0., 60000., 60000.),
                 id='charity total limit'),
    # line 14: 20000 + min(0.3 * 100000, 40000) = 50000 is below
    # 0.6 * 100000
    pytest.param(None, {'MARS': 1, 'c00100': 100000., 'e19800': 20000.,
                        'e20100': 40000.},
                 (0., 0., 0., 50000., 0., 0., 0., 50000., 50000.),
                 id='charity cash and noncash limit'),
    # line 17: 2500 + 15000 + 12000 + 15000 + 0 + 0
    pytest.param(None, ID_ALL_ITEMS,
                 (2500., 15000., 12000., 15000., 0., 0., 0., 44500.,
                  44500.),
                 id='all items'),
    # Pease reform: line 17 = 2500 + 15000 + 12000 + 15000 = 44500;
    # AGI below the 300000 Pease threshold, so no reduction
    pytest.param(ID_PEASE_REFORM, ID_ALL_ITEMS,
                 (2500., 15000., 12000., 15000., 0., 0., 0., 44500.,
                  44500.),
                 id='Pease reform below threshold'),
    # Pease reform: line 4 = 40000 - 0.075 * 400000 = 10000;
    # line 17 = 10000 + 20000 + 10000 = 40000;
    # reduction = min(0.8 * (40000 - 10000), 0.03 * (400000 - 300000))
    pytest.param(ID_PEASE_REFORM, {'MARS': 1, 'c00100': 400000.,
                                   'e17500': 40000., 'e18400': 20000.,
                                   'e19200': 10000.},
                 (10000., 20000., 10000., 0., 0., 0., 3000., 40000.,
                  37000.),
                 id='Pease reform'),
    # reduction reform: taxable income 700000 exceeds the 626350 top
    # bracket threshold by 73650; 20000 - 0.05 * 73650
    pytest.param(ID_REDUCTION_REFORM, {'MARS': 1, 'c00100': 700000.,
                                       'e19200': 20000.},
                 (0., 0., 20000., 0., 0., 0., 0., 20000., 16317.5),
                 id='reduction reform'),
    # reduction reform: taxable income below the top bracket threshold
    pytest.param(ID_REDUCTION_REFORM, {'MARS': 1, 'c00100': 600000.,
                                       'e19200': 20000.},
                 (0., 0., 20000., 0., 0., 0., 0., 20000., 20000.),
                 id='reduction reform below threshold'),
    # cap reform: min(44500, 25000)
    pytest.param(ID_CAP_REFORM, ID_ALL_ITEMS,
                 (2500., 15000., 12000., 15000., 0., 0., 0., 44500.,
                  25000.),
                 id='cap reform'),
])
def test_ItemDed(call_calcfunc, reform, rvars, expected):
    """
    Tests the ItemDed function against 2025 Schedule A logic
    """
    actual = call_calcfunc('ItemDed', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AdditionalMedicareTax
# ----------------------------------------------------------------------


# AdditionalMedicareTax test cases use the 2025 current-law values,
# which match 2025 Form 8959: a 0.009 rate (line 7 and line 13) and a
# threshold (line 5 and line 9) of 200000 (250000 when married filing
# jointly and 125000 when married filing separately).  A qualifying
# surviving spouse (MARS 5) uses the 200000 threshold on Form 8959 but
# the 250000 threshold on Form 8960.  Sch SE line 4a keeps 0.9235 of
# self-employment earnings.


@pytest.mark.parametrize('rvars, expected', [
    # Part I: 0.009 * (300000 - 200000)
    pytest.param({'MARS': 1, 'e00200': 300000.}, 900., id='single'),
    # Part I: 0.009 * (300000 - 250000)
    pytest.param({'MARS': 2, 'e00200': 300000.}, 450., id='joint'),
    # Part I: 0.009 * (300000 - 125000)
    pytest.param({'MARS': 3, 'e00200': 300000.}, 1575., id='separate'),
    # Part I: 0.009 * (300000 - 200000)
    pytest.param({'MARS': 4, 'e00200': 300000.}, 900.,
                 id='head of household'),
    # Part I: 0.009 * (300000 - 200000)
    pytest.param({'MARS': 5, 'e00200': 300000.}, 900.,
                 id='surviving spouse'),
    # Part I: wages at the threshold produce no tax
    pytest.param({'MARS': 1, 'e00200': 200000.}, 0.,
                 id='wages at threshold'),
    # Part II: line 8 = 0.9235 * 100000 = 92350;
    # line 11 = 200000 - 150000 = 50000; line 13 = 0.009 * 42350
    pytest.param({'MARS': 1, 'e00200': 150000., 'e00900p': 100000.},
                 381.15, id='SE uses remaining threshold'),
    # line 18 adds Part I and Part II: line 7 = 0.009 * 100000 = 900;
    # line 11 = 0, so line 13 = 0.009 * 92350 = 831.15
    pytest.param({'MARS': 1, 'e00200': 300000., 'e00900p': 100000.},
                 1731.15, id='both parts'),
    # every per-spouse component of Sch SE line 6 reaches line 8:
    # line 8 = 0.9235 * (60000 + 6000) = 60951; wages equal the joint
    # threshold, so line 11 = 0 and line 13 = 0.009 * 60951
    pytest.param({'MARS': 2, 'e00200': 250000.,
                  'e00900p': 10000., 'e00900s': 1000.,
                  'e02100p': 20000., 'e02100s': 2000.,
                  'k1bx14p': 30000., 'k1bx14s': 3000.},
                 548.559, id='SE components'),
    # each spouse files a separate Sch SE, so the spouse loss does not
    # offset the taxpayer profit: line 8 = 0.9235 * 300000 = 277050;
    # line 13 = 0.009 * 277050 (flooring only the sum of the spouses
    # would give 0.009 * 0.9235 * 200000 = 1662.30)
    pytest.param({'MARS': 2, 'e00200': 250000.,
                  'e00900p': 300000., 'e00900s': -100000.},
                 2493.45, id='SE floors each spouse'),
    # line 1 Medicare wages (W-2 box 5) include the pension
    # contributions that e00200 (W-2 box 1) excludes:
    # line 1 = 230000 + 15000 + 10000 = 255000;
    # line 7 = 0.009 * (255000 - 250000)
    pytest.param({'MARS': 2, 'e00200': 230000.,
                  'pencon_p': 15000., 'pencon_s': 10000.},
                 45., id='pension contributions'),
    # a spouse whose Sch SE line 4c amount is below $400 has no SE
    # income on line 8: line 8 = 0.9235 * 10000 = 9235 (the spouse's
    # 277.05 is excluded); line 11 = 0, so line 13 = 0.009 * 9235
    pytest.param({'MARS': 2, 'e00200': 250000.,
                  'e00900p': 10000., 'e00900s': 300.},
                 83.115, id='SE floor per spouse'),
])
def test_AdditionalMedicareTax(call_calcfunc, rvars, expected):
    """
    Tests the AdditionalMedicareTax function against 2025 Form 8959
    logic: Part I (lines 1-7) taxes Medicare wages above the threshold,
    Part II (lines 8-13) taxes self-employment income above what remains
    of the threshold, and line 18 adds the two parts
    """
    actual = call_calcfunc('AdditionalMedicareTax', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# StdDed
# ----------------------------------------------------------------------


# StdDed test cases use 2025 current-law policy values, which match the
# 2025 Form 1040 line 12 standard deduction chart:
#   STD = [15750, 31500, 15750, 23625, 31500] by MARS, and
#   STD_Aged = [2000, 1600, 1600, 2000, 1600] by MARS per 65+/blind box,
# and the 2025 Standard Deduction Worksheet for Dependents:
#   STD_Dep_earned_add = 450 (line 2) and STD_Dep = 1350 (line 4).
# The 2025 nonitemizer charitable deduction ceiling is zero.


@pytest.mark.stded
@pytest.mark.parametrize('rvars, expected', [
    # line 12 chart: single, under 65 and not blind
    pytest.param({'MARS': 1, 'age_head': 45}, 15750., id='single'),
    # line 12 chart: single, 65 or older: 15750 + 2000
    pytest.param({'MARS': 1, 'age_head': 66}, 17750., id='single aged'),
    # line 12 chart: single, 65 or older and blind: 15750 + 2 * 2000
    pytest.param({'MARS': 1, 'age_head': 66, 'blind_head': 1}, 19750.,
                 id='single aged blind'),
    # line 12 chart: married filing jointly, both under 65
    pytest.param({'MARS': 2, 'age_head': 45, 'age_spouse': 44}, 31500.,
                 id='joint'),
    # line 12 chart: married filing jointly, spouse 65 or older:
    # 31500 + 1600
    pytest.param({'MARS': 2, 'age_head': 44, 'age_spouse': 66}, 33100.,
                 id='joint spouse aged'),
    # line 12 chart: married filing jointly, both 65 or older and
    # spouse blind: 31500 + 3 * 1600
    pytest.param({'MARS': 2, 'age_head': 66, 'age_spouse': 67,
                  'blind_spouse': 1},
                 36300., id='joint both aged spouse blind'),
    # line 12 chart: married filing separately, 65 or older:
    # 15750 + 1600; spouse boxes count only on a joint return, so the
    # spouse age and blindness are ignored
    pytest.param({'MARS': 3, 'age_head': 66, 'age_spouse': 70,
                  'blind_spouse': 1},
                 17350., id='separate aged'),
    # line 12 instructions: married filing separately and spouse
    # itemizes, so the standard deduction is zero
    pytest.param({'MARS': 3, 'age_head': 66, 'MIDR': 1}, 0.,
                 id='separate spouse itemizes'),
    # line 12 chart: head of household, 65 or older: 23625 + 2000
    pytest.param({'MARS': 4, 'age_head': 66}, 25625., id='head aged'),
    # line 12 chart: qualifying surviving spouse, blind: 31500 + 1600
    pytest.param({'MARS': 5, 'age_head': 50, 'blind_head': 1}, 33100.,
                 id='surviving spouse blind'),
    # dependent worksheet: line 3 = 500 + 450 = 950;
    # line 5 = max(950, 1350) = 1350; result = min(1350, 15750)
    pytest.param({'MARS': 1, 'DSI': 1, 'age_head': 16, 'earned': 500.}, 1350.,
                 id='dependent low earnings'),
    # dependent worksheet: line 3 = 5000 + 450 = 5450;
    # line 5 = max(5450, 1350) = 5450; result = min(5450, 15750)
    pytest.param({'MARS': 1, 'DSI': 1, 'age_head': 20, 'earned': 5000.}, 5450.,
                 id='dependent middle earnings'),
    # dependent worksheet: line 3 = 20000 + 450 = 20450;
    # line 5 = max(20450, 1350) = 20450; result = min(20450, 15750)
    pytest.param({'MARS': 1, 'DSI': 1, 'age_head': 20, 'earned': 20000.},
                 15750., id='dependent high earnings'),
    # dependent worksheet: min(5450, 15750) as above plus one 65+/blind
    # box amount for a blind single dependent: 5450 + 2000
    pytest.param({'MARS': 1, 'DSI': 1, 'age_head': 20, 'earned': 5000.,
                  'blind_head': 1}, 7450., id='dependent blind'),
    # cash charitable contributions do not raise the standard deduction
    # because the 2025 nonitemizer charitable deduction ceiling is zero
    pytest.param({'MARS': 1, 'age_head': 45, 'e19800': 1000.}, 15750.,
                 id='single with charity'),
])
def test_StdDed(call_calcfunc, rvars, expected):
    """
    Tests the StdDed function against 2025 Form 1040 line 12 logic
    """
    actual = call_calcfunc('StdDed', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# TaxInc
# ----------------------------------------------------------------------


# TaxInc test cases use the 2025 current-law QBI deduction parameters,
# which match 2025 Form 8995 and Form 8995-A: a 20 percent deduction
# rate, a taxable income threshold of 197300 (394600 when married filing
# jointly), and a phase-in range of 50000 (100000 when married filing
# jointly).  The minimum QBI deduction does not begin until 2026.
# The returned tuple is (c04800, qbided).
QBID_MIN_REFORM = {
    'PT_qbid_min_ded': {2025: 400},
    'PT_qbid_min_qbi': {2025: 1000},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # Form 1040 line 15: 80000 - 15750 with no QBI
    pytest.param(None,
                 {'MARS': 1, 'c00100': 80000., 'standard': 15750.},
                 (64250., 0.), id='no QBI'),
    # Form 1040 line 12 is the larger of itemized and standard
    # deductions: 100000 - 25000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 100000., 'standard': 15750.,
                  'c04470': 25000.},
                 (75000., 0.), id='itemizer'),
    # Sch 1-A deductions (Form 1040 line 13b) are subtracted:
    # 80000 - 17750 - (6000 + 5000 + 3000 + 1000)
    pytest.param(None,
                 {'MARS': 1, 'c00100': 80000., 'standard': 17750.,
                  'senior_deduction': 6000., 'tip_income_deduction': 5000.,
                  'overtime_income_deduction': 3000.,
                  'auto_loan_interest_deduction': 1000.},
                 (47250., 0.), id='Sch 1-A deductions'),
    # Form 8995: QBI = 100000 - 7000 (deductible SE tax) = 93000;
    # line 5 = 0.2 * 93000 = 18600; line 11 = 200000 - 31500 = 168500;
    # line 14 = 0.2 * 168500 = 33700; line 15 = 18600
    pytest.param(None,
                 {'MARS': 2, 'c00100': 200000., 'standard': 31500.,
                  'e00900': 100000., 'c03260': 7000.},
                 (149900., 18600.), id='Form 8995'),
    # Form 8995: line 5 = 0.2 * 50000 = 10000; line 11 = 44250;
    # line 12 = 10000 qualified dividends; line 14 = 0.2 * 34250 = 6850
    pytest.param(None,
                 {'MARS': 1, 'c00100': 60000., 'standard': 15750.,
                  'e26270': 50000., 'e00650': 10000.},
                 (37400., 6850.), id='Form 8995 income limit'),
    # Form 8995: line 12 net capital gain = 10000 LTCG - 4000 STCL;
    # line 14 = 0.2 * (44250 - 6000) = 7650
    pytest.param(None,
                 {'MARS': 1, 'c00100': 60000., 'standard': 15750.,
                  'e26270': 50000., 'p22250': -4000., 'p23250': 10000.},
                 (36600., 7650.), id='Form 8995 net capital gain'),
    # Form 8995-A above the 247300 phase-in end: line 3 = 60000;
    # line 5 = 0.5 * 80000 = 40000; line 9 = 0.25 * 80000 = 20000;
    # line 11 = min(60000, 40000); line 36 = 0.2 * 384250 = 76850
    pytest.param(None,
                 {'MARS': 1, 'c00100': 400000., 'standard': 15750.,
                  'e26270': 300000., 'PT_binc_w2_wages': 80000.},
                 (344250., 40000.), id='Form 8995-A wage limit'),
    # Form 8995-A: line 5 = 0.5 * 20000 = 10000;
    # line 9 = 0.25 * 20000 + 0.025 * 1000000 = 30000;
    # line 11 = min(60000, 30000)
    pytest.param(None,
                 {'MARS': 1, 'c00100': 400000., 'standard': 15750.,
                  'e26270': 300000., 'PT_binc_w2_wages': 20000.,
                  'PT_ubia_property': 1e6},
                 (354250., 30000.), id='Form 8995-A UBIA limit'),
    # Form 8995-A: an SSTB above the phase-in end gets no deduction
    pytest.param(None,
                 {'MARS': 1, 'c00100': 400000., 'standard': 15750.,
                  'e26270': 300000., 'PT_binc_w2_wages': 80000.,
                  'PT_SSTB_income': 1},
                 (384250., 0.), id='Form 8995-A SSTB above phase-in'),
    # Form 8995-A Part III: taxable income 222000; line 24 =
    # (222000 - 197300) / 50000 = 0.494; line 3 = 20000; line 10 =
    # 0.5 * 10000 = 5000; line 25 = 0.494 * (20000 - 5000) = 7410;
    # line 26 = 20000 - 7410 = 12590
    pytest.param(None,
                 {'MARS': 1, 'c00100': 237750., 'standard': 15750.,
                  'e26270': 100000., 'PT_binc_w2_wages': 10000.},
                 (209410., 12590.), id='Form 8995-A phase-in'),
    # Form 8995-A Schedule A: applicable percentage =
    # (247300 - 222000) / 50000 = 0.506; line 3 = 0.506 * 20000 = 10120;
    # line 10 = 0.506 * 5000 = 2530; line 25 = 0.494 * (10120 - 2530) =
    # 3749.46; line 26 = 10120 - 3749.46 = 6370.54
    pytest.param(None,
                 {'MARS': 1, 'c00100': 237750., 'standard': 15750.,
                  'e26270': 100000., 'PT_binc_w2_wages': 10000.,
                  'PT_SSTB_income': 1},
                 (215629.46, 6370.54), id='Form 8995-A SSTB phase-in'),
    # Form 8995-A Part III with joint filers: taxable income 419600;
    # line 24 = (419600 - 394600) / 100000 = 0.25; line 3 = 40000;
    # line 10 = 0.5 * 20000 = 10000; line 25 = 0.25 * 30000 = 7500;
    # line 26 = 40000 - 7500 = 32500
    pytest.param(None,
                 {'MARS': 2, 'c00100': 451100., 'standard': 31500.,
                  'e26270': 200000., 'PT_binc_w2_wages': 20000.},
                 (387100., 32500.), id='Form 8995-A joint phase-in'),
    # reform-only minimum deduction: QBI 1500 at least 1000, so the
    # deduction rises from 0.2 * 1500 = 300 to 400
    pytest.param(QBID_MIN_REFORM,
                 {'MARS': 1, 'c00100': 50000., 'standard': 15750.,
                  'e00900': 1500.},
                 (33850., 400.), id='reform minimum deduction'),
    # reform-only minimum deduction: QBI 900 below 1000, so no minimum
    pytest.param(QBID_MIN_REFORM,
                 {'MARS': 1, 'c00100': 50000., 'standard': 15750.,
                  'e00900': 900.},
                 (34070., 180.), id='reform QBI below minimum'),
])
def test_TaxInc(call_calcfunc, reform, rvars, expected):
    """
    Tests the TaxInc function against 2025 Form 1040 line 15 logic and
    2025 Form 8995 and Form 8995-A logic
    """
    actual = call_calcfunc('TaxInc', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# SchXYZ
# ----------------------------------------------------------------------


# SchXYZ test cases use the 2025 current-law rates and brackets, which
# match the 2025 Tax Rate Schedules X, Y-1, Y-2, and Z.
TOP_BRACKET_REFORM = {
    'II_brk7': {2025: [20e6, 20e6, 20e6, 20e6, 20e6]},
    'II_rt8': {2025: 0.44},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # Schedule X: 1192.50 + 0.12 * (48475 - 11925)
    #             + 0.22 * (50000 - 48475)
    pytest.param(None, {'MARS': 1, 'taxable_income': 50000.}, 5914.,
                 id='single'),
    # Schedule X: 188769.75 + 0.37 * (1000000 - 626350)
    pytest.param(None, {'MARS': 1, 'taxable_income': 1e6}, 327020.25,
                 id='single top bracket'),
    # Schedule Y-1: 2385 + 0.12 * (96950 - 23850)
    #               + 0.22 * (100000 - 96950)
    pytest.param(None, {'MARS': 2, 'taxable_income': 100000.}, 11828.,
                 id='joint'),
    # Schedule Y-2: 101077.25 + 0.37 * (400000 - 375800)
    pytest.param(None, {'MARS': 3, 'taxable_income': 400000.},
                 110031.25, id='separate top bracket'),
    # Schedule Z: 1700 + 0.12 * (60000 - 17000)
    pytest.param(None, {'MARS': 4, 'taxable_income': 60000.}, 6860.,
                 id='head of household'),
    # Schedule Y-1 is used by a qualifying surviving spouse:
    # 2385 + 0.12 * (50000 - 23850)
    pytest.param(None, {'MARS': 5, 'taxable_income': 50000.}, 5523.,
                 id='surviving spouse'),
    # no tax on zero or negative taxable income
    pytest.param(None, {'MARS': 1, 'taxable_income': -1000.}, 0.,
                 id='negative taxable income'),
    # reform with a 44 percent rate above 20 million:
    # 188769.75 + 0.37 * (20000000 - 626350)
    #           + 0.44 * (100000000 - 20000000)
    pytest.param(TOP_BRACKET_REFORM,
                 {'MARS': 1, 'taxable_income': 100e6}, 42557020.25,
                 id='reform new top bracket'),
])
def test_SchXYZ(call_calcfunc, reform, rvars, expected):
    """
    Tests the SchXYZ function against the 2025 Tax Rate Schedules
    """
    actual = call_calcfunc('SchXYZ', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# SchXYZTax
# ----------------------------------------------------------------------


# SchXYZTax routes regular taxable income (c04800, Form 1040 line 15)
# through the SchXYZ function, so its test cases use the 2025
# current-law rates and brackets, which match the 2025 Tax Rate
# Schedules X, Y-1, Y-2, and Z.  The returned value is c05200, the tax
# on all taxable income computed without the capital-gains preference.


@pytest.mark.parametrize('reform, rvars, expected', [
    # Schedule X: 1192.50 + 0.12 * (48475 - 11925)
    #             + 0.22 * (50000 - 48475)
    pytest.param(None, {'MARS': 1, 'c04800': 50000.}, 5914.,
                 id='single'),
    # Schedule Y-1: 2385 + 0.12 * (96950 - 23850)
    #               + 0.22 * (100000 - 96950)
    pytest.param(None, {'MARS': 2, 'c04800': 100000.}, 11828.,
                 id='joint'),
    # Schedule Y-2: 101077.25 + 0.37 * (400000 - 375800)
    pytest.param(None, {'MARS': 3, 'c04800': 400000.}, 110031.25,
                 id='separate top bracket'),
    # Schedule Z: 1700 + 0.12 * (60000 - 17000)
    pytest.param(None, {'MARS': 4, 'c04800': 60000.}, 6860.,
                 id='head of household'),
    # Schedule Y-1 is used by a qualifying surviving spouse:
    # 2385 + 0.12 * (50000 - 23850)
    pytest.param(None, {'MARS': 5, 'c04800': 50000.}, 5523.,
                 id='surviving spouse'),
    # no tax on zero taxable income, and any prior c05200 value is
    # overwritten
    pytest.param(None, {'MARS': 1, 'c04800': 0., 'c05200': 999.}, 0.,
                 id='zero taxable income'),
    # reform with a 44 percent rate above 20 million:
    # 188769.75 + 0.37 * (20000000 - 626350)
    #           + 0.44 * (100000000 - 20000000)
    pytest.param(TOP_BRACKET_REFORM, {'MARS': 1, 'c04800': 100e6},
                 42557020.25, id='reform new top bracket'),
])
def test_SchXYZTax(call_calcfunc, reform, rvars, expected):
    """
    Tests the SchXYZTax function against the 2025 Tax Rate Schedules
    """
    actual = call_calcfunc('SchXYZTax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# GainsTax
# ----------------------------------------------------------------------


# GainsTax test cases use the 2025 current-law values, which match the
# 2025 Qualified Dividends and Capital Gain Tax Worksheet (QDCGTW) and
# the 2025 Schedule D Tax Worksheet (Sch D TW): a 0% rate up to line 15
# amounts of 48350 (96700 when married filing jointly), a 15% rate up to
# line 25 amounts of 533400 (600050 when married filing jointly), and a
# 20% rate above that.  Each c05200 value is the Tax Rate Schedule tax
# on c04800 (see test_SchXYZTax).  The CG_rt4 and CG_brk3 parameters
# define a reform-only fourth rate bracket that is inert under 2025
# current law; like the line 15 and line 25 amounts, CG_brk3 is a
# taxable-income threshold with gains stacked on top of ordinary
# income.  The returned tuple is
# (dwks10, dwks13, dwks14, dwks18, dwks43, c05700, taxbc).
CG_NODIFF_REFORM = {'CG_nodiff': {2025: True}}
CG_BRK3_REFORM = {
    'CG_brk3': {2025: [1e6, 1e6, 1e6, 1e6, 1e6]},
    'CG_rt4': {2025: 0.25},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # no qualified dividends or capital gains: taxbc = c05200
    pytest.param(None, {'MARS': 1, 'c04800': 50000., 'c05200': 5914.},
                 (0., 0., 0., 0., 0., 0., 5914.), id='no gains'),
    # QDCGTW: line 4 = 10000; line 5 = 50000 - 10000 = 40000;
    # line 9 = 48350 - 40000 = 8350 @ 0%; line 17 = 10000 - 8350
    # = 1650 @ 15%; line 22 = 1192.50 + 0.12 * (40000 - 11925);
    # line 23 = 0.15 * 1650 + 4561.50
    pytest.param(None,
                 {'MARS': 1, 'c04800': 50000., 'c05200': 5914.,
                  'e00650': 10000.},
                 (10000., 10000., 40000., 40000., 4809., 0., 4809.),
                 id='qualified dividends'),
    # Form 4952 line 4g election of 4000 reduces qualified dividends to
    # 6000: line 9 = 48350 - 44000 = 4350 @ 0%; 1650 @ 15%;
    # 1192.50 + 0.12 * (44000 - 11925) + 0.15 * 1650
    pytest.param(None,
                 {'MARS': 1, 'c04800': 50000., 'c05200': 5914.,
                  'e00650': 10000., 'e58990': 4000.},
                 (6000., 6000., 44000., 44000., 5289., 0., 5289.),
                 id='investment interest election'),
    # QDCGTW with capital gain distributions (no Sch D) for joint filers:
    # line 9 = 96700 - 80000 = 16700 @ 0%; 3300 @ 15%;
    # 2385 + 0.12 * (80000 - 23850) + 0.15 * 3300
    pytest.param(None,
                 {'MARS': 2, 'c04800': 100000., 'c05200': 11828.,
                  'e01100': 20000.},
                 (20000., 20000., 80000., 80000., 9618., 0., 9618.),
                 id='joint cap gain distributions'),
    # short-term gain only: no preferential-rate income, so the
    # worksheet tax equals the Tax Rate Schedule tax
    pytest.param(None,
                 {'MARS': 1, 'c04800': 50000., 'c05200': 5914.,
                  'c23650': 10000.},
                 (0., 0., 50000., 50000., 5914., 0., 5914.),
                 id='short-term gain only'),
    # long-term gain of 200000 all taxed @ 20%:
    # 188769.75 + 0.37 * (800000 - 626350) + 0.20 * 200000
    pytest.param(None,
                 {'MARS': 1, 'c04800': 1e6, 'c05200': 327020.25,
                  'p23250': 200000., 'c23650': 200000.},
                 (200000., 200000., 800000., 800000., 293020.25, 0.,
                  293020.25),
                 id='long-term gain top rate'),
    # Sch D TW with 30000 of un-recaptured section 1250 gain:
    # line 13 = 100000 - 30000; line 18 = 300000 - 100000;
    # 70000 @ 15% + 30000 @ 25% + Schedule X tax on 200000 of 41063
    pytest.param(None,
                 {'MARS': 1, 'c04800': 300000., 'c05200': 74547.25,
                  'p23250': 100000., 'c23650': 100000.,
                  'e24515': 30000.},
                 (100000., 70000., 230000., 200000., 59063., 0., 59063.),
                 id='section 1250 gain'),
    # Sch D TW with 30000 of 28% rate gain:
    # 70000 @ 15% + 30000 @ 28% + Schedule X tax on 200000 of 41063
    pytest.param(None,
                 {'MARS': 1, 'c04800': 300000., 'c05200': 74547.25,
                  'p23250': 100000., 'c23650': 100000.,
                  'e24518': 30000.},
                 (100000., 70000., 230000., 200000., 59963., 0., 59963.),
                 id='28 percent rate gain'),
    # reform-only CG_nodiff taxes qualified dividends at ordinary rates
    pytest.param(CG_NODIFF_REFORM,
                 {'MARS': 1, 'c04800': 50000., 'c05200': 5914.,
                  'e00650': 10000.},
                 (0., 0., 0., 0., 0., 0., 5914.), id='reform nodiff'),
    # reform-only fourth bracket taxes long-term gain stacked above
    # 1000000 of taxable income at 25%: the 1200000 gain occupies
    # taxable income from 800000 to 2000000, so 1000000 is above the
    # threshold: 188769.75 + 0.37 * (800000 - 626350) + 0.20 * 1200000
    #            + (0.25 - 0.20) * (2000000 - 1000000)
    pytest.param(CG_BRK3_REFORM,
                 {'MARS': 1, 'c04800': 2e6, 'c05200': 697020.25,
                  'p23250': 1.2e6, 'c23650': 1.2e6},
                 (1.2e6, 1.2e6, 800000., 800000., 543020.25, 0.,
                  543020.25),
                 id='reform fourth bracket'),
    # reform-only fourth bracket with ordinary income of 1500000 above
    # the 1000000 threshold, so all 200000 of long-term gain is taxed at
    # 25%: 188769.75 + 0.37 * (1500000 - 626350) + 0.25 * 200000
    pytest.param(CG_BRK3_REFORM,
                 {'MARS': 1, 'c04800': 1.7e6, 'c05200': 586020.25,
                  'p23250': 200000., 'c23650': 200000.},
                 (200000., 200000., 1.5e6, 1.5e6, 562020.25, 0.,
                  562020.25),
                 id='reform fourth bracket all gain'),
])
def test_GainsTax(call_calcfunc, reform, rvars, expected):
    """
    Tests the GainsTax function against the 2025 Qualified Dividends and
    Capital Gain Tax Worksheet and the 2025 Schedule D Tax Worksheet
    """
    actual = call_calcfunc('GainsTax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AGIsurtax
# ----------------------------------------------------------------------


# AGIsurtax is a reform-only construct with no IRS form; AGI_surtax_trt
# is zero under 2025 current law, whose AGI_surtax_thd values are all
# 9e+99.  The returned tuple is (taxbc, surtax).
AGI_SURTAX_REFORM = {
    'AGI_surtax_trt': {2025: 0.02},
    'AGI_surtax_thd': {2025: [1e6, 2e6, 1e6, 1.5e6, 2e6]},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no AGI surtax; taxbc unchanged
    pytest.param(None,
                 {'MARS': 1, 'c00100': 3e6, 'taxbc': 900000.},
                 (900000., 0.), id='current law'),
    # reform, single above threshold: 0.02 * (3000000 - 1000000)
    pytest.param(AGI_SURTAX_REFORM,
                 {'MARS': 1, 'c00100': 3e6, 'taxbc': 900000.},
                 (940000., 40000.), id='reform single'),
    # reform, joint above threshold: 0.02 * (3000000 - 2000000)
    pytest.param(AGI_SURTAX_REFORM,
                 {'MARS': 2, 'c00100': 3e6, 'taxbc': 850000.},
                 (870000., 20000.), id='reform joint'),
    # reform, head of household above threshold:
    # 0.02 * (2000000 - 1500000)
    pytest.param(AGI_SURTAX_REFORM,
                 {'MARS': 4, 'c00100': 2e6, 'taxbc': 600000.},
                 (610000., 10000.), id='reform head of household'),
    # reform, AGI below threshold
    pytest.param(AGI_SURTAX_REFORM,
                 {'MARS': 1, 'c00100': 800000., 'taxbc': 200000.},
                 (200000., 0.), id='reform below threshold'),
    # reform, surtax adds to existing surtax accumulator:
    # 0.02 * (1500000 - 1000000) = 10000
    pytest.param(AGI_SURTAX_REFORM,
                 {'MARS': 1, 'c00100': 1.5e6, 'taxbc': 400000.,
                  'surtax': 5000.},
                 (410000., 15000.), id='reform surtax accumulation'),
])
def test_AGIsurtax(call_calcfunc, reform, rvars, expected):
    """
    Tests the AGIsurtax function
    """
    actual = call_calcfunc('AGIsurtax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AMT
# ----------------------------------------------------------------------


# AMT test cases use the 2025 current-law values, which match 2025 Form
# 6251: a line 5 exemption of 88100 (137000 when married filing jointly
# or a qualifying surviving spouse) that is reduced by 25% of AMTI above
# 626350 (1252700 when married filing jointly or a qualifying surviving
# spouse), a 26% rate up to a line 7 amount of 239100 and 28% above
# that, and Part III capital gains rates that match the 2025 QDCGTW and
# Sch D TW (see test_GainsTax).  The IRC 59(j) exemption for a filer
# under age 18 is limited to earned income plus 9550.  Each taxbc value
# is the regular tax on the implied taxable income (see test_SchXYZTax
# and test_GainsTax).  The pre-2017 AMT medical deduction add-back
# (AMT_Medical_frt) is inert under 2025 current law, as is the
# reform-only fourth Part III rate bracket defined by the AMT_CG_rt4 and
# AMT_CG_brk3 parameters, where, like the line 19 and line 25 amounts,
# AMT_CG_brk3 is a taxable-income threshold with gains stacked on top of
# ordinary income.  The returned tuple is (c62100, c09600, c05800),
# which are Form 6251 line 4, Form 6251 line 11, and Form 1040 line 16
# plus Sch 2 line 1.
AMT_MEDICAL_REFORM = {'AMT_Medical_frt': {2025: 0.025}}
AMT_CG_BRK3_REFORM = {
    'AMT_CG_brk3': {2025: [1e6, 1e6, 1e6, 1e6, 1e6]},
    'AMT_CG_rt4': {2025: 0.25},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # nonitemizer: line 4 = AGI; line 6 = 100000 - 88100 = 11900;
    # line 9 = 0.26 * 11900 = 3094 is less than regular tax of 13449
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 100000.,
                  'taxbc': 13449.},
                 (100000., 0., 13449.), id='nonitemizer no amt'),
    # nonitemizer: line 1a subtracts QBID and the Sch 1-A tip, overtime,
    # and auto loan interest deductions: 100000 - 5000 - 10000 - 3000
    # - 2000 = 80000, which is less than the exemption
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 100000.,
                  'qbided': 5000., 'tip_income_deduction': 10000.,
                  'overtime_income_deduction': 3000.,
                  'auto_loan_interest_deduction': 2000., 'taxbc': 8000.},
                 (80000., 0., 8000.), id='sch 1-A deductions'),
    # joint itemizer: line 4 = 400000 - 60000 + 40000 (line 2a SALT)
    # - 5000 (line 2b refund) = 375000; line 6 = 375000 - 137000
    # = 238000; line 9 = 0.26 * 238000 = 61880 is less than regular
    # tax on 340000 of 67294
    pytest.param(None,
                 {'MARS': 2, 'c00100': 400000., 'c04470': 60000.,
                  'c18300': 40000., 'e00700': 5000., 'taxbc': 67294.},
                 (375000., 0., 67294.), id='itemizer no amt'),
    # joint itemizer with 100000 of line 2i ISO preference: line 4
    # = 400000 - 60000 + 40000 + 100000 = 480000; line 6 = 343000;
    # line 7 = 0.26 * 343000 + 0.02 * (343000 - 239100) = 91258;
    # line 11 = 91258 - 67294
    pytest.param(None,
                 {'MARS': 2, 'c00100': 400000., 'c04470': 60000.,
                  'c18300': 40000., 'cmbtp': 100000., 'taxbc': 67294.},
                 (480000., 23964., 91258.), id='itemizer iso preference'),
    # as above with a regular FTC of 2000 and no Form 6251 filed:
    # line 8 = 2000; line 10 = 67294 - 2000; line 11 unchanged
    pytest.param(None,
                 {'MARS': 2, 'c00100': 400000., 'c04470': 60000.,
                  'c18300': 40000., 'cmbtp': 100000., 'taxbc': 67294.,
                  'e07300': 2000.},
                 (480000., 23964., 91258.), id='regular ftc'),
    # as above with Form 6251 filed and an AMT FTC of 1000:
    # line 9 = 91258 - 1000; line 11 = 90258 - (67294 - 2000) = 24964
    pytest.param(None,
                 {'MARS': 2, 'c00100': 400000., 'c04470': 60000.,
                  'c18300': 40000., 'cmbtp': 100000., 'taxbc': 67294.,
                  'e07300': 2000., 'f6251': 1, 'e62900': 1000.},
                 (480000., 24964., 92258.), id='amt ftc'),
    # reform-only (pre-2017 law) medical add-back:
    # min(20000, 0.025 * 400000) = 10000 increases line 4 to 385000
    pytest.param(AMT_MEDICAL_REFORM,
                 {'MARS': 2, 'c00100': 400000., 'c04470': 60000.,
                  'c18300': 40000., 'c17000': 20000., 'e00700': 5000.,
                  'taxbc': 67294.},
                 (385000., 0., 67294.), id='reform medical add-back'),
    # nonitemizer with 300000 of line 2i ISO preference: line 4
    # = 1000000; line 5 = 88100 - 0.25 * (1000000 - 626350) < 0;
    # line 7 = 0.26 * 1000000 + 0.02 * (1000000 - 239100) = 275218;
    # line 11 = 275218 - 210192.75 (regular tax on 684250)
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 700000.,
                  'cmbtp': 300000., 'taxbc': 210192.75},
                 (1e6, 65025.25, 275218.), id='exemption phased out'),
    # IRC 59(j) filer under age 18 with no earned income:
    # line 5 = min(88100, 0 + 9550); line 6 = 60000 - 9550 = 50450;
    # line 7 = 0.26 * 50450 = 13117; line 11 = 13117 - 5000
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 60000.,
                  'age_head': 15, 'taxbc': 5000.},
                 (60000., 8117., 13117.), id='kiddie exemption'),
    # Part III with 100000 of long-term gain and 150000 of ISO
    # preference: line 6 = 450000 - 88100 = 361900;
    # line 17 = 361900 - 100000 = 261900;
    # line 18 = 0.26 * 261900 + 0.02 * (261900 - 239100) = 68550;
    # line 21 = 0; line 30 = 100000 @ 15% = 15000;
    # line 38 = 83550 < line 39 = 0.26 * 361900 + 0.02 * 122800;
    # line 11 = 83550 - 52067 (regular tax on 284250)
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 300000.,
                  'cmbtp': 150000., 'dwks10': 100000., 'dwks13': 100000.,
                  'dwks14': 184250., 'dwks18': 184250., 'taxbc': 52067.},
                 (450000., 31483., 83550.), id='part III 15 percent'),
    # Part III for joint filers with 60000 of long-term gain and 300000
    # of ISO preference: line 6 = 441500 - 137000 = 304500;
    # line 17 = 244500; line 18 = 0.26 * 244500 + 0.02 * 5400 = 63678;
    # line 21 = 96700 - 50000 = 46700 @ 0%; line 30 = 13300 @ 15%;
    # line 38 = 63678 + 1995 = 65673;
    # line 11 = 65673 - 7518 (regular tax on 110000)
    pytest.param(None,
                 {'MARS': 2, 'standard': 31500., 'c00100': 141500.,
                  'cmbtp': 300000., 'dwks10': 60000., 'dwks13': 60000.,
                  'dwks14': 50000., 'dwks18': 50000., 'taxbc': 7518.},
                 (441500., 58155., 65673.), id='part III zero percent'),
    # Part III with 600000 of long-term gain and 500000 of ISO
    # preference: line 5 = 0; line 6 = 1215750; line 17 = 615750;
    # line 18 = 0.26 * 615750 + 0.02 * 376650 = 167628;
    # line 29 = 533400 - 100000 = 433400 @ 15% = 65010;
    # line 33 = 166600 @ 20% = 33320; line 38 = 265958;
    # line 11 = 265958 - 115244 (regular tax on 700000)
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 715750.,
                  'cmbtp': 500000., 'dwks10': 600000., 'dwks13': 600000.,
                  'dwks14': 100000., 'dwks18': 100000., 'taxbc': 115244.},
                 (1215750., 150714., 265958.), id='part III 20 percent'),
    # reform-only fourth bracket taxes long-term gain stacked above
    # 1000000 of taxable income at 25%: with 1200000 of long-term gain
    # and 500000 of ISO preference, line 6 = 1815750; line 17 = 615750;
    # line 18 = 167628; line 28 = 100000; line 30 = 433400 @ 15%
    # = 65010; line 33 = 766600 @ 20% = 153320; line 33 occupies
    # taxable income from 533400 to 1300000, so
    # (0.25 - 0.20) * (1300000 - 1000000) = 15000; line 38 = 400958;
    # line 11 = 400958 - 235244 (regular tax on 1300000)
    pytest.param(AMT_CG_BRK3_REFORM,
                 {'MARS': 1, 'standard': 15750., 'c00100': 1315750.,
                  'cmbtp': 500000., 'dwks10': 1.2e6, 'dwks13': 1.2e6,
                  'dwks14': 100000., 'dwks18': 100000., 'taxbc': 235244.},
                 (1815750., 165714., 400958.), id='reform fourth bracket'),
    # Part III with 30000 of unrecaptured section 1250 gain (see the
    # test_GainsTax section 1250 case) and 200000 of ISO preference:
    # line 6 = 515750 - 88100 = 427650; line 15 = 100000;
    # line 17 = 327650; line 18 = 0.26 * 327650 + 0.02 * 88550 = 86960;
    # line 30 = 70000 @ 15% = 10500; line 36 = 30000 @ 25% = 7500;
    # line 38 = 104960; line 11 = 104960 - 59063
    pytest.param(None,
                 {'MARS': 1, 'standard': 15750., 'c00100': 315750.,
                  'cmbtp': 200000., 'dwks10': 100000., 'dwks13': 70000.,
                  'dwks14': 230000., 'dwks18': 200000., 'e24515': 30000.,
                  'taxbc': 59063.},
                 (515750., 45897., 104960.), id='part III section 1250'),
])
def test_AMT(call_calcfunc, reform, rvars, expected):
    """
    Tests the AMT function against 2025 Form 6251
    """
    actual = call_calcfunc('AMT', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# NetInvIncTax
# ----------------------------------------------------------------------


# NetInvIncTax test cases use the 2025 current-law values, which match
# 2025 Form 8960: a 0.038 rate (line 17) and a threshold (line 14) of
# 200000 (250000 when married filing jointly or a qualifying surviving
# spouse and 125000 when married filing separately).  The e02000 and
# e26270 values differ so that the line 4b adjustment is nonzero.
NIIT_INCOME = {'e00300': 10000., 'e00600': 5000., 'e02000': 20000.,
               'e26270': 5000., 'c01000': 15000.}
NIIT_PT_TAXED_REFORM = {'NIIT_PT_taxed': {2025: True}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # line 8 = 10000 + 5000 + (20000 - 5000) + 15000 = 45000;
    # line 15 = 100000; line 16 = min(45000, 100000);
    # line 17 = 0.038 * 45000
    pytest.param(None, {**NIIT_INCOME, 'MARS': 1, 'c00100': 300000.},
                 1710., id='nii below excess'),
    # reform-only NIIT_PT_taxed drops the line 4b adjustment, so line 12
    # rises by e26270 and the tax by 0.038 * 5000
    pytest.param(NIIT_PT_TAXED_REFORM,
                 {**NIIT_INCOME, 'MARS': 1, 'c00100': 300000.},
                 1900., id='reform pt taxed'),
    # modified AGI at the line 14 threshold: line 15 is zero
    pytest.param(None, {**NIIT_INCOME, 'MARS': 1, 'c00100': 200000.},
                 0., id='magi at threshold'),
    # line 15 = 10000 below line 12 = 45000: 0.038 * 10000
    pytest.param(None, {**NIIT_INCOME, 'MARS': 1, 'c00100': 210000.},
                 380., id='excess below nii'),
    # negative investment income is floored at zero by line 12
    pytest.param(None,
                 {'MARS': 1, 'e02000': -50000., 'c01000': -3000.,
                  'c00100': 300000.},
                 0., id='negative nii'),
    # joint filers: line 15 = 270000 - 250000; 0.038 * 20000
    pytest.param(None, {**NIIT_INCOME, 'MARS': 2, 'c00100': 270000.},
                 760., id='joint threshold'),
    # qualifying surviving spouse uses the joint threshold
    pytest.param(None, {**NIIT_INCOME, 'MARS': 5, 'c00100': 270000.},
                 760., id='surviving spouse threshold'),
    # married filing separately: line 15 = 150000 - 125000;
    # 0.038 * 25000
    pytest.param(None, {**NIIT_INCOME, 'MARS': 3, 'c00100': 150000.},
                 950., id='separate threshold'),
])
def test_NetInvIncTax(call_calcfunc, reform, rvars, expected):
    """
    Tests the NetInvIncTax function against 2025 Form 8960 lines 12-17:
    the tax is the line 17 rate applied to the lesser of net investment
    income (line 12) and the excess of modified AGI over the
    MARS-indexed line 14 threshold (line 15)
    """
    actual = call_calcfunc('NetInvIncTax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# F2441
# ----------------------------------------------------------------------


# F2441 test cases use the 2025 current-law values, which match 2025
# Form 2441 Part II: a line 3 expense limit of 3000 per qualifying
# person for at most two persons, and a line 8 decimal amount of 0.35
# that is reduced by 0.01 for each 2000 (or fraction thereof) of AGI
# above 15000, but not below 0.20.  The exact flag selects the form's
# whole-step rounding.  The line 10 Credit Limit Worksheet amount is
# the Form 1040 line 18 tax less the Sch 3 line 1 foreign tax credit.
# The second phase-down (CDCC_ps2, CDCC_po2_step_size, and
# CDCC_po2_rate_min), which begins in 2026, is inert in 2025, as is the
# reform-only CDCC_refundable switch.  The returned tuple is
# (c32800, c07180, CDCC_refund), which are Form 2441 line 3, Form 2441
# line 11, and the refundable credit amount.
CDCC_PS2_REFORM = {
    'CDCC_ps2': {2025: [75000, 150000, 75000, 75000, 75000]},
    'CDCC_po2_step_size': {2025: [2000, 4000, 2000, 2000, 2000]},
    'CDCC_po2_rate_min': {2025: 0.},
}
CDCC_REFUNDABLE_REFORM = {'CDCC_refundable': {2025: True}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # line 3 = min(5000, 3000); line 6 = 3000; line 8 = 0.35 - 0.01 *
    # ceil((40000 - 15000) / 2000) = 0.22; line 9a = 0.22 * 3000 = 660
    pytest.param(None,
                 {'MARS': 1, 'f2441': 1, 'e32800': 5000., 'exact': 1,
                  'earned_p': 40000., 'c00100': 40000., 'c05800': 5000.},
                 (3000., 660., 0.), id='one person'),
    # line 3 = min(10000, 2 * 3000); line 8 = 0.35 at AGI of 15000;
    # line 9a = 0.35 * 6000 = 2100
    pytest.param(None,
                 {'MARS': 4, 'f2441': 3, 'e32800': 10000., 'exact': 1,
                  'earned_p': 15000., 'c00100': 15000., 'c05800': 5000.},
                 (6000., 2100., 0.), id='three persons capped at two'),
    # as above, but line 11 is limited to the line 10 tax of 1000
    pytest.param(None,
                 {'MARS': 4, 'f2441': 2, 'e32800': 10000., 'exact': 1,
                  'earned_p': 15000., 'c00100': 15000., 'c05800': 1000.},
                 (6000., 1000., 0.), id='tax limit'),
    # line 10 = 1000 - 400 foreign tax credit
    pytest.param(None,
                 {'MARS': 4, 'f2441': 2, 'e32800': 10000., 'exact': 1,
                  'earned_p': 15000., 'c00100': 15000., 'c05800': 1000.,
                  'e07300': 400.},
                 (6000., 600., 0.), id='foreign tax credit'),
    # AGI of 16000 is in the first 2000 step above 15000:
    # line 8 = 0.35 - 0.01 = 0.34; line 9a = 0.34 * 3000 = 1020
    pytest.param(None,
                 {'MARS': 1, 'f2441': 1, 'e32800': 3000., 'exact': 1,
                  'earned_p': 16000., 'c00100': 16000., 'c05800': 5000.},
                 (3000., 1020., 0.), id='exact rounding'),
    # without exact rounding: line 8 = 0.35 - 0.01 * 0.5 = 0.345;
    # line 9a = 0.345 * 3000 = 1035
    pytest.param(None,
                 {'MARS': 1, 'f2441': 1, 'e32800': 3000., 'exact': 0,
                  'earned_p': 16000., 'c00100': 16000., 'c05800': 5000.},
                 (3000., 1035., 0.), id='no exact rounding'),
    # joint filers: line 6 is limited by the spouse's line 5 earned
    # income of 4000; line 8 = 0.20 at AGI of 100000; 0.20 * 4000
    pytest.param(None,
                 {'MARS': 2, 'f2441': 2, 'e32800': 8000., 'exact': 1,
                  'earned_p': 96000., 'earned_s': 4000., 'c00100': 100000.,
                  'c05800': 10000.},
                 (6000., 800., 0.), id='joint spouse earnings limit'),
    # joint filers: a spouse with no earned income makes line 6 zero
    pytest.param(None,
                 {'MARS': 2, 'f2441': 1, 'e32800': 3000., 'exact': 1,
                  'earned_p': 50000., 'c00100': 50000., 'c05800': 5000.},
                 (3000., 0., 0.), id='joint spouse no earnings'),
    # unmarried filers: line 5 is the line 4 amount, so line 6 =
    # min(3000, 2000); line 8 = 0.35; 0.35 * 2000
    pytest.param(None,
                 {'MARS': 4, 'f2441': 1, 'e32800': 3000., 'exact': 1,
                  'earned_p': 2000., 'c00100': 12000., 'c05800': 5000.},
                 (3000., 700., 0.), id='taxpayer earnings limit'),
    # reform second phase-down for joint filers: line 8 = 0.20 - 0.01 *
    # ceil((170000 - 150000) / 4000) = 0.15; 0.15 * 6000
    pytest.param(CDCC_PS2_REFORM,
                 {'MARS': 2, 'f2441': 2, 'e32800': 6000., 'exact': 1,
                  'earned_p': 85000., 'earned_s': 85000.,
                  'c00100': 170000., 'c05800': 20000.},
                 (6000., 900., 0.), id='reform second phase-down'),
    # reform second phase-down for a single filer: line 8 = max(0,
    # 0.20 - 0.01 * ceil((150000 - 75000) / 2000))
    pytest.param(CDCC_PS2_REFORM,
                 {'MARS': 1, 'f2441': 1, 'e32800': 3000., 'exact': 1,
                  'earned_p': 150000., 'c00100': 150000.,
                  'c05800': 30000.},
                 (3000., 0., 0.), id='reform second phase-down to zero'),
    # reform refundable credit: the full line 9a amount of
    # 0.35 * 3000 = 1050 is refundable despite zero tax
    pytest.param(CDCC_REFUNDABLE_REFORM,
                 {'MARS': 4, 'f2441': 1, 'e32800': 3000., 'exact': 1,
                  'earned_p': 12000., 'c00100': 12000.},
                 (3000., 0., 1050.), id='reform refundable'),
])
def test_F2441(call_calcfunc, reform, rvars, expected):
    """
    Tests the F2441 function against 2025 Form 2441 Part II logic
    """
    actual = call_calcfunc('F2441', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# EITCamount
# ----------------------------------------------------------------------


# EITC test cases use the 2025 current-law EITC parameters, which match
# the 2025 Form 1040 instructions (EIC Worksheet A and the EIC Table) and
# Pub 596, indexed by the number of qualifying children (0, 1, 2, 3+):
#   phase-in rate  = [0.0765, 0.34, 0.40, 0.45]
#   maximum credit = [649, 4328, 7152, 8046]
#   phase-out start = [10620, 23350, 23350, 23350]
#     (plus [7110, 7120, 7120, 7120] when married filing jointly)
#   phase-out rate = [0.0765, 0.1598, 0.2106, 0.2106]
#   investment income limit = 11950
# The expected values use the formula behind the EIC Table rather than
# the table's $50 income bands.


@pytest.mark.parametrize('earnings, agi, expected', [
    # phase-in: 0.45 * 10000
    pytest.param(10000., 10000., 4500., id='phase-in'),
    # plateau: min(0.45 * 20000, 8046)
    pytest.param(20000., 20000., 8046., id='plateau'),
    # phase-out: 8046 - 0.2106 * (30000 - 23350)
    pytest.param(30000., 30000., 6645.51, id='phase-out'),
    # EIC Worksheet A line 6: AGI above the phase-out start, so the
    # smaller of the earned-income credit (4500) and the AGI credit
    # (6645.51) is allowed
    pytest.param(10000., 30000., 4500., id='AGI above earnings'),
    # earnings credit (6645.51) is smaller than the AGI credit (8046)
    pytest.param(30000., 20000., 6645.51, id='earnings above AGI'),
    # 8046 - 0.2106 * (70000 - 23350) < 0
    pytest.param(70000., 70000., 0., id='phased out'),
])
def test_EITCamount(earnings, agi, expected):
    """
    Tests the EITCamount function using the 2025 EITC parameters for a
    filer with three or more qualifying children who is not married
    filing jointly
    """
    actual = calcfunctions.EITCamount(0., 0.45, earnings, 8046., 23350.,
                                      agi, 0.2106)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# EITC
# ----------------------------------------------------------------------


@pytest.mark.parametrize('rvars, expected', [
    # three children: min(0.45 * 20000, 8046)
    pytest.param({'MARS': 4, 'EIC': 3, 'earned': 20000.,
                  'c00100': 20000.}, 8046., id='three children plateau'),
    # one child: 4328 - 0.1598 * (30000 - 23350)
    pytest.param({'MARS': 1, 'EIC': 1, 'earned': 30000.,
                  'c00100': 30000.}, 3265.33, id='one child phase-out'),
    # two children, joint: phase-out start = 23350 + 7120 = 30470;
    # 7152 - 0.2106 * (40000 - 30470)
    pytest.param({'MARS': 2, 'EIC': 2, 'earned': 40000.,
                  'c00100': 40000.}, 5144.982, id='two children joint'),
    # no children, age 30: 0.0765 * 8000
    pytest.param({'MARS': 1, 'EIC': 0, 'age_head': 30, 'earned': 8000.,
                  'c00100': 8000.}, 612., id='no children'),
    # Pub 596 rule 11: no children and under age 25
    pytest.param({'MARS': 1, 'EIC': 0, 'age_head': 22, 'earned': 8000.,
                  'c00100': 8000.}, 0., id='no children under 25'),
    # Pub 596 rule 11: no children and over age 64
    pytest.param({'MARS': 1, 'EIC': 0, 'age_head': 70, 'earned': 8000.,
                  'c00100': 8000.}, 0., id='no children over 64'),
    # Pub 596 rule 11: joint filers need only one spouse aged 25-64:
    # 0.0765 * 8000
    pytest.param({'MARS': 2, 'EIC': 0, 'age_head': 22, 'age_spouse': 30,
                  'earned': 8000., 'c00100': 8000.}, 612.,
                 id='no children joint one spouse eligible'),
    # Pub 596 rule 3: a separated spouse filing separately may claim
    # the credit, using the non-joint phase-out start: min(0.34 * 15000,
    # 4328)
    pytest.param({'MARS': 3, 'EIC': 1, 'earned': 15000.,
                  'c00100': 15000.}, 4328., id='separate'),
    # Pub 596 rule 10: a filer claimed as a dependent cannot claim
    pytest.param({'MARS': 1, 'EIC': 1, 'DSI': 1, 'earned': 15000.,
                  'c00100': 15000.}, 0., id='dependent'),
    # Pub 596 rule 6: investment income 11950 is not above the limit:
    # 8046 - 0.2106 * (31950 - 23350)
    pytest.param({'MARS': 4, 'EIC': 3, 'earned': 20000.,
                  'c00100': 31950., 'e00300': 11950.}, 6234.84,
                 id='investment income at limit'),
    # Pub 596 rule 6: taxable interest above the limit
    pytest.param({'MARS': 4, 'EIC': 3, 'earned': 20000.,
                  'c00100': 32000., 'e00300': 12000.}, 0.,
                 id='interest above limit'),
    # Pub 596 rule 6: capital gain net income above the limit
    pytest.param({'MARS': 4, 'EIC': 3, 'earned': 20000.,
                  'c00100': 33000., 'c01000': 13000.}, 0.,
                 id='capital gain above limit'),
])
def test_EITC(call_calcfunc, rvars, expected):
    """
    Tests the EITC function against 2025 EIC logic
    """
    actual = call_calcfunc('EITC', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# ChildDepTaxCredit
# ----------------------------------------------------------------------


# ChildDepTaxCredit test cases use the 2025 current-law values, which
# match the 2025 Schedule 8812: a 2200 child tax credit per qualifying
# child (line 5), a 500 credit for other dependents (line 7), and a
# phase-out of 0.05 times modified AGI above 200000 (400000 when
# married filing jointly) that on the form is first rounded up to the
# next multiple of 1000 (line 10).  The exact flag selects that
# rounding.  Schedule 8812 line 14 reports only the total nonrefundable
# credit; Tax-Calculator splits it between CTC and ODC in proportion to
# lines 5 and 7.  The returned tuple is (c07220, odc, codtc_limited).


@pytest.mark.parametrize('rvars, expected', [
    # line 5 = 2 * 2200 = 4400; line 14 = min(4400, 10000)
    pytest.param({'MARS': 2, 'num': 2, 'XTOT': 4, 'n24': 2,
                  'c00100': 100000., 'c05800': 10000.},
                 (4400., 0., 0.), id='two children'),
    # line 14 = min(4400, 3000) = 3000; 1400 left for Part II
    pytest.param({'MARS': 2, 'num': 2, 'XTOT': 4, 'n24': 2,
                  'c00100': 100000., 'c05800': 3000.},
                 (3000., 0., 1400.), id='tax limited'),
    # line 5 = 2200; line 7 = 500 * (3 - 1 - 1) = 500; line 14 = 2700
    pytest.param({'MARS': 4, 'num': 1, 'XTOT': 3, 'n24': 1,
                  'c00100': 60000., 'c05800': 5000.},
                 (2200., 500., 0.), id='child and other dependent'),
    # line 14 = min(2700, 1000) = 1000, split 2200:500 between CTC and
    # ODC as 814.8148 and 185.1852; 1700 left for Part II
    pytest.param({'MARS': 4, 'num': 1, 'XTOT': 3, 'n24': 1,
                  'c00100': 30000., 'c05800': 1000.},
                 (1000. * 2200. / 2700., 1000. * 500. / 2700., 1700.),
                 id='child and other dependent tax limited'),
    # a 17-year-old is not a qualifying child, but is an other
    # dependent: line 7 = 500 * (3 - 0 - 2)
    pytest.param({'MARS': 2, 'num': 2, 'XTOT': 3, 'nu18': 1,
                  'c00100': 80000., 'c05800': 5000.},
                 (0., 500., 0.), id='other dependent age 17'),
    # line 10 = 16000 after rounding 15500 up; line 11 = 800;
    # line 12 = 2200 - 800
    pytest.param({'MARS': 1, 'num': 1, 'XTOT': 2, 'n24': 1,
                  'c00100': 215500., 'c05800': 40000., 'exact': 1},
                 (1400., 0., 0.), id='phase-out exact'),
    # without rounding: 2200 - 0.05 * 15500
    pytest.param({'MARS': 1, 'num': 1, 'XTOT': 2, 'n24': 1,
                  'c00100': 215500., 'c05800': 40000.},
                 (1425., 0., 0.), id='phase-out smoothed'),
    # line 11 = 0.05 * 100000 = 5000 exceeds line 8 = 2200
    pytest.param({'MARS': 2, 'num': 2, 'XTOT': 3, 'n24': 1,
                  'c00100': 500000., 'c05800': 100000.},
                 (0., 0., 0.), id='phased out'),
    # Credit Limit Worksheet A: 5000 - (1000 + 1500 + 500) = 2000;
    # line 14 = min(4400, 2000); 2400 left for Part II
    pytest.param({'MARS': 2, 'num': 2, 'XTOT': 4, 'n24': 2,
                  'c00100': 100000., 'c05800': 5000., 'c07180': 1000.,
                  'c07230': 1500., 'e07240': 500.},
                 (2000., 0., 2400.), id='other credits limit'),
])
def test_ChildDepTaxCredit(call_calcfunc, rvars, expected):
    """
    Tests the ChildDepTaxCredit function against 2025 Schedule 8812 logic
    """
    actual = call_calcfunc('ChildDepTaxCredit', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# PersonalTaxCredit
# ----------------------------------------------------------------------


# PersonalTaxCredit computes reform-only personal credits and the
# recovery rebate credit, which was on the 2020 and 2021 Form 1040 but
# not on the 2025 Form 1040; all their parameters are zero under 2025
# current law.  The returned tuple is (personal_refundable_credit,
# personal_nonrefundable_credit, recovery_rebate_credit).
PERSONAL_CREDIT_REFORM = {
    'II_credit': {2025: [1000, 2000, 1000, 1500, 2000]},
    'II_credit_ps': {2025: [50000, 100000, 50000, 75000, 100000]},
    'II_credit_prt': {2025: 0.05},
    'II_credit_nr': {2025: [300, 600, 300, 450, 600]},
    'II_credit_nr_ps': {2025: [40000, 80000, 40000, 60000, 80000]},
    'II_credit_nr_prt': {2025: 0.01},
}
# ARPA-style recovery rebate credit applied in 2025
RRC_PERSON_REFORM = {
    'RRC_c': {2025: 1400},
    'RRC_ps': {2025: [75000, 150000, 75000, 112500, 150000]},
    'RRC_pe': {2025: [80000, 160000, 80000, 120000, 160000]},
}
# CARES-style recovery rebate credit applied in 2025
RRC_UNIT_REFORM = {
    'RRC_c_unit': {2025: [1200, 2400, 1200, 1200, 2400]},
    'RRC_c_kids': {2025: 500},
    'RRC_prt': {2025: 0.05},
    'RRC_ps': {2025: [75000, 150000, 75000, 112500, 150000]},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: all three credits are zero
    pytest.param(None,
                 {'MARS': 2, 'c00100': 80000., 'XTOT': 4, 'nu18': 2},
                 (0., 0., 0.), id='current law'),
    # 2025 current law with negative AGI
    pytest.param(None,
                 {'MARS': 1, 'c00100': -5000., 'XTOT': 1},
                 (0., 0., 0.), id='current law negative AGI'),
    # reform: joint AGI below both phase-out starts
    pytest.param(PERSONAL_CREDIT_REFORM, {'MARS': 2, 'c00100': 75000.},
                 (2000., 600., 0.), id='personal credits below ps'),
    # reform: refundable 2000 - 0.05 * 20000 = 1000;
    # nonrefundable 600 - 0.01 * 40000 = 200
    pytest.param(PERSONAL_CREDIT_REFORM, {'MARS': 2, 'c00100': 120000.},
                 (1000., 200., 0.), id='personal credits phasing out'),
    # reform: refundable 2000 - 0.05 * 50000 < 0;
    # nonrefundable 600 - 0.01 * 70000 < 0
    pytest.param(PERSONAL_CREDIT_REFORM, {'MARS': 2, 'c00100': 150000.},
                 (0., 0., 0.), id='personal credits phased out'),
    # ARPA-style reform: 1400 * 1 below phase-out start
    pytest.param(RRC_PERSON_REFORM,
                 {'MARS': 1, 'c00100': 50000., 'XTOT': 1},
                 (0., 0., 1400.), id='ARPA-style below ps'),
    # ARPA-style reform: 1400 * (1 - (76000 - 75000) / 5000)
    pytest.param(RRC_PERSON_REFORM,
                 {'MARS': 1, 'c00100': 76000., 'XTOT': 1},
                 (0., 0., 1120.), id='ARPA-style phasing out'),
    # ARPA-style reform: AGI above phase-out end
    pytest.param(RRC_PERSON_REFORM,
                 {'MARS': 1, 'c00100': 90000., 'XTOT': 1},
                 (0., 0., 0.), id='ARPA-style phased out'),
    # CARES-style reform: 2400 + 2 * 500 below phase-out start
    pytest.param(RRC_UNIT_REFORM,
                 {'MARS': 2, 'c00100': 100000., 'XTOT': 4, 'nu18': 2},
                 (0., 0., 3400.), id='CARES-style below ps'),
    # CARES-style reform: 3400 - 0.05 * (160000 - 150000)
    pytest.param(RRC_UNIT_REFORM,
                 {'MARS': 2, 'c00100': 160000., 'XTOT': 4, 'nu18': 2},
                 (0., 0., 2900.), id='CARES-style phasing out'),
])
def test_PersonalTaxCredit(call_calcfunc, reform, rvars, expected):
    """
    Tests the PersonalTaxCredit function
    """
    actual = call_calcfunc('PersonalTaxCredit', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AmOppCreditParts
# ----------------------------------------------------------------------


# AmOppCreditParts test cases follow 2025 Form 8863 Part I, whose
# amounts are hardcoded in the function: a line 2 phase-out base of
# 90000 (180000 when married filing jointly) and a line 5 phase-out
# range of 10000 (20000 when married filing jointly), which is why num
# is specified in every case.  The exact flag rounds the line 6
# fraction to three decimals.  Line 8 is 0.4 of line 7 and the Part II
# line 9 nonrefundable amount is the rest of line 7.  The reform-only
# CR_AmOppRefundable_hc and CR_AmOppNonRefundable_hc haircuts are zero
# under 2025 current law.  The returned tuple is (c10960, c87668),
# which are Form 8863 line 8 and Part II line 9.
AOTC_HAIRCUT_REFORM = {
    'CR_AmOppRefundable_hc': {2025: 0.5},
    'CR_AmOppNonRefundable_hc': {2025: 0.2},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # no tentative credit on line 1
    pytest.param(None, {'num': 1, 'c00100': 50000.},
                 (0., 0.), id='no credit'),
    # line 4 = 90000 - 50000 exceeds line 5, so line 6 = 1.000;
    # line 7 = 2500; line 8 = 0.4 * 2500; line 9 = 2500 - 1000
    pytest.param(None, {'num': 1, 'c00100': 50000., 'e87521': 2500.},
                 (1000., 1500.), id='below phase-out'),
    # line 6 = (90000 - 85000) / 10000 = 0.500; line 7 = 1250
    pytest.param(None,
                 {'num': 1, 'c00100': 85000., 'e87521': 2500., 'exact': 1},
                 (500., 750.), id='phasing out'),
    # line 6 = 3333 / 10000 rounded to 0.333; line 7 = 832.5
    pytest.param(None,
                 {'num': 1, 'c00100': 86667., 'e87521': 2500., 'exact': 1},
                 (333., 499.5), id='exact rounding'),
    # without exact rounding: line 7 = 0.3333 * 2500 = 833.25
    pytest.param(None,
                 {'num': 1, 'c00100': 86667., 'e87521': 2500., 'exact': 0},
                 (333.3, 499.95), id='no exact rounding'),
    # MAGI above the 90000 line 2 amount: line 4 = 0
    pytest.param(None, {'num': 1, 'c00100': 95000., 'e87521': 2500.},
                 (0., 0.), id='phased out'),
    # joint filers: line 6 = (180000 - 175000) / 20000 = 0.250;
    # line 7 = 0.25 * 5000 = 1250
    pytest.param(None,
                 {'num': 2, 'c00100': 175000., 'e87521': 5000., 'exact': 1},
                 (500., 750.), id='joint phasing out'),
    # reform haircuts: line 8 = 0.5 * 1000; line 9 = 0.8 * 1500
    pytest.param(AOTC_HAIRCUT_REFORM,
                 {'num': 1, 'c00100': 50000., 'e87521': 2500.},
                 (500., 1200.), id='reform haircuts'),
])
def test_AmOppCreditParts(call_calcfunc, reform, rvars, expected):
    """
    Tests the AmOppCreditParts function against 2025 Form 8863 Part I
    lines 1-8 and the Part II line 9 nonrefundable amount
    """
    actual = call_calcfunc('AmOppCreditParts', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# SchR
# ----------------------------------------------------------------------


# SchR test cases follow 2025 Schedule R Part III, whose amounts are
# hardcoded in the function: a line 10 base amount of 5000 (7500 when
# married filing jointly with both spouses 65+ and 3750 when married
# filing separately) and a line 15 AGI threshold of 7500 (10000 when
# married filing jointly and 5000 when married filing separately).
# Line 13c is nontaxable social security benefits plus nontaxable
# pensions, line 17 is half the AGI excess over line 15, line 20 is
# 0.15 of line 19, and line 21 is c05800 minus e07300 and c07180.
# The reform-only CR_SchR_hc haircut is zero under 2025 current law.
SCHR_HAIRCUT_REFORM = {'CR_SchR_hc': {2025: 0.2}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # head under 65: not eligible
    pytest.param(None,
                 {'MARS': 1, 'age_head': 64, 'c00100': 5000.,
                  'c05800': 1000.},
                 0., id='under 65'),
    # Box 1: line 19 = 5000; line 20 = 0.15 * 5000
    pytest.param(None,
                 {'MARS': 1, 'age_head': 65, 'c00100': 5000.,
                  'c05800': 1000.},
                 750., id='single 65 below threshold'),
    # line 13a = 3000; line 17 = 0.5 * (9500 - 7500);
    # line 19 = 5000 - 4000; line 20 = 0.15 * 1000
    pytest.param(None,
                 {'MARS': 1, 'age_head': 65, 'c00100': 9500.,
                  'e02400': 3000., 'c05800': 1000.},
                 150., id='single 65 nontaxable OASDI and AGI excess'),
    # line 13b = 2000 - 1500; line 19 = 4500; line 20 = 0.15 * 4500
    pytest.param(None,
                 {'MARS': 1, 'age_head': 65, 'c00100': 5000.,
                  'e01500': 2000., 'e01700': 1500., 'c05800': 1000.},
                 675., id='single 65 nontaxable pensions'),
    # Box 1: line 17 = 0.5 * (20000 - 7500) exceeds line 10
    pytest.param(None,
                 {'MARS': 4, 'age_head': 70, 'c00100': 20000.,
                  'c05800': 1000.},
                 0., id='head of household 70 phased out'),
    # Box 3: line 17 = 0.5 * (12000 - 10000);
    # line 19 = 7500 - 1000; line 20 = 0.15 * 6500
    pytest.param(None,
                 {'MARS': 2, 'age_head': 66, 'age_spouse': 67,
                  'c00100': 12000., 'c05800': 2000.},
                 975., id='joint both 65+'),
    # Box 7: only spouse 65+; line 19 = 5000; line 20 = 0.15 * 5000
    pytest.param(None,
                 {'MARS': 2, 'age_head': 60, 'age_spouse': 66,
                  'c00100': 10000., 'c05800': 2000.},
                 750., id='joint spouse only 65+'),
    # Box 8: line 19 = 3750; line 20 = 0.15 * 3750
    pytest.param(None,
                 {'MARS': 3, 'age_head': 65, 'c00100': 5000.,
                  'c05800': 1000.},
                 562.5, id='separate 65'),
    # separate filer with only spouse 65+: not eligible
    pytest.param(None,
                 {'MARS': 3, 'age_head': 60, 'age_spouse': 66,
                  'c00100': 5000., 'c05800': 1000.},
                 0., id='separate spouse only 65+'),
    # line 21 = 900 - 100 - 200 is less than line 20 = 750
    pytest.param(None,
                 {'MARS': 1, 'age_head': 65, 'c00100': 5000.,
                  'c05800': 900., 'e07300': 100., 'c07180': 200.},
                 600., id='tax liability limit'),
    # reform haircut: 0.8 * 750
    pytest.param(SCHR_HAIRCUT_REFORM,
                 {'MARS': 1, 'age_head': 65, 'c00100': 5000.,
                  'c05800': 1000.},
                 600., id='reform haircut'),
])
def test_SchR(call_calcfunc, reform, rvars, expected):
    """
    Tests the SchR function against 2025 Schedule R Part III lines 10-22
    """
    actual = call_calcfunc('SchR', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# EducationTaxCredit
# ----------------------------------------------------------------------


# EducationTaxCredit test cases follow 2025 Form 8863 Part II lines 10-19
# and the Credit Limit Worksheet (CLW) in the Form 8863 instructions.
# Under 2025 current law the line 11 expense cap (LLC_Expense_c) is
# 10000 and the line 13 amount (ETC_pe_Single and ETC_pe_Married, in
# thousands) is 90000 (180000 when married filing jointly); the line 16
# phaseout spread is hardcoded as 10000 (20000 when married filing
# jointly).  CLW line 6 is c05800 minus e07300, c07180, and c07200.
# The reform-only CR_Education_hc haircut is zero under 2025 current law.
ETC_HAIRCUT_REFORM = {'CR_Education_hc': {2025: 0.2}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # no lifetime learning expenses and no nonrefundable AOTC
    pytest.param(None, {'MARS': 1, 'c00100': 50000., 'c05800': 5000.},
                 0., id='no credit'),
    # line 12 = 0.2 * 5000; line 17 = 1.000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 5000.,
                  'c05800': 5000.},
                 1000., id='below phase-out'),
    # line 11 = min(15000, 10000); line 12 = 0.2 * 10000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 15000.,
                  'c05800': 5000.},
                 2000., id='expense cap'),
    # line 17 = (90000 - 85000) / 10000 = 0.500; line 18 = 0.5 * 1000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 85000., 'e87530': 5000.,
                  'c05800': 5000., 'exact': 1},
                 500., id='phasing out'),
    # line 17 = 3333 / 10000 rounded to 0.333; line 18 = 0.333 * 1000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 86667., 'e87530': 5000.,
                  'c05800': 5000., 'exact': 1},
                 333., id='exact rounding'),
    # without exact rounding: line 18 = 0.3333 * 1000
    pytest.param(None,
                 {'MARS': 1, 'c00100': 86667., 'e87530': 5000.,
                  'c05800': 5000., 'exact': 0},
                 333.3, id='no exact rounding'),
    # AGI above the 90000 line 13 amount: line 15 = 0
    pytest.param(None,
                 {'MARS': 1, 'c00100': 95000., 'e87530': 5000.,
                  'c05800': 5000.},
                 0., id='phased out'),
    # joint filers: line 17 = (180000 - 175000) / 20000 = 0.250;
    # line 18 = 0.25 * 1000
    pytest.param(None,
                 {'MARS': 2, 'c00100': 175000., 'e87530': 5000.,
                  'c05800': 5000., 'exact': 1},
                 250., id='joint phasing out'),
    # line 9 nonrefundable AOTC is not subject to the line 13-17 phaseout
    pytest.param(None,
                 {'MARS': 1, 'c00100': 95000., 'c87668': 1500.,
                  'c05800': 5000.},
                 1500., id='nonrefundable AOTC only'),
    # CLW line 3 = 1000 + 1500
    pytest.param(None,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 5000.,
                  'c87668': 1500., 'c05800': 5000.},
                 2500., id='LLC and nonrefundable AOTC'),
    # CLW line 6 = 3000 - (500 + 700 + 300) is less than CLW line 3
    pytest.param(None,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 5000.,
                  'c87668': 1500., 'c05800': 3000., 'e07300': 500.,
                  'c07180': 700., 'c07200': 300.},
                 1500., id='tax liability limit'),
    # CLW line 5 exceeds CLW line 4, so CLW line 6 = 0
    pytest.param(None,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 5000.,
                  'c87668': 1500., 'c05800': 1000., 'e07300': 1500.},
                 0., id='no tax liability'),
    # reform haircut: 0.8 * 2500
    pytest.param(ETC_HAIRCUT_REFORM,
                 {'MARS': 1, 'c00100': 50000., 'e87530': 5000.,
                  'c87668': 1500., 'c05800': 5000.},
                 2000., id='reform haircut'),
])
def test_EducationTaxCredit(call_calcfunc, reform, rvars, expected):
    """
    Tests the EducationTaxCredit function against 2025 Form 8863 Part II
    lines 10-19 and the Form 8863 instructions Credit Limit Worksheet
    """
    actual = call_calcfunc('EducationTaxCredit', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# CharityCredit
# ----------------------------------------------------------------------


# CharityCredit is a reform-only nonrefundable credit for charitable
# giving with no 2025 IRS form; its parameters are zero under 2025
# current law.  The credit is CR_Charity_rt times the giving in excess
# of the larger of the MARS-indexed CR_Charity_f dollar floor and the
# CR_Charity_frt share of AGI.
CHARITY_RATE_REFORM = {'CR_Charity_rt': {2025: 0.25}}
CHARITY_FLOOR_REFORM = {
    'CR_Charity_rt': {2025: 0.25},
    'CR_Charity_f': {2025: [500, 1000, 500, 500, 1000]},
    'CR_Charity_frt': {2025: 0.02},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no charity credit
    pytest.param(None,
                 {'MARS': 1, 'e19800': 3000., 'c00100': 50000.},
                 0., id='current law'),
    # rate-only reform: 0.25 * (1500 + 500) with no floor
    pytest.param(CHARITY_RATE_REFORM,
                 {'MARS': 1, 'e19800': 1500., 'e20100': 500.,
                  'c00100': 50000.},
                 500., id='reform no floor'),
    # floor reform: no giving
    pytest.param(CHARITY_FLOOR_REFORM,
                 {'MARS': 1, 'c00100': 50000.},
                 0., id='reform no giving'),
    # floor = max(0.02 * 20000, 500) = 500; 0.25 * (3000 - 500)
    pytest.param(CHARITY_FLOOR_REFORM,
                 {'MARS': 1, 'e19800': 3000., 'c00100': 20000.},
                 625., id='reform dollar floor binds'),
    # floor = max(0.02 * 20000, 1000) = 1000; 0.25 * (3000 - 1000)
    pytest.param(CHARITY_FLOOR_REFORM,
                 {'MARS': 2, 'e19800': 3000., 'c00100': 20000.},
                 500., id='reform joint dollar floor binds'),
    # floor = max(0.02 * 100000, 500) = 2000; 0.25 * (3000 + 1000 - 2000)
    pytest.param(CHARITY_FLOOR_REFORM,
                 {'MARS': 1, 'e19800': 3000., 'e20100': 1000.,
                  'c00100': 100000.},
                 500., id='reform AGI floor binds'),
    # floor = 2000 exceeds giving of 1500
    pytest.param(CHARITY_FLOOR_REFORM,
                 {'MARS': 1, 'e19800': 1500., 'c00100': 100000.},
                 0., id='reform giving below floor'),
])
def test_CharityCredit(call_calcfunc, reform, rvars, expected):
    """
    Tests the reform-only CharityCredit function
    """
    actual = call_calcfunc('CharityCredit', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# NonrefundableCredits
# ----------------------------------------------------------------------


# NonrefundableCredits test cases follow the 2025 Schedule 3 Part I line
# order plus Form 1040 line 19, limiting each credit in turn against the
# Form 1040 line 18 tax (c05800) that remains after the credits ahead of
# it: Sch 3 lines 1-4 (foreign tax, child and dependent care, education,
# retirement savings), then Form 1040 line 19 (CTC, then ODC), then Sch 3
# lines 5a, 6a, 6b, 6d, and 6z (residential energy, general business,
# prior-year minimum tax, Sch R, other).  The reform-only charity and
# personal nonrefundable credits, which are computed upstream and are
# zero under current law, come last.  The reform-only CR_*_hc haircuts
# are zero and the CTC_is_refundable and ODC_is_refundable switches are
# false under 2025 current law.  The returned tuple is (c07180, c07200,
# c07220, c07230, c07240, odc, c07260, c07300, c07400, c07600, c08000,
# charity_credit, personal_nonrefundable_credit).
NRC_CREDITS = {
    'e07300': 600., 'c07180': 1000., 'c07230': 500., 'e07240': 300.,
    'c07220': 2200., 'odc': 500., 'e07260': 400., 'e07400': 700.,
    'e07600': 200., 'c07200': 800., 'p08000': 100.,
}
NRC_HAIRCUT_REFORM = {
    'CR_ForeignTax_hc': {2025: 0.5},
    'CR_RetirementSavings_hc': {2025: 0.5},
    'CR_ResidentialEnergy_hc': {2025: 0.5},
    'CR_GeneralBusiness_hc': {2025: 0.5},
    'CR_MinimumTax_hc': {2025: 0.5},
    'CR_OtherCredits_hc': {2025: 0.5},
}
NRC_CTC_REFUNDABLE_REFORM = {'CTC_is_refundable': {2025: True}}
NRC_ODC_REFUNDABLE_REFORM = {'ODC_is_refundable': {2025: True}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # line 18 tax of 20000 exceeds the 7300 sum of all credits
    pytest.param(None, {**NRC_CREDITS, 'c05800': 20000.},
                 (1000., 800., 2200., 500., 300., 500.,
                  400., 600., 700., 200., 100., 0., 0.),
                 id='no tax limit'),
    # no tax liability: every credit is limited to zero
    pytest.param(None, {**NRC_CREDITS, 'c05800': 0.},
                 (0., 0., 0., 0., 0., 0.,
                  0., 0., 0., 0., 0., 0., 0.),
                 id='no tax'),
    # negative tax is treated as zero tax
    pytest.param(None, {**NRC_CREDITS, 'c05800': -1000.},
                 (0., 0., 0., 0., 0., 0.,
                  0., 0., 0., 0., 0., 0., 0.),
                 id='negative tax'),
    # 2000 - 600 (line 1) - 1000 (line 2) = 400 left for line 3
    pytest.param(None, {**NRC_CREDITS, 'c05800': 2000.},
                 (1000., 0., 0., 400., 0., 0.,
                  0., 600., 0., 0., 0., 0., 0.),
                 id='limited in Sch 3 line 3'),
    # 4000 - (600 + 1000 + 500 + 300) = 1600 left for CTC
    pytest.param(None, {**NRC_CREDITS, 'c05800': 4000.},
                 (1000., 0., 1600., 500., 300., 0.,
                  0., 600., 0., 0., 0., 0., 0.),
                 id='limited in CTC'),
    # 6500 - 2400 (lines 1-4) - 2700 (line 19) - (400 + 700 + 200)
    # = 100 left for Sch 3 line 6d; nothing left for line 6z
    pytest.param(None, {**NRC_CREDITS, 'c05800': 6500.},
                 (1000., 100., 2200., 500., 300., 500.,
                  400., 600., 700., 200., 0., 0., 0.),
                 id='limited in Sch 3 line 6d'),
    # a negative credit is treated as zero and does not raise the
    # tax available to later credits
    pytest.param(None,
                 {'c05800': 1000., 'e07300': -500., 'c07180': 1200.},
                 (1000., 0., 0., 0., 0., 0.,
                  0., 0., 0., 0., 0., 0., 0.),
                 id='negative credit'),
    # upstream reform-only credits: 1500 - 1000 (line 2) - 300 (charity)
    # = 200 left for the personal nonrefundable credit
    pytest.param(None,
                 {'c05800': 1500., 'c07180': 1000., 'charity_credit': 300.,
                  'personal_nonrefundable_credit': 400.},
                 (1000., 0., 0., 0., 0., 0.,
                  0., 0., 0., 0., 0., 300., 200.),
                 id='reform-only credits limited'),
    # reform haircuts: half of each raw-input credit is allowed
    pytest.param(NRC_HAIRCUT_REFORM, {**NRC_CREDITS, 'c05800': 20000.},
                 (1000., 800., 2200., 500., 150., 500.,
                  200., 300., 350., 100., 50., 0., 0.),
                 id='reform haircuts'),
    # reform refundable CTC is not limited: 4000 - 2400 (lines 1-4)
    # - 500 (ODC) - 400 (line 5a) = 700 left for line 6a
    pytest.param(NRC_CTC_REFUNDABLE_REFORM,
                 {**NRC_CREDITS, 'c05800': 4000.},
                 (1000., 0., 2200., 500., 300., 500.,
                  400., 600., 700., 0., 0., 0., 0.),
                 id='reform refundable CTC'),
    # reform refundable ODC is not limited: 4000 - 2400 (lines 1-4)
    # = 1600 left for CTC; nothing left for later credits
    pytest.param(NRC_ODC_REFUNDABLE_REFORM,
                 {**NRC_CREDITS, 'c05800': 4000.},
                 (1000., 0., 1600., 500., 300., 500.,
                  0., 600., 0., 0., 0., 0., 0.),
                 id='reform refundable ODC'),
])
def test_NonrefundableCredits(call_calcfunc, reform, rvars, expected):
    """
    Tests the NonrefundableCredits function against the 2025 Schedule 3
    Part I and Form 1040 line 19 credit ordering
    """
    actual = call_calcfunc('NonrefundableCredits', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# CTC_new
# ----------------------------------------------------------------------


# CTC_new is a reform-only refundable child credit (like the 2021 ARPA
# credit) with no 2025 IRS form; its parameters are zero under 2025
# current law.
CTC_NEW_REFORM = {
    'CTC_new_c': {2025: 1000},
    'CTC_new_c_under6_bonus': {2025: 600},
    'CTC_new_ps': {2025: [75000, 150000, 75000, 112500, 150000]},
    'CTC_new_prt': {2025: 0.05},
    'CTC_new_for_all': {2025: True},
}
CTC_NEW_PHASEIN_REFORM = {
    'CTC_new_c': {2025: 1000},
    'CTC_new_rt': {2025: 0.15},
    'CTC_new_ps': {2025: [75000, 150000, 75000, 112500, 150000]},
    'CTC_new_prt': {2025: 0.05},
}
CTC_NEW_REFUND_LIMIT_REFORM = {
    **CTC_NEW_REFORM,
    'CTC_new_refund_limited': {2025: True},
    'CTC_new_refund_limit_payroll_rt': {2025: 1.0},
}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no new CTC
    pytest.param(None,
                 {'MARS': 4, 'n24': 2, 'nu06': 1, 'c00100': 50000.}, 0.,
                 id='current law'),
    # reform: 2 * 1000 + 1 * 600
    pytest.param(CTC_NEW_REFORM,
                 {'MARS': 4, 'n24': 2, 'nu06': 1, 'c00100': 50000.}, 2600.,
                 id='reform'),
    # reform: 2600 - 0.05 * (120000 - 112500)
    pytest.param(CTC_NEW_REFORM,
                 {'MARS': 4, 'n24': 2, 'nu06': 1, 'c00100': 120000.},
                 2225., id='reform phase-out smoothed'),
    # reform: excess 7500 rounded up to 8000: 2600 - 0.05 * 8000
    pytest.param(CTC_NEW_REFORM,
                 {'MARS': 4, 'n24': 2, 'nu06': 1, 'c00100': 120000.,
                  'exact': 1},
                 2200., id='reform phase-out exact'),
    # reform: no qualifying children
    pytest.param(CTC_NEW_REFORM,
                 {'MARS': 4, 'nu18': 1, 'c00100': 50000.}, 0.,
                 id='reform no children'),
    # phase-in reform: min(0.15 * 5000, 1000)
    pytest.param(CTC_NEW_PHASEIN_REFORM,
                 {'MARS': 1, 'n24': 1, 'c00100': 5000.}, 750.,
                 id='reform phase-in'),
    # refund-limit reform: refund = 2600 - 500 = 2100; limit =
    # 1.0 * 1000 OASDI tax; credit = 2600 - (2100 - 1000)
    pytest.param(CTC_NEW_REFUND_LIMIT_REFORM,
                 {'MARS': 4, 'n24': 2, 'nu06': 1, 'c00100': 50000.,
                  'c09200': 500., 'ptax_oasdi': 1000.},
                 1500., id='reform refund limit'),
])
def test_CTC_new(call_calcfunc, reform, rvars, expected):
    """
    Tests the CTC_new function
    """
    actual = call_calcfunc('CTC_new', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# FairShareTax
# ----------------------------------------------------------------------


# FairShareTax is a reform-only construct with no IRS form; FST_AGI_trt
# is zero under 2025 current law, whose FST_AGI_thd_lo and FST_AGI_thd_hi
# values are 1000000 and 2000000 (500000 and 1000000 when MARS is 3).
# The returned tuple is (fstax, iitax, combined, surtax).
FST_REFORM = {'FST_AGI_trt': {2025: 0.3}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no fair-share tax; other outputs unchanged
    pytest.param(None,
                 {'MARS': 1, 'c00100': 3e6, 'iitax': 600000.,
                  'combined': 630000.},
                 (0., 600000., 630000., 0.), id='current law'),
    # reform, AGI above upper threshold: employee payroll share =
    # (30000 - 15000) + 0.5 * 0 + 25000 = 40000;
    # fstax = 0.3 * 3000000 - 600000 - 40000 = 260000
    pytest.param(FST_REFORM,
                 {'MARS': 1, 'c00100': 3e6, 'ptax_was': 30000.,
                  'ptax_er_p': 15000., 'ptax_amc': 25000.,
                  'iitax': 600000., 'combined': 630000.},
                 (260000., 860000., 890000., 260000.),
                 id='reform above upper threshold'),
    # reform, AGI in phase-in range: employee payroll share =
    # (30000 - 15000) + 0.5 * 20000 + 11700 = 36700;
    # full fstax = 0.3 * 1500000 - 300000 - 36700 = 113300;
    # phase-in fraction = (1500000 - 1000000) / 1000000 = 0.5
    pytest.param(FST_REFORM,
                 {'MARS': 1, 'c00100': 1.5e6, 'ptax_was': 30000.,
                  'ptax_er_p': 15000., 'setax': 20000.,
                  'ptax_amc': 11700., 'iitax': 300000.,
                  'combined': 336700.},
                 (56650., 356650., 393350., 56650.),
                 id='reform in phase-in range'),
    # reform, married filing separately in phase-in range:
    # full fstax = 0.3 * 750000 - 150000 = 75000;
    # phase-in fraction = (750000 - 500000) / 500000 = 0.5
    pytest.param(FST_REFORM,
                 {'MARS': 3, 'c00100': 750000., 'iitax': 150000.,
                  'combined': 150000.},
                 (37500., 187500., 187500., 37500.),
                 id='reform separate'),
    # reform, AGI below lower threshold
    pytest.param(FST_REFORM,
                 {'MARS': 1, 'c00100': 900000., 'iitax': 200000.,
                  'combined': 200000.},
                 (0., 200000., 200000., 0.), id='reform below threshold'),
    # reform, income tax already exceeds 0.3 * AGI
    pytest.param(FST_REFORM,
                 {'MARS': 1, 'c00100': 3e6, 'iitax': 1e6,
                  'combined': 1e6},
                 (0., 1e6, 1e6, 0.), id='reform tax exceeds minimum'),
])
def test_FairShareTax(call_calcfunc, reform, rvars, expected):
    """
    Tests the FairShareTax function
    """
    actual = call_calcfunc('FairShareTax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# LumpSumTax
# ----------------------------------------------------------------------


# LumpSumTax is a reform-only construct with no IRS form; LST is zero
# under 2025 current law.  The returned tuple is (lumpsum_tax, combined).
LST_REFORM = {'LST': {2025: 200}}


@pytest.mark.parametrize('reform, rvars, expected', [
    # 2025 current law: no lump-sum tax and combined is unchanged
    pytest.param(None, {'num': 2, 'XTOT': 4, 'combined': 1000.},
                 (0., 1000.), id='current law'),
    # reform: 200 * max(2, 4) = 800 added to combined
    pytest.param(LST_REFORM, {'num': 2, 'XTOT': 4, 'combined': 1000.},
                 (800., 1800.), id='reform family'),
    # reform: 200 * max(1, 0) = 200
    pytest.param(LST_REFORM, {'num': 1, 'XTOT': 0, 'combined': 1000.},
                 (200., 1200.), id='reform no exemptions'),
    # reform: dependent filers are exempt
    pytest.param(LST_REFORM,
                 {'DSI': 1, 'num': 1, 'XTOT': 1, 'combined': 1000.},
                 (0., 1000.), id='reform dependent'),
])
def test_LumpSumTax(call_calcfunc, reform, rvars, expected):
    """
    Tests the LumpSumTax function
    """
    actual = call_calcfunc('LumpSumTax', reform=reform, **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# ExpandIncome
# ----------------------------------------------------------------------


# ExpandIncome and AfterTaxIncome are model-only accounting constructs
# with no IRS form.


def test_ExpandIncome(call_calcfunc):
    """
    Tests the ExpandIncome function, which sums its income arguments
    """
    rvars = {
        'e00200': 50000., 'pencon_p': 3000., 'pencon_s': 2000.,
        'e00300': 1000., 'e00400': 500., 'e00600': 2000.,
        'e00700': 100., 'e00800': 0., 'e00900': 10000., 'e01100': 50.,
        'e01200': -200., 'e01400': 4000., 'e01500': 6000.,
        'e02000': 7000., 'e02100': -1000.,
        'p22250': -2000., 'p23250': 5000., 'cmbtp': 300.,
        'ptax_er_p': 3825., 'ptax_er_s': 0., 'benefit_value_total': 1200.,
    }
    # wages: 50000 + 3000 + 2000 = 55000
    # investment income: 1000 + 500 + 2000 = 3500
    # other income: 100 + 0 + 10000 + 50 - 200 + 4000 + 6000
    #               + 7000 - 1000 = 25950
    # capital gains: -2000 + 5000 = 3000
    # other: 300 + 3825 + 0 + 1200 = 5325
    expected = 55000. + 3500. + 25950. + 3000. + 5325.
    assert np.allclose(expected, 92775.)
    actual = call_calcfunc('ExpandIncome', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'


# ----------------------------------------------------------------------
# AfterTaxIncome
# ----------------------------------------------------------------------


@pytest.mark.parametrize('rvars, expected', [
    # 100000 - 25000
    pytest.param({'expanded_income': 100000., 'combined': 25000.}, 75000.,
                 id='positive tax'),
    # a net refund (negative combined tax) raises after-tax income
    pytest.param({'expanded_income': 100000., 'combined': -3000.},
                 103000., id='negative tax'),
])
def test_AfterTaxIncome(call_calcfunc, rvars, expected):
    """
    Tests the AfterTaxIncome function
    """
    actual = call_calcfunc('AfterTaxIncome', **rvars)
    assert np.allclose(actual, expected), f'{actual} != {expected}'
