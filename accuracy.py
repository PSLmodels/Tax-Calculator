import numpy as np
import pandas as pd
import h5py as h5

import os
import os.path as op


_VARIABLES_OF_INTEREST = {
    'AGI.csv' : ['c00100'],
    'ItemDed.csv' : ['c04470']
}


def main(sas_codes_path, rerun=False):
    if rerun:
        import translation
        translation.Test(True)
    # for now output dir for translation has to be set up separately
    # TO-DO: automate this directory setup
    gold_std = h5.File(sas_codes_path)
    out_dir = 'py_output'
    errors = compute_error(gen_file_paths(out_dir), gold_std)
    errors.columns = ['Error']
    errors.sort(columns='Error', ascending=False, inplace=True)
    # errors = compute_error(_VARIABLES_OF_INTEREST, 'py_output', gold_std)
    errors.to_csv('error_values.csv', 
        # header=['Error'],
        index_label='Variable'
        )


def compute_error(to_look_at, gold_std):
    '''Computes the "error" by looking at a specified list of variables and
    reporting 
    '''
    error = {}
    for file_name in to_look_at:
        file_vars = pd.read_csv(file_name)
        # for var_name in to_look_at[file_name]:
        for var_name in file_vars:
            if var_name.lower().startswith('c') and var_name not in error:
                per_taxpayer_diff = file_vars[var_name] - gold_std[var_name]
                error[var_name] = np.absolute(per_taxpayer_diff).sum()

    return pd.DataFrame.from_dict(error, orient='index')


def mismatching_records(gold_std, variable, out_dir='py_output'):
    '''
    Given a gold standard dictionary, a variable name and a path to the file
    where this variable is stored returns an array of indices for taxpayer
    records where python's output does not match  that of SAS.
    '''
    py_answer = pd.Series()
    for file_path in gen_file_paths(out_dir):
        temp = pd.read_csv(file_path)
        if variable in temp:
            print file_path
            py_answer = temp[variable]
            break
    
    if len(py_answer) == 0:
        print 'Variable was not found, returning empty series!'
        return py_answer
    
    mismatches = np.array(np.absolute(py_answer - gold_std[variable]) > 0)

    if not mismatches.any():
        print 'No cells satisfied the condition, returning series as is'
        return mismatches

    # print mismatches[0], type(mismatches)
    all_indices = np.arange(len(mismatches))
    return all_indices[mismatches]


def report_accuracy(sas_codes, indx, python_output_dir='py_output'):
    '''Our current implementation of accuracy testing.
    expects directory with results of sameer's python translation as well as 
    a c-codes dictionary and the index which to use
    '''
    accuracies = {}
    for var_file_path in gen_file_paths(python_output_dir):
        var_df = pd.read_csv(var_file_path)

        accuracies.update(var_df.iloc[indx].to_dict())

    accuracies = merge_dicts(sas_codes, indx, accuracies)
    accuracy_df = pd.DataFrame.from_dict(accuracies, orient='index')
    accuracy_df.to_csv('accuracy.csv')


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
    file_paths = tuple(op.join(dir_name, file_name) 
        for file_name in os.listdir(dir_name))
    if filter_func:
        return filter(filter_func, file_paths)    
    return file_paths


def merge_dicts(sas_codes, taxpayer, python_codes):
    '''
    Combines SAS output for a taxpayer with the corresponding python output.
    '''
    result = {}
    for variable in sas_codes:
        sas_taxpayer = sas_codes[variable][taxpayer]
        lc_v = variable.lower()
        if variable in python_codes:
            result[variable] = (sas_taxpayer, python_codes[variable])
        elif lc_v in python_codes:
            result[lc_v] = (sas_taxpayer, python_codes[lc_v])
        else:
            result[variable] = (sas_taxpayer, '')
    return result


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser('Testing script')
    parser.add_argument('SASCODESPATH',
        help='path to HDF5 file with SAS codes')
    parser.add_argument('rerun', nargs='?', default=False,
        help=('pass any integer other than 0 to rerun taxcalc, '
            'otherwise do not pass anything'))

    cmd_input = parser.parse_args()
    main(cmd_input.SASCODESPATH, bool(cmd_input.rerun))
