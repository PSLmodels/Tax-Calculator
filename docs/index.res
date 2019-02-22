index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     197.2      -6.1      20.9       0.0      14.8
 1    17.19     499.8      -8.0      44.6       0.0      36.5
 2    17.19     663.3      -3.4      50.6       0.0      47.3
 3    17.19     829.2       1.3      68.5       0.0      69.8
 4    17.19    1031.2       7.9      87.0       0.0      94.9
 5    17.19    1274.5      16.8     104.3       0.0     121.0
 6    17.19    1598.3      40.9     137.5       0.0     178.4
 7    17.19    2046.5      81.9     183.5       0.0     265.5
 8    17.19    2822.9     177.6     264.9       0.0     442.5
 9    17.19    6344.1    1017.4     481.3       0.0    1498.7
 A   171.93   17307.0    1326.4    1443.0       0.0    2769.4

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     197.2      -1.7       0.0       0.0      -1.7
 1    17.19     499.8      -7.0       0.0       0.0      -7.0
 2    17.19     663.3      -8.1       0.0       0.0      -8.1
 3    17.19     829.2     -11.0       0.0       0.0     -11.0
 4    17.19    1031.2     -15.2       0.0       0.0     -15.2
 5    17.19    1274.5     -21.5       0.0       0.0     -21.5
 6    17.19    1598.3     -29.0       0.0       0.0     -29.0
 7    17.19    2046.5     -39.0       0.0       0.0     -39.0
 8    17.19    2822.9     -63.2       0.0       0.0     -63.2
 9    17.19    6344.1     -87.1       0.0       0.0     -87.1
 A   171.93   17307.0    -282.7       0.0       0.0    -282.7
create PNG graph output by hand
$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|157.558
filing status (MARS) | weighted count of filing units
1|81.303
2|61.655
4|14.599
weighted count of those with NEGATIVE MTR
15.473
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|26.896|0.0
0|2.606|7.18
1|60.85|14.11
2|37.803|25.54
3|12.804|32.26
4|1.0|43.08
5|0.11|55.74
6|0.015|66.76
