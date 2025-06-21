"""
This policy parameter projection script, which calculates policy
parameter values that were changed by TCJA and will revert to
their pre-TCJA values in 2026 (adjusted for inflation).

USAGE: (taxcalc-dev) T-C% python ppp.py
THEN CHECK:             % diff pcl.json taxcalc/policy_current_law.json
IF DIFFS OK             % mv pcl.json taxcalc/policy_current_law.json

WHEN TO USE: use this script to update taxcalc/policy_current_law.json
whenever post-2016 inflation rates in the growfactors.csv files are changed.
"""

import sys
import re
from pathlib import Path
from taxcalc import Policy

REVERTING_PARAMS = {
    'ALD_BusinessLosses_c': 2029,
    'II_em': 2026,
    'II_em_ps': 2026,
    'STD': 2026,
    'ID_AllTaxes_c': 2026,
    'ID_ps': 2026,
    'II_brk1': 2026,
    'II_brk2': 2026,
    'II_brk3': 2026,
    'II_brk4': 2026,
    'II_brk5': 2026,
    'II_brk6': 2026,
    'II_brk7': 2026,
    'PT_qbid_taxinc_thd': 2026,
    'AMT_em': 2026,
    'AMT_em_ps': 2026,
    'AMT_em_pe': 2026,
}
MARS_VALUES = ['single', 'mjoint', 'mseparate', 'headhh', 'widow']
PYEAR = 2017  # prior year before TCJA first implemented
FYEAR = 2026  # final year in which parameter values revert


def cumulative_ifactor():
    """
    Return PYEAR-to_FYEAR inflation factor.
    """
    pol = Policy()
    # calculate the inflation factor used to calculate the
    # inflation-adjusted 2026 reverting parameter values
    # NOTE: pvalue[t+1] = pvalue[t] * ( 1 + irate[t] )
    cum_ifactor = 1.0
    for year in range(PYEAR, FYEAR):
        # pylint: disable=protected-access
        rate = pol._inflation_rates[year - pol.start_year]
        cum_ifactor *= 1.0 + rate
    return cum_ifactor


def integrate_fragments(fragments):
    """
    Integrate specified fragments with the policy_current_law.json text.
    """
    # pylint: disable=too-many-locals
    p_c_l_path = Path('.') / 'taxcalc' / 'policy_current_law.json'
    with open(p_c_l_path, 'r', encoding='utf-8') as ofile:
        olines = ofile.readlines()
    # pylint: disable=consider-using-with
    nfile = open('pcl.json', 'w', encoding='utf-8')
    re_param_line = re.compile(r'^\s{4}"(\w+)": {$')
    re_ryear26_line = re.compile(r'^\s{16}"year": 2026,$')
    re_ryear29_line = re.compile(r'^\s{16}"year": 2029,$')
    re_value_line = re.compile(r'^\s{16}"value":')
    writing_oline = True
    pname_has_fragments = False
    for oline in olines:
        pmatch = re_param_line.search(oline)
        if pmatch:
            pname = pmatch.group(1)
            pname_has_fragments = pname in fragments
            if pname_has_fragments:
                if fragments[pname][0]['year'] == 2026:
                    re_ryear_line = re_ryear26_line
                else:
                    re_ryear_line = re_ryear29_line
                idx = -1
        elif pname_has_fragments:
            ymatch = re_ryear_line.search(oline)
            if ymatch:
                idx += 1
        if pname_has_fragments and idx >= 0:
            if re_value_line.search(oline):
                writing_oline = False
            else:
                writing_oline = True
        if writing_oline:
            nfile.write(oline)
        else:
            nfile.write(
                f'                "value": {fragments[pname][idx]["value"]}\n'
            )
    nfile.close()
    return 0


def main():
    """
    High-level script logic.
    """
    ifactor = cumulative_ifactor()

    # construct policy_current_law.json revert-year fragments
    # for each reverting parameter in a fragments dictionary
    fragments = {}
    parameters = Policy()
    for pname, ryear in REVERTING_PARAMS.items():
        vos = parameters.select_eq(pname, year=PYEAR)
        frag_list = []
        for vo in vos:
            rval = min(9e99, round(vo['value'] * ifactor, 0))
            frag_list.append({'year': ryear, 'value': rval})
        fragments[pname] = frag_list

    # integrate fragment info into existing policy_current_law.json
    rcode = integrate_fragments(fragments)

    # return exit code returned by integrate_fragments function
    return rcode
# end main function code


if __name__ == '__main__':
    sys.exit(main())
