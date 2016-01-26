"""
Tests for Tax-Calculator functions.py logic.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_functions.py
# pylint --disable=locally-disabled test_functions.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

from taxcalc import IncomeTaxIO  # pylint: disable=import-error
from io import StringIO
import pandas as pd
import pytest


@pytest.mark.one
def test_1():
    """
    Test calculation of AGI adjustment for half of Self-Employment Tax,
    which is the FICA payroll tax on self-employment income.
    """
    agi_ovar_num = 10
    # specify a reform that eliminates all Medicare FICA taxes and sets
    #   the maximum taxable earnings (MTE) at $100,000 in 2015, in order
    #   to simplify the hand calculations that follow the IRS form logic.
    mte = 100000  # lower than current-law to simplify hand calculations
    ssr = 0.124  # current law OASDI ee+er payroll tax rate
    mrr = 0.029  # current law HI ee+er payroll tax rate
    reform = {
        2015: {
            '_SS_Earnings_c': [mte],
            '_FICA_ss_trt': [ssr],
            '_FICA_mc_trt': [mrr],
        }
    }
    funit = (
        u'RECID,MARS,e00200,e00200p,e00900,e00900s\n'
        u'1,    2,   200000, 200000,200000, 200000\n'
    )
    # The expected AGI for this filing unit is $400,000 minus half of
    # the  spouse's Self-Employment Tax (SET), which represents the
    # "employer share" of the SET.  The spouse pays OASDI SET on only
    # $100,000 of self-employment income, which implies a tax of
    # $12,400.  The spouse also pays HI SET on 0.9235 * 200000 * 0.029,
    # which implies a tax of $5,356.30.  So, the spouse's total SET is
    # the sum of the two, which equals $17,756.30.
    # The SET AGI adjustment is one-half of that amount, which is $8,878.15.
    # So, filing unit's AGI is $400,000 less this, which is $391,121.85.
    expected_agi = '391121.85'
    input_dataframe = pd.read_csv(StringIO(funit))
    inctax = IncomeTaxIO(input_data=input_dataframe,
                         tax_year=2015,
                         policy_reform=reform,
                         blowup_input_data=False)
    output = inctax.calculate()
    output_list = output.split()
    agi = output_list[agi_ovar_num - 1]
    assert agi == expected_agi
