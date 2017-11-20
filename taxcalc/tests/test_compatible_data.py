"""
Tests of the compatible_data field in current_law_policy.json.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_pufcsv.py
# pylint --disable=locally-disabled test_pufcsv.py

import os
import json
import difflib
import pytest
import numpy as np
import pandas as pd
import copy
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator


@pytest.mark.requires_pufcsv
@pytest.mark.pre_release
@pytest.mark.parametrize('puftest', [True, False])
def test_compatible_data(puftest, tests_path, cps_subsample, puf_subsample):
    """

    """

    clppath = os.path.join(tests_path, '..', 'current_law_policy.json')
    pfile = open(clppath, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)

    # These parameters are exempt because they are not active under
    # current law and activating them would deactive other parameters.

    exempt = ['_CG_ec', '_CG_reinvest_ec_rt']

    p_xx = Policy()

    # Set baseline to activate parameters that are inactive under current law.
    reform_xx = {
        2017: {
            '_CTC_new_refund_limited': [True],
            '_FST_AGI_trt': [0.5],
            '_CTC_new_rt': [0.5],
            '_CTC_new_c': [5000],
            '_CTC_new_prt': [0.1],
            '_ID_BenefitSurtax_trt': [0.1],
            '_UBI3': [1000],
            '_PT_brk7': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ID_BenefitSurtax_crt': [0.1],
            '_II_credit_prt': [0.1],
            '_II_credit': [[100, 100, 100, 100, 100]],
            '_CG_brk3': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ALD_Dependents_Child_c': [1000],
            '_II_credit_nr': [[1000, 1000, 1000, 1000, 1000]],
            '_II_credit_nr_prt': [0.1],
            '_AMT_CG_brk3': [[500000, 500000, 500000, 500000, 500000]],
            '_AGI_surtax_thd': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_AGI_surtax_trt': [0.5],
            '_ID_AmountCap_rt': [0.5],
            '_II_brk7': [[1000000, 1000000, 1000000, 1000000, 1000000]],
            '_ID_BenefitCap_rt': [0.5],
            '_DependentCredit_Child_c': [500],
            '_PT_exclusion_rt': [.2],
            '_PT_rt7': [.35]
        }
    }

    p_xx.implement_reform(reform_xx)
    if puftest:
        print('puftest')
        rec_xx = Records(data=puf_subsample)
    else:
        print('cpstest')
        rec_xx = Records.cps_constructor(data=cps_subsample)
    c_xx = Calculator(policy=p_xx, records=rec_xx)
    c_xx.advance_to_year(2018)
    c_xx.calc_all()

    for pname in allparams:
        param = allparams[pname]
        max_listed = param['range']['max']
        # Handle links to other params or self
        if isinstance(max_listed, str):
            if max_listed == 'default':
                max_val = param['value'][-1]
            else:
                max_val = allparams[max_listed]['value'][0]
        if not isinstance(max_listed, str):
            if isinstance(param['value'][0], list):
                max_val = [max_listed] * len(param['value'][0])
            else:
                max_val = max_listed
        min_listed = param['range']['min']
        if isinstance(min_listed, str):
            if min_listed == 'default':
                min_val = param['value'][-1]
            else:
                min_val = allparams[min_listed]['value'][0]
        if not isinstance(min_listed, str):
            if isinstance(param['value'][0], list):
                min_val = [min_listed] * len(param['value'][0])
            else:
                min_val = min_listed
        # Create reform dictionaries
        max_reform = copy.deepcopy(reform_xx)
        min_reform = copy.deepcopy(reform_xx)
        max_reform[2017][str(pname)] = [max_val]
        min_reform[2017][str(pname)] = [min_val]
        # Assess whether max reform changes results
        if puftest:
            rec_yy = Records(data=puf_subsample)
        else:
            rec_yy = Records.cps_constructor(data=cps_subsample)
        p_yy = Policy()
        p_yy.implement_reform(max_reform)
        c_yy = Calculator(policy=p_yy, records=rec_yy)
        c_yy.advance_to_year(2018)
        c_yy.calc_all()
        max_reform_change = ((c_yy.records.combined - c_xx.records.combined) *
                             c_xx.records.s006).sum()
        min_reform_change = 0
        # Assess whether min reform changes results, if max reform did not
        if max_reform_change == 0:
            p_yy = Policy()
            p_yy.implement_reform(min_reform)
            c_yy = Calculator(policy=p_yy, records=rec_xx)
            c_yy.advance_to_year(2018)
            c_yy.calc_all()
            min_reform_change = ((c_yy.records.combined -
                                 c_xx.records.combined) *
                                 c_xx.records.s006).sum()
            if min_reform_change == 0 and pname not in exempt:
                print(pname)
                if puftest:
                    assert param['compatible_data']['puf'] is False
                else:
                    assert param['compatible_data']['cps'] is False
        if max_reform_change != 0 or min_reform_change != 0:
            print(pname)
            if puftest:
                assert param['compatible_data']['puf'] is True
            else:
                assert param['compatible_data']['cps'] is True
