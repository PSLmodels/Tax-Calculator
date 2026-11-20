"""
This script uses the input data files to update the availability values
of the read variables in the taxcalc/records_variables.json file.

USAGE: (taxcalc-dev) T-C% python update_availability.py
THEN CHECK:             % git diff taxcalc/records_variables.json

A variable is available in an input data file when the variable is
present in the file and has some nonzero values (missing values do not
count as nonzero values).

Only the availability information for the data sources whose input
data files are present is updated; the availability information for
the other data sources is left unchanged.  Each change in availability
is written to stdout.

WHEN TO USE: use this script whenever a new version of any input data
file is used, then regenerate the docs/guide/input_vars.md file using
the `make docs` command.
"""

import os
import re
import sys
import json
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
RVJSON_PATH = os.path.join(ROOT, 'taxcalc', 'records_variables.json')
# data sources in the order they appear in each availability value
DATA_FILES = {
    'taxdata_puf': os.path.join(ROOT, 'puf.csv'),
    'taxdata_cps': os.path.join(ROOT, 'taxcalc', 'cps.csv.gz'),
    'taxmicrodata_tmd': os.path.join(ROOT, 'tmd.csv'),
}
NONE = 'none'
VAR_LINE = re.compile(r'^    "(\w+)": \{$')
AVAIL_LINE = re.compile(r'^(\s+"availability": )"(.*)"(,?)$')


def parse_availability(value):
    """
    Return list of data sources contained in specified availability value.
    """
    if value == NONE:
        return []
    return [src.strip() for src in value.split(',')]


def make_availability(sources):
    """
    Return availability value for specified collection of data sources.
    """
    ordered = [src for src in DATA_FILES if src in sources]
    return ', '.join(ordered) if ordered else NONE


def nonzero_variables(data_path):
    """
    Return set of variable names in specified data file that have some
    nonzero values, where a missing (NaN) value is not a nonzero value.
    """
    dfx = pd.read_csv(data_path)
    return {var for var in dfx.columns
            if (dfx[var].notna() & (dfx[var] != 0)).any()}


def new_availability(read_vars, nonzero):
    """
    Return dictionary of new availability values for each read variable,
    or None if an existing availability value is invalid.
    """
    new_avail = {}
    for var, info in read_vars.items():
        old_value = info['availability']
        sources = set(parse_availability(old_value))
        if sources - set(DATA_FILES):
            print(f'ERROR: {var} has invalid availability {old_value}')
            return None
        for src, nzvars in nonzero.items():
            if var in nzvars:
                sources.add(src)
            else:
                sources.discard(src)
        new_avail[var] = make_availability(sources)
        if new_avail[var] != old_value:
            print(f'{var}: "{old_value}" ==> "{new_avail[var]}"')
    return new_avail


def revised_json_text(old_text, new_avail):
    """
    Return records_variables.json text with revised availability values
    in the read section, leaving the rest of the text unchanged.
    """
    new_lines = []
    in_read_section = False
    var = None
    for line in old_text.split('\n'):
        if line == '  "read": {':
            in_read_section = True
        elif line.startswith('  "') and in_read_section:
            in_read_section = False
        if in_read_section:
            vmatch = VAR_LINE.match(line)
            if vmatch:
                var = vmatch.group(1)
            amatch = AVAIL_LINE.match(line)
            if amatch:
                line = (f'{amatch.group(1)}"{new_avail[var]}"'
                        f'{amatch.group(3)}')
        new_lines.append(line)
    return '\n'.join(new_lines)


def main():
    """
    High-level logic of the script.
    """
    # read nonzero variables in each data file that is present
    nonzero = {}
    for src, path in DATA_FILES.items():
        if os.path.isfile(path):
            nonzero[src] = nonzero_variables(path)
        else:
            print(f'SKIPPING {src} because {path} is not present')
    if not nonzero:
        print('ERROR: no input data files are present')
        return 1
    # read records_variables.json file
    with open(RVJSON_PATH, 'r', encoding='utf-8') as jfile:
        old_text = jfile.read()
    old_dict = json.loads(old_text)
    read_vars = old_dict['read']
    # check that all data file variables are read variables
    unknown = set().union(*nonzero.values()) - set(read_vars)
    if unknown:
        print(f'ERROR: data variables not in records_variables.json: '
              f'{sorted(unknown)}')
        return 1
    # compute new availability values and revise JSON text
    new_avail = new_availability(read_vars, nonzero)
    if new_avail is None:
        return 1
    new_text = revised_json_text(old_text, new_avail)
    # check that only availability values have changed
    for var in read_vars:
        old_dict['read'][var]['availability'] = new_avail[var]
    assert json.loads(new_text) == old_dict
    # write revised records_variables.json file
    if new_text == old_text:
        print('NO CHANGES in variable availability information')
    else:
        with open(RVJSON_PATH, 'w', encoding='utf-8') as jfile:
            jfile.write(new_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
