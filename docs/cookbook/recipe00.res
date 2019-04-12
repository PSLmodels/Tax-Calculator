
REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default growth assumptions
Response Growth-Difference Assumption Values by Year:
none: using default growth assumptions
Policy Reform Parameter Values by Year:
2020:
 II_em : 1000.0
  name: Personal and dependent exemption amount
  desc: Subtracted from AGI in the calculation of taxable income, per taxpayer
        and dependent.
  baseline_value: 0.0
 II_rt5 : 0.36
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 5
  desc: The third highest tax rate, applied to the portion of taxable income
        below tax bracket 5 and above tax bracket 4.
  baseline_value: 0.32
 II_rt6 : 0.39
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 6
  desc: The second higher tax rate, applied to the portion of taxable income
        below tax bracket 6 and above tax bracket 5.
  baseline_value: 0.35
 II_rt7 : 0.41
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 7
  desc: The tax rate applied to the portion of taxable income below tax
        bracket 7 and above tax bracket 6.
  baseline_value: 0.37
 PT_rt5 : 0.36
  name: Pass-through income tax rate 5
  desc: The third highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 5
        and above tax bracket 4.
  baseline_value: 0.32
 PT_rt6 : 0.39
  name: Pass-through income tax rate 6
  desc: The second higher tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 6
        and above tax bracket 5.
  baseline_value: 0.35
 PT_rt7 : 0.41
  name: Pass-through income tax rate 7
  desc: The highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 7
        and above tax bracket 6.
  baseline_value: 0.37

2020_CLP_itax_rev($B)= 1447.348
2020_REF_itax_rev($B)= 1443.743

CLP diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        12109.411
Itemizers (#m)                     32.050
Itemized Deduction ($b)           902.537
Standard Deduction Filers (#m)    135.470
Standard Deduction ($b)          2420.211
Personal Exemption ($b)             0.000
Taxable Income ($b)              9272.044
Regular Tax ($b)                 1606.637
AMT Income ($b)                 11474.939
AMT Liability ($b)                  1.405
AMT Filers (#m)                     0.280
Tax before Credits ($b)          1608.042
Refundable Credits ($b)            77.664
Nonrefundable Credits ($b)         94.005
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                   10.974
Ind Income Tax ($b)              1447.348
Payroll Taxes ($b)               1323.691
Combined Liability ($b)          2771.039
With Income Tax <= 0 (#m)          59.970
With Combined Tax <= 0 (#m)        38.980

REF diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        12109.411
Itemizers (#m)                     31.970
Itemized Deduction ($b)           900.224
Standard Deduction Filers (#m)    135.540
Standard Deduction ($b)          2421.571
Personal Exemption ($b)           333.334
Taxable Income ($b)              9019.038
Regular Tax ($b)                 1600.587
AMT Income ($b)                 11476.890
AMT Liability ($b)                  1.397
AMT Filers (#m)                     0.290
Tax before Credits ($b)          1601.985
Refundable Credits ($b)            80.415
Nonrefundable Credits ($b)         88.801
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                   10.974
Ind Income Tax ($b)              1443.743
Payroll Taxes ($b)               1323.691
Combined Liability ($b)          2767.434
With Income Tax <= 0 (#m)          62.220
With Combined Tax <= 0 (#m)        39.300

Extract of 2020 distribution table by baseline expanded-income decile:
        funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0-10n         0.05      0.007      0.007            -14.435            -14.435
0-10z         0.93      0.000      0.000             -0.000             -0.000
0-10p        15.77     -4.224     -4.588            176.333            176.697
10-20        16.75     -1.588     -2.657            415.040            416.109
20-30        16.75      3.706      2.464            553.009            554.251
30-40        16.75     10.033      8.338            681.747            683.442
40-50        16.75     19.472     17.108            839.630            841.993
50-60        16.75     33.183     30.100           1032.450           1035.533
60-70        16.75     62.473     58.499           1270.002           1273.976
70-80        16.75    108.590    103.219           1594.096           1599.467
80-90        16.75    218.186    209.884           2126.428           2134.730
90-100       16.75    997.510   1021.368           4384.605           4360.747
ALL         167.51   1447.348   1443.743          13058.905          13062.510
90-95         8.38    218.019    213.730           1454.483           1458.772
95-99         6.70    333.136    331.816           1692.273           1693.593
Top 1%        1.68    446.355    475.822           1237.848           1208.382

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.05         0.000           4.5                  0.0
0-10z         0.93         0.000           0.0                  0.0
0-10p        15.77        -0.364         -23.1                  0.2
10-20        16.75        -1.069         -63.8                  0.3
20-30        16.75        -1.242         -74.2                  0.2
30-40        16.75        -1.694        -101.2                  0.2
40-50        16.75        -2.363        -141.1                  0.3
50-60        16.75        -3.083        -184.1                  0.3
60-70        16.75        -3.974        -237.2                  0.3
70-80        16.75        -5.371        -320.6                  0.3
80-90        16.75        -8.302        -495.6                  0.4
90-100       16.75        23.858        1424.2                 -0.5
ALL         167.51        -3.604         -21.5                  0.0
90-95         8.38        -4.289        -512.1                  0.3
95-99         6.70        -1.320        -197.0                  0.1
Top 1%        1.68        29.466       17578.2                 -2.4
