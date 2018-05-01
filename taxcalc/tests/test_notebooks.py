# CODING-STYLE CHECKS:
# pycodestyle test_notebooks.py

import os
import json
import subprocess
import pytest


def notebook_run(test_path, notebook_path):
    content = []
    for cell in json.load(open(notebook_path))['cells']:
        if cell.get('cell_type') == 'code':
            content.append('\n'.join(cell['source']))
    script = '\n  ## Next Cell ## \n'.join(content)
    sfilename = os.path.join(test_path, 'notebook_script.py')
    with open(sfilename, 'w') as sfile:
        sfile.write(script)
    rcode = subprocess.check_call(['python', sfilename], cwd=test_path)
    if os.path.exists(sfilename):
        os.remove(sfilename)
    return rcode


@pytest.mark.notebook
@pytest.mark.requires_pufcsv
@pytest.mark.skip
def test_10minutes_notebook(tests_path):
    notebook_path = os.path.join(tests_path, '..', '..',
                                 'read-the-docs', 'notebooks',
                                 '10_Minutes_to_Tax-Calculator.ipynb')
    assert notebook_run(tests_path, notebook_path) == 0
