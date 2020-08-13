import argparse
import os
import sys
import shutil


usage_str = 'python taxcalc.py LYY_FILENAME [--save] [--help]'

parser = argparse.ArgumentParser(
    prog='',
    usage=usage_str,
    description=('Call Tax-Calculator tc CLI reading input data from '
                 'specified TAXSIM-32 input file and writing output '
                 'in TAXSIM-32 output format to a file with the '
                 'specified input file name plus the .out-taxcalc '
                 'extension.'))

parser.add_argument('LYY_FILENAME',
                    help=('L is a letter that is valid taxsim_input.py L '
                          'input and YY is valid taxsim_input.py YEAR ,'
                          '(20YY) input.'),
                    default='')

parser.add_argument('--save',
                    help=('Save intermediate files.'),
                    default=False,
                    action="store_true")

args = parser.parse_args()

CURR_PATH = os.path.abspath(os.path.dirname(__file__))

taxsim_in = args.LYY_FILENAME
save = args.save

if os.path.exists(os.path.join(CURR_PATH, taxsim_in)) is False:
    sys.exit("ERROR: LYY_FILENAME is not a valid path")

taxsim_in_csv = taxsim_in + ".csv"
taxsim_out_csv = taxsim_in + ".out.csv"
L = taxsim_in[0]
YY = taxsim_in[1:3]


# prepare Tax-Calculator input file
def prep_tc_input():
    command = "python prepare_taxcalc_input.py " + taxsim_in + \
        " " + taxsim_in_csv
    os.system(command)


# calculate Tax-Calculator output
def calc_tc_output():
    year = '20' + YY
    command = "tc " + taxsim_in_csv + " " + year + \
        " --reform taxsim_emulation.json --dump"
    os.system(command)

    file_temp = taxsim_in + "-" + YY + "-#-taxsim_emulation-#.csv"
    file_temp_path = os.path.join(CURR_PATH, file_temp)
    file_out_path = os.path.join(CURR_PATH, taxsim_out_csv)
    shutil.move(file_temp_path, file_out_path)

    file_temp2 = taxsim_in + "-" + YY + "-#-taxsim_emulation-#-doc.text"
    file_temp2_path = os.path.join(CURR_PATH, file_temp2)
    os.remove(file_temp2)


# convert Tax-Calculator output to TAXSIM-32 format
def convert_to_taxsim():
    file_out = taxsim_in + ".out-taxcalc"
    command = "python process_taxcalc_output.py " + taxsim_out_csv + \
        " " + file_out
    os.system(command)


# delete intermediate input and output files if not saving
def del_int_files():
    if save is False:
        os.remove(taxsim_in_csv)
        os.remove(taxsim_out_csv)


if __name__ == "__main__":
    prep_tc_input()
    calc_tc_output()
    convert_to_taxsim()
    del_int_files()
