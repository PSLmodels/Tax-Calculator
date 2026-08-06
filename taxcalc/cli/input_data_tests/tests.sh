#!/bin/zsh
# CLI input data tests assume that the three national TMD files are in the top-
# level Tax-Calculator folder where they are ignored by git version control.
# These tests assume calibrated (less than full) claiming of credits.
# See Makefile target idtest for usage.

# use CPS input files
tc cps.csv 2025 --numyears 11 --exact --tables --silent
for yr in {25..35}; do
    diff -q cps-$yr-#-#-#-#.tables cps-$yr.tables
    if [ $? -eq 0 ]; then
        rm cps-$yr-#-#-#-#.tables
    fi
done

# use TMD input files
if ! [[ -f ../../../tmd.csv ]]; then
    echo "Skipping TMD input data test" >&2
    exit 0
fi
tc ../../../tmd.csv 2025 --numyears 11 --exact --tables --silent
for yr in {25..35}; do
    diff -q tmd-$yr-#-#-#-#.tables tmd-$yr.tables
    if [ $? -eq 0 ]; then
        rm tmd-$yr-#-#-#-#.tables
    fi
done

