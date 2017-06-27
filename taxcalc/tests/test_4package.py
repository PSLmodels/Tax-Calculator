import re
import subprocess
import pytest


@pytest.mark.requires_pufcsv
def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest.
    Primarily to help developers catch mistaken installations of taxcalc;
    the requires_pufcsv mark prevents test from running on GitHub.
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc']).decode('ascii')
    envless_out = out.replace('taxcalc-dev', 'environment')
    if re.search('taxcalc', envless_out) is not None:
        assert 'taxcalc package' == 'installed'
