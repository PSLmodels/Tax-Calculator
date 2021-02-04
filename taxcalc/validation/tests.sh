#!/bin/bash
# Executes validation TESTS by calling test.sh scripts in subdirectories.
echo "STARTING WITH VALIDATION TESTS : `date`"
# execute tests several at a time
echo "In taxsim27 directory, executing test.sh using a11, b11, c11 data..."
cd taxsim27
./test.sh a11 &
./test.sh b11 &
./test.sh c11 &
wait
echo "In taxsim27 directory, executing test.sh using a12, b12, c12 data..."
./test.sh a12 &
./test.sh b12 &
./test.sh c12 &
wait
echo "In taxsim27 directory, executing test.sh using a13, b13, c13 data..."
./test.sh a13 &
./test.sh b13 &
./test.sh c13 &
wait
echo "In taxsim27 directory, executing test.sh using a17, b17, c17 data..."
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
