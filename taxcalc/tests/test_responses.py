"""
Test example JSON response assumption files in taxcalc/responses directory
"""
# CODING-STYLE CHECKS:
# pycodestyle est_responses.py
# pylint --disable=locally-disabled test_responses.py

import os
import glob
from taxcalc.consumption import Consumption
from taxcalc.growdiff import GrowDiff


def test_response_json(tests_path):
    """
    Check that each JSON file can be converted into dictionaries that
    can be used to construct objects needed for a Calculator object.
    """
    # pylint: disable=too-many-locals
    responses_path = os.path.join(tests_path, '..', 'responses', '*.json')
    for jpf in glob.glob(responses_path):
        # read contents of jpf (JSON parameter filename)
        with open(jpf, 'r', encoding='utf-8') as jfile:
            jpf_text = jfile.read()
        # check that jpf_text can be used to construct objects
        response_file = ('"consumption"' in jpf_text and
                         '"growdiff_baseline"' in jpf_text and
                         '"growdiff_response"' in jpf_text)
        if response_file:
            consumption = Consumption()
            con_change = Consumption.read_json_update(jpf_text)
            consumption.update_consumption(con_change)
            del consumption
            for topkey in ['growdiff_baseline', 'growdiff_response']:
                growdiff = GrowDiff()
                gdiff_change = GrowDiff.read_json_update(jpf_text, topkey)
                growdiff.update_growdiff(gdiff_change)
                del growdiff
        else:  # jpf_text is not a valid JSON response assumption file
            print('test-failing-filename: ' + jpf)
            assert False
