Tax-Calculator Contributor Guide
================================

The purpose of this guide is to get you to the point where you can
make improvements to the Tax-Calculator and share them with the rest
of the development team.

We keep track of Tax-Calculator source code using the [Git version
control system](https://git-scm.com/) via
[GitHub](https://help.github.com/articles/github-glossary/#git).  We
don't expect you to be an expert Git user. Where possible, we link to
Git and GitHub documentation to help with some of the unfamiliar
terminology (often from this [glossary of GitHub
terms](https://help.github.com/articles/github-glossary/). Following
the next steps will get you up and running and contributing to
Tax-Calculator even if you've never used anything like Git and GitHub.

If you have already completed the [Setup Python](#setup-python) and
[Setup Git](#setup-Git) sections, please skip to [Workflow](#workflow).

Setup Python
------------

Tax-Calculator is written in the Python programming language.
Download and install the free Anaconda distribution of Python 3.6 or
Python 3.7 from [Anaconda](https://www.anaconda.com/download/).  You
must do this even if you already have Python installed on your
computer because the Anaconda distribution contains all the additional
Python packages that we use to conduct tax calculations (many of which
are not included in other Python installations).  You can install the
Anaconda distribution without having administrative privileges on your
computer and the Anaconda distribution will not interfere with any
Python installation that came as part of your computer's operating
system.

Setup Git
---------

1. Create a free GitHub user account from the [GitHub home
page](https://github.com/).

2. Install Git on your local computer by following steps 1-4
[here](https://help.github.com/articles/set-up-git/).

3. Tell Git to remember your GitHub password by following steps 1-4
[here](https://help.github.com/articles/caching-your-github-password-in-git/).

4. Sign in to GitHub and create your own
   [remote](https://help.github.com/articles/github-glossary/#remote)
   [repository](https://help.github.com/articles/github-glossary/#repository)
   (or "repo" for short) of Tax-Calculator by clicking on
   [Fork](https://help.github.com/articles/github-glossary/#fork) in
   the upper right corner of the [Tax-Calculator GitHub
   page](https://github.com/PSLmodels/Tax-Calculator). Select your
   username when asked "Where should we fork this repository?"

5. From your command line, navigate to the directory on your computer
   where you would like your local repo to live.

6. Create a local repo by entering at the command line the text after
   the `$` character on Mac and Linux (or the `>` character on Windows).
   This step creates a directory called Tax-Calculator in
   the directory that you specified in the prior step:
   ```
   $ git clone https://github.com/[github-username]/Tax-Calculator.git
   ```

7. From your command line or terminal, navigate to your local
   Tax-Calculator directory.

8. Make it easier to
   [push](https://help.github.com/articles/github-glossary/#push) your
   local work to others and [pull]() others' work to your local computer
   by entering at the command line:
   ```
   $ cd Tax-Calculator
   $ git remote add upstream https://github.com/PSLmodels/Tax-Calculator.git
   ```

9. Create a conda environment with all of the necessary packages to
   execute Tax-Calculator source code in the Tax-Calculator directory:
   ```
   $ conda env create
   ```

10. The prior command will create a conda environment called `taxcalc-dev`.
    Activate this environment as follows if working on Mac or Linux:

    $ source activate taxcalc-dev

    If you are working on Windows, use the following from the command line::

    $ activate taxcalc-dev

    Important Note: never conda install the taxcalc package in the
    taxcalc-dev environment because the taxcalc source code and the
    installed package will conflict.

11. To check that everything is working properly, run the following at
    the command line in the Tax-Calculator directory:
    ```
    $ cd taxcalc
    $ py.test -m "not requires_pufcsv and not pre_release" -n4
    ```
    If you do have a copy of the `puf.csv` file used by Tax-Calculator,
    then on the second line above omit the 'not requires_pufcsv and'
    expression so as to execute `py.test -m "not pre_release" -n4`.

    If all the tests pass, you're good to go. If they don't pass, enter
    the following updates at the command line and then try running the
    tests again:
    ```
    $ conda update conda
    $ conda env update
    ```
    
    For more detail on Tax-Calculator testing procedures, read the
    [testing documentation](https://github.com/PSLmodels/Tax-Calculator/blob/master/TESTING.md).
    If the tests still don't pass, please contact us.

If you've made it this far, you've successfully made a remote copy (a
fork) of central Tax-Calculator repo. That remote repo is hosted on
GitHub.com. You've also created a local repo --- a
[clone](https://help.github.com/articles/github-glossary/#clone) ---
that lives on your computer and only you can see; you will make your
changes to the Tax-Calculator by editing the files in the
Tax-Calculator directory on your computer and then submitting those
changes to your local repo. As a new contributor, you will push your
changes from your local repo to your remote repo when you're ready to
share that work with the team.

Don't be alarmed if the above paragraph is confusing. The following
section introduces some standard Git practices and guides you through
the contribution process.

Workflow
--------

The following text describes a typical workflow for changing
Tax-Calculator.  Different workflows may be necessary in some
situations, in which case other contributors are here to help.

1. Before you edit the Tax-Calculator source code on your machine,
   make sure you have the latest version of the central Tax-Calculator
   repository by executing the following **four** Git commands:

   a. Tell Git to switch to the master branch in your local repo.
      Navigate to your local Tax-Calculator directory and enter the
      following text at the command line::

        Tax-Calculator$ git checkout master

   b. Download all of the content from the central Tax-Calculator repo::

        Tax-Calculator$ git fetch upstream

   c. Update your local master branch to contain the latest content of
      the central master branch using `merge`_. This step ensures that
      you are working with the latest version of the Tax-Calculator::

        Tax-Calculator$ git merge upstream/master

   d. Push the updated master branch in your local repo to your GitHub repo::

        Tax-Calculator$ git push origin master

2. Create a new `branch`_ on your local machine. Think of your
   branches as a way to organize your projects. If you want to work on
   this documentation, for example, create a separate branch for that
   work. If you want to change the maximum child care tax credit in
   the Tax-Calculator, create a different branch for that project::

     Tax-Calculator$ git checkout -b [new-branch-name]

3. If your changes involve creating a new tax policy parameter, be
   sure to read about Tax-Calculator :doc:`parameter naming
   conventions </parameter_naming>`.

4. As you make changes, frequently check that your changes do not
   introduce bugs or degrade the accuracy of the Tax-Calculator. To do
   this, run the following command from the command line from inside
   the Tax-Calculator/taxcalc directory::

     Tax-Calculator/taxcalc$ py.test -m "not requires_pufcsv and not pre_release" -n4

   If the tests do not pass, try to fix the issue by using the
   information provided by the error message. If this isn't possible
   or doesn't work, we are here to help.

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
   version of your work if you need to.  Do this to commit::

     Tax-Calculator$ git add [filename]
     Tax-Calculator$ git commit -m "[description-of-your-commit]"

6. Periodically, make sure that the branch you created in step 2
   is in sync with the changes other contributors are making to
   the central master branch by fetching upstream and merging
   upstream/master into your branch::

      Tax-Calculator$ git fetch upstream
      Tax-Calculator$ git merge upstream/master

   You may need to resolve conflicts that arise when another
   contributor changed the same section of code that you are
   changing. Feel free to ask other contributors for guidance
   if this happens to you. If you do need to fix a merge
   conflict, re-run the test suite afterwards (step 4.)

7. When you are ready for other team members to review your code, make
   your final commit and push your local branch to your remote repo::

     Tax-Calculator$ git push origin [new-branch-name]

8. From the GitHub.com user interface, `open a pull request`_.

9. When you open a GitHub pull request, a code coverage report will be
   automatically generated.  If your branch adds new code that is not
   tested, the code coverage percent will decline and the number of
   untested statements ("misses" in the report) will increase.  If
   this happens, you need to add to your branch one or more tests of
   your newly added code.  Add tests so that the number of untested
   statements is the same as it is on the master branch.

You should now read the more `detailed pull-request workflow`_ document.

   
Simple Usage
------------

For examples of Tax-Calculator usage, see the `Cookbook of Tested
Recipes for Python Programming with Tax-Calculator`_, which contains
Python scripts that can be executed by the Python command-line
interpreter or imported into a Python notebook for interactive execution.


.. [1] The dollar sign is the end of the command prompt on a Mac.  If
       you're on Windows, this is usually the right angle bracket (>).
       No matter the symbol, you don't need to type it (or anything to
       its left, which shows the current working directory) at the
       command line before you enter a command; the prompt symbol and
       preceding characters should already be there.


.. _`quant econ`:
   http://quant-econ.net/py/learning_python.html

.. _`Git setup`:
   https://help.github.com/articles/set-up-git/

.. _`Fork`:
   https://help.github.com/articles/github-glossary/#fork

.. _`password setup`:
   https://help.github.com/articles/caching-your-github-password-in-git/

.. _`Tax-Calculator's GitHub page`:
   https://github.com/PSLmodels/Tax-Calculator

.. _`repository`:
   https://help.github.com/articles/github-glossary/#repository

.. _`push`:
   https://help.github.com/articles/github-glossary/#push

.. _`pull`:
   https://help.github.com/articles/github-glossary/#pull

.. _`Github Flow`:
   https://guides.github.com/introduction/flow/

.. _`Anaconda`:
   https://www.anaconda.com/download/

.. _`remote`:
   https://help.github.com/articles/github-glossary/#remote

.. _`testing documentation`:
   https://github.com/PSLmodels/Tax-Calculator/blob/master/TESTING.md

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

.. _`Cookbook of Tested Recipes for Python Programming with Tax-Calculator`:
   https://github.com/PSLmodels/Tax-Calculator/blob/master/docs/cookbook.html

.. _`detailed pull-request workflow`:
   https://github.com/PSLmodels/Tax-Calculator/blob/master/WORKFLOW.md#tax-calculator-pull-request-workflow
