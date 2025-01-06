Testing
=======

This description of Tax-Calculator testing procedures is written for a
person who wants to contribute changes to Tax-Calculator source code.

It assumes that you have read {doc}`contributor_guide` and
{doc}`param_naming`, have forked the [central GitHub Tax-Calculator
repository](https://github.com/PSLmodels/Tax-Calculator) to your
GitHub account, and have cloned that forked copy to your local
computer.

This document also assumes that you have read {doc}`pr_workflow`
so that you understand where the testing procedures fit into
the broader workflow of preparing a pull request that changes
Tax-Calculator source code.

There are two phases of testing: testing that the source code
complies with the Tax-Calculator coding style and testing that
the source code does not contain bugs.

## Testing coding style

The Tax-Calculator project follows `pycodestyle` and `pylint`
recommended coding style in most cases.

Check that your changes on a local branch are coding-style compliant
by running the coding-style test in the top-level Tax-Calculator
directory as follows:

```
make cstest
```

No messages indicate the tests pass.  Fix any warnings.  When you pass
all these coding-style tests, proceed to the second phase of testing.

## Testing with pytest

There are two variants of this second testing phase depending on
whether or not you have access to a file called `puf.csv` that
contains a representative sample of tax filing units derived from the
IRS-SOI PUF data.

A brief description of the `puf.csv` file is followed by instructions
on how to run the two variants of the second-phase tests.

The Tax-Calculator `puf.csv` file has been constructed by the core
development team by merging information from a publicly available
IRS-SOI PUF file for 2011 and from the Census CPS file for the
corresponding year.  If you have acquired from IRS the 2011 SOI PUF
file and want to execute the tests that require the `puf.csv` file,
contact the core development team to discuss your options.

**NO PUF.CSV**: If you do not have access to the `puf.csv` file (or if
you just want to do a quick test), run the second-phase of testing as
follows at the command prompt in the Tax-Calculator directory:

```
make pytest-cps
```

This will start executing a pytest suite containing hundreds of tests,
but will skip the tests that require the `puf.csv` file as input and
the tests that are executed only just before a new release is being
prepared.

**HAVE PUF.CSV**: If you do have access to the `puf.csv` file, copy it
into the Tax-Calculator directory at the top of the repository
directory tree (but **never** add it to your repository) and run the
second-phase of testing as follows at the command prompt in the
Tax-Calculator directory:

```
make pytest
```

This will start executing a pytest suite containing hundreds of tests,
including the tests that require the `puf.csv` file as input but
excluding the tests that are executed only just before a new release
is being prepared.

Just before releasing a new version of Tax-Calculator or just after
adding a new parameter to `policy_current_law.json`, you should also
execute the pre-release tests using this command:

```
make pytest-all
```

## Interpreting test results

If you are adding an enhancement that expands the capabilities of the
Tax-Calculator, then all the tests you can run should pass before you
submit a pull request containing the enhancement.  In addition, it
essential to add a test to the pytest suite, which is located in the
`taxcalc/tests` directory, that somehow checks that your enhancement
is working as you expect it to work.

On the other hand, if you think you have found a bug in the existing
Tax-Calculator source code, the first thing to do is add a test to the
pytest suite that demonstrates how the source code produces an
incorrect result (that is, the test fails because the result is
incorrect).  Then change the source code to fix the bug and
demonstrate that the newly-added test, which used to fail, now passes.

## Updating test results

After an enhancement or bug fix, you may be convinced that the new and
different second-phase test results are, in fact, correct.  How do you
eliminate the test failures?  For all but the few tests that require
the `puf.csv` file or the `cps.csv` file as input, simply edit the
appropriate `taxcalc/tests/test_*.py` file so that the test passes
when you rerun pytest.  If there are failures for the tests that write
results files, read the test error message for instructions about how
to update the test results.
