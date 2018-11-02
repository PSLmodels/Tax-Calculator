Tax-Calculator Testing Procedures
=================================

This description of Tax-Calculator testing procedures is written for a
person who wants to contribute changes to Tax-Calculator source code.

It assumes that you have read the [Contributor
Guide](https://taxcalc.readthedocs.io/en/latest/contributor_guide.html)
and the [conventions about naming and placing new policy
parameters](https://taxcalc.readthedocs.io/en/latest/parameter_naming.html),
have forked the [central GitHub Tax-Calculator
repository](https://github.com/open-source-economics/Tax-Calculator)
to your GitHub account, and have cloned that forked copy to your local
computer.

This document also assumes that you have read the [pull-request
workflow](https://github.com/open-source-economics/Tax-Calculator/blob/master/WORKFLOW.md#tax-calculator-pull-request-workflow)
document so that you understand where the testing procedures fit into
the broader workflow of preparing a pull request that changes
Tax-Calculator source code.

Currently there are two phases of testing.

Testing with pycodestyle (the program formerly known as pep8)
-------------------------------------------------------------

The first phase of testing checks the formatting of the Python code
against a PEP8-like standard.  Assuming you are in the top-level
directory of the repository, run these tests by doing:
```
pycodestyle taxcalc
```

No messages indicate the tests pass.  Fix any errors.  When you
pass all these PEP8-like tests, proceed to the second phase of testing.

If you are proposing changes in a JSON file, then you should also run
the following test:
```
pycodestyle --ignore=E501,E121 PATH_TO_JSON_FILE
```
where you replace `PATH_TO_JSON_FILE` with the relative path to the
JSON file you changed.  So, for example, if you edited the
`policy_current_law.json` file in the `taxcalc` subdirectory, you
would replace `PATH_TO_JSON_FILE` with
`taxcalc/policy_current_law.json`.

Testing with pytest
-------------------

There are two variants of this second testing phase depending on
whether or not you have access to a file called `puf.csv` that
contains a representative sample of tax filing units used by the
[TaxBrain web application](https://www.ospc.org/taxbrain) and by core
Tax-Calculator developers.

A brief description of the `puf.csv` file is followed by
instructions on how to run the two variants of the second-phase tests.

The Tax-Calculator `puf.csv` file has been constructed by the core
development team by merging information from the most recent publicly
available IRS SOI PUF file and from the Census CPS file for the
corresponding year.  If you have acquired from IRS the most recent SOI
PUF file and want to execute the tests that require the `puf.csv`
file, contact the core development team to discuss your options.

If you have access to the Tax-Calculator `puf.csv` file, you should
have access to the private GitHub repository `taxpuf`, from which
updates of the `puf.csv` are distributed.  When you receive a private
email announcing a new version of the `puf.csv` file, be sure to
execute a `conda update ... taxpuf` command (as described in the
`taxpuf` repository's README file) before executing the tests
described below.

**NO PUF.CSV**: If you do not have access to the `puf.csv` file (or if
you want to do just a quick test), run the second-phase of testing as
follows at the command prompt in the tax-calculator directory at the
top of the repository directory tree:
```
cd taxcalc
pytest -m "not requires_pufcsv and not pre_release" -n4
cd ..
```

This will start executing a pytest suite containing hundreds of tests,
but will skip the tests that require the `puf.csv` file as input and
the tests that are executed only just before a new release is being
prepared.  Depending on your computer, the execution time for this
incomplete suite of tests is roughly one minute.  The `-n4` option
calls for using as many as four CPU cores for parallel execution of the
tests.  If you want sequential execution of the tests (which will
take at least twice as long to execute), simply omit the `-n4` option.

**HAVE PUF.CSV**: If you do have access to the `puf.csv` file, copy it
into the Tax-Calculator directory at the top of the repository
directory tree (but **never** add it to your repository) and run the
second-phase of testing as follows at the command prompt in the
top-level directory:
```
cd taxcalc
pytest -m "not pre_release" -n4
cd ..
```

This will start executing a pytest suite containing hundreds of tests,
including the tests that require the `puf.csv` file as input but excluding
the tests that are executed only just before a new release is being
prepared. Depending on your computer, the execution time for this suite
of unit tests is roughly two minutes.  The `-n4` option calls for
using as many as four CPU cores for parallel execution of the tests.
If you want sequential execution of the tests (which will take at
least twice as long to execute), simply omit the `-n4` option.

Just before releasing a new version of Tax-Calculator or just after
adding a new parameter to `policy_current_law.json`, you should also
execute the pre-release tests using this command:
```
cd taxcalc
pytest -m pre_release -n4
cd ..
``` 

But if you execute the pre_release tests well before releasing a new
version of Tax-Calculator, be sure **not** to include the updated
`docs/index.html` file in your commit.  After checking that you can
make a `docs/index.html` file that is correct, revert to the old
version of `docs/index.html` by executing this command:
```
git checkout -- docs/index.html
```

Following this procedure will ensure that the documentation is not
updated before the Tax-Calculator release is available.

Interpreting the Test Results
-----------------------------

If you are adding an enhancement that expands the capabilities of the
Tax-Calculator, then all the tests you can run should pass before you
submit a pull request containing the enhancement.  In addition, it
would be highly desirable to add a test to the pytest suite, which is
located in the `taxcalc/tests` directory, that somehow checks that
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
different second-phase test results are, in fact, correct.  How do you
eliminate the test failures?  For all but the few tests that require
the `puf.csv` file or the `cps.csv` file as input, simply edit the
appropriate `taxcalc/tests/test_*.py` file so that the test passes
when you rerun pytest.  If there are failures for the tests that write
results files, read the test error message for instructions about how
to update the test results.

Optional Coding Style Testing with pylint
-----------------------------------------

There is another tool, `pylint`, that warns about deviations from a
broader set coding styles than does `pycodestyle`.  The use of
`pylint`, while being the number one recommendation in the [Google
Python Style Guide](https://google.github.io/styleguide/pyguide.html),
is strictly-speaking optional for Tax-Calculator work.  But several
important files in the repository are maintained in a way that their
coding style does not generate any `pylint` warnings.  You can
determine which files these are by looking for the comments near the
top of the file that begin `# CODING-STYLE CHECKS:`.  If there is a
line in these comments that mentions `pylint`, then this file is being
tested with `pylint`.  It is highly recommended that, if you are
proposing changes in one these files, you check your work by running
the `pylint` command listed in that file's coding-style comment.

Make sure you have an up-to-date version of `pylint` installed on your
computer by entering at the operating system command prompt:
```
pylint --version
```
If you get a no-such-command error, install `pylint` as follows:
```
conda install pylint
```
If you do have `pylint` installed, but the version is before 1.8.4,
then get a more recent version as follows:
```
conda update pylint
```
