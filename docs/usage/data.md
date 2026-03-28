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

The taxdata repository also produces an input variables file, weights
file, and ratios file, using the 2011 IRS-SOI Public Use File (PUF).
For users who have purchased from IRS-SOI their own version of the
2011 PUF, the `puf.csv`, `puf_weights.csv.gz` and `puf_ratios.csv`
files from the taxdata repository, can be used by Tax-Calculator using
the `Records.puf_constructor(...)` static method.

We refer users of the PUF to the IRS limitations on the use of those
data and their distribution.  We also refer users of the PUF input
data to the [taxdata](https://github.com/PSLmodels/taxdata)
documentation for details on how to use these files with the PUF and
to see how well the resulting tax calculations hit aggregate targets
published by the IRS.  However, we do note that analysis with a
PUF-based data file tends to be more accurate than the `cps.csv` file.

### 2015 IRS public use data (`tmd.csv`)

The [tax-microdata
repository](https://github.com/PSLmodels/tax-microdata-benchmarking)
produces an input variables file (`tmd.csv.gz`), a **national** weights
file (`tmd_weights.csv.gz`), and a variable growth factors file
(`tmd_growfactors.csv`) that can be used with the Tax-Calculator
package beginning with the 3.6.0 release.  Beginning with Tax-Calculator
release 6.5.0, the start year for the TMD data is 2022.  The TMD files
are available only to users who have purchased their own version of the
2015 IRS-SOI PUF.  For those users, the TMD files are available from the
tax-microdata repository.  The three TMD files can be used with
Tax-Calculator in two ways:
  - with the **Python API**:
     * instantiate a GrowFactors object that uses TMD growth factors
      [`gf=GrowFactors("path/to/tmd_growfactors.csv")`] and by using
      the `Records.tmd_constructor(...)` static method to instantiate
      a Records object, and
    * after each instantiation of a Policy object, activate the TMD
      refundable credit claiming behavior by executing the
      `implement_reform(TMD_CREDIT_CLAIMING)` method on the Policy
      object (both for baseline and reform Policy objects), where the
      `TMD_CREDIT_CLAIMING` dictionary is imported from the `taxcalcio.py`
      module.
  - or
  - with the **CLI tool**, use `tc`, when the three TMD files are all
    in the same folder and the `tmd.csv.gz` file has been unzipped.
    The `tc` tool automatically activates the TMD refundable credit
    claiming behavior, so there is no need to do that on the command
    line when using the CLI tool.

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
```

Or for the first Congressional district in New Mexico, put the
`nm01_tmd_weights.csv.gz` file in the folder with the other TMD
files and execute this command:
```
(taxcalc-dev) myruns> TMD_AREA=nm01 tc tmd.csv 2024 --exact --tables
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
