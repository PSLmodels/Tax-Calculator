"""
Tests all recipes by executing each recipeNN.py program and comparing
the program output with the expected output in the recipeNN.res file.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_recipes.py
# pylint --disable=locally-disabled test_recipes.py

from datetime import datetime
import os
import glob
import subprocess
import re


# print start time
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# make list of recipeNN.py filenames
RECIPES = glob.glob('recipe[0-9][0-9].py')
RECIPES.append('recipe04_pandas.py')

# execute each recipe in RECIPES list and compare output with expected output
for recipe in sorted(RECIPES):
    out_filename = recipe.replace('.py', '.out')
    if os.path.isfile(out_filename):
        os.remove(out_filename)
    try:
        out = subprocess.check_output(['python', recipe]).decode()
    except subprocess.CalledProcessError as err:
        print('{} FAIL with error rtncode={}'.format(recipe, err.returncode))
        continue  # to next recipe
    res_filename = recipe.replace('.py', '.res')
    with open(res_filename, 'r') as resfile:
        exp = resfile.read()
    # check for differences between out and exp results ignoring whitespace
    actual = re.sub(r'\s', '', out)
    expect = re.sub(r'\s', '', exp)
    differences = actual != expect
    # write actual output to file if any differences; else report PASS
    if differences:
        with open(out_filename, 'w') as outfile:
            outfile.write(out)
        msg = '{} FAIL : actual in {} & expected in {}'
        print(msg.format(recipe, out_filename, res_filename))
    else:
        print('{} PASS'.format(recipe))

# print finish time
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
