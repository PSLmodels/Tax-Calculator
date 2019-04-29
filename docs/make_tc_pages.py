"""
Reads skeletal tc_*.htmx files and writes fleshed-out tc_*.html files
containing the standard navigation bar menu.
"""
# CODING-STYLE CHECKS:
# pycodestyle --ignore=E402 make_tc_pages.py
# pylint --disable=locally-disabled make_tc_pages.py

import os
import sys
import glob


def main():
    """
    Contains high-level logic of the script.
    """
    curdir_path = os.path.abspath(os.path.dirname(__file__))

    # read navigation-menu code into navbar variable
    navbar_filename = os.path.join(curdir_path, 'navbar.htmx')
    with open(navbar_filename, 'r') as navbar_file:
            navbar = navbar_file.read()

    # read top-button code into topbtn variable
    topbtn_filename = os.path.join(curdir_path, 'topbtn.htmx')
    with open(topbtn_filename, 'r') as topbtn_file:
            topbtn = topbtn_file.read()

    # process index.htmx and each tc_*.htmx file
    input_filenames = ['index.htmx']
    input_filenames += glob.glob(os.path.join(curdir_path, 'tc_*.htmx'))
    for ifile in input_filenames:
        # ... read input file into text variable
        with open(ifile, 'r') as infile:
            text = infile.read()
        # ... augment text variable with do-not-edit warning
        old = '<!-- #WARN# -->'
        new = ('<!-- *** NEVER EDIT THIS FILE BY HAND *** -->\n'
               '<!-- *** INSTEAD EDIT {} FILE *** -->'.format(ifile))
        text = text.replace(old, new)
        # ... augment text variable with navbar menu code
        old = '<!-- #NAVBAR# -->'
        text = text.replace(old, navbar)
        # ... augment text variable with top button code
        old = '<!-- #TOP# -->'
        text = text.replace(old, topbtn)
        # ... write text variable to output file
        with open(ifile.replace('.htmx', '.html'), 'w') as outfile:
            outfile.write(text)

    # normal return code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
