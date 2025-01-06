Contributor guide
=================

The purpose of this guide is to get you to the point where you can
make improvements to Tax-Calculator and share them with the rest
of the development team as a GitHub pull request.
This document assumes that you have read {doc}`../usage/starting` and
{doc}`../recipes/index`.

If the objective of your Tax-Calculator improvement is to add the
ability to analyze a tax reform that cannot be analyzed using existing
policy parameters, then you need to follow the steps described in this
paragraph **before** preparing a pull request.
(a) Modify {doc}`../recipes/recipe06` to
analyze the kind of tax reform you want to add to the list of reforms
that can be analyzed parametricly by Tax-Calculator.
(b) Raise a Tax-Calculator issue in which you show your modified
recipe 6 that simulates the reform and provide some numerical results
that illustrate the effects of the reform.
In the course of the conversation about your issue, you may be asked
to prepare a pull request that would allow this reform to be analyzed
using new policy parameters and associated logic.  If so, follow the
directions below when preparing that pull request.

We keep track of Tax-Calculator source code using the [Git version
control system and
GitHub](https://www.w3schools.com/git/git_intro.asp?remote=github).
We don't expect you to be an expert Git user.  Where possible, we link
to Git and GitHub documentation to help with some of the unfamiliar
terminology (often from this [glossary of GitHub
terms](https://help.github.com/articles/github-glossary/)).  Following
the next steps will get you up and running and contributing to
Tax-Calculator even if you've never used anything like Git and GitHub.
But if you are unfamiliar with the concept of version control, you
should read an introductory tutorial online.  A good tutorial can be
found
[here](https://homes.cs.washington.edu/~mernst/advice/version-control.html).

If you have already completed the following Setup Python and Setup Git
sections, please skip to [Workflow](#workflow).


## Setup Python

Follow the [getting started
instructions](https://taxcalc.pslmodels.org/usage/starting.html).

If you are new to or have limited experience with Python, you should
read some introductory tutorials available online.  One such
interactive tutorial is the [W3 Schools' Python
Introduction](https://www.w3schools.com/python/python_intro.asp).


## Setup Git

1. Create a free GitHub user account from the [GitHub home
page](https://github.com).

2. Install Git on your local computer by following the steps
[here](https://help.github.com/articles/set-up-git/).

3. Tell Git to remember your GitHub password by following the steps
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
   git clone https://github.com/[github-username]/Tax-Calculator.git
   ```

7. From your command line or terminal, navigate to your local
   Tax-Calculator directory.

8. Make it easier to
   [push](https://help.github.com/articles/github-glossary/#push) your
   local work to others and
   [pull](https://help.github.com/articles/github-glossary/#pull)
   others' work to your local computer by entering at the command
   line:
   ```
   cd Tax-Calculator
   git remote add upstream https://github.com/PSLmodels/Tax-Calculator.git
   ```

9. Create a conda environment with all of the necessary packages to
   execute Tax-Calculator source code in the Tax-Calculator directory:
   ```
   conda create --name taxcalc-dev
   ```

10. The prior command will create a conda environment called `taxcalc-dev`.
    Activate this environment as follows:
    ```
    conda activate taxcalc-dev
    ```
    Important Note: never conda install the taxcalc package in the
    taxcalc-dev environment because the taxcalc source code and the
    installed package may be in conflict.

11. To check that everything is working properly, run the following at
    the command line in the Tax-Calculator directory:
    ```
    cd taxcalc
    pytest -m "not requires_pufcsv and not pre_release" -n4
    ```
    If you do have a copy of the `puf.csv` file used by Tax-Calculator,
    then on the second line above omit the `not requires_pufcsv and`
    expression so as to execute `pytest -m "not pre_release" -n4`.

    If all the tests pass, you're good to go. If they don't pass, enter
    the following updates at the command line and then try running the
    tests again:
    ```
    conda update conda
    conda env update
    ```
    
    For more detail on Tax-Calculator testing procedures, read {doc}`testing`.
    If the tests still don't pass, please contact us.

If you've made it this far, you've successfully made a remote copy (a
fork) of central Tax-Calculator repo. That remote repo is hosted on
GitHub.  You've also created a local repo --- a
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


## Workflow

The following text describes a typical workflow for changing
Tax-Calculator.  Different workflows may be necessary in some
situations, in which case other contributors are here to help.

1. Before you edit the Tax-Calculator source code on your computer,
   make sure you have the latest version of the central Tax-Calculator
   repository by executing the **four** Git commands listed in
   substeps `a-d` (or alternatively by executing just substeps `a` and
   `e`):

   a. Tell Git to switch to the master branch in your local repo.
      Navigate to your local Tax-Calculator directory and enter the
      following text at the command line:
      ```
      git switch master
      ```

   b. Download all of the content from the central Tax-Calculator repo
      using the Git
      [fetch](https://help.github.com/articles/github-glossary/#fetch)
      command:
      ```
      git fetch upstream
      ```

   c. Update your local master branch to contain the latest content of
      the central master branch using the Git
      [merge](https://help.github.com/articles/github-glossary/#merge)
      command. This step ensures that you are working with the latest
      version of the Tax-Calculator on your computer:
      ```
      git merge upstream/master
      ```

   d. Push the updated master branch in your local repo to your GitHub
      repo using the Git
      [push](https://help.github.com/articles/github-glossary/#push)
      command:
      ```
      git push origin master
      ```

   e. As an alternative to executing substeps `a-d`, you can
      simply execute substeps `a` and `e`.  If you are working on Mac
      or Linux, execute these commands in the Tax-Calculator directory:
      ```
      git switch master
      ./gitsync
      ```
      If you are working on Windows, execute these commands in the
      Tax-Calculator directory:
      ```
      git switch master
      gitsync
      ```

2. Create a new
   [branch](https://help.github.com/articles/github-glossary/#branch)
   on your local computer in the Tax-Calculator directory. Think of
   your branches as a way to organize your projects. If you want to
   work on this documentation, for example, create a separate branch
   for that work. If you want to change the maximum child care tax
   credit in the Tax-Calculator, create a different branch for that
   project:
   ```
   git checkout -b [new-branch-name]
   ```

3. If your changes involve creating a new tax policy parameter, be
   sure to read about the Tax-Calculator {doc}`param_naming`.

4. As you make changes, frequently check that your changes do not
   violate Tax-Calculator coding style, introduce bugs, or degrade the
   accuracy of Tax-Calculator.  To do this, run the following commands
   from the command line in the Tax-Calculator directory:
   ```
   make cstest
   make pytest-cps
   ```
   Consult {doc}`testing` for more details.

   If the tests do not pass, try to fix the problem by using the
   information provided by the error message.  If this isn't possible
   or doesn't work, we are here to help.

5. Now you're ready to
   [commit](https://help.github.com/articles/github-glossary/#commit)
   your changes to your local repo using the commands described in
   this step. You need to use the Git `add` command only if your
   branch creates one or more new files that you want to include in
   the repository.  Use the Git `status` command to see which files
   you have edited and which files are new:
   ```
   git status
   ```
   If adding a new file, use the Git `add` command:
   ```
   git add [new-filename]
   ```
   As a rule, do not add large files. If you'd like to add a file that is
   larger than 25 MB, please contact the other contributors and ask how to
   proceed.

   The actual commit of code changes (and possibly new files) to your
   local repository is accomplished with this sort of command:
   ```
   git commit -a -m "[description-of-your-commit]"
   ```
   where you should replace the bracketed text inside the quotation
   marks with a short (no more than about 70 characters) description
   of your changes.

   **Tip**: Committing often is a good idea as Git keeps a record of
   your changes. This means that you can always revert to a previous
   version of your work if you need to.

6. Periodically, make sure that the branch you created in step 2
   is in sync with the changes other contributors are making to
   the central master branch by fetching upstream and merging
   upstream/master into your branch:
   ```
   git fetch upstream
   git merge upstream/master
   ```
   You may need to resolve conflicts that arise when another
   contributor changed the same section of code that you are
   changing.  Feel free to ask other contributors for guidance
   if this happens to you.  If you do need to fix a merge
   conflict, run the tests (step 4) again after fixing.

7. When you are ready for other team members to review your code, make
   your final commit and push your local branch to your remote repo:
   ```
   git push origin [new-branch-name]
   ```

8. From the [central GitHub Tax-Calculator
   page](https://github.com/PSLmodels/Tax-Calculator), open a [pull
   request](https://help.github.com/articles/creating-a-pull-request/#creating-the-pull-request)
   containing the changes in your local branch.

9. When you open a GitHub pull request, a code coverage report will be
   automatically generated.  If your branch adds new code that is not
   tested, the code coverage percent will decline and the number of
   untested statements ("misses" in the report) will increase.  If
   this happens, you need to add to your branch one or more tests of
   your newly added code.  Add tests so that the number of untested
   statements is the same as it is on the master branch.

**IMPORTANT NOTE:** you can always make more changes on your local
branch, commit them (step 6), and push them to your remote repo (step
7), and these changes will be automatically incorporated into your
pull request.

You should now read the more detailed {doc}`pr_workflow` document.

This is the end of the Contributor Guide document.
