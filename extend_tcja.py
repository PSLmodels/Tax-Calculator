"""
This script generates a JSON reform file, which could be called
extend_tcja.json, that can serve as an alternative baseline to
current-law policy (which ends TCJA temporary provisions after 2025).

USAGE: (taxcalc-dev) Tax-Calculator% python extend_tcja.py > ext.json
  THEN CHECK:                      % diff ext.json taxcalc/reforms/ext.json
  IF DIFFS:                        % mv ext.json taxcalc/reforms/ext.json

WHEN TO USE: use this script to update reforms/ext.json in these situations:
(a) whenever inflation rates in the growfactors.csv files are changed
OR
(b) whenever inflation-indexed parameters are updated (usually as part
    of changes that increase the value of Policy.LAST_KNOWN_YEAR).
"""

import sys
import numpy
import taxcalc

TCJA_CATEGORY = None  # set to None to generate all TCJA temporary provisions
TCJA_PARAMETERS = {
    # category 1 ...
    "II_rt1": {"indexed": False, "category": 1},
    "II_brk1": {"indexed": True, "category": 1},
    "II_rt2": {"indexed": False, "category": 1},
    "II_brk2": {"indexed": True, "category": 1},
    "II_rt3": {"indexed": False, "category": 1},
    "II_brk3": {"indexed": True, "category": 1},
    "II_rt4": {"indexed": False, "category": 1},
    "II_brk4": {"indexed": True, "category": 1},
    "II_rt5": {"indexed": False, "category": 1},
    "II_brk5": {"indexed": True, "category": 1},
    "II_rt6": {"indexed": False, "category": 1},
    "II_brk6": {"indexed": True, "category": 1},
    "II_rt7": {"indexed": False, "category": 1},
    "II_brk7": {"indexed": True, "category": 1},
    # category 2 ...
    "CTC_c": {"indexed": False, "category": 2},
    "ACTC_c": {"indexed": True, "category": 2},
    "ACTC_c-indexed": {"indexed": False, "category": 2},
    "ODC_c": {"indexed": False, "category": 2},
    "CTC_ps": {"indexed": False, "category": 2},
    "ACTC_Income_thd": {"indexed": False, "category": 2},
    # category 3 ...
    "AMT_em": {"indexed": True, "category": 3},
    "AMT_em_ps": {"indexed": True, "category": 3},
    "AMT_em_pe": {"indexed": True, "category": 3},
    # category 4 ...
    "STD": {"indexed": True, "category": 4},
    # category 5 ...
    "ID_AllTaxes_c": {"indexed": False, "category": 5},
    "ID_Charity_crt_all": {"indexed": False, "category": 5},
    "ID_Casualty_hc": {"indexed": False, "category": 5},
    "ID_Miscellaneous_hc": {"indexed": False, "category": 5},
    "ID_ps": {"indexed": True, "category": 5},
    "ID_prt": {"indexed": False, "category": 5},
    "ID_crt": {"indexed": False, "category": 5},
    # category 6 ...
    "II_em": {"indexed": True, "category": 6},
    "II_em_ps": {"indexed": True, "category": 6},
    # category 7 ...
    "PT_qbid_rt": {"indexed": False, "category": 7},
    "PT_qbid_taxinc_thd": {"indexed": True, "category": 7},
    "PT_qbid_taxinc_gap": {"indexed": False, "category": 7},
    "PT_qbid_w2_wages_rt": {"indexed": False, "category": 7},
    "PT_qbid_alt_w2_wages_rt": {"indexed": False, "category": 7},
    "PT_qbid_alt_property_rt": {"indexed": False, "category": 7},
    # category 8 ...
    "ALD_BusinessLosses_c": {"indexed": True, "category": 8},
}


def main():
    """
    High-level script logic.
    """
    # pylint: disable=too-many-statements,too-many-branches

    # identify last parameter name in TCJA_PARAMETERS
    last_pname = list(TCJA_PARAMETERS.keys())[-1]
    # calculate 2025-to-2026 parameters indexing factor
    pol = taxcalc.Policy()
    pirates = pol.inflation_rates()
    ifactor25 = 1.0 + pirates[2025 - taxcalc.Policy.JSON_START_YEAR]
    ifactor28 = 1.0 + pirates[2028 - taxcalc.Policy.JSON_START_YEAR]
    # specify extend-TCJA-beyond-2025 reform
    # ... get 2025 parameter values
    year = 2025
    pol.set_year(year)
    pdata = dict(pol.items())
    # ... write reform header comments
    print(f'// REFORM TO EXTEND TEMPORARY TCJA PROVISIONS BEYOND {year}')
    print(f'// USING TAX-CALCULATOR {taxcalc.__version__}')
    print(f'// WITH 2025-to-2026 INDEXING FACTOR = {ifactor25:.6f}')
    print(f'//  AND 2028-to-2029 INDEXING FACTOR = {ifactor28:.6f}')
    if TCJA_CATEGORY:
        print(f'// ONLY TCJA PROVISIONS IN CATEGORY {TCJA_CATEGORY}')
    print('{')
    # ... set 2026/29 nonreverted values for the parameters set to revert
    left_brace = '{'
    right_brace = '}'
    year = 2026
    for pname, pinfo in TCJA_PARAMETERS.items():
        if TCJA_CATEGORY and pinfo['category'] != TCJA_CATEGORY:
            continue  # skip this parameter
        if pname == 'ACTC_c-indexed':
            year = 2026
            sys.stdout.write(f'    "{pname}": ')
            sys.stdout.write(f'{left_brace}"{year}": ')
            sys.stdout.write('true')
            sys.stdout.write(f'{right_brace}{trailing_comma}\n')
            continue  # to top of the for pname, pinfo loop
        if pname == 'ALD_BusinessLosses_c':
            ifactor = ifactor28
            year = 2029
            pol.set_year(2028)
            pdata = dict(pol.items())
        else:
            if year != 2026:
                pol.set_year(2025)
                pdata = dict(pol.items())
            ifactor = ifactor25
            year = 2026
        trailing_comma = '' if pname == last_pname else ','
        if pinfo['indexed']:
            pval = pdata[pname][0] * ifactor
            if isinstance(pval, numpy.ndarray):
                # handle vector parameter
                pval = numpy.minimum(9e99, pval.round(2))
                sys.stdout.write(f'    "{pname}": ')
                sys.stdout.write(f'{left_brace}"{year}": ')
                sys.stdout.write(f'{pval.tolist()}')
                sys.stdout.write(f'{right_brace}{trailing_comma}\n')
            else:
                # handle scalar parameter
                pval = min(9e99, pval)
                sys.stdout.write(f'    "{pname}": ')
                sys.stdout.write(f'{left_brace}"{year}": ')
                sys.stdout.write(f'{(pval * ifactor):.2f}')
                sys.stdout.write(f'{right_brace}{trailing_comma}\n')
        else:  # if parameter is not indexed
            pval = pdata[pname][0]
            if isinstance(pval, numpy.ndarray):
                # handle vector parameter
                pval = numpy.minimum(9e99, pval.round(2))
                sys.stdout.write(f'    "{pname}": ')
                sys.stdout.write(f'{left_brace}"{year}": ')
                sys.stdout.write(f'{pval.tolist()}')
                sys.stdout.write(f'{right_brace}{trailing_comma}\n')
            else:
                # handle scalar parameter
                sys.stdout.write(f'    "{pname}": ')
                sys.stdout.write(f'{left_brace}"{year}": ')
                sys.stdout.write(f'{pval:.2f}')
                sys.stdout.write(f'{right_brace}{trailing_comma}\n')
    print('}')
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
