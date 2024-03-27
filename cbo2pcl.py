"""
This script automates the incorporation of projected CBO tax parameters
into the Tax-Calculator/taxcalc/policy_current_law.json file.

The CBO tax parameter projection spreadsheet is a supplement to the
CBO report entitled "The Budget and Economic Outlook."
The most recent supplement is entitled:
CBO Tax Parameters and Effective Marginal Tax Rates | Feb 2024
and is available at this URL:
https://www.cbo.gov/system/files/2024-02/53724-2024-02-Tax-Parameters.xlsx

NOTE: whenever a new spreadsheet becomes available, it should be visually
inspected to see how the CBO_* structure data (see below) need to be updated.

USAGE: (taxcalc-dev) Tax-Calculator% python cbo2pcl.py --help

IMPORTANT USAGE NOTE: after updating growfactors.csv to new CBO projection,
first execute ppp.py script and commit the resulting policy_current_law.json,
then execute this cbo2pcl.py script and commit the resulting file.
BE SURE TO FOLLOW THIS ORDER OF SCRIPT EXECUTION.
"""

import os
import sys
import argparse
import shutil
import collections
import json
import pandas
import taxcalc


# Data on the expected CBO spreadsheet structure:
CBO_SHEET = 1  # the sheet called "1. Tax Parameters"
CBO_STR_COLS = [0, 1, 2, 3]  # expect columns A:D are strings; others numeric
CBO_YEAR = {
    'first': {'year': 2021, 'col': 'E'},
    'last':  {'year': 2034, 'col': 'R'},
}
# keys in CBO_ROWS are arbitrary names for parameter in the CBO spreadsheet
# NOTE: include a 'pct' key for CBO_ROWS that are expressed as a percent
#       (the 'pct' key can have any value)
CBO_ROWS = {
    'year': {'row': 8, 'label': 'Tax Year'},
    # income tax rates ...
    'trate1': {'row': 15, 'pct': '', 'label': 'First statutory rate'},
    'trate2': {'row': 16, 'pct': '', 'label': 'Second statutory rate'},
    'trate3': {'row': 17, 'pct': '', 'label': 'Third statutory rate'},
    'trate4': {'row': 18, 'pct': '', 'label': 'Fourth statutory rate'},
    'trate5': {'row': 19, 'pct': '', 'label': 'Fifth statutory rate'},
    'trate6': {'row': 20, 'pct': '', 'label': 'Sixth statutory rate'},
    'trate7': {'row': 21, 'pct': '', 'label': 'Seventh statutory rate'},
    # income tax brackets (top of bracket amount) ...
    'tbrk1_sng': {'row': 26, 'label': 'Second rate begins'},
    'tbrk1_jnt': {'row': 35, 'label': 'Second rate begins'},
    'tbrk1_hoh': {'row': 44, 'label': 'Second rate begins'},
    'tbrk1_sep': {'row': 53, 'label': 'Second rate begins'},
    'tbrk2_sng': {'row': 27, 'label': 'Third rate begins'},
    'tbrk2_jnt': {'row': 36, 'label': 'Third rate begins'},
    'tbrk2_hoh': {'row': 45, 'label': 'Third rate begins'},
    'tbrk2_sep': {'row': 54, 'label': 'Third rate begins'},
    'tbrk3_sng': {'row': 28, 'label': 'Fourth rate begins'},
    'tbrk3_jnt': {'row': 37, 'label': 'Fourth rate begins'},
    'tbrk3_hoh': {'row': 46, 'label': 'Fourth rate begins'},
    'tbrk3_sep': {'row': 55, 'label': 'Fourth rate begins'},
    'tbrk4_sng': {'row': 29, 'label': 'Fifth rate begins'},
    'tbrk4_jnt': {'row': 38, 'label': 'Fifth rate begins'},
    'tbrk4_hoh': {'row': 47, 'label': 'Fifth rate begins'},
    'tbrk4_sep': {'row': 56, 'label': 'Fifth rate begins'},
    'tbrk5_sng': {'row': 30, 'label': 'Sixth rate begins'},
    'tbrk5_jnt': {'row': 39, 'label': 'Sixth rate begins'},
    'tbrk5_hoh': {'row': 48, 'label': 'Sixth rate begins'},
    'tbrk5_sep': {'row': 57, 'label': 'Sixth rate begins'},
    'tbrk6_sng': {'row': 31, 'label': 'Seventh rate begins'},
    'tbrk6_jnt': {'row': 40, 'label': 'Seventh rate begins'},
    'tbrk6_hoh': {'row': 49, 'label': 'Seventh rate begins'},
    'tbrk6_sep': {'row': 58, 'label': 'Seventh rate begins'},
    # personal exemption ...
    'pe_amt': {'row': 63, 'label': 'Personal exemption'},
    'pe_ps_sng': {'row': 83, 'label': 'Single filer'},
    'pe_ps_jnt': {'row': 84, 'label': 'Married filing jointly'},
    'pe_ps_hoh': {'row': 85, 'label': 'Head of household'},
    'pe_ps_sep': {'row': 86, 'label': 'Married filing separately'},
    # deduction ...
    'stded_base_sng': {'row': 66, 'label': 'Single filer'},
    'stded_base_jnt': {'row': 67, 'label': 'Married filing jointly'},
    'stded_base_hoh': {'row': 68, 'label': 'Head of household'},
    'stded_base_sep': {'row': 69, 'label': 'Married filing separately'},
    'stded_aged_sng': {'row': 73, 'label': 'Single or head of household'},
    'stded_aged_jnt': {'row': 74, 'label': 'Married filing jointly or'},
    'itded_ps_sng': {'row': 77, 'label': 'Single filer'},
    'itded_ps_jnt': {'row': 78, 'label': 'Married filing jointly'},
    'itded_ps_hoh': {'row': 79, 'label': 'Head of household'},
    'itded_ps_sep': {'row': 80, 'label': 'Married filing separately'},
    # alternative minimum tax ...
    'amt_bracket': {'row': 95, 'label': 'Single filer'},
    'amt_em_sng': {'row': 101, 'label': 'Single Filer'},
    'amt_em_jnt': {'row': 102, 'label': 'Married filing jointly'},
    'amt_em_hoh': {'row': 103, 'label': 'Head of household'},
    'amt_em_sep': {'row': 104, 'label': 'Married filing Separately'},
    'amt_em_ps_sng': {'row': 107, 'label': 'Single Filer'},
    'amt_em_ps_jnt': {'row': 108, 'label': 'Married filing jointly'},
    'amt_em_ps_hoh': {'row': 109, 'label': 'Head of household'},
    'amt_em_ps_sep': {'row': 110, 'label': 'Married filing Separately'},
    # EITC ...
    'eitc_max_0': {'row': 127, 'label': 'Maximum credit amount'},
    'eitc_max_1': {'row': 135, 'label': 'Maximum credit amount'},
    'eitc_max_2': {'row': 143, 'label': 'Maximum Credit Amount'},
    'eitc_max_3': {'row': 151, 'label': 'Maximum credit amount'},
    'eitc_ps_s0': {'row': 125, 'label': 'Beginning of phaseout (single'},
    'eitc_ps_s1': {'row': 133, 'label': 'Beginning of phaseout (single'},
    'eitc_ps_s2': {'row': 141, 'label': 'Beginning of phaseout (single'},
    'eitc_ps_s3': {'row': 149, 'label': 'Beginning of phaseout (single'},
    'eitc_ps_m0': {'row': 126, 'label': 'Beginning of phaseout (married'},
    'eitc_ps_m1': {'row': 134, 'label': 'Beginning of phaseout (married'},
    'eitc_ps_m2': {'row': 142, 'label': 'Beginning of phaseout (married'},
    'eitc_ps_m3': {'row': 150, 'label': 'Beginning of phaseout (married'},
}


# Map Tax-Calculator parameter names to CBO_ROWS keys (i.e., names):
# NOTE that Tax-Calculator parameters are either vectors or scalars:
#  - a vector parameter has a parameter index variable (pivar) that
#    ranges over the parameter index variable's values (pivals)
#  - a scalar parameter has no parameter index variable
PARAM_MAP = {
    # income tax rates:
    'II_rt1': {
        'pivar': None,
        'cbo': 'trate1',
    },
    'II_rt2': {
        'pivar': None,
        'cbo': 'trate2',
    },
    'II_rt3': {
        'pivar': None,
        'cbo': 'trate3',
    },
    'II_rt4': {
        'pivar': None,
        'cbo': 'trate4',
    },
    'II_rt5': {
        'pivar': None,
        'cbo': 'trate5',
    },
    'II_rt6': {
        'pivar': None,
        'cbo': 'trate6',
    },
    'II_rt7': {
        'pivar': None,
        'cbo': 'trate7',
    },
    'PT_rt1': {
        'pivar': None,
        'cbo': 'trate1',
    },
    'PT_rt2': {
        'pivar': None,
        'cbo': 'trate2',
    },
    'PT_rt3': {
        'pivar': None,
        'pct': '',
        'cbo': 'trate3',
    },
    'PT_rt4': {
        'pivar': None,
        'cbo': 'trate4',
    },
    'PT_rt5': {
        'pivar': None,
        'cbo': 'trate5',
    },
    'PT_rt6': {
        'pivar': None,
        'cbo': 'trate6',
    },
    'PT_rt7': {
        'pivar': None,
        'cbo': 'trate7',
    },
    # income tax brackets (top of bracket amount):
    'II_brk1': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk1_sng',
            'mjoint':    'tbrk1_jnt',
            'mseparate': 'tbrk1_sep',
            'headhh':    'tbrk1_hoh',
            'widow':     'tbrk1_jnt',
        },
    },
    'II_brk2': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk2_sng',
            'mjoint':    'tbrk2_jnt',
            'mseparate': 'tbrk2_sep',
            'headhh':    'tbrk2_hoh',
            'widow':     'tbrk2_jnt',
        },
    },
    'II_brk3': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk3_sng',
            'mjoint':    'tbrk3_jnt',
            'mseparate': 'tbrk3_sep',
            'headhh':    'tbrk3_hoh',
            'widow':     'tbrk3_jnt',
        },
    },
    'II_brk4': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk4_sng',
            'mjoint':    'tbrk4_jnt',
            'mseparate': 'tbrk4_sep',
            'headhh':    'tbrk4_hoh',
            'widow':     'tbrk4_jnt',
        },
    },
    'II_brk5': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk5_sng',
            'mjoint':    'tbrk5_jnt',
            'mseparate': 'tbrk5_sep',
            'headhh':    'tbrk5_hoh',
            'widow':     'tbrk5_jnt',
        },
    },
    'II_brk6': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk6_sng',
            'mjoint':    'tbrk6_jnt',
            'mseparate': 'tbrk6_sep',
            'headhh':    'tbrk6_hoh',
            'widow':     'tbrk6_jnt',
        },
    },
    # top of seventh tax bracket is infinity
    'PT_brk1': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk1_sng',
            'mjoint':    'tbrk1_jnt',
            'mseparate': 'tbrk1_sep',
            'headhh':    'tbrk1_hoh',
            'widow':     'tbrk1_jnt',
        },
    },
    'PT_brk2': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk2_sng',
            'mjoint':    'tbrk2_jnt',
            'mseparate': 'tbrk2_sep',
            'headhh':    'tbrk2_hoh',
            'widow':     'tbrk2_jnt',
        },
    },
    'PT_brk3': {
        'pivar': 'MARS',
        'pct': '',
        'cbo': {
            'single':    'tbrk3_sng',
            'mjoint':    'tbrk3_jnt',
            'mseparate': 'tbrk3_sep',
            'headhh':    'tbrk3_hoh',
            'widow':     'tbrk3_jnt',
        },
    },
    'PT_brk4': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk4_sng',
            'mjoint':    'tbrk4_jnt',
            'mseparate': 'tbrk4_sep',
            'headhh':    'tbrk4_hoh',
            'widow':     'tbrk4_jnt',
        },
    },
    'PT_brk5': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk5_sng',
            'mjoint':    'tbrk5_jnt',
            'mseparate': 'tbrk5_sep',
            'headhh':    'tbrk5_hoh',
            'widow':     'tbrk5_jnt',
        },
    },
    'PT_brk6': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'tbrk6_sng',
            'mjoint':    'tbrk6_jnt',
            'mseparate': 'tbrk6_sep',
            'headhh':    'tbrk6_hoh',
            'widow':     'tbrk6_jnt',
        },
    },
    # top of seventh tax bracket is infinity
    # personal exemption params:
    'II_em': {
        'pivar': None,
        'cbo': 'pe_amt',
    },
    'II_em_ps': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'pe_ps_sng',
            'mjoint':    'pe_ps_jnt',
            'mseparate': 'pe_ps_sep',
            'headhh':    'pe_ps_hoh',
            'widow':     'pe_ps_jnt',
        },
    },
    # standard deduction params:
    'STD': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'stded_base_sng',
            'mjoint':    'stded_base_jnt',
            'mseparate': 'stded_base_sep',
            'headhh':    'stded_base_hoh',
            'widow':     'stded_base_jnt',
        },
    },
    'STD_Aged': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'stded_aged_sng',
            'mjoint':    'stded_aged_jnt',
            'mseparate': 'stded_aged_jnt',
            'headhh':    'stded_aged_sng',
            'widow':     'stded_aged_jnt',
        },
    },
    # itemized deduction phaseout param:
    'ID_ps': {
        'skip_years': [2021, 2022, 2023, 2024, 2025],  # skip faulty CBO values
        'pivar': 'MARS',
        'cbo': {
            'single':    'itded_ps_sng',
            'mjoint':    'itded_ps_jnt',
            'mseparate': 'itded_ps_sep',
            'headhh':    'itded_ps_hoh',
            'widow':     'itded_ps_jnt',
        },
    },
    # alternative minimum tax params:
    'AMT_brk1': {
        'pivar': None,
        'cbo': 'amt_bracket',
    },
    'AMT_em': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'amt_em_sng',
            'mjoint':    'amt_em_jnt',
            'mseparate': 'amt_em_sep',
            'headhh':    'amt_em_hoh',
            'widow':     'amt_em_jnt',
        },
    },
    'AMT_em_ps': {
        'pivar': 'MARS',
        'cbo': {
            'single':    'amt_em_ps_sng',
            'mjoint':    'amt_em_ps_jnt',
            'mseparate': 'amt_em_ps_sep',
            'headhh':    'amt_em_ps_hoh',
            'widow':     'amt_em_ps_jnt',
        },
    },
    # EITC params:
    'EITC_c': {
        'pivar': 'EIC',
        'cbo': {
            '0kids':  'eitc_max_0',
            '1kid':   'eitc_max_1',
            '2kids':  'eitc_max_2',
            '3+kids': 'eitc_max_3',
        },
    },
    'EITC_ps': {
        'pivar': 'EIC',
        'cbo': {
            '0kids':  'eitc_ps_s0',
            '1kid':   'eitc_ps_s1',
            '2kids':  'eitc_ps_s2',
            '3+kids': 'eitc_ps_s3',
        },
    },
    'EITC_ps_MarriedJ': {
        'pivar': 'EIC',
        'cbo': {
            '0kids':  'eitc_ps_m0-eitc_ps_s0',
            '1kid':   'eitc_ps_m1-eitc_ps_s1',
            '2kids':  'eitc_ps_m2-eitc_ps_s2',
            '3+kids': 'eitc_ps_m3-eitc_ps_s3',
        },
    },
}
PCLFILENAME = './taxcalc/policy_current_law.json'


def rindex(row_number):
    """
    Convert spreadsheet row number (1-based) to DataFrame row index (0-based).
    """
    return row_number - 1


def cindex(capital_letter):
    """
    Convert spreadsheet column letter to DataFrame column index (0-based).
    """
    return ord(capital_letter) - ord('A')


def cbo_value(cbodf, name, year):
    """
    Return value in specified year of CBO parameter with specified name;
    return None if there are any problems.
    """
    # check argument values
    args_ok = True
    if name not in CBO_ROWS:
        msg = f'name {name} not in CBO_ROWS data structure'
        sys.stderr.write(f'CBO: {msg}\n')
        args_ok = False
    first_year = CBO_YEAR['first']['year']
    if year < first_year:
        msg = f'year {year} less than first year {first_year}'
        sys.stderr.write(f'CBO: {msg}\n')
        args_ok = False
    last_year = CBO_YEAR['last']['year']
    if year > last_year:
        msg = f'year {year} greater than last year {last_year}'
        sys.stderr.write(f'CBO: {msg}\n')
        args_ok = False
    if not args_ok:
        return None
    # translate name to row number
    row = CBO_ROWS[name]['row']
    # convert year to column letter
    ord_first_year = ord(CBO_YEAR['first']['col'])
    letter = chr(ord_first_year + year - first_year)
    # get cbo_value from cbodf
    val = cbodf.iat[rindex(row), cindex(letter)]
    if 'pct' in CBO_ROWS[name]:
        return round(0.01 * val, 6)
    return val


def cbo_reform(cbodf):
    """
    Return adjustment-style "reform" that contains CBO parameter values.
    """
    cboadj = collections.defaultdict(list)
    last_year = CBO_YEAR['last']['year']
    for year in range(CBO_YEAR['first']['year'], last_year+1):
        for pname, pdict in PARAM_MAP.items():
            if 'skip_years' in pdict and year in pdict['skip_years']:
                continue  # skip pname for year
            if pdict['pivar'] is None:
                # handle scalar parameter
                cname = pdict['cbo']
                cval = cbo_value(cbodf, cname, year)
                adict = {'year': year, 'value': cval}
                cboadj[pname].append(adict)
            else:
                # handle vector parameter
                ivar = pdict['pivar']
                for ival, cname in pdict['cbo'].items():
                    if '-' in cname:
                        # cname is a parameter formula using one minus sign
                        cnames = cname.split('-')
                        assert len(cnames) == 2, \
                            f'"{cname}" formula contains more than two terms'
                        cvala = cbo_value(cbodf, cnames[0], year)
                        cvalb = cbo_value(cbodf, cnames[1], year)
                        cval = cvala - cvalb
                    else:
                        # cname is a CBO parameter name
                        cval = cbo_value(cbodf, cname, year)
                    adict = {'year': year, f'{ivar}': f'{ival}', 'value': cval}
                    cboadj[pname].append(adict)
    return cboadj


def write_json_file(cboadj):
    """
    Write new JSON file named PCLFILENAME that incorporates CBO parameter
    values specified in the specified cboadj adjustment dictionary after
    making a backup copy of the PCLFILENAME file.
    """
    # use cboadj "reform" to adjust Policy object
    pol = taxcalc.Policy()
    pol.adjust(cboadj)
    pol.clear_state()
    spec = pol.specification(
        meta_data=False, serializable=True, use_state=False, _auto=False
    )
    # read existing JSON file into a dictionary
    with open(PCLFILENAME, 'r', encoding='utf-8') as pcl_old:
        pcl = json.load(pcl_old)
    # replace parameter values in the pcl dictionary with spec values
    for pname in spec:
        pcl[pname]['value'] = spec[pname]
    # make a backup copy of PCLFILENAME file
    shutil.copy(PCLFILENAME, f'{PCLFILENAME}.bak')
    # overwrite new JSON file
    with open(PCLFILENAME, 'w', encoding='utf-8') as pcl_new:
        json.dump(pcl, pcl_new, indent=4)


def check_cbo_year():
    """
    Check CBO_YEAR for consistency: return 0 if OK, else return 1.
    """
    ydiff = CBO_YEAR['last']['year'] - CBO_YEAR['first']['year']
    cdiff = cindex(CBO_YEAR['last']['col']) - cindex(CBO_YEAR['first']['col'])
    if ydiff != cdiff:
        msg = 'CBO_YEAR contents are inconsistent'
        sys.stderr.write(f'STRUCT: {msg}\n')
        return 1
    return 0


def read_cbo_label(cbolabel, row):
    """
    Return string label from cbodf row.
    """
    ridx = rindex(row)
    for col in CBO_STR_COLS:
        label = cbolabel[col][ridx]
        if label != 'nan':
            return label
    return None


def read_check_spreadsheet(fname):
    """
    Read spreadsheet in specified fname and check its contents against
    the expected structure specified in the CBO_* data structures above.
    Function returns a pd.DataFrame except when any check errors are found,
    in which case it return None.
    """
    # check CBO_YEAR consistency
    rcode = check_cbo_year()
    if rcode != 0:
        return None
    # read spreadsheet
    try:
        cbodf = pandas.read_excel(fname, CBO_SHEET, header=None, dtype=object)
    except:  # pylint: disable=bare-except
        msg = f'could not read sheet in {fname} into a DataFrame'
        sys.stderr.write(f'READ: {msg}\n')
        return None
    # extract string columns into cbolabel dictionary containing row lists
    cbolabel = {}
    for col in CBO_STR_COLS:
        cbolabel[col] = [str(obj) for obj in cbodf[col].tolist()]
    # check spreadsheet against CBO_ROWS
    for cname, cdict in CBO_ROWS.items():
        elabel = cdict['label']
        alabel = read_cbo_label(cbolabel, cdict['row'])
        if not alabel.startswith(elabel):
            msg = f'for {cname} expected label is {elabel} but found {alabel}'
            sys.stderr.write(f'READ: {msg}\n')
            return None
    return cbodf


def check_arguments(args):
    """
    Check validity of command-line arguments returning one if there
    are problems or zero if there are no problems.
    """
    rcode = 0
    fname = args.CBOFILENAME
    if len(fname) <= 0:
        msg = 'must specify CBOFILENAME command-line argument'
        sys.stderr.write(f'ERROR: {msg}\n')
        return 1
    if not fname.endswith('.xlsx'):
        msg = f'CBOFILENAME {fname} does not end with .xlsx'
        sys.stderr.write(f'ERROR: {msg}\n')
        rcode = 1
    if not os.path.exists(fname):
        msg = f'CBOFILENAME {fname} does not exist'
        sys.stderr.write(f'ERROR: {msg}\n')
        rcode = 1
    return rcode


def main():
    """
    High-level script logic.
    """
    # parse command-line arguments:
    usage_str = 'python cbo2pcl.py CBOFILENAME [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=(
            'Writes tax parameter values from CBOFILENAME '
            'spreadsheet to ./taxcalc/policy_current_law.json file '
            'after making a backup file.  IMPORTANT NOTE: always '
            'inspect a new CBO spreadsheet to see which CBO_* data '
            'structures at the top of this script need to be updated.')
    )
    parser.add_argument('CBOFILENAME', nargs='?',
                        help=('file name of CBO .xlsx spreadsheet.'),
                        default='')
    args = parser.parse_args()
    # check command-line arguments
    rcode = check_arguments(args)
    if rcode != 0:
        sys.stderr.write(f'USAGE: {usage_str}\n')
        return rcode
    # read and check structure of CBO tax parameters spreadsheet
    cbodf = read_check_spreadsheet(args.CBOFILENAME)
    if not isinstance(cbodf, pandas.DataFrame):
        sys.stderr.write('ERROR: CBO spreadsheet has unexpected structure\n')
        return 1
    # create taxcalc adjustment-style "reform" containing CBO parameter values
    cboadj = cbo_reform(cbodf)
    # overwrite PCLFILENAME file with new file containing CBO parameter values
    write_json_file(cboadj)
    return 0
# end main function code


if __name__ == '__main__':
    sys.exit(main())
