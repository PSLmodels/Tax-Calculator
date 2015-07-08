"""
Turns csv output of tax calculator to ascii output with uniform columns
and transposes data so columns are rows, rows are columns

"""

import pandas as pd

def ascii_output():
    csv_results = "results_puf_ctrl_2008.csv" #input csv file
    ascii_results = "test_ascii.txt"

    #list of integers corresponding to the number(s) of the row(s) in the
    #csv file, only rows in list will be recorded in final output
    #if left as [], results in entire file being converted to ascii
    #put in order from smallest to largest
    recids = [0]
    #recids = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 107298, 108820]

    #Number of characters in each column, must be whole nonnegative integer
    col_size = 15
    
    df = pd.read_csv(csv_results)
    
    #keeps only listed recid's
    if recids != []:
        df = df.ix[recids]

    #does transposition
    out = df.T.reset_index()

    #formats data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)

    out.to_csv(ascii_results, header=False, index=False, delim_whitespace=True, sep='\t')
    
ascii_output()