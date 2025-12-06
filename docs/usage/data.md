Data for Tax-Calculator
=======================

A Tax-Calculator `Records` object is created by passing a Pandas
DataFrame or a string that provides the path to a CSV file with data
you'd like to use with Tax-Calculator.


## Using prepared data with Tax-Calculator

To make Tax-Calculator more useful out of the box, it includes three
data options for users, two of which (`cps.csv` and `puf.csv`) are
created in the [taxdata
repository](https://github.com/PSLmodels/taxdata), and one of which
(`tmd.csv`) is created in the [tax-microdata
repository](https://github.com/PSLmodels/tax-microdata-benchmarking).
We refer users to those repositories for more specific documentation
of these data, but we provide a brief overview of the three prepared
data options that are compatible with Tax-Calculator.

### Current Population Survey data (`cps.csv`)

Using the `Records.cps_constructor()` method to create a `Records`
class object, Tax-Calculator users will be loading the `taxdata`
Current Population Survey (CPS) data file.  This file is based on
publicly available survey data, which is then weighted in `taxdata` to
hit IRS/SOI targets.  The data are then grown out to hit aggregate
forecasts through the time horizon available in Tax-Calculator
(approximately the next 10 years).  All the files required to use this
prepared data option are included in the Tax-Calculator package.

Tax-Calculator provides unit tests to ensure that certain totals are
hit with the CPS-based file.  However, users should note that these
tests are simply to ensure **the accuracy of Tax-Calculator's tax
logic** and **not the accuracy of the CPS-based data file produced by
`taxdata`**.  Please see the
[taxdata](https://github.com/PSLmodels/taxdata) documentation for any
validation of those data.

### 2011 IRS public use data (`puf.csv`)

The taxdata repository also produces a weights file and growth
factors file for use with the 2011 IRS-SOI Public Use File (PUF).  For
users who have purchased their own version of the 2011 PUF, the `puf.csv`,
`puf_weights.csv.gz` and `puf_ratios.csv` files from the taxdata repository,
can be used by Tax-Calculator using the `Records.puf_constructor(...)`
static method.

We refer users of the PUF to the IRS limitations on the use of those
data and their distribution.  We also refer users of the PUF input
data to the [taxdata](https://github.com/PSLmodels/taxdata)
documentation for details on how to use these files with the PUF and
to see how well the resulting tax calculations hit aggregate targets
published by the IRS.  However, we do note that analysis with a
PUF-based data file tends to be more accurate than the `cps.csv` file
and that the validation of Tax-Calculator with other microsimulation
models uses the `puf.csv` file.

### 2015 IRS public use data (`tmd.csv`)

The [tax-microdata
repository](https://github.com/PSLmodels/tax-microdata-benchmarking)
produces an input variables file (`tmd.csv.gz`), a **national** weights
file (`tmd_weights.csv.gz`), and a variable growth factors file
(`tmd_growfactors.csv`) that can be used with the Tax-Calculator
package beginning with the 3.6.0 release.  The TMD files are available
only to users who have purchased their own version of the 2015 IRS-SOI
PUF.  For those users, the TMD files are available from the
tax-microdata repository.  The three TMD files can be used with
Tax-Calculator in two ways:
  - with the **Python API** by instantiating a GrowFactors object that
    uses TMD growth factors [`gf=GrowFactors("path/to/tmd_growfactors.csv")`]
    and by using the `Records.tmd_constructor(...)` static method to
    instantiate a Records object, or
  - with the **CLI tool**, `tc`, when the three TMD files are all in
    the same folder and the `tmd.csv.gz` file has been unzipped.

The [tax-microdata
repository](https://github.com/PSLmodels/tax-microdata-benchmarking)
also produces state and Congressional district weights files that can
be used to estimate federal taxes for various sub-national areas.  The
easiest way to produce sub-national federal tax estimates is to supply
the **CLI tool** with the value of an environmental variable
(`TMD_AREA`) that indicates the sub-national area.  So, for example,
if you have the New Mexico state weights in the
`nm_tmd_weights.csv.gz` file, put that file in the folder that
contains the three national TMD files described above.  Then, execute
this command for tabular output under 2024 current-law policy:
```
(taxcalc-dev) myruns> TMD_AREA=nm tc tmd.csv 2024 --exact --tables
Read input data for 2021; input data were extrapolated to 2024
Write tabular output to file tmd_nm-24-#-#-#-#.tables
Execution time is 8.2 seconds
(taxcalc-dev) myruns> awk '$1~/Ret/||$1~/A/' tmd_nm-24-#-#-#-#.tables | head -2
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
 A     1.17      87.0       7.2       6.9       0.0      14.1
```

Or for the first Congressional district in New Mexico, put the
`nm01_tmd_weights.csv.gz` file in the folder with the other TMD
files and execute this command:
```
(taxcalc-dev) myruns> TMD_AREA=nm01 tc tmd.csv 2024 --exact --tables
Read input data for 2021; input data were extrapolated to 2024
Write tabular output to file tmd_nm01-24-#-#-#-#.tables
Execution time is 8.3 seconds
(taxcalc-dev) myruns> awk '$1~/Ret/||$1~/A/' tmd_nm01-24-#-#-#-#.tables | head -2
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
 A     0.40      31.9       2.8       2.5       0.0       5.3
```


## Using other data with Tax-Calculator

Using other data sources with Tax-Calculator is possible.  Users can
pass any csv file to the `Records` class and, so long as it has the
appropriate [input
variables](https://taxcalc.pslmodels.org/guide/input_vars.html), one
may be able to obtain results.  Using Tax-Calculator with custom data
takes care and significant understanding of the model and data.  Those
interested in using their own data with Tax-Calculator might also look
to the [Tax-Cruncher](https://github.com/PSLmodels/Tax-Cruncher)
project, which is built as an interface between Tax-Calculator and
custom datasets.
