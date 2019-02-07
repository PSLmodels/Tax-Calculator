TCJA FAQ
========

In Tax-Calculator release 0.15.0 and higher, the `policy_current_law`
file represents TCJA, not the pre-TCJA policy that was represented by
`policy_current_law.json` in releases before 0.15.0.

**1. How can I use pre-TCJA policy as the baseline?**

You need to use the new
[2017_law.json](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/reforms/2017_law.json)
as a "reform", and then, if you want to compare that pre-TCJA policy
to an old reform, implement the old reform as usual.  This
compound-reform technique works well and is being used extensively in
the Tax-Calculator test suite.  This technique is illustrated in
recipe 01 of the [Cookbook of Tested Recipes for Python Programming
with
Tax-Calculator](https://pslmodels.github.io/Tax-Calculator/cookbook.html)
using the `2017_law.json` and `TCJA.json` reform files.  For a check
of the consistency of the `2017_law.json` and `TCJA.json` reform
files, see `test_round_trip_tcja_reform` in the
`taxcalc/tests/test_reforms.py` file.

**2. Does Tax-Calculator produce the same results for pre-TCJA policy
     as before?**

Yes, release 0.14.3 and 0.15.0 produce the same aggregate results for
pre-TCJA policy even though the contents of `policy_current_law.json`
have changed.

For an analysis that shows the pre-TCJA tax revenues for 2019 are the
same, see below at the heading **TCJA and pre-TCJA Comparisons**.

**3. Does Tax-Calculator produce the same results for TCJA policy as
     before?**

No, there is a small difference (less than one percent) in aggregate
income tax revenues between the Tax-Calculator releases 0.15.0 and
0.14.3.  This difference is caused by the fact that Tax-Calculator
0.15.0 adds several TCJA provisions that were not included in
Tax-Calculator 0.14.3.  See pull requests #1818 and #1819 for details
on the newly added TCJA provisions.

**4. Does TCJA current-law policy incorporate any behavior responses?**

Beginning with release 0.25.0, Tax-Calculator incorporates a new CBO
budget outlook that presumably includes the effects of any behavioral
changes and growth effects that one might expect to be caused by TCJA.
