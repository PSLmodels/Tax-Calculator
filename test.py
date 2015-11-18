"""
Test program for Calculator class logic that uses 'puf.csv' records and
writes results to the 'results_puf.csv' file.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 test.py
# pylint --disable=locally-disabled test.py

import pandas as pd
from taxcalc import Policy, Records, Calculator


def run():
    """
    Run each function defined in Calculator.calc_all_test method using
    'puf.csv' input and writing ouput to a CSV file named 'results_puf.csv'.
    """
    # create a Policy object containing current-law policy (clp) parameters
    clp = Policy()

    # create a Records object (puf) containing puf.csv input records
    tax_dta = pd.read_csv('puf.csv')
    blowup_factors = './taxcalc/StageIFactors.csv'
    weights = './taxcalc/WEIGHTS.csv'
    puf = Records(tax_dta, blowup_factors, weights)

    # create a Calculator object using clp policy and puf records
    calc = Calculator(policy=clp, records=puf)

    # save calculated test results in output dataframe (odf)
    odf = calc.calc_all_test()
    odf = odf.T.groupby(level=0).first().T

    # write test output to csv file named 'results_puf.csv'
    odf.to_csv('results_puf.csv', float_format='%1.3f',
               sep=',', header=True, index=False)


if __name__ == '__main__':
    run()
