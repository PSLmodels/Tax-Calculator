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
    # os.system(f"curl -u taxsim:02138 -T {f} ftp://taxsimftp.nber.org/tmp/tc_valid")
    # c_out = str(
    #     "curl -u taxsim:02138 "
    #     + "ftp://taxsimftp.nber.org/tmp/tc_valid.txm35 -o "
    #     + file_out
    # )
    # os.system(c_out)
    # os.system(f"ssh -T -o StrictHostKeyChecking=no taxsimssh@taxsimssh.nber.org <{f} >{file_out}")
    # not the above was not working in April 2023, so using a different method
    # however, method below has issues if f has more than 1000 records
    os.system(
        f"curl -F {f}=@{f} 'https://taxsim.nber.org/taxsim35/redirect.cgi' >{file_out}"
    )


def change_delim(letter, year):
    """ "
    This function changes the delimter in the taxsim output files from
    a comma to a space

    This is necessary because taxsim output seems to vary - for some years
    the separator is a comma and for others (seemingly before 2020) it's a space

    Args:
        letter (character): letter denoting assumption set to generate data
        year (int): year data will represent
        offset (int): offset to alter the random number seed

    Returns:
        None
    """
    f = str(letter + str(year) + ".in")
    file_out = f + ".out-taxsim"
    # Read in the file
    with open(file_out, "r") as fin:
        filedata = fin.read()

    # Replace the target string
    filedata = filedata.replace(",", " ")

    # Write the file out again
    with open(file_out, "w") as fout:
        fout.write(filedata)


def taxsim_io(assump_set, years):
    for letter in assump_set:
        for year in years:
            taxsim_input.generate_datasets(letter, year)
            get_ftp_output(letter, year)
            # change_delim(letter, year)
