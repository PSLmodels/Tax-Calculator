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

    # check validity of each reform
    for ref in sorted(reforms_dict):
        check_reform_reps_and_years(ref, reforms_dict[ref])

    # compute taxcalc results for current-law policy
    (itax_taxcalc_clp, fica_taxcalc_clp) = taxcalc_clp_results()

    # check that selenium package and chromedriver program are available
    check_selenium_and_chromedriver()

    # create Chrome webdriver object
    driver = selenium.webdriver.Chrome(executable_path=CWD_PATH)

    # process each reform in reforms_dict
    for ref in sorted(reforms_dict):
        replications = reforms_dict[ref]['replications']
        syr = reforms_dict[ref]['start_year']
        refspec = reforms_dict[ref]['specification']
        refdict = Policy.convert_reform_dictionary(refspec)
        (itax_taxcalc,
         fica_taxcalc) = taxcalc_results(syr, refdict,
                                         itax_taxcalc_clp,
                                         fica_taxcalc_clp)
        for repl in range(replications):
            (itax_taxbrain,
             fica_taxbrain,
             taxbrain_output_url) = taxbrain_results(driver, syr, refspec)
            check_for_differences(ref, repl, 'ITAX', taxbrain_output_url,
                                  itax_taxbrain, itax_taxcalc)
            check_for_differences(ref, repl, 'FICA', taxbrain_output_url,
                                  fica_taxbrain, fica_taxcalc)
        break  # >>>>>>> TEMP CODE <<<<<<<<<

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


def check_reform_reps_and_years(reform_name, complete_reform_dict):
    """
    Check specified complete_reform_dict for reform with specified
    reform_name for valid year values and number of replications.
    Raises error if there are any illegal values; otherwise
    returns without doing anything or returning anything.
    """
    replications = complete_reform_dict['replications']
    start_year = complete_reform_dict['start_year']
    refspec = complete_reform_dict['specification']
    refdict = Policy.convert_reform_dictionary(refspec)
    if replications < 1 or replications > 1000:
        msg = 'reform {} has replications {} outside [1,1000] range'
        raise ValueError(msg.format(reform_name, replications))
    if start_year < MIN_START_YEAR or start_year > MAX_START_YEAR:
        msg = 'reform {} has start year {} outside [{},{}] range'
        raise ValueError(msg.format(reform_name, start_year,
                                    MIN_START_YEAR, MAX_START_YEAR))
    first_year = min(refdict)
    if first_year < start_year:
        msg = 'reform {} has first reform year {} before start year {}'
        raise ValueError(msg.format(reform_name, first_year, start_year))
    last_year = max(refdict)
    max_year = start_year + NUMBER_OF_YEARS
    if last_year > max_year:
        msg = 'reform {} has last reform year {} after last results year {}'
        raise ValueError(msg.format(reform_name, last_year, max_year))
    return


def taxcalc_clp_results():
    """
    Use taxcalc package on this computer to compute aggregate income tax
    and payroll tax revenues for years beginning with MIN_START_YEAR and
    ending with MAX_START_YEAR+NUMBER_OF_YEARS-1 for current-law policy.
    Returns two aggregate revenue dictionaries indexed by calendar year.
    """
    calc = Calculator(policy=Policy(), records=Records(data=PUF_PATH))
    nyrs = MAX_START_YEAR + NUMBER_OF_YEARS - MIN_START_YEAR
    adt = calc.diagnostic_table(num_years=nyrs)
    # note that adt is Pandas DataFrame object
    return (adt.xs('Ind inc tax ($b)').to_dict(),
            adt.xs('Payroll tax ($b)').to_dict())


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


def taxbrain_results(driver, start_year, reform_dict):
    """
    Use TaxBrain website running in the cloud to compute aggregate income tax
    and payroll tax revenue difference (between reform and current-law policy)
    for ten years beginning with the specified start_year using the specified
    reform_spec dictionary.
    Returns two aggregate revenue difference dictionaries indexed by calendar
    year and the URL of the complete TaxBrain results.
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
        itax[int(year)] = float(itaxd)
        fica[int(year)] = float(ficad)
    return (itax, fica, url)


def taxcalc_results(start_year, reform_dict, itax_clp, fica_clp):
    """
    Use taxcalc package on this computer to compute aggregate income tax and
    payroll tax revenue difference (between reform and current-law policy)
    for ten years beginning with the specified start_year using the specified
    reform_spec dictionary and the two specified current-law-policy results
    dictionaries.
    Returns two aggregate revenue difference dictionaries indexed by calendar
    year and the URL of the complete TaxBrain results.
    """
    pol = Policy()
    pol.implement_reform(reform_dict)
    calc = Calculator(policy=pol, records=Records(data=PUF_PATH))
    calc.advance_to_year(start_year)
    adt = calc.diagnostic_table(num_years=NUMBER_OF_YEARS)
    # note that adt is Pandas DataFrame object
    itax_ref = adt.xs('Ind inc tax ($b)').to_dict()
    fica_ref = adt.xs('Payroll tax ($b)').to_dict()
    itax_diff = {}
    fica_diff = {}
    for year in itax_ref:
        itax_diff[year] = round(itax_ref[year] - itax_clp[year], 1)
        fica_diff[year] = round(fica_ref[year] - fica_clp[year], 1)
    return (itax_diff, fica_diff)


def check_for_differences(ref, repl, taxkind, out_url, taxbrain, taxcalc):
    """
    Check for differences in the specified taxbrain and taxcalc dictionaries,
    which are for the kind of tax specified in the taxkind string and for the
    specified reform ref and replication repl with complete TaxBrain output
    in specified out_url.
    Writes to stdout only when absolute value of taxbrain-minus-taxcalc
    difference is greater than epsilon, with written information being
    reform, taxkind, year, taxbrain-minus-taxcalc difference, and the
    relative percentage difference measured by 100*abs(diff)/abs(taxcalc)
    """
    epsilon = 0.05
    for year in sorted(taxbrain):
        diff = taxbrain[year] - taxcalc[year]
        if abs(diff) > epsilon:
            if abs(taxcalc[year]) > 0.0:
                pctdiff = 100.0 * abs(diff) / abs(taxcalc[year])
            else:
                pctdiff = float('inf')
            template = '{}\t{}\t{}\t{:.1f}\t{:.2f}\t{}\n'
            rpr = ref + '-{:3d}'.format(repl)
            msg = template.format(rpr, taxkind, year, diff, pctdiff, out_url)
            sys.stdout.write(msg)


if __name__ == '__main__':
    sys.exit(main())
