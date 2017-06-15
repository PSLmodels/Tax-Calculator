import pytest
import subprocess
import re


def test_for_package_existence():
    res = subprocess.check_output(['conda', 'list', 'taxcalc'])
    if re.search('taxcalc', res) is not None:
        assert 'taxcalc package' == 'installed'
