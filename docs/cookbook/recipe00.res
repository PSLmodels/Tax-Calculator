You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2014.

REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default baseline growth assumptions
Policy Reform Parameter Values by Year:
2018:
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
 _STD : [12000, 24000, 12000, 18000, 24000]
        ['single', 'joint', 'separate', 'headhousehold', 'widow']
  name: Standard deduction amount
  desc: Amount filing unit can use as a standard deduction.
  baseline_value: [6492.88, 12985.75, 6492.88, 9560.38, 12985.75]
 _STD_Aged : [0, 0, 0, 0, 0]
             ['single', 'joint', 'separate', 'headhousehold', 'widow']
  name: Additional standard deduction for blind and aged
  desc: To get the standard deduction for aged or blind individuals, taxpayers
        need to add this value to regular standard deduction.
  baseline_value: [1584.88, 1278.13, 1278.13, 1584.88, 1584.88]
 _STD_Dep : 0
  name: Standard deduction for dependents
  desc: This is the maximum standard deduction for dependents.
  baseline_value: 1073.63

2018_CLP_itax_rev($B)= 1287.51
2018_REF_itax_rev($B)= 1234.66

******** EXPANDED_INCOME IS SAME ********

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
Itemizers (#m)                      34.58
Itemized Deduction ($b)          1,010.91
Standard Deduction Filers (#m)     117.28
Standard Deduction ($b)          1,958.91
Personal Exemption ($b)          1,222.60
Taxable Income ($b)              6,993.08
Regular Tax ($b)                 1,317.86
AMT Income ($b)                  9,945.40
AMT Liability ($b)                  16.87
AMT Filers (#m)                      4.40
Tax before Credits ($b)          1,334.73
Refundable Credits ($b)             81.41
Nonrefundable Credits ($b)          27.99
Reform Surtaxes ($b)                 0.00
Other Taxes ($b)                     9.32
Ind Income Tax ($b)              1,234.66
Payroll Taxes ($b)               1,233.56
Combined Liability ($b)          2,468.22
With Income Tax <= 0 (#m)           79.01
With Combined Tax <= 0 (#m)         49.54

Extract of 2018 distribution tables by baseline expanded-income decile:
    funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0        16.99      -1.65      -1.65              -5.30              -5.31
1        16.99     -12.65     -12.82             168.67             168.85
2        16.99     -15.20     -17.23             287.66             289.69
3        16.99     -12.74     -17.18             402.40             406.84
4        16.99       2.69      -4.50             520.45             527.65
5        16.99      27.14      17.77             665.73             675.10
6        16.99      63.42      50.65             861.52             874.29
7        16.99     119.61     107.46           1,153.42           1,165.57
8        16.99     212.26     201.22           1,629.28           1,640.32
9        16.99     904.62     910.94           3,599.33           3,593.01
10      169.89   1,287.51   1,234.66           9,283.16           9,336.02
11        8.49     200.80     197.05           1,150.22           1,153.97
12        6.79     318.15     317.48           1,386.68           1,387.35
13        1.70     385.67     396.41           1,062.43           1,051.69
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively

Extract of 2018 income-tax difference table by expanded-income decile:
    funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0        16.99          0.00          0.27                 0.09
1        16.99         -0.17        -10.24                 0.10
2        16.99         -2.03       -119.71                 0.71
3        16.99         -4.43       -260.96                 1.10
4        16.99         -7.19       -423.46                 1.38
5        16.99         -9.37       -551.70                 1.41
6        16.99        -12.77       -751.77                 1.48
7        16.99        -12.15       -715.03                 1.05
8        16.99        -11.05       -650.18                 0.68
9        16.99          6.32        371.95                -0.18
10      169.89        -52.85       -311.09                 0.57
11        8.49         -3.75       -441.16                 0.33
12        6.79         -0.67        -98.94                 0.05
13        1.70         10.74      6,315.38                -1.01
Note: deciles are numbered 0-9 with top decile divided into bottom 5%,
      next 4%, and top 1%, in the lines numbered 11-13, respectively
