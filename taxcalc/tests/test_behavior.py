"""
Test example JSON behavioral responses files in taxcalc/behavior directory
"""
# CODING-STYLE CHECKS:
# pycodestyle test_behavior.py
# pylint --disable=locally-disabled test_behavior.py

import os
import glob
from taxcalc import json_to_dict


def test_responses_json(tests_path):
    """
    Check that each JSON file can be converted into a dictionary that
    can be used to construct parameters used by functions in the
    behresp.py module.
    """
    exp_keys = sorted(['sub', 'inc', 'cg'])
    responses_path = os.path.join(tests_path, '..', 'behavior', '*.json')
    for jpf in glob.glob(responses_path):
        # read contents of jpf (JSON parameter filename) into a dictionary
        with open(jpf, 'r', encoding='utf-8') as jfile:
            jpf_text = jfile.read()
        jpf_dict = json_to_dict(jpf_text)
        # check that top-level keys of jpf_dict are as expected
        act_keys = sorted(list(jpf_dict))
        if act_keys != exp_keys:
            emsg = f'{act_keys} != {exp_keys} in file {jpf}'
            raise ValueError(emsg)
