"""
Generates TAXSIM-35 `.in` input files, downloads `.in.out-taxsim` output files,
prepares files for Tax Calculator and zips them
"""
import os
import glob
import taxsim_input


def get_ftp_output(letter, year):
    """
    Uses `curl` to upload assumption set input files
    and save taxsim-35 output files

    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent
        offset (int): offset to alter the random number seed

    Returns:
        None
    """
    f = str(letter + str(year) + ".in")
    file_out = f + ".out-taxsim"
    os.system(f"curl -u taxsim:02138 -T {f} ftp://taxsimftp.nber.org/tmp/userid")
    c_out = str(
        "curl -u taxsim:02138 "
        + "ftp://taxsimftp.nber.org/tmp/userid.txm35 -o "
        + file_out
    )
    os.system(c_out)


# def change_delim():
#     """"
#     This function changes the delimter in the taxsim output files from
#     a comma to a space
#     """
#     for file in glob.glob("*.in.out-taxsim"):
#         # Read in the file
#         with open(file, "r") as fin:
#             filedata = fin.read()

#         # Replace the target string
#         filedata = filedata.replace(",", " ")

#         # Write the file out again
#         with open(file, "w") as fout:
#             fout.write(filedata)


def taxsim_io(assump_set, years):
    for letter in assump_set:
        for year in years:
            taxsim_input.generate_datasets(letter, year)
            get_ftp_output(letter, year)
            # change_delim()
