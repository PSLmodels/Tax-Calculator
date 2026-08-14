"""
Test example JSON assumption files in taxcalc/assumptions directory
"""
# CODING-STYLE CHECKS:
# pycodestyle test_responses.py
# pylint --disable=locally-disabled test_assumptions.py

import os
import glob
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff


def test_assumptions_json(tests_path):
    """
    Check that each JSON file can be converted into a dictionary that
    can be used to construct Consumption and GrowDiff objects.
    """
    assumptions_path = os.path.join(tests_path, '..', 'assumptions', '*.json')
    for jpf in glob.glob(assumptions_path):
        # read contents of jpf (JSON parameter filename)
        with open(jpf, 'r', encoding='utf-8') as jfile:
            jpf_text = jfile.read()
        # check that jpf_text can be used to construct objects
        valid_file = (
            '"consumption"' in jpf_text and
            '"growdiff_baseline"' in jpf_text and
            '"growdiff_response"' in jpf_text
        )
        if not valid_file:
            raise ValueError(f'Improper top-level keys in file {jpf}')
        consumption = Consumption()
        con_change = Consumption.read_json_update(jpf_text)
        consumption.update_consumption(con_change)
        del consumption
        for topkey in ['growdiff_baseline', 'growdiff_response']:
            growdiff = GrowDiff()
            gdiff_change = GrowDiff.read_json_update(jpf_text, topkey)
            growdiff.update_growdiff(gdiff_change)
            del growdiff
