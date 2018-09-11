"""
Tests all recipes by executing each recipeNN.py script and comparing
the script output with the expected output in the recipeNN.res file.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_recipes.py
# pylint --disable=locally-disabled test_recipes.py

from datetime import datetime
import os
import glob
import subprocess
import difflib


# print start time
print('{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

# make list of recipeNN.py filenames
RECIPES = glob.glob('./recipe[0-9][0-9].py')

# execute each recipe in RECIPES list and compare output with expected output
for recipe in RECIPES:
    out_filename = recipe.replace('.py', '.out')
    if os.path.isfile(out_filename):
        os.remove(out_filename)
    try:
        out = subprocess.check_output(['python', recipe]).decode()
    except subprocess.CalledProcessError as err:
        print('{} FAIL with error rtncode={}'.format(recipe, err.returncode))
        continue  # to next recipe
    with open(recipe.replace('.py', '.res'), 'r') as resfile:
        exp = resfile.read()
    # check for differences between out and exp results
    actual = out.splitlines(True)
    expect = exp.splitlines(True)
    diff_lines = list()
    diff = difflib.unified_diff(expect, actual,
                                fromfile='expect', tofile='actual', n=0)
    for line in diff:
        diff_lines.append(line)
    # write actual output to file if any differences; else report PASS
    if diff_lines:
        print('{} FAIL with output differences'.format(recipe))
        outfilename = recipe.replace('.py', '.out')
        with open(outfilename, 'w') as outfile:
            outfile.write(out)
    else:
        print('{} PASS'.format(recipe))

# print finish time
print('{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
