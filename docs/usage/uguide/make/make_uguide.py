"""
Reads skeletal uguide.htmx file and writes fleshed-out uguide.html file
containing information from several JSON files.
"""
# CODING-STYLE CHECKS:
# pycodestyle make_uguide.py
# pylint --disable=locally-disabled make_uguide.py

import os
import sys
from collections import OrderedDict
import taxcalc as tc


INPUT_FILENAME = 'test_in.md'
OUTPUT_FILENAME = 'test_out.md'

CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))

TAXCALC_PATH = os.path.join(CURDIR_PATH, '..', 'taxcalc')

# INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
# Use TCJA to determine whether policies change in 2026.
TCJA_PATH = os.path.join(CURDIR_PATH,'../taxcalc/reforms/TCJA.json')
POLICY_PATH = os.path.join(TAXCALC_PATH, 'policy_current_law.json')
IOVARS_PATH = os.path.join(TAXCALC_PATH, 'records_variables.json')
CONSUMPTION_PATH = os.path.join(TAXCALC_PATH, 'consumption.json')
GROWDIFF_PATH = os.path.join(TAXCALC_PATH, 'growdiff.json')
TEMPLATE_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
OUTPUT_PATH = os.path.join(CURDIR_PATH, OUTPUT_FILENAME)

START_YEAR = 2013
END_YEAR_SHORT = 2020
END_YEAR_LONG = 2027

def main():
    """
    Creates documentation markdown files for each set of parameters and
    variables in Tax-Calculator, using header templates and other scripts in
    this folder.
    """
    # Policy parameters.
    policy_param_text = 
    write_file(, policy_param_text, )
    # augment text variable with information from JSON files
    # text = io_variables('read', IOVARS_PATH, text)
    # text = io_variables('calc', IOVARS_PATH, text)
    # text = assumption_params('consumption', CONSUMPTION_PATH, text)
    # text = assumption_params('growdiff', GROWDIFF_PATH, text)

    # normal return code
    return 0
# end of main function code


def write_file(template_path, add_text, file):
    """ Writes the concatenation of a template and calculated text to a file.

    Args:
        template_path: Path holding template header text file.
        add_text: String with calculated documentation.
        file: Filename where result is written.

    Returns:
        Nothing. Result is written to file.
    """
    with open(template,'r') as f:
        text = f.read()
    text += add_text
    with open(file, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    sys.exit(main())
