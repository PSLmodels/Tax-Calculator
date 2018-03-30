index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      91.8      -9.0      10.9       0.0       1.9
 1    17.93     378.4     -19.1      29.9       0.0      10.8
 2    17.93     563.7     -18.4      48.9       0.0      30.5
 3    17.93     748.5      -9.3      66.6       0.0      57.3
 4    17.93     965.9       1.9      89.1       0.0      91.0
 5    17.93    1238.7      19.5     115.6       0.0     135.0
 6    17.93    1597.8      48.0     149.8       0.0     197.8
 7    17.93    2084.8      89.6     196.5       0.0     286.2
 8    17.93    2860.1     171.4     271.7       0.0     443.0
 9    17.93    6140.7     888.4     438.6       0.0    1327.0
 A   179.26   16670.3    1163.0    1417.5       0.0    2580.4

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.93      91.8      -0.0       0.0       0.0      -0.0
 1    17.93     378.4      -3.3       0.0       0.0      -3.3
 2    17.93     563.7      -7.0       0.0       0.0      -7.0
 3    17.93     748.5     -10.4       0.0       0.0     -10.4
 4    17.93     965.9     -14.9       0.0       0.0     -14.9
 5    17.93    1238.7     -24.3       0.0       0.0     -24.3
 6    17.93    1597.8     -32.8       0.0       0.0     -32.8
 7    17.93    2084.8     -40.3       0.0       0.0     -40.3
 8    17.93    2860.1     -63.7       0.0       0.0     -63.7
 9    17.93    6140.7     -70.3       0.0       0.0     -70.3
 A   179.26   16670.3    -266.9       0.0       0.0    -266.9
create PNG graph output by hand
$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|165.399
filing status (MARS) | weighted count of filing units
1|87.385
2|68.234
4|9.781
weighted count of those with NEGATIVE MTR
21.708
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|30.993|0.0
0|2.586|7.18
1|58.614|14.14
2|36.492|25.47
3|14.089|32.21
4|0.798|43.4
5|0.102|55.2
6|0.017|66.73
