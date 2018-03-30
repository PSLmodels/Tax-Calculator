#!/bin/bash
if [[ "$#" -ne 2 ]]; then
    echo "csv_show.sh prints all non-zero CSV file column values for RECID"
    echo "ERROR: must specify exactly two command-line arguments"
    echo "USAGE: ./csv_show.sh FILENAME RECID"
    exit 1
fi
awk -F, '
BEGIN {
    recid_varnum = 0
}
NR == 1 {
    for ( i = 1; i <= NF; i++ ) {
        varname[i] = $i
        if ( $i == "RECID" ) recid_varnum = i
    }
}
$recid_varnum == id {
    for ( i = 1; i <= NF; i++ ) {
        if ( $i != 0 ) {
            print i, varname[i], $i
        }
    }
    exit
}
' id=$2 $1
