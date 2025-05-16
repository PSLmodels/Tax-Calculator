# TCJA after 2025

Many provisions of the TCJA are temporary and are scheduled to end
after 2025 under current-law policy.  Tax policy parameters that are
associated with expiring provisions and that are not inflation indexed
will revert to their 2017 values in 2026.  Tax policy parameters that
are associated with expiring provisions and that are inflation indexed
will revert to their 2017 values indexed to 2026 using a chained CPI-U
inflation factor.  For a list of the ending TCJA provisions, see this
Congressional Research Service document: [Reference Table: Expiring
Provisions in the "Tax Cuts and Jobs Act" (TCJA, P.L. 115-97)](
https://crsreports.congress.gov/product/pdf/R/R47846), which is dated
November 21, 2023.

This document provides examples of using the PSLmodels Tax-Calculator
command-line-interface tool
[tc](https://taxcalc.pslmodels.org/guide/cli.html) with the newer
`tmd.csv` file generated in the PSLmodels
[tax-microdata](https://github.com/PSLmodels/tax-microdata-benchmarking)
repository.  The `tmd` data and weights are based on the 2015 IRS/SOI
PUF data and on recent CPS data, and therefore, are the best data to
use with Tax-Calculator.  All the examples assume you have the [three
`tmd` data
files](https://taxcalc.pslmodels.org/usage/data.html#irs-public-use-data-tmd-csv)
in the parent directory of your working directory.  The `tmd` data
contain information on 225,256 tax filing units.

Before reading the rest of this document, be sure you understand how
to use the Tax-Calculator command-line tool
[tc](https://taxcalc.pslmodels.org/guide/cli.html), particularly the
`--baseline` and `--reform` command-line options.  For complete and
up-to-date `tc` documentation, enter `tc --help` at the command
prompt.  Omitting the `--baseline` option means the baseline policy is
current-law policy.  Omitting the `--reform` option means the reform
policy is current-law policy.  The `--tables` option produces two
tables in one file: the top table contains aggregate and income decile
estimates under the reform and the bottom table contains estimates of
reform-minus-baseline differences by income decile and in aggregate.

Nobody knows how the 2025 tax legislation will turn out, so the idea
of this document is to illustrate how to use the Tax-Calculator CLI
tool to analyze some of the TCJA revisions that were being reported in
the press in early May 2025.  The basic legislative goal is to extend
TCJA beyond 2025, but there is discussion of a number of **revisions**
to the basic extension.  The revisions being discussed include, but
are not limited to, raising the SALT deduction cap, making social
security benefits nontaxable, and liberalizing the child tax credit.
(Given the nature of the reconciliation rules under which the
legislation is being developed, no changes in social security
financing can be made, so there is discussion of a higher
elderly/disability standard deduction amount to proxy the nontaxable
social security benefits revision.)
These revisions all cause reductions in income tax revenue, so there
is also discussion about **enhancements** to the extended-TCJA policy
that would raise revenue to pay for revisions.  The enhancement
considered here is the one that adds a new top income tax bracket with
a 39.6 percent marginal tax rate.

The analysis examples below focus on the following policy scenarios:

1. a strict extension of TCJA without any revisions or enhancements
2. a TCJA extension with the nontaxable social security benefits revision
3. a TCJA extension with the higher elderly/disabled standard deduction revision
4. a TCJA extension with the higher elderly/disabled standard deduction revision and the new top tax bracket enhancement

All the examples use Tax-Calculator 4.6.2 version.
```
% tc --version
Tax-Calculator 4.6.2 on Python 3.12
```

The examples below were done on an ancient Mac with an old Intel
processor with four CPU cores.  The execution times on newer computers
should be substantially less than shown below.  In all the examples,
each `tc` run is using just one CPU core.

The
[`ext.json`](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/ext.json)
reform file is used all the examples.  See the section at the end of
this document for more information on `ext.json` contents.


## 1. TCJA extension without any revisions or enhancements

```
% tc ../tmd.csv 2026 --numyears 10 --reform ext.json --exact --tables
Read input data for 2021; input data were extrapolated to 2026
Write tabular output to file tmd-26-#-ext-#-tables.text
Advance input data and policy to 2027
Write tabular output to file tmd-27-#-ext-#-tables.text
Advance input data and policy to 2028
Write tabular output to file tmd-28-#-ext-#-tables.text
Advance input data and policy to 2029
Write tabular output to file tmd-29-#-ext-#-tables.text
Advance input data and policy to 2030
Write tabular output to file tmd-30-#-ext-#-tables.text
Advance input data and policy to 2031
Write tabular output to file tmd-31-#-ext-#-tables.text
Advance input data and policy to 2032
Write tabular output to file tmd-32-#-ext-#-tables.text
Advance input data and policy to 2033
Write tabular output to file tmd-33-#-ext-#-tables.text
Advance input data and policy to 2034
Write tabular output to file tmd-34-#-ext-#-tables.text
Advance input data and policy to 2035
Write tabular output to file tmd-35-#-ext-#-tables.text
Execution time is 56.8 seconds
```

Because the aggregate change in taxes is displayed on the last line of
the tables file (in column four), we can look at the ten changes like
this:

```
% tail -1 tmd-??-#-ext-#-tables.text
==> tmd-26-#-ext-#-tables.text <==
 A   192.41   20828.3    -284.1       0.0       0.0    -284.1

==> tmd-27-#-ext-#-tables.text <==
 A   193.77   21613.4    -291.8       0.0       0.0    -291.8

==> tmd-28-#-ext-#-tables.text <==
 A   194.72   22404.7    -299.6       0.0       0.0    -299.6

==> tmd-29-#-ext-#-tables.text <==
 A   195.66   23243.3    -291.9       0.0       0.0    -291.9

==> tmd-30-#-ext-#-tables.text <==
 A   196.58   24115.1    -299.9       0.0       0.0    -299.9

==> tmd-31-#-ext-#-tables.text <==
 A   197.48   25020.0    -307.9       0.0       0.0    -307.9

==> tmd-32-#-ext-#-tables.text <==
 A   198.35   25952.7    -315.9       0.0       0.0    -315.9

==> tmd-33-#-ext-#-tables.text <==
 A   199.21   26905.4    -323.8       0.0       0.0    -323.8

==> tmd-34-#-ext-#-tables.text <==
 A   200.03   27878.9    -331.7       0.0       0.0    -331.7

==> tmd-35-#-ext-#-tables.text <==
 A   200.83   28883.0    -339.7       0.0       0.0    -339.7
```

And the ten-year change in aggregate federal income tax liability can
be tabulated this way:

```
% tail -1 tmd-??-#-ext-#-tables.text | awk '$1~/A/{n++;c+=$4}END{print n,c}'
10 -3086.3
```


## 2. TCJA extension with the nontaxable social security benefits revision

There is some discussion of exempting all social security benefits
from federal income taxation.  Here is a JSON file that implements
that reform:

```
% cat no_ssben_tax.json 
{
    "SS_percentage1": {"2026": 0.0},
    "SS_percentage2": {"2026": 0.0}
}
```

The marginal effect of adding that reform on to the TCJA-extension can be
estimated in this 2026 run:

```
% tc ../tmd.csv 2026 --baseline ext.json --reform ext.json+no_ssben_tax.json --exact --tables 
Read input data for 2021; input data were extrapolated to 2026
Write tabular output to file tmd-26-ext-ext+no_ssben_tax-#-tables.text
Execution time is 33.4 seconds

% tail -1 tmd-26-ext-ext+no_ssben_tax-#-tables.text
 A   192.41   20828.3    -110.7       0.0       0.0    -110.7
```

So, this reform reduces federal income tax liability by $110.7 billion in
2026.


## 3. TCJA extension with the higher elderly/disabled standard deduction revision

Next we find a reform that approximates the `no_ssben_tax` reform
analyzed in the previous section.  Trying higher values for the
`STD_Aged` parameter, we quickly find that $31,500 for all filing
statuses produces a reasonable approximation of the effects of the
`no_ssben_tax` reform.

```
% cat higher_aged_std.json 
{
    "STD_Aged": {"2026": [31500, 31500, 31500, 31500, 31500]}
}

% tc ../tmd.csv 2026 --baseline ext.json --reform ext.json+higher_aged_std.json --exact --tables
Read input data for 2021; input data were extrapolated to 2026
Write tabular output to file tmd-26-ext-ext+higher_aged_std-#-tables.text
Execution time is 32.4 seconds

% diff tmd-26-ext-ext+higher_aged_std-#-tables.text tmd-26-ext-ext+no_ssben_tax-#-tables.text | tail -18
22,29c22,29
<  3    19.24     629.1      -0.4       0.0       0.0      -0.4
<  4    19.24     876.9      -1.9       0.0       0.0      -1.9
<  5    19.24    1173.0      -6.9       0.0       0.0      -6.9
<  6    19.25    1581.6     -13.4       0.0       0.0     -13.4
<  7    19.24    2191.6     -25.6       0.0       0.0     -25.6
<  8    19.24    3238.1     -33.2       0.0       0.0     -33.2
<  9    19.24   10787.1     -29.5       0.0       0.0     -29.5
<  A   192.41   20828.3    -111.1       0.0       0.0    -111.1
---
>  3    19.24     629.1      -0.1       0.0       0.0      -0.1
>  4    19.24     876.9      -1.0       0.0       0.0      -1.0
>  5    19.24    1173.0      -4.9       0.0       0.0      -4.9
>  6    19.25    1581.6     -11.9       0.0       0.0     -11.9
>  7    19.24    2191.6     -21.3       0.0       0.0     -21.3
>  8    19.24    3238.1     -29.9       0.0       0.0     -29.9
>  9    19.24   10787.1     -41.5       0.0       0.0     -41.5
>  A   192.41   20828.3    -110.7       0.0       0.0    -110.7
```


## 4. TCJA extension with the higher elderly/disabled standard deduction revision and the new top tax bracket enhancement

In this last example, we look at how much of the extra cost of the
`higher_aged_std` reform can be paid for by adding a new top income
tax bracket to the TCJA-extension reform.

```
(taxcalc-dev) Tax-Calculator% cat new_top_bracket.json
{
    "II_brk7": {"2026": [2.5e6, 5.0e6, 2.5e6, 4.2e6, 5.0e6]},
    "II_rt8": {"2026": 0.396},
    "PT_brk7": {"2026": [2.5e6, 5.0e6, 2.5e6, 4.2e6, 5.0e6]},
    "PT_rt8": {"2026": 0.396}
}

% tc ../tmd.csv 2026 --baseline ext.json+higher_aged_std.json --reform ext.json+higher_aged_std.json+new_top_bracket.json --exact --tables --graphs
Read input data for 2021; input data were extrapolated to 2026
Write tabular output to file tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Write graphical output to file tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-pch.html
Write graphical output to file tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-atr.html
Write graphical output to file tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-mtr.html
Execution time is 39.8 seconds

% tail -14 tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    19.24    -274.9       0.1       0.0       0.0       0.1
 1    19.24     210.9       0.0       0.0       0.0       0.0
 2    19.24     414.9       0.0       0.0       0.0       0.0
 3    19.24     629.1       0.0       0.0       0.0       0.0
 4    19.24     876.9       0.0       0.0       0.0       0.0
 5    19.24    1173.0       0.0       0.0       0.0       0.0
 6    19.25    1581.6       0.0       0.0       0.0       0.0
 7    19.24    2191.6       0.0       0.0       0.0       0.0
 8    19.24    3238.1       0.0       0.0       0.0       0.0
 9    19.24   10787.1      15.8       0.0       0.0      15.8
 A   192.41   20828.3      15.8       0.0       0.0      15.8
```

So, the new top bracket (with a 39.6% marginal tax rate) raises
aggregate federal income tax liability by enough to pay for the TCJA
revision that approximates making social security benefits tax-free
and produces an additional $15.8 billion (in 2026) that could be used
to pay for other revisions.

While those with the highest incomes do pay more tax, the reduction in
their after-tax expanded income is quite small as can be seen in one
of the standard graphs:
`tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-pch.html`.
This graph shows that the top one percent of the income distribution
experiences a decline in after-tax income of about 0.36 percent (or
less than four dollars per thousand dollars).

Here are the ten-year results for this run:

```
% tc ../tmd.csv 2026 --numyears 10 --baseline ext.json+higher_aged_std.json --reform ext.json+higher_aged_std.json+new_top_bracket.json --exact --tables
Read input data for 2021; input data were extrapolated to 2026
Write tabular output to file tmd-26-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2027
Write tabular output to file tmd-27-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2028
Write tabular output to file tmd-28-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2029
Write tabular output to file tmd-29-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2030
Write tabular output to file tmd-30-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2031
Write tabular output to file tmd-31-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2032
Write tabular output to file tmd-32-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2033
Write tabular output to file tmd-33-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2034
Write tabular output to file tmd-34-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Advance input data and policy to 2035
Write tabular output to file tmd-35-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text
Execution time is 57.1 seconds

% tail -1 tmd-??-ext+higher_aged_std-ext+higher_aged_std+new_top_bracket-#-tables.text | awk '$1~/A/{n++;c+=$4}END{print n,c}'
10 187.9
```

So, there is nearly $188 billion left to pay for other revisions to
the basic TCJA extension.


## How is the `ext.json` file generated?

The short answer is by using the
[`extend_tcja.py`](https://github.com/PSLmodels/Tax-Calculator/blob/master/extend_tcja.py) script.

Reading the `extend_tcja.py` script will provide details on how the
values in the `ext.json` file are generated.

It is important to bear in mind that the `extend_tcja.py` script will
generate a different `ext.json` file whenever the CBO economic
projection (incorporated in the Tax-Calculator `growfactors.csv` file)
changes or whenever new historical values of policy parameters are
added to the `policy_current_law.json` file thereby changing the
`Policy.LAST_KNOWN_YEAR`.

Beginning with the 4.5.0 version, Tax-Calculator incorporates the
January 2025 CBO economic projection and contains historical tax
policy parameter values through 2025.

