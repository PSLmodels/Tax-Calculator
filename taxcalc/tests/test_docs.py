"""
Tests for Tax-Calculator docs.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test_docs.py
# pylint --disable=locally-disabled test_docs.py

import os
import pytest


@pytest.mark.local_test
def test_docs_up_to_date(tests_path):
    """
    Check that index.html timestamp is greater than the timestamp
    of each of its dependencies, where a timestamp is the time a file
    was last modified.
    """
    code_path = os.path.join(tests_path, '..')
    docs_path = os.path.join(code_path, '..', 'docs')
    target = os.path.join(docs_path, 'index.html')
    dependencies = [os.path.join(docs_path, 'index.htmx'),
                    os.path.join(docs_path, 'make.py'),
                    os.path.join(code_path, 'current_law_policy.json'),
                    os.path.join(code_path, 'consumption.json'),
                    os.path.join(code_path, 'behavior.json'),
                    os.path.join(code_path, 'growdiff.json'),
                    os.path.join(code_path, 'records_variables.json')]
    target_timestamp = os.path.getmtime(target)
    target_up_to_date = True
    for dep in dependencies:
        if os.path.getmtime(dep) > target_timestamp:
            target_up_to_date = False
    if not target_up_to_date:
        msg = 'Tax-Calculator/docs/index.html IS NOT UP-TO-DATE\n'
        msg += 'FIX BY DOING THIS:                             \n'
        msg += ' $ cd Tax-Calculator/docs                      \n'
        msg += ' $ python make.py                              \n'
        msg += 'AND INCLUDE UPDATED index.html IN NEXT COMMIT  \n'
        raise ValueError(msg)
