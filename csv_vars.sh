#!/bin/bash
if [[ "$#" -ne 1 ]]; then
    echo "csv_vars.sh prints all CSV file column numbers and names"
    echo "ERROR: number of command-line arguments not equal to one"
    echo "USAGE: ./csv_vars.sh FILENAME"
    exit 1
fi
awk -F, '
NR == 1 { for( i = 1; i <= NF; i++ ) print i, $i }
' $1
