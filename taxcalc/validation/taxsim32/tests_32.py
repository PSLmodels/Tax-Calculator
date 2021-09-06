import os
import glob
import input_setup
import main_comparison

CUR_PATH = os.path.abspath(os.path.dirname(__file__))

# setup input files
if not glob.glob(os.path.join(CUR_PATH, '*in.out-taxsim')):
    input_setup.main()

# run taxcalc/taxsim comparison
for assump_set in ('a', 'b', 'c'):
    for year in (17, 18, 19):
        main_comparison.main(assump_set, year)

# clean up taxcalc files
# keep taxsim files to avoid download again
for file in CUR_PATH:
    for file in glob.glob('*.out*') and glob.glob('*.in*'):
        if file.endswith('taxcalc'):
            os.remove(file)
