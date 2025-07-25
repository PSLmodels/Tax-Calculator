"""
This script implements policy parameters to reflect new OBBBA policy.

USAGE: (taxcalc-dev) OBBBA% python implement.py
THEN CHECK:             % [g]diff pcl.json pcl-510.json
IF DIFFS OK:            % mv pcl.json taxcalc/policy_current_law.json
MAKE PACKAGE AND EXECUTE tally.sh AND ASSESS tally.results
REVERT CHANGES IN taxcalc/policy_current_law.json
"""

import os
import re
import sys
import json
import argparse

LIST_PARAMS = False

OBBBA_PARAMS = {
    'pname': {
        'group': 'A',
        'values': [
        ],
    },
    # 'SS_Earnings_c': [
    #     {'year': 2023, 'value': 160200.0},
    #     {'year': 2024, 'value': 168600.0},
    #     {'year': 2025, 'value': 176100.0},
    #  ],
    # 'II_brk1': [
    #     {'year': 2023, 'MARS': 'single', 'value': 11000.0},
    #     {'year': 2023, 'MARS': 'mjoint', 'value': 22000.0},
    #     {'year': 2023, 'MARS': 'mseparate', 'value': 11000.0},
    #     {'year': 2023, 'MARS': 'headhh', 'value': 15700.0},
    #     {'year': 2023, 'MARS': 'widow', 'value': 22000.0},
    #  ],
}


def list_param_info(poldict):
    """
    Prints to sdtout information about all policy parameters.
    """
    for pname, pdict in poldict.items():
        if pname == 'schema':
            continue
        # get inflation-indexing status of parameter
        inf = 'indexed' if pdict.get('indexed', False) else 'static'
        # get vector index of parameter
        value_list = pdict['value']
        assert isinstance(value_list, list)
        val0 = value_list[0]
        assert isinstance(val0, dict)
        if 'MARS' in val0:
            idx = 'MARS'
        elif 'EIC' in val0:
            idx = 'EIC'
        else:
            idx = 'scalar'
        print(f'{pname} {inf} {idx}')


def main():
    """
    High-level script logic.
    """
    # read existing policy_current_law.json into a policy dictionary
    fname = os.path.join('..', 'taxcalc', 'policy_current_law.json')
    with open(fname, 'r', encoding='utf-8') as jfile:
        poldict = json.load(jfile)

    # optionally list parameter information and quit
    if LIST_PARAMS:
        list_param_info(poldict)
        return 1

    # parse command line argument(s)
    parser = argparse.ArgumentParser(
        prog='',
        usage='python implement.py [--group GROUP]',
        description='Write pcl.json containing OBBBA parameter values.',
    )
    parser.add_argument(
        '--group',
        help='GROUP is optional name of paramter group.',
        default='all',
    )
    args = parser.parse_args()
    group = args.group.upper()
    if group == 'ALL':
        print('OBBBA/implement.py is using ALL groups')
    else:
        if len(group) == 1:
            if re.match('[A-Z]', group):
                print(f'OBBBA/implement.py is using {group} group')
            else:
                print(f'ERROR: GROUP={group} must be a single letter')
                return 1
        else:
            print(f'ERROR: GROUP={group} is not a single character')
            return 1

    # implmment OBBBA values for parameter in specified group(s)
    pcount = 0
    for pname, pdict in poldict.items():
        if pname == 'schema':
            continue
        if pname not in OBBBA_PARAMS:
            continue
        if group not in ['ALL', OBBBA_PARAMS[pname]['group']]:
            continue
        pcount += 1

        """
        plist = pdict[pname]['value']
        # ... see if adding values before existing plist items for 2026
        bindex = None
        for itm in plist:
            if itm['year'] == 2026:
                bindex = plist.index(itm)
                break
        # ... add new items to plist for this pname
        for item in NEW_KNOWN_ITEMS[pname]:
            if item in plist:
                continue
            if bindex:
                plist.insert(bindex, item)
                bindex += 1
            else:
                plist.append(item)
        """

    # write updated policy dictionary to pcl.json file
    with open('pcl.json', 'w', encoding='utf-8') as jfile:
        jfile.write(json.dumps(poldict, indent=4) + '\n')

    print(f'Implemented OBBBA policy for {pcount} parameters in pcl.json file')

    # return no-error exit code
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
