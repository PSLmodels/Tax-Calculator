index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.0      -6.2      20.9       0.0      14.7
 1    17.19     496.3      -8.2      44.4       0.0      36.2
 2    17.19     660.1      -3.2      51.7       0.0      48.5
 3    17.19     823.6       0.7      67.3       0.0      68.0
 4    17.19    1023.1       7.1      85.5       0.0      92.6
 5    17.19    1264.4      15.9     102.8       0.0     118.7
 6    17.19    1583.8      39.1     135.4       0.0     174.5
 7    17.19    2025.7      78.7     180.4       0.0     259.1
 8    17.19    2791.3     172.0     259.1       0.0     431.2
 9    17.19    6276.2    1012.3     471.2       0.0    1483.5
 A   171.93   17139.6    1308.2    1418.8       0.0    2727.0

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.0      -1.7       0.0       0.0      -1.7
 1    17.19     496.3      -7.0       0.0       0.0      -7.0
 2    17.19     660.1      -8.3       0.0       0.0      -8.3
 3    17.19     823.6     -10.8       0.0       0.0     -10.8
 4    17.19    1023.1     -14.9       0.0       0.0     -14.9
 5    17.19    1264.4     -21.2       0.0       0.0     -21.2
 6    17.19    1583.8     -28.6       0.0       0.0     -28.6
 7    17.19    2025.7     -38.5       0.0       0.0     -38.5
 8    17.19    2791.3     -62.4       0.0       0.0     -62.4
 9    17.19    6276.2     -71.3       0.0       0.0     -71.3
 A   171.93   17139.6    -264.7       0.0       0.0    -264.7
create PNG graph output by hand
$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|157.558
filing status (MARS) | weighted count of filing units
1|81.303
2|61.655
4|14.599
weighted count of those with NEGATIVE MTR
15.338
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|26.649|0.0
0|2.484|7.17
1|60.493|14.14
2|38.317|25.55
3|13.159|32.26
4|0.988|43.15
5|0.113|55.53
6|0.016|66.75
