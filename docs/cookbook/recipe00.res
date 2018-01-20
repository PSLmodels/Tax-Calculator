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

2020_CLP_itax_rev($B)= 1280.12
2020_REF_itax_rev($B)= 1272.53

CLP diagnostic table:
                                     2020
Returns (#m)                       174.51
AGI ($b)                        11,492.77
Itemizers (#m)                      30.21
Itemized Deduction ($b)            843.61
Standard Deduction Filers (#m)     125.80
Standard Deduction ($b)          2,257.60
Personal Exemption ($b)              0.00
Taxable Income ($b)              8,725.23
Regular Tax ($b)                 1,462.90
AMT Income ($b)                 10,904.75
AMT Liability ($b)                   2.13
AMT Filers (#m)                      0.47
Tax before Credits ($b)          1,465.03
Refundable Credits ($b)             92.93
Nonrefundable Credits ($b)         102.59
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                    10.61
Ind Income Tax ($b)              1,280.12
Payroll Taxes ($b)               1,344.74
Combined Liability ($b)          2,624.87
With Income Tax <= 0 (#m)           76.01
With Combined Tax <= 0 (#m)         50.35

REF diagnostic table:
                                     2020
Returns (#m)                       174.51
AGI ($b)                        11,492.77
Itemizers (#m)                      30.06
Itemized Deduction ($b)            839.35
Standard Deduction Filers (#m)     125.95
Standard Deduction ($b)          2,260.35
Personal Exemption ($b)            302.93
Taxable Income ($b)              8,488.61
Regular Tax ($b)                 1,453.17
AMT Income ($b)                 10,908.01
AMT Liability ($b)                   2.07
AMT Filers (#m)                      0.49
Tax before Credits ($b)          1,455.24
Refundable Credits ($b)             95.72
Nonrefundable Credits ($b)          97.59
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                    10.61
Ind Income Tax ($b)              1,272.53
Payroll Taxes ($b)               1,344.74
Combined Liability ($b)          2,617.27
With Income Tax <= 0 (#m)           78.26
With Combined Tax <= 0 (#m)         50.77

Extract of 2020 distribution table by baseline expanded-income decile:
    funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0        17.45      -1.94      -1.94              -4.93              -4.93
1        17.45     -14.47     -14.49             186.06             186.09
2        17.45     -17.92     -18.37             316.40             316.86
3        17.45     -16.83     -17.82             442.67             443.66
4        17.45      -2.82      -4.58             573.63             575.39
5        17.45      21.17      18.32             734.07             736.92
6        17.45      58.67      53.99             949.22             953.90
7        17.45     114.82     109.31           1,271.24           1,276.75
8        17.45     210.70     201.79           1,793.22           1,802.14
9        17.45     928.74     946.33           4,010.69           3,993.11
10      174.51   1,280.12   1,272.53          10,272.28          10,279.87
11        8.73     201.38     196.26           1,269.33           1,274.45
12        6.98     316.53     314.64           1,543.61           1,545.50
13        1.75     410.83     435.43           1,197.76           1,173.16
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively

Extract of 2020 income-tax difference table by expanded-income decile:
    funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0        17.45         -0.00         -0.00                -0.00
1        17.45         -0.03         -1.48                 0.01
2        17.45         -0.46        -26.11                 0.14
3        17.45         -0.99        -56.61                 0.22
4        17.45         -1.76       -100.90                 0.31
5        17.45         -2.85       -163.14                 0.39
6        17.45         -4.68       -268.10                 0.49
7        17.45         -5.51       -315.78                 0.43
8        17.45         -8.91       -510.78                 0.50
9        17.45         17.59      1,007.82                -0.44
10      174.51         -7.59        -43.51                 0.07
11        8.73         -5.12       -587.26                 0.40
12        6.98         -1.89       -270.77                 0.12
13        1.75         24.60     14,097.41                -2.05
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively
