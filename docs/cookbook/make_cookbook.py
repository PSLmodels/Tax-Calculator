"""
Creates HTML files in parent directory from files in this directory and below.
WORKFLOW:  cd Tax-Calculator/docs/cookbook
           python test_recipes.py
then, assuming all recipies PASS, execute this script as follows:
           python make_cookbook.py
"""
# CODING-STYLE CHECKS:
# pycodestyle --ignore=E402 make_cookbook.py
# pylint --disable=locally-disabled make_cookbook.py

from __future__ import print_function
import os
import glob
import string
import shutil


def write_html_file(filename):
    """
    Write HTML version of filename in parent directory.
    """
    with open(filename, 'r') as ifile:
        txt = ifile.read()
    fname = string.replace(filename, 'ingredients/', '')
    html = '<title>{}</title><pre>\n{}</pre>\n'.format(fname, txt)
    ofilename = '../{}.html'.format(fname)
    with open(ofilename, 'w') as ofile:
        ofile.write(html)


# make list of recipeNN.py filenames
RECIPES = glob.glob('recipe[0-9][0-9].py')

# construct HTML files for each recipe in RECIPES list
for recipe in RECIPES:
    recipe_root = string.replace(recipe, '.py', '')
    write_html_file('{}.{}'.format(recipe_root, 'py'))
    write_html_file('{}.{}'.format(recipe_root, 'res'))
    graph = '{}.graph.html'.format(recipe_root)
    if os.path.exists(graph):
        shutil.copy(graph, '..')
        os.remove(graph)

# make list of ingredient/*json filenames
INGREDIENTS = glob.glob('ingredients/*json')
for ingr in INGREDIENTS:
    write_html_file(ingr)
