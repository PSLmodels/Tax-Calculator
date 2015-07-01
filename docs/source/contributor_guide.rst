Contribute to the Tax Calculator 
================================

The purpose of this guide is to get you to the point where you can make improvements to the Tax Calculator and share them with the rest of the team. 

We keep track of our Tax Calculator code using `Git`_, but we don’t expect you to be an expert Git user. Where possible, we link to Git and GitHub documentation to help with some of the unfamiliar terminology. Following the next steps will get you up and running and contributing to our model even if you've never used anything like Git.

If you’ve already completed the Setup Python and Setup Git sections, please skip to `Workflow`_.

Setup Python
-------------

Our Tax Calculator is written in the Python programming language. Download and install the Anaconda distribution of Python from `Continuum Analytics`_. Even if you already have Python installed, we recommend using that distribution because it contains all the additional Python packages that we use in the project.

Setup Git
----------

1. Create a `GitHub`_ user account.

2. Install Git on your local machine by following steps 1-4 on `Git setup`_.

3. Tell Git to remember your GitHub password by following steps 1-4 on `password setup`_. 

4. Sign in to GitHub and create your own `remote`_ `repository`_ (repo) of OSPC's tax calculator by clicking `Fork`_ in the upper right corner of the `Tax Calculator's GitHub page`_. Select your username when asked, “Where should we fork this repository?”

5. From your command line, navigate to the directory on your computer where you would like your local repo to live.

6. Create a local repo by entering at the command line the text after the $. [1]_ This step creates a folder called tax-calculator in the directory that you specified in step 5.

	.. code-block:: python

   		$ git clone https://github.com/[github-username]/tax-calculator.git

7. From your command line or terminal, navigate to your local tax-calculator directory.

8. Make it easier to `push`_ your local work to others and `pull`_ others' work to your local machine by entering at the command line:

	.. code-block:: python

   		$ git remote add upstream https://github.com/opensourcepolicycenter/tax-calculator.git
..

9. Create a conda environment with all of the necessary packages to run the source:

	.. code-block:: python

   		$ cd Tax-Calculator; conda env create
..


10. This will create a conda environment called "tax". Activate the environment:

	.. code-block:: python

   		$ source activate taxcalc-dev
..


11. To check that everything is working properly, navigate to tax-calculator/ and run the following at the command line.

	.. code-block:: python

		$ py.test
..

   If the tests pass, you’re good to go. If they don’t pass, enter the following updates at the command line and then try running py.test again. If the tests still don’t pass, please contact us.

	.. code-block:: python

		$ conda update conda
		$ conda update numba
		$ conda update pandas
..

If you’ve made it here, you’ve successfully made a remote copy (a fork) of OSPC’s repo. That remote repo is hosted on GitHub.com. You’ve also created a local repo (a `clone`_) that lives on your machine and only you can see; you will make your changes to the Tax Calculator by editing the files in the tax-calculator directory on your machine and then submitting those changes to your local repo. As a new contributor, you will push your changes from your local repo to your remote repo when you’re ready to share that work with the team.

Don’t be alarmed if the above paragraph is confusing. The following section introduces some standard Git practices and guides you through the contribution process. 

.. _Workflow
Workflow
--------

The following text describes a typical workflow for the Tax Calculator package. Different workflows may be necessary in some situations, in which case other contributors are here to help. 

1. Before you edit the calculator on your machine, make sure you have the latest version of the OSPC Tax Calculator:

	* Download all of the content from the main OSPC Tax Calculator repo. Navigate to your local tax-calculator directory and enter the following text at the command line.

	.. code-block:: python 
	
		$ git fetch upstream

	
	* Tell Git to switch to the master branch in your local repo.

	.. code-block:: python
	
		$ git checkout master 

	
	* Update your local master branch to contain the latest content of the OSPC master branch using `merge`_. This step ensures that you are working with the latest version of the Tax Calculator.

	.. code-block:: python
	
		$ git merge upstream/master
..

2. Create a new `branch`_ on your local machine. Think of your branches as a way to organize your projects. If you want to work on this documentation, for example, create a separate branch for that work. If you want to change the maximum child care tax credit in the Tax Calculator, create a different branch for that project. 

	.. code-block:: python 

		$ git checkout -b [new-branch-name]

3. See :doc:`Making changes in your local tax-calculator directory </make_local_change>` for examples showing you how to do just that.

..
4. As you go, frequently check that your changes do not introduce bugs and/or degrade the accuracy of the Tax Calculator. To do this, run the following at the command line from inside /tax-calculator/taxcalc. If the tests do not pass, try to fix the issue by using the information provided by the error message. If this isn’t possible or doesn’t work, we are here to help.

	.. code-block:: python

		$ py.test

5. Now you’re ready to `commit`_ your changes to your local repo using the code below. The first line of code tells Git to track a file. Use “git status” to find all the files you’ve edited, and “git add” each of the files that you’d like Git to track. As a rule, do not add large files. If you’d like to add a file that is > 25 MB, please contact the other contributors and ask how to proceed. The second line of code commits your changes to your local repo and allows you to create a commit message; this should be a short description of your changes.

   *Tip*: Committing often is a good idea as Git keeps a record of your commits. This means that you can always revert to a previous version of your work if you need to.

	.. code-block:: python

		$ git add [filename]
		$ git commit -m '[description-of-your-commit]'
..

6. When you’re ready for other team members to review your code, make your final commit and push your local branch to your remote repo (this repo is also called the origin). 

	.. code-block:: python

		$ git push origin [new-branch-name]
..

7. Ask other team members to review your changes by directing them to: github.com/[Github Username]/Tax-Calculator/[new-branch-name]. 

..
8. If this is your first time, wait for feedback and instructions on how to proceed. Most likely, the other contributors will ask you to `fetch`_ and merge new changes from `upstream`_/master and then open a `pull request`_.  
	
Example Code
------------

For example usage, you can view our sample notebooks:

* `10 Minutes To TaxCalc`_

.. [1] The dollar sign is the end of the command prompt on a Mac. If you’re on Windows, this is usually the right angle bracket (>). No matter the symbol, you don’t need to type it at the command line before you enter a command - the symbol should already be there.

.. _`Git`: https://help.github.com/articles/github-glossary/#git
.. _`quant econ`: http://quant-econ.net/py/learning_python.html
.. _`GitHub`: http://www.github.com
.. _`Git setup`: https://help.github.com/articles/set-up-git/
.. _`Fork`: https://help.github.com/articles/github-glossary/#fork
.. _`password setup`: https://help.github.com/articles/caching-your-github-password-in-git/
.. _`Tax Calculator's GitHub page`: https://github.com/OpenSourcePolicyCenter/Tax-Calculator
.. _`repository`: https://help.github.com/articles/github-glossary/#repository
.. _`push`: https://help.github.com/articles/github-glossary/#push
.. _`pull`: https://help.github.com/articles/github-glossary/#pull
.. _`Github Flow`: https://guides.github.com/introduction/flow/    
.. _`10 Minutes To TaxCalc`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/notebooks/10_Minutes_to_Taxcalc.ipynb
.. _`Behavior Example`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/notebooks/Behavioral_example.ipynb
.. _`Continuum Analytics`: http://www.continuum.io/downloads
.. _`remote`: https://help.github.com/articles/github-glossary/#remote
.. _`clone`: https://help.github.com/articles/github-glossary/#clone
.. _`branch`: https://help.github.com/articles/github-glossary/#branch
.. _`merge`: https://help.github.com/articles/github-glossary/#merge
.. _`commit`: https://help.github.com/articles/github-glossary/#commit
.. _`fetch`: https://help.github.com/articles/github-glossary/#fetch
.. _`upstream`: https://help.github.com/articles/github-glossary/#upstream
.. _`pull request`: https://help.github.com/articles/github-glossary/#pull-request




