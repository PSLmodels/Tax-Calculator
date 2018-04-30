"""
Tests for package existence and dependencies consistency.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_4package.py
# pylint --disable=locally-disabled test_4package.py

import os
import re
import subprocess
import yaml
import pytest


@pytest.mark.local
def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest.
    Primarily to help developers catch mistaken installations of taxcalc;
    the pre_release mark prevents test from running on GitHub.
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc']).decode('ascii')
    envless_out = out.replace('taxcalc-dev', 'environment')
    if re.search('taxcalc', envless_out) is not None:
        assert 'taxcalc package' == 'installed'


def test_for_consistency(tests_path):
    """
    Ensure that there is consistency between environment.yml dependencies
    and conda.recipe/meta.yaml requirements.
    It is OK if only environment.yml contains the development packages
    included in the dev_pkgs set.
    It is also OK if only conda.recipe/meta.yaml contains the run packages
    included in the run_pkgs set.
    """
    dev_pkgs = set([
        'mock',
        'pep8',
        'pycodestyle',
        'pylint',
        'coverage',
        'pytest-pep8',
        'pytest-xdist'
    ])
    run_pkgs = set([
        'python'
    ])
    # read conda.recipe/meta.yaml requirements
    meta_file = os.path.join(tests_path, '..', '..',
                             'conda.recipe', 'meta.yaml')
    with open(meta_file, 'r') as stream:
        meta = yaml.load(stream)
    bld = set(meta['requirements']['build'])
    run = set(meta['requirements']['run'])
    # confirm conda.recipe/meta.yaml build and run requirements are the same
    assert bld == run
    # read environment.yml dependencies
    envr_file = os.path.join(tests_path, '..', '..',
                             'environment.yml')
    with open(envr_file, 'r') as stream:
        envr = yaml.load(stream)
    env = set(envr['dependencies'])
    # confirm all extras in env are in dev_pkgs set
    extras = env - run
    assert extras <= dev_pkgs
    # confirm all extras in run are in run_pkgs set
    extras = run - env
    assert extras <= run_pkgs
