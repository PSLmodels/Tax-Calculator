import os
import sys
import shutil
import prepare_taxcalc_input as ptci
import process_taxcalc_output as ptco

CURR_PATH = os.path.abspath(os.path.dirname(__file__))


# prepare Tax-Calculator input file
def prep_tc_input(letter, year):
    """
    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent

    Returns:
        None
    """
    taxsim_in = str(letter + str(year) + ".in")
    taxsim_in_csv = taxsim_in + ".csv"
    ptci.main(taxsim_in, taxsim_in_csv)


# calculate Tax-Calculator output
def calc_tc_output(letter, year):
    """
    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent

    Returns:
        None
    """
    YY = str(year)
    taxsim_in = str(letter + str(year) + ".in")
    taxsim_in_csv = taxsim_in + ".csv"
    taxsim_out_csv = taxsim_in + ".out.csv"
    if os.path.exists(os.path.join(CURR_PATH, taxsim_in_csv)) is False:
        sys.exit("ERROR: LYY_FILENAME is not a valid path")
    year = "20" + YY
    command = (
        "tc "
        + taxsim_in_csv
        + " "
        + year
        + " --reform taxsim_emulation.json --dump"
    )
    os.system(command)

    file_temp = taxsim_in + "-" + YY + "-#-taxsim_emulation-#.csv"
    file_temp_path = os.path.join(CURR_PATH, file_temp)
    file_out_path = os.path.join(CURR_PATH, taxsim_out_csv)
    shutil.move(file_temp_path, file_out_path)

    file_temp2 = taxsim_in + "-" + YY + "-#-taxsim_emulation-#-doc.text"
    os.remove(file_temp2)


def convert_to_taxsim(letter, year, save=False):
    """
     Convert Tax-Calculator output to TAXSIM-35 format

     Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent

    Returns:
        None
    """
    taxsim_in = str(letter + str(year) + ".in")
    taxsim_in_csv = taxsim_in + ".csv"
    taxsim_out_csv = taxsim_in + ".out.csv"
    file_out = taxsim_in + ".out-taxcalc"
    ptco.main(taxsim_out_csv, file_out)
    if not save:  # Delete intermediate input and output files if not saving
        os.remove(taxsim_in_csv)
        os.remove(taxsim_out_csv)


def io(letter, year):
    """
    Call Tax-Calculator tc CLI reading input data from specified
    TAXSIM-35 input file and writing output in TAXSIM-35 output format
    to a file with the specified input file name plus the .out-taxcalc
    extension.

    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent
        offset (int): offset to alter the random number seed

    Returns:
        None
    """
    prep_tc_input(letter, year)
    calc_tc_output(letter, year)
    convert_to_taxsim(letter, year)
