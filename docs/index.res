index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.6      -6.1      20.9       0.0      14.8
 1    17.19     500.1      -8.0      44.1       0.0      36.1
 2    17.19     664.2      -2.9      51.7       0.0      48.8
 3    17.19     829.5       1.1      68.5       0.0      69.6
 4    17.19    1030.5       7.6      86.7       0.0      94.3
 5    17.19    1273.3      16.6     103.9       0.0     120.5
 6    17.19    1596.8      40.5     137.6       0.0     178.1
 7    17.19    2044.5      81.2     183.3       0.0     264.5
 8    17.19    2821.3     176.9     263.2       0.0     440.1
 9    17.19    6369.3    1023.3     476.3       0.0    1499.7
 A   171.93   17325.2    1330.2    1436.2       0.0    2766.4

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.6      -1.7       0.0       0.0      -1.7
 1    17.19     500.1      -7.0       0.0       0.0      -7.0
 2    17.19     664.2      -8.3       0.0       0.0      -8.3
 3    17.19     829.5     -10.9       0.0       0.0     -10.9
 4    17.19    1030.5     -15.1       0.0       0.0     -15.1
 5    17.19    1273.3     -21.4       0.0       0.0     -21.4
 6    17.19    1596.8     -29.0       0.0       0.0     -29.0
 7    17.19    2044.5     -39.0       0.0       0.0     -39.0
 8    17.19    2821.3     -63.0       0.0       0.0     -63.0
 9    17.19    6369.3     -86.9       0.0       0.0     -86.9
 A   171.93   17325.2    -282.3       0.0       0.0    -282.3
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
