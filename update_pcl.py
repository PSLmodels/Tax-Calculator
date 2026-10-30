"""
This script uses known values of inflation-indexed policy parameters after
2025 to write an updated version of the taxcalc/policy_current_law.json file.

USAGE: (taxcalc-dev) T-C% python update_pcl.py
THEN CHECK:             % diff pcl.json taxcalc/policy_current_law.json
IF DIFFS OK:            % mv pcl.json taxcalc/policy_current_law.json

WHEN TO USE: use this script to update taxcalc/policy_current_law.json
whenever inflation rates in the growfactors.csv files are changed, or
whenever new known policy parameter values are published.
"""

import os
import sys
import json

LIST_MARS_ZERO = [
    {'year': 2026, 'MARS': 'single', 'value': 0.0},
    {'year': 2026, 'MARS': 'mjoint', 'value': 0.0},
    {'year': 2026, 'MARS': 'mseparate', 'value': 0.0},
    {'year': 2026, 'MARS': 'headhh', 'value': 0.0},
    {'year': 2026, 'MARS': 'widow', 'value': 0.0},
]
LIST_MARS_INF = [
    {'year': 2026, 'MARS': 'single', 'value': 9e99},
    {'year': 2026, 'MARS': 'mjoint', 'value': 9e99},
    {'year': 2026, 'MARS': 'mseparate', 'value': 9e99},
    {'year': 2026, 'MARS': 'headhh', 'value': 9e99},
    {'year': 2026, 'MARS': 'widow', 'value': 9e99},
]
LIST_SCALAR_ZERO = [
    {'year': 2026, 'value': 0.0},
]
NEW_KNOWN_ITEMS = {
    # PAYROLL TAX PARAMETER SOURCES:
    # - SSA Office of the Chief Actuary: Contribution and Benefit Base
    #       https://www.ssa.gov/OACT/COLA/cbb.html
    'SS_Earnings_c': [
        {'year': 2026, 'value': 184500.0},
    ],
    'SS_Earnings_thd': [
        {'year': 2026, 'value': 9e99},
    ],
    # INCOME TAX PARAMETER SOURCES:
    # - IRS Rev. Proc. 2025-32 containing 2026 policy parameter values is at:
    #       https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
    'II_brk1': [
        {'year': 2026, 'MARS': 'single', 'value': 12400.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 24800.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 12400.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 17700.0},
        {'year': 2026, 'MARS': 'widow', 'value': 24800.0},
    ],
    'II_brk2': [
        {'year': 2026, 'MARS': 'single', 'value': 50400.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 100800.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 50400.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 67450.0},
        {'year': 2026, 'MARS': 'widow', 'value': 100800.0},
    ],
    'II_brk3': [
        {'year': 2026, 'MARS': 'single', 'value': 105700.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 211400.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 105700.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 105700.0},
        {'year': 2026, 'MARS': 'widow', 'value': 211400.0},
    ],
    'II_brk4': [
        {'year': 2026, 'MARS': 'single', 'value': 201775.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 403550.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 201775.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 201750.0},
        {'year': 2026, 'MARS': 'widow', 'value': 403550.0},
    ],
    'II_brk5': [
        {'year': 2026, 'MARS': 'single', 'value': 256225.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 512450.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 256225.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 256200.0},
        {'year': 2026, 'MARS': 'widow', 'value': 512450.0},
    ],
    'II_brk6': [
        {'year': 2026, 'MARS': 'single', 'value': 640600.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 768700.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 384350.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 640600.0},
        {'year': 2026, 'MARS': 'widow', 'value': 768700.0},
    ],
    'II_brk7': [
        {'year': 2026, 'MARS': 'single', 'value': 9e99},
        {'year': 2026, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2026, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2026, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2026, 'MARS': 'widow', 'value': 9e99},
    ],
    'CG_brk1': [
        {'year': 2026, 'MARS': 'single', 'value': 49450.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 98900.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 49450.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 66200.0},
        {'year': 2026, 'MARS': 'widow', 'value': 98900.0},
    ],
    'CG_brk2': [
        {'year': 2026, 'MARS': 'single', 'value': 545500.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 613700.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 306850.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 579600.0},
        {'year': 2026, 'MARS': 'widow', 'value': 613700.0},
    ],
    'CG_brk3': [
        {'year': 2026, 'MARS': 'single', 'value': 9e99},
        {'year': 2026, 'MARS': 'mjoint', 'value': 9e99},
        {'year': 2026, 'MARS': 'mseparate', 'value': 9e99},
        {'year': 2026, 'MARS': 'headhh', 'value': 9e99},
        {'year': 2026, 'MARS': 'widow', 'value': 9e99},
    ],
    'EITC_c': [
        {'year': 2026, 'EIC': '0kids', 'value': 664.0},
        {'year': 2026, 'EIC': '1kid', 'value': 4427.0},
        {'year': 2026, 'EIC': '2kids', 'value': 7316.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 8231.0},
    ],
    'EITC_ps': [
        {'year': 2026, 'EIC': '0kids', 'value': 10860.0},
        {'year': 2026, 'EIC': '1kid', 'value': 23890.0},
        {'year': 2026, 'EIC': '2kids', 'value': 23890.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 23890.0},
    ],
    'EITC_ps_addon_MarriedJ': [
        {'year': 2026, 'EIC': '0kids', 'value': 7280.0},
        {'year': 2026, 'EIC': '1kid', 'value': 7270.0},
        {'year': 2026, 'EIC': '2kids', 'value': 7270.0},
        {'year': 2026, 'EIC': '3+kids', 'value': 7270.0},
    ],
    'EITC_InvestIncome_c': [
        {'year': 2026, 'value': 12200.0},
    ],
    'AMT_brk1': [
        {'year': 2026, 'MARS': 'single', 'value': 244500.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 244500.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 122250.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 244500.0},
        {'year': 2026, 'MARS': 'widow', 'value': 244500.0},
    ],
    'AMT_em': [
        {'year': 2026, 'MARS': 'single', 'value': 90100.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 140200.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 70100.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 90100.0},
        {'year': 2026, 'MARS': 'widow', 'value': 140200.0},
    ],
    'AMT_em_ps': [
        {'year': 2026, 'MARS': 'single', 'value': 500000.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 1000000.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 500000.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 500000.0},
        {'year': 2026, 'MARS': 'widow', 'value': 1000000.0},
    ],
    'AMT_child_em': [
        {'year': 2026, 'value': 9750.0},
    ],
    'STD': [
        {'year': 2026, 'MARS': 'single', 'value': 16100.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 32200.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 16100.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 24150.0},
        {'year': 2026, 'MARS': 'widow', 'value': 32200.0},
    ],
    'STD_Dep': [
        {'year': 2026, 'value': 1350.0},
    ],
    'STD_Dep_earned_add': [
        {'year': 2026, 'value': 450.0},
    ],
    'STD_Aged': [
        {'year': 2026, 'MARS': 'single', 'value': 2050.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 1650.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 1650.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 2050.0},
        {'year': 2026, 'MARS': 'widow', 'value': 1650.0},
    ],
    'PT_qbid_taxinc_thd': [
        {'year': 2026, 'MARS': 'single', 'value': 201750.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 403500.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 201775.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 201750.0},
        {'year': 2026, 'MARS': 'widow', 'value': 201750.0},
    ],
    'PT_qbid_min_ded': [
        {'year': 2026, 'value': 400},
    ],
    'PT_qbid_min_qbi': [
        {'year': 2026, 'value': 1000},
    ],
    'ALD_BusinessLosses_c': [
        {'year': 2026, 'MARS': 'single', 'value': 256000.0},
        {'year': 2026, 'MARS': 'mjoint', 'value': 512000.0},
        {'year': 2026, 'MARS': 'mseparate', 'value': 256000.0},
        {'year': 2026, 'MARS': 'headhh', 'value': 256000.0},
        {'year': 2026, 'MARS': 'widow', 'value': 512000.0},
    ],
    'CTC_c': [
        {'year': 2026, 'value': 2200.0},
    ],
    'ACTC_c': [
        {'year': 2026, 'value': 1700.0},
    ],
    # OTHER PARAMS THAT ARE NOT INDEXED:
    'II_em': LIST_SCALAR_ZERO,
    'II_em_ps': LIST_MARS_INF,
    'II_credit': LIST_MARS_ZERO,
    'II_credit_ps': LIST_MARS_ZERO,
    'II_credit_nr': LIST_MARS_ZERO,
    'II_credit_nr_ps': LIST_MARS_ZERO,
    'ID_Medical_c': LIST_MARS_INF,
    'ID_StateLocalTax_c': LIST_MARS_INF,
    'ID_RealEstate_c': LIST_MARS_INF,
    'ID_InterestPaid_c': LIST_MARS_INF,
    'ID_Charity_c': LIST_MARS_INF,
    'ID_Casualty_c': LIST_MARS_INF,
    'ID_Miscellaneous_c': LIST_MARS_INF,
    'ID_ps': LIST_MARS_INF,
    'ID_c': LIST_MARS_INF,
    'CG_ec': LIST_SCALAR_ZERO,
    'PT_qbid_ps': LIST_MARS_INF,
    'CTC_new_ps': LIST_MARS_ZERO,
    'UBI_u18': LIST_SCALAR_ZERO,
    'UBI_1820': LIST_SCALAR_ZERO,
    'UBI_21': LIST_SCALAR_ZERO,
}
for num in range(1, 3 + 1):
    NEW_KNOWN_ITEMS[f'AMT_CG_brk{num}'] = NEW_KNOWN_ITEMS[f'CG_brk{num}']


def main():
    """
    High-level script logic.
    """
    # read existing policy_current_law.json into pdict dictionary
    fname = os.path.join('taxcalc', 'policy_current_law.json')
    with open(fname, 'r', encoding='utf-8') as jfile:
        pdict = json.load(jfile)

    # update indexed parameter values in pdict dictionary using NEW_KNOWN_ITEMS
    num_indexed_params = 0
    for pname, pinfo in pdict.items():
        if pname == 'schema':
            continue
        if not pinfo.get('indexed', False):
            continue
        num_indexed_params += 1
        if pname not in NEW_KNOWN_ITEMS:
            print(f'NO NEW_KNOWN_ITEMS FOR INDEXED POLICY PARAMETER {pname}')
            continue
        # specify plist as policy_current_law.json value list
        plist = pdict[pname]['value']
        # specify new list and its first_new_year in NEW_KNOWN_ITEMS
        newlist = NEW_KNOWN_ITEMS[pname]
        first_new_year = newlist[0]['year']
        # remove plist items for years no less than first_new_year
        while True:
            if plist[-1]['year'] >= first_new_year:
                del plist[-1]
            else:
                break  # out of while loop
        # add newlist to end of plist
        pdict[pname]['value'] = plist + newlist
    print('NUMBER OF INDEXED PARAMETERS =', num_indexed_params)

    # write updated pdict dictionary to pcl.json file
    with open('pcl.json', 'w', encoding='utf-8') as jfile:
        jfile.write(json.dumps(pdict, indent=4) + '\n')

    # return no-error exit code
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
