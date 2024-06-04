"""
Tests of Tax-Calculator using tmd.csv input.

Note that the tmd.csv file that is required to run this program has
been constructed in the PSLmodels tax-microdata repository using the
2015 IRS SOI PUF file and recent Census CPS data.  If you have
acquired from IRS the 2015 SOI PUF file and want to execute this program,
contact the Tax-Calculator development team to discuss your options.

Read Tax-Calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_tmdcsv.py
# pylint --disable=locally-disabled test_tmdcsv.py

import pytest
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator


@pytest.mark.requires_tmdcsv
def test_tmd_input(tmd_fullsample):
    """
    Test Tax-Calculator using full-sample tmd.csv file.
    """
    taxyear = 2022
    # create a Policy object with current-law policy parameters
    pol = Policy()
    # create a Records object containing all tmd.csv input records
    recs = Records.tmd_constructor(data=tmd_fullsample)
    # create a Calculator object using current-law policy and tmd records
    calc = Calculator(policy=pol, records=recs)
    calc.advance_to_year(taxyear)
    calc.calc_all()
    assert calc.data_year == Records.TMDCSV_YEAR
    assert calc.current_year == taxyear
    inctax = calc.weighted_total('iitax')
    assert inctax > 0
