#!/bin/bash
# USAGE: ./index_results.sh
# ACTION: (1) check for existence of taxcalc package
#         (2) executes several tc commands used in index.htmx
#         (3) shows differences between index.out and index.res
#         (4) prints reminder of how to create *.png files
#         (5) delete non-HTML tc output files

echo "STARTING : `date`"

# check existence of taxcalc package
conda list taxcalc | awk '$1~/taxcalc/{rc=1}END{exit(rc)}'
if [ $? -eq 0 ]; then
    echo "ERROR: taxcalc package does not exist"
    exit 1
fi

# exectue tc commands used in index.htmx
OUT=./index.out
echo "index.res" > $OUT
tc cps.csv 2022 --reform ref3.json --tables
echo "$ cat cps-22-#-ref3-#-tab.text" >> $OUT
cat cps-22-#-ref3-#-tab.text >> $OUT
tc cps.csv 2024 --reform ref3.json --graphs
echo "create PNG graph output by hand" >> $OUT
tc cps.csv 2016 --sqldb
echo "$ cat tab.sql | sqlite3 cps-16-#-#-#.db" >> $OUT
cat tab.sql | sqlite3 cps-16-#-#-#.db >> $OUT

# show differences between index.out and index.res
echo "diff index.out index.res"
echo "*********************************************************************"
diff $OUT index.res
echo "*********************************************************************"

# remind how to convert graph *.html files to *.png files
echo "==> open cps-24-#-ref3-#-atr.html and save as atr.png"
echo "==> open cps-24-#-ref3-#-mtr.html and save as mtr.png"
echo "==> open cps-24-#-ref3-#-pch.html and save as pch.png"

# remove non-HTML tc output files
rm cps-??-#-*csv
rm cps-??-#-*text
rm cps-??-#-*db

echo "FINISHED : `date`"
exit 0
