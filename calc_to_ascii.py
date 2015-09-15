import pandas as pd


def calc_to_ascii(calc, ascii_results=""):
    '''
    Takes in calc object to print relevant records into ascii form
    '''

    if ascii_results == "":
        print("no output file name given!")
        exit(0)

    # list of integers corresponding to the number(s) of the row(s) in the
    # csv file, only rows in list will be recorded in final output
    # if left as [], results in entire file being converted to ascii
    # put in order from smallest to largest, for example:
    # recids = [33180, 64023, 68020, 74700, 84723, 98001, 107039, 107298, 
    #           108820]
    recids = [1, 4, 5]
    
    # Number of characters in each column, must be whole nonnegative integer
    col_size = 15

    # creates empty dataframe
    df = pd.DataFrame()
    # gets dimensions of attributes that can be converted into a dataframe
    rshape = calc.records.e00100.shape

    for attr in dir(calc.records):
        value = getattr(calc.records, attr)
        if hasattr(value, "shape"):
            if (value.shape == rshape):
                df[attr] = value

    # keeps only listed recid's
    if recids != []:

        def f(x):
            return x - 1
        recids = map(f, recids)  # maps recids to correct index in df
        df = df.ix[recids]

    # does transposition
    out = df.T.reset_index()

    # formats data into uniform columns
    fstring = '{:' + str(col_size) + '}'
    out = out.applymap(fstring.format)

    out.to_csv(ascii_results, header=False, index=False,
               delim_whitespace=True, sep='\t')

