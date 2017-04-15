"""
Adds JSON information to input HTML and writes augmented HTML file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 make.py
# pylint --disable=locally-disabled make.py

import sys
import os

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
INPUT_FILENAME = 'index.htmx'
INPUT_PATH = os.path.join(CUR_PATH, INPUT_FILENAME)
# --- JSON FILENAMES/PATHS GO HERE --- #
OUTPUT_FILENAME = 'index.html'
OUTPUT_PATH = os.path.join(CUR_PATH, OUTPUT_FILENAME)


def main():
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into text variable
    with open(INPUT_PATH, 'r') as ifile:
        text = ifile.read()

    # augment text variable with information from JSON files

    # write text variable to OUTPUT file
    with open(OUTPUT_PATH, 'w') as ofile:
        ofile.write(text)

    # normal return code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
