#!/bin/zsh
# CLI tests of behavior responses logic using CPS and TMD input data.
# These tests assume calibrated (less than full) claiming of credits.
#
# The runs below uses either the refA.json or refB.json policy reforms.
# The runs are organized in pairs: the first member of each pair analyzes
# 2035 alone and the second analyzes the eight years 2028 through 2035,
# so that comparing their 2035 tables checks that advancing through intervening
# years produces the same 2035 results as analyzing 2035 directly.
#
# Runs using CPS input data and the refA.json reform:
#   runs 10 and 11: no --behavior option (static analysis)
#   runs 20 and 21: --behavior br0.json (all elasticities zero)
#   runs 30 and 31: --behavior br1.json (all elasticities are non-zero)
# Runs using TMD input data and the refB.json reform:
#   run 50: no --behavior option (static analysis)
#   run 60: --behavior br1.json (all elasticities are non-zero)
#
# The within-pair comparions should never fail.  The comparion with an
# -expect file should not fail unless the behavioral response or policy
# reform parameters have been changed.
#
# Note that the capital-gains response has no effect on results computed
# with CPS input data, because those data contain no long-term capital
# gains (p23250 is zero for every filing unit).
#
# This script always exits zero, so check its output for the word
# "Differences" rather than relying on its exit status.

ERRORS=0

tc cps.csv 2035 --numyears 1                     --runid 10 \
   --reform refA.json --exact --tables --silent &
tc cps.csv 2028 --numyears 8                     --runid 11 \
   --reform refA.json --exact --tables --silent &
tc cps.csv 2035 --numyears 1 --behavior br0.json --runid 20 \
   --reform refA.json --exact --tables --silent &
wait
tc cps.csv 2028 --numyears 8 --behavior br0.json --runid 21 \
   --reform refA.json --exact --tables --silent &
tc cps.csv 2035 --numyears 1 --behavior br1.json --runid 30 \
   --reform refA.json --exact --tables --silent &
tc cps.csv 2028 --numyears 8 --behavior br1.json --runid 31 \
   --reform refA.json --exact --tables --graphs --silent &
wait
cmp run11-35.tables run11-35.tables-expect
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run11-35.tables run11-35.tables-expect
fi
cmp run11-35.tables run10-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run11-35.tables run10-35.tables
fi
cmp run20-35.tables run10-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run20-35.tables run10-35.tables
fi
cmp run21-35.tables run20-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run21-35.tables run20-35.tables
fi
cmp run30-35.tables run30-35.tables-expect
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run30-35.tables run30-35.tables-expect
fi
cmp run31-35.tables run30-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run31-35.tables run30-35.tables
fi
if [ $ERRORS -eq 0 ]; then
    rm -f run??-??.tables
    rm -f run31-??-???.html
fi

# use TMD input files
if ! [[ -f ../../../tmd.csv ]]; then
    echo "Skipping TMD input data test" >&2
    exit 0
fi
if ! [[ -f ../../../tmd_weights.csv.gz ]]; then
    echo "Skipping TMD input data test" >&2
    exit 0
fi
if ! [[ -f ../../../tmd_growfactors.csv ]]; then
    echo "Skipping TMD input data test" >&2
    exit 0
fi
tc ../../../tmd.csv 2035 --numyears 1 --runid 50 \
   --reform refB.json --exact --tables --silent &
tc ../../../tmd.csv 2035 --numyears 1 --behavior br1.json --runid 60 \
   --reform refB.json --exact --tables --silent &
wait
cmp run50-35.tables run50-35.tables-expect
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run50-35.tables run50-35.tables-expect
fi
cmp run60-35.tables run60-35.tables-expect
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run60-35.tables run60-35.tables-expect
fi
if [ $ERRORS -eq 0 ]; then
    rm -f run??-??.tables
fi
