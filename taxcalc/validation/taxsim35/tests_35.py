import os
import glob
import input_setup
import main_comparison

CUR_PATH = os.path.abspath(os.path.dirname(__file__))

# define the scope of the tests
assumption_set = ["a", "b", "c"]  # datafiles to test
years = [17, 18, 19, 20, 21]  # years to test


# setup input files
# if not glob.glob(os.path.join(CUR_PATH, '*in.out-taxsim')):
input_setup.taxsim_io(assumption_set, years)

# run taxcalc/taxsim comparison
for letter in assumption_set:
    for year in years:
        main_comparison.main(letter, year)

# clean up taxcalc files
# keep taxsim files to avoid download again
for file in CUR_PATH:
    for file in glob.glob("*.out*") and glob.glob("*.in*"):
        if file.endswith("taxcalc"):
            os.remove(file)
