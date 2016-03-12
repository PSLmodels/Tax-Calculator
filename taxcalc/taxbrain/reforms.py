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
CWD_PATH = os.path.join(CUR_PATH, '..', '..', 'chromedriver')
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import Policy, Records, Calculator  # pylint: disable=import-error
import re
import json
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pyperclip


MIN_START_YEAR = 2013
MAX_START_YEAR = 2017
NUMBER_OF_YEARS = 10  # number of years for which results are calculated


def main():
    """
    Highest-level logic of reforms.py script.
    """
    # read reforms.json file and convert to a dictionary of reforms
    reforms_dict = read_reforms_json_file('reforms.json')

    # check that selenium package and chromedriver program are available
    check_selenium_and_chromedriver()
    # create Chrome webdriver object
    driver = selenium.webdriver.Chrome(executable_path=CWD_PATH)

    # initial empty results dictionaries that contain reform-indexed
    # dictionaries of year-indexed aggregate tax revenue dictionaries
    # : TaxBrain results are differences between reform and current-law policy
    itax_taxbrain_diff = {}
    fica_taxbrain_diff = {}
    # : taxcalc results are levels under reform policy
    itax_taxcalc = {}
    fica_taxcalc = {}
    # : URL of complete TaxBrain output results
    taxbrain_output_url = {}

    # process each reform in reforms_dict
    for ref in sorted(reforms_dict):
        dsc = reforms_dict[ref]['description']
        syr = reforms_dict[ref]['start_year']
        refspec = reforms_dict[ref]['spec']
        refdict = Policy.convert_reform_dictionary(refspec)
        check_reform_years(ref, syr, refdict)
        (itax_taxbrain_diff[ref],
         fica_taxbrain_diff[ref],
         taxbrain_output_url[ref]) = taxbrain_results(driver, syr, refspec)
        (itax_taxcalc[ref],
         fica_taxcalc[ref]) = taxcalc_results(syr, refdict)
        break  # out of loop >>> TEMP CODE <<<

    # delete Chrome webdriver object
    driver.quit()

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


def check_selenium_and_chromedriver():
    """
    Check availability of selenium package and chromedriver program.
    Raises error if package or program not installed correctly;
    otherwise returns without doing anything or returning anything.
    """
    # check for selenium package
    try:
        import imp
        imp.find_module('selenium')
    except ImportError:
        msg = 'cannot find selenium package to import'
        raise ImportError(msg)
    # check for chromedriver program
    if not os.path.isfile(CWD_PATH):
        msg = 'cannot find chromedriver program at {}'.format(CWD_PATH)
        raise ValueError(msg)
    return


def check_reform_years(reform_name, start_year, reform_dict):
    """
    Check specified reform start_year and specified reform_dict (a
    dictionary with year as the primary key) for valid year values.
    Raises error if there are illegal year values; otherwise
    returns without doing anything or returning anything.
    """
    if start_year < MIN_START_YEAR or start_year > MAX_START_YEAR:
        msg = 'reform {} has start year {} outside [{},{}] range'
        raise ValueError(msg.format(reform_name, start_year,
                                    MIN_START_YEAR, MAX_START_YEAR))
    first_year = min(reform_dict)
    if first_year < start_year:
        msg = 'reform {} has first reform year {} before start year {}'
        raise ValueError(msg.format(reform_name, first_year, start_year))
    last_year = max(reform_dict)
    max_year = start_year + NUMBER_OF_YEARS
    if last_year > max_year:
        msg = 'reform {} has last reform year {} after last results year {}'
        raise ValueError(msg.format(reform_name, last_year, max_year))
    return


def taxbrain_results(driver, start_year, reform_dict):
    """
    Use TaxBrain website running in the cloud to compute aggregate income tax
    and payroll tax revenues for ten years beginning with the specified
    start_year using the specified reform_spec dictionary.
    Returns two aggregate revenue dictionaries indexed by calendar year and
    the URL of the complete TaxBrain results.
    """
    # browse TaxBrain input webpage for specified start_year
    url = 'http://www.ospc.org/taxbrain/?start_year={}'.format(start_year)
    driver.get(url)

    # insert reform parameters into fields on input webpage
    css = 'input#id_SS_Earnings_c.form-control'
    txt = '999999999'  # TODO: derive txt from reform_dict values
    driver.find_element_by_css_selector(css).send_keys(txt)

    # click on "Show me the results!" button to start tax calculations
    css = 'input#tax-submit.btn.btn-secondary.btn-block.btn-animate'
    driver.find_element_by_css_selector(css).click()

    # wait for TaxBrain output webpage to appear
    css = 'div.flatblock.block-taxbrain_results_header'
    wait_secs = 120  # time to wait before triggering wait error
    wait_error_msg = 'No TaxBrain results after {} seconds'.format(wait_secs)
    WebDriverWait(driver, wait_secs).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css)), wait_error_msg)

    # copy "TOTAL LIABILITIES CHANGE BY CALENDAR YEAR" table to clipboard
    css = 'a.btn.btn-default.buttons-copy.buttons-html5'
    driver.find_element_by_css_selector(css).click()
    sleep(1)  # wait for a second for the copy to clipboard to finish

    # return extracted contents of clipboard
    return taxbrain_output_table_extract(pyperclip.paste())


def taxbrain_output_table_extract(table):
    """
    Extract from specified "TOTAL LIABILITIES CHANGE BY CALENDAR YEAR" table
    reform-vs-current-law-policy differences in itax and fica aggregate
    revenue by calendar year, which are returned as dictionaries.
    Also, extract the URL of the complete TaxBrain results and return.
    """
    tlines = table.split('\n')
    tyears = tlines[0].split()
    titaxd = (tlines[2].split())[5:]
    tficad = (tlines[3].split())[4:]
    url = (tlines[5].split())[1:]
    itax = {}
    fica = {}
    for year, itaxd, ficad in zip(tyears, titaxd, tficad):
        itax[year] = float(itaxd)
        fica[year] = float(ficad)
    return (itax, fica, url)


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
    adt = calc.diagnostic_table(num_years=NUMBER_OF_YEARS)
    # note that adt is Pandas DataFrame object
    return (adt.xs('Ind inc tax ($b)').to_dict(),
            adt.xs('Payroll tax ($b)').to_dict())


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
