"""
This script implements policy parameters to reflect new OBBBA policy.

USAGE: (taxcalc-dev) OBBBA% ./implement.sh GROUP
THEN CHECK                % [g]diff pcl.json pcl-510.json
IF DIFFS OK               % mv pcl.json ../taxcalc/policy_current_law.json
MAKE PACKAGE              % pushd .. ; make package ; popd
EXECUTE tally.sh          % ./tally.sh
ASSESS tally.results DIFF % [g]diff tally.res-new tally.result
REVERT POLICY CHANGES     % git restore ../taxcalc/policy_current_law.json
REMOVE PACKAGE            % pushd .. ; make clean ; popd
"""

import os
import re
import sys
import json
import argparse

LIST_PARAMS = False

OBBBA_PARAMS = {
    # A group:
    'AMT_em': {
        'group': 'A',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 89400},
            {'year': 2026, 'MARS': 'mjoint', 'value': 139000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 69600},
            {'year': 2026, 'MARS': 'headhh', 'value': 89400},
            {'year': 2026, 'MARS': 'widow', 'value': 139000},
        ],
    },
    'AMT_em_ps': {
        'group': 'A',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 500000},
            {'year': 2026, 'MARS': 'mjoint', 'value': 1000000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 500000},
            {'year': 2026, 'MARS': 'headhh', 'value': 500000},
            {'year': 2026, 'MARS': 'widow', 'value': 1000000},
        ],
    },
    'AMT_em_pe': {
        'group': 'A',
        'changes': [
            {'year': 2026, 'value': 639200},
        ],
    },
    # B group:
    'II_rt1': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.1},
        ],
    },
    'II_brk1': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 11925},
            {'year': 2026, 'MARS': 'mjoint', 'value': 23850},
            {'year': 2026, 'MARS': 'mseparate', 'value': 11925},
            {'year': 2026, 'MARS': 'headhh', 'value': 17000},
            {'year': 2026, 'MARS': 'widow', 'value': 23850},
        ],
    },
    'II_rt2': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.12},
        ],
    },
    'II_brk2': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 48475},
            {'year': 2026, 'MARS': 'mjoint', 'value': 96950},
            {'year': 2026, 'MARS': 'mseparate', 'value': 48475},
            {'year': 2026, 'MARS': 'headhh', 'value': 64850},
            {'year': 2026, 'MARS': 'widow', 'value': 96950},
        ],
    },
    'II_rt3': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.22},
        ],
    },
    'II_brk3': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 104900},
            {'year': 2026, 'MARS': 'mjoint', 'value': 208300},
            {'year': 2026, 'MARS': 'mseparate', 'value': 104900},
            {'year': 2026, 'MARS': 'headhh', 'value': 104900},
            {'year': 2026, 'MARS': 'widow', 'value': 208300},
        ],
    },
    'II_rt4': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.24},
        ],
    },
    'II_brk4': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 198800},
            {'year': 2026, 'MARS': 'mjoint', 'value': 397650},
            {'year': 2026, 'MARS': 'mseparate', 'value': 198800},
            {'year': 2026, 'MARS': 'headhh', 'value': 198800},
            {'year': 2026, 'MARS': 'widow', 'value': 397650},
        ],
    },
    'II_rt5': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.32},
        ],
    },
    'II_brk5': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 256450},
            {'year': 2026, 'MARS': 'mjoint', 'value': 512950},
            {'year': 2026, 'MARS': 'mseparate', 'value': 256450},
            {'year': 2026, 'MARS': 'headhh', 'value': 256486},
            {'year': 2026, 'MARS': 'widow', 'value': 512950},
        ],
    },
    'II_rt6': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.35},
        ],
    },
    'II_brk6': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 643950},
            {'year': 2026, 'MARS': 'mjoint', 'value': 772750},
            {'year': 2026, 'MARS': 'mseparate', 'value': 386350},
            {'year': 2026, 'MARS': 'headhh', 'value': 643950},
            {'year': 2026, 'MARS': 'widow', 'value': 772750},
        ],
    },
    'II_rt7': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'value': 0.37},
        ],
    },
    'II_brk7': {
        'group': 'B',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mjoint', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mseparate', 'value': 9e+99},
            {'year': 2026, 'MARS': 'headhh', 'value': 9e+99},
            {'year': 2026, 'MARS': 'widow', 'value': 9e+99},
        ],
    },
    # C group:
    'CTC_c': {
        'group': 'C',
        'indexed': True,
        'changes': [
            {'year': 2025, 'value': 2200},
        ],
    },
    'CTC_ps': {
        'group': 'C',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 200000},
            {'year': 2025, 'MARS': 'mjoint', 'value': 400000},
            {'year': 2025, 'MARS': 'mseparate', 'value': 200000},
            {'year': 2025, 'MARS': 'headhh', 'value': 200000},
            {'year': 2025, 'MARS': 'widow', 'value': 400000},
        ],
    },
    'ACTC_c': {
        'group': 'C',
        'indexed': True,
        'changes': [
            {'year': 2025, 'value': 1700},
        ],
    },
    'ACTC_Income_thd': {
        'group': 'C',
        'changes': [
            {'year': 2025, 'value': 2500},
        ],
    },
    'ODC_c': {
        'group': 'C',
        'changes': [
            {'year': 2025, 'value': 500},
        ],
    },
    # D group:
    'STD': {
        'group': 'D',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 15750},
            {'year': 2025, 'MARS': 'mjoint', 'value': 31500},
            {'year': 2025, 'MARS': 'mseparate', 'value': 15750},
            {'year': 2025, 'MARS': 'headhh', 'value': 23625},
            {'year': 2025, 'MARS': 'widow', 'value': 31500},
        ],
    },
    # E group:
    'II_em': {
        'group': 'E',
        'changes': [
            {'year': 2026, 'value': 0.0},
        ],
    },
    'II_em_ps': {
        'group': 'E',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mjoint', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mseparate', 'value': 9e+99},
            {'year': 2026, 'MARS': 'headhh', 'value': 9e+99},
            {'year': 2026, 'MARS': 'widow', 'value': 9e+99},
        ],
    },
    # F group:
}


def revised_value(pdict, odict):
    """
    Returns OBBBA-revised pdict['value'] given parameter's OBBBA odict.
    """
    # determine first_year of OBBBA reform in odict
    first_year = odict['changes'][0]['year']

    # remove pdict['value'] list items for first_year and subsequent years
    while True:
        if pdict['value'][-1]['year'] >= first_year:
            del pdict['value'][-1]
        else:
            break  # out of while loop

    # add OBBBA changes to end of pdict['value'] list
    new_pdict_value = pdict['value'] + odict['changes']

    return new_pdict_value


def list_param_info(policy_dict):
    """
    Prints to sdtout information about all policy parameters.
    """
    for pname, pdict in policy_dict.items():
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
        pcldict = json.load(jfile)

    # optionally list parameter information and quit
    if LIST_PARAMS:
        list_param_info(pcldict)
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
    for pname, pdict in pcldict.items():
        if pname == 'schema':
            continue
        if pname not in OBBBA_PARAMS:
            continue
        if group not in ['ALL', OBBBA_PARAMS[pname]['group']]:
            continue
        pcount += 1
        odict = OBBBA_PARAMS[pname]
        if 'indexed' in odict:
            assert 'indexed' in pdict, f'ERROR: {pname} has no indexed item'
            pcldict[pname]['indexed'] = odict['indexed']
        pcldict[pname]['value'] = revised_value(pdict, odict)

    # write updated policy dictionary to pcl.json file
    with open('pcl.json', 'w', encoding='utf-8') as jfile:
        jfile.write(json.dumps(pcldict, indent=4) + '\n')

    print(f'Implemented OBBBA policy for {pcount} parameters in pcl.json file')

    # return no-error exit code
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
