#!/bin/zsh
# CLI input data tests assume that the three national TMD files are in the top-
# level Tax-Calculator folder where they are ignored by git version control.
# See Makefile target idtest for usage.

# use CPS input files
tc cps.csv 2025 --numyears 11 --exact --params --tables --silent
for yr in {25..35}; do
    diff -q cps-$yr-#-#-#-#-params.baseline cps-$yr-params.baseline
    if [ $? -eq 0 ]; then
        rm cps-$yr-#-#-#-#-params.baseline
    fi
    diff -q cps-$yr-#-#-#-#-params.reform cps-$yr-params.reform
    if [ $? -eq 0 ]; then
        rm cps-$yr-#-#-#-#-params.reform
    fi
    diff -q cps-$yr-#-#-#-#.tables cps-$yr.tables
    if [ $? -eq 0 ]; then
        rm cps-$yr-#-#-#-#.tables
    fi
done

# use TMD input files
tc ../../../tmd.csv 2025 --numyears 11 --exact --params --tables --silent
for yr in {25..35}; do
    diff -q tmd-$yr-#-#-#-#-params.baseline tmd-$yr-params.baseline
    if [ $? -eq 0 ]; then
        rm tmd-$yr-#-#-#-#-params.baseline
    fi
    diff -q tmd-$yr-#-#-#-#-params.reform tmd-$yr-params.reform
    if [ $? -eq 0 ]; then
        rm tmd-$yr-#-#-#-#-params.reform
    fi
    diff -q tmd-$yr-#-#-#-#.tables tmd-$yr.tables
    if [ $? -eq 0 ]; then
        rm tmd-$yr-#-#-#-#.tables
    fi
done

