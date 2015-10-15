Tax Calculator
==============

The Tax Calculator simulates the US federal individual income tax
system.  In conjunction with micro data that represent the US
population and a set of behavioral assumptions, the Tax Calculator can
be used to conduct revenue scoring and distributional analyses of tax
policies.  The Tax Calculator is written in Python, an interpreted
language that can execute on Windows, Mac, or Linux.


Disclaimer
==========

Results will change as the underlying models improve. A fundamental reason for adopting open source methods in this project is so that people from all backgrounds can contribute to the models that our society uses to assess economic policy; when community-contributed improvements are incorporated, the model will produce different results.

Getting Started
===============

At the moment there are two ways to start using the Tax Calculator.

The first way is install the Tax Calculator on your computer.  Do this
by following the instructions in our [Contributor
Guide](http://taxcalc.readthedocs.org/en/latest/contributor_guide.html).

The second way is to access the Tax Calculator through our web
application, [TaxBrain](http://www.ospc.org/taxbrain).

Conda Package for Advanced Anaconda Users
=========================================

Conda taxcalc packages are created for every release of the Tax
Calculator.  We use them to install taxcalc on Amazon Web Services
(AWS) instances that run the TaxBrain web application.  You can get
the latest release of the taxcalc package to run on your computer via
the command `conda install -c ospc taxcalc`.  Note that this package
does not include a micro data set that represents the US population.
