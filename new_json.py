"""
Command-line tool that converts Tax-Calculator JSON reform/assumption file
from the old (1.x) format to the new (2.0) format.
------------------------------------------------------------------------
WARNING: This program make certain assumptions about how the JSON file
         is formatted, so it will not work correctly on a JSON file
         that is not formatted in the assumed way.  There is no risk
         in trying it because a copy of the original JSON file is made.
------------------------------------------------------------------------
"""
# CODING-STYLE CHECKS:
# pycodestyle new_json.py
# pylint --disable=locally-disabled new_json.py

import os
import sys
import argparse
import shutil
import re


def main():
    """
    Contains high-level logic.
    """
    # parse command-line argument:
    usage_str = 'python new_json.py FILENAME [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Converts old (1.x) JSON reform/assumption file '
                     'named FILENAME to new (2.0) format.  The newly '
                     'formatted file is also called FILENAME, while '
                     'the old file is saved as FILENAME-old.')
    )
    parser.add_argument('FILENAME', nargs='?',
                        help=('FILENAME is name of JSON-formatted file that '
                              'is to be converted.'),
                        default='')
    args = parser.parse_args()
    # check existence of FILENAME
    if not os.path.isfile(args.FILENAME):
        msg = 'ERROR: FILENAME={} does not exist'.format(args.FILENAME)
        print(msg)
        return 1
    # copy FILENAME to FILENAME-old
    shutil.copyfile(args.FILENAME, '{}-old'.format(args.FILENAME))
    # read FILENAME into string
    with open(args.FILENAME, 'r') as oldfile:
        txt = oldfile.read()
    # convert txt elements
    defaults_file = (args.FILENAME == 'policy_current_law.json' or
                     args.FILENAME == 'consumption.json' or
                     args.FILENAME == 'growdiff.json')
    if defaults_file:
        txt = re.sub(r'(^\s*")_', r'\g<1>', txt, flags=re.MULTILINE)
    else:
        txt = re.sub(r'(\s*")_', r'\g<1>', txt, flags=re.MULTILINE)
        txt = re.sub(r'\[([0-9tf\-])', r'\g<1>', txt, flags=re.MULTILINE)
        txt = re.sub(r'([0-9e])\]', r'\g<1>', txt, flags=re.MULTILINE)
    # write converted txt to FILENAME
    with open(args.FILENAME, 'w') as newfile:
        newfile.write(txt)
    # normal return code
    return 0
# end of main function code


if __name__ == '__main__':
    sys.exit(main())
