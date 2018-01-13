"""
Tests of the compatible_data field in current_law_policy.json.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_pufcsv.py

import copy
import pytest
import numpy as np
import six
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator


NPARAMS = len(Policy.default_data())
BATCHSIZE = 10


@pytest.fixture(scope="module")
def reform_xx():
    """
    Fixture for reform dictionary
    """
    # Set baseline to activate parameters that are inactive under current law.
    _reform_xx = {
        2017: {
            '_FST_AGI_trt': [0.5],
            '_CTC_new_rt': [0.5],
            '_CTC_new_c': [5000],
            '_CTC_new_prt': [0.1],
            '_CTC_new_refund_limited': [True],
            '_CTC_new_refund_limit_payroll_rt': [1],
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
    return _reform_xx


@pytest.fixture(scope="module")
def allparams():
    """
    Get current law parameters
    """
    return Policy.default_data(metadata=True)


@pytest.fixture(scope="module")
def sorted_param_names(allparams):
    """
    Fixture for storing a sorted parameter list
    """
    return sorted(list(allparams.keys()))


@pytest.fixture(
    params=[i for i in range(0, int(np.floor(NPARAMS / BATCHSIZE)) + 1)]
)
def allparams_batch(request, allparams, sorted_param_names):
    """
    Fixture for grouping Tax-Calculator parameters
    """
    ix = request.param
    ix_start = ix * BATCHSIZE
    ix_end = min((ix + 1) * BATCHSIZE, NPARAMS)
    pnames = sorted_param_names[ix_start: ix_end]
    return {pname: allparams[pname] for pname in pnames}


@pytest.fixture(params=[True, False], scope="module")
def tc_objs(request, reform_xx, puf_subsample, cps_subsample):
    """
    Fixture for creating TC objects corresponding to using the PUF and using
    the CPS (only called twice--once for PUF and once for CPS)
    """
    puftest = request.param
    p_xx = Policy()
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

    return p_xx, rec_xx, c_xx, puftest


@pytest.mark.requires_pufcsv
@pytest.mark.pre_release
def test_compatible_data(cps_subsample, puf_subsample, allparams, reform_xx,
                         tc_objs, allparams_batch):
    """
    Test that the compatible_data attribute in current_law_policy.json
    is accurate by implementing the min and max values of each parameter
    as reforms and ensuring that revenue differs from baseline when for
    at least one of these reforms when using datasets marked compatible
    and does not differ when using datasets marked as incompatible.
    """
    # Get taxcalc objects from tc_objs fixture
    p_xx, rec_xx, c_xx, puftest = tc_objs

    # These parameters are exempt because they are not active under
    # current law and activating them would deactive other parameters.
    exempt = ['_CG_ec', '_CG_reinvest_ec_rt']

    for pname in allparams_batch:
        param = allparams_batch[pname]
        max_listed = param['range']['max']
        # Handle links to other params or self
        if isinstance(max_listed, six.string_types):
            if max_listed == 'default':
                max_val = param['value'][-1]
            else:
                max_val = allparams[max_listed]['value'][0]
        if not isinstance(max_listed, six.string_types):
            if isinstance(param['value'][0], list):
                max_val = [max_listed] * len(param['value'][0])
            else:
                max_val = max_listed
        min_listed = param['range']['min']
        if isinstance(min_listed, six.string_types):
            if min_listed == 'default':
                min_val = param['value'][-1]
            else:
                min_val = allparams[min_listed]['value'][0]
        if not isinstance(min_listed, six.string_types):
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
