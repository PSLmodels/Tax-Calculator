"""
Tests all recipes by executing each recipeNN.py script and comparing
the script output with the expected output in the recipeNN.res file.
"""
# CODING-STYLE CHECKS:
# pycodestyle --ignore=E402 test_recipes.py
# pylint --disable=locally-disabled test_recipes.py

from __future__ import print_function
from datetime import datetime
import os
import glob
import string
import subprocess
import difflib


# print start time
print('{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

# make list of recipeNN.py filenames
RECIPES = glob.glob('./recipe[0-9][0-9].py')

# execute each recipe in RECIPES list and compare output with expected output
for recipe in RECIPES:
    out_filename = string.replace(recipe, '.py', '.out')
    if os.path.isfile(out_filename):
        os.remove(out_filename)
    try:
        out = subprocess.check_output(['python', recipe])
    except subprocess.CalledProcessError as err:
        print('{} FAIL with error rtncode={}'.format(recipe, err.returncode))
        continue  # to next recipe
    with open(string.replace(recipe, '.py', '.res'), 'r') as resfile:
        exp = resfile.read()
    # check for differences between out and exp results
    actual = out.splitlines(True)
    expected = exp.splitlines(True)
    diff_lines = list()
    diff = difflib.unified_diff(expected, actual,
                                fromfile='expected', tofile='actual', n=0)
    for line in diff:
        diff_lines.append(line)
    # write actual output to file if any differences; else report PASS
    if diff_lines:
        print('{} FAIL with output differences'.format(recipe))
        outfilename = string.replace(recipe, '.py', '.out')
        with open(outfilename, 'w') as outfile:
            outfile.write(out)
    else:
        print('{} PASS'.format(recipe))

# print finish time
print('{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
