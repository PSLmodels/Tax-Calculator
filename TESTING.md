[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator Testing Procedures
=================================

This description of Tax-Calculator testing procedure is written for a
person who wants to contribute changes to Tax-Calculator source code.
It assumes that you have read the [Contributor
Guide](http://taxcalc.readthedocs.org/en/latest/contributor_guide.html),
have cloned the [central GitHub Tax-Calculator
repository](https://github.com/open-source-economics/Tax-Calculator)
to your GitHub account and to your local computer, and are familiar
with how to prepare a pull request for consideration by the core
development team.  This document describes the testing procedure you
should follow on your local computer before submitting a development
branch as a pull request to the central Tax-Calculator repository at
GitHub.

Currently there are two phases of testing.

Testing with py.test
--------------------

There are two variants of this first testing phase depending on
whether or not you have access to a file called ```puf.csv``` that
contains a representative sample of tax filing units used by the
[TaxBrain web application](http://www.ospc.org/taxbrain) and by core
Tax-Calculator developers.

A brief description of the ```puf.csv``` file is followed by
instructions on how to run the two variants of the first-phase tests.

The Tax-Calculator ```puf.csv``` file has been constructed by the core
development team by merging information from the most recent publicly
available IRS SOI PUF file and from the Census CPS file for the
corresponding year.  If you have acquired from IRS the most recent SOI
PUF file and want to execute the tests that require the ```puf.csv```
file, contact the core development team to discuss your options.

**NO PUF.CSV**: If you do not have access to the ```puf.csv``` file,
run the first-phase of testing as follows at the command prompt in the
tax-calculator directory at the top of the repository directory tree:

```
cd taxcalc
py.test -m "not requires_pufcsv"
```

This will start executing a pytest suite containing more than one
hundred tests, but will skip the few tests that require the
```puf.csv``` file as input.  Depending on your computer, the
execution time for this incomplete suite of tests is about three
minutes.

**HAVE PUF.CSV**: If you do have access to the ```puf.csv``` file,
copy it into the tax-calculator directory at the top of the repository
directory tree (but **never** add it to your repository) and run the
first-phase of testing as follows at the command prompt in the
tax-calculator directory at the top of the repository directory tree:

```
cd taxcalc
py.test
```

This will start executing a pytest suite containing more than one
hundred tests, including the few tests that require the ```puf.csv```
file as input.  Depending on your computer, the execution time for
this incomplete suite of tests is about five minutes.

Testing with validation/tests
-----------------------------

There are two variants of this second testing phase depending on
whether or not you want to run a shorter or a longer test.  The
current version of the validation/tests run only under Mac and Linux;
if you are working under Windows, skip this second phase of testing.

Both variants of the validation/tests generate samples of tax filing
units whose attributes are specified in a random, non-representative
manner.  Each sample is used to generate tax liabilities, intermediate
income tax results, and marginal tax rates using Internet-TAXSIM and
simtax.py, which is a command-line interface to the Tax-Calculator.
And then the output from the two models are compared item-by-item and
unit-by-unit to produce cross-model-validation summary results.  See
the [description of the Internet-TAXSIM validation
tests](taxcalc/validation/README.md) for more details.  The only
difference between the two variants of this second phase of testing is
the number of randomly-generated samples that are generated and
compared.

**SHORTER TEST**: If you don't want to run all the validation/tests,
run the second-phase of testing as follows at the Mac or Linux command
prompt in the tax-calculator directory at the top of the repository
directory tree:

```
cd taxcalc/validation
./tests
```

This will start executing a subset of the validation/tests.  Depending
on your computer, the execution time for this incomplete suite of
validation/tests is about two minutes.

**LONGER TEST**: If you do want to run all the validation/tests, run
the second-phase of testing as follows at the Mac or Linux command
prompt in the tax-calculator directory at the top of the repository
directory tree:

```
cd taxcalc/validation
./tests all
```

This will start executing all of the validation/tests.  Depending on
your computer, the execution time for this complete suite of
validation/tests is about nine minutes.

Interpreting the Test Results
-----------------------------

If you are adding an enhancement that expands the capabilities of the
Tax-Calculator, then all the tests should pass before you submit a
pull request containing the enhancement.  In addition, it would be
highly desirable to add a test to the pytest suite, which are located
in the ```taxcalc/tests``` directory, that somehow checks that your
enhancement is working as you expect it to work.

On the other hand, if you think you have found a bug in the
Tax-Calculator source code, the first thing to do is add a test to the
pytest suite that demonstrates how the source code produces an incorrect
result.  Then change the source code to fix the bug and demonstrate that
the newly-added test, which used to fail, now passes.
