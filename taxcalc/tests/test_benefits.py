"""
Tests of Tax-Calculator benefits.

Note that the CPS-related files that are required to run this program
have been constructed by the Tax-Calculator development team from publicly
available Census data files.  Hence, the CPS-related files are freely
available and are part of the Tax-Calculator repository.

Read Tax-Calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_benefits.py
# pylint --disable=locally-disabled test_benefits.py

from __future__ import print_function
import os
import pytest
import pandas as pd
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, nonsmall_diffs

@pytest.mark.one
@pytest.mark.pre_release
def test_benefits(tests_path, cps_fullsample):
    """
    Test CPS benefits.
    """
    # pylint: disable=too-many-locals
    benefit_names = ['ssi', 'mcare', 'mcaid', 'snap', 'wic',
                     'tanf', 'vet', 'housing']
    recs = Records.cps_constructor(data=cps_fullsample)
    start_year = recs.current_year
    calc = Calculator(policy=Policy(), records=recs, verbose=False)
    assert calc.current_year == start_year
    year_list = list()
    bname_list = list()
    benamt_list = list()
    bencnt_list = list()
    benavg_list = list()
    for year in range(start_year, Policy.LAST_BUDGET_YEAR + 1):
        calc.advance_to_year(year)
        xtot = calc.array('XTOT')
        wght = calc.array('s006')
        # compute benefit aggregate amounts and head counts and average benefit
        for bname in benefit_names:
            ben = calc.array('{}_ben'.format(bname))
            benamt = round((ben * wght).sum() * 1e-9, 3)
            bencnt = round((xtot[ben > 0] * wght[ben > 0]).sum() * 1e-6, 3)
            benavg = round(benamt / bencnt, 1)
            year_list.append(year)
            bname_list.append(bname)
            benamt_list.append(benamt)
            bencnt_list.append(bencnt)
            benavg_list.append(benavg)
    bdict = {'year': year_list,
             'bname': bname_list,
             'benamt': benamt_list,
             'bencnt': bencnt_list,
             'benavg': benavg_list}
    bdf = pd.DataFrame(data=bdict,
                       columns=['year', 'bname', 'benamt', 'bencnt', 'benavg'])
    ben_act_path = os.path.join(tests_path, 'benefits_actual.csv')
    bdf.to_csv(ben_act_path, index=False)
