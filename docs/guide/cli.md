Command-line interface
======================

You can use Tax-Calculator on your own computer via a command-line
interface (CLI) called `tc`.  This approach requires the use of a text
editor to prepare simple files that are read by `tc`.  Computer
programming knowledge is not required, but this approach to using
Tax-Calculator assumes you are willing to work at the command line
(Terminal on Mac or Anaconda Prompt on Windows) and to use a text
editor (for example, TextEdit on Mac or Notepad on Windows).

## Test `tc` CLI

The `tc` CLI is part of the Tax-Calculator `taxcalc` package you
installed on your computer as part of {doc}`../usage/starting`.

To check your installation of `tc`, enter the following command:

```
tc --test
```

Expected output (after a number of seconds) is `PASSED TEST`.  If you
get `FAILED TEST`, something went wrong in the installation
process. If the installation test fails, please report your experience
by [creating a new
issue](https://github.com/PSLmodels/Tax-Calculator/issues).

If your installation passes the test, you are ready to begin using
`tc` to analyze tax reforms. Continue reading this section for
information about how to do that. But if you want a quick hint about
the range of `tc` capabilities, enter the following:

```
tc --help
```

The basic idea of `tc` tax analysis is that each tax reform is
specified in a text file using a simple method to describe the details
of the reform. Read the next part of this section to see how policy
reform files are formatted.

## Specify tax reform

The details of a tax reform are contained in a text file that you
write with a text editor. The reform is expressed by specifying which
tax policy parameters are changed from their current-law values by the
reform. The current-law values of each policy parameter are documented
in [this
section](https://taxcalc.pslmodels.org/guide/policy_params.html#policy-parameters)
of the guide. The timing and magnitude of these policy parameter
changes are written in JSON, a simple and widely-used
data-specification language.

For several examples of reform files and the general rules for writing
JSON reform files, go to [this
page](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/README.md#policy-reform-files).

## Specify analysis assumptions

This part explains how to specify economic assumption files used in
static tax analysis. This is an advanced topic, so if you want to
start out using the default assumptions (which are documented in [this
section](https://taxcalc.pslmodels.org/guide/policy_params.html#policy-parameters))
of the guide), you can skip this part now and come back to read it
whenever you want to change the default assumptions. The [next
part](https://taxcalc.pslmodels.org/guide/cli.html#specify-filing-units)
of this section discusses filing-unit input files.

The details of analysis assumptions are contained in a text file that
you write with a text editor. The assumptions are expressed by
specifying which parameters are changed from their default values. The
timing and magnitude of these parameter changes are written in JSON, a
simple and widely-used data-specification language.

For examples of assumption files and the general rules for writing
JSON assumption files, go to [this
page](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/assumptions/README.md#economic-assumption-files).

## Specify filing units

The `taxcalc` package containing `tc` does not include an
IRS-SOI-PUF-derived microsimulation sample. This is because, unlike
Census public-use files, the IRS-SOI Public Use File (PUF) is
proprietary. If you or your organization has paid IRS to use the PUF
version being by Tax-Calculator, then it may be possible for us to
share with you our PUF-derived sample, which we call `puf.csv` even
though it contains CPS records that represent non-filers. Otherwise,
you have two choices.

**First**, you can easily create with a text editor a CSV-formatted
file containing several filing units whose experience under your tax
reform is of interest to you. Much of the public discussion of tax
reforms is of this type: how is this family or that family affected by
a reform; how do they fare under different reforms; etc. The test
conducted to check the `tc` installation has left one such file. It is
called `test.csv` and contains two filing units with only wage and
salary income: a lower income family and a higher income family. You
can use this `test.csv` file as `tc` input to analyze your tax
reforms. Before creating your own input files be sure to read the
short set of guidelines that appear after this list of two
choices. Some people pursue this approach using a statistical pacakge
like R or Stata, in which case the `tc` CLI program can be invoked
from within the statistical package. There may be a need (especially
on Windows) to [add to the system
PATH](https://github.com/PSLmodels/Tax-Calculator/issues/2273#issuecomment-479572287)
in order to do this.

**Second**, the `taxcalc` does include a freely available
microsimulation samplecontaining only filing units derived from
several recent March CPS surveys. For several reasons, the results
generated by this `cps.csv` file are substantially different from the
results generated by the `puf.csv` file. The `cps.csv` file contains a
sample of the population while the `puf.csv` file contains mostly a
sample of income tax filers in which high-income filing units are over
represented. Also, the `cps.csv` file has many income variables that
are missing (and assumed to be zero by Tax-Calculator), which causes
an understating of total incomes, especially for those with high
incomes. All these differences mean that the aggregate revenue and
distributional results generated when using the `cps.csv` file as
input to Tax-Calculator can be substantially different from the
results generated when using the `puf.csv` file as input. And this is
particularly true when analyzing reforms that change the tax treatment
of high-income filers.

**Input-File-Preparation Guidelines**

The `tc` CLI to Tax-Calculator is flexible enough to read almost any
kind of CSV-formatted input data on filing units as long as the
variable names correspond to those expected by Tax-Calculator. The
only required input variables are `RECID` (a unique filing-unit record
identifier) and `MARS` (a positive-valued filing-status
indicator). Other variables in the input file must have variable names
that are listed in the [Input Variables](#input) section for them to
affect the tax calculations. Any variable listed in Input Variables
that is not in an input file is automatically set to zero for every
filing unit. Variables in the input file that are not listed in Input
Variables are ignored by Tax-Calculator.

However, there are important data-preparation issues related to the
fact that the payroll tax is a tax on individuals, not on income-tax
filing units. Tax-Calculator expects that the filing-unit total for
each of several earnings-related variables is split between the
taxpayer and the spouse. It is the responsibility of anyone preparing
data for Tax-Calculator input to do this earnings splitting. Here are
the relationships between the filing-unit variable and the taxpayer
(`p`) and spouse (`s`) variables expected by Tax-Calculator:

```
e00200 = e00200p + e00200s
e00900 = e00900p + e00900s
e02100 = e02100p + e02100s
```

Obviously, when `MARS` is not equal to 2 (married filing jointly), the
values of the three `s` variables are zero and the value of each `p`
variable is equal to the value of its corresponding filing-unit
variable. Note that the input file can omit any one, or all, of these
three sets variables. If the three variables in one of these sets are
omitted, the required relationship will be satisfied because zero
equals zero plus zero.

In addition to this earnings-splitting data-preparation issue,
Tax-Calculator expects that the value of ordinary dividends (`e00600`)
will be no less than the value of qualified dividends (`e00650`) for
each filing unit. And it also expects that the value of total pension
and annuity income (`e01500`) will be no less than the value of
taxable pension and annuity income (`e01700`) for each filing
unit. Tax-Calculator also expects the value of the required MARS
variable to be in the range from one to five, and the value of the EIC
variable to be in the range from zero to three. Again, it is your
responsibility to prepare input data for Tax-Calculator in a way that
ensures these relationships are true for each filing unit.

Here's an example of how to specify a few stylized filing units with
and without young children:

```
RECID,MARS,XTOT,EIC,n24,...
    11   ,  1 ,  1 , 0 , 0 ,... <== single person with no kids
    12   ,  4 ,  2 , 1 , 1 ,... <== single person with a young kid
    13   ,  2 ,  4 , 2 , 2 ,... <== married couple with two young kids
```

Be sure to read the documentation of the `MARS`, `XTOT`, `EIC`, and
`n24` input variables. Also, there may be a need to add other
child-age input variables if you want to simulate reforms like a child
credit bonus for young children. Also, the universal basic income
(UBI) reform is implemented using its own set of three age-group-count
input variables.

The name of your input data file is also relevant to how `tc` will
behave. If your file name ends with "puf.csv" or "cps.csv", `tc` will
automatically extrapolate your data from its base year to the year you
specify for tax calculations to be calculated using built in growth
factors, extrapolated weights, and other adjustment factors. If you
are not using the "puf.csv" or "cps.csv" files produced by the TaxData
project, it is likely that your data will not be compatible with these
extrapolations and you should adopt filenames with alternative
endings.

## Initiate reform analysis

Executing `tc` requires only two command-line arguments: the name of
an input file containing one or more filing units and the year for
which the tax calculations are done. A baseline policy file is
optional; specifying no baseline file implies the baseline policy is
current-law policy. A policy reform file is optional; specifying no
reform file implies calculations are done for the baseline policy. An
economic assumption file is also optional; no assumption file implies
you want to use the default values of the assumption parameters. The
output files written by `tc` are built-up from the name of the input
file, tax year, baseline file, reform file, and assumption file using
a `#` character if an option is not specified.

Here we explain how to conduct tax analysis with `tc` by presenting a
series of examples and explaining what output is produced in each
example. There are several types of output that `tc` can generate so
there will be more than a few examples. The examples are numbered in
order to make it easier to refer to different examples. All the
examples assume that the input file is `test.csv`, which was mentioned
earlier in this guide.

```
tc test.csv 2020
```

This produces a minimal output file containing 2020 tax liabilities
for each filing unit assuming the income amounts in the input file are
amounts for 2020 and assuming current-law tax policy projected to
2020\. The name of the CSV-formatted output file is
`test-20-#-#-#.csv`. The first `#` symbol indicates we did not specify
a baseline file and the second `#` symbol indicates we did not specify
a policy reform file and the third `#` symbol indicates we did not
specify an economic assumption file.  The variables included in the
minimal output file include: `RECID` (of filing unit in the input
file), `YEAR` (specified when executing `tc`), `WEIGHT` (which is same
as `s006`), `INCTAX` (which is same as `iitax`), `LSTAX` (which is
same as `lumpsum_tax`) and `PAYTAX` (which is same as `payroll_tax`).

Also, documentation of the reform is always written to a text file
ending in `-doc.text`, which in this example would be named
`test-20-#-#-#-doc.text`.

```
tc test.csv 2020 --dump
```

This produces a much more complete output file with the same name
`test-20-#-#-#.csv` as the minimal output file produced in example
(1). No other output is generated other than the
`test-20-#-#-#-doc.text` file. The `--dump` option causes **all** the
input variables (including the ones understood by Tax-Calculator but
not included in `test.csv`, which are all zero) and **all** the output
variables calculated by Tax-Calculator to be included in the output
file. For a complete list of input variables, see the [Input
Variables](#input) section. For a complete list of output variables,
see the [Output Variables](#output) section. Since Tax-Calculator
ignores variables in the input file that are not in the Input
Variables section, the dump output file in example (2) can be used as
an input file and it will produce exactly the same tax liabilities
(apart from rounding errors of one or two cents) as in the original
dump output.

This full dump output can be useful for debugging and is small when
using just a few filing units as input. But when using large samples
as input (for example, the `cps.csv` input file), the size of the dump
output becomes quite large. There is a way to specify a **partial
dump** that includes only variables of interest. To have `tc` do a
partial dump, create a text file that lists the names of the variables
to be included in the partial dump. You can put the varible names on
separate lines and/or put several names on one line separated by
spaces. Then point to that file using the `--dvars` option. So, for
example, if your list of dump variables is in a file named
`mydumpvars`, a partial dump file is created this way:

```
tc cps.csv 2020 --dump --dvars mydumpvars
```

If there is no `--dvars` option, the `--dump` option produces a full dump.

```
tc test.csv 2020 --sqldb
```

This produces the same dump output as example (2) except that the dump
output is written not to a CSV-formatted file, but to the dump table
in an SQLite3 database file, which is called `test-20-#-#-#.db` in
this example. Because the `--dump` option is not used in example (3),
minimal output will be written to the `test-20-#-#-#.csv` file. Note
that use of the `--dvars` option causes the contents of the database
file to be a partial dump.

Pros and cons of putting dump output in a CSV file or an SQLite3
database table: The CSV file is almost twice as large as the database,
but it can be easily imported into a wide range of statistical
packages. The main advantage of the SQLite3 database is that the
Anaconda Python distribution includes
[sqlite3](https://www.sqlite.org/cli.html) (or sqlite3.exe on
Windows), a command-line tool that can be used to tabulate dump output
using structured query language (SQL). SQL is a language that you use
to specify the tabulation you want and the SQL database figures out
the procedure for generating your tabulation and then executes that
procedure; there is no computer programming involved. We illustrate
SQL tabulation of dump output in a [subsequent
section](#cli-tab-results).

```
tc test.csv 2020 --dump --sqldb
```

This shows that you can get dump output in the two different formats
from a single `tc` run.

The remaining examples use neither the `--dump` nor the `--sqldb`
option, and thus, produce minimal output for the reform. But either or
both of those options could be used in all the subsequent examples to
generate more complete output for the reform.

```
tc test.csv 2021 --reform ref3.json
```

This produces 2021 output for the filing units in the `test.csv` file
using the policy reform specified in the `ref3.json` file. The name of
the output file in this example is `test-21-#-ref3-#.csv` because no
baseline or assumption options were specified.

If, in addition to `ref3.json`, there was a `ref4.json` reform file
and analysis of the **compound reform** (consisting of first
implementing the `ref3.json` reform relative to current-law policy and
then implementing the `ref4.json` reform relative to the `ref3.json`
reform) is desired, both reform files can be mentioned in the
`--reform` option as follows:

```
tc test.csv 2021 --reform ref3.json+ref4.json
```

The above command generates an output file named `test-21-#-ref3+ref4-#.csv`

```
tc test.csv 2021 --reform ref3.json --assump res1.json
```

This produces 2021 output for the filing units in the `test.csv` file
using the policy reform specified in the `ref3.json` file and the
economic assumptions specified in the `eas1.json` file. The output
results produced by this analysis are written to the
`test-21-#-ref3-eas1.csv` file.

In the preceding examples, all the output files are written in the
directory where the `tc` command was executed. If you want the output
files to be written in a different directory, use the `--outdir`
option. So, for example, if you have created the `myoutput` directory
as a subdirectory of the directory from where you are running `tc`,
output files will be written there if you use the `--outdir myoutput`
option.

The following examples illustrate output options that work only if
each filing unit in the input file has a positive sampling weight
(`s006`). So, we are going to use the `cps.csv` file in these examples
along with the policy reform specified in the `ref3.json` file, the
content of which is:

```
// ref3.json raises personal exemption amount to 8000 in 2022,
// after which it continues to be indexed to price inflation.
{
    "II_em": {"2022": 8000}
}
```

The output options illustrated in the following examples generate
tables of the post-reform level and the reform-induced change in tax
liability by income deciles as well as graphs of marginal and average
tax rates and percentage change in aftertax income by income
percentiles. These tables and graphs are meant to provide a quick
glance at the impact of a reform. Any serious analysis of a reform
will involve generating custom tables and graphs using [partial
dump](#partdump) output. One of many examples of this sort of custom
analysis is
[here](https://www.washingtonpost.com/graphics/2017/business/tax-bill-calculator/?).

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

This produces 2022 output for the filing units in the `cps.csv` file
using the policy reform specified in the `ref3.json` file. Notice that
Tax-Calculator knows to extrapolate (or "age") filing unit data in the
`cps.csv` file to the specified tax year.  It knows to do that because
of the special input file name `cps.csv`.  The tables produced by this
analysis are written to the `cps-22-#-ref3-#-tab.text` file.  Note
that on Windows you would use `dir` instead of `ls` and `type` instead
of `cat`.

Also note that the tables above in example (7) include in the bottom
decile some filing units who have negative or zero expanded income in
the baseline. If you want tables that somehow exclude those filing
units, use the `--dump` option and tabulate your own tables.

```
$ tc cps.csv 2024 --reform ref3.json --graphs
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2024.

$ ls cps-24-*
cps-24-#-ref3-#-atr.html    cps-24-#-ref3-#-pch.html
cps-24-#-ref3-#-doc.text    cps-24-#-ref3-#.csv
cps-24-#-ref3-#-mtr.html
```

This example is like the previous one, except we ask for 2024 static
output and for graphs instead of tables, although we could ask for
both.  The HTML files containing the graphs can be viewed in your
browser.

Here is what the average tax rate graph in `cps-24-#-ref3-#-atr.html`
looks like.

![atr graph](../_static/atr.png)

Here is what the marginal tax rate graph in `cps-24-#-ref3-#-mtr.html`
looks like:

![mtr graph](../_static/mtr.png)

Here is what the percentage change in aftertax income graph in
`cps-24-#-ref3-#-pch.html` looks like:

![pch graph](../_static/pch.png)

There is yet another `tc` output option that writes to the screen
results from a normative welfare analysis of the specified policy
reform. This `--ceeu` option produces experimental results that make
sense only with input files that contain representative samples of the
population such as the `cps.csv` file. The name of this option stands
for certainty-equivalent expected utility. If you want to use this
output option, you should read the commented Python source code for
the `ce_aftertax_expanded_income` function in the `taxcalc/utils.py`
file in the [Tax-Calculator
repository](https://github.com/PSLmodels/Tax-Calculator).

None of the above examples use the `--baseline` option, which means
that baseline policy in those examples is current-law policy. The
following example shows how to use the `--baseline` option to engage
in counter-factual historical analysis. Suppose we want to analyze
what would have happened if some alternative to TCJA had been enacted
in late 2017\. To do this we need to have pre-TCJA policy be the
baseline policy and we need to have the alternative reform be
implemented relative to pre-TCJA policy. The following `tc` run does
exactly that using a local copy of the
[2017_law.json](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/2017_law.json)
<a>file and the `alt_reform.json` file containing the alternative
reform defined relative to pre-TCJA law.

```
$ tc cps.csv 2019 --baseline 2017_law.json --reform 2017_law.json+alt_reform.json
You loaded data for 2014.
Tax-Calculator startup automatically extrapolated your data to 2019.
```

In all the examples in this section, we have executed one `tc` run at
at time.  But **what if you want to execute many `tc` runs** because
you want results for many years and/or for several different reforms.
Unless you are asking for full-dump output, a single `tc` run should
take no more than one minute on your computer (even if you are using
the large `cps.csv` input file).  The easiest way to speed up the
execution of many `tc` runs is to split them into groups of runs and
execute each group of runs in a different command-prompt window.  On
most modern computers that have four CPU cores and a fast disk drive,
executing four runs in different windows will take not much more time
than executing a single `tc` run.  If you have more than one run in
each group, put them in a Unix/Mac bash script or a Windows batch
file, and execute one script in each command-prompt window.  If it
still takes too long, consider splitting the `tc` runs across more
than one computer.

## Tabulate reform results

Given that `tc` output can be written to either CSV-formatted files or
SQLite3 database files, there is an enormous range of software tools
that can be used to tabulate the output. You can use SAS or R, Stata
or MATLAB, or even import output into a spreadsheet (but this would
seem to be the least useful option). If you just want to compare the
contents of two output files, you can use your favorite graphical diff
program to view the two files <q>side by side</q> with highlighting of
numbers that are different. The main point is to use a software tool
that is available to you, that is appropriate for the task, and that
you have experience using.

Here we give some examples of using the `sqlite3` command-line tool
that is part of the Anaconda distribution (so it is always available
when using Tax-Calculator). The first step, of course, is to use the
`--sqldb` option when running `tc`. Then you can use the `sqlite3`
tool interactively or use it to execute SQL scripts you have saved in
a text file. We'll provide examples of both those approaches. There
are many online tutorials on the SQL select command; if you want to
learn more, search the Internet.

First, we provide a simple example of using `sqlite3` interactively.
This approach is ideal for exploratory data analysis.  Our example
uses the `cps.csv` file as input, but you can do the following with
the output from any input file that has weights (`s006`).  Also, we
specify no policy reform file, so the output is for current-law
policy.  What you cannot see from the following record of the analysis
is that the `sqlite3` tool keeps a command history, so pressing the
up-arrow key will bring up the prior command for editing.  This
feature reduces substantially the amount of typing required to conduct
exploratory data analysis.

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

Second, we provide a simple example of using `sqlite3` with SQL
commands stored in a text file.  This approach is useful if you want
to tabulate many different output files in the same way.  This second
example assumes that the first example has already been done.  Note
that on Windows you should replace `cat` with `type`.

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

The `cat` command writes the contents of the `tab.sql` file to stdout.
We do nothing but that in the first command in order to show you the
file contents.  The second command pipes the contents of the `tab.sql`
file into the `sqlite3` tool, which executes the SQL statements and
writes the tabulation results to stdout.  (If you're wondering about
the validity of those high marginal tax rates, rest assured that all
filing units with marginal income tax rates greater than sixty percent
have been checked by hand and are valid: most are caught in the rapid
phase-out of non-refundable education credits or in the phase-in of
taxation of social security benefits.  The negative marginal tax rates
are caused by refundable credits, primarily the earned income tax
credit.)

If you want to use the `sqlite3` tool to tabulate the changes caused
by a reform, use `tc` to generate two database dump files (one for
current-law policy and the other for your reform) and then use the
SQLite3 ATTACH command to make both database files available in your
SQLite tabulation session.
