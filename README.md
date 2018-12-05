[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Build Status](https://travis-ci.org/PSLmodels/Tax-Calculator.svg?branch=master)](https://travis-ci.org/PSLmodels/Tax-Calculator)
[![Codecov](https://codecov.io/gh/PSLmodels/Tax-Calculator/branch/master/graph/badge.svg)](https://codecov.io/gh/PSLmodels/Tax-Calculator)


Developing Tax-Calculator
=========================

This document tells you how to begin contributing to Tax-Calculator by
reporting a bug, improving the documentation, or making an enhancement
to the Python source code.  If you only want to **use** Tax-Calculator,
you should begin by reading the [user
documentation](https://PSLmodels.github.io/Tax-Calculator/)
that describes how to use Tax-Calculator on your own computer (without
doing any programming) and how to use the Tax-Calculator web application
called [TaxBrain](https://www.ospc.org/taxbrain/).  If you want the most
flexibility in using Tax-Calculator on your own computer, read the [user
documentation](https://PSLmodels.github.io/Tax-Calculator/)
first and then read our [Cookbook of Tested Recipes for Python Programming
with
Tax-Calculator](https://PSLmodels.github.io/Tax-Calculator/cookbook.html).


What is Tax-Calculator?
-----------------------

Tax-Calculator simulates the USA federal individual income and payroll
tax system.  In conjunction with micro data that represent the USA
population, Tax-Calculator can be used to estimate the aggregate
revenue and distributional effects of tax reforms under static
analysis assumptions.  In conjunction with other modules,
Tax-Calculator can be used to estimate reform effects under a range of
non-static assumptions.  Tax-Calculator is written in Python, an
interpreted language that can execute on Windows, Mac, or Linux.


Disclaimer
----------

Results will change as model data and logic improve. A fundamental
reason for adopting open source methods in this project is so that
people from all backgrounds can contribute to the models that our
society uses to assess economic policy; when community-contributed
improvements are incorporated, the model will produce different
results.


Getting Started
---------------

If you want to **report a bug**, create a new issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think is wrong with Tax-Calculator.

If you want to **request an enhancement**, create a new issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think should be added to Tax-Calculator.

If you want to **propose code changes**, follow the directions in the
[Contributor
Guide](https://taxcalc.readthedocs.io/en/latest/contributor_guide.html)
on how to fork and clone the Tax-Calculator git repository.  Before
developing any code changes be sure to read completely the Contributor
Guide and then read about the [pull-request
workflow](https://github.com/PSLmodels/Tax-Calculator/blob/master/WORKFLOW.md#tax-calculator-pull-request-workflow).
The Tax-Calculator [release
history](https://github.com/PSLmodels/Tax-Calculator/blob/master/RELEASES.md#tax-calculator-release-history)
provides a high-level summary of past pull requests and access to a
complete list of merged, closed, and pending pull requests.

If you are relying on Tax-Calculator capabilities in your own project,
be sure to read the definition of the [Tax-Calculator Public
API](https://taxcalc.readthedocs.io/en/latest/public_api.html).


Citing Tax-Calculator
---------------------

Please cite the source of your analysis as "Tax-Calculator release
#.#.#, author's calculations." If you wish to link to Tax-Calculator,
https://PSLmodels.github.io/Tax-Calculator/ is
preferred. Additionally, we strongly recommend that you describe the
input data used, and provide a link to the materials required to
replicate your analysis or, at least, note that those materials are
available upon request.
