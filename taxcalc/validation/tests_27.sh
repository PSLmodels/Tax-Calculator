# taxcalc python package MUST be installed
# Headers from each .out-taxsim file MUST be removed

#!/bin/bash
# Executes validation TESTS by calling test.sh scripts in subdirectories.
echo "STARTING WITH VALIDATION TESTS : `date`"
# execute tests several at a time
echo "In taxsim27 directory, executing test.sh using a17, b17, c17 data..."
cd taxsim27
./test.sh a17 &
./test.sh b17 &
./test.sh c17 &
wait
echo "In taxsim27 directory, executing test.sh using a18, b18, c18 data..."
./test.sh a18 &
./test.sh b18 &
./test.sh c18 &
wait
cd ..
# cd someothermodel
# ./test.sh xxx &
# wait
# cd ..
echo "FINISHED WITH VALIDATION TESTS : `date`"
exit 0
