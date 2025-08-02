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
    'ALD_BusinessLosses_c': {
        'group': 'F',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 313000},
            {'year': 2025, 'MARS': 'mjoint', 'value': 626000},
            {'year': 2025, 'MARS': 'mseparate', 'value': 313000},
            {'year': 2025, 'MARS': 'headhh', 'value': 313000},
            {'year': 2025, 'MARS': 'widow', 'value': 626000},
        ],
    },
    # G group:
    'SeniorDed_c': {
        'group': 'G',
        'changes': [
            {'year': 2025, 'value': 6000},
            {'year': 2029, 'value': 0},
        ],
    },
    # H group:
    'ID_AllTaxes_c': {
        'group': 'H',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 40000},
            {'year': 2025, 'MARS': 'mjoint', 'value': 40000},
            {'year': 2025, 'MARS': 'mseparate', 'value': 20000},
            {'year': 2025, 'MARS': 'headhh', 'value': 40000},
            {'year': 2025, 'MARS': 'widow', 'value': 40000},
            # ------
            {'year': 2026, 'MARS': 'single', 'value': 40400},
            {'year': 2026, 'MARS': 'mjoint', 'value': 40400},
            {'year': 2026, 'MARS': 'mseparate', 'value': 20200},
            {'year': 2026, 'MARS': 'headhh', 'value': 40400},
            {'year': 2026, 'MARS': 'widow', 'value': 40400},
            # ------
            {'year': 2027, 'MARS': 'single', 'value': 40804},
            {'year': 2027, 'MARS': 'mjoint', 'value': 40804},
            {'year': 2027, 'MARS': 'mseparate', 'value': 20402},
            {'year': 2027, 'MARS': 'headhh', 'value': 40804},
            {'year': 2027, 'MARS': 'widow', 'value': 40804},
            # ------
            {'year': 2028, 'MARS': 'single', 'value': 41212},
            {'year': 2028, 'MARS': 'mjoint', 'value': 41212},
            {'year': 2028, 'MARS': 'mseparate', 'value': 20606},
            {'year': 2028, 'MARS': 'headhh', 'value': 41212},
            {'year': 2028, 'MARS': 'widow', 'value': 41212},
            # ------
            {'year': 2029, 'MARS': 'single', 'value': 41624},
            {'year': 2029, 'MARS': 'mjoint', 'value': 41624},
            {'year': 2029, 'MARS': 'mseparate', 'value': 20812},
            {'year': 2029, 'MARS': 'headhh', 'value': 41624},
            {'year': 2029, 'MARS': 'widow', 'value': 41624},
            # ------
            {'year': 2030, 'MARS': 'single', 'value': 10000},
            {'year': 2030, 'MARS': 'mjoint', 'value': 10000},
            {'year': 2030, 'MARS': 'mseparate', 'value': 5000},
            {'year': 2030, 'MARS': 'headhh', 'value': 10000},
            {'year': 2030, 'MARS': 'widow', 'value': 10000},
        ],
    },
    # I group:
    'PT_qbid_taxinc_thd': {
        'group': 'I',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 200300},
            {'year': 2026, 'MARS': 'mjoint', 'value': 400600},
            {'year': 2026, 'MARS': 'mseparate', 'value': 200300},
            {'year': 2026, 'MARS': 'headhh', 'value': 200300},
            {'year': 2026, 'MARS': 'widow', 'value': 400600},
        ],
    },
    'PT_qbid_taxinc_gap': {
        'group': 'I',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 75000},
            {'year': 2026, 'MARS': 'mjoint', 'value': 150000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 75000},
            {'year': 2026, 'MARS': 'headhh', 'value': 75000},
            {'year': 2026, 'MARS': 'widow', 'value': 150000},
        ],
    },
    'PT_qbid_min_ded': {
        'group': 'I',
        'changes': [
            {'year': 2026, 'value': 400},
        ],
    },
    'PT_qbid_min_qbi': {
        'group': 'I',
        'changes': [
            {'year': 2026, 'value': 1000},
        ],
    },
    # J group:
    'ID_Charity_crt_all': {
        'group': 'J',
        'changes': [
            {'year': 2026, 'value': 0.6},
        ],
    },
    'ID_Charity_crt_noncash': {
        'group': 'J',
        'changes': [
            {'year': 2026, 'value': 0.3},
        ],
    },
    'ID_Charity_frt': {
        'group': 'J',
        'changes': [
            {'year': 2026, 'value': 0.005},
        ],
    },
    'ID_Casualty_hc': {
        'group': 'J',
        'changes': [
            {'year': 2026, 'value': 1.0},
        ],
    },
    'ID_Miscellaneous_hc': {
        'group': 'J',
        'changes': [
            {'year': 2026, 'value': 1.0},
        ],
    },
    # K group:
    'STD_allow_charity_ded_nonitemizers': {
        'group': 'K',
        'changes': [
            {'year': 2026, 'value': True},
        ],
    },
    'STD_charity_ded_nonitemizers_max': {
        'group': 'K',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 1000},
            {'year': 2026, 'MARS': 'mjoint', 'value': 2000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 1000},
            {'year': 2026, 'MARS': 'headhh', 'value': 1000},
            {'year': 2026, 'MARS': 'widow', 'value': 1000},
        ],
    },
    # L group:
    'ID_ps': {
        'group': 'L',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mjoint', 'value': 9e+99},
            {'year': 2026, 'MARS': 'mseparate', 'value': 9e+99},
            {'year': 2026, 'MARS': 'headhh', 'value': 9e+99},
            {'year': 2026, 'MARS': 'widow', 'value': 9e+99},
        ],
    },
    'ID_prt': {
        'group': 'L',
        'changes': [
            {'year': 2026, 'value': 0.0},
        ],
    },
    'ID_crt': {
        'group': 'L',
        'changes': [
            {'year': 2026, 'value': 1.0},
        ],
    },
    'ID_reduction_rate': {
        'group': 'L',
        'changes': [
            {'year': 2026, 'value': 0.05405405},  # = 2/37
        ],
    },
    # M group:
    'ID_AllTaxes_c_ps': {
        'group': 'M',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 500000},
            {'year': 2025, 'MARS': 'mjoint', 'value': 500000},
            {'year': 2025, 'MARS': 'mseparate', 'value': 250000},
            {'year': 2025, 'MARS': 'headhh', 'value': 500000},
            {'year': 2025, 'MARS': 'widow', 'value': 500000},
            # -----
            {'year': 2030, 'MARS': 'single', 'value': 9e+99},
            {'year': 2030, 'MARS': 'mjoint', 'value': 9e+99},
            {'year': 2030, 'MARS': 'mseparate', 'value': 9e+99},
            {'year': 2030, 'MARS': 'headhh', 'value': 9e+99},
            {'year': 2030, 'MARS': 'widow', 'value': 9e+99},
        ],
    },
    'ID_AllTaxes_c_po_rate': {
        'group': 'M',
        'changes': [
            {'year': 2025, 'value': 0.3},
            {'year': 2030, 'value': 0.0},
        ],
    },
    'ID_AllTaxes_c_po_floor': {
        'group': 'M',
        'changes': [
            {'year': 2025, 'MARS': 'single', 'value': 10000},
            {'year': 2025, 'MARS': 'mjoint', 'value': 10000},
            {'year': 2025, 'MARS': 'mseparate', 'value': 5000},
            {'year': 2025, 'MARS': 'headhh', 'value': 10000},
            {'year': 2025, 'MARS': 'widow', 'value': 10000},
            # -----
            {'year': 2030, 'MARS': 'single', 'value': 0},
            {'year': 2030, 'MARS': 'mjoint', 'value': 0},
            {'year': 2030, 'MARS': 'mseparate', 'value': 0},
            {'year': 2030, 'MARS': 'headhh', 'value': 0},
            {'year': 2030, 'MARS': 'widow', 'value': 0},
        ],
    },
    # N group:
    'CDCC_c': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 3000},
        ],
    },
    'CDCC_ps1': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 15000},
        ],
    },
    'CDCC_ps2': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 75000},
            {'year': 2026, 'MARS': 'mjoint', 'value': 150000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 75000},
            {'year': 2026, 'MARS': 'headhh', 'value': 75000},
            {'year': 2026, 'MARS': 'widow', 'value': 75000},
        ],
    },
    'CDCC_po1_rate_max': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 0.5},
        ],
    },
    'CDCC_po1_rate_min': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 0.35},
        ],
    },
    'CDCC_po2_rate_min': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 0.2},
        ],
    },
    'CDCC_po1_step_size': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 2000},
        ],
    },
    'CDCC_po2_step_size': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'MARS': 'single', 'value': 2000},
            {'year': 2026, 'MARS': 'mjoint', 'value': 4000},
            {'year': 2026, 'MARS': 'mseparate', 'value': 2000},
            {'year': 2026, 'MARS': 'headhh', 'value': 2000},
            {'year': 2026, 'MARS': 'widow', 'value': 2000},
        ],
    },
    'CDCC_po_rate_per_step': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': 0.01},
        ],
    },
    'CDCC_refundable': {
        'group': 'N',
        'changes': [
            {'year': 2026, 'value': False},
        ],
    },
    # O group:
    'PT_qbid_rt': {
        'group': 'O',
        'changes': [
            {'year': 2026, 'value': 0.2},
        ],
    },
    'PT_qbid_w2_wages_rt': {
        'group': 'O',
        'changes': [
            {'year': 2026, 'value': 0.5},
        ],
    },
    'PT_qbid_alt_w2_wages_rt': {
        'group': 'O',
        'changes': [
            {'year': 2026, 'value': 0.25},
        ],
    },
    'PT_qbid_alt_property_rt': {
        'group': 'O',
        'changes': [
            {'year': 2026, 'value': 0.025},
        ],
    },
    # P group:
    'ALD_AlimonyPaid_hc': {
        'group': 'P',
        'changes': [
            {'year': 2026, 'value': 1.0},
        ],
    },
    'ALD_AlimonyReceived_hc': {
        'group': 'P',
        'changes': [
            {'year': 2026, 'value': 0.0},
        ],
    },
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
