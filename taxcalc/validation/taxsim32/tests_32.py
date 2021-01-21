import os
from datetime import date
import input_setup
import main_comparison

# setup input files
# input_setup.main()

# run taxcalc/taxsim comparison
for assump_set in ('a', 'b', 'c'):
    for year in (18, 19):
        main_comparison.main(assump_set, year)

# clean up files auxillary files
os.system('rm -f *.in* *.out*')