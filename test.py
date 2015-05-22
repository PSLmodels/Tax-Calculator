"""
Testing file for calculate.py
"""

from pandas import DataFrame, concat
from taxcalc.calculate import *
from taxcalc.records import *
from taxcalc.parameters import *
import taxcalc.parameters as parameters
#from timer.timed_calculate import *


def to_csv(fname, df):
    """
    Save this dataframe to a CSV file with name 'fname' and containing
    a header with the column names of the dataframe.
    """
    df.to_csv(fname, float_format= '%1.3f', sep=',', header=True, index=False)



def run(puf=True):
    """
    Run each function defined in calculate.py, saving the ouput to a CSV file.
    'puf' set to True by default, to use the 'puf2.csv' as an input
    
    For functions returning an additional non-global variable in addition
    to the DataFrame to be printed, one line saves the dataFrame to be printed 
    first, and then saves the variable to be used by a following function second. 
    """

    # Create a Parameters object
    params = Parameters()

    # Create a Public Use File object

    tax_dta = pd.read_csv("/Users/Amy/Documents/puf.csv")

    blowup_factors = "./taxcalc/StageIFactors.csv"
    weights = "./taxcalc/WEIGHTS.csv"

    puf = Records(tax_dta, blowup_factors, weights)

    # Create a Calculator
    calc = Calculator(parameters=params, records=puf)
    #calc.records.e18400 = calc.records.e18400 - calc.records.e18400
    #calc.records.e18425 = calc.records.e18425 - calc.records.e18425
    #calc.records.e18450 = calc.records.e18450 - calc.records.e18450
    #calc.records.e18500 = calc.records.e18500 - calc.records.e18500
    #calc.records.e18800 = calc.records.e18800 - calc.records.e18800
    #calc.records.e18900 = calc.records.e18900 - calc.records.e18900
    totaldf = calc.calc_all_test()

    # drop duplicates
    totaldf = totaldf.T.groupby(level=0).first().T

    to_csv("results_puf.csv", totaldf)

if __name__ == '__main__':
    run()
