You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default baseline growth assumptions
Policy Reform Parameter Values by Year:
2018:
 _AMT_rt1 : 0.0
  name: AMT rate 1
  desc: The tax rate applied to the portion of AMT taxable income below the
        surtax threshold, AMT bracket 1.
  baseline_value: 0.26
 _AMT_rt2 : 0.0
  name: Additional AMT rate for AMT taxable income above AMT bracket 1
  desc: The additional tax rate applied to the portion of AMT income above the
        AMT bracket 1.
  baseline_value: 0.02
 _II_rt5 : 0.35
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 5
  desc: The third highest tax rate, applied to the portion of taxable income
        below tax bracket 5 and above tax bracket 4.
  baseline_value: 0.33
 _II_rt6 : 0.37
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 6
  desc: The second higher tax rate, applied to the portion of taxable income
        below tax bracket 6 and above tax bracket 5.
  baseline_value: 0.35
 _II_rt7 : 0.42
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 7
  desc: The tax rate applied to the portion of taxable income below tax
        bracket 7 and above tax bracket 6.
  baseline_value: 0.396
 _PT_rt5 : 0.35
  name: Pass-through income tax rate 5
  desc: The third highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S corporations below tax bracket 5
        and above tax bracket 4.
  baseline_value: 0.33
 _PT_rt6 : 0.37
  name: Pass-through income tax rate 6
  desc: The second higher tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S corporations below tax bracket 6
        and above tax bracket 5.
  baseline_value: 0.35
 _PT_rt7 : 0.42
  name: Pass-through income tax rate 7
  desc: The highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S corporations below tax bracket 7
        and above tax bracket 6.
  baseline_value: 0.396

2018_CLP_itax_rev($B)= 1287.51
2018_REF_itax_rev($B)= 1283.12

CLP diagnostic table for 2018:
                                     2018
Returns (#m)                       169.89
AGI ($b)                        10,503.83
Itemizers (#m)                      67.99
Itemized Deduction ($b)          1,500.94
Standard Deduction Filers (#m)      83.86
Standard Deduction ($b)            771.37
Personal Exemption ($b)          1,222.60
Taxable Income ($b)              7,421.92
Regular Tax ($b)                 1,369.71
AMT Income ($b)                  9,664.54
AMT Liability ($b)                  18.02
AMT Filers (#m)                      4.22
Tax before Credits ($b)          1,387.73
Refundable Credits ($b)             76.61
Nonrefundable Credits ($b)          32.93
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.32
Ind Income Tax ($b)              1,287.51
Payroll Taxes ($b)               1,233.56
Combined Liability ($b)          2,521.07
With Income Tax <= 0 (#m)           72.00
With Combined Tax <= 0 (#m)         48.60

REF diagnostic table for 2018:
                                     2018
Returns (#m)                       169.89
AGI ($b)                        10,503.83
Itemizers (#m)                      68.03
Itemized Deduction ($b)          1,501.75
Standard Deduction Filers (#m)      83.82
Standard Deduction ($b)            771.17
Personal Exemption ($b)          1,222.60
Taxable Income ($b)              7,421.27
Regular Tax ($b)                 1,383.33
AMT Income ($b)                  9,665.24
AMT Liability ($b)                   0.00
AMT Filers (#m)                       nan
Tax before Credits ($b)          1,383.33
Refundable Credits ($b)             76.62
Nonrefundable Credits ($b)          32.91
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.32
Ind Income Tax ($b)              1,283.12
Payroll Taxes ($b)               1,233.56
Combined Liability ($b)          2,516.68
With Income Tax <= 0 (#m)           72.03
With Combined Tax <= 0 (#m)         48.62

Extract of 2018 income-tax difference table by expanded-income decile:
    funits(#m)  total_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0        16.99            0.00          0.00                 0.00
1        16.99           -0.00         -0.16                 0.00
2        16.99           -0.01         -0.64                 0.00
3        16.99           -0.03         -1.56                 0.01
4        16.99           -0.06         -3.57                 0.01
5        16.99           -0.08         -4.89                 0.01
6        16.99           -0.06         -3.31                 0.01
7        16.99           -0.08         -4.65                 0.01
8        16.99           -0.11         -6.36                 0.01
9        16.99           -3.96       -233.19                 0.21
10      169.89           -4.39           nan                  nan
11        8.49           -0.35        -40.65                 0.03
12        6.79           -7.43     -1,093.70                 0.47
13        1.70            3.82      2,243.60                 0.07
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively
