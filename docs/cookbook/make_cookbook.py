"""
Creates HTML files in parent directory from files in this directory and below.
WORKFLOW:  cd Tax-Calculator/docs/cookbook
           python test_recipes.py
then, assuming all recipies PASS, execute this script as follows:
           python make_cookbook.py
"""
# CODING-STYLE CHECKS:
# pycodestyle make_cookbook.py
# pylint --disable=locally-disabled make_cookbook.py

import os
import glob
import shutil


def write_html_file(old_filename, new_filename):
    """
    Write HTML version of old_filename in parent directory as new_filename
    """
    with open(old_filename, 'r') as ifile:
        txt = ifile.read()
    html = '<title>{}</title><pre>\n{}</pre>\n'.format(old_filename, txt)
    filename = os.path.join('..', '{}.html'.format(new_filename))
    with open(filename, 'w') as ofile:
        ofile.write(html)


# make list of recipeNN.py filenames
RECIPES = glob.glob('recipe[0-9][0-9].py')

# construct HTML files for each recipe in RECIPES list
for recipe in RECIPES:
    recipe_root = recipe.replace('.py', '')
    write_html_file('{}.{}'.format(recipe_root, 'py'),
                    '{}_{}'.format(recipe_root, 'py'))
    write_html_file('{}.{}'.format(recipe_root, 'res'),
                    '{}_{}'.format(recipe_root, 'res'))
    old_graph_name = '{}.graph.html'.format(recipe_root)
    if os.path.exists(old_graph_name):
        new_graph_name = old_graph_name.replace('.graph.html', '_graph.html')
        shutil.move(old_graph_name, os.path.join('..', new_graph_name))

# make list of *json filenames
INGREDIENTS = glob.glob('*.json')
for ingredient in INGREDIENTS:
    write_html_file(ingredient, ingredient.replace('.json', '_json'))
