import re
import subprocess
import pytest


def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc'])
    if re.search('taxcalc'.encode('ascii'), out.encode('ascii')) is not None:
        assert 'taxcalc package' == 'installed'
