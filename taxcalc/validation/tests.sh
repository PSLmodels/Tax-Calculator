#!/bin/bash
# Executes validation TESTS by calling test.sh scripts in subdirectories.
echo "STARTING WITH VALIDATION TESTS : `date`"
# execute tests several at a time
cd taxsim27
./test.sh a17 &
./test.sh b17 &
./test.sh c17 &
wait
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
