[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator
==============

Tax-Calculator simulates the US federal individual income tax
system.  In conjunction with micro data that represent the US
population and a set of behavioral assumptions, Tax-Calculator can
be used to conduct revenue scoring and distributional analyses of tax
policies.  Tax-Calculator is written in Python, an interpreted
language that can execute on Windows, Mac, or Linux.

Disclaimer
==========

Results will change as the underlying models improve. A fundamental
reason for adopting open source methods in this project is so that
people from all backgrounds can contribute to the models that our
society uses to assess economic policy; when community-contributed
improvements are incorporated, the model will produce different
results.

Getting Started
===============

There are two common ways to get started with Tax-Calculator:

The **first way** is to install the Tax-Calculator repository on your
computer.  Do this by following the instructions in our [Contributor
Guide](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html).
After the installation you can read the source code and either use
Tax-Calculator as is or develop new Tax-Calculator capabilities.

When using Tax-Calculator on your computer you will have to supply
your own input data on tax filing units because the repository does
not include a representative sample of tax filing units.  However, you
can use it to estimate tax liabilities and marginal tax rates for any
collection of filing units specified in [Internet-TAXSIM input
format](http://users.nber.org/~taxsim/taxsim-calc9/) using the
`simtax.py` command-line interface to Tax-Calculator.  And you can
also process your own CSV-formatted data using the `inctax.py`
command-line interface to Tax-Calculator, but when doing this be
sure to read the [data-preparation guidelines](DATAPREP.md).

When developing new Tax-Calculator capabilities be sure to read about
our [coding style](CODING.md) and [testing procedures](TESTING.md)
after you have read completely the [Contributor
Guide](http://taxcalc.readthedocs.io/en/latest/contributor_guide.html).

The **second way** is to access Tax-Calculator through our web
application, [TaxBrain](http://www.ospc.org/taxbrain).  This way
allows you to generate aggregate and distributional tax reform
estimates using a nationally representative sample of tax filing units
that is not part of the Tax-Calculator repository.

And, of course, you can get started with Tax-Calculator both ways.

Citing Tax-Calculator
======================
Tax-Calculator (Version #.#.#)[Source code], https://github.com/open-source-economics/tax-calculator
