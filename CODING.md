[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator Coding Style
===========================

This description of Tax-Calculator coding style is written for a
person who wants to contribute changes to Tax-Calculator source code.
It assumes that you have read the [Contributor
Guide](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html),
have cloned the [central GitHub Tax-Calculator
repository](https://github.com/open-source-economics/Tax-Calculator)
to your GitHub account and to your local computer, and are familiar
with how to prepare a pull request for consideration by the core
development team.  This document describes the coding style you should
follow when preparing a pull request on local computer.  By coding
style we mean primarily the vertical and horizontal spacing of the
code and the naming of new variables.

You main objective is to write Python code that is indistinguishable
in style from existing code in the repository.  In other words, after
your new code is merged with existing code it should be difficult for
somebody else to determine what you contributed.

In order to achieve this objective any new policy parameter names must
comply with the [parameter naming and placement
conventions](http://taxcalc.readthedocs.io/en/latest/parameter_naming.html).

In addition, any new or revised code must meet certain coding style
guidelines.

There are two recommended tools that can help you develop seamless and
correct code enhancements.

pep8
----

One of these tools, `pep8`, enforces coding styles that are required
of all Python code in the repository, and therefore, all pull requests
are tested using the `pep8` tool.  Pull requests that fail these
`pep8` tests need to be revised before they can be merged into the
repository.  The most efficient way to comply with this coding style
requirement is to process each file containing revisions through
`pep8` on your local computer before submitting your pull request.

Make sure you have an up-to-date version of `pep8` installed on your
computer by entering at the operating system command line:
```
pep8 --version
```
If you get a no-such-command error, install `pep8` as follows:
```
conda install pep8
```
If you do have `pep8` installed, but the version is before 1.7.0,
then get a more recent version as follows:
```
conda update pep8
```
Once you have a current version of `pep8` installed on your computer,
use the `pep8` tool as follows:
```
pep8 --ignore=E402 records.py
```
where in the above example you want to check the coding style of your
proposed revisions to the `records.py` file.

pylint
------

The other of these tools, `pylint`, warns about deviations from a
broader set coding styles than does `pep8`.  The use of `pylint`,
while being the number one recommendation in the [Google Python Style
Guide](https://google.github.io/styleguide/pyguide.html), is
strictly-speaking optional for Tax-Calculator work.  But several
important files in the repository are maintained in a way that their
coding style does not generate any `pylint` warnings.  You can
determine which files these are by looking for the comment near the
top of the file that begins `# CODING-STYLE CHECKS:`.  It is
recommended that, if you are proposing changes in one these files, you
check your work by running the `pylint` command listed in that file's
coding-style comment.

Make sure you have an up-to-date version of `pylint` installed on your
computer by entering at the operating system command line:
```
pylint --version
```
If you get a no-such-command error, install `pylint` as follows:
```
conda install pylint
```
If you do have `pylint` installed, but the version is before 1.5.4,
then get a more recent version as follows:
```
conda update pylint
```
