#!/bin/zsh
# CLI tests of behavior responses logic

ERRORS=0

tc cps.csv 2035 --numyears 1                     --runid 10 \
   --reform ref.json --exact --tables --silent
tc cps.csv 2028 --numyears 8                     --runid 11 \
   --reform ref.json --exact --tables --silent
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

tc cps.csv 2035 --numyears 1 --behavior br0.json --runid 20 \
   --reform ref.json --exact --tables --silent
cmp run20-35.tables run10-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run20-35.tables run10-35.tables
fi
tc cps.csv 2028 --numyears 8 --behavior br0.json --runid 21 \
   --reform ref.json --exact --tables --silent
cmp run21-35.tables run20-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run21-35.tables run20-35.tables
fi

tc cps.csv 2035 --numyears 1 --behavior br1.json --runid 30 \
   --reform ref.json --exact --tables --silent
cmp run30-35.tables run30-35.tables-expect
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run30-35.tables run30-35.tables-expect
fi
tc cps.csv 2028 --numyears 8 --behavior br1.json --runid 31 \
   --reform ref.json --exact --tables --graphs --silent
cmp run31-35.tables run30-35.tables
if [ $? -ne 0 ]; then
    ERRORS=1
    echo Differences between run31-35.tables run30-35.tables
fi

if [ $ERRORS -eq 0 ]; then
    rm -f run??-??.tables
    rm -f run31-??-???.html
fi
