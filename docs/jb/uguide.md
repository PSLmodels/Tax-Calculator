User Guide
==========

This document tells you how to use Tax-Calculator, an open-source federal income and payroll tax microsimulation model. It assumes that you are already familiar with the material covered in the [introductory documentation](https://pslmodels.github.io/Tax-Calculator/) (except for the guides and cookbook) and that you are using the latest release of Tax-Calculator mentioned there.

### Table of Contents

1.  [**Python-Progamming Usage**](#pyp)
2.  [**No-Programming Usage**](#cli)

1.  [Test tc CLI](#cli-install-test)
2.  [Specify Tax Reform](#cli-spec-reform)
3.  [Specify Analysis Assumptions](#cli-spec-assump)
4.  [Specify Filing Units](#cli-spec-funits)
5.  [Initiate Reform Analysis](#cli-init-analysis)
6.  [Tabulate Reform Results](#cli-tab-results)

4.  [**Policy Parameters**](#pol)

1.  [Parameter Indexing](#pol-parameter-indexing)
2.  [Payroll Taxes](#pol-payroll-taxes)
3.  [Social Security Taxability](#pol-social-security-taxability)
4.  [Above The Line Deductions](#pol-above-the-line-deductions)
5.  [Personal Exemptions](#pol-personal-exemptions)
6.  [Standard Deduction](#pol-standard-deduction)
7.  [Nonrefundable Credits](#pol-nonrefundable-credits)
8.  [Child/Dependent Credits](#pol-childdependent-credits)
9.  [Itemized Deductions](#pol-itemized-deductions)
10.  [Capital Gains And Dividends](#pol-capital-gains-dividends)
11.  [Personal Income](#pol-personal-income)
12.  [Other Taxes](#pol-other-taxes)
13.  [Refundable Credits](#pol-refundable-credits)
14.  [Surtaxes](#pol-surtaxes)
15.  [Universal Basic Income](#pol-ubi)
16.  [Benefits](#pol-benefits)
17.  [Other Parameters](#pol-other-parameters)

6.  [**Input Variables**](#input)
7.  [**Output Variables**](#output)
8.  [**Assumption Parameters**](#params)

1.  [Growdiff Parameters](#params-growdiff)
2.  [Consumption Parameters](#params-consump)

### 1\. Python-Programming Usage

Of the two ways of using Tax-Calculator described in this guide, one requires writing Python programs, the other involves using a command-line tool and requires no computer programming. The detailed information in this guide about policy parameters, input variables, output variables, and assumption parameters, will be useful to you either way you use Tax-Calculator.

If you want to learn more about how to write Python programs that use Tax-Calculator, read the [python cookbook](https://PSLmodels.github.io/Tax-Calculator/cookbook.html), which contains a collection of tested recipes that employ both basic and advanced techniques.

### 2\. No-Programming Usage

You can use Tax-Calculator on your own computer via a command-line interface (CLI) called `tc`.
This approach requires the use of a text editor to prepare simple files that are read by `tc`.
Computer programming knowledge is not required, but this approach to using Tax-Calculator assumes you are willing to work at the command line (Terminal on Mac or Anaconda Prompt on Windows) and to use a text editor (for example, TextEdit on Mac or Notepad on Windows).

#### 2a. Test `tc` CLI

The `tc` CLI is part of the Tax-Calculator `taxcalc` package you installed on your computer as part of [Getting Started](https://pslmodels.github.io/Tax-Calculator/tc_starting.html).

To check your installation of `tc`, enter the following command:

```
tc --test
```

Expected output (after a number of seconds) is `PASSED TEST`. If you get `FAILED TEST`, something went wrong in the installation process. If the installation test fails, please report your experience by creating a new issue at [this website](https://github.com/PSLmodels/Tax-Calculator/issues).

If your installation passes the test, you are ready to begin using `tc` to analyze tax reforms. Continue reading this section for information about how to do that. But if you want a quick hint about the range of `tc` capabilities, enter the following:

```
tc --help
```

The basic idea of `tc` tax analysis is that each tax reform is specified in a text file using a simple method to describe the details of the reform. Read the next part of this section to see how policy reform files are formatted.

#### 2b. Specify Tax Reform

The details of a tax reform are contained in a text file that you write with a text editor. The reform is expressed by specifying which tax policy parameters are changed from their current-law values by the reform. The current-law values of each policy parameter are documented in [this section](#pol) of the guide. The timing and magnitude of these policy parameter changes are written in JSON, a simple and widely-used data-specification language.

For several examples of reform files and the general rules for writing JSON reform files, go to [this page](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/README.md#policy-reform-files).

#### 2c. Specify Analysis Assumptions

This part explains how to specify economic assumption files used in static tax analysis. This is an advanced topic, so if you want to start out using the default assumptions (which are documented in [this section](#params) of the guide), you can skip this part now and come back to read it whenever you want to change the default assumptions. The [next part](#cli-spec-funits) of this section discusses filing-unit input files.

The details of analysis assumptions are contained in a text file that you write with a text editor. The assumptions are expressed by specifying which parameters are changed from their default values. The timing and magnitude of these parameter changes are written in JSON, a simple and widely-used data-specification language.

For examples of assumption files and the general rules for writing JSON assumption files, go to [this page](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/assumptions/README.md#economic-assumption-files).

#### 2d. Specify Filing Units

The `taxcalc` package containing `tc` does not include an IRS-SOI-PUF-derived microsimulation sample. This is because, unlike Census public-use files, the IRS-SOI Public Use File (PUF) is proprietary. If you or your organization has paid IRS to use the PUF version being by Tax-Calculator, then it may be possible for us to share with you our PUF-derived sample, which we call `puf.csv` even though it contains CPS records that represent non-filers. Otherwise, you have two choices.

**First**, you can easily create with a text editor a CSV-formatted file containing several filing units whose experience under your tax reform is of interest to you. Much of the public discussion of tax reforms is of this type: how is this family or that family affected by a reform; how do they fare under different reforms; etc. The test conducted to check the `tc` installation has left one such file. It is called `test.csv` and contains two filing units with only wage and salary income: a lower income family and a higher income family. You can use this `test.csv` file as `tc` input to analyze your tax reforms. Before creating your own input files be sure to read the short set of guidelines that appear after this list of two choices. Some people pursue this approach using a statistical pacakge like R or Stata, in which case the `tc` CLI program can be invoked from within the statistical package. There may be a need (especially on Windows) to [add to the system PATH](https://github.com/PSLmodels/Tax-Calculator/issues/2273#issuecomment-479572287) in order to do this.

**Second**, the `taxcalc` does include a freely available microsimulation sample containing only filing units derived from several recent March CPS surveys. For several reasons, the results generated by this `cps.csv` file are substantially different from the results generated by the `puf.csv` file. The `cps.csv` file contains a sample of the population while the `puf.csv` file contains mostly a sample of income tax filers in which high-income filing units are over represented. Also, the `cps.csv` file has many income variables that are missing (and assumed to be zero by Tax-Calculator), which causes an understating of total incomes, especially for those with high incomes. All these differences mean that the aggregate revenue and distributional results generated when using the `cps.csv` file as input to Tax-Calculator can be substantially different from the results generated when using the `puf.csv` file as input. And this is particularly true when analyzing reforms that change the tax treatment of high-income filers.

**Input-File-Preparation Guidelines**

The `tc` CLI to Tax-Calculator is flexible enough to read almost any kind of CSV-formatted input data on filing units as long as the variable names correspond to those expected by Tax-Calculator. The only required input variables are `RECID` (a unique filing-unit record identifier) and `MARS` (a positive-valued filing-status indicator). Other variables in the input file must have variable names that are listed in the [Input Variables](#input) section for them to affect the tax calculations. Any variable listed in Input Variables that is not in an input file is automatically set to zero for every filing unit. Variables in the input file that are not listed in Input Variables are ignored by Tax-Calculator.

However, there are important data-preparation issues related to the fact that the payroll tax is a tax on individuals, not on income-tax filing units. Tax-Calculator expects that the filing-unit total for each of several earnings-related variables is split between the taxpayer and the spouse. It is the responsibility of anyone preparing data for Tax-Calculator input to do this earnings splitting. Here are the relationships between the filing-unit variable and the taxpayer (`p`) and spouse (`s`) variables expected by Tax-Calculator:

```
e00200 = e00200p + e00200s
e00900 = e00900p + e00900s
e02100 = e02100p + e02100s
```

Obviously, when `MARS` is not equal to 2 (married filing jointly), the values of the three `s` variables are zero and the value of each `p` variable is equal to the value of its corresponding filing-unit variable. Note that the input file can omit any one, or all, of these three sets variables. If the three variables in one of these sets are omitted, the required relationship will be satisfied because zero equals zero plus zero.

In addition to this earnings-splitting data-preparation issue, Tax-Calculator expects that the value of ordinary dividends (`e00600`) will be no less than the value of qualified dividends (`e00650`) for each filing unit. And it also expects that the value of total pension and annuity income (`e01500`) will be no less than the value of taxable pension and annuity income (`e01700`) for each filing unit. Tax-Calculator also expects the value of the required MARS variable to be in the range from one to five, and the value of the EIC variable to be in the range from zero to three. Again, it is your responsibility to prepare input data for Tax-Calculator in a way that ensures these relationships are true for each filing unit.

Here's an example of how to specify a few stylized filing units with and without young children:

```
RECID,MARS,XTOT,EIC,n24,...
    11   ,  1 ,  1 , 0 , 0 ,... <== single person with no kids
    12   ,  4 ,  2 , 1 , 1 ,... <== single person with a young kid
    13   ,  2 ,  4 , 2 , 2 ,... <== married couple with two young kids
```

Be sure to read the documentation of the `MARS`, `XTOT`, `EIC`, and `n24` input variables. Also, there may be a need to add other child-age input variables if you want to simulate reforms like a child credit bonus for young children. Also, the universal basic income (UBI) reform is implemented using its own set of three age-group-count input variables.

The name of your input data file is also relevant to how `tc` will behave. If your file name ends with "puf.csv" or "cps.csv", `tc` will automatically extrapolate your data from its base year to the year you specify for tax calculations to be calculated using built in growth factors, extrapolated weights, and other adjustment factors. If you are not using the "puf.csv" or "cps.csv" files produced by the TaxData project, it is likely that your data will not be compatible with these extrapolations and you should adopt filenames with alternative endings.

#### 2e. Initiate Reform Analysis

Executing `tc` requires only two command-line arguments: the name of an input file containing one or more filing units and the year for which the tax calculations are done. A baseline policy file is optional; specifying no baseline file implies the baseline policy is current-law policy. A policy reform file is optional; specifying no reform file implies calculations are done for the baseline policy. An economic assumption file is also optional; no assumption file implies you want to use the default values of the assumption parameters. The output files written by `tc` are built-up from the name of the input file, tax year, baseline file, reform file, and assumption file using a `#` character if an option is not specified.

Here we explain how to conduct tax analysis with `tc` by presenting a series of examples and explaining what output is produced in each example. There are several types of output that `tc` can generate so there will be more than a few examples. The examples are numbered in order to make it easier to refer to different examples. All the examples assume that the input file is `test.csv`, which was mentioned earlier in this guide.

```
tc test.csv 2020
```

This produces a minimal output file containing 2020 tax liabilities for each filing unit assuming the income amounts in the input file are amounts for 2020 and assuming current-law tax policy projected to 2020\. The name of the CSV-formatted output file is `test-20-#-#-#.csv`. The first `#` symbol indicates we did not specify a baseline file and the second `#` symbol indicates we did not specify a policy reform file and the third `#` symbol indicates we did not specify an economic assumption file.  
The variables included in the minimal output file include: `RECID` (of filing unit in the input file), `YEAR` (specified when executing `tc`), `WEIGHT` (which is same as `s006`), `INCTAX` (which is same as `iitax`), `LSTAX` (which is same as `lumpsum_tax`) and `PAYTAX` (which is same as `payroll_tax`).

Also, documentation of the reform is always written to a text file ending in `-doc.text`, which in this example would be named `test-20-#-#-#-doc.text`.

```
tc test.csv 2020 --dump
```

This produces a much more complete output file with the same name `test-20-#-#-#.csv` as the minimal output file produced in example (1). No other output is generated other than the `test-20-#-#-#-doc.text` file. The `--dump` option causes **all** the input variables (including the ones understood by Tax-Calculator but not included in `test.csv`, which are all zero) and **all** the output variables calculated by Tax-Calculator to be included in the output file. For a complete list of input variables, see the [Input Variables](#input) section. For a complete list of output variables, see the [Output Variables](#output) section. Since Tax-Calculator ignores variables in the input file that are not in the Input Variables section, the dump output file in example (2) can be used as an input file and it will produce exactly the same tax liabilities (apart from rounding errors of one or two cents) as in the original dump output.

This full dump output can be useful for debugging and is small when using just a few filing units as input. But when using large samples as input (for example, the `cps.csv` input file), the size of the dump output becomes quite large. There is a way to specify a **partial dump** that includes only variables of interest. To have `tc` do a partial dump, create a text file that lists the names of the variables to be included in the partial dump. You can put the varible names on separate lines and/or put several names on one line separated by spaces. Then point to that file using the `--dvars` option. So, for example, if your list of dump variables is in a file named `mydumpvars`, a partial dump file is created this way:

```
tc cps.csv 2020 --dump --dvars mydumpvars
```

If there is no `--dvars` option, the `--dump` option produces a full dump.

```
tc test.csv 2020 --sqldb
```

This produces the same dump output as example (2) except that the dump output is written not to a CSV-formatted file, but to the dump table in an SQLite3 database file, which is called `test-20-#-#-#.db` in this example. Because the `--dump` option is not used in example (3), minimal output will be written to the `test-20-#-#-#.csv` file. Note that use of the `--dvars` option causes the contents of the database file to be a partial dump.

Pros and cons of putting dump output in a CSV file or an SQLite3 database table: The CSV file is almost twice as large as the database, but it can be easily imported into a wide range of statistical packages. The main advantage of the SQLite3 database is that the Anaconda Python distribution includes [sqlite3](https://www.sqlite.org/cli.html) (or sqlite3.exe on Windows), a command-line tool that can be used to tabulate dump output using structured query language (SQL). SQL is a language that you use to specify the tabulation you want and the SQL database figures out the procedure for generating your tabulation and then executes that procedure; there is no computer programming involved. We illustrate SQL tabulation of dump output in a [subsequent section](#cli-tab-results).

```
tc test.csv 2020 --dump --sqldb
```

This shows that you can get dump output in the two different formats from a single `tc` run.

The remaining examples use neither the `--dump` nor the `--sqldb` option, and thus, produce minimal output for the reform. But either or both of those options could be used in all the subsequent examples to generate more complete output for the reform.

```
tc test.csv 2021 --reform ref3.json
```

This produces 2021 output for the filing units in the `test.csv` file using the policy reform specified in the `ref3.json` file. The name of the output file in this example is `test-21-#-ref3-#.csv` because no baseline or assumption options were specified.

If, in addition to `ref3.json`, there was a `ref4.json` reform file and analysis of the **compound reform** (consisting of first implementing the `ref3.json` reform relative to current-law policy and then implementing the `ref4.json` reform relative to the `ref3.json` reform) is desired, both reform files can be mentioned in the `--reform` option as follows:

``
tc test.csv 2021 --reform ref3.json+ref4.json
```

The above command generates an output file named `test-21-#-ref3+ref4-#.csv`

```
tc test.csv 2021 --reform ref3.json --assump res1.json
```

This produces 2021 output for the filing units in the `test.csv` file using the policy reform specified in the `ref3.json` file and the economic assumptions specified in the `eas1.json` file. The output results produced by this analysis are written to the `test-21-#-ref3-eas1.csv` file.

In the preceding examples, all the output files are written in the directory where the `tc` command was executed. If you want the output files to be written in a different directory, use the `--outdir` option. So, for example, if you have created the `myoutput` directory as a subdirectory of the directory from where you are running `tc`, output files will be written there if you use the `--outdir myoutput` option.

The following examples illustrate output options that work only if each filing unit in the input file has a positive sampling weight (`s006`). So, we are going to use the `cps.csv` file in these examples along with the policy reform specified in the `ref3.json` file, the content of which is:

```
// ref3.json raises personal exemption amount to 8000 in 2022,
// after which it continues to be indexed to price inflation.
{
    "II_em": {"2022": 8000}
}
```

The output options illustrated in the following examples generate tables of the post-reform level and the reform-induced change in tax liability by income deciles as well as graphs of marginal and average tax rates and percentage change in aftertax income by income percentiles. These tables and graphs are meant to provide a quick glance at the impact of a reform. Any serious analysis of a reform will involve generating custom tables and graphs using [partial dump](#partdump) output. One of many examples of this sort of custom analysis is [here](https://www.washingtonpost.com/graphics/2017/business/tax-bill-calculator/?).

```
$ tc cps.csv 2022 --reform ref3.json --tables
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2022.

ls cps-22*
cps-22-#-ref3-#-doc.text    cps-22-#-ref3-#.csv
cps-22-#-ref3-#-tab.text

$ cat cps-22-#-ref3-#-tab.text
Weighted Tax Reform Totals by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.6      -6.1      20.9       0.0      14.8
 1    17.19     500.1      -7.9      44.1       0.0      36.2
 2    17.19     664.2      -2.7      51.7       0.0      49.0
 3    17.19     829.5       1.3      68.5       0.0      69.8
 4    17.19    1030.5       7.8      86.7       0.0      94.5
 5    17.19    1273.3      16.7     103.9       0.0     120.6
 6    17.19    1596.8      40.7     137.6       0.0     178.4
 7    17.19    2044.5      81.4     183.3       0.0     264.7
 8    17.19    2821.3     177.0     263.2       0.0     440.2
 9    17.19    6369.3    1025.5     476.3       0.0    1501.8
 A   171.93   17325.2    1333.8    1436.2       0.0    2770.0

Weighted Tax Differences by Baseline Expanded-Income Decile
    Returns    ExpInc    IncTax    PayTax     LSTax    AllTax
       (#m)      ($b)      ($b)      ($b)      ($b)      ($b)
 0    17.19     195.6      -1.8       0.0       0.0      -1.8
 1    17.19     500.1      -7.0       0.0       0.0      -7.0
 2    17.19     664.2      -8.3       0.0       0.0      -8.3
 3    17.19     829.5     -11.0       0.0       0.0     -11.0
 4    17.19    1030.5     -15.1       0.0       0.0     -15.1
 5    17.19    1273.3     -21.4       0.0       0.0     -21.4
 6    17.19    1596.8     -28.9       0.0       0.0     -28.9
 7    17.19    2044.5     -38.9       0.0       0.0     -38.9
 8    17.19    2821.3     -62.9       0.0       0.0     -62.9
 9    17.19    6369.3     -87.0       0.0       0.0     -87.0
 A   171.93   17325.2    -282.4       0.0       0.0    -282.4
```

This produces 2022 output for the filing units in the `cps.csv` file using the policy reform specified in the `ref3.json` file. Notice that Tax-Calculator knows to extrapolate (or "age") filing unit data in the `cps.csv` file to the specified tax year.
It knows to do that because of the special input file name `cps.csv`.
The tables produced by this analysis are written to the `cps-22-#-ref3-#-tab.text` file.
Note that on Windows you would use `dir` instead of `ls` and `type` instead of `cat`.

Also note that the tables above in example (7) include in the bottom decile some filing units who have negative or zero expanded income in the baseline. If you want tables that somehow exclude those filing units, use the `--dump` option and tabulate your own tables.

```
$ tc cps.csv 2024 --reform ref3.json --graphs
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2024.

$ ls cps-24-*
cps-24-#-ref3-#-atr.html    cps-24-#-ref3-#-pch.html
cps-24-#-ref3-#-doc.text    cps-24-#-ref3-#.csv
cps-24-#-ref3-#-mtr.html
```

This example is like the previous one, except we ask for 2024 static output and for graphs instead of tables, although we could ask for both.
The HTML files containing the graphs can be viewed in your browser.

Here is what the average tax rate graph in `cps-24-#-ref3-#-atr.html` looks like.

![atr graph](atr.png)

Here is what the marginal tax rate graph in `cps-24-#-ref3-#-mtr.html` looks like:

![mtr graph](mtr.png)

Here is what the percentage change in aftertax income graph in `cps-24-#-ref3-#-pch.html` looks like:

![pch graph](pch.png)

There is yet another `tc` output option that writes to the screen results from a normative welfare analysis of the specified policy reform. This `--ceeu` option produces experimental results that make sense only with input files that contain representative samples of the population such as the `cps.csv` file. The name of this option stands for certainty-equivalent expected utility. If you want to use this output option, you should read the commented Python source code for the `ce_aftertax_expanded_income` function in the `taxcalc/utils.py` file in the [Tax-Calculator repository](https://github.com/PSLmodels/Tax-Calculator).

None of the above examples use the `--baseline` option, which means that baseline policy in those examples is current-law policy. The following example shows how to use the `--baseline` option to engage in counter-factual historical analysis. Suppose we want to analyze what would have happened if some alternative to TCJA had been enacted in late 2017\. To do this we need to have pre-TCJA policy be the baseline policy and we need to have the alternative reform be implemented relative to pre-TCJA policy. The following `tc` run does exactly that using a local copy of the [2017_law.json](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/2017_law.json) <a>file and the `alt_reform.json` file containing the alternative reform defined relative to pre-TCJA law.

```
$ tc cps.csv 2019 --baseline 2017_law.json --reform 2017_law.json+alt_reform.json
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2019.
```

In all the examples in this section, we have executed one `tc` run at at time. 
But **what if you want to execute many `tc` runs** because you want results for many years and/or for several different reforms.
Unless you are asking for full-dump output, a single `tc` run should take no more than one minute on your computer (even if you are using the large `cps.csv` input file).
The easiest way to speed up the execution of many `tc` runs is to split them into groups of runs and execute each group of runs in a different command-prompt window.
On most modern computers that have four CPU cores and a fast disk drive, executing four runs in different windows will take not much more time than executing a single `tc` run.
If you have more than one run in each group, put them in a Unix/Mac bash script or a Windows batch file, and execute one script in each command-prompt window. 
If it still takes too long, consider splitting the `tc` runs across more than one computer.

#### 2f. Tabulate Reform Results

Given that `tc` output can be written to either CSV-formatted files or SQLite3 database files, there is an enormous range of software tools that can be used to tabulate the output. You can use SAS or R, Stata or MATLAB, or even import output into a spreadsheet (but this would seem to be the least useful option). If you just want to compare the contents of two output files, you can use your favorite graphical diff program to view the two files <q>side by side</q> with highlighting of numbers that are different. The main point is to use a software tool that is available to you, that is appropriate for the task, and that you have experience using.

Here we give some examples of using the `sqlite3` command-line tool that is part of the Anaconda distribution (so it is always available when using Tax-Calculator). The first step, of course, is to use the `--sqldb` option when running `tc`. Then you can use the `sqlite3` tool interactively or use it to execute SQL scripts you have saved in a text file. We'll provide examples of both those approaches. There are many online tutorials on the SQL select command; if you want to learn more, search the Internet.

First, we provide a simple example of using `sqlite3` interactively. This approach is ideal for exploratory data analysis. Our example uses the `cps.csv` file as input, but you can do the following with the output from any input file that has weights (`s006`). Also, we specify no policy reform file, so the output is for current-law policy. What you cannot see from the following record of the analysis is that the `sqlite3` tool keeps a command history, so pressing the up-arrow key will bring up the prior command for editing. This feature reduces substantially the amount of typing required to conduct exploratory data analysis.

```
$ tc cps.csv 2016 --sqldb
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2016.

$ sqlite3 cps-16-#-#-#.db
SQLite version 3.22.0 2018-01-22 18:45:57
Enter ".help" for usage hints.
sqlite> YOUR FIRST SQL COMMAND GOES HERE
sqlite> YOUR SECOND SQL COMMAND GOES HERE
sqlite> ...
sqlite> YOUR FINAL SQL COMMAND GOES HERE
sqlite> .quit
```

Second, we provide a simple example of using `sqlite3` with SQL commands stored in a text file. This approach is useful if you want to tabulate many different output files in the same way. This second example assumes that the first example has already been done. Note that on Windows you should replace `cat` with `type`.

```
$ cat tab.sql
-- tabulate unweighted and weighted number of filing units
select "unweighted count | weighted count (#m) of filing units";
select count(*),  -- unweighted count of filing units
       round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump;

-- weighted count by filing status (MARS)
select "filing status (MARS) | weighted count of filing units";
select MARS, -- filing status
       round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump
group by MARS;

-- tabulate weight of those with NEGATIVE marginal income tax rates
select "weighted count of those with NEGATIVE MTR";
select round(sum(s006)*1e-6,3) -- weighted count of filing units (#m)
from dump
where mtr_inctax < 0;

-- construct NON-NEGATIVE marginal income tax rate histogram with bin width 10
select "bin number | weighted count | mean NON-NEGATIVE MTR in bin";
select cast(round((mtr_inctax-5)/10) as int) as mtr_bin, -- histogram bin number
       round(sum(s006)*1e-6,3), -- weight count of filing units in bin (#m)
       -- weighted mean marginal income tax rate on taxpayer earnings in bin:
       round(sum(mtr_inctax*s006)/sum(s006),2)
from dump
where mtr_inctax >= 0 -- include only those with NON-NEGATIVE marginal tax rate
group by mtr_bin
order by mtr_bin;

$ cat tab.sql | sqlite3 cps-16-#-#-#.db
unweighted count | weighted count (#m) of filing units
456465|157.558
filing status (MARS) | weighted count of filing units
1|81.303
2|61.655
4|14.599
weighted count of those with NEGATIVE MTR
15.473
bin number | weighted count | mean NON-NEGATIVE MTR in bin
-1|26.896|0.0
0|2.606|7.18
1|60.85|14.11
2|37.803|25.54
3|12.804|32.26
4|1.0|43.08
5|0.11|55.74
6|0.015|66.76
```

The `cat` command writes the contents of the `tab.sql` file to stdout. We do nothing but that in the first command in order to show you the file contents. The second command pipes the contents of the `tab.sql` file into the `sqlite3` tool, which executes the SQL statements and writes the tabulation results to stdout. (If you're wondering about the validity of those high marginal tax rates, rest assured that all filing units with marginal income tax rates greater than sixty percent have been checked by hand and are valid: most are caught in the rapid phase-out of non-refundable education credits or in the phase-in of taxation of social security benefits. The negative marginal tax rates are caused by refundable credits, primarily the earned income tax credit.)

If you want to use the `sqlite3` tool to tabulate the changes caused by a reform, use `tc` to generate two database dump files (one for current-law policy and the other for your reform) and then use the SQLite3 ATTACH command to make both database files available in your SQLite tabulation session.

### 3\. Policy Parameters

This section contains documentation of policy parameters in a format that is easy to search and print.
The policy parameters are grouped here as they are are in the [Tax-Brain webapp](https://www.compmodels.org/PSLmodels/Tax-Brain/).
Parameters understood by Tax-Calculator and the `tc` CLI, but not available on Tax-Brain, are placed in an Other Parameters group at the end of the section.

#### 3a. Parameter Indexing

**Parameter Indexing — Offsets**  
_tc Name:_ CPI_offset  
_Title:_ Decimal offset ADDED to unchained CPI to get parameter indexing rate  
_Description:_ Values are zero before 2017; reforms that introduce indexing with chained CPI would have values around -0.0025 beginning in the year before the first year policy parameters will have values computed with chained CPI.  
_Notes:_ See [April 2013 CBO report](https://www.cbo.gov/publication/44089) entitled 'What Would Be the Effect on the Deficit of Using the Chained CPI to Index Benefit Programs and the Tax Code?', which includes this: 'The chained CPI grows more slowly than the traditional CPI does: an average of about 0.25 percentage points more slowly per year over the past decade.'
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: -0.0025  
2018: -0.0025  
2019: -0.0025  
2020: -0.0025  
2021: -0.0025  
2022: -0.0025  
2023: -0.0025  
2024: -0.0025  
2025: -0.0025  
2026: -0.0025  
_Valid Range:_ min = -0.005 and max = 0.005  
_Out-of-Range Action:_ error

#### 3b. Payroll Taxes

**Payroll Taxes — Social Security FICA**  
_tc Name:_ FICA_ss_trt  
_Title:_ Social Security payroll tax rate  
_Description:_ Social Security FICA rate, including both employer and employee.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.124  
2014: 0.124  
2015: 0.124  
2016: 0.124  
2017: 0.124  
2018: 0.124  
2019: 0.124  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Payroll Taxes — Social Security FICA**  
_tc Name:_ SS_Earnings_c  
_Title:_ Maximum taxable earnings (MTE) for Social Security  
_Description:_ Individual earnings below this amount are subjected to Social Security (OASDI) payroll tax.  
_Notes:_ This parameter is indexed by the rate of growth in average wages, not by the price inflation rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 113700.0  
2014: 117000.0  
2015: 118500.0  
2016: 118500.0  
2017: 127200.0  
2018: 128400.0  
2019: 132900.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Payroll Taxes — Social Security FICA**  
_tc Name:_ SS_Earnings_thd  
_Title:_ Additional Taxable Earnings Threshold for Social Security  
_Description:_ Individual earnings above this threshold are subjected to Social Security (OASDI) payroll tax, in addition to earnings below the maximum taxable earnings threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Payroll Taxes — Medicare FICA**  
_tc Name:_ FICA_mc_trt  
_Title:_ Medicare payroll tax rate  
_Description:_ Medicare FICA rate, including both employer and employee.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.029  
2014: 0.029  
2015: 0.029  
2016: 0.029  
2017: 0.029  
2018: 0.029  
2019: 0.029  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Payroll Taxes — Additional Medicare FICA**  
_tc Name:_ AMEDT_ec  
_Title:_ Additional Medicare tax earnings exclusion  
_Description:_ The Additional Medicare Tax rate, AMEDT_rt, applies to all earnings in excess of this excluded amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2014: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2015: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2016: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2017: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2018: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
2019: [200000.0, 250000.0, 125000.0, 200000.0, 200000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Payroll Taxes — Additional Medicare FICA**  
_tc Name:_ AMEDT_rt  
_Title:_ Additional Medicare tax rate  
_Description:_ This is the rate applied to the portion of Medicare wages, RRTA compensation and self-employment income exceeding the Additional Medicare Tax earning exclusion.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.009  
2014: 0.009  
2015: 0.009  
2016: 0.009  
2017: 0.009  
2018: 0.009  
2019: 0.009  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3c. Social Security Taxability

**Social Security Taxability — Threshold For Social Security Benefit Taxability 1**  
_tc Name:_ SS_thd50  
_Title:_ Threshold for Social Security benefit taxability 1  
_Description:_ The first threshold for Social Security benefit taxability: if taxpayers have provisional income greater than this threshold, up to 50% of their Social Security benefit will be subject to tax under current law.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2014: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2015: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2016: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2017: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2018: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
2019: [25000.0, 32000.0, 25000.0, 25000.0, 25000.0]  
_Valid Range:_ min = 0 and max = SS_thd85  
_Out-of-Range Action:_ error

**Social Security Taxability — Threshold For Social Security Benefit Taxability 2**  
_tc Name:_ SS_thd85  
_Title:_ Threshold for Social Security benefit taxability 2  
_Description:_ The second threshold for Social Security taxability: if taxpayers have provisional income greater than this threshold, up to 85% of their Social Security benefit will be subject to tax under current law.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2014: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2015: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2016: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2017: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2018: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
2019: [34000.0, 44000.0, 34000.0, 34000.0, 34000.0]  
_Valid Range:_ min = SS_thd50 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3d. Above The Line Deductions

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_StudentLoan_hc  
_Title:_ Adjustment for student loan interest haircut  
_Description:_ This decimal fraction can be applied to limit the student loan interest adjustment allowed.  
_Notes:_ The final adjustment amount will be (1-Haircut)*StudentLoanInterest.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_SelfEmploymentTax_hc  
_Title:_ Adjustment for self-employment tax haircut  
_Description:_ This decimal fraction, if greater than zero, reduces the employer equivalent portion of self-employment adjustment.  
_Notes:_ The final adjustment amount would be (1-Haircut)*SelfEmploymentTaxAdjustment.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_SelfEmp_HealthIns_hc  
_Title:_ Adjustment for self employed health insurance haircut  
_Description:_ This decimal fraction, if greater than zero, reduces the health insurance adjustment for self-employed taxpayers.  
_Notes:_ The final adjustment amount would be (1-Haircut)*SelfEmployedHealthInsuranceAdjustment.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_KEOGH_SEP_hc  
_Title:_ Adjustment for contributions to either KEOGH or SEP plan haircut  
_Description:_ Under current law, contributions to Keogh or SEP plans can be fully deducted from gross income. This haircut can be used to limit the adjustment allowed.  
_Notes:_ The final adjustment amount is (1-Haircut)*KEOGH_SEP_Contributinos.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_EarlyWithdraw_hc  
_Title:_ Adjustment for early withdrawal penalty haircut  
_Description:_ Under current law, early withdraw penalty can be fully deducted from gross income. This haircut can be used to limit the adjustment allowed.  
_Notes:_ The final adjustment amount is (1-Haircut)*EarlyWithdrawPenalty.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_AlimonyPaid_hc  
_Title:_ Adjustment for alimony-paid haircut  
_Description:_ Under pre-TCJA law, the full amount of alimony paid is taken as an adjustment from gross income in arriving at AGI. This haircut can be used to change the deduction allowed.  
_Notes:_ The final adjustment amount would be (1-Haircut)*AlimonyPaid.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_AlimonyReceived_hc  
_Title:_ Adjustment for alimony-received haircut  
_Description:_ Under pre-TCJA law, none of alimony received is taken as an adjustment from gross income in arriving at AGI. This haircut can be used to change the deduction allowed.  
_Notes:_ The final adjustment amount would be (1-Haircut)*AlimonyReceived.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_EducatorExpenses_hc  
_Title:_ Deduction for educator expenses haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of educator expenses that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*EducatorExpenses.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_HSADeduction_hc  
_Title:_ Deduction for HSA deduction haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of a taxpayer's HSA deduction that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*HSA_Deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_IRAContributions_hc  
_Title:_ Deduction for IRA contributions haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of IRA contributions that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*IRA_Contribution.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_DomesticProduction_hc  
_Title:_ Deduction for domestic production activity haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of domestic production activity that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*DomesticProductionActivity.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Adjustment Haircuts**  
_tc Name:_ ALD_Tuition_hc  
_Title:_ Deduction for tuition and fees haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of tuition and fees that can be deducted from AGI.  
_Notes:_ The final adjustment amount would be (1-Haircut)*TuitionFees.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Exclusions**  
_tc Name:_ ALD_InvInc_ec_rt  
_Title:_ Investment income exclusion rate haircut  
_Description:_ Decimal fraction of investment income base that can be excluded from AGI.  
_Notes:_ The final taxable investment income will be (1-_ALD_InvInc_ec_rt)*investment_income_base. Even though the excluded portion of investment income is not included in AGI, it still is included in investment income used to calculate the Net Investment Income Tax and Earned Income Tax Credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Misc. Exclusions**  
_tc Name:_ ALD_BusinessLosses_c  
_Title:_ Maximum amount of business losses deductible  
_Description:_ Business losses in excess of this amount may not be deducted from AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [250000.0, 500000.0, 250000.0, 250000.0, 500000.0]  
2019: [255000.0, 510000.0, 255000.0, 255000.0, 510000.0]  
2020: [259029.0, 518058.0, 259029.0, 259029.0, 518058.0]  
2021: [264675.83, 529351.66, 264675.83, 264675.83, 529351.66]  
2022: [270683.97, 541367.94, 270683.97, 270683.97, 541367.94]  
2023: [276936.77, 553873.54, 276936.77, 276936.77, 553873.54]  
2024: [283084.77, 566169.53, 283084.77, 283084.77, 566169.53]  
2025: [289199.4, 578398.79, 289199.4, 289199.4, 578398.79]  
2026: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Above The Line Deductions — Child And Elderly Care**  
_tc Name:_ ALD_Dependents_hc  
_Title:_ Deduction for childcare costs haircut  
_Description:_ This decimal fraction, if greater than zero, reduces the portion of childcare costs that can be deducted from AGI.  
_Notes:_ The final adjustment would be (1-Haircut)*AverageChildcareCosts.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Above The Line Deductions — Child And Elderly Care**  
_tc Name:_ ALD_Dependents_Child_c  
_Title:_ National average childcare costs: ceiling for available childcare deduction.  
_Description:_ The weighted average of childcare costs in the US. 7165 is the weighted average from the 'Child Care in America: 2016 State Fact Sheets'.  
_Notes:_ This is a weighted average of childcare costs in each state  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Above The Line Deductions — Child And Elderly Care**  
_tc Name:_ ALD_Dependents_Elder_c  
_Title:_ Ceiling for elderly care deduction proposed in Trump's tax plan  
_Description:_ A taxpayer can take an above the line deduction up to this amount if they have an elderly dependent. The Trump 2016 campaign proposal was for $5000.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Above The Line Deductions — Child And Elderly Care**  
_tc Name:_ ALD_Dependents_thd  
_Title:_ Maximum level of income to qualify for the dependent care deduction  
_Description:_ A taxpayer can only claim the dependent care deduction if their total income is below this level. The Trump 2016 campaign proposal was for 250000 single, 500000 joint, 250000 separate, 500000 head of household].  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3e. Personal Exemptions

**Personal Exemptions — Personal And Dependent Exemption Amount**  
_tc Name:_ II_em  
_Title:_ Personal and dependent exemption amount  
_Description:_ Subtracted from AGI in the calculation of taxable income, per taxpayer and dependent.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 3900.0  
2014: 3950.0  
2015: 4000.0  
2016: 4050.0  
2017: 4050.0  
2018: 0.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 4880.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Exemptions — Personal Exemption Phaseout Rate**  
_tc Name:_ II_prt  
_Title:_ Personal exemption phaseout rate  
_Description:_ Personal exemption amount will decrease by this rate for each dollar of AGI exceeding exemption phaseout start.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Exemptions — Repeal for Dependents Under Age 18**  
_tc Name:_ II_no_em_nu18  
_Title:_ Repeal personal exemptions for dependents under age 18  
_Description:_ Total personal exemptions will be decreased by the number of dependents under the age of 18.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

#### 3f. Standard Deduction

**Standard Deduction — Standard Deduction Amount**  
_tc Name:_ STD  
_Title:_ Standard deduction amount  
_Description:_ Amount filing unit can use as a standard deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [6100.0, 12200.0, 6100.0, 8950.0, 12200.0]  
2014: [6200.0, 12400.0, 6200.0, 9100.0, 12400.0]  
2015: [6300.0, 12600.0, 6300.0, 9250.0, 12600.0]  
2016: [6300.0, 12600.0, 6300.0, 9300.0, 12600.0]  
2017: [6350.0, 12700.0, 6350.0, 9350.0, 12700.0]  
2018: [12000.0, 24000.0, 12000.0, 18000.0, 24000.0]  
2019: [12200.0, 24400.0, 12200.0, 18350.0, 24400.0]  
2020: [12392.76, 24785.52, 12392.76, 18639.93, 24785.52]  
2021: [12662.92, 25325.84, 12662.92, 19046.28, 25325.84]  
2022: [12950.37, 25900.74, 12950.37, 19478.63, 25900.74]  
2023: [13249.52, 26499.05, 13249.52, 19928.59, 26499.05]  
2024: [13543.66, 27087.33, 13543.66, 20371.0, 27087.33]  
2025: [13836.2, 27672.42, 13836.2, 20811.01, 27672.42]  
2026: [7651.0, 15303.0, 7651.0, 11266.0, 15303.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Standard Deduction — Additional Standard Deduction For Blind And Aged**  
_tc Name:_ STD_Aged  
_Title:_ Additional standard deduction for blind and aged  
_Description:_ To get the standard deduction for aged or blind individuals, taxpayers need to add this value to regular standard deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [1500.0, 1200.0, 1200.0, 1500.0, 1500.0]  
2014: [1550.0, 1200.0, 1200.0, 1550.0, 1550.0]  
2015: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2016: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2017: [1550.0, 1250.0, 1250.0, 1550.0, 1550.0]  
2018: [1600.0, 1300.0, 1300.0, 1600.0, 1300.0]  
2019: [1650.0, 1300.0, 1300.0, 1650.0, 1300.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3g. Nonrefundable Credits

**Nonrefundable Credits — Child And Dependent Care**  
_tc Name:_ CDCC_c  
_Title:_ Maximum child & dependent care credit per dependent  
_Description:_ The maximum amount of credit allowed for each qualifying dependent.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 3000.0  
2014: 3000.0  
2015: 3000.0  
2016: 3000.0  
2017: 3000.0  
2018: 3000.0  
2019: 3000.0  
_Valid Range:_ min = 0 and max = 3000  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Child And Dependent Care**  
_tc Name:_ CDCC_ps  
_Title:_ Child & dependent care credit phaseout start  
_Description:_ For taxpayers with AGI over this amount, the credit is reduced by one percentage point each $2000 of AGI over this amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 15000.0  
2014: 15000.0  
2015: 15000.0  
2016: 15000.0  
2017: 15000.0  
2018: 15000.0  
2019: 15000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Child And Dependent Care**  
_tc Name:_ CDCC_crt  
_Title:_ Child & dependent care credit phaseout percentage rate ceiling  
_Description:_ The maximum percentage rate in the AGI phaseout; this percentage rate decreases as AGI rises above the CDCC_ps level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 35.0  
2014: 35.0  
2015: 35.0  
2016: 35.0  
2017: 35.0  
2018: 35.0  
2019: 35.0  
_Valid Range:_ min = 0 and max = 100  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_RetirementSavings_hc  
_Title:_ Credit for retirement savings haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the retirement savings credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*RetirementSavingsCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_ForeignTax_hc  
_Title:_ Credit for foreign tax haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the foreign tax credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ForeignTaxCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_ResidentialEnergy_hc  
_Title:_ Credit for residential energy haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the residential energy credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ResidentialEnergyCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_GeneralBusiness_hc  
_Title:_ Credit for general business haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the general business credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*GeneralBusinessCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_MinimumTax_hc  
_Title:_ Credit for previous year minimum tax credit haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the previous year minimum tax credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*PreviousYearMinimumTaxCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_AmOppRefundable_hc  
_Title:_ Refundable portion of the American Opportunity Credit haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the refundable American Opportunity credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*RefundablePortionOfAmericanOpportunityCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_AmOppNonRefundable_hc  
_Title:_ Nonrefundable portion of the American Opportunity Credit haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of the nonrefundable American Opportunity credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*NonRefundablePortionOfAmericanOpportunityCredit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_SchR_hc  
_Title:_ Schedule R Credit haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of Schedule R credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*ScheduleRCredit  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_OtherCredits_hc  
_Title:_ Other Credits haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of other credit that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*OtherCredits.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Misc. Credit Limits**  
_tc Name:_ CR_Education_hc  
_Title:_ Education Credits haircut  
_Description:_ If greater than zero, this decimal fraction reduces the portion of education credits that can be claimed.  
_Notes:_ Credit claimed will be (1-Haircut)*EducationCredits.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Personal Nonrefundable Credit**  
_tc Name:_ II_credit_nr  
_Title:_ Personal nonrefundable credit maximum amount  
_Description:_ This credit amount is not refundable and is phased out based on AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Personal Nonrefundable Credit**  
_tc Name:_ II_credit_nr_ps  
_Title:_ Personal nonrefundable credit phaseout start  
_Description:_ The personal nonrefundable credit amount will be reduced for taxpayers with AGI higher than this threshold level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Nonrefundable Credits — Personal Nonrefundable Credit**  
_tc Name:_ II_credit_nr_prt  
_Title:_ Personal nonrefundable credit phaseout rate  
_Description:_ The personal nonrefundable credit amount will be reduced at this rate for each dollar of AGI exceeding the II_credit_nr_ps threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3h. Child/Dependent Credits

**Child/Dependent Credits — Child Tax Credit**  
_tc Name:_ CTC_c  
_Title:_ Maximum nonrefundable child tax credit per child  
_Description:_ The maximum nonrefundable credit allowed for each child.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1000.0  
2016: 1000.0  
2017: 1000.0  
2018: 2000.0  
2019: 2000.0  
2020: 2000.0  
2021: 2000.0  
2022: 2000.0  
2023: 2000.0  
2024: 2000.0  
2025: 2000.0  
2026: 1000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Child Tax Credit**  
_tc Name:_ CTC_c_under5_bonus  
_Title:_ Bonus child tax credit maximum for qualifying children under five  
_Description:_ The maximum amount of child tax credit allowed for each child is increased by this amount for qualifying children under 5 years old.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Child Tax Credit**  
_tc Name:_ CTC_ps  
_Title:_ Child tax credit phaseout MAGI start  
_Description:_ Child tax credit begins to decrease when MAGI is above this level; read descriptions of the dependent credit amounts for how they phase out when MAGI is above this level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2014: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2015: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2016: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2017: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2020: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2021: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2022: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2023: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2024: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2025: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2026: [75000.0, 110000.0, 55000.0, 75000.0, 75000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Child Tax Credit**  
_tc Name:_ CTC_prt  
_Title:_ Child and dependent tax credit phaseout rate  
_Description:_ The amount of the credit starts to decrease at this rate if MAGI is higher than child tax credit phaseout start.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.05  
2014: 0.05  
2015: 0.05  
2016: 0.05  
2017: 0.05  
2018: 0.05  
2019: 0.05  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Additional Child Tax Credit**  
_tc Name:_ ACTC_c  
_Title:_ Maximum refundable additional child tax credit  
_Description:_ This refundable credit is applied to child dependents and phases out exactly like the CTC amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1000.0  
2016: 1000.0  
2017: 1000.0  
2018: 1400.0  
2019: 1400.0  
2020: 1400.0  
2021: 1400.0  
2022: 1500.0  
2023: 1500.0  
2024: 1500.0  
2025: 1600.0  
2026: 1000.0  
_Valid Range:_ min = 0 and max = CTC_c  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Additional Child Tax Credit**  
_tc Name:_ ACTC_rt  
_Title:_ Additional Child Tax Credit rate  
_Description:_ This is the fraction of earnings used in calculating the ACTC, which is a partially refundable credit that supplements the CTC for some taxpayers.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Additional Child Tax Credit**  
_tc Name:_ ACTC_rt_bonus_under5family  
_Title:_ Bonus additional child tax credit rate for families with qualifying children under 5  
_Description:_ For families with qualifying children under 5 years old, this bonus rate is added to the fraction of earnings (additional child tax credit rate) used in calculating the ACTC.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Additional Child Tax Credit**  
_tc Name:_ ACTC_Income_thd  
_Title:_ Additional Child Tax Credit income threshold  
_Description:_ The portion of earned income below this threshold does not count as base for the Additional Child Tax Credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 3000.0  
2014: 3000.0  
2015: 3000.0  
2016: 3000.0  
2017: 3000.0  
2018: 2500.0  
2019: 2500.0  
2020: 2500.0  
2021: 2500.0  
2022: 2500.0  
2023: 2500.0  
2024: 2500.0  
2025: 2500.0  
2026: 3000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Additional Child Tax Credit**  
_tc Name:_ ACTC_ChildNum  
_Title:_ Additional Child Tax Credit minimum number of qualified children for different formula  
_Description:_ Families with this number of qualified children or more may qualify for a different formula to calculate the Additional Child Tax Credit, which is a partially refundable credit that supplements the Child Tax Credit for some taxpayers.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 3  
2014: 3  
2015: 3  
2016: 3  
2017: 3  
2018: 3  
2019: 3  
_Valid Range:_ min = 0 and max = 99  
_Out-of-Range Action:_ error

**Child/Dependent Credits — Other Dependent Tax Credit**  
_tc Name:_ ODC_c  
_Title:_ Maximum nonrefundable other-dependent credit  
_Description:_ This nonrefundable credit is applied to non-child dependents and phases out along with the CTC amount.  
_Notes:_ Became current-law policy with passage of TCJA  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 500.0  
2019: 500.0  
2020: 500.0  
2021: 500.0  
2022: 500.0  
2023: 500.0  
2024: 500.0  
2025: 500.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3i. Itemized Deductions

**Itemized Deductions — Medical Expenses**  
_tc Name:_ ID_Medical_frt  
_Title:_ Floor (as a decimal fraction of AGI) for deductible medical expenses.  
_Description:_ Taxpayers are eligible to deduct the portion of their medical expenses exceeding this fraction of AGI.  
_Notes:_ When using PUF data, lowering this parameter value may produce unexpected results because PUF e17500 variable is zero below the floor.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.075  
2018: 0.075  
2019: 0.075  
2020: 0.075  
2021: 0.075  
2022: 0.075  
2023: 0.075  
2024: 0.075  
2025: 0.075  
2026: 0.075  
_Valid Range:_ min = 0.075 and max = 0.1  
_Out-of-Range Action:_ warn

**Itemized Deductions — Medical Expenses**  
_tc Name:_ ID_Medical_frt_add4aged  
_Title:_ Addon floor (as a decimal fraction of AGI) for deductible medical expenses for elderly filing units.  
_Description:_ Elderly taxpayers have this fraction added to the value of the regular floor rate for deductible medical expenses. This fraction was -0.025 from 2013 to 2016, but that was temporary and it changed to zero beginning in 2017.  
_Notes:_ When using PUF data, changing this parameter value may produce unexpected results because PUF e17500 variable is zero below the floor.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: -0.025  
2014: -0.025  
2015: -0.025  
2016: -0.025  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = -0.025 and max = 0.0  
_Out-of-Range Action:_ warn

**Itemized Deductions — Medical Expenses**  
_tc Name:_ ID_Medical_hc  
_Title:_ Medical expense deduction haircut  
_Description:_ This decimal fraction can be applied to limit the amount of medical expense deduction allowed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Medical Expenses**  
_tc Name:_ ID_Medical_c  
_Title:_ Ceiling on the amount of medical expense deduction allowed (dollars)  
_Description:_ The amount of medical expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — State And Local Income And Sales Taxes**  
_tc Name:_ ID_StateLocalTax_hc  
_Title:_ State and local income and sales taxes deduction haircut.  
_Description:_ This decimal fraction reduces the state and local income and sales tax deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — State And Local Income And Sales Taxes**  
_tc Name:_ ID_StateLocalTax_crt  
_Title:_ Ceiling (as a decimal fraction of AGI) for the combination of all state and local income and sales tax deductions.  
_Description:_ The total deduction for state and local taxes is capped at this fraction of AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — State And Local Income And Sales Taxes**  
_tc Name:_ ID_StateLocalTax_c  
_Title:_ Ceiling on the amount of state and local income and sales taxes deduction allowed (dollars)  
_Description:_ The amount of state and local income and sales taxes deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — State, Local, And Foreign Real Estate Taxes**  
_tc Name:_ ID_RealEstate_hc  
_Title:_ State, local, and foreign real estate taxes deduction haircut.  
_Description:_ This decimal fraction reduces real estate taxes paid eligible to deduct in itemized deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — State, Local, And Foreign Real Estate Taxes**  
_tc Name:_ ID_RealEstate_crt  
_Title:_ Ceiling (as a decimal fraction of AGI) for the combination of all state, local, and foreign real estate tax deductions.  
_Description:_ The total deduction for all real estate taxes is capped at this fraction of AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — State, Local, And Foreign Real Estate Taxes**  
_tc Name:_ ID_RealEstate_c  
_Title:_ Ceiling on the amount of state, local, and foreign real estate taxes deduction allowed (dollars)  
_Description:_ The amount of real estate taxes deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — State And Local Taxes And Real Estate Taxes**  
_tc Name:_ ID_AllTaxes_hc  
_Title:_ State and local income, sales, and real estate tax deduction haircut.  
_Description:_ This decimal fraction reduces all state and local taxes paid eligible to deduct in itemized deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — State And Local Taxes And Real Estate Taxes**  
_tc Name:_ ID_AllTaxes_c  
_Title:_ Ceiling on the amount of state and local income, sales and real estate tax deductions allowed (dollars)  
_Description:_ The amount of state and local income, sales and real estate tax deductions is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2019: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2020: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2021: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2022: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2023: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2024: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2025: [10000.0, 10000.0, 5000.0, 10000.0, 10000.0]  
2026: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Interest Paid**  
_tc Name:_ ID_InterestPaid_hc  
_Title:_ Interest paid deduction haircut  
_Description:_ This decimal fraction can be applied to limit the amount of interest paid deduction allowed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Interest Paid**  
_tc Name:_ ID_InterestPaid_c  
_Title:_ Ceiling on the amount of interest paid deduction allowed (dollars)  
_Description:_ The amount of interest paid deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_crt_all  
_Title:_ Ceiling (as a decimal fraction of AGI) for all charitable contribution deductions  
_Description:_ The total deduction for charity is capped at this fraction of AGI.  
_Notes:_ When using PUF data, raising this parameter value may produce unexpected results because in PUF data the variables e19800 and e20100 are already capped.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.5  
2014: 0.5  
2015: 0.5  
2016: 0.5  
2017: 0.5  
2018: 0.6  
2019: 0.6  
2020: 0.6  
2021: 0.6  
2022: 0.6  
2023: 0.6  
2024: 0.6  
2025: 0.6  
2026: 0.5  
_Valid Range:_ min = 0 and max = 0.6  
_Out-of-Range Action:_ warn

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_crt_noncash  
_Title:_ Ceiling (as a decimal fraction of AGI) for noncash charitable contribution deductions  
_Description:_ The deduction for noncash charity contributions is capped at this fraction of AGI.  
_Notes:_ When using PUF data, raising this parameter value may produce unexpected results because in PUF data the variables e19800 and e20100 are already capped.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.3  
2014: 0.3  
2015: 0.3  
2016: 0.3  
2017: 0.3  
2018: 0.3  
2019: 0.3  
_Valid Range:_ min = 0 and max = 0.3  
_Out-of-Range Action:_ warn

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_frt  
_Title:_ Floor (as a decimal fraction of AGI) for deductible charitable contributions.  
_Description:_ Taxpayers are eligible to deduct the portion of their charitable expense exceeding this fraction of AGI.  
_Notes:_ This parameter allows for implementation of Option 52 from https://www.cbo.gov/sites/default/files/cbofiles/attachments/49638-BudgetOptions.pdf.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_hc  
_Title:_ Charity expense deduction haircut  
_Description:_ This decimal fraction can be applied to limit the amount of charity expense deduction allowed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_c  
_Title:_ Ceiling on the amount of charity expense deduction allowed (dollars)  
_Description:_ The amount of charity expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Charity**  
_tc Name:_ ID_Charity_f  
_Title:_ Floor on the amount of charity expense deduction allowed (dollars)  
_Description:_ Only charitable giving in excess of this dollar amount is eligible for a deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Casualty**  
_tc Name:_ ID_Casualty_frt  
_Title:_ Floor (as a decimal fraction of AGI) for deductible casualty loss.  
_Description:_ Taxpayers are eligible to deduct the portion of their gross casualty losses exceeding this fraction of AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Casualty**  
_tc Name:_ ID_Casualty_hc  
_Title:_ Casualty expense deduction haircut  
_Description:_ This decimal fraction can be applied to limit the amount of casualty expense deduction allowed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Casualty**  
_tc Name:_ ID_Casualty_c  
_Title:_ Ceiling on the amount of casualty expense deduction allowed (dollars)  
_Description:_ The amount of casualty expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Miscellaneous**  
_tc Name:_ ID_Miscellaneous_frt  
_Title:_ Floor (as a decimal fraction of AGI) for deductible miscellaneous expenses.  
_Description:_ Taxpayers are eligible to deduct the portion of their miscellaneous expense exceeding this fraction of AGI.  
_Notes:_ When using PUF data, lowering this parameter value may produce unexpected results because in PUF data the variable e20400 is zero below the floor.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0.02 and max = 1  
_Out-of-Range Action:_ warn

**Itemized Deductions — Miscellaneous**  
_tc Name:_ ID_Miscellaneous_hc  
_Title:_ Miscellaneous expense deduction haircut  
_Description:_ This decimal fraction can be applied to limit the amount of miscellaneous expense deduction allowed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Miscellaneous**  
_tc Name:_ ID_Miscellaneous_c  
_Title:_ Ceiling on the amount of miscellaneous expense deduction allowed (dollars)  
_Description:_ The amount of miscellaneous expense deduction is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Itemized Deduction Limitation**  
_tc Name:_ ID_ps  
_Title:_ Itemized deduction phaseout AGI start (Pease provision)  
_Description:_ The itemized deductions will be reduced for taxpayers with AGI higher than this level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [250000.0, 300000.0, 150000.0, 275000.0, 300000.0]  
2014: [254200.0, 305050.0, 152525.0, 279650.0, 305050.0]  
2015: [258250.0, 309900.0, 154950.0, 284050.0, 309900.0]  
2016: [259400.0, 311300.0, 155650.0, 285350.0, 311300.0]  
2017: [261500.0, 313800.0, 156900.0, 287650.0, 313800.0]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2020: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2021: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2022: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2023: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2024: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2025: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2026: [315093.0, 378112.0, 189056.0, 346603.0, 378112.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Itemized Deduction Limitation**  
_tc Name:_ ID_prt  
_Title:_ Itemized deduction phaseout rate (Pease provision)  
_Description:_ Taxpayers will not be eligible to deduct the full amount of itemized deduction if their AGI is above the phaseout start. The deductible portion would be decreased at this rate for each dollar exceeding the start.  
_Notes:_ This phaseout rate cannot be lower than 0.03 for each dollar, due to limited data on non-itemizers.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.03  
2014: 0.03  
2015: 0.03  
2016: 0.03  
2017: 0.03  
2018: 0.0  
2019: 0.0  
2020: 0.0  
2021: 0.0  
2022: 0.0  
2023: 0.0  
2024: 0.0  
2025: 0.0  
2026: 0.03  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Itemized Deduction Limitation**  
_tc Name:_ ID_crt  
_Title:_ Itemized deduction maximum phaseout as a decimal fraction of total itemized deductions (Pease provision)  
_Description:_ The phaseout amount is capped at this fraction of the original total deduction.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.8  
2014: 0.8  
2015: 0.8  
2016: 0.8  
2017: 0.8  
2018: 1.0  
2019: 1.0  
2020: 1.0  
2021: 1.0  
2022: 1.0  
2023: 1.0  
2024: 1.0  
2025: 1.0  
2026: 0.8  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Surtax On Itemized Deduction Benefits Above An AGI Threshold**  
_tc Name:_ ID_BenefitSurtax_trt  
_Title:_ Surtax rate on the benefits from specified itemized deductions  
_Description:_ The benefit from specified itemized deductions exceeding the credit is taxed at this rate. A surtax rate of 1 strictly limits the benefit from specified itemized deductions to the specified credit. In http://www.nber.org/papers/w16921, Feldstein, Feenberg, and MacGuineas propose a credit of 2% of AGI against a 100% tax rate; in their proposal, however, a broader set of tax benefits, including the employer provided health exclusion, would be taxed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Surtax On Itemized Deduction Benefits Above An AGI Threshold**  
_tc Name:_ ID_BenefitSurtax_crt  
_Title:_ Credit on itemized deduction benefit surtax (decimal fraction of AGI)  
_Description:_ The surtax on specified itemized deductions applies to benefits in excess of this fraction of AGI. In http://www.nber.org/papers/w16921, Feldstein, Feenberg, and MacGuineas propose a credit of 2% of AGI against a 100% tax rate; in their proposal, however, a broader set of tax benefits, including the employer provided health exclusion, would be taxed.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Surtax On Itemized Deduction Benefits Above An AGI Threshold**  
_tc Name:_ ID_BenefitSurtax_em  
_Title:_ Exemption for itemized deduction benefit surtax (dollar AGI threshold)  
_Description:_ This amount is subtracted from itemized deduction benefits in the calculation of the itemized deduction benefit surtax. With ID_BenefitSurtax_crt set to 0.0 and ID_BenefitSurtax_trt set to 1.0, this amount serves as a dollar limit on the value of itemized deductions.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Surtax On Itemized Deduction Benefits Above An AGI Threshold**  
_tc Name:_ ID_BenefitSurtax_Switch  
_Title:_ Deductions subject to the surtax on itemized deduction benefits  
_Description:_ The surtax on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
   for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Itemized Deductions — Ceiling On The Benefit Of Itemized Deductions As A Percent Of Deductible Expenses**  
_tc Name:_ ID_BenefitCap_rt  
_Title:_ Ceiling on the benefits from itemized deductions; decimal fraction of total deductible expenses  
_Description:_ The benefit from specified itemized deductions is capped at this percent of the total deductible expenses.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Itemized Deductions — Ceiling On The Benefit Of Itemized Deductions As A Percent Of Deductible Expenses**  
_tc Name:_ ID_BenefitCap_Switch  
_Title:_ Deductions subject to the cap on itemized deduction benefits  
_Description:_ The cap on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
   for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Itemized Deductions — Ceiling On The Amount Of Itemized Deductions Allowed**  
_tc Name:_ ID_c  
_Title:_ Ceiling on the amount of itemized deductions allowed (dollars)  
_Description:_ The amount of itemized deductions is limited to this dollar amount.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Ceiling On The Amount Of Itemized Deductions Allowed**  
_tc Name:_ ID_AmountCap_rt  
_Title:_ Ceiling on the gross amount of itemized deductions allowed; decimal fraction of AGI  
_Description:_ The gross allowable amount of specified itemized deductions is capped at this percent of AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Itemized Deductions — Ceiling On The Amount Of Itemized Deductions Allowed**  
_tc Name:_ ID_AmountCap_Switch  
_Title:_ Deductions subject to the cap on itemized deduction benefits  
_Description:_ The cap on itemized deduction benefits applies to the benefits derived from the itemized deductions specified with this parameter.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
   for: [med, sltx, retx, cas, misc, int, char]  
2013: [True, True, True, True, True, True, True]  
2014: [True, True, True, True, True, True, True]  
2015: [True, True, True, True, True, True, True]  
2016: [True, True, True, True, True, True, True]  
2017: [True, True, True, True, True, True, True]  
2018: [True, True, True, True, True, True, True]  
2019: [True, True, True, True, True, True, True]  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

#### 3j. Capital Gains And Dividends

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_rt1  
_Title:_ Long term capital gain and qualified dividends (regular/non-AMT) rate 1  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are below threshold 1 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_brk1  
_Title:_ Top of long-term capital gains and qualified dividends (regular/non-AMT) tax bracket 1  
_Description:_ The gains and dividends (stacked on top of regular income) below this are taxed at capital gain rate 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38600.0, 77200.0, 38600.0, 51700.0, 77200.0]  
2019: [39375.0, 78750.0, 39375.0, 52750.0, 78750.0]  
_Valid Range:_ min = 0 and max = CG_brk2  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_rt2  
_Title:_ Long term capital gain and qualified dividends (regular/non-AMT) rate 2  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are below threshold 2 and above threshold 1 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_brk2  
_Title:_ Top of long-term capital gains and qualified dividends (regular/non-AMT) tax bracket 2  
_Description:_ The gains and dividends (stacked on top of regular income) below this and above top of bracket 1 are taxed at capital gain rate 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [425800.0, 479000.0, 239500.0, 452400.0, 479000.0]  
2019: [434550.0, 488850.0, 244425.0, 461700.0, 488850.0]  
_Valid Range:_ min = CG_brk1 and max = CG_brk3  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_rt3  
_Title:_ Long term capital gain and qualified dividends (regular/non-AMT) rate 3  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 2 and below threshold 3 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.2  
2014: 0.2  
2015: 0.2  
2016: 0.2  
2017: 0.2  
2018: 0.2  
2019: 0.2  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_brk3  
_Title:_ Top of long-term capital gains and qualified dividend tax (regular/non-AMT) bracket 3  
_Description:_ The gains and dividends (stacked on top of regular income) below this and above top of bracket 2 are taxed at the capital gain rate 3; above this they are taxed at capital gain rate 4\. Default value is essentially infinity.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = CG_brk2 and max = 9e+99  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Regular - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ CG_rt4  
_Title:_ Long term capital gain and qualified dividends (regular/non-AMT) rate 4  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 3 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_rt1  
_Title:_ Long term capital gain and qualified dividends (AMT) rate 1  
_Description:_ Capital gain and qualified dividends (stacked on top of regular income) below threshold 1 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_brk1  
_Title:_ Top of long-term capital gains and qualified dividends (AMT) tax bracket 1  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this are taxed at AMT capital gain rate 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38600.0, 77200.0, 38600.0, 51700.0, 77200.0]  
2019: [39375.0, 78750.0, 39375.0, 52750.0, 78750.0]  
_Valid Range:_ min = 0 and max = AMT_CG_brk2  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_rt2  
_Title:_ Long term capital gain and qualified dividends (AMT) rate 2  
_Description:_ Capital gain and qualified dividend (stacked on top of regular income) below threshold 2 and above threshold 1 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.15  
2019: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_brk2  
_Title:_ Top of long-term capital gains and qualified dividends (AMT) tax bracket 2  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this threshold and above bracket 1 are taxed at AMT capital gain rate 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [425800.0, 479000.0, 239500.0, 452400.0, 479000.0]  
2019: [434550.0, 488850.0, 244425.0, 461700.0, 488850.0]  
_Valid Range:_ min = AMT_CG_brk1 and max = AMT_CG_brk3  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_rt3  
_Title:_ Long term capital gain and qualified dividends (AMT) rate 3  
_Description:_ The capital gain and qualified dividend (stacked on top of regular income) above threshold 2 and below threshold 3 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.2  
2014: 0.2  
2015: 0.2  
2016: 0.2  
2017: 0.2  
2018: 0.2  
2019: 0.2  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_brk3  
_Title:_ Long term capital gain and qualified dividends (AMT) threshold 3  
_Description:_ The gains and dividends, stacked last, of AMT taxable income below this and above bracket 2 are taxed at capital gain rate 3; above thisthey are taxed at AMT capital gain rate 4\. Default value is essentially infinity.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = AMT_CG_brk2 and max = 9e+99  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — AMT - Long Term Capital Gains And Qualified Dividends**  
_tc Name:_ AMT_CG_rt4  
_Title:_ Long term capital gain and qualified dividends (AMT) rate 4  
_Description:_ The capital gain and dividends (stacked on top of regular income) that are above threshold 3 are taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Tax All Capital Gains And Dividends The Same As Regular Taxable Income**  
_tc Name:_ CG_nodiff  
_Title:_ Long term capital gains and qualified dividends taxed no differently than regular taxable income  
_Description:_ Specifies whether or not long term capital gains and qualified dividends are taxed like regular taxable income.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Tax All Capital Gains And Dividends The Same As Regular Taxable Income**  
_tc Name:_ CG_ec  
_Title:_ Dollar amount of all capital gains and qualified dividends that are excluded from AGI.  
_Description:_ Positive value used only if long term capital gains and qualified dividends taxed no differently than regular taxable income.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Capital Gains And Dividends — Tax All Capital Gains And Dividends The Same As Regular Taxable Income**  
_tc Name:_ CG_reinvest_ec_rt  
_Title:_ Fraction of all capital gains and qualified dividends in excess of the dollar exclusion that are excluded from AGI.  
_Description:_ Positive value used only if long term capital gains and qualified dividends taxed no differently than regular taxable income. To limit the exclusion to capital gains and dividends invested within one year, set to statutory exclusion rate times the fraction of capital gains and qualified dividends in excess of the exclusion that are assumed to be reinvested within the year.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3k. Personal Income

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt1  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 1  
_Description:_ The lowest tax rate, applied to the portion of taxable income below tax bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
2020: 0.1  
2021: 0.1  
2022: 0.1  
2023: 0.1  
2024: 0.1  
2025: 0.1  
2026: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk1  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 1  
_Description:_ Taxable income below this threshold is taxed at tax rate 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [8925.0, 17850.0, 8925.0, 12750.0, 17850.0]  
2014: [9075.0, 18150.0, 9075.0, 12950.0, 18150.0]  
2015: [9225.0, 18450.0, 9225.0, 13150.0, 18450.0]  
2016: [9275.0, 18550.0, 9275.0, 13250.0, 18550.0]  
2017: [9325.0, 18650.0, 9325.0, 13350.0, 18650.0]  
2018: [9525.0, 19050.0, 9525.0, 13600.0, 19050.0]  
2019: [9700.0, 19400.0, 9700.0, 13850.0, 19400.0]  
2020: [9853.26, 19706.52, 9853.26, 14068.83, 19706.52]  
2021: [10068.06, 20136.12, 10068.06, 14375.53, 20136.12]  
2022: [10296.6, 20593.21, 10296.6, 14701.85, 20593.21]  
2023: [10534.45, 21068.91, 10534.45, 15041.46, 21068.91]  
2024: [10768.31, 21536.64, 10768.31, 15375.38, 21536.64]  
2025: [11000.91, 22001.83, 11000.91, 15707.49, 22001.83]  
2026: [11236.0, 22472.0, 11236.0, 16086.0, 22472.0]  
_Valid Range:_ min = 0 and max = II_brk2  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt2  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 2  
_Description:_ The second lowest tax rate, applied to the portion of taxable income below tax bracket 2 and above tax bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.12  
2019: 0.12  
2020: 0.12  
2021: 0.12  
2022: 0.12  
2023: 0.12  
2024: 0.12  
2025: 0.12  
2026: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk2  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 2  
_Description:_ Income below this threshold and above tax bracket 1 is taxed at tax rate 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38700.0, 77400.0, 38700.0, 51800.0, 77400.0]  
2019: [39475.0, 78950.0, 39475.0, 52850.0, 78950.0]  
2020: [40098.7, 80197.41, 40098.7, 53685.03, 80197.41]  
2021: [40972.85, 81945.71, 40972.85, 54855.36, 81945.71]  
2022: [41902.93, 83805.88, 41902.93, 56100.58, 83805.88]  
2023: [42870.89, 85741.8, 42870.89, 57396.5, 85741.8]  
2024: [43822.62, 87645.27, 43822.62, 58670.7, 87645.27]  
2025: [44769.19, 89538.41, 44769.19, 59937.99, 89538.41]  
2026: [45728.0, 91455.0, 45728.0, 61211.0, 91455.0]  
_Valid Range:_ min = II_brk1 and max = II_brk3  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt3  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 3  
_Description:_ The third lowest tax rate, applied to the portion of taxable income below tax bracket 3 and above tax bracket 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.22  
2019: 0.22  
2020: 0.22  
2021: 0.22  
2022: 0.22  
2023: 0.22  
2024: 0.22  
2025: 0.22  
2026: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk3  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 3  
_Description:_ Income below this threshold and above tax bracket 2 is taxed at tax rate 3.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [87850.0, 146400.0, 73200.0, 125450.0, 146400.0]  
2014: [89350.0, 148850.0, 74425.0, 127550.0, 148850.0]  
2015: [90750.0, 151200.0, 75600.0, 129600.0, 151200.0]  
2016: [91150.0, 151900.0, 75950.0, 130150.0, 151900.0]  
2017: [91900.0, 153100.0, 76550.0, 131200.0, 153100.0]  
2018: [82500.0, 165000.0, 82500.0, 82500.0, 165000.0]  
2019: [84200.0, 168400.0, 84200.0, 84200.0, 168400.0]  
2020: [85530.36, 171060.72, 85530.36, 85530.36, 171060.72]  
2021: [87394.92, 174789.84, 87394.92, 87394.92, 174789.84]  
2022: [89378.78, 178757.57, 89378.78, 89378.78, 178757.57]  
2023: [91443.43, 182886.87, 91443.43, 91443.43, 182886.87]  
2024: [93473.47, 186946.96, 93473.47, 93473.47, 186946.96]  
2025: [95492.5, 190985.01, 95492.5, 95492.5, 190985.01]  
2026: [110735.0, 184477.0, 92239.0, 158089.0, 184477.0]  
_Valid Range:_ min = II_brk2 and max = II_brk4  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt4  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 4  
_Description:_ The tax rate applied to the portion of taxable income below tax bracket 4 and above tax bracket 3.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.28  
2014: 0.28  
2015: 0.28  
2016: 0.28  
2017: 0.28  
2018: 0.24  
2019: 0.24  
2020: 0.24  
2021: 0.24  
2022: 0.24  
2023: 0.24  
2024: 0.24  
2025: 0.24  
2026: 0.28  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk4  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 4  
_Description:_ Income below this threshold and above tax bracket 3 is taxed at tax rate 4.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [183250.0, 223050.0, 111525.0, 203150.0, 223050.0]  
2014: [186350.0, 226850.0, 113425.0, 206600.0, 226850.0]  
2015: [189300.0, 230450.0, 115225.0, 209850.0, 230450.0]  
2016: [190150.0, 231450.0, 115725.0, 210800.0, 231450.0]  
2017: [191650.0, 233350.0, 116675.0, 212500.0, 233350.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160725.0, 321450.0, 160725.0, 160700.0, 321450.0]  
2020: [163264.46, 326528.91, 163264.46, 163239.06, 326528.91]  
2021: [166823.63, 333647.24, 166823.63, 166797.67, 333647.24]  
2022: [170610.53, 341221.03, 170610.53, 170583.98, 341221.03]  
2023: [174551.63, 349103.24, 174551.63, 174524.47, 349103.24]  
2024: [178426.68, 356853.33, 178426.68, 178398.91, 356853.33]  
2025: [182280.7, 364561.36, 182280.7, 182252.33, 364561.36]  
2026: [230928.0, 281174.0, 140587.0, 256051.0, 281174.0]  
_Valid Range:_ min = II_brk3 and max = II_brk5  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt5  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 5  
_Description:_ The third highest tax rate, applied to the portion of taxable income below tax bracket 5 and above tax bracket 4.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.33  
2014: 0.33  
2015: 0.33  
2016: 0.33  
2017: 0.33  
2018: 0.32  
2019: 0.32  
2020: 0.32  
2021: 0.32  
2022: 0.32  
2023: 0.32  
2024: 0.32  
2025: 0.32  
2026: 0.33  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk5  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket (upper threshold) 5  
_Description:_ Income below this threshold and above tax bracket 4 is taxed at tax rate 5.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [398350.0, 398350.0, 199175.0, 398350.0, 398350.0]  
2014: [405100.0, 405100.0, 202550.0, 405100.0, 405100.0]  
2015: [411500.0, 411500.0, 205750.0, 411500.0, 411500.0]  
2016: [413350.0, 413350.0, 206675.0, 413350.0, 413350.0]  
2017: [416700.0, 416700.0, 208350.0, 416700.0, 416700.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [204100.0, 408200.0, 204100.0, 204100.0, 408200.0]  
2020: [207324.78, 414649.56, 207324.78, 207324.78, 414649.56]  
2021: [211844.46, 423688.92, 211844.46, 211844.46, 423688.92]  
2022: [216653.33, 433306.66, 216653.33, 216653.33, 433306.66]  
2023: [221658.02, 443316.04, 221658.02, 221658.02, 443316.04]  
2024: [226578.83, 453157.66, 226578.83, 226578.83, 453157.66]  
2025: [231472.93, 462945.87, 231472.93, 231472.93, 462945.87]  
2026: [502101.0, 502101.0, 251050.0, 502101.0, 502101.0]  
_Valid Range:_ min = II_brk4 and max = II_brk6  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt6  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 6  
_Description:_ The second higher tax rate, applied to the portion of taxable income below tax bracket 6 and above tax bracket 5.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.35  
2014: 0.35  
2015: 0.35  
2016: 0.35  
2017: 0.35  
2018: 0.35  
2019: 0.35  
2020: 0.35  
2021: 0.35  
2022: 0.35  
2023: 0.35  
2024: 0.35  
2025: 0.35  
2026: 0.35  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk6  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket 6  
_Description:_ Income below this threshold and above tax bracket 5 is taxed at tax rate 6.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [500000.0, 600000.0, 300000.0, 500000.0, 600000.0]  
2019: [510300.0, 612350.0, 306175.0, 510300.0, 612350.0]  
2020: [518362.74, 622025.13, 311012.56, 518362.74, 622025.13]  
2021: [529663.05, 635585.28, 317792.63, 529663.05, 635585.28]  
2022: [541686.4, 650013.07, 325006.52, 541686.4, 650013.07]  
2023: [554199.36, 665028.37, 332514.17, 554199.36, 665028.37]  
2024: [566502.59, 679792.0, 339895.98, 566502.59, 679792.0]  
2025: [578739.05, 694475.51, 347237.73, 578739.05, 694475.51]  
2026: [504149.0, 567168.0, 283584.0, 535659.0, 567168.0]  
_Valid Range:_ min = II_brk5 and max = II_brk7  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt7  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 7  
_Description:_ The tax rate applied to the portion of taxable income below tax bracket 7 and above tax bracket 6.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.396  
2014: 0.396  
2015: 0.396  
2016: 0.396  
2017: 0.396  
2018: 0.37  
2019: 0.37  
2020: 0.37  
2021: 0.37  
2022: 0.37  
2023: 0.37  
2024: 0.37  
2025: 0.37  
2026: 0.396  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_brk7  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax bracket 7  
_Description:_ Income below this threshold and above tax bracket 6 is taxed at tax rate 7; income above this threshold is taxed at tax rate 8\. Default value is essentially infinity.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = II_brk6 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Regular: Non-AMT, Non-Pass-Through**  
_tc Name:_ II_rt8  
_Title:_ Personal income (regular/non-AMT/non-pass-through) tax rate 8  
_Description:_ The tax rate applied to the portion of taxable income above tax bracket 7.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt1  
_Title:_ Pass-through income tax rate 1  
_Description:_ The lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.1  
2014: 0.1  
2015: 0.1  
2016: 0.1  
2017: 0.1  
2018: 0.1  
2019: 0.1  
2020: 0.1  
2021: 0.1  
2022: 0.1  
2023: 0.1  
2024: 0.1  
2025: 0.1  
2026: 0.1  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk1  
_Title:_ Pass-through income tax bracket (upper threshold) 1  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold is taxed at tax rate 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [8925.0, 17850.0, 8925.0, 12750.0, 17850.0]  
2014: [9075.0, 18150.0, 9075.0, 12950.0, 18150.0]  
2015: [9225.0, 18450.0, 9225.0, 13150.0, 18450.0]  
2016: [9275.0, 18550.0, 9275.0, 13250.0, 18550.0]  
2017: [9325.0, 18650.0, 9325.0, 13350.0, 18650.0]  
2018: [9525.0, 19050.0, 9525.0, 13600.0, 19050.0]  
2019: [9700.0, 19400.0, 9700.0, 13850.0, 19400.0]  
2020: [9853.26, 19706.52, 9853.26, 14068.83, 19706.52]  
2021: [10068.06, 20136.12, 10068.06, 14375.53, 20136.12]  
2022: [10296.6, 20593.21, 10296.6, 14701.85, 20593.21]  
2023: [10534.45, 21068.91, 10534.45, 15041.46, 21068.91]  
2024: [10768.31, 21536.64, 10768.31, 15375.38, 21536.64]  
2025: [11000.91, 22001.83, 11000.91, 15707.49, 22001.83]  
2026: [11236.0, 22472.0, 11236.0, 16086.0, 22472.0]  
_Valid Range:_ min = 0 and max = PT_brk2  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt2  
_Title:_ Pass-through income tax rate 2  
_Description:_ The second lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 2 and above tax bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.15  
2014: 0.15  
2015: 0.15  
2016: 0.15  
2017: 0.15  
2018: 0.12  
2019: 0.12  
2020: 0.12  
2021: 0.12  
2022: 0.12  
2023: 0.12  
2024: 0.12  
2025: 0.12  
2026: 0.15  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk2  
_Title:_ Pass-through income tax bracket (upper threshold) 2  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 1 is taxed at tax rate 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [36250.0, 72500.0, 36250.0, 48600.0, 72500.0]  
2014: [36900.0, 73800.0, 36900.0, 49400.0, 73800.0]  
2015: [37450.0, 74900.0, 37450.0, 50200.0, 74900.0]  
2016: [37650.0, 75300.0, 37650.0, 50400.0, 75300.0]  
2017: [37950.0, 75900.0, 37950.0, 50800.0, 75900.0]  
2018: [38700.0, 77400.0, 38700.0, 51800.0, 77400.0]  
2019: [39475.0, 78950.0, 39475.0, 52850.0, 78950.0]  
2020: [40098.7, 80197.41, 40098.7, 53685.03, 80197.41]  
2021: [40972.85, 81945.71, 40972.85, 54855.36, 81945.71]  
2022: [41902.93, 83805.88, 41902.93, 56100.58, 83805.88]  
2023: [42870.89, 85741.8, 42870.89, 57396.5, 85741.8]  
2024: [43822.62, 87645.27, 43822.62, 58670.7, 87645.27]  
2025: [44769.19, 89538.41, 44769.19, 59937.99, 89538.41]  
2026: [45728.0, 91455.0, 45728.0, 61211.0, 91455.0]  
_Valid Range:_ min = PT_brk1 and max = PT_brk3  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt3  
_Title:_ Pass-through income tax rate 3  
_Description:_ The third lowest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 3 and above tax bracket 2.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.22  
2019: 0.22  
2020: 0.22  
2021: 0.22  
2022: 0.22  
2023: 0.22  
2024: 0.22  
2025: 0.22  
2026: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk3  
_Title:_ Pass-through income tax bracket (upper threshold) 3  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 2 is taxed at tax rate 3.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [87850.0, 146400.0, 73200.0, 125450.0, 146400.0]  
2014: [89350.0, 148850.0, 74425.0, 127550.0, 148850.0]  
2015: [90750.0, 151200.0, 75600.0, 129600.0, 151200.0]  
2016: [91150.0, 151900.0, 75950.0, 130150.0, 151900.0]  
2017: [91900.0, 153100.0, 76550.0, 131200.0, 153100.0]  
2018: [82500.0, 165000.0, 82500.0, 82500.0, 165000.0]  
2019: [84200.0, 168400.0, 84200.0, 84200.0, 168400.0]  
2020: [85530.36, 171060.72, 85530.36, 85530.36, 171060.72]  
2021: [87394.92, 174789.84, 87394.92, 87394.92, 174789.84]  
2022: [89378.78, 178757.57, 89378.78, 89378.78, 178757.57]  
2023: [91443.43, 182886.87, 91443.43, 91443.43, 182886.87]  
2024: [93473.47, 186946.96, 93473.47, 93473.47, 186946.96]  
2025: [95492.5, 190985.01, 95492.5, 95492.5, 190985.01]  
2026: [110735.0, 184477.0, 92239.0, 158089.0, 184477.0]  
_Valid Range:_ min = PT_brk2 and max = PT_brk4  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt4  
_Title:_ Pass-through income tax rate 4  
_Description:_ The tax rate applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 4 and above tax bracket 3.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.28  
2014: 0.28  
2015: 0.28  
2016: 0.28  
2017: 0.28  
2018: 0.24  
2019: 0.24  
2020: 0.24  
2021: 0.24  
2022: 0.24  
2023: 0.24  
2024: 0.24  
2025: 0.24  
2026: 0.28  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk4  
_Title:_ Pass-through income tax bracket (upper threshold) 4  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 3 is taxed at tax rate 4.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [183250.0, 223050.0, 111525.0, 203150.0, 223050.0]  
2014: [186350.0, 226850.0, 113425.0, 206600.0, 226850.0]  
2015: [189300.0, 230450.0, 115225.0, 209850.0, 230450.0]  
2016: [190150.0, 231450.0, 115725.0, 210800.0, 231450.0]  
2017: [191650.0, 233350.0, 116675.0, 212500.0, 233350.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160725.0, 321450.0, 160725.0, 160700.0, 321450.0]  
2020: [163264.46, 326528.91, 163264.46, 163239.06, 326528.91]  
2021: [166823.63, 333647.24, 166823.63, 166797.67, 333647.24]  
2022: [170610.53, 341221.03, 170610.53, 170583.98, 341221.03]  
2023: [174551.63, 349103.24, 174551.63, 174524.47, 349103.24]  
2024: [178426.68, 356853.33, 178426.68, 178398.91, 356853.33]  
2025: [182280.7, 364561.36, 182280.7, 182252.33, 364561.36]  
2026: [230928.0, 281174.0, 140587.0, 256051.0, 281174.0]  
_Valid Range:_ min = PT_brk3 and max = PT_brk5  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt5  
_Title:_ Pass-through income tax rate 5  
_Description:_ The third highest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 5 and above tax bracket 4.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.33  
2014: 0.33  
2015: 0.33  
2016: 0.33  
2017: 0.33  
2018: 0.32  
2019: 0.32  
2020: 0.32  
2021: 0.32  
2022: 0.32  
2023: 0.32  
2024: 0.32  
2025: 0.32  
2026: 0.33  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk5  
_Title:_ Pass-through income tax bracket (upper threshold) 5  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 4 is taxed at tax rate 5.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [398350.0, 398350.0, 199175.0, 398350.0, 398350.0]  
2014: [405100.0, 405100.0, 202550.0, 405100.0, 405100.0]  
2015: [411500.0, 411500.0, 205750.0, 411500.0, 411500.0]  
2016: [413350.0, 413350.0, 206675.0, 413350.0, 413350.0]  
2017: [416700.0, 416700.0, 208350.0, 416700.0, 416700.0]  
2018: [200000.0, 400000.0, 200000.0, 200000.0, 400000.0]  
2019: [204100.0, 408200.0, 204100.0, 204100.0, 408200.0]  
2020: [207324.78, 414649.56, 207324.78, 207324.78, 414649.56]  
2021: [211844.46, 423688.92, 211844.46, 211844.46, 423688.92]  
2022: [216653.33, 433306.66, 216653.33, 216653.33, 433306.66]  
2023: [221658.02, 443316.04, 221658.02, 221658.02, 443316.04]  
2024: [226578.83, 453157.66, 226578.83, 226578.83, 453157.66]  
2025: [231472.93, 462945.87, 231472.93, 231472.93, 462945.87]  
2026: [502101.0, 502101.0, 251050.0, 502101.0, 502101.0]  
_Valid Range:_ min = PT_brk4 and max = PT_brk6  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt6  
_Title:_ Pass-through income tax rate 6  
_Description:_ The second higher tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 6 and above tax bracket 5.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.35  
2014: 0.35  
2015: 0.35  
2016: 0.35  
2017: 0.35  
2018: 0.35  
2019: 0.35  
2020: 0.35  
2021: 0.35  
2022: 0.35  
2023: 0.35  
2024: 0.35  
2025: 0.35  
2026: 0.35  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk6  
_Title:_ Pass-through income tax bracket (upper threshold) 6  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 5 is taxed at tax rate 6.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [400000.0, 450000.0, 225000.0, 425000.0, 450000.0]  
2014: [406750.0, 457600.0, 228800.0, 432200.0, 457600.0]  
2015: [413200.0, 464850.0, 232425.0, 439000.0, 464850.0]  
2016: [415050.0, 466950.0, 233475.0, 441000.0, 466950.0]  
2017: [418400.0, 470700.0, 235350.0, 444550.0, 470700.0]  
2018: [500000.0, 600000.0, 300000.0, 500000.0, 600000.0]  
2019: [510300.0, 612350.0, 306175.0, 510300.0, 612350.0]  
2020: [518362.74, 622025.13, 311012.56, 518362.74, 622025.13]  
2021: [529663.05, 635585.28, 317792.63, 529663.05, 635585.28]  
2022: [541686.4, 650013.07, 325006.52, 541686.4, 650013.07]  
2023: [554199.36, 665028.37, 332514.17, 554199.36, 665028.37]  
2024: [566502.59, 679792.0, 339895.98, 566502.59, 679792.0]  
2025: [578739.05, 694475.51, 347237.73, 578739.05, 694475.51]  
2026: [504149.0, 567168.0, 283584.0, 535659.0, 567168.0]  
_Valid Range:_ min = PT_brk5 and max = PT_brk7  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt7  
_Title:_ Pass-through income tax rate 7  
_Description:_ The highest tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations below tax bracket 7 and above tax bracket 6.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.396  
2014: 0.396  
2015: 0.396  
2016: 0.396  
2017: 0.396  
2018: 0.37  
2019: 0.37  
2020: 0.37  
2021: 0.37  
2022: 0.37  
2023: 0.37  
2024: 0.37  
2025: 0.37  
2026: 0.396  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_brk7  
_Title:_ Extra pass-through income tax bracket  
_Description:_ Income from sole proprietorships, partnerships and S-corporations below this threshold and above tax bracket 6 is taxed at tax rate 7\. Default value is essentially infinity.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = PT_brk6 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_rt8  
_Title:_ Extra pass-through income tax rate  
_Description:_ The extra tax rate, applied to the portion of income from sole proprietorships, partnerships and S-corporations above the tax bracket 7.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_EligibleRate_active  
_Title:_ Share of active business income eligible for PT rate schedule  
_Description:_ Eligibility rate of active business income for separate pass-through rates.  
_Notes:_ Active business income defined as e00900 + e26270  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 1.0  
2014: 1.0  
2015: 1.0  
2016: 1.0  
2017: 1.0  
2018: 1.0  
2019: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_EligibleRate_passive  
_Title:_ Share of passive business income eligible for PT rate schedule  
_Description:_ Eligibility rate of passive business income for mseparate pass-through rates.  
_Notes:_ Passive business income defined as e02000 - e26270  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_wages_active_income  
_Title:_ Wages included in (positive) active business income eligible for PT rates  
_Description:_ Whether active business income eligibility base for PT schedule for includes wages.  
_Notes:_ Only applies if active business income is positive  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_top_stacking  
_Title:_ PT taxable income stacked on top of regular taxable income  
_Description:_ Whether taxable income eligible for PT rate schedule is stacked on top of regular taxable income.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: True  
2014: True  
2015: True  
2016: True  
2017: True  
2018: True  
2019: True  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_rt  
_Title:_ Pass-through qualified business income deduction rate  
_Description:_ Fraction of pass-through business income that may be excluded from taxable income.  
_Notes:_ Applies to e00900 + e26270  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.2  
2019: 0.2  
2020: 0.2  
2021: 0.2  
2022: 0.2  
2023: 0.2  
2024: 0.2  
2025: 0.2  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_taxinc_thd  
_Title:_ Lower threshold of pre-QBID taxable income  
_Description:_ Pre-QBID taxable income above this lower threshold implies the QBID amount begins to be limited.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [157500.0, 315000.0, 157500.0, 157500.0, 315000.0]  
2019: [160700.0, 321400.0, 160725.0, 160700.0, 321400.0]  
2020: [163239.06, 326478.12, 163264.46, 163239.06, 326478.12]  
2021: [166797.67, 333595.34, 166823.63, 166797.67, 333595.34]  
2022: [170583.98, 341167.95, 170610.53, 170583.98, 341167.95]  
2023: [174524.47, 349048.93, 174551.63, 174524.47, 349048.93]  
2024: [178398.91, 356797.82, 178426.68, 178398.91, 356797.82]  
2025: [182252.33, 364504.65, 182280.7, 182252.33, 364504.65]  
2026: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_taxinc_gap  
_Title:_ Dollar gap between upper and lower threshold of pre-QBID taxable income  
_Description:_ Pre-QBID taxable income above this upper threshold implies the QBID amount is even more limited.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [1.0, 1.0, 1.0, 1.0, 1.0]  
2014: [1.0, 1.0, 1.0, 1.0, 1.0]  
2015: [1.0, 1.0, 1.0, 1.0, 1.0]  
2016: [1.0, 1.0, 1.0, 1.0, 1.0]  
2017: [1.0, 1.0, 1.0, 1.0, 1.0]  
2018: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2019: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2020: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2021: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2022: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2023: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2024: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2025: [50000.0, 100000.0, 50000.0, 50000.0, 100000.0]  
2026: [1.0, 1.0, 1.0, 1.0, 1.0]  
_Valid Range:_ min = 1 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_w2_wages_rt  
_Title:_ QBID cap rate on pass-through business W-2 wages paid  
_Description:_ QBID is capped at this fraction of W-2 wages paid by the pass-through business if pre-QBID taxable income is above the QBID thresholds.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.5  
2019: 0.5  
2020: 0.5  
2021: 0.5  
2022: 0.5  
2023: 0.5  
2024: 0.5  
2025: 0.5  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_alt_w2_wages_rt  
_Title:_ Alternative QBID cap rate on pass-through business W-2 wages paid  
_Description:_ QBID is capped at this fraction of W-2 wages paid by the pass-through business plus some fraction of business property if pre-QBID taxable income is above the QBID thresholds and the alternative cap is higher than the main wage-only cap.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.25  
2019: 0.25  
2020: 0.25  
2021: 0.25  
2022: 0.25  
2023: 0.25  
2024: 0.25  
2025: 0.25  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Pass-Through**  
_tc Name:_ PT_qbid_alt_property_rt  
_Title:_ Alternative QBID cap rate on pass-through business property owned  
_Description:_ QBID is capped at this fraction of business property owned plus some fraction of W-2 wages paid by the pass-through business if pre-QBID taxable income is above the QBID thresholds and the alternative cap is higher than the main wage-only cap.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.025  
2019: 0.025  
2020: 0.025  
2021: 0.025  
2022: 0.025  
2023: 0.025  
2024: 0.025  
2025: 0.025  
2026: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_em  
_Title:_ AMT exemption amount  
_Description:_ The amount of AMT taxable income exempted from AMT.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [51900.0, 80800.0, 40400.0, 51900.0, 80800.0]  
2014: [52800.0, 82100.0, 41050.0, 52800.0, 82100.0]  
2015: [53600.0, 83400.0, 41700.0, 53600.0, 83400.0]  
2016: [53900.0, 83800.0, 41900.0, 53900.0, 83800.0]  
2017: [54300.0, 84500.0, 42250.0, 54300.0, 84500.0]  
2018: [70300.0, 109400.0, 54700.0, 70300.0, 109400.0]  
2019: [71700.0, 111700.0, 55850.0, 71700.0, 111700.0]  
2020: [72832.86, 113464.86, 56732.43, 72832.86, 113464.86]  
2021: [74420.62, 115938.39, 57969.2, 74420.62, 115938.39]  
2022: [76109.97, 118570.19, 59285.1, 76109.97, 118570.19]  
2023: [77868.11, 121309.16, 60654.59, 77868.11, 121309.16]  
2024: [79596.78, 124002.22, 62001.12, 79596.78, 124002.22]  
2025: [81316.07, 126680.67, 63340.34, 81316.07, 126680.67]  
2026: [65429.0, 101818.0, 50909.0, 65429.0, 101818.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_prt  
_Title:_ AMT exemption phaseout rate  
_Description:_ AMT exemption will decrease at this rate for each dollar of AMT taxable income exceeding AMT phaseout start.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.25  
2014: 0.25  
2015: 0.25  
2016: 0.25  
2017: 0.25  
2018: 0.25  
2019: 0.25  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_em_ps  
_Title:_ AMT exemption phaseout start  
_Description:_ AMT exemption starts to decrease when AMT taxable income goes beyond this threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [115400.0, 153900.0, 76950.0, 115400.0, 153900.0]  
2014: [117300.0, 156500.0, 78250.0, 117300.0, 156500.0]  
2015: [119200.0, 158900.0, 79450.0, 119200.0, 158900.0]  
2016: [119700.0, 159700.0, 79850.0, 119700.0, 159700.0]  
2017: [120700.0, 160900.0, 80450.0, 120700.0, 160900.0]  
2018: [500000.0, 1000000.0, 500000.0, 500000.0, 1000000.0]  
2019: [510300.0, 1020600.0, 510300.0, 510300.0, 1020600.0]  
2020: [518362.74, 1036725.48, 518362.74, 518362.74, 1036725.48]  
2021: [529663.05, 1059326.1, 529663.05, 529663.05, 1059326.1]  
2022: [541686.4, 1083372.8, 541686.4, 541686.4, 1083372.8]  
2023: [554199.36, 1108398.71, 554199.36, 554199.36, 1108398.71]  
2024: [566502.59, 1133005.16, 566502.59, 566502.59, 1133005.16]  
2025: [578739.05, 1157478.07, 578739.05, 578739.05, 1157478.07]  
2026: [145437.0, 193876.0, 96938.0, 145437.0, 193876.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_rt1  
_Title:_ AMT rate 1  
_Description:_ The tax rate applied to the portion of AMT taxable income below the surtax threshold, AMT bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.26  
2014: 0.26  
2015: 0.26  
2016: 0.26  
2017: 0.26  
2018: 0.26  
2019: 0.26  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_brk1  
_Title:_ AMT bracket 1 (upper threshold)  
_Description:_ AMT taxable income below this is subject to AMT rate 1 and above it is subject to AMT rate 1 + the additional AMT rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 179500.0  
2014: 182500.0  
2015: 185400.0  
2016: 186300.0  
2017: 187800.0  
2018: 191100.0  
2019: 194800.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Personal Income — Alternative Minimum Tax**  
_tc Name:_ AMT_rt2  
_Title:_ Additional AMT rate for AMT taxable income above AMT bracket 1  
_Description:_ The additional tax rate applied to the portion of AMT income above the AMT bracket 1.  
_Notes:_ This is the additional tax rate (on top of AMT rate 1) for AMT income above AMT bracket 1.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.02  
2014: 0.02  
2015: 0.02  
2016: 0.02  
2017: 0.02  
2018: 0.02  
2019: 0.02  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3l. Other Taxes

**Other Taxes — Net Investment Income Tax**  
_tc Name:_ NIIT_thd  
_Title:_ Net Investment Income Tax modified AGI threshold  
_Description:_ If modified AGI is more than this threshold, filing unit is subject to the Net Investment Income Tax.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2014: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2015: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2016: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2017: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2018: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
2019: [200000.0, 250000.0, 125000.0, 200000.0, 250000.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Taxes — Net Investment Income Tax**  
_tc Name:_ NIIT_PT_taxed  
_Title:_ Whether or not partnership and S-corp income is in NIIT base  
_Description:_ false ==> partnership and S-corp income excluded from NIIT base; true ==> partnership and S-corp income is in NIIT base.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Other Taxes — Net Investment Income Tax**  
_tc Name:_ NIIT_rt  
_Title:_ Net Investment Income Tax rate  
_Description:_ If modified AGI exceeds NIIT_thd, all net investment income is taxed at this rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.038  
2014: 0.038  
2015: 0.038  
2016: 0.038  
2017: 0.038  
2018: 0.038  
2019: 0.038  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3m. Refundable Credits

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_c  
_Title:_ Maximum earned income credit  
_Description:_ This is the maximum amount of earned income credit taxpayers are eligible for; it depends on how many kids they have.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [0kids, 1kid, 2kids, 3+kids]  
2013: [487.0, 3250.0, 5372.0, 6044.0]  
2014: [496.0, 3305.0, 5460.0, 6143.0]  
2015: [503.0, 3359.0, 5548.0, 6242.0]  
2016: [506.0, 3373.0, 5572.0, 6269.0]  
2017: [510.0, 3400.0, 5616.0, 6318.0]  
2018: [519.0, 3461.0, 5716.0, 6431.0]  
2019: [529.0, 3526.0, 5828.0, 6557.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_rt  
_Title:_ Earned income credit phasein rate  
_Description:_ Pre-phaseout credit is minimum of this rate times earnings and the maximum earned income credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [0kids, 1kid, 2kids, 3+kids]  
2013: [0.0765, 0.34, 0.4, 0.45]  
2014: [0.0765, 0.34, 0.4, 0.45]  
2015: [0.0765, 0.34, 0.4, 0.45]  
2016: [0.0765, 0.34, 0.4, 0.45]  
2017: [0.0765, 0.34, 0.4, 0.45]  
2018: [0.0765, 0.34, 0.4, 0.45]  
2019: [0.0765, 0.34, 0.4, 0.45]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_basic_frac  
_Title:_ Fraction of maximum earned income credit paid at zero earnings  
_Description:_ This fraction of EITC_c is always paid as a credit and one minus this fraction is applied to the phasein rate, EITC_rt. This fraction is zero under current law.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0.0 and max = 1.0  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_prt  
_Title:_ Earned income credit phaseout rate  
_Description:_ Earned income credit begins to decrease at the this rate when AGI is higher than earned income credit phaseout start AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [0kids, 1kid, 2kids, 3+kids]  
2013: [0.0765, 0.1598, 0.2106, 0.2106]  
2014: [0.0765, 0.1598, 0.2106, 0.2106]  
2015: [0.0765, 0.1598, 0.2106, 0.2106]  
2016: [0.0765, 0.1598, 0.2106, 0.2106]  
2017: [0.0765, 0.1598, 0.2106, 0.2106]  
2018: [0.0765, 0.1598, 0.2106, 0.2106]  
2019: [0.0765, 0.1598, 0.2106, 0.2106]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_ps  
_Title:_ Earned income credit phaseout start AGI  
_Description:_ If AGI is higher than this threshold, the amount of EITC will start to decrease at the phaseout rate.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [0kids, 1kid, 2kids, 3+kids]  
2013: [7970.0, 17530.0, 17530.0, 17530.0]  
2014: [8110.0, 17830.0, 17830.0, 17830.0]  
2015: [8250.0, 18150.0, 18150.0, 18150.0]  
2016: [8270.0, 18190.0, 18190.0, 18190.0]  
2017: [8340.0, 18340.0, 18340.0, 18340.0]  
2018: [8490.0, 18660.0, 18660.0, 18660.0]  
2019: [8650.0, 19030.0, 19030.0, 19030.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_ps_MarriedJ  
_Title:_ Extra earned income credit phaseout start AGI for married filling jointly  
_Description:_ This is the additional amount added on the regular phaseout start amount for taxpayers with filling status of married filing jointly.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [0kids, 1kid, 2kids, 3+kids]  
2013: [5340.0, 5340.0, 5340.0, 5340.0]  
2014: [5430.0, 5430.0, 5430.0, 5430.0]  
2015: [5500.0, 5500.0, 5500.0, 5500.0]  
2016: [5550.0, 5550.0, 5550.0, 5550.0]  
2017: [5590.0, 5590.0, 5590.0, 5590.0]  
2018: [5680.0, 5690.0, 5690.0, 5690.0]  
2019: [5800.0, 5790.0, 5790.0, 5790.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_MinEligAge  
_Title:_ Minimum Age for Childless EITC Eligibility  
_Description:_ For a childless filing unit, at least one individual's age needs to be no less than this age (but no greater than the EITC_MaxEligAge) in order to be eligible for an earned income tax credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 25  
2014: 25  
2015: 25  
2016: 25  
2017: 25  
2018: 25  
2019: 25  
_Valid Range:_ min = 0 and max = 125  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_MaxEligAge  
_Title:_ Maximum Age for Childless EITC Eligibility  
_Description:_ For a childless filing unit, at least one individual's age needs to be no greater than this age (but no less than the EITC_MinEligAge) in order to be eligible for an earned income tax credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 64  
2014: 64  
2015: 64  
2016: 64  
2017: 64  
2018: 64  
2019: 64  
_Valid Range:_ min = 0 and max = 125  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_InvestIncome_c  
_Title:_ Maximum investment income before EITC reduction  
_Description:_ The EITC amount is reduced when investment income exceeds this ceiling.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 3300.0  
2014: 3350.0  
2015: 3400.0  
2016: 3400.0  
2017: 3450.0  
2018: 3500.0  
2019: 3600.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_excess_InvestIncome_rt  
_Title:_ Rate of EITC reduction when investment income exceeds ceiling  
_Description:_ The EITC amount is reduced at this rate per dollar of investment income exceeding the ceiling.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 9e+99  
2014: 9e+99  
2015: 9e+99  
2016: 9e+99  
2017: 9e+99  
2018: 9e+99  
2019: 9e+99  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_indiv  
_Title:_ EITC is computed for each spouse based on individual earnings  
_Description:_ Current-law value is false implying EITC is filing-unit based; a value of true implies EITC is computed for each individual wage earner. The additional phaseout start for joint filers is not affected by this parameter, nor are investment income and age eligibilty rules.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Refundable Credits — Earned Income Tax Credit**  
_tc Name:_ EITC_sep_filers_elig  
_Title:_ Separate filers are eligibile for the EITC  
_Description:_ Current-law value is false, implying ineligibility.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_c  
_Title:_ New refundable child tax credit maximum amount per child  
_Description:_ In addition to all credits currently available for dependents, this parameter gives each qualifying child a new refundable credit with this maximum amount.  
_Notes:_ Child age qualification for the new child tax credit is the same as under current-law Child Tax Credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_c_under5_bonus  
_Title:_ Bonus new refundable child tax credit maximum for qualifying children under five  
_Description:_ The maximum amount of the new refundable child tax credit allowed for each child is increased by this amount for qualifying children under 5 years old.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_for_all  
_Title:_ Whether or not maximum amount of the new refundable child tax credit is available to all  
_Description:_ The maximum amount of the new refundable child tax credit does not depend on AGI when true; otherwise, see CTC_new_rt.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_rt  
_Title:_ New refundable child tax credit amount phasein rate  
_Description:_ The maximum amount of the new child tax credit is increased at this rate per dollar of positive AGI until CTC_new_c times the number of qualified children is reached if CTC_new_for_all is false; if CTC_new_for_all is true, there is no AGI limitation to the maximum amount.  
_Notes:_ Child age qualification for the new child tax credit is the same as under current-law Child Tax Credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_ps  
_Title:_ New refundable child tax credit phaseout starting AGI  
_Description:_ The total amount of new child tax credit is reduced for taxpayers with AGI higher than this level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_prt  
_Title:_ New refundable child tax credit amount phaseout rate  
_Description:_ The total amount of the new child tax credit is reduced at this rate per dollar exceeding the phaseout starting AGI, CTC_new_ps.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_refund_limited  
_Title:_ New child tax credit refund limited to a decimal fraction of payroll taxes  
_Description:_ Specifies whether the new child tax credit refund is limited by the new child tax credit refund limit rate (_CTC_new_refund_limit_payroll_rt).  
_Notes:_ Set this parameter to true to limit the refundability or false to allow full refundability for all taxpayers.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_refund_limit_payroll_rt  
_Title:_ New child tax credit refund limit rate (decimal fraction of payroll taxes)  
_Description:_ The fraction of payroll taxes (employee plus employer shares, but excluding all Medicare payroll taxes) that serves as a limit to the amount of new child tax credit that can be refunded.  
_Notes:_ Set this parameter to zero for no refundability; set it to 9e99 for unlimited refundability for taxpayers with payroll tax liabilities.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — New Refundable Child Tax Credit**  
_tc Name:_ CTC_new_refund_limited_all_payroll  
_Title:_ New child tax credit refund limit applies to all FICA taxes, not just OASDI  
_Description:_ Specifies whether the new child tax credit refund limit rate (_CTC_new_refund_limit_payroll_rt) applies to all FICA taxes (true) or just OASDI taxes (false).  
_Notes:_ If the new CTC is limited, set this parameter to true to limit the refundability to all FICA taxes or false to limit refundabiity to OASDI taxes.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Refundable Credits — Personal Refundable Credit**  
_tc Name:_ II_credit  
_Title:_ Personal refundable credit maximum amount  
_Description:_ This credit amount is fully refundable and is phased out based on AGI. It is available to tax units who would otherwise not file.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Personal Refundable Credit**  
_tc Name:_ II_credit_ps  
_Title:_ Personal refundable credit phaseout start  
_Description:_ The personal refundable credit amount will be reduced for taxpayers with AGI higher than this threshold level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Personal Refundable Credit**  
_tc Name:_ II_credit_prt  
_Title:_ Personal refundable credit phaseout rate  
_Description:_ The personal refundable credit amount will be reduced at this rate for each dollar of AGI exceeding the II_credit_ps threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Refundable Credits — Refundable Payroll Tax Credit**  
_tc Name:_ RPTC_c  
_Title:_ Maximum refundable payroll tax credit  
_Description:_ This is the maximum amount of the refundable payroll tax credit for each taxpayer/spouse.  
_Notes:_ Positive values of RPTC_c and RPTC_rt can be used to emulate a payroll tax exemption, the implied value of which is RPTC_c divided by RPTC_rt.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Refundable Credits — Refundable Payroll Tax Credit**  
_tc Name:_ RPTC_rt  
_Title:_ Refundable payroll tax credit phasein rate  
_Description:_ Pre-phaseout credit is minimum of this rate times earnings and the maximum refundable payroll tax credit, where earnings is defined as in FICA and SECA.  
_Notes:_ Positive values of RPTC_c and RPTC_rt can be used to emulate a payroll tax exemption, the implied value of which is RPTC_c divided by RPTC_rt.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3n. Surtaxes

**Surtaxes — New Minimum Tax**  
_tc Name:_ FST_AGI_trt  
_Title:_ New minimum tax; rate as a decimal fraction of AGI  
_Description:_ Individual income taxes and the employee share of payroll taxes are credited against this minimum tax, so the surtax is the difference between the tax rate times AGI and the credited taxes. The new minimum tax is similar to the Fair Share Tax, except that no credits are exempted from the base.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Surtaxes — New Minimum Tax**  
_tc Name:_ FST_AGI_thd_lo  
_Title:_ Minimum AGI needed to be subject to the new minimum tax  
_Description:_ A taxpayer is only subject to the new minimum tax if they exceed this level of AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2014: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2015: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2016: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2017: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2018: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
2019: [1000000.0, 1000000.0, 500000.0, 1000000.0, 1000000.0]  
_Valid Range:_ min = 0 and max = FST_AGI_thd_hi  
_Out-of-Range Action:_ error

**Surtaxes — New Minimum Tax**  
_tc Name:_ FST_AGI_thd_hi  
_Title:_ AGI level at which the New Minimum Tax is fully phased in  
_Description:_ The new minimum tax will be fully phased in at this level of AGI. If there is no phase-in, this upper threshold should be set equal to the lower AGI threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2014: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2015: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2016: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2017: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2018: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
2019: [2000000.0, 2000000.0, 1000000.0, 2000000.0, 2000000.0]  
_Valid Range:_ min = FST_AGI_thd_lo and max = 9e+99  
_Out-of-Range Action:_ error

**Surtaxes — New AGI Surtax**  
_tc Name:_ AGI_surtax_trt  
_Title:_ New AGI surtax rate  
_Description:_ The surtax rate is applied to the portion of Adjusted Gross Income above the AGI surtax threshold.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Surtaxes — New AGI Surtax**  
_tc Name:_ AGI_surtax_thd  
_Title:_ Threshold for the new AGI surtax  
_Description:_ The aggregate gross income above this AGI surtax threshold is taxed at surtax rate on AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2014: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2015: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2016: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2017: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Surtaxes — Lump-Sum Tax**  
_tc Name:_ LST  
_Title:_ Dollar amount of lump-sum tax  
_Description:_ The lump-sum tax is levied on every member of a tax filing unit. The lump-sum tax is included only in combined taxes; it is not included in income or payroll taxes.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = -9e+99 and max = 9e+99  
_Out-of-Range Action:_ error

#### 3o. Universal Basic Income

**Universal Basic Income — UBI Benefits**  
_tc Name:_ UBI_u18  
_Title:_ UBI benefit for those under 18  
_Description:_ UBI benefit provided to people under 18.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Universal Basic Income — UBI Benefits**  
_tc Name:_ UBI_1820  
_Title:_ UBI benefit for those 18 through 20  
_Description:_ UBI benefit provided to people 18-20 years of age.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Universal Basic Income — UBI Benefits**  
_tc Name:_ UBI_21  
_Title:_ UBI benefit for those 21 and over  
_Description:_ UBI benefit provided to people 21 and over.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Universal Basic Income — UBI Taxability**  
_tc Name:_ UBI_ecrt  
_Title:_ Fraction of UBI benefits excluded from AGI  
_Description:_ One minus this fraction of UBI benefits are taxable and will be added to AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

#### 3p. Benefits

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_ssi_repeal  
_Title:_ SSI benefit repeal switch  
_Description:_ SSI benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_housing_repeal  
_Title:_ Housing benefit repeal switch  
_Description:_ Housing benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_snap_repeal  
_Title:_ SNAP benefit repeal switch  
_Description:_ SNAP benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_tanf_repeal  
_Title:_ TANF benefit repeal switch  
_Description:_ TANF benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_vet_repeal  
_Title:_ Veterans benefit repeal switch  
_Description:_ Veterans benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_wic_repeal  
_Title:_ WIC benefit repeal switch  
_Description:_ WIC benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_mcare_repeal  
_Title:_ Medicare benefit repeal switch  
_Description:_ Medicare benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_mcaid_repeal  
_Title:_ Medicaid benefit repeal switch  
_Description:_ Medicaid benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_oasdi_repeal  
_Title:_ Social Security benefit repeal switch  
_Description:_ Social Security benefits (e02400) can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_ui_repeal  
_Title:_ Unemployment insurance benefit repeal switch  
_Description:_ Unemployment insurance benefits (e02300) can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Benefits — Benefit Repeal**  
_tc Name:_ BEN_other_repeal  
_Title:_ Other benefit repeal switch  
_Description:_ Other benefits can be repealed by switching this parameter to true.  
_Has An Effect When Using:_   _PUF data:_ False   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

#### 3q. Other Parameters

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ SS_percentage1  
_Title:_ Social Security taxable income decimal fraction 1  
_Description:_ Under current law if their provisional income is above the first threshold for Social Security taxability but below the second threshold, taxpayers need to apply this fraction to both the excess of their provisional income over the first threshold and their Social Security benefits, and then include the smaller one in their AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.5  
2014: 0.5  
2015: 0.5  
2016: 0.5  
2017: 0.5  
2018: 0.5  
2019: 0.5  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ SS_percentage2  
_Title:_ Social Security taxable income decimal fraction 2  
_Description:_ Under current law if their provisional income is above the second threshold for Social Security taxability, taxpayers need to apply this fraction to both the excess of their provisional income over the second threshold and their social security benefits, and then include the smaller one in their AGI.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.85  
2014: 0.85  
2015: 0.85  
2016: 0.85  
2017: 0.85  
2018: 0.85  
2019: 0.85  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ II_em_ps  
_Title:_ Personal exemption phaseout starting income  
_Description:_ If taxpayers' AGI is above this level, their personal exemption will start to decrease at the personal exemption phaseout rate (PEP provision).  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [250000.0, 300000.0, 150000.0, 275000.0, 300000.0]  
2014: [254200.0, 305050.0, 152525.0, 279650.0, 305050.0]  
2015: [258250.0, 309900.0, 154950.0, 284040.0, 309900.0]  
2016: [259400.0, 311300.0, 155650.0, 285350.0, 311300.0]  
2017: [261500.0, 313800.0, 156900.0, 287650.0, 313800.0]  
2018: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
2019: [9e+99, 9e+99, 9e+99, 9e+99, 9e+99]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ STD_Dep  
_Title:_ Standard deduction for dependents  
_Description:_ This is the maximum standard deduction for dependents.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 1000.0  
2014: 1000.0  
2015: 1050.0  
2016: 1050.0  
2017: 1050.0  
2018: 1050.0  
2019: 1100.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ STD_allow_charity_ded_nonitemizers  
_Title:_ Allow standard deduction filers to take the charitable contributions deduction  
_Description:_ Extends the charitable contributions deduction to taxpayers who take the standard deduction. The same ceilings, floor, and haircuts applied to itemized deduction for charitable contributions also apply here.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ bool  
_Known Values:_  
2013: False  
2014: False  
2015: False  
2016: False  
2017: False  
2018: False  
2019: False  
_Valid Range:_ min = False and max = True  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ AMT_child_em  
_Title:_ Child AMT exemption additional income base  
_Description:_ The child's AMT exemption is capped by this amount plus the child's earned income.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 7150.0  
2014: 7250.0  
2015: 7400.0  
2016: 7400.0  
2017: 7500.0  
2018: 7600.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ AMT_child_em_c_age  
_Title:_ Age ceiling for special AMT exemption  
_Description:_ Individuals under this age must use the child AMT exemption rules.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ int  
_Known Values:_  
2013: 18  
2014: 18  
2015: 18  
2016: 18  
2017: 18  
2018: 18  
2019: 18  
_Valid Range:_ min = 0 and max = 30  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ AMT_em_pe  
_Title:_ AMT exemption phaseout ending AMT taxable income for Married filing Separately  
_Description:_ The AMT exemption is entirely disallowed beyond this AMT taxable income level for individuals who are married but filing separately.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 238550.0  
2014: 242450.0  
2015: 246250.0  
2016: 247450.0  
2017: 249450.0  
2018: 718800.0  
2019: 733700.0  
2020: 745292.46  
2021: 761539.84  
2022: 778826.79  
2023: 796817.69  
2024: 814507.04  
2025: 832100.39  
2026: 300574.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ LLC_Expense_c  
_Title:_ Lifetime learning credit expense limit  
_Description:_ The maximum expense eligible for lifetime learning credit, per child.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 10000.0  
2014: 10000.0  
2015: 10000.0  
2016: 10000.0  
2017: 10000.0  
2018: 10000.0  
2019: 10000.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ ETC_pe_Single  
_Title:_ Education tax credit phaseout ends (Single)  
_Description:_ The education tax credit will be zero for those taxpayers of single filing status with modified AGI (in thousands) higher than this level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 63.0  
2014: 64.0  
2015: 65.0  
2016: 65.0  
2017: 66.0  
2018: 67.0  
2019: 68.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ ETC_pe_Married  
_Title:_ Education tax credit phaseout ends (Married)  
_Description:_ The education tax credit will be zero for those taxpayers of married filing status with modified AGI level (in thousands) higher than this level.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ False  
_Can Be Inflation Indexed:_ True     _Is Inflation Indexed:_ True  
_Value Type:_ float  
_Known Values:_  
2013: 127.0  
2014: 128.0  
2015: 130.0  
2016: 131.0  
2017: 132.0  
2018: 134.0  
2019: 136.0  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ CR_Charity_rt  
_Title:_ Charity Credit rate  
_Description:_ If greater than zero, this decimal fraction represents the portion of total charitable contributions provided as a nonrefundable tax credit.  
_Notes:_ Credit claimed will be (rt) * (e19800 + e20100)  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ CR_Charity_f  
_Title:_ Charity Credit Floor  
_Description:_ Only charitable giving in excess of this dollar amount is eligible for the charity credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
   for: [single, mjoint, mseparate, headhh, widow]  
2013: [0.0, 0.0, 0.0, 0.0, 0.0]  
2014: [0.0, 0.0, 0.0, 0.0, 0.0]  
2015: [0.0, 0.0, 0.0, 0.0, 0.0]  
2016: [0.0, 0.0, 0.0, 0.0, 0.0]  
2017: [0.0, 0.0, 0.0, 0.0, 0.0]  
2018: [0.0, 0.0, 0.0, 0.0, 0.0]  
2019: [0.0, 0.0, 0.0, 0.0, 0.0]  
_Valid Range:_ min = 0 and max = 9e+99  
_Out-of-Range Action:_ error

**Other Parameters — Not in Tax-Brain webapp**  
_tc Name:_ CR_Charity_frt  
_Title:_ Charity Credit Floor Rate  
_Description:_ Only charitable giving in excess of this decimal fraction of AGI is eligible for the charity credit.  
_Has An Effect When Using:_   _PUF data:_ True   _CPS data:_ True  
_Can Be Inflation Indexed:_ False     _Is Inflation Indexed:_ False  
_Value Type:_ float  
_Known Values:_  
2013: 0.0  
2014: 0.0  
2015: 0.0  
2016: 0.0  
2017: 0.0  
2018: 0.0  
2019: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

### 4\. Input Variables

This section contains documentation of input variables in a format that is easy to search and print. The input variables are ordered alphabetically by name. There are no subsections, just a long list of input variables that Tax-Calculator is programmed to use in its calculations. The Availability information indicates which input data files contain the variable.

_Input Variable Name:_ **DSI**  
_Description:_ 1 if claimed as dependent on another return; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 6a

_Input Variable Name:_ **EIC**  
_Description:_ number of EIC qualifying children (range: 0 to 3)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch EIC

_Input Variable Name:_ **FLPDYR**  
_Description:_ Calendar year for which taxes are calculated  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040

_Input Variable Name:_ **MARS**  
**_Required Input Variable_**  
_Description:_ Filing (marital) status: line number of the checked box [1=single, 2=joint, 3=separate, 4=household-head, 5=widow(er)]  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Input Variable Name:_ **MIDR**  
_Description:_ 1 if separately filing spouse itemizes; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 39b

_Input Variable Name:_ **PT_SSTB_income**  
_Description:_ Value of one implies business income is from a specified service trade or business (SSTB); value of zero implies business income is from a qualified trade or business  
_Datatype:_ integer  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **PT_binc_w2_wages**  
_Description:_ Filing unit's share of total W-2 wages paid by the pass-through business  
_Datatype:_ real  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **PT_ubia_property**  
_Description:_ Filing unit's share of total business property owned by the pass-through business  
_Datatype:_ real  
_Availability:_  
_IRS Form Location:_  
2018-20??: specified in custom data

_Input Variable Name:_ **RECID**  
**_Required Input Variable_**  
_Description:_ Unique numeric identifier for filing unit; appears as RECID variable in tc CLI minimal output  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: private info

_Input Variable Name:_ **XTOT**  
_Description:_ Total number of exemptions for filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 6d

_Input Variable Name:_ **a_lineno**  
_Description:_ CPS line number for the person record of the head of the tax filing unit (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **age_head**  
_Description:_ Age in years of taxpayer (i.e. primary adult)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **age_spouse**  
_Description:_ Age in years of spouse (i.e. secondary adult if present)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **agi_bin**  
_Description:_ Historical AGI category used in data extrapolation  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: not used in tax calculations

_Input Variable Name:_ **blind_head**  
_Description:_ 1 if taxpayer is blind; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 39a

_Input Variable Name:_ **blind_spouse**  
_Description:_ 1 if spouse is blind; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 39a

_Input Variable Name:_ **cmbtp**  
_Description:_ Estimate of income on (AMT) Form 6251 but not in AGI  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251 and 1040

_Input Variable Name:_ **data_source**  
_Description:_ 1 if unit is created primarily from IRS-SOI PUF data; 0 if created primarily from CPS data (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **e00200**  
_Description:_ Wages, salaries, and tips for filing unit net of pension contributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7

_Input Variable Name:_ **e00200p**  
_Description:_ Wages, salaries, and tips for taxpayer net of pension contributions (pencon_p)  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7 component

_Input Variable Name:_ **e00200s**  
_Description:_ Wages, salaries, and tips for spouse net of pension contributions (pencon_s)  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 7 component

_Input Variable Name:_ **e00300**  
_Description:_ Taxable interest income  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 8a

_Input Variable Name:_ **e00400**  
_Description:_ Tax-exempt interest income  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 8b

_Input Variable Name:_ **e00600**  
_Description:_ Ordinary dividends included in AGI  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 9a

_Input Variable Name:_ **e00650**  
_Description:_ Qualified dividends included in ordinary dividends  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 9b

_Input Variable Name:_ **e00700**  
_Description:_ Taxable refunds of state and local income taxes  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 10

_Input Variable Name:_ **e00800**  
_Description:_ Alimony received  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 11

_Input Variable Name:_ **e00900**  
_Description:_ Sch C business net profit/loss for filing unit  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12

_Input Variable Name:_ **e00900p**  
_Description:_ Sch C business net profit/loss for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12 component

_Input Variable Name:_ **e00900s**  
_Description:_ Sch C business net profit/loss for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 12 component

_Input Variable Name:_ **e01100**  
_Description:_ Capital gain distributions not reported on Sch D  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 13

_Input Variable Name:_ **e01200**  
_Description:_ Other net gain/loss from Form 4797  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 14

_Input Variable Name:_ **e01400**  
_Description:_ Taxable IRA distributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 15b

_Input Variable Name:_ **e01500**  
_Description:_ Total pensions and annuities  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 16a

_Input Variable Name:_ **e01700**  
_Description:_ Taxable pensions and annuities  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 16b

_Input Variable Name:_ **e02000**  
_Description:_ Sch E total rental, royalty, partnership, S-corporation, etc, income/loss (includes e26270 and e27200)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 17

_Input Variable Name:_ **e02100**  
_Description:_ Farm net income/loss for filing unit from Sch F  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18

_Input Variable Name:_ **e02100p**  
_Description:_ Farm net income/loss for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18 component

_Input Variable Name:_ **e02100s**  
_Description:_ Farm net income/loss for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 18 component

_Input Variable Name:_ **e02300**  
_Description:_ Unemployment insurance benefits  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 19

_Input Variable Name:_ **e02400**  
_Description:_ Total social security (OASDI) benefits  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 20a

_Input Variable Name:_ **e03150**  
_Description:_ Total deductible IRA contributions  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 32

_Input Variable Name:_ **e03210**  
_Description:_ Student loan interest  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 33

_Input Variable Name:_ **e03220**  
_Description:_ Educator expenses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 23

_Input Variable Name:_ **e03230**  
_Description:_ Tuition and fees from Form 8917  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 34

_Input Variable Name:_ **e03240**  
_Description:_ Domestic production activities from Form 8903  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 35

_Input Variable Name:_ **e03270**  
_Description:_ Self-employed health insurance deduction  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 29

_Input Variable Name:_ **e03290**  
_Description:_ Health savings account deduction from Form 8889  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 25

_Input Variable Name:_ **e03300**  
_Description:_ Contributions to SEP, SIMPLE and qualified plans  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 line 28

_Input Variable Name:_ **e03400**  
_Description:_ Penalty on early withdrawal of savings  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 30

_Input Variable Name:_ **e03500**  
_Description:_ Alimony paid  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 line 31a

_Input Variable Name:_ **e07240**  
_Description:_ Retirement savings contributions credit from Form 8880  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 50  
2014-2016: 1040 line 51

_Input Variable Name:_ **e07260**  
_Description:_ Residential energy credit from Form 5695  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 52  
2014-2016: 1040 line 53

_Input Variable Name:_ **e07300**  
_Description:_ Foreign tax credit from Form 1116  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 47  
2014-2016: 1040 line 48

_Input Variable Name:_ **e07400**  
_Description:_ General business credit from Form 3800  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53a  
2014-2016: 1040 line 54a

_Input Variable Name:_ **e07600**  
_Description:_ Prior year minimum tax credit from Form 8801  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53b  
2014-2016: 1040 line 54b

_Input Variable Name:_ **e09700**  
_Description:_ Recapture of Investment Credit  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2015: 4255 line 15  
2016-2016: 4255 line 20

_Input Variable Name:_ **e09800**  
_Description:_ Unreported payroll taxes from Form 4137 or 8919  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 57  
2014-2016: 1040 line 58

_Input Variable Name:_ **e09900**  
_Description:_ Penalty tax on qualified retirement plans  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 58  
2014-2016: 1040 line 59

_Input Variable Name:_ **e11200**  
_Description:_ Excess payroll (FICA/RRTA) tax withheld  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 69  
2014-2016: 1040 line 71

_Input Variable Name:_ **e17500**  
_Description:_ Itemizable medical and dental expenses. WARNING: this variable is zero below the floor in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 1

_Input Variable Name:_ **e18400**  
_Description:_ Itemizable state and local income/sales taxes  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 5

_Input Variable Name:_ **e18500**  
_Description:_ Itemizable real-estate taxes paid  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 6

_Input Variable Name:_ **e19200**  
_Description:_ Itemizable interest paid  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 15

_Input Variable Name:_ **e19800**  
_Description:_ Itemizable charitable giving: cash/check contributions. WARNING: this variable is already capped in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 16

_Input Variable Name:_ **e20100**  
_Description:_ Itemizable charitable giving: other than cash/check contributions. WARNING: this variable is already capped in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 17

_Input Variable Name:_ **e20400**  
_Description:_ Itemizable miscellaneous deductions. WARNING: this variable is zero below the floor in PUF data.  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 24

_Input Variable Name:_ **e24515**  
_Description:_ Sch D: Un-Recaptured Section 1250 Gain  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 19

_Input Variable Name:_ **e24518**  
_Description:_ Sch D: 28% Rate Gain or Loss  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 18

_Input Variable Name:_ **e26270**  
_Description:_ Sch E: Combined partnership and S-corporation net income/loss (includes k1bx14p and k1bx14s amounts and is included in e02000)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch E line 32

_Input Variable Name:_ **e27200**  
_Description:_ Sch E: Farm rent net income or loss (included in e02000)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch E line 40

_Input Variable Name:_ **e32800**  
_Description:_ Child/dependent-care expenses for qualifying persons from Form 2441  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 2441 line 3

_Input Variable Name:_ **e58990**  
_Description:_ Investment income elected amount from Form 4952  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 4952 line 4g

_Input Variable Name:_ **e62900**  
_Description:_ Alternative Minimum Tax foreign tax credit from Form 6251  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251 line 32

_Input Variable Name:_ **e87521**  
_Description:_ Total tentative AmOppCredit amount for all students  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 8863 Part I line 1 and 8863 Part III line 30

_Input Variable Name:_ **e87530**  
_Description:_ Adjusted qualified lifetime learning expenses for all students  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 8863 Part I line 10 and 8863 Part III line 31

_Input Variable Name:_ **elderly_dependents**  
_Description:_ number of dependents age 65+ in filing unit excluding taxpayer and spouse  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data; not used in tax law

_Input Variable Name:_ **f2441**  
_Description:_ number of child/dependent-care qualifying persons  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: 2441 line 2b

_Input Variable Name:_ **f6251**  
_Description:_ 1 if Form 6251 (AMT) attached to return; otherwise 0  
_Datatype:_ integer  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 6251

_Input Variable Name:_ **ffpos**  
_Description:_ CPS family identifier within household (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **fips**  
_Description:_ FIPS state code (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **g20500**  
_Description:_ Itemizable gross (before 10% AGI disregard) casualty or theft loss  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch A line 20 before disregard subtracted

_Input Variable Name:_ **h_seq**  
_Description:_ CPS household sequence number (not used in tax-calculation logic)  
_Datatype:_ integer  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2013-2016: sample construction info

_Input Variable Name:_ **housing_ben**  
_Description:_ Imputed housing benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **k1bx14p**  
_Description:_ Partner self-employment earnings/loss for taxpayer (included in e26270 total)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1065 (Schedule K-1) box 14

_Input Variable Name:_ **k1bx14s**  
_Description:_ Partner self-employment earnings/loss for spouse (included in e26270 total)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1065 (Schedule K-1) box 14

_Input Variable Name:_ **mcaid_ben**  
_Description:_ Imputed Medicaid benefits expressed as the actuarial value of Medicaid health insurance  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **mcare_ben**  
_Description:_ Imputed Medicare benefits expressed as the actuarial value of Medicare health insurance  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **n1820**  
_Description:_ Number of people age 18-20 years old in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **n21**  
_Description:_ Number of people 21 years old or older in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **n24**  
_Description:_ Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu05**  
_Description:_ Number of dependents under 5 years old  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu13**  
_Description:_ Number of dependents under 13 years old  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **nu18**  
_Description:_ Number of people under 18 years old in the filing unit  
_Datatype:_ integer  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: imputed from CPS data

_Input Variable Name:_ **other_ben**  
_Description:_ Non-imputed benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: determined using government benefit program data

_Input Variable Name:_ **p08000**  
_Description:_ Other tax credits (but not including Sch R credit)  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2013: 1040 line 53  
2014-2016: 1040 line 54

_Input Variable Name:_ **p22250**  
_Description:_ Sch D: Net short-term capital gains/losses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 7

_Input Variable Name:_ **p23250**  
_Description:_ Sch D: Net long-term capital gains/losses  
_Datatype:_ real  
_Availability:_ taxdata_puf  
_IRS Form Location:_  
2013-2016: 1040 Sch D line 15

_Input Variable Name:_ **pencon_p**  
_Description:_ Contributions to defined-contribution pension plans for taxpayer  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: Imputed using IRS tabulations of Form W-2 sample

_Input Variable Name:_ **pencon_s**  
_Description:_ Contributions to defined-contribution pension plans for spouse  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: Imputed using IRS tabulations of Form W-2 sample

_Input Variable Name:_ **s006**  
_Description:_ Filing unit sampling weight; appears as WEIGHT variable in tc CLI minimal output  
_Datatype:_ real  
_Availability:_ taxdata_puf, taxdata_cps  
_IRS Form Location:_  
2013-2016: not used in filing unit tax calculations

_Input Variable Name:_ **snap_ben**  
_Description:_ Imputed SNAP benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **ssi_ben**  
_Description:_ Imputed SSI benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **tanf_ben**  
_Description:_ Imputed TANF benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **vet_ben**  
_Description:_ Imputed Veteran's benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

_Input Variable Name:_ **wic_ben**  
_Description:_ Imputed WIC benefits  
_Datatype:_ real  
_Availability:_ taxdata_cps  
_IRS Form Location:_  
2014-20??: imputed using the C-TAM model

### 5\. Output Variables

This section contains documentation of output variables in a format that is easy to search and print. The output variables are ordered alphabetically by name. There are no subsections, just a long list of output variables that Tax-Calculator is programmed to calculate.

_Output Variable Name:_ **aftertax_income**  
_Description:_ After tax income is equal to expanded_income minus combined  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **benefit_cost_total**  
_Description:_ Government cost of all benefits received by tax unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **benefit_value_total**  
_Description:_ Consumption value of all benefits received by tax unit, which is included in expanded_income  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c00100**  
_Description:_ Adjusted Gross Income (AGI)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 37  
2018-20??: 1040 line 7

_Output Variable Name:_ **c01000**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c02500**  
_Description:_ Social security (OASDI) benefits included in AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 20b

_Output Variable Name:_ **c02900**  
_Description:_ Total of all 'above the line' income adjustments to get AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 36

_Output Variable Name:_ **c03260**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c04470**  
_Description:_ Itemized deductions after phase-out (zero for non-itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8

_Output Variable Name:_ **c04600**  
_Description:_ Personal exemptions after phase-out  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 42  
2018-20??:

_Output Variable Name:_ **c04800**  
_Description:_ Regular taxable income  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 43  
2018-20??: 1040 line 10

_Output Variable Name:_ **c05200**  
_Description:_ Tax amount from Sch X,Y,X tables  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c05700**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c05800**  
_Description:_ Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 46  
2014-2016: 1040 line 47

_Output Variable Name:_ **c07100**  
_Description:_ Total non-refundable credits used to reduce positive tax liability  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 46 minus 1040 line 55  
2014-2016: 1040 line 47 minus 1040 line 56

_Output Variable Name:_ **c07180**  
_Description:_ Credit for child and dependent care expenses from Form 2441  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 48  
2014-2016: 1040 line 49

_Output Variable Name:_ **c07200**  
_Description:_ Schedule R credit for the elderly and the disabled  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07220**  
_Description:_ Child tax credit (adjusted) from Form 8812  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 51  
2014-2016: 1040 line 52

_Output Variable Name:_ **c07230**  
_Description:_ Education tax credits non-refundable amount from Form 8863 (includes c87668)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 8863 line 19 and 1040 line 49  
2014-2016: 8863 line 19 and 1040 line 50

_Output Variable Name:_ **c07240**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07260**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07300**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07400**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c07600**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c08000**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c09200**  
_Description:_ Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 61  
2014-2016: 1040 line 63

_Output Variable Name:_ **c09600**  
_Description:_ Alternative Minimum Tax (AMT) liability  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 45

_Output Variable Name:_ **c10960**  
_Description:_ American Opportunity Credit refundable amount from Form 8863  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 8863 line 8 and 1040 line 66  
2014-2016: 8863 line 8 and 1040 line 68

_Output Variable Name:_ **c11070**  
_Description:_ Child tax credit (refunded) from Form 8812  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 65  
2014-2016: 1040 line 67

_Output Variable Name:_ **c17000**  
_Description:_ Sch A: Medical expenses deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c18300**  
_Description:_ Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c19200**  
_Description:_ Sch A: Interest deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c19700**  
_Description:_ Sch A: Charity contributions deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c20500**  
_Description:_ Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c20800**  
_Description:_ Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c21040**  
_Description:_ Itemized deductions that are phased out  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c21060**  
_Description:_ Itemized deductions before phase-out (zero for non-itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c23650**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c59660**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **c62100**  
_Description:_ Alternative Minimum Tax (AMT) taxable income  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 6251 line 28

_Output Variable Name:_ **c87668**  
_Description:_ American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **care_deduction**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **charity_credit**  
_Description:_ Credit for charitable giving  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **codtc_limited**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **combined**  
_Description:_ Sum of iitax and payrolltax and lumpsum_tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ctc_new**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks10**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks13**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks14**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **dwks19**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e17500_capped**  
_Description:_ Sch A: Medical expenses, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e18400_capped**  
_Description:_ Sch A: State and local income taxes deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e18500_capped**  
_Description:_ Sch A: State and local real estate taxes deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e19200_capped**  
_Description:_ Sch A: Interest deduction deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e19800_capped**  
_Description:_ Sch A: Charity cash contributions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e20100_capped**  
_Description:_ Sch A: Charity noncash contributions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **e20400_capped**  
_Description:_ Sch A: Gross miscellaneous deductions deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned_p**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **earned_s**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **eitc**  
_Description:_ Earned Income Credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 64a  
2014-2016: 1040 line 66a

_Output Variable Name:_ **exact**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ integer  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **expanded_income**  
_Description:_ Broad income measure that includes benefit_value_total  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **fstax**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **g20500_capped**  
_Description:_ Sch A: Gross casualty or theft loss deductible, capped as a decimal fraction of AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **iitax**  
_Description:_ Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 61 minus line 56 minus line 60a  
2014-2016: 1040 line 63 minus line 57 minus line 62a

_Output Variable Name:_ **invinc_agi_ec**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **invinc_ec_base**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **lumpsum_tax**  
_Description:_ Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **mtr_inctax**  
_Description:_ Marginal income tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **mtr_paytax**  
_Description:_ Marginal payroll tax rate (in percentage terms) on extra taxpayer earnings (e00200p)  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **niit**  
_Description:_ Net Investment Income Tax from Form 8960  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 60b  
2014-2016: 1040 line 62b

_Output Variable Name:_ **nontaxable_ubi**  
_Description:_ Amount of UBI benefit excluded from AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **num**  
_Description:_ 2 when MARS is 2 (married filing jointly); otherwise 1  
_Datatype:_ integer  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Output Variable Name:_ **odc**  
_Description:_ Other Dependent Credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **othertaxes**  
_Description:_ Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: sum of 1040 lines 57 through 60  
2014-2016: sum of 1040 lines 58 through 62

_Output Variable Name:_ **payrolltax**  
_Description:_ Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDI+HI FICA plus 1040 lines 56 and 60a  
2014-2016: OASDI+HI FICA plus 1040 lines 57 and 62a

_Output Variable Name:_ **personal_nonrefundable_credit**  
_Description:_ Personal nonrefundable credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **personal_refundable_credit**  
_Description:_ Personal refundable credit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **pre_c04600**  
_Description:_ Personal exemption before phase-out  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ptax_amc**  
_Description:_ Additional Medicare Tax from Form 8959 (included in payrolltax)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 60a  
2014-2016: 1040 line 62a

_Output Variable Name:_ **ptax_oasdi**  
_Description:_ Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDI FICA plus 1040 line 56  
2014-2016: OASDI FICA plus 1040 line 57

_Output Variable Name:_ **ptax_was**  
_Description:_ Employee + employer OASDI + HI FICA tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: OASDHI FICA  
2014-2016: OASDHI FICA

_Output Variable Name:_ **qbided**  
_Description:_ Qualified Business Income (QBI) deduction  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017:  
2018-20??: 1040 line 9

_Output Variable Name:_ **refund**  
_Description:_ Total refundable income tax credits  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc**  
_Description:_ Refundable Payroll Tax Credit for filing unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc_p**  
_Description:_ Refundable Payroll Tax Credit for taxpayer  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **rptc_s**  
_Description:_ Refundable Payroll Tax Credit for spouse  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **sep**  
_Description:_ 2 when MARS is 3 (married filing separately); otherwise 1  
_Datatype:_ integer  
_IRS Form Location:_  
2013-2016: 1040 lines 1-5

_Output Variable Name:_ **setax**  
_Description:_ Self-employment tax  
_Datatype:_ real  
_IRS Form Location:_  
2013-2013: 1040 line 56  
2014-2016: 1040 line 57

_Output Variable Name:_ **sey**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **standard**  
_Description:_ Standard deduction (zero for itemizers)  
_Datatype:_ real  
_IRS Form Location:_  
2013-2017: 1040 line 40  
2018-20??: 1040 line 8

_Output Variable Name:_ **surtax**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **taxable_ubi**  
_Description:_ Amount of UBI benefit included in AGI  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **taxbc**  
_Description:_ Regular tax on regular taxable income before credits  
_Datatype:_ real  
_IRS Form Location:_  
2013-2016: 1040 line 44

_Output Variable Name:_ **ubi**  
_Description:_ Universal Basic Income benefit for filing unit  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **was_plus_sey_p**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **was_plus_sey_s**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ymod**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

_Output Variable Name:_ **ymod1**  
_Description:_ search taxcalc/calcfunctions.py for how calculated and used  
_Datatype:_ real  
_IRS Form Location:_  
2013-20??: calculated variable

### 6\. Assumption Parameters

This section contains documentation of several sets of parameters that characterize responses to a tax reform. Consumption parameters are used to compute marginal tax rates and to compute the consumption value of in-kind benefits. Growdiff parameters are used to specify baseline differences and/or reform responses in the annual rate of growth in economic variables. (Note that behavior parameters used to compute changes in input variables caused by a tax reform in a partial-equilibrium setting are not part of Tax-Calculator, but can be used via the Behavioral-Response `behresp` package in a Python program.)

The assumption parameters control advanced features of Tax-Calculator, so understanding the source code that uses them is essential. Default values of many assumption parameters are zero and are projected into the future at that value, which implies no response to the reform. The benefit value consumption parameters have a default value of one, which implies the consumption value of the in-kind benefits is equal to the government cost of providing the benefits.

#### 6a. Growdiff Parameters

**Assumption Parameter — Growdiff**  
_tc Name:_ ABOOK  
_Long Name:_ ABOOK additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABOOK extrapolates input variables: e07300 and e07400.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ACGNS  
_Long Name:_ ACGNS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ACGNS extrapolates input variables: e01200, p22250, p23250, e24515 and e24518.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ACPIM  
_Long Name:_ ACPIM additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ACPIM extrapolates input variables: e03270, e03290 and e17500.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ACPIU  
_Long Name:_ ACPIU additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ACPIU is the price inflation rate used to inflate many policy parameters. Note that non-zero values of this parameter will not affect historically known values of policy parameters.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ADIVS  
_Long Name:_ ADIVS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ADIVS extrapolates input variables: e00600 and e00650.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ AINTS  
_Long Name:_ AINTS additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. AINTS extrapolates input variables: e00300 and e00400.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ AIPD  
_Long Name:_ AIPD additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. AIPD extrapolates input variables: e19200.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASCHCI  
_Long Name:_ ASCHCI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASCHCI extrapolates input variables: e00900, e00900p and e00900s when they are positive.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASCHCL  
_Long Name:_ ASCHCL additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASCHCL extrapolates input variables: e00900, e00900p and e00900s when they are negative.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASCHEI  
_Long Name:_ ASCHEI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASCHEI extrapolates input variables: e02000 when positive, and e26270, k1bx14p, k1bx14s and e27200 for all values.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASCHEL  
_Long Name:_ ASCHEL additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASCHEL extrapolates input variable: e02000 when negative.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASCHF  
_Long Name:_ ASCHF additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASCHF extrapolates input variables: e02100, e02100p and e02100s.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ASOCSEC  
_Long Name:_ ASOCSEC additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ASOCSEC extrapolates input variable: e02400.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ATXPY  
_Long Name:_ ATXPY additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ATXPY extrapolates input variables: e00700, e00800, e01400, e01500, e01700, e03150, e03210, e03220, e03230, e03300, e03400, e03500, e07240, e07260, p08000, e09700, e09800, e09900, e11200, e18400, e18500, e19800, e20100, e20400, g20500, e07600, e32800, e58990, e62900, e87530, e87521 and cmbtp.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ AUCOMP  
_Long Name:_ AUCOMP additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. AUCOMP extrapolates input variable: e02300.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ AWAGE  
_Long Name:_ AWAGE additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. AWAGE extrapolates input variables: e00200, e00200p and e00200s. Also, AWAGE is the wage growth rate used to inflate the OASDI maximum taxable earnings policy parameter, _SS_Earnings_c. Note that non-zero values of this parameter will not affect historically known values of _SS_Earnings_c.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENOTHER  
_Long Name:_ ABENOTHER additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENOTHER extrapolates input variable other_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENMCARE  
_Long Name:_ ABENMCARE additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENMCARE extrapolates input variable mcare_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENMCAID  
_Long Name:_ ABENMCAID additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENMCAID extrapolates input variable mcaid_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENSSI  
_Long Name:_ ABENSSI additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENSSI extrapolates input variable ssi_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENSNAP  
_Long Name:_ ABENSNAP additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENSNAP extrapolates input variable snap_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENWIC  
_Long Name:_ ABENWIC additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENWIC extrapolates input variable wic_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENHOUSING  
_Long Name:_ ABENHOUSING additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENHOUSING extrapolates input variable housing_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENTANF  
_Long Name:_ ABENTANF additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENTANF extrapolates input variable tanf_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

**Assumption Parameter — Growdiff**  
_tc Name:_ ABENVET  
_Long Name:_ ABENVET additive difference from default projection  
_Description:_ Default projection is in growfactors.csv file. ABENVET extrapolates input variable vet_ben.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = -10 and max = 10  
_Out-of-Range Action:_ error

#### 6b. Consumption Parameters

**Assumption Parameter — Consumption**  
_tc Name:_ MPC_e17500  
_Long Name:_ Marginal propensity to consume medical expenses  
_Description:_ Defined as dollar change in medical-expense consumption divided by dollar change in income. Typical value is in [0,1] range.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ MPC_e18400  
_Long Name:_ Marginal propensity to consume state-and-local taxes  
_Description:_ Defined as dollar change in state-and-local-taxes consumption divided by dollar change in income. Typical value is in [0,1] range.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ MPC_e19800  
_Long Name:_ Marginal propensity to consume charity cash contributions  
_Description:_ Defined as dollar change in charity-cash-contribution consumption divided by dollar change in income. Typical value is in [0,1] range.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ MPC_e20400  
_Long Name:_ Marginal propensity to consume miscellaneous deduction expenses  
_Description:_ Defined as dollar change in miscellaneous-deduction-expense consumption divided by dollar change in income. Typical value is in [0,1] range.  
_Default Value:_  
2013: 0.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_housing_value  
_Long Name:_ Consumption value of housing benefits  
_Description:_ Consumption value per dollar of housing benefits, all of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_snap_value  
_Long Name:_ Consumption value of SNAP benefits  
_Description:_ Consumption value per dollar of SNAP benefits, all of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_tanf_value  
_Long Name:_ Consumption value of TANF benefits  
_Description:_ Consumption value per dollar of TANF benefits, some of which are cash benefits and some of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_vet_value  
_Long Name:_ Consumption value of veterans benefits  
_Description:_ Consumption value per dollar of veterans benefits, some of which are in-kind benefits (only about 48% are cash benefits).  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_wic_value  
_Long Name:_ Consumption value of WIC benefits  
_Description:_ Consumption value per dollar of WIC benefits, all of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_mcare_value  
_Long Name:_ Consumption value of Medicare benefits  
_Description:_ Consumption value per dollar of Medicare benefits, all of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_mcaid_value  
_Long Name:_ Consumption value of Medicaid benefits  
_Description:_ Consumption value per dollar of Medicaid benefits, all of which are in-kind benefits.  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 2  
_Out-of-Range Action:_ error

**Assumption Parameter — Consumption**  
_tc Name:_ BEN_other_value  
_Long Name:_ Consumption value of other benefits  
_Description:_ Consumption value per dollar of other benefits, some of which are in-kind benefits (somewhere between 52% and 76% are in-kind benefits).  
_Default Value:_  
2013: 1.0  
_Valid Range:_ min = 0 and max = 1  
_Out-of-Range Action:_ error