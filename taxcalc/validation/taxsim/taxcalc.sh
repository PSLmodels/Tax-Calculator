#!/bin/bash
# Call Tax-Calculator tc CLI reading input data from specified TAXSIM-27
# input file and writing output in TAXSIM-27 output format to a file
# with the spcified input file name plus the .out-taxcalc extension.
#
# USAGE: ./taxcalc.sh LYY_FILENAME [save]
#
# ... check command-line arguments
if [[ "$#" -lt 1 || "$#" -gt 2 ]]; then
    echo "ERROR: number of command-line arguments not in 1-to-2 range"
    echo "USAGE: ./taxcalc.sh LYY_FILENAME [save]"
    echo "       WHERE L is a letter that is valid taxsim_input.py L input and"
    echo "             YY is valid taxsim_input.py YEAR (20YY) input;"
    echo "       WHERE the 'save' option skips the deletion of intermediate"
    echo "             files at the end of this script"
    exit 1
fi
LYY_FN=$1
SAVE=false
if [[ "$#" -eq 2 ]]; then
    if [[ "$2" == "save" ]]; then
        SAVE=true
    else
        echo "ERROR: optional second command-line argument must be 'save'"
        echo "USAGE: ./taxcalc.sh LYY_FILENAME [save]"
        exit 1
    fi
fi
# ... prepare Tax-Calculator input file
L=${LYY_FN:0:1}    
YY=${LYY_FN:1:2}
python prepare_taxcalc_input.py $LYY_FN $LYY_FN.csv
# ... calculate Tax-Calculator output
tc $LYY_FN.csv 20$YY --dump
# ... convert Tax-Calculator output to Internet-TAXSIM-27-format
python process_taxcalc_output.py $LYY_FN-$YY-#-#-#.csv $LYY_FN.out-taxcalc
# ... delete intermediate input and output files if not saving files
rm -f $LYY_FN-$YY-#-#-#-doc.text
if [[ $SAVE == false ]]; then
    rm -f $LYY_FN.csv
    rm -f $LYY_FN-$YY-#-#-#.csv
fi
exit 0
