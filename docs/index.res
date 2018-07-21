index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     161.7      -5.7      14.6       0.0       8.9
 1    17.19     429.0     -12.7      37.4       0.0      24.7
 2    17.19     590.5     -11.6      53.6       0.0      42.0
 3    17.19     760.9      -4.2      70.9       0.0      66.7
 4    17.19     960.9       6.7      90.3       0.0      97.0
 5    17.19    1217.1      23.2     112.6       0.0     135.8
 6    17.19    1565.9      50.1     143.4       0.0     193.5
 7    17.19    2047.6      91.2     187.9       0.0     279.1
 8    17.19    2867.0     180.5     258.0       0.0     438.5
 9    17.19    6393.6     991.4     450.1       0.0    1441.4
 A   171.93   16994.2    1308.9    1418.8       0.0    2727.6

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     161.7      -0.6       0.0       0.0      -0.6
 1    17.19     429.0      -5.5       0.0       0.0      -5.5
 2    17.19     590.5      -8.1       0.0       0.0      -8.1
 3    17.19     760.9     -11.3       0.0       0.0     -11.3
 4    17.19     960.9     -15.4       0.0       0.0     -15.4
 5    17.19    1217.1     -24.0       0.0       0.0     -24.0
 6    17.19    1565.9     -31.7       0.0       0.0     -31.7
 7    17.19    2047.6     -39.8       0.0       0.0     -39.8
 8    17.19    2867.0     -61.5       0.0       0.0     -61.5
 9    17.19    6393.6     -66.5       0.0       0.0     -66.5
 A   171.93   16994.2    -264.5       0.0       0.0    -264.5
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
-1|26.74|0.0
0|2.487|7.16
1|60.446|14.14
2|38.274|25.55
3|13.156|32.26
4|0.988|43.15
5|0.113|55.53
6|0.016|66.75
