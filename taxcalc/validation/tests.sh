#!/bin/bash
# Executes validation TESTS by calling TESTS scripts in various subdirectories.
# .... check number of command-line arguments
if [[ "$#" -gt 1 ]]; then
    echo "ERROR: can specify at most one command-line argument"
    echo "USAGE: ./tests.sh [all]"
    echo "       (using the 'all' option may execute four tests at a time)"
    exit 1
fi
# .... specify whether or not to execute all tests
ALLTESTS=false
if [[ "$#" -eq 1 ]]; then
    if [[ "$1" == "all" ]]; then
        ALLTESTS=true
    else
        echo "ERROR: optional command-line argument must be all"
        echo "USAGE: ./tests.sh [all]"
        exit 1
    fi
fi
echo "STARTING WITH VALIDATION TESTS : `date`"
if [[ $ALLTESTS == true ]] ; then
    # execute all tests sequentially
    cd taxsim
    bash tests.sh all
    cd ..
    # cd drake
    # bash tests.sh all
    # cd ..
else
    # execute basic tests simultaneously
    cd taxsim
    bash tests.sh &
    cd ..
    # cd drake
    # bash tests.sh &
    # cd ..
    wait
fi
echo "FINISHED WITH VALIDATION TESTS : `date`"
exit 0
