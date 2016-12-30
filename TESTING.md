[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator Testing Procedures
=================================

This description of Tax-Calculator testing procedure is written for a
person who wants to contribute changes to Tax-Calculator source code.
It assumes that you have read the [Contributor
Guide](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html)
and the [conventions about naming and placing new policy
parameters](http://taxcalc.readthedocs.io/en/latest/parameter_naming.html),
have cloned the [central GitHub Tax-Calculator
repository](https://github.com/open-source-economics/Tax-Calculator)
to your GitHub account and to your local computer, and are familiar
with how to prepare a pull request for consideration by the core
development team.  This document describes the testing procedure you
should follow on your local computer before submitting a development
branch as a pull request to the central Tax-Calculator repository at
GitHub.

Currently there are three phases of testing.

Testing with py.test
--------------------

There are two variants of this first testing phase depending on
whether or not you have access to a file called `puf.csv` that
contains a representative sample of tax filing units used by the
[TaxBrain web application](http://www.ospc.org/taxbrain) and by core
Tax-Calculator developers.

A brief description of the `puf.csv` file is followed by
instructions on how to run the two variants of the first-phase tests.

The Tax-Calculator `puf.csv` file has been constructed by the core
development team by merging information from the most recent publicly
available IRS SOI PUF file and from the Census CPS file for the
corresponding year.  If you have acquired from IRS the most recent SOI
PUF file and want to execute the tests that require the `puf.csv`
file, contact the core development team to discuss your options.

**NO PUF.CSV**: If you do not have access to the `puf.csv` file, run
the first-phase of testing as follows at the command prompt in the
tax-calculator directory at the top of the repository directory tree:

```
cd taxcalc
py.test -m "not requires_pufcsv"
```

This will start executing a pytest suite containing hundreds of tests,
but will skip the few tests that require the `puf.csv` file as input.
Depending on your computer, the execution time for this incomplete
suite of tests is roughly two minutes.

**HAVE PUF.CSV**: If you do have access to the `puf.csv` file, copy it
into the tax-calculator directory at the top of the repository
directory tree (but **never** add it to your repository) and run the
first-phase of testing as follows at the command prompt in the
tax-calculator directory at the top of the repository directory tree:

```
cd taxcalc
py.test
```

This will start executing a pytest suite containing hundreds of tests,
including the few tests that require the `puf.csv` file as input.
Depending on your computer, the execution time for this complete suite
of unit tests is roughly four minutes.

Testing with validation/tests
-----------------------------

The current version of the validation/tests runs only under Mac and
Linux; if you are working under Windows, skip this second phase of
testing.  See the [description of the validation
tests](taxcalc/validation/README.md) for more details.

Run the second-phase of testing as follows at the Mac or Linux command
prompt in the tax-calculator directory at the top of the repository
directory tree:

```
cd taxcalc/validation
./tests
```

This will start executing the validation/tests.  Depending on your
computer, the execution time for this suite of validation/tests is
roughly one minute.

Testing with comparison/reform_results.py
-----------------------------------------

This is the longest running test, which takes roughly eleven minutes.
It generates aggregate revenue estimates for over fifty reform
proposals writing those results to the `reform_results.txt` file.
This test requires access to the `puf.csv` file.  So, if you do not
have access to this file, skip this test.  If you do have access to
the `puf.csv` file, copy it into the tax-calculator directory at the
top of the repository directory tree (but **never** add it to your
repository) and run the third-phase of testing as follows at the
command prompt in the tax-calculator directory at the top of the
repository directory tree:

```
cd taxcalc/comparison
python reform_results.py
```

The output from this command, the `reform_results.txt` file, is under
version control, so difference can been seen by using the `git diff`
command.

Interpreting the Test Results
-----------------------------

If you are adding an enhancement that expands the capabilities of the
Tax-Calculator, then all the tests you can run should pass before you
submit a pull request containing the enhancement.  In addition, it
would be highly desirable to add a test to the pytest suite, which is
located in the ```taxcalc/tests``` directory, that somehow checks that
your enhancement is working as you expect it to work.

On the other hand, if you think you have found a bug in the
Tax-Calculator source code, the first thing to do is add a test to the
pytest suite that demonstrates how the source code produces an
incorrect result (that is, the test fails because the result is
incorrect).  Then change the source code to fix the bug and
demonstrate that the newly-added test, which used to fail, now passes.

Updating the Test Results
-------------------------

After an enhancement or bug fix, you may be convinced that the new and
different first-phase test results are, in fact, correct.  How do you
eliminate the test failures?  For all but the few tests that require
the `puf.csv` file as input, simply edit the appropriate
`taxcalc/tests/test_*.py` file so that the test passes when you rerun
py.test.  If there are failures for the tests that require the
`puf.csv` file as input, the new test results will be written to a
file named `pufcsv_*_actual.txt` (where the value of `*` depends on
the test).  Use any diff utility to see the differences between this
new `pufcsv_*_actual.txt` file and the old `pufcsv_*_expect.txt` file.
Then copy the new `actual` file to the `expect` file overwriting the
old expected test results.  When all this is done, rerunning py.test
should produce no failures.  If so, then delete any
`pufcsv_*_actual.txt` files and commit all the revised `test_*.py` and
`pufcsv_*_expect.txt` files.
