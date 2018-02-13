You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.

REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default baseline growth assumptions
Policy Reform Parameter Values by Year:
2020:
 _II_em : 1000
  name: Personal and dependent exemption amount
  desc: Subtracted from AGI in the calculation of taxable income, per taxpayer
        and dependent.
  baseline_value: 0.0
 _II_rt5 : 0.36
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 5
  desc: The third highest tax rate, applied to the portion of taxable income
        below tax bracket 5 and above tax bracket 4.
  baseline_value: 0.32
 _II_rt6 : 0.39
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 6
  desc: The second higher tax rate, applied to the portion of taxable income
        below tax bracket 6 and above tax bracket 5.
  baseline_value: 0.35
 _II_rt7 : 0.41
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 7
  desc: The tax rate applied to the portion of taxable income below tax
        bracket 7 and above tax bracket 6.
  baseline_value: 0.37
 _PT_rt5 : 0.36
  name: Pass-through income tax rate 5
  desc: The third highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 5
        and above tax bracket 4.
  baseline_value: 0.32
 _PT_rt6 : 0.39
  name: Pass-through income tax rate 6
  desc: The second higher tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 6
        and above tax bracket 5.
  baseline_value: 0.35
 _PT_rt7 : 0.41
  name: Pass-through income tax rate 7
  desc: The highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 7
        and above tax bracket 6.
  baseline_value: 0.37

2020_CLP_itax_rev($B)= 1178.30
2020_REF_itax_rev($B)= 1170.16

CLP diagnostic table:
                                     2020
Returns (#m)                       174.51
AGI ($b)                        10,957.82
Itemizers (#m)                      30.33
Itemized Deduction ($b)            855.21
Standard Deduction Filers (#m)     125.68
Standard Deduction ($b)          2,252.26
Personal Exemption ($b)              0.00
Taxable Income ($b)              8,195.37
Regular Tax ($b)                 1,364.44
AMT Income ($b)                 10,356.83
AMT Liability ($b)                   1.78
AMT Filers (#m)                      0.45
Tax before Credits ($b)          1,366.22
Refundable Credits ($b)             96.03
Nonrefundable Credits ($b)         101.09
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.20
Ind Income Tax ($b)              1,178.30
Payroll Taxes ($b)               1,300.25
Combined Liability ($b)          2,478.55
With Income Tax <= 0 (#m)           77.09
With Combined Tax <= 0 (#m)         50.91

REF diagnostic table:
                                     2020
Returns (#m)                       174.51
AGI ($b)                        10,957.82
Itemizers (#m)                      30.16
Itemized Deduction ($b)            850.47
Standard Deduction Filers (#m)     125.84
Standard Deduction ($b)          2,255.19
Personal Exemption ($b)            303.70
Taxable Income ($b)              7,960.03
Regular Tax ($b)                 1,354.10
AMT Income ($b)                 10,360.56
AMT Liability ($b)                   1.74
AMT Filers (#m)                      0.47
Tax before Credits ($b)          1,355.84
Refundable Credits ($b)             98.87
Nonrefundable Credits ($b)          96.01
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.20
Ind Income Tax ($b)              1,170.16
Payroll Taxes ($b)               1,300.25
Combined Liability ($b)          2,470.42
With Income Tax <= 0 (#m)           79.35
With Combined Tax <= 0 (#m)         51.30

Extract of 2020 distribution table by baseline expanded-income decile:
    funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0        17.45      -8.02      -8.02              72.44              72.44
1        17.45     -14.80     -15.32             320.94             321.47
2        17.45     -11.13     -12.11             463.97             464.94
3        17.45      -2.19      -3.64             596.79             598.23
4        17.45       9.68       7.64             748.71             750.75
5        17.45      29.95      26.76             934.72             937.92
6        17.45      58.99      54.94           1,176.49           1,180.53
7        17.45     101.44      96.61           1,500.69           1,505.51
8        17.45     187.73     179.50           2,014.19           2,022.42
9        17.45     826.65     843.80           4,113.39           4,096.24
10      174.51   1,178.30   1,170.16          11,942.33          11,950.46
11        8.73     178.31     173.73           1,371.04           1,375.62
12        6.98     274.86     272.80           1,610.61           1,612.68
13        1.75     373.47     397.27           1,131.74           1,107.94
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively

Extract of 2020 income-tax difference table by expanded-income decile:
    funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0        17.45         -0.00         -0.04                 0.00
1        17.45         -0.52        -30.05                 0.16
2        17.45         -0.98        -55.91                 0.21
3        17.45         -1.45        -82.85                 0.24
4        17.45         -2.04       -117.00                 0.27
5        17.45         -3.19       -183.07                 0.34
6        17.45         -4.05       -231.90                 0.34
7        17.45         -4.82       -276.27                 0.32
8        17.45         -8.23       -471.65                 0.41
9        17.45         17.15        982.66                -0.42
10      174.51         -8.13        -46.60                 0.07
11        8.73         -4.58       -524.71                 0.33
12        6.98         -2.07       -296.25                 0.13
13        1.75         23.80     13,634.71                -2.10
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively
