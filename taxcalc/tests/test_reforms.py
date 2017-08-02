"""
Test example JSON policy reform files in taxcalc/reforms directory
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_reforms.py
# pylint --disable=locally-disabled test_reforms.py

import os
import glob
from taxcalc import Calculator, Policy  # pylint: disable=import-error


def test_reform_json(tests_path):
    """
    Check that each JSON reform file can be converted into a reform dictionary
    that can then be passed to the Policy class implement_reform() method.
    """
    reforms_path = os.path.join(tests_path, '..', 'reforms', '*.json')
    for jpf in glob.glob(reforms_path):
        # read contents of jpf (JSON parameter filename)
        jfile = open(jpf, 'r')
        jpf_text = jfile.read()
        # check that jpf_text has "policy" that can be implemented as a reform
        if '"policy"' in jpf_text:
            # pylint: disable=protected-access
            policy_dict = (
                Calculator._read_json_policy_reform_text(jpf_text,
                                                         arrays_not_lists=True)
            )
            policy = Policy()
            policy.implement_reform(policy_dict)
        else:  # jpf_text is not a valid JSON policy reform file
            print('test-failing-filename: ' +
                  jpf)
            assert False
