#!/bin/zsh
#
# Script used in process of implementing OBBBA reforms in Tax-Calculator
# https://github.com/PSLmodels/Tax-Calculator/issues/2926
# 
# NOTE: test uses the three TMD input data files located in home folder and
#            uses a copy of Tax-Calculator/taxcalc/reforms/ext.json located
#            in the folder containing this script
# USAGE: conduct this test in the Tax-Calculator/OBBBA folder by
#        (a) installing a version of Tax-Calculator and then
#        (b) executing this script using the ./tally.sh command

tc --version
diff -q ext.json ../taxcalc/reforms/ext.json
if [[ $? -ne 0 ]]; then
    echo "ERROR: ext.json differs from ../taxcalc/reforms/ext.json"
    exit 1
fi
date

tc ~/tmd.csv 2024 --numyears 12 --baseline ext.json --exact --tables --runid 9
if [[ $? -ne 0 ]]; then
    echo "ERROR: no Tax-Calculator package installed"
    exit 1
fi

echo "Twelve-year (2024-2035) itax revenue change is:" > tally.res-new
tail -1 run9-??.tables | awk '$1~/A/{x+=$4}END{print x}' >> tally.res-new
cat run9-??.tables >> tally.res-new
rm -f run9-??.tables
ls -l tally.res*
diff -q tally.res-new tally.results
if [[ $? -ne 0 ]]; then
    echo "SOME DIFFERENCES between tally.res-new tally.results"
else
    echo "NO DIFFERENCES between tally.res-new tally.results"
    rm -f tally.res-new
fi
exit 0
