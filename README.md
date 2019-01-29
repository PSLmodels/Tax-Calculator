[![PSL cataloged](https://img.shields.io/badge/PSL-cataloged-a0a0a0.svg)](https://www.PSLmodels.org)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Build Status](https://travis-ci.org/PSLmodels/Tax-Calculator.svg?branch=master)](https://travis-ci.org/PSLmodels/Tax-Calculator)
[![Codecov](https://codecov.io/gh/PSLmodels/Tax-Calculator/branch/master/graph/badge.svg)](https://codecov.io/gh/PSLmodels/Tax-Calculator)


Tax-Calculator
==============

This document tells you how to begin using or contributing to
Tax-Calculator.  This is the first document to read when learning
about Tax-Calculator.

If you only want to **use** Tax-Calculator, you should finish reading
this document and then read the [user
guide](https://PSLmodels.github.io/Tax-Calculator/) that describes how
to use Tax-Calculator on your own computer (without doing any
programming) and how to use the Tax-Calculator web application called
[TaxBrain](https://www.ospc.org/taxbrain/).  If you want the most
flexibility in using Tax-Calculator on your own computer, read the
user guide first and then read our [Cookbook of Tested Recipes for
Python Programming with
Tax-Calculator](https://PSLmodels.github.io/Tax-Calculator/cookbook.html).

If you also want to **contribute** to Tax-Calculator, you should
finish reading this document, then read the [user
guide](https://PSLmodels.github.io/Tax-Calculator/), and finally read
the [contributor
guide](https://github.com/PSLmodels/Tax-Calculator/blob/master/CONTRIBUTING.md#tax-calculator-contributor-guide).


What is Tax-Calculator?
-----------------------

Tax-Calculator simulates the USA federal individual income and payroll
tax system.  In conjunction with [micro
data](https://github.com/PSLmodels/taxdata#about-taxdata-repository)
that represent the USA population, Tax-Calculator can be used to
estimate the aggregate revenue and distributional effects of tax
reforms under static analysis assumptions.  In conjunction with other
modules, Tax-Calculator can be used to estimate reform effects under a
range of non-static assumptions.  Tax-Calculator is written in Python,
an interpreted language that can execute on Windows, Mac, or Linux.
It is released under an [open-source
license](https://github.com/PSLmodels/Tax-Calculator/blob/master/LICENSE.md#license).


Disclaimer
----------

Results will change as model data and logic improve. A fundamental
reason for adopting open-source methods in this project is so that
people from all backgrounds can contribute to the models that our
society uses to assess economic policy; when community-contributed
improvements are incorporated, the model will produce different
results.


Getting Started
---------------

The first step for everyone (users and developers) is to open a free
GitHub account so that you can communicate with Tax-Calculator
developers.  This is by far the easiest way to ask questions, make
suggestions, or report bugs.  Note only does this put you into direct
contact with Tax-Calculator develops, it allows the community of more
experienced users, all of whom are watching the Tax-Calculator GitHub
repository, to answer your questions.  You can create an account at
the [Join
GitHub](https://github.com/join?source=experiment-header-dropdowns)
webpage.  And then you can specify how you want to "watch" the
Tax-Calculator repository by clicking on the Watch button in the
upper-right corner of the [Tax-Calculator main
page](https://github.com/PSLmodels/Tax-Calculator).

The second step is to get familiar with Tax-Caclulator code by reading
the [code
documentation](https://PSLmodels.github.io/Tax-Calculator/code.html).

Then after taking these two steps, you can do any of these things:

1. If you want to **ask a question**, create a new issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues)
posing your question about Tax-Calculator as clearly as possible.

2. If you want to **report a bug**, create a new issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think is wrong with Tax-Calculator.

3. If you want to **request an enhancement**, create a new issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think should be added to Tax-Calculator.

4. If you want to **propose code changes**, follow the directions in
the [contributor
guide](https://github.com/PSLmodels/Tax-Calculator/blob/master/CONTRIBUTING.md#tax-calculator-contributor-guide)
on how to fork and clone the Tax-Calculator git repository.  Before
developing any code changes be sure to read completely the contributor
guide.  The Tax-Calculator [release
history](https://github.com/PSLmodels/Tax-Calculator/blob/master/RELEASES.md#tax-calculator-release-history)
and [change
history](https://github.com/PSLmodels/Tax-Calculator/blob/master/CHANGES.md#tax-calculator-change-history)
provide descriptions of features introduced or changed in past
Tax-Calculator releases.  The release history is more technical while
the change history is less technical and may be sufficient for many
users.


Citing Tax-Calculator
---------------------

Please cite the source of your analysis as "Tax-Calculator release
#.#.#, author's calculations." If you wish to link to Tax-Calculator,
`https://PSLmodels.github.io/Tax-Calculator/` is
preferred. Additionally, we strongly recommend that you describe the
input data used, and provide a link to the materials required to
replicate your analysis or, at least, note that those materials are
available upon request.


Additional Information
----------------------

- [Ongoing cross-model validation
  work](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/validation/README.md#validation-of-tax-calculator-logic)

- [Plans for future Tax-Calculator
  development](https://github.com/PSLmodels/Tax-Calculator/blob/master/ROADMAP.md#plans-for-future-tax-calculator-development)

- [Tax-Calculator origins and
  contributors](https://github.com/PSLmodels/Tax-Calculator/blob/master/CONTRIBUTORS.md#tax-calculator-contributors)
