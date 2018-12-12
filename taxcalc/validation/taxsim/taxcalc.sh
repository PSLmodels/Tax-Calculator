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
if [[ $? -ne 0 ]]; then
    echo "ERROR: prepare_taxcalc_input.py failed"
    exit 1
fi
# ... calculate Tax-Calculator output
tc $LYY_FN.csv 20$YY --reform taxsim_emulation.json --dump
if [[ $? -ne 0 ]]; then
    echo "ERROR: taxcalc package is not available"
    exit 1
fi
mv $LYY_FN-$YY-#-taxsim_emulation-#.csv $LYY_FN.out.csv
rm -f $LYY_FN-$YY-#-taxsim_emulation-#-doc.text
# ... convert Tax-Calculator output to Internet-TAXSIM-27-format
python process_taxcalc_output.py $LYY_FN.out.csv $LYY_FN.out-taxcalc
if [[ $? -ne 0 ]]; then
    echo "ERROR: process_taxcalc_output.py failed"
    exit 1
fi
# ... delete intermediate input and output files if not saving files
if [[ $SAVE == false ]]; then
    rm -f $LYY_FN.csv
    rm -f $LYY_FN.out.csv
fi
exit 0
