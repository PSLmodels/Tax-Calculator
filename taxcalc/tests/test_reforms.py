"""
Tests all the example JSON reform files located in taxcalc/reforms directory.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import glob
import re
import json
import pytest
from taxcalc import Calculator, Policy  # pylint: disable=import-error


@pytest.fixture(scope='session')
def reforms_path(tests_path):
    """
    Return path to taxcalc/reforms/*.txt files
    """
    return os.path.join(tests_path, '..', 'reforms', '*.txt')


def test_reforms(reforms_path):  # pylint: disable=redefined-outer-name
    """
    Check that each JSON reform file can be converted into a reform dictionary,
    which can then be passed to the Policy.implement_reform() method.
    While doing this, construct a set of Policy parameters (other than those
    ending in '_cpi') included in the JSON reform files.
    """
    params_set = set()
    for jrf in glob.glob(reforms_path):
        # read contents of jrf (JSON reform filename)
        with open(jrf) as jrfile:
            jrf_text = jrfile.read()
        # check that jrf_text can be implemented as a Policy reform
        jrf_dict = Calculator.read_json_reform_text(jrf_text)
        policy = Policy()
        policy.implement_reform(jrf_dict)
        # identify policy parameters included in jrf after removing //-comments
        json_without_comments = re.sub('//.*', ' ', jrf_text)
        json_dict = json.loads(json_without_comments)
        for param in json_dict.keys():
            if param.endswith('_cpi'):
                continue
            params_set.add(param)
    # TODO: compare params_set to set of parameters in current_law_policy.json
