"""
Python script that compares federal individual income and payroll tax
reform results produced by Tax-Calculator in two ways:
(1) via the TaxBrain webapp running in the cloud, and
(2) via the taxcalc package running on this computer.

COMMAND-LINE USAGE: python reforms.py

Note that this script is intended for the use of core development team;
it is not useful for conducting any kind of tax policy analysis.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 reforms.py
# pylint --disable=locally-disabled reforms.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)

import argparse
import os
import sys
import re
import json
from time import sleep
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
PUF_PATH = os.path.join(CUR_PATH, '..', '..', 'puf.csv')
CWD_PATH = os.path.join(CUR_PATH, '..', '..', 'chromedriver')
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pyperclip
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator


MIN_START_YEAR = 2013
MAX_START_YEAR = 2017
NUMBER_OF_YEARS = 10  # number of years for which results are calculated

TRACING = False  # set to true to write name of each parameter processed


def main(reforms_json_filename):
    """
    Highest-level logic of reforms.py script.
    """
    # read specified reforms file and convert to a dictionary of reforms
    reforms_dict = read_reforms_json_file(reforms_json_filename)

    # check validity of each reform
    for ref in sorted(reforms_dict):
        check_complete_reform_dict(ref, reforms_dict[ref])

    # compute taxcalc results for current-law policy
    (itax_taxcalc_clp, fica_taxcalc_clp) = taxcalc_clp_results()

    # check that selenium package and chromedriver program are available
    check_selenium_and_chromedriver()

    # process each reform in reforms_dict
    for ref in sorted(reforms_dict):
        syr = reforms_dict[ref]['start_year']
        refspec = reforms_dict[ref]['specification']
        refdict = Policy.convert_reform_dictionary(refspec)
        (itax_taxcalc,
         fica_taxcalc) = taxcalc_results(syr, refdict,
                                         itax_taxcalc_clp,
                                         fica_taxcalc_clp)
        for repl in range(reforms_dict[ref]['replications']):
            ref_repl = '{}-{:03d}'.format(ref, repl)
            (itax_taxbrain,
             fica_taxbrain,
             taxbrain_output_url) = taxbrain_results(ref_repl, syr, refspec)
            if len(taxbrain_output_url) == 0:  # no TaxBrain output
                continue  # to top of replication loop
            check_for_differences(ref_repl, 'ITAX', taxbrain_output_url,
                                  itax_taxbrain, itax_taxcalc)
            check_for_differences(ref_repl, 'FICA', taxbrain_output_url,
                                  fica_taxbrain, fica_taxcalc)

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
        msg = '{} file contains invalid JSON'.format(filename)
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


def check_complete_reform_dict(reform_name, complete_reform_dict):
    """
    Check specified complete_reform_dict for reform with specified
    reform_name for valid year values and for valid number of replications.
    Raise error if there are any illegal values; otherwise
    return without doing anything or returning anything.
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
    Return two aggregate revenue dictionaries indexed by calendar year.
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
    Raise error if package or program not installed correctly;
    otherwise return without doing anything or returning anything.
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


def taxbrain_results(ref_repl, start_year, reform_spec):
    """
    Use TaxBrain webapp running in the cloud to compute aggregate income tax
    and payroll tax revenue difference (between reform and current-law policy)
    for ten years beginning with the specified start_year using the specified
    reform_spec dictionary for the reform with the specified ref_repl name.
    Return two aggregate revenue difference dictionaries indexed by calendar
    year and the URL of the complete TaxBrain results.
    """
    # create Chrome webdriver object
    driver = selenium.webdriver.Chrome(executable_path=CWD_PATH)

    # browse TaxBrain input webpage for specified start_year
    url = 'http://www.ospc.org/taxbrain/?start_year={}'.format(start_year)
    driver.get(url)

    # make TaxBrain input webpage bigger so that all elements are visible
    driver.maximize_window()

    # insert reform parameters into fields on input webpage
    taxbrain_param_values_insert(driver, start_year, reform_spec)

    # click on "Show me the results!" button to start tax calculations
    css = 'input#tax-submit.btn.btn-secondary.btn-block.btn-animate'
    driver.find_element_by_css_selector(css).click()

    # wait for TaxBrain input error message
    css = 'div.alert.alert-danger.text-center.lert-dismissible'
    wait_secs = 10  # time to wait for an input error message
    try:
        WebDriverWait(driver, wait_secs).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        msg = '{}\tTaxBrain-input-error\n'.format(ref_repl)
        sys.stdout.write(msg)
        sys.stdout.flush()
        return ({}, {}, '')
    except TimeoutException:
        pass

    # wait for TaxBrain output webpage to appear
    css = 'div.flatblock.block-taxbrain_results_header'
    wait_secs = 100  # time to wait before triggering wait error
    try:
        WebDriverWait(driver, wait_secs).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    except TimeoutException:
        template = '{}\tTaxBrain-timeout-after-{}-seconds\n'
        msg = template.format(ref_repl, wait_secs)
        sys.stdout.write(msg)
        sys.stdout.flush()
        return ({}, {}, '')

    # copy "TOTAL LIABILITIES CHANGE BY CALENDAR YEAR" table to clipboard
    css = 'a.btn.btn-default.buttons-copy.buttons-html5'
    driver.find_element_by_css_selector(css).click()
    sleep(1)  # wait for a second for the copy to clipboard to finish

    # extract tax revenue difference dictionaries from clipboard contents
    dicts = taxbrain_output_table_extract(pyperclip.paste())

    # clear the clipboard
    pyperclip.copy('')

    # delete Chrome webdriver object
    driver.quit()

    # return dictionaries extracted from "TOTAL LIABILITIES CHANGE" table
    return dicts


def taxbrain_param_values_insert(driver, start_year, reform_spec):
    """
    Insert policy parameter values into TaxBrain input webpage using
    specified reform_spec dictionary, which has parameter-name string keys
    and dictionary values, where each parameter dictionary contains one
    or more year:value pairs, and the specified start_year.
    Function returns nothing.
    """
    for param in reform_spec:
        if TRACING:
            sys.stdout.write('==> PARAM {}\n'.format(param))
            sys.stdout.flush()
        param_dict = reform_spec[param]
        pval = param_dict[(param_dict.keys())[0]]
        if isinstance(pval[0], list):  # [0] removes the outer brackets
            taxbrain_vector_pval_insert(driver, start_year, param, param_dict)
        else:
            taxbrain_scalar_pval_insert(driver, start_year, param, param_dict)
    return


def taxbrain_scalar_pval_insert(driver, start_year, param_name, param_dict):
    """
    Insert scalar policy parameter values into TaxBrain input webpage.
    Function returns nothing.
    """
    pyrs = sorted(param_dict.keys())
    # handle first pyr in pyrs list of year strings
    pyr = pyrs[0]
    pval = param_dict[pyr][0]  # [0] removes the outer brackets
    pyr = int(pyr)
    if pyr == start_year:
        txt = '{}'.format(pval)
    else:  # pyr > start_year
        txt = '*'
        for _ in range(pyr - start_year + 1):
            txt += ',*'
        txt += ',{}'.format(pval)
    prior_pyr = pyr
    # handle subsequent pyr in pyrs list
    for pyr in pyrs[1:]:
        pval = param_dict[pyr][0]  # [0] removes the outer brackets
        pyr = int(pyr)
        for _ in range(pyr - prior_pyr - 1):
            txt += ',*'
        txt += ',{}'.format(pval)
        prior_pyr = pyr
    # insert txt into parameter field
    css = 'input#id{}.form-control'.format(param_name)
    try:
        field = WebDriverWait(driver, 2, 0.1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        field.send_keys(txt + Keys.TAB)
    except TimeoutException:
        msg = 'no TaxBrain parameter named {}'.format(param_name)
        raise ValueError(msg)
    return


def taxbrain_vector_pval_insert(driver, start_year, param_name, param_dict):
    """
    Insert vector policy parameter values into TaxBrain input webpage.
    Function returns nothing.
    """
    if param_name == '_BenefitSurtax_Switch':
        vector_length = 7
    else:
        vector_length = 4
    pyrs = sorted(param_dict.keys())
    for idx in range(vector_length):
        # handle first pyr in pyrs list of year strings
        pyr = pyrs[0]
        pval = param_dict[pyr][0]  # [0] removes the outer brackets
        pyr = int(pyr)
        if pyr == start_year:
            txt = '{}'.format(pval[idx])
        else:  # pyr > start_year
            txt = '*'
            for _ in range(pyr - start_year + 1):
                txt += ',*'
            txt += ',{}'.format(pval[idx])
        prior_pyr = pyr
        # handle subsequent pyr in pyrs list
        for pyr in pyrs[1:]:
            pval = param_dict[pyr][0]  # [0] removes the outer brackets
            pyr = int(pyr)
            for _ in range(pyr - prior_pyr - 1):
                txt += ',*'
            txt += ',{}'.format(pval[idx])
            prior_pyr = pyr
        # insert txt into parameter field
        css = 'input#id{}_{}.form-control'.format(param_name, idx)
        try:
            field = WebDriverWait(driver, 2, 0.1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css)))
            field.send_keys(txt + Keys.TAB)
        except TimeoutException:
            msg = 'no TaxBrain parameter named {}_{}'.format(param_name, idx)
            raise ValueError(msg)
    return


def taxbrain_output_table_extract(table):
    """
    Extract from specified "TOTAL LIABILITIES CHANGE BY CALENDAR YEAR" table
    reform-vs-current-law-policy differences in itax and fica aggregate
    revenue by calendar year, which are returned as dictionaries.
    Also, extract the URL of the complete TaxBrain results and return it.
    """
    tlines = table.split('\n')
    tyears = tlines[0].split()
    titaxd = (tlines[2].split())[5:]
    tficad = (tlines[3].split())[4:]
    url_list = (tlines[5].split())[1:]
    url = (url_list[0])[7:]
    itax = {}
    fica = {}
    for year, itaxd, ficad in zip(tyears, titaxd, tficad):
        itax[int(year)] = float(re.sub(',', '', itaxd))
        fica[int(year)] = float(re.sub(',', '', ficad))
    return (itax, fica, url)


def taxcalc_results(start_year, reform_dict, itax_clp, fica_clp):
    """
    Use taxcalc package on this computer to compute aggregate income tax and
    payroll tax revenue difference (between reform and current-law policy)
    for ten years beginning with the specified start_year using the specified
    reform_dict dictionary and the two specified current-law-policy results
    dictionaries.
    Return two aggregate tax revenue difference dictionaries indexed by
    calendar year.
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


def check_for_differences(ref_repl, taxkind, out_url, taxbrain, taxcalc):
    """
    Check for differences in the specified taxbrain and taxcalc dictionaries,
    which are for the kind of tax specified in the taxkind string and for the
    specified reform-replication with complete TaxBrain output in specified
    out_url.
    Write to stdout only when absolute value of taxbrain-minus-taxcalc
    difference is greater than epsilon, with written information being
    reform-replication, taxkind, year, taxbrain-minus-taxcalc difference,
    the relative percentage difference measured by 100*diff/abs(taxcalc),
    and the URL from which complete TaxBrain output results are available.
    Each line written to stdout is tab-delimited.
    """
    epsilon = 0.05  # one-half of one-tenth of a billion dollars
    for year in sorted(taxbrain):
        diff = taxbrain[year] - taxcalc[year]
        if abs(diff) > epsilon:
            if abs(taxcalc[year]) > 0.0:
                pctdiff = 100.0 * diff / abs(taxcalc[year])
            else:
                if diff > 0.0:
                    pctdiff = float('inf')
                else:
                    pctdiff = -float('inf')
            template = '{}\t{}\t{}\t{:.1f}\t{:.2f}\t{}\n'
            msg = template.format(ref_repl, taxkind, year,
                                  diff, pctdiff, out_url)
            sys.stdout.write(msg)
            sys.stdout.flush()
    return


if __name__ == '__main__':
    # parse command-line arguments:
    PARSER = argparse.ArgumentParser(
        prog='python reforms.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=('Writes to stdout any differences in federal income '
                     'tax and payroll tax\nrevenue changes for a set of '
                     'policy reforms that are generated by\nTax-Calculator '
                     'in two ways:\n(a) via the TaxBrain webapp running '
                     'in the cloud, and\n(b) via the taxcalc package '
                     'running on this computer.\n'
                     'Each output line contains six tab-delimited fields:\n'
                     '(1) reform-replication\n'
                     '(2) tax type (ITAX or FICA)\n'
                     '(3) calendar year of difference\n'
                     '(4) difference amount in $billion (TaxBrain change '
                     'minus taxcalc change)\n'
                     '(5) percentage difference (relative to size of '
                     'taxcalc revenue change)\n'
                     '(6) URL of detailed TaxBrain output'))
    PARSER.add_argument('--filename',
                        help=('optional flag to specify name of file '
                              'containing\nJSON specification of policy '
                              'reforms;\nno flag implies '
                              'FILENAME is "reforms.json".'),
                        default='reforms.json')
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.filename))
