#!/bin/zsh
# CLI input data tests assume that the three PUF files and the
# three TMD national files are in the top-level Tax-Calculator
# directory where they are ignored by git version control.
# See Makefile target idtest for usage.

tc cps.csv 2035 --exact --params --tables --silent
diff -q cps-35-#-#-#-#-params.baseline cps-35-params.baseline
if [ $? -eq 0 ]; then
    rm cps-35-#-#-#-#-params.baseline
fi
diff -q cps-35-#-#-#-#-params.reform cps-35-params.reform
if [ $? -eq 0 ]; then
    rm cps-35-#-#-#-#-params.reform
fi
diff -q cps-35-#-#-#-#.tables cps-35.tables
if [ $? -eq 0 ]; then
    rm cps-35-#-#-#-#.tables
fi

tc ../../../puf.csv 2035 --exact --params --tables --silent
diff -q puf-35-#-#-#-#-params.baseline puf-35-params.baseline
if [ $? -eq 0 ]; then
    rm puf-35-#-#-#-#-params.baseline
fi
diff -q puf-35-#-#-#-#-params.reform puf-35-params.reform
if [ $? -eq 0 ]; then
    rm puf-35-#-#-#-#-params.reform
fi
diff -q puf-35-#-#-#-#.tables puf-35.tables
if [ $? -eq 0 ]; then
    rm puf-35-#-#-#-#.tables
fi

tc ../../../tmd.csv 2035 --exact --params --tables --silent
diff -q tmd-35-#-#-#-#-params.baseline tmd-35-params.baseline
if [ $? -eq 0 ]; then
    rm tmd-35-#-#-#-#-params.baseline
fi
diff -q tmd-35-#-#-#-#-params.reform tmd-35-params.reform
if [ $? -eq 0 ]; then
    rm tmd-35-#-#-#-#-params.reform
fi
diff -q tmd-35-#-#-#-#.tables tmd-35.tables
if [ $? -eq 0 ]; then
    rm tmd-35-#-#-#-#.tables
fi
