"""
Turns csv output of tax calculator to ascii output with uniform columns
and transposes data so columns are rows, rows are columns

"""

import pandas as pd

def ascii_output(csv_results="", ascii_results=""):
    
    if csv_results == "":
        print("no csv file given!")
        exit(0)
    if ascii_results == "":
        print("no output file name given!")
        exit(0)

    #list of integers corresponding to the number(s) of the row(s) in the
    #csv file, only rows in list will be recorded in final output
    #if left as [], results in entire file being converted to ascii
    #put in order from smallest to largest, for example:
    #recids = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 107298, 108820]
    recids = [1,4,5]
    
    #Number of characters in each column, must be whole nonnegative integer
    col_size = 15
    
    df = pd.read_csv(csv_results, dtype=object)
    
    #keeps only listed recid's
    if recids != []:
        f = lambda x : x - 1
        recids = map(f, recids) #maps recids to correct index in df
        df = df.ix[recids]

    #does transposition
    out = df.T.reset_index()

    #formats data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)

    out.to_csv(ascii_results, header=False, index=False, delim_whitespace=True, sep='\t')
