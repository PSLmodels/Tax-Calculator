"""
Test example JSON response assumption files in taxcalc/responses directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_responses.py
# pylint --disable=locally-disabled test_responses.py

import os
import glob
import pytest
# pylint: disable=import-error
from taxcalc import Calculator, Consumption, Behavior, Growdiff


@pytest.fixture(scope='session')
def responses_path(tests_path):
    """
    Return path to taxcalc/responses/*.json files
    """
    return os.path.join(tests_path, '..', 'responses', '*.json')


def test_response_json(responses_path):  # pylint: disable=redefined-outer-name
    """
    Check that each JSON file can be converted into dictionaries that
    can be used to construct objects needed for a Calculator object.
    """
    for jpf in glob.glob(responses_path):
        # read contents of jpf (JSON parameter filename)
        jfile = open(jpf, 'r')
        jpf_text = jfile.read()
        # check that jpf_text can be used to construct objects
        response_file = ('"consumption"' in jpf_text and
                         '"behavior"' in jpf_text and
                         '"growdiff_baseline"' in jpf_text and
                         '"growdiff_response"' in jpf_text)
        if response_file:
            # pylint: disable=protected-access
            (con, beh, gdiff_base,
             gdiff_resp) = (
                 Calculator._read_json_econ_assump_text(jpf_text,
                                                        arrays_not_lists=True))
            cons = Consumption()
            cons.update_consumption(con)
            behv = Behavior()
            behv.update_behavior(beh)
            growdiff_baseline = Growdiff()
            growdiff_baseline.update_growdiff(gdiff_base)
            growdiff_response = Growdiff()
            growdiff_response.update_growdiff(gdiff_resp)
        else:  # jpf_text is not a valid JSON response assumption file
            print('test-failing-filename: ' +
                  jpf)
            assert False
