"""
Python script that compares federal individual income and payroll tax
reform results produced by Tax-Calculator in two ways:
(1) via the TaxBrain website running in the clould, and
(2) via the taxcalc package running on this computer.

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


MIN_START_YEAR = 2013
MAX_START_YEAR = 2017
NUM_YEARS = 10  # number of years for which results are calculated


def main():
    """
    .................
    """
    # read reforms.json file and convert to a dictionary of reforms
    reforms_dict = read_reforms_json_file('reforms.json')

    # process each reform in reforms_dict
    for ref in sorted(reforms_dict):
        # reform_desc = reforms_dict[ref]['desc']
        start_year = reforms_dict[ref]['year']
        if start_year < MIN_START_YEAR or start_year > MAX_START_YEAR:
            msg = 'reform {} has start_year {} outside [{},{}] range'
            raise ValueError(msg.format(ref, start_year,
                                        MIN_START_YEAR, MAX_START_YEAR))
        reform_spec = reforms_dict[ref]['spec']
        reform_dict = Policy.convert_reform_dictionary(reform_spec)
        (itax_taxcalc,
         fica_taxcalc) = taxcalc_results(start_year, reform_dict)
        (itax_taxbrain,
         fica_taxbrain) = taxbrain_results(start_year, reform_spec)
        differences('ITAX', itax_taxcalc, itax_taxbrain)
        differences('FICA', fica_taxcalc, fica_taxbrain)
        break  # out of loop >> TEMP CODE <<

    # return no-error exit code
    return 0
# end of main function code


def read_reforms_json_file(filename):
    """
    Read specified filename; strip //-comments; and
    return dictionary of reforms if file contains valid JSON.
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


def taxcalc_results(start_year, reform_dict):
    """
    Use taxcalc package on this computer to compute aggregate income tax
    and payroll tax revenues for ten years beginning with the specified
    start_year using the specified reform_dict dictionary.
    Returns two aggregate revenue dictionaries indexed by calendar year.
    """
    pol = Policy()
    pol.implement_reform(reform_dict)
    calc = Calculator(policy=pol, records=Records(data=PUF_PATH))
    calc.advance_to_year(start_year)
    adt = calc.diagnostic_table(num_years=NUM_YEARS)  # adt is Pandas DataFrame
    return (adt.xs('Ind inc tax ($b)').to_dict(),
            adt.xs('Payroll tax ($b)').to_dict())


def taxbrain_results(start_year, reform_dict):
    """
    Use TaxBrain website running in the cloud to compute aggregate income tax
    and payroll tax revenues for ten years beginning with the specified
    start_year using the specified reform_spec dictionary.
    Returns two aggregate revenue dictionaries indexed by calendar year.
    """
    itax = {}
    fica = {}
    for year in range(start_year, start_year + NUM_YEARS):
        itax[year] = 0.0
        fica[year] = 0.0
    return (itax, fica)


def differences(taxkind, taxcalc, taxbrain):
    """
    Check for differences in the taxcalc and taxbrain dictionaries,
    which are for the kind of tax specified in the taxkind string.
    """
    first_year = min(taxcalc)
    last_year = max(taxcalc)
    for year in range(first_year, last_year + 1):
        diff = taxcalc[year] - taxbrain[year]
        print 'YR,{}_DIFF,_TAXCALC: {} {:.1f} {:.1f}'.format(taxkind,
                                                             year, diff,
                                                             taxcalc[year])


if __name__ == '__main__':
    sys.exit(main())
