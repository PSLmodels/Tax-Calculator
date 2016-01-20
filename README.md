[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator
==============

The Tax-Calculator simulates the US federal individual income tax
system.  In conjunction with micro data that represent the US
population and a set of behavioral assumptions, the Tax-Calculator can
be used to conduct revenue scoring and distributional analyses of tax
policies.  The Tax-Calculator is written in Python, an interpreted
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

At the moment there are three ways to start using the Tax-Calculator.

The **first way** is to install the Tax-Calculator repository on your
computer.  Do this by following the instructions in our [Contributor
Guide](http://taxcalc.readthedocs.org/en/latest/contributor_guide.html)
and then reading about our [testing procedures](TESTING.md).  This way
allows you to read the source code and contribute enhancements to the
source code.  While this way does not provide you with a
representative sample of tax filing units, it does allow you to
estimate tax liabilities and marginal tax rates for any collection of
filing units specified in [Internet-TAXSIM input
format](http://users.nber.org/~taxsim/taxsim-calc9/) using the
```simtax.py``` command-line interface to the Tax-Calculator.

The **second way** is to access the Tax-Calculator through our web
application, [TaxBrain](http://www.ospc.org/taxbrain).  This way
allows you to generate tax reform estimates using a representative
sample of tax filing units that is not part of the Tax-Calculator
repository.

The **third way**, which is for advanced Anaconda users, involves
installing a taxcalc package on your local computer.  A new taxcalc
package is generated for every release of the Tax-Calculator.  We use
the package to install taxcalc on Amazon Web Services (AWS) instances
that run the TaxBrain web application.  You can get the latest release
of the Tax-Calculator to run on your computer via the command ```conda
install -c ospc taxcalc```.  Note that this package does not include a
micro data set that represents the US population.  Also, note that
there is some skill involved in Getting Started the first way and
installing the taxcalc package on the same local computer.

And, of course, you can get started with any combination of these
three ways of using the Tax-Calculator.
