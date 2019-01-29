#!/bin/bash
if [[ "$#" -ne 1 ]]; then
    echo ERROR: LYY base filename is a required command-line argument
    exit 1
fi
LYY=$1
./taxcalc.sh $LYY.in
tclsh taxdiffs.tcl $LYY.in.out-taxcalc $LYY.in.out-taxsim > $LYY.taxdiffs-actual
cat $LYY.taxdiffs-actual
