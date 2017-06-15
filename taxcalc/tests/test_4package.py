import re
import subprocess
import pytest


def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc']).decode('ascii')
    envless_out = out.replace('taxcalc-dev', 'environment')
    if re.search('taxcalc', envless_out) is not None:
        assert 'taxcalc package' == 'installed'
