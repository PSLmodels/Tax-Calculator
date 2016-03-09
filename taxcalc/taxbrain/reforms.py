"""
Python script that compares federal individual income tax reform results
produced by the Tax-Calculator taxcalc package on this computer with those
produced by the TaxBrain Internet site.

COMMAND-LINE USAGE: python reforms.py

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 reforms.py
# pylint --disable=locally-disabled reforms.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
PUF_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
import re
import json


def main():
    """
    .................
    """
    # read reforms.json file and convert to a dictionary of reforms
    reforms_dict = read_reforms_json_file('reforms.json')

    # ...
    for ref in sorted(reforms_dict):
        reform = reforms_dict.get(ref)
        start_year = reform['taxbrain_start_year']
        reform_name = reform['name']
        reform_spec = reform['spec']
        reform_dict = Policy.convert_reform_dictionary(reform_spec)
        print '*** REFORM:', ref, start_year, reform_name
        print '      SPEC:', reform_spec
        print '      DICT:', reform_dict

    # calc = Calculator(policy=Policy(), records=Records(data=PUF_PATH))
    # calc.diagnostic_table(num_years=5)

    # return no-error exit code
    return 0
# end of main function code


def read_reforms_json_file(filename):
    """
    Read specified filename; strip //-comments;
    and return dictionary of  if is valid JSON
    """
    with open(filename, 'r') as reforms_file:
        json_with_comments = reforms_file.read()
    json_without_comments = re.sub('//.*', '', json_with_comments)
    try:
        reforms_dict = json.loads(json_without_comments)
    except ValueError:
        msg = 'reforms.json file contains invalid JSON'
        line = '----------------------------------------------------------'
        txt = ('TO FIND FIRST JSON SYNTAX ERROR,\n'
               'COPY TEXT BETWEEN LINES AND '
               'PASTE INTO BOX AT jsonlint.com')
        sys.stderr.write(txt + '\n')
        sys.stderr.write(line + '\n')
        sys.stderr.write(json_without_comments.strip() + '\n')
        sys.stderr.write(line + '\n')
        raise ValueError(msg)
    return reforms_dict


if __name__ == '__main__':
    sys.exit(main())
