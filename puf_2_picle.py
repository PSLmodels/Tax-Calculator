import cPickle

# needed for modifying the CSV
import pandas as pd
import numpy as np


def pickle_puf(input_filename, output_filename, protocol=2):
    '''Given a name for input and output files, opens input (assumes it's CSV)
    file and pickles it using the protocol (can be optionally set to 0 or 1,
    see docs for cPickle) with the output file name.
    '''
    csv_dataframe = pd.read_csv(input_filename)
    # this code is specific to OSPC processing of the CSV
    narray_dict = {}
    for col_name in csv_dataframe.columns.values:
        new_col = col_name.upper() if col_name.isalpha() else col_name
        narray_dict[new_col] = np.array(csv_dataframe[col_name])

    with open(output_filename, 'w') as target:
        cPickle.dump(narray_dict, target, protocol)

def unpicle(f_name):
    '''Given a file name opens the file and uses cPickle to load it as a python
    object.
    '''
    with open(f_name) as y_file:
        return cPickle.load(y_file)
