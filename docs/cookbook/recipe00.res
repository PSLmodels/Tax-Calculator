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
0-10p        16.75      -4.25      -4.61             162.91             163.27
10-20        16.75      -1.72      -2.80             413.27             414.35
20-30        16.75       3.49       2.26             551.40             552.63
30-40        16.75       9.90       8.22             679.03             680.72
40-50        16.75      18.88      16.55             836.85             839.18
50-60        16.75      32.45      29.39           1,028.48           1,031.54
60-70        16.75      61.43      57.51           1,263.59           1,267.52
70-80        16.75     106.69     101.38           1,583.96           1,589.27
80-90        16.75     213.76     205.51           2,108.73           2,116.98
90-100       16.75     972.80     997.39           4,309.80           4,285.21
ALL         167.51   1,413.43   1,410.78          12,938.02          12,940.66
90-95         8.38     214.47     210.15           1,438.22           1,442.54
95-99         6.70     327.05     326.02           1,668.49           1,669.52
Top 1%        1.68     431.28     461.22           1,203.09           1,173.15

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.00          0.00          0.00                  nan
0-10z         0.00          0.00          0.00                  nan
0-10p        16.75         -0.37        -21.82                 0.22
10-20        16.75         -1.08        -64.24                 0.26
20-30        16.75         -1.23        -73.54                 0.22
30-40        16.75         -1.68       -100.58                 0.25
40-50        16.75         -2.33       -139.01                 0.28
50-60        16.75         -3.06       -182.61                 0.30
60-70        16.75         -3.93       -234.50                 0.31
70-80        16.75         -5.31       -316.82                 0.34
80-90        16.75         -8.25       -492.52                 0.39
90-100       16.75         24.59      1,467.69                -0.57
ALL         167.51         -2.65        -15.79                 0.02
90-95         8.38         -4.32       -515.68                 0.30
95-99         6.70         -1.03       -153.88                 0.06
Top 1%        1.68         29.94     17,871.04                -2.49
