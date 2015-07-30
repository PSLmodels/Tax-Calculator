""" Test program for Calculator class logic that uses 'puf.csv' records and
writes results to the 'results_puf.csv' file.

PYLINT USAGE: pylint test.py
"""
import pandas as pd
from taxcalc.parameters import Parameters
from taxcalc.records import Records
from taxcalc.calculate import Calculator


def run():
    """ Run each function defined in Calculator.calc_all_test method using
    'puf.csv' input and writing ouput to a CSV file named 'results_puf.csv'.
    """
    # create a Parameters object containing current-law policy (clp) parameters
    clp = Parameters()

    # create a Records object (puf) containing puf.csv input records
    tax_dta = pd.read_csv('puf.csv')
    blowup_factors = './taxcalc/StageIFactors.csv'
    weights = './taxcalc/WEIGHTS.csv'
    puf = Records(tax_dta, blowup_factors, weights)

    # create a Calculator object using clp params and puf records
    calc = Calculator(params=clp, records=puf)

    # save calculated test results in output dataframe (odf)
    odf = calc.calc_all_test()
    odf = odf.T.groupby(level=0).first().T

    # write test output to csv file named 'results_puf.csv'
    odf.to_csv('results_puf.csv', float_format='%1.3f',
               sep=',', header=True, index=False)


if __name__ == '__main__':
    run()
