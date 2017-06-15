import pytest
import subprocess
import re


def test_for_package_existence():
    out = subprocess.check_output(['conda', 'list', 'taxcalc'])
    if re.search('taxcalc', out.decode('utf-8')) is not None:
        assert 'taxcalc package' == 'installed'
