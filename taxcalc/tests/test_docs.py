"""
Tests for Tax-Calculator docs.
"""
# CODING-STYLE CHECKS:
# pep8 test_docs.py
# pylint --disable=locally-disabled test_docs.py

import os
import glob
import pytest


@pytest.mark.pre_release
def test_docs_index_up_to_date(tests_path):
    """
    Check that index.html timestamp is greater than the timestamp
    of each of its dependencies, where a timestamp is the time a file
    was last modified.
    """
    code_path = os.path.join(tests_path, '..')
    docs_path = os.path.join(code_path, '..', 'docs')
    target = os.path.join(docs_path, 'index.html')
    dependencies = [os.path.join(docs_path, 'index.htmx'),
                    os.path.join(docs_path, 'make_index.py'),
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
        msg += ' $ python make_index.py                        \n'
        msg += 'AND INCLUDE UPDATED index.html IN NEXT COMMIT  \n'
        raise ValueError(msg)


@pytest.mark.pre_release
def test_docs_cookbook_up_to_date(tests_path):
    """
    Check that cookbook.html timestamp is greater than the timestamp
    of each of its dependencies, where a timestamp is the time a file
    was last modified.
    """
    docs_path = os.path.join(tests_path, '..', '..', 'docs')
    target = os.path.join(docs_path, 'cookbook.html')
    recipes = glob.glob(os.path.join(docs_path, 'recipes', '*'))
    ingredients = glob.glob(os.path.join(docs_path, 'recipes',
                                         'ingredients', '*'))
    dependencies = recipes + ingredients

    target_timestamp = os.path.getmtime(target)
    target_up_to_date = True
    for dep in dependencies:
        if os.path.getmtime(dep) > target_timestamp:
            target_up_to_date = False
    if not target_up_to_date:
        msg = 'Tax-Calculator/docs/cookbook.html IS NOT UP-TO-DATE:   \n'
        msg += 'EDIT cookbook.html SO THAT IT REFERENCES              \n'
        msg += '- ALL cookbook/recipe*py FILES,                       \n'
        msg += '- ALL cookbook/recipe*res FILES,                      \n'
        msg += '- ALL cookbook/ingredients FILES.                     \n'
        msg += 'AND INCLUDE THE UPDATED cookbook.html IN NEXT COMMIT. \n'
        msg += '                                                      \n'
        msg += 'IF NO SUBSTATIVE CHANGES IN cookbook.html ARE RQUIRED,\n'
        msg += 'SAVE THE UNCHANGED FILE SO IT HAS A CURRENT TIMESTAMP.\n'
        raise ValueError(msg)
