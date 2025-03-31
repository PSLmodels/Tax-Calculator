Getting started
===============

Tax-Calculator packages are available for Windows, Mac, and Linux computers
that have the free Anaconda Python 3.10, 3.11, or 3.12 distribution
installed.  You can use Tax-Calculator without doing any Python programming,
but the Anaconda distribution is required for Tax-Calculator to run.
Take the following four steps to get started.

## Install Anaconda Python

Download and install the free Anaconda distribution of Python from
[Anaconda](https://www.anaconda.com/products/individual).
You must do this even if you already have Python installed on your computer,
because the Anaconda distribution contains all the additional Python packages
that Tax-Calculator uses to conduct its calculations
(many of which are not included in other Python installations).
You can install the Anaconda distribution without having administrative
privileges on your computer and the Anaconda distribution will not interfere
with any Python installation that came as part of your computer's operating
system.

## Download Tax-Calculator package

Download a Tax-Calculator `taxcalc` package for your computer by executing
this command from the command prompt:

```
conda install -c conda-forge taxcalc
```

This command will also install all the Python packages required by
Tax-Calculator.

## Become a registered GitHub user

Open a free GitHub account so that you can communicate with Tax-Calculator
developers.
This is by far the easiest way to ask questions, make suggestions, or report
bugs.
Not only does this put you into direct contact with Tax-Calculator developers,
it allows the community of more experienced users, all of whom are watching the
Tax-Calculator GitHub repository, to answer your questions.
You can create an account at the [Join GitHub](https://github.com/join)
webpage.
And then you can specify how you want to "watch" the Tax-Calculator repository
by clicking on the _Watch_ button in the upper-right corner of the
[Tax-Calculator main page](https://github.com/PSLmodels/Tax-Calculator).

## Read Tax-Calculator user guide

Read the {doc}`../guide/index` about how to conduct tax analysis with
Tax-Calculator two different ways:
(a) without doing any computer programming, or
(b) by writing Python programs.
Then after reading the {doc}`overview`, you will be in a position to do any of
the following:

1.  If you want to **ask a question**,
[create a new issue](https://github.com/PSLmodels/Tax-Calculator/issues)
posing your question about Tax-Calculator as clearly as possible.

2.  If you want to **request an enhancement**,
[create a new issue](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think should be added to Tax-Calculator.

3.  If you want to **report a bug**,
[create a new issue](https://github.com/PSLmodels/Tax-Calculator/issues)
providing details on what you think is wrong with Tax-Calculator.
An ideal bug report demonstrates for a single filing unit that a Tax-Calculator
result is not the same as what you get when filling out the relevant IRS tax
form.

4.  If you want to **propose code changes**, follow the directions in the
{doc}`../contributing/contributor_guide` on how to fork and clone the
Tax-Calculator git repository.
Before developing any code changes, be sure to read completely the contributor
guide.
