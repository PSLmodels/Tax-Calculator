TCJA after 2025
===============

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
in the parent directory of your working directory.

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

While nobody knows how the 2025 tax legislation will turn out, the
idea of this document is to illustrate how to use the Tax-Calculator
CLI tool to analyze some of the TCJA revisions that are being reported
in the press in early May 2025.  The basic legislative goal is to
extend TCJA beyond 2025, but there is discussion of a number of
**revisions** to the basic extension.  The revisions being discussed
include (but are not limited to) raising the SALT deduction cap,
making social security benefits non-taxable, and liberalizing the
child tax credit.  (Give the nature of the rules under which the
legislation is being developed, no changes in social security
financing can be make, so there is discussion of higher
elderly/disability standard deduction amounts to proxy the non-taxable
social security benefits revision.)  These revisions all involve
reductions in income tax revenue, so there is also discussion about
**enhancements** to the extended-TCJA policy that would raise revenue
to pay for revisions.  The enhancement considered here is the one that
adds a new top income tax bracket with a 39.6 percent marginal tax rate.

The analysis examples below focus on the following policy scenarios:

1. a strict extension of TCJA without any revisions or enhancements
2. a TCJA extension with the nontaxable social security benefits revision
3. a TCJA extension with the higher elderly/disabled standard deduction revision
4. a TCJA extension with the higher elderly/disabled standard deduction revision and the new top tax bracket enhancement





=============================================================================
OLD TEXT:

The `--baseline` option is not commonly used, but it can be
very helpful in analyzing reforms that take effect beginning in 2026.
Such a reform could be analyzed relative to current-law policy (that
is, with temporary TCJA provisions expiring after 2025) by omitting
the `--baseline` option.  But if such a reform were to be analyzed
relative to extending all the temporary TCJA provisions beyond 2025,
then the `--baseline ext.json` option would need to be used.  The
[`ext.json`](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/ext.json)
file contains the 2026 tax policy reform provisions that would extend
TCJA's temporary provisions beyond 2025.  Before using this `ext.json`
reform file, be sure to read how it is generated at the end of this
document.

Here are some concrete examples of using the `tc` tool to analyze a
reform of interest to you that begins in 2026.  The examples assume
you have named your reform file `x.json` and that you are using one
of the compatible input datasets describe above.  The examples will
call the input dataset `z.csv`.

To analyze your reform relative to current-law policy (which means
temporary TCJA provisions have expired beginning in 2026), you would
execute this command:

```
tc z.csv 2026 --exact --tables --reform x.json
```

The tables would be in the `z-26-#-x-#-tab.text` output file generated
by this `tc` run.  If you want to do custom tabulations of the micro
output data, use the `--dumpdb` and `--dumpvars` options as explained
by the `tc --help` documentation.

To analyze your reform relative to a reform that extends all TCJA
temporary provisions beyond 2025, you would execute this command:

```
tc z.csv 2026 --exact --tables --baseline ext.json --reform ext.json+x.json
```

The tables would be in the `z-26-ext-ext+x-#-tab.text` output file
generated by this `tc` run.

And finally, you might consider creating a reform file called
`end.json` that contains just the two characters `{}`.  This is a null
reform, which is equivalent to current-law policy, that could be used
as follows:

```
tc z.csv 2026 --exact --tables --baseline end.json --reform x.json
```

The resulting table output would be named `z-26-end-x-#-tab.text` and
have the same tabular output as the `z-26-#-x-#-tab.text` file.  Some
people may prefer `end` to `#` as a way of naming current-law policy
in the context of discussing TCJA-related reforms.


**How is the `ext.json` file generated?**

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

=============================================================================
