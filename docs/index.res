index.res
$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     192.5      -6.1      20.5       0.0      14.4
 1    17.19     492.0      -8.5      44.1       0.0      35.7
 2    17.19     655.0      -3.9      50.5       0.0      46.6
 3    17.19     817.2       0.1      67.5       0.0      67.6
 4    17.19    1016.9       6.6      86.8       0.0      93.4
 5    17.19    1260.2      15.8     103.5       0.0     119.3
 6    17.19    1583.5      40.2     136.7       0.0     177.0
 7    17.19    2031.1      80.3     181.3       0.0     261.6
 8    17.19    2805.0     173.4     258.7       0.0     432.1
 9    17.19    6288.3    1010.8     469.0       0.0    1479.8
 A   171.93   17141.7    1308.9    1418.8       0.0    2727.6

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     192.5      -1.6       0.0       0.0      -1.6
 1    17.19     492.0      -6.9       0.0       0.0      -6.9
 2    17.19     655.0      -8.0       0.0       0.0      -8.0
 3    17.19     817.2     -10.8       0.0       0.0     -10.8
 4    17.19    1016.9     -15.0       0.0       0.0     -15.0
 5    17.19    1260.2     -21.4       0.0       0.0     -21.4
 6    17.19    1583.5     -29.0       0.0       0.0     -29.0
 7    17.19    2031.1     -38.7       0.0       0.0     -38.7
 8    17.19    2805.0     -62.2       0.0       0.0     -62.2
 9    17.19    6288.3     -70.9       0.0       0.0     -70.9
 A   171.93   17141.7    -264.5       0.0       0.0    -264.5
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
