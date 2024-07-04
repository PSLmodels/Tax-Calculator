# taxcalc python package MUST be installed

#!/bin/bash
# Executes validation TESTS by calling test.sh scripts in subdirectories.
echo "STARTING WITH VALIDATION TESTS : `date`"
# execute tests several at a time
echo "In taxsim35 directory, executing test_35.py..."
cd taxsim35
python tests_35.py
wait
cd ..
echo "FINISHED WITH VALIDATION TESTS : `date`"
exit 0
