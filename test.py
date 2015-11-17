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
    # create a Policy object containing current-law policy parameters
    policy = Policy()

    # create a Records object containing puf.csv input records
    recs = Records()

    # create a Calculator object using policy and recs objects
    calc = Calculator(policy=policy, records=recs)

    # save calculated test results in output dataframe (odf)
    odf = calc.calc_all_test()
    odf = odf.T.groupby(level=0).first().T

    # write test output to csv file named 'results_puf.csv'
    odf.to_csv('results_puf.csv', float_format='%1.3f',
               sep=',', header=True, index=False)


if __name__ == '__main__':
    run()
