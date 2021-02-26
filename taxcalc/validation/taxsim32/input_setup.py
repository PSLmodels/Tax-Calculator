"""
Generates TAXSIM-32 `.in` input files, downloads `.in.out-taxsim` output files,
prepares files for Tax Calculator and zips them
"""
import pandas as pd
import os
import glob
from zipfile import ZipFile

# requires curl
def get_inputs():
    """
    Runs taxsim_input.py for all combinations of year and assumption sets
    """
    letters = ["a", "b", "c"]
    years = ["2018", "2019"]

    name_list = [str(y + " " + x) for x in letters for y in years]

    for name in name_list:
        command = str("python taxsim_input.py " + name)
        os.system(command)


def get_ftp_output():
    """
    Uses `curl` to upload assumption set input files
    and save taxsim-32 output files
    """
    letters = ["a", "b", "c"]
    years = ["18", "19"]
    file_list = [str(x + y + ".in") for x in letters for y in years]

    for f in file_list:
        file_out = f + ".out-taxsim"
        os.system(f"curl -u taxsim:02138 -T {f} ftp://taxsimftp.nber.org/tmp/userid")
        c_out = str(
            "curl -u taxsim:02138 "
            + "ftp://taxsimftp.nber.org/tmp/userid.txm32 -o "
            + file_out
        )
        os.system(c_out)


def change_delim():
    for file in glob.glob("*.in.out-taxsim"):
        # Read in the file
        with open(file, "r") as fin:
            filedata = fin.read()

        # Replace the target string
        filedata = filedata.replace(",", " ")

        # Write the file out again
        with open(file, "w") as fout:
            fout.write(filedata)


def main():
    get_inputs()
    get_ftp_output()
    change_delim()
