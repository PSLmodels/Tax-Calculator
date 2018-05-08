index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      91.0      -9.0      10.8       0.0       1.9
 1    17.93     376.8     -18.8      29.7       0.0      10.9
 2    17.93     561.9     -18.0      48.9       0.0      30.8
 3    17.92     746.3      -9.1      66.4       0.0      57.3
 4    17.93     963.2       2.2      88.7       0.0      91.0
 5    17.93    1235.4      20.0     115.4       0.0     135.3
 6    17.92    1593.9      48.7     150.0       0.0     198.7
 7    17.93    2080.4      90.4     196.4       0.0     286.8
 8    17.92    2854.7     172.3     272.1       0.0     444.4
 9    17.93    6133.3     889.9     439.2       0.0    1329.1
 A   179.26   16637.0    1168.5    1417.5       0.0    2586.0

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      91.0      -0.0       0.0       0.0      -0.0
 1    17.93     376.8      -3.2       0.0       0.0      -3.2
 2    17.93     561.9      -7.0       0.0       0.0      -7.0
 3    17.92     746.3     -10.3       0.0       0.0     -10.3
 4    17.93     963.2     -14.8       0.0       0.0     -14.8
 5    17.93    1235.4     -24.3       0.0       0.0     -24.3
 6    17.92    1593.9     -32.8       0.0       0.0     -32.8
 7    17.93    2080.4     -40.2       0.0       0.0     -40.2
 8    17.92    2854.7     -63.9       0.0       0.0     -63.9
 9    17.93    6133.3     -70.4       0.0       0.0     -70.4
 A   179.26   16637.0    -267.0       0.0       0.0    -267.0
create PNG graph output by hand
$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|165.399
filing status (MARS) | weighted count of filing units
1|87.385
2|68.234
4|9.781
weighted count of those with NEGATIVE MTR
21.474
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|31.186|0.0
0|2.548|7.2
1|58.678|14.14
2|36.669|25.47
3|13.927|32.23
4|0.798|43.4
5|0.103|55.22
6|0.017|66.73
