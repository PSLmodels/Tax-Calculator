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

import os
import pytest
import numpy as np
import pandas as pd
from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.calculator import Calculator


@pytest.mark.benefits
def test_benefits(tests_path, cps_fullsample):
    """
    Test CPS benefits from 2015 thru 2034.
    """
    # pylint: disable=too-many-locals
    benefit_names = ['ssi', 'mcare', 'mcaid', 'snap', 'wic',
                     'tanf', 'vet', 'housing']
    # write benefits_actual.csv file
    recs = Records.cps_constructor(data=cps_fullsample)
    start_year = recs.current_year
    calc = Calculator(policy=Policy(), records=recs, verbose=False)
    assert calc.current_year == start_year
    year_list = []
    bname_list = []
    benamt_list = []
    bencnt_list = []
    benavg_list = []
    for year in range(start_year, 2034 + 1):
        calc.advance_to_year(year)
        size = calc.array('XTOT')
        wght = calc.array('s006')
        # compute benefit aggregate amounts and head counts and average benefit
        # (head counts include all members of filing unit receiving a benefit,
        #  which means benavg is f.unit benefit amount divided by f.unit size)
        for bname in benefit_names:
            ben = calc.array(f'{bname}_ben')
            benamt = round((ben * wght).sum() * 1e-9, 3)
            bencnt = round((size[ben > 0] * wght[ben > 0]).sum() * 1e-6, 3)
            benavg = round(benamt / bencnt, 1)
            year_list.append(year)
            bname_list.append(bname)
            benamt_list.append(benamt)
            bencnt_list.append(bencnt)
            benavg_list.append(benavg)
    adict = {'year': year_list,
             'bname': bname_list,
             'benamt': benamt_list,
             'bencnt': bencnt_list,
             'benavg': benavg_list}
    adf = pd.DataFrame(data=adict,
                       columns=['year', 'bname', 'benamt', 'bencnt', 'benavg'])
    ben_act_path = os.path.join(tests_path, 'benefits_actual.csv')
    adf.to_csv(ben_act_path, index=False)
    # read benefits_expect.csv file
    ben_exp_path = os.path.join(tests_path, 'benefits_expect.csv')
    edf = pd.read_csv(ben_exp_path)
    # compare benefit information
    atol = 0.0001
    rtol = 0.0
    diffs = False
    for col in ['benamt', 'bencnt', 'benavg']:
        if not np.allclose(adf[col], edf[col], atol=atol, rtol=rtol):
            diffs = True
    if diffs:
        msg = 'CPS BENEFITS RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN benefits_actual.csv FILE   ---\n'
        msg += '--- if new OK, copy benefits_actual.csv to    ---\n'
        msg += '---                 benefits_expect.csv       ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    os.remove(ben_act_path)
