#!/bin/zsh
# CLI tests of behavior responses logic

tc cps.csv 2035 --numyears 1                     --runid 10 \
   --reform ref.json --exact --params --tables --silent
echo finished run10
tc cps.csv 2028 --numyears 8                     --runid 11 \
   --reform ref.json --exact --params --tables --silent
echo finished run11
echo run11-vs-run11exp-diffs:
diff run11-35.tables run11-35.tables-expect
echo run11-vs-run10-diffs:
diff run11-35.tables run10-35.tables

tc cps.csv 2035 --numyears 1 --behavior br0.json --runid 20 \
   --reform ref.json --exact --params --tables --silent
echo finished run20
echo run20-vs-run10-diffs:
diff run20-35.tables run10-35.tables
tc cps.csv 2028 --numyears 8 --behavior br0.json --runid 21 \
   --reform ref.json --exact --params --tables --silent
echo finished run21
echo run21-vs-run20-diffs:
diff run21-35.tables run20-35.tables

tc cps.csv 2035 --numyears 1 --behavior br1.json --runid 30 \
   --reform ref.json --exact --params --tables --silent
echo finished run30
tc cps.csv 2028 --numyears 8 --behavior br1.json --runid 31 \
   --reform ref.json --exact --params --tables --silent
echo finished run31
echo run31-vs-run30-diffs:
diff run31-35.tables run30-35.tables
