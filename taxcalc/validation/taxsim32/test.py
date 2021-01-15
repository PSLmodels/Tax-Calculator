# from colorama import Fore, Style
# print(Fore.RED + Style.BRIGHT + 'test')

import sys
import argparse
import os
# from zipfile import ZipFile
import numpy as np
import pandas as pd


def main():

    usage_str = 'python test.py LETTER YEAR [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Main runner file for each assumption set per year.'))
    parser.add_argument('LETTER', nargs='?', default='',
                        help=('LETTER specifies assumption set '
                              'used to generate input data.'))
    parser.add_argument('YEAR', nargs='?', type=int, default=0,
                        help=('YEAR specifies calendar year assumed in '
                              'generated input data (specified in the form '
                              '20{year})'))

    args = parser.parse_args()
    runner(args.LETTER, args.YEAR)

def runner(assump_set, year):
    # (1) generate TAXSIM-32-formatted output using Tax-Calculator tc CLI
    # os.system(f'python taxcalc.py {assump_set}{year}.in')

    # (2) generate tax differences
    taxsim_df = pd.read_csv(f'{assump_set}{year}.in.out-taxsim', sep=' ', skipinitialspace=True, index_col=False)
    taxsim_df = taxsim_df.iloc[:, 0:28]
    taxcalc_df = pd.read_csv(f'{assump_set}{year}.in.out-taxcalc', sep=' ', skipinitialspace=True, index_col=False, header=None)
    
    taxcalc_df.columns = taxsim_df.columns # rename taxcalc output columns

    diff_dict = {
                '# of differing records': [], 
                 'max_diff': [],
                 'max_diff_index': [],
                 'max_diff_taxsim_val': [],
                 'max_diff_taxcalc_val': []
                 }

    for col in taxsim_df.columns[3:]:

        df_diff = pd.DataFrame({'a': taxsim_df[col], 'b': taxcalc_df[col]})
        df_diff_recs = df_diff[df_diff['a'] != df_diff['b']]
        diff_dict['# of differing records'].append(df_diff_recs.shape[0])

        diff_list = [x-y for x, y in zip(taxsim_df[col], taxcalc_df[col])]
        max_val, ind = max(diff_list), diff_list.index(max(diff_list))

        diff_dict['max_diff'].append(max_val)
        if max_val != 0:
            diff_dict['max_diff_index'].append(ind)
            diff_dict['max_diff_taxsim_val'].append(taxsim_df.loc[ind, col])
            diff_dict['max_diff_taxcalc_val'].append(taxcalc_df.loc[ind, col])
        else:
            diff_dict['max_diff_index'].append('no diff')
            diff_dict['max_diff_taxsim_val'].append('no diff')
            diff_dict['max_diff_taxcalc_val'].append('no diff')


    final_df = pd.DataFrame(diff_dict, index=taxsim_df.columns[3:])
    print(final_df)

    # (3) check for difference between LYY.taxdiffs-actual and LYY.taxdiffs-expect




if __name__ == '__main__':
    sys.exit(main())