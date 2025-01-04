"""
Creates documentation markdown files for each set of parameters and
variables in Tax-Calculator, using header templates and other scripts in
this folder, and JSON files from Tax-Calculator.
"""
# CODING-STYLE CHECKS:
# pycodestyle make_uguide.py
# pylint --disable=locally-disabled make_uguide.py

import os
import sys
# Other scripts in this folder.
import make_params
import make_io_vars

CURDIR_PATH = os.path.abspath(os.path.dirname(__file__))

TAXCALC_PATH = os.path.join(CURDIR_PATH, '../../..', 'taxcalc')

# INPUT_PATH = os.path.join(CURDIR_PATH, INPUT_FILENAME)
# Use TCJA to determine whether policies change in 2026.
TCJA_PATH = os.path.join(TAXCALC_PATH, 'reforms/TCJA.json')
POLICY_PATH = os.path.join(TAXCALC_PATH, 'policy_current_law.json')
IOVARS_PATH = os.path.join(TAXCALC_PATH, 'records_variables.json')
CONSUMPTION_PATH = os.path.join(TAXCALC_PATH, 'consumption.json')
GROWDIFF_PATH = os.path.join(TAXCALC_PATH, 'growdiff.json')
TEMPLATE_PATH = os.path.join(CURDIR_PATH, '../templates')
OUTPUT_PATH = os.path.join(CURDIR_PATH, '..')

START_YEAR = 2013
END_YEAR_SHORT = 2020
END_YEAR_LONG = 2027


def main():
    # Policy parameters.
    policy_param_text = make_params.make_params(POLICY_PATH, 'policy')
    write_file(policy_param_text, 'policy_params')
    # Assumption parameters, created separately for growdiff and consumption.
    growdiff_param_text = make_params.make_params(GROWDIFF_PATH, 'growdiff')
    consumption_param_text = make_params.make_params(CONSUMPTION_PATH,
                                                     'consumption')
    assumption_param_text = ('## Growdiff\n\n' + growdiff_param_text +
                             '\n\n## Consumption\n\n' + consumption_param_text)
    write_file(assumption_param_text, 'assumption_params')
    # Input and output variables.
    input_var_text = make_io_vars.make_io_vars(IOVARS_PATH, 'read')
    write_file(input_var_text, 'input_vars')
    output_var_text = make_io_vars.make_io_vars(IOVARS_PATH, 'calc')
    write_file(output_var_text, 'output_vars')
    # Normal return code
    return 0


def write_file(text, file):
    """ Writes the concatenation of a template and calculated text to a file.

    Args:
        text: String with calculated documentation.
        file: Filename (without '.md' or a path). Must also match the filename
            of the template.

    Returns:
        Nothing. Result is written to file.
    """
    template = os.path.join(TEMPLATE_PATH, file + '_template.md')
    outfile = os.path.join(OUTPUT_PATH, file + '.md')
    with open(template, 'r') as f:
        template_text = f.read()
    with open(outfile, 'w') as f:
        f.write(template_text + '\n\n' + text)


if __name__ == '__main__':
    sys.exit(main())
