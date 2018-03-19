index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      89.4      -8.8      10.6       0.0       1.8
 1    17.93     371.8     -19.1      29.1       0.0      10.0
 2    17.93     557.6     -18.8      48.7       0.0      29.9
 3    17.92     742.6      -9.7      66.1       0.0      56.4
 4    17.93     960.8       1.8      89.3       0.0      91.1
 5    17.93    1235.0      19.4     115.8       0.0     135.2
 6    17.92    1594.7      48.2     150.3       0.0     198.5
 7    17.93    2082.5      89.8     196.8       0.0     286.6
 8    17.93    2858.7     171.5     271.9       0.0     443.4
 9    17.93    6139.4     889.0     438.8       0.0    1327.7
 A   179.26   16632.5    1163.3    1417.5       0.0    2580.8

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      89.4      -0.0       0.0       0.0      -0.0
 1    17.93     371.8      -3.1       0.0       0.0      -3.1
 2    17.93     557.6      -7.0       0.0       0.0      -7.0
 3    17.92     742.6     -10.3       0.0       0.0     -10.3
 4    17.93     960.8     -14.9       0.0       0.0     -14.9
 5    17.93    1235.0     -24.3       0.0       0.0     -24.3
 6    17.92    1594.7     -32.9       0.0       0.0     -32.9
 7    17.93    2082.5     -40.3       0.0       0.0     -40.3
 8    17.93    2858.7     -63.8       0.0       0.0     -63.8
 9    17.93    6139.4     -70.3       0.0       0.0     -70.3
 A   179.26   16632.5    -266.9       0.0       0.0    -266.9
create PNG graph output by hand
$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|165.399
filing status (MARS) | weighted count of filing units
1|87.385
2|68.234
4|9.781
weighted count of those with NEGATIVE MTR
21.707
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|30.994|0.0
0|2.586|7.18
1|58.614|14.14
2|36.489|25.47
3|14.091|32.21
4|0.798|43.4
5|0.102|55.2
6|0.017|66.73
