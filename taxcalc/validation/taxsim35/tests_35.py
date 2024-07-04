import os
import shutil
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
tests_passed_dict = {"a": {}, "b": {}, "c": {}}
for letter in assumption_set:
    for year in years:
        tests_passed = main_comparison.main(letter, year)
        tests_passed_dict[letter][year] = tests_passed

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
any_fail = False
for letter in assumption_set:
    for year in years:
        if tests_passed_dict[letter][year]:
            print(
                "************************************************** \n"
                + "************************************************** \n"
                + "Validation tests for "
                + letter
                + str(year)
                + " pass.  "
                + "Any differences betweeen "
                + "taxcalc and TAXSIM-35 are expected due to modeling "
                + "differences. \n"
                + "************************************************** \n"
                + "**************************************************"
            )
            file = os.path.join(
                CUR_PATH,
                "actual_differences",
                letter + str(year) + "differences.xlsx",
            )
            os.remove(file)
            file = os.path.join(
                CUR_PATH,
                "actual_differences",
                letter + str(year) + "-taxdiffs-actual.csv",
            )
            os.remove(file)

        else:
            any_fail = True
            print(
                "************************************************** \n"
                + "************************************************** \n"
                + "At least one validation test for "
                + letter
                + str(year)
                + " failed.  Please look "
                + "at differences in the actual and expected files and "
                + "resolve the unexpected differences. \n"
                + "************************************************** \n"
                + "**************************************************"
            )
if not any_fail:  # if none fail, remove the actual_differences directory
    shutil.rmtree(os.path.join(CUR_PATH, "actual_differences"))
