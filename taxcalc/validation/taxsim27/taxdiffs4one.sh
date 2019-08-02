#!/bin/bash
# Compute tax differences for a single filing unit.
#
# USAGE: ./taxdiffs4one.sh RECID OUT-TAXCALC OUT-TAXSIM
#
# check command-line arguments
if [[ "$#" -ne 3 ]]; then
    echo "ERROR: number of command-line arguments not equal to three"
    echo "USAGE: ./taxdiffs4one.sh RECID OUT-TAXCALC OUT-TAXSIM"
    exit 1
fi
awk -v ID=$1 '$1==ID' $2 > tmpfile1
echo
cat tmpfile1
awk -v ID=$1 '$1==ID' $3 > tmpfile2
echo
cat tmpfile2
echo
tclsh taxdiffs.tcl tmpfile1 tmpfile2
rm tmpfile1 tmpfile2
exit 0
