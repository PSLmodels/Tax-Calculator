import os
import shutil
import subprocess
import tempfile

import pytest

d = os.path.dirname
TEST_DIR = d(os.path.abspath(__file__))
TOP_DIR = os.path.join(d(d(TEST_DIR)))

FILES = ('10_Minutes_to_Tax-Calculator.ipynb', 'Behavioral_example.ipynb',)
NB0 = os.path.join(TOP_DIR, 'docs',
                   'notebooks',
                   FILES[0])
NB1 = os.path.join(TOP_DIR, 'docs',
                   'notebooks',
                   FILES[1])


def notebook_run(path):
    import json
    content = []
    for cell in json.load(open(path))['cells']:
        if cell.get('cell_type') == 'code':
            content.append('\n'.join(cell['source']))
    script = '\n  ## Next Cell ## \n'.join(content)
    try:
        f = os.path.join(TEST_DIR, '10_minutes_script.py')
        with open(f, 'w') as f2:
            f2.write(script)
        args = ['python', f]
        return subprocess.check_call(args, cwd=TEST_DIR)
    finally:
        if os.path.exists(f):
            os.remove(f)


@pytest.mark.notebook
@pytest.mark.requires_pufcsv
def test_10_Minutes_to_Tax_Calculator():
    assert notebook_run(NB0) == 0


@pytest.mark.notebook
@pytest.mark.requires_pufcsv
def test_Behavioral_example():
    assert notebook_run(NB1) == 0
