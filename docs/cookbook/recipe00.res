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
0-10p        16.75      -4.79      -4.99             140.04             140.24
10-20        16.75      -6.96      -7.84             366.66             367.53
20-30        16.75      -3.79      -5.08             497.38             498.67
30-40        16.75       5.75       3.98             628.28             630.06
40-50        16.75      19.17      16.74             781.19             783.63
50-60        16.75      42.27      38.73             973.59             977.13
60-70        16.75      73.58      69.33           1,235.28           1,239.53
70-80        16.75     119.16     113.69           1,591.17           1,596.64
80-90        16.75     220.09     212.11           2,180.02           2,188.00
90-100       16.75     948.94     974.11           4,467.12           4,441.96
ALL         167.51   1,413.43   1,410.78          12,860.73          12,863.38
90-95         8.38     212.56     208.76           1,499.54           1,503.34
95-99         6.70     311.41     310.71           1,747.48           1,748.17
Top 1%        1.68     424.97     454.63           1,220.10           1,190.45

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.00          0.00          0.00                  nan
0-10z         0.00          0.00          0.00                  nan
0-10p        16.75         -0.20        -11.99                 0.14
10-20        16.75         -0.87        -52.02                 0.24
20-30        16.75         -1.29        -77.20                 0.26
30-40        16.75         -1.77       -105.71                 0.28
40-50        16.75         -2.44       -145.49                 0.31
50-60        16.75         -3.54       -211.25                 0.36
60-70        16.75         -4.24       -253.25                 0.34
70-80        16.75         -5.47       -326.60                 0.34
80-90        16.75         -7.98       -476.42                 0.37
90-100       16.75         25.16      1,502.02                -0.56
ALL         167.51         -2.65        -15.79                 0.02
90-95         8.38         -3.80       -453.95                 0.25
95-99         6.70         -0.69       -103.08                 0.04
Top 1%        1.68         29.65     17,702.19                -2.43
