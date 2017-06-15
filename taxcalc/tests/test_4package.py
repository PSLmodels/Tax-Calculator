import re
import subprocess
import pytest

@pytest.mark.one
def test_for_package_existence():
    """
    Ensure that no conda taxcalc package is installed when running pytest
    """
    out = subprocess.check_output(['conda', 'list', 'taxcalc'])
    if re.search('taxcalc', out.decode('ascii')) is not None:
        assert 'taxcalc package' == 'installed'
