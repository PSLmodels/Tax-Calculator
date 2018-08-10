You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
WARNING: Tax-Calculator packages for Python 2.7 will
         no longer be provided beginning in 2019
         because Pandas is stopping development for 2.7
SOLUTION: upgrade to Python 3.6 now
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
WARNING: Tax-Calculator packages for Python 2.7 will
         no longer be provided beginning in 2019
         because Pandas is stopping development for 2.7
SOLUTION: upgrade to Python 3.6 now

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

2020_CLP_itax_rev($B)= 1413.43
2020_REF_itax_rev($B)= 1410.78

CLP diagnostic table:
                                     2020
Returns (#m)                       167.51
AGI ($b)                        11,946.47
Itemizers (#m)                      31.03
Itemized Deduction ($b)            872.79
Standard Deduction Filers (#m)     136.48
Standard Deduction ($b)          2,438.38
Personal Exemption ($b)              0.00
Taxable Income ($b)              9,126.24
Regular Tax ($b)                 1,574.26
AMT Income ($b)                 11,332.09
AMT Liability ($b)                   1.83
AMT Filers (#m)                      0.42
Tax before Credits ($b)          1,576.08
Refundable Credits ($b)             78.60
Nonrefundable Credits ($b)          93.69
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.63
Ind Income Tax ($b)              1,413.43
Payroll Taxes ($b)               1,316.61
Combined Liability ($b)          2,730.03
With Income Tax <= 0 (#m)           60.37
With Combined Tax <= 0 (#m)         39.23

REF diagnostic table:
                                     2020
Returns (#m)                       167.51
AGI ($b)                        11,946.47
Itemizers (#m)                      30.95
Itemized Deduction ($b)            870.48
Standard Deduction Filers (#m)     136.56
Standard Deduction ($b)          2,439.80
Personal Exemption ($b)            327.45
Taxable Income ($b)              8,879.74
Regular Tax ($b)                 1,569.19
AMT Income ($b)                 11,334.04
AMT Liability ($b)                   1.79
AMT Filers (#m)                      0.42
Tax before Credits ($b)          1,570.97
Refundable Credits ($b)             81.35
Nonrefundable Credits ($b)          88.47
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.63
Ind Income Tax ($b)              1,410.78
Payroll Taxes ($b)               1,316.61
Combined Liability ($b)          2,727.39
With Income Tax <= 0 (#m)           62.57
With Combined Tax <= 0 (#m)         39.56

Extract of 2020 distribution table by baseline expanded-income decile:
        funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0-10n         0.00       0.00       0.00               0.00               0.00
0-10z         0.00       0.00       0.00               0.00               0.00
0-10p        16.75      -4.25      -4.61             160.88             161.24
10-20        16.75      -2.01      -3.07             409.93             411.00
20-30        16.75       2.73       1.52             548.16             549.37
30-40        16.75       8.97       7.29             674.04             675.71
40-50        16.75      18.65      16.31             829.91             832.26
50-60        16.75      32.73      29.62           1,022.95           1,026.06
60-70        16.75      62.45      58.48           1,260.75           1,264.71
70-80        16.75     108.36     103.01           1,586.12           1,591.46
80-90        16.75     214.75     206.55           2,120.99           2,129.20
90-100       16.75     971.05     995.68           4,324.82           4,300.19
ALL         167.51   1,413.43   1,410.78          12,938.55          12,941.20
90-95         8.37     213.57     209.30           1,446.38           1,450.66
95-99         6.70     326.10     325.07           1,674.21           1,675.24
Top 1%        1.68     431.38     461.31           1,204.23           1,174.29

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.00          0.00          0.00                  nan
0-10z         0.00          0.00          0.00                  nan
0-10p        16.75         -0.36        -21.37                 0.22
10-20        16.75         -1.06        -63.37                 0.26
20-30        16.75         -1.21        -72.33                 0.22
30-40        16.75         -1.67        -99.85                 0.25
40-50        16.75         -2.34       -139.94                 0.28
50-60        16.75         -3.11       -185.53                 0.30
60-70        16.75         -3.97       -236.87                 0.31
70-80        16.75         -5.34       -319.02                 0.34
80-90        16.75         -8.21       -490.02                 0.39
90-100       16.75         24.63      1,470.33                -0.57
ALL         167.51         -2.65        -15.79                 0.02
90-95         8.37         -4.28       -510.73                 0.30
95-99         6.70         -1.03       -153.84                 0.06
Top 1%        1.68         29.94     17,856.01                -2.49
