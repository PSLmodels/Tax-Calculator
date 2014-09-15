import numpy as np
import pandas as pd

import cPickle
import re

import os


def check_accuracy(py_answer, gold_std):
    '''The older way of computing accuracy.
    Takes two dictionaries, py_answer with python script's output variables
    and gold_std with Dan's C-codes.
    '''
    acc_dict = {}
    for key in py_answer:
        if key in gold_std:
            print 'Found {} in gold standard'.format(key)
            test_length = float(len(py_answer[key]))
            gold_array = np.array(gold_std[key])
            print 'Array length is equal? {}'.format(len(gold_array) == test_length)
            n_correct = sum(py_answer[key] == gold_array)
            # n_correct = sum(np.in1d(py_answer[key], gold_array))
            acc_dict[key] = n_correct / test_length
    return acc_dict


def gen_file_paths(dir_name, filter_func=None):
    '''A function for wrapping all the os.path commands involved in listing files
    in a directory, then turning file names into file paths by concatenating
    them with the directory name.
    
    This also optionally supports filtering file names using filter_func.

    :param dir_name: name of directory to list files in
    :type dir_name: string
    :param filter_func: optional name of function to filter file names by
    :type filter_func: None by default, function if passed
    :returns: iterator over paths for files in *dir_name*
    '''
    file_paths = tuple(os.path.join(dir_name, file_name) 
        for file_name in os.listdir(dir_name))
    if filter_func:
        return filter(filter_func, file_paths)    
    return file_paths


def main(translation_output_dir, pickled_C_codes):
    '''Our current implementation of accuracy testing.

    NOTE: DUE TO MISSING DATA IN THE C-CODES FILE, THIS IMPLEMENTATION DOES NOT
    YET WORK.

    Takes name for folder containing output csvs from the python translation
    and file path to pickled C-codes (correct answers).
    Writes per variable comparison statistics to a csv, prints following info:
    - # of mismatches in length between variables
    - # of variables traversed
    - # of variables not found in C-codes file
    '''
    report_msg = ("# of mismatches in length: {0}\n"
        "total # variables processed: {1}\n"
        "couldn't find {2} variables in C-Codes file\n"
        "length of accuracy dict: {3}")

    simplifier = re.compile('\W')    
    array = np.array
    sum = np.sum
    # start by unpickling the c-codes file
    with open(pickled_C_codes) as c_code_file:
        c_codes = cPickle.load(c_code_file)
    # print c_codes.keys()
    different_lens = 0
    vars_processed, vars_not_found = 0, 0
    accuracies = {}
    # loop over csv files in output directory
    for var_file_path in gen_file_paths(translation_output_dir):
        var_df = pd.read_csv(var_file_path)
        for variable in var_df:
            vars_processed += 1
            variable_clean = simplifier.sub('', variable)
            # We check if a cleaned up version of var name is in c_codes file
            if variable_clean in c_codes:
                # only need to convert c_code column to array
                py_ansr = var_df[variable]
                # below line raises errors if c-codes variable only contains
                # empty strings. Will have to check with Dan about how
                # to deal with them. IK.
                gold_std = array(map(float, c_codes[variable_clean]))
                py_ansr_len = len(py_ansr)
                # compare arrays element-wise for equality, convert number of 
                # matches to float for subsequent division
                n_correct = float(sum(py_ansr == gold_std))

                different_lens += int(py_ansr_len == len(gold_std))                

                accuracies[variable] = n_correct / py_ansr_len
            else:
                # in case our var isn't in C-codes file
                vars_not_found += 1

    print report_msg.format(different_lens, vars_processed, 
        vars_not_found, len(accuracies))

    # clear C-Codes file
    c_codes = None
    # create a pandas DataFrame 
    accuracy_df = pd.DataFrame.from_dict(accuracies, orient='index')
    #write it to csv, creating column names
    accuracy_df.to_csv('accuracy.csv', colums=('VarName', 'RatioCorrect'))


if __name__ == '__main__':
    main('test/gold_csv', 'test/withc.pickle')

