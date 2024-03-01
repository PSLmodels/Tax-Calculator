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
tests_passed_list = []
for letter in assumption_set:
    for year in years:
        tests_passed = main_comparison.main(letter, year)
        tests_passed_list.append(tests_passed)

# clean up files
for file in CUR_PATH:
    for file in glob.glob("*.out*") and glob.glob("*.in*"):
        if file.endswith("taxcalc"):
            os.remove(file)
        if file.endswith("taxsim"):
            os.remove(file)
    for file in glob.glob("*.in"):
        os.remove(file)
# If tests passed, clean up the actual_differences directory
# keep if tests fail to help diagnose the problem
if not any(x is False for x in tests_passed_list):
    for file in os.path.join(CUR_PATH, "actual_differences"):
        os.remove(file)
    os.rmdir(os.path.join(CUR_PATH, "actual_differences"))
