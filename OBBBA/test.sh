#!/bin/zsh
#
# Test used in process of implementing OBBBA reforms in Tax-Calculator
# https://github.com/PSLmodels/Tax-Calculator/issues/2926
# 
# NOTE: test uses the three TMD input data files located in home folder and
#            uses a copy of Tax-Calculator/taxcalc/reforms/ext.json located
#            in the folder containing this script
# USAGE: conduct this test in the Tax-Calculator/OBBBA folder by
#        (a) installing a version of Tax-Calculator and then
#        (b) executing this script using the ./test.sh command

tc --version
diff -q ext.json ../taxcalc/reforms/ext.json
if [[ $? -ne 0 ]]; then
    echo "ERROR: ext.json differs from ../taxcalc/reforms/ext.json"
    exit 1
fi
date

tc ~/tmd.csv 2024 --numyears 12 --reform ext.json --exact --tables --runid 5
if [[ $? -ne 0 ]]; then
    echo "ERROR: no Tax-Calculator package installed"
    exit 1
fi

cat run5-??.tables > test-tables.actual
rm -f run5-??.tables
ls -l test-tables.??????
diff -q test-tables.actual test-tables.expect
if [[ $? -ne 0 ]]; then
    echo "SOME DIFFERENCES between test-tables.actual test-tables.expect"
else
    echo "NO DIFFERENCES between test-tables.actual test-tables.expect"
    rm -f test-tables.actual
fi
exit 0
