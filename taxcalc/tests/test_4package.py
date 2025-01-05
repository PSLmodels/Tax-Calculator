"""
Tests for package existence and dependencies consistency.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_4package.py
# pylint --disable=locally-disabled test_4package.py

import os
import re
import ast
import subprocess
import yaml
import pytest


def extract_install_requires(setup_py_content):
    """
    Extract the install_requires list from a setup.py file content.

    Args:
        setup_py_content (str): The full content of the setup.py file

    Returns:
        list: A list of package requirements
    """
    # Use regex to find the install_requires list
    match = re.search(
        r'"install_requires"\s*:\s*\[([^\]]+)\]', setup_py_content, re.DOTALL
    )
    if match:
        # Extract the contents of the list and split into packages
        packages_str = match.group(1)
        # Use ast.literal_eval to safely parse the string representations
        packages = [
            ast.literal_eval(f'{pkg.strip()}')
            for pkg in packages_str.split(',')
            if pkg.strip()
        ]
        return packages

    return []


@pytest.mark.local
def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest.
    Primarily to help developers catch mistaken installations of taxcalc;
    the local mark prevents test from running on GitHub.
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc']).decode('ascii')
    envless_out = out.replace('taxcalc-dev', 'environment')
    if re.search('taxcalc', envless_out) is not None:
        assert False, 'ERROR: taxcalc package is installed'


def test_for_consistency(tests_path):
    """
    Ensure that there is consistency between environment.yml dependencies
    and conda.recipe/meta.yaml requirements.
    """
    # pylint: disable=too-many-locals
    dev_pkgs = set([
        'pytest',
        'pytest-xdist',
        'pycodestyle',
        'pylint',
        'coverage',
        "pip",
        "jupyter-book",
        "setuptools"
    ])
    # read conda.recipe/meta.yaml requirements
    meta_file = os.path.join(tests_path, '..', '..',
                             'conda.recipe', 'meta.yaml')
    with open(meta_file, 'r', encoding='utf-8') as stream:
        meta = yaml.safe_load(stream)
    bld = set(meta['requirements']['build'])
    run = set(meta['requirements']['run'])
    # confirm conda.recipe/meta.yaml build and run requirements are the same
    assert bld == run
    # read environment.yml dependencies
    envr_file = os.path.join(tests_path, '..', '..',
                             'environment.yml')
    with open(envr_file, 'r', encoding='utf-8') as stream:
        envr = yaml.safe_load(stream)

    env = []
    for dep in envr["dependencies"]:
        if isinstance(dep, dict):
            assert list(dep.keys()) == ["pip"]
            env += dep["pip"]
        else:
            env.append(dep)
    env = set(env)
    # confirm that extras in env (relative to run) equal the dev_pkgs set
    extras = env - run
    assert extras == dev_pkgs
    # Read the setup.py file and extract the install_requires list
    setup_file = os.path.join(tests_path, '..', '..',
                              'setup.py')
    with open(setup_file, 'r', encoding='utf-8') as f:
        setup_py_content = f.read()
    setup = set(extract_install_requires(setup_py_content))
    # confirm that setup.py
    print("Setup packages = ", setup)
    print("Meta packages = ", bld)
    # if package in both, confirm that the version is the same
    for pkg in setup.intersection(bld):
        assert pkg in setup
        assert pkg in bld
