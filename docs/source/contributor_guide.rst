Contributor Guide
=================

The purpose of this guide is to get you to the point where you can
make improvements to the Tax-Calculator and share them with the rest
of the team.

We keep track of our Tax-Calculator code using `Git`_, but we don't
expect you to be an expert Git user. Where possible, we link to Git
and GitHub documentation to help with some of the unfamiliar
terminology. Following the next steps will get you up and running and
contributing to our model even if you've never used anything like Git.

If you have already completed the Setup Python and Setup Git sections,
please skip to `Workflow`_.

Setup Python
-------------

The Tax-Calculator is written in the Python programming language.
Download and install the free Anaconda distribution of Python from
`Continuum Analytics`_.  You must do this even if you already have
Python installed on your computer because the Anaconda distribution
contains all the additional Python packages that we use to conduct tax
calculations (many of which are not included in other Python
installations).  You can install the Anaconda distribution without
having administrative privileges on your computer and the Anaconda
distribution will not interfere with any Python installation that came
as part of your computer's operating system.

Setup Git
----------

1. Create a `GitHub`_ user account.

2. Install Git on your local machine by following steps 1-4 on `Git
   setup`_.

3. Tell Git to remember your GitHub password by following steps 1-4 on
   `password setup`_.

4. Sign in to GitHub and create your own `remote`_ `repository`_
   (repo) of Tax-Calculator by clicking `Fork`_ in the upper
   right corner of the `Tax-Calculator's GitHub page`_. Select your
   username when asked "Where should we fork this repository?"

5. From your command line, navigate to the directory on your computer
   where you would like your local repo to live.

6. Create a local repo by entering at the command line the text after
   the $. [1]_ This step creates a directory called tax-calculator in
   the directory that you specified in the prior step.

   .. code-block:: python

      $ git clone https://github.com/[github-username]/tax-calculator.git

7. From your command line or terminal, navigate to your local
   tax-calculator directory.

8. Make it easier to `push`_ your local work to others and `pull`_
   others' work to your local machine by entering at the command line:

   .. code-block:: python

      $ cd tax-calculator
      tax-calculator$ git remote add upstream https://github.com/open-source-economics/tax-calculator.git

9. Create a conda environment with all of the necessary packages to
   execute the source code:

   .. code-block:: python

      tax-calculator$ conda env create

10. The prior command will create a conda environment called "taxcalc-dev".
    Activate this environment as follows:

    .. code-block:: python

       tax-calculator$ source activate taxcalc-dev

    If you are working on Windows, use the following from the command line:

    .. code-block:: python
   
       tax-calculator$ activate taxcalc-dev
   
11. To check that everything is working properly, run the following at
    the command line from the tax-calculator directory, but skip the
    validation tests if you are working on Windows.  For more detail on
    Tax-Calculator testing procedures, read the `testing documentation`_.

   .. code-block:: python

      tax-calculator$ cd taxcalc
      tax-calculator/taxcalc$ py.test -m "not requires_pufcsv"
      tax-calculator/taxcalc$ cd validation
      tax-calculator/taxcalc/validation$ ./tests

   If all the tests pass, you're good to go. If they don't pass, enter
   the following updates at the command line and then try running the
   tests again. If the tests still don't pass, please contact us.

   .. code-block:: python

      tax-calculator$ conda update conda
      tax-calculator$ conda update anaconda
      tax-calculator$ conda env update

If you've made it this far, you've successfully made a remote copy (a
fork) of central Tax-Calculator repo. That remote repo is hosted on
GitHub.com. You've also created a local repo (a `clone`_) that lives
on your machine and only you can see; you will make your changes to
the Tax-Calculator by editing the files in the tax-calculator
directory on your machine and then submitting those changes to your
local repo. As a new contributor, you will push your changes from your
local repo to your remote repo when you're ready to share that work
with the team.

Don't be alarmed if the above paragraph is confusing. The following
section introduces some standard Git practices and guides you through
the contribution process.

.. _Workflow:

Workflow
--------

The following text describes a typical workflow for the Tax-Calculator
simulation model. Different workflows may be necessary in some
situations, in which case other contributors are here to help.

1. Before you edit the calculator on your machine, make sure you have
   the latest version of the central Tax-Calculator by executing the
   following **three** Git commands:

   a. Download all of the content from the central Tax-Calculator repo.
      Navigate to your local tax-calculator directory and enter the
      following text at the command line.

      .. code-block:: python

         tax-calculator$ git fetch upstream

   b. Tell Git to switch to the master branch in your local repo.

      .. code-block:: python

         tax-calculator$ git checkout master

   c. Update your local master branch to contain the latest content of
      the central master branch using `merge`_. This step ensures that
      you are working with the latest version of the Tax-Calculator.

      .. code-block:: python

         tax-calculator$ git merge upstream/master

2. Create a new `branch`_ on your local machine. Think of your
   branches as a way to organize your projects. If you want to work on
   this documentation, for example, create a separate branch for that
   work. If you want to change the maximum child care tax credit in
   the Tax-Calculator, create a different branch for that project.

   .. code-block:: python

      tax-calculator$ git checkout -b [new-branch-name]

3. See :doc:`Making changes to your local copy of the Tax-Calculator
   </make_local_change>` for examples showing you how to do just that.

4. As you make changes, frequently check that your changes do not
   introduce bugs or degrade the accuracy of the Tax-Calculator. To do
   this, run the following commands from the command line from inside
   the tax-calculator/taxcalc directory (but skip the validation tests
   if you are working on Windows). If the tests do not pass, try to
   fix the issue by using the information provided by the error
   message. If this isn't possible or doesn't work, we are here to
   help.

   .. code-block:: python

      tax-calculator/taxcalc$ py.test -m "not requires_pufcsv"
      tax-calculator/taxcalc$ cd validation
      tax-calculator/taxcalc/validation$ ./tests

5. Now you're ready to `commit`_ your changes to your local repo using
   the code below. The first line of code tells Git to track a
   file. Use "git status" to find all the files you've edited, and
   "git add" each of the files that you'd like Git to track. As a
   rule, do not add large files. If you'd like to add a file that is
   larger than 25 MB, please contact the other contributors and ask how to
   proceed. The second line of code commits your changes to your local
   repo and allows you to create a commit message; this should be a
   short description of your changes.

   *Tip*: Committing often is a good idea as Git keeps a record of
   your changes. This means that you can always revert to a previous
   version of your work if you need to.

   .. code-block:: python

      tax-calculator$ git add [filename]
      tax-calculator$ git commit -m "[description-of-your-commit]"

6. Periodically, make sure that the branch you created in step 2
   is in sync with the changes other contributors are making to 
   the central master branch by fetching upstream and merging
   upstream/master into your branch. 

   .. code-block:: python

       tax-calculator$ git fetch upstream
       tax-calculator$ git merge upstream/master

    You may need to resolve conflicts that arise when another
    contributor changed the same section of code that you are 
    changing. Feel free to ask other contributors for guidance 
    if this happens to you. If you do need to fix a merge
    conflict, re-run the test suite afterwards (step 4.)

6. When you are ready for other team members to review your code, make
   your final commit and push your local branch to your remote repo.

   .. code-block:: python

      tax-calculator$ git push origin [new-branch-name]

7. From the GitHub.com user interface, `open a pull request`_.  


Simple Usage
------------

For examples of Tax-Calculator usage (without changing tax parameter
values and without adding a new tax parameter), you can view our code
sample notebook: `10 Minutes To Tax-Calculator`_.


.. [1] The dollar sign is the end of the command prompt on a Mac.  If
       you're on Windows, this is usually the right angle bracket (>).
       No matter the symbol, you don't need to type it (or anything to
       its left, which shows the current working directory) at the
       command line before you enter a command; the prompt symbol and
       preceding characters should already be there.


.. _`Git`:
   https://help.github.com/articles/github-glossary/#git

.. _`quant econ`:
   http://quant-econ.net/py/learning_python.html

.. _`GitHub`:
   https://github.com/

.. _`Git setup`:
   https://help.github.com/articles/set-up-git/

.. _`Fork`:
   https://help.github.com/articles/github-glossary/#fork

.. _`password setup`:
   https://help.github.com/articles/caching-your-github-password-in-git/

.. _`Tax-Calculator's GitHub page`: 
   https://github.com/open-source-economics/Tax-Calculator

.. _`repository`:
   https://help.github.com/articles/github-glossary/#repository

.. _`push`:
   https://help.github.com/articles/github-glossary/#push

.. _`pull`:
   https://help.github.com/articles/github-glossary/#pull

.. _`Github Flow`:
   https://guides.github.com/introduction/flow/

.. _`10 Minutes To Tax-Calculator`:
   http://nbviewer.ipython.org/github/open-source-economics/Tax-Calculator/
   blob/master/docs/notebooks/10_Minutes_to_Tax-Calculator.ipynb

.. _`Behavior Example`:
   http://nbviewer.ipython.org/github/open-source-economics/Tax-Calculator/
   blob/master/docs/notebooks/Behavioral_example.ipynb

.. _`Continuum Analytics`:
   http://www.continuum.io/downloads

.. _`remote`:
   https://help.github.com/articles/github-glossary/#remote

.. _`testing documentation`:
   https://github.com/open-source-economics/Tax-Calculator/blob/master/TESTING.md

.. _`clone`:
   https://help.github.com/articles/github-glossary/#clone

.. _`branch`:
   https://help.github.com/articles/github-glossary/#branch

.. _`merge`:
   https://help.github.com/articles/github-glossary/#merge

.. _`commit`:
   https://help.github.com/articles/github-glossary/#commit

.. _`fetch`:
   https://help.github.com/articles/github-glossary/#fetch

.. _`upstream`:
   https://help.github.com/articles/github-glossary/#upstream

.. _`pull request`:
   https://help.github.com/articles/github-glossary/#pull-request

.. _`open a pull request`:
   https://help.github.com/articles/creating-a-pull-request/#creating-the-pull-request
