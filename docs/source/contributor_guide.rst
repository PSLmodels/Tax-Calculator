Contribute to the Tax Calculator 
========================

Brief overview? 

For a fast paced introduction to the Python programming language, `quant econ`_ is a good starting place for economists who are new to the language. 

Setup Python
-------------
1. Download and install the Anaconda distribution of Python from `Continuum Analytics`_

Setup Git
----------

1. Create a github_ user account
2. Install git on your local machine by following steps 1-4 on `git setup`_
3. Tell Git to remember your Github password by following steps 1-4 on `password setup`_ 
4. Create your own remote version of OSPC's tax calculator by clicking "Fork" in the upper right hand corner of the `Tax Calculator's github page`_

..	Notes:: In this step, you are copying OSPC's code repository as your own remote repository (your fork) on the Github server. A repository (Repo) is a workspace where git remembers all different versions of one project, including both past versions and current working progress. By staying on your own fork, you are able to work parallel with other members in the team, who have their own forks as well, without interrupting the functionality of the main repo. The changes you made on your fork won't be merged into the main repo until you make a request (pull request) to do so.

5. From your command line or terminal, navigate to the directory on your computer where you would like the repo to live and create a local copy of your tax calculator fork by entering:

	.. code-block:: python

   		>>> git clone https://github.com/[github-username]/tax-calculator.git
..

		Notes: Usually there are three repos involved in this particular git workflow, OSPC repo, your fork, and your local repo. In this step, you are creating a local repo by copying (clone) your own remote repo on the Github server onto your local machine. It's convenient for you to make changes in your local repo first and then push it your own remote repo. Notice that Git doesn't know what changes you have made and saved in your local repo until you commit them.

6. Make it easier to *push* your local work to others and *pull* others' work to your local machine by adding remote repositories by entering on the command line:

	.. code-block:: python

   		>>> git remote add origin https://github.com/[github-username]/tax-calculator.git
   		>>> git remote add upstream https://github.com/opensourcepolicycenter/tax-calculator.git
..

		Notes: Here you are telling git to remember your own remote repo as 'origin', and the OSPC main repo as 'upstream'. Notice that you have write access to origin but not upstream, so you should always be able to *push* local changes to origin but never to upstream. In order to stay in sync with the progress on upstream, you will need to *pull* changes from upstream. A *pull* is a combination of *fetch* the latest version of OSPC repo and merge the changes if any. All of this described below.

Workflow
--------

The following describes a basic workflow for the Tax Calculator package. Other workflows may be neccesary in some situations, in which case other contributors will help you. 

1. Before you edit the calculator locally, make sure you have the latest version:
	
	* Download content from the main OSPC tax-calculator repository by entering on the command line from your working director:

	.. code-block:: python 
	
		>>> git fetch upstream
	
	
	* Repositories can have several paths, or "branches", of development happening simultaneously. Switch to the branch where you would like to begin your work, most likely this will be the "master" branch. 

	.. code-block:: python
	
		>>> git checkout master 

	
	* Combine the latest changes from the main OSPC  tax-calculator repository with your local changes. 

	.. code-block:: python
	
		>>> git merge upstream/master
..

		Notes: Different versions of the code are stored on different branches of one repo. Here we fetched all branches in upstream, and merge one upstream branch of your choice with a local branch of your choice. In this case, you will update your local master branch with OSPC master branch. This step does not update your remote repository.

2. Create a new branch on your local machine to make your desired changes.

	.. code-block:: python 

		>>> git checkout -b [new-branch-name]

3. MAKE LOCAL CHANGES! 


4. As you go, frequently test that your changes have not introduced bugs and/or degraded the accuracy of the tax calculator by running the following from inside ..\tax-calculator\taxcalc

	.. code-block:: python

		>>> py.test

5. As you go, if the tests are passing, commit your changes by entering

	.. code-block:: python

		>>> git add .
		>>> git commit -m '[description-of-your-commit]'
..
	
		Notes: As mentioned before, saving your files in the working directory is not equal to making changes in your local repo. You need to tell Git to what changes are important and ask Git to track these changes. In this step, by 'git add [filename]', you are telling Git which changes are important. You should not add large files to the repository, because all other contributors will have to download these files every time they fetch upstream. After 'git commit', your local repo will know the differences between your current commit and your last commit. One advantage of making commits often is that you can always revert to a previous commit if necessary.

6. When you are ready for others to review your code, make your final commit, and push your branch to your remote fork. 

	.. code-block:: python

		>>> git push origin [new-branch-name]
..

		Notes: Your local changes would be pushed from your local repo to your remote repo. So others in the team will be able to see your changes and pull the changes to their fork if necessary.

7. Ask others to review your changes by directing them to github.com/[Github Username]/Tax-Calculator/[new-branch-name]. 

8. Wait for feedback and instructions on how to proceed. 


	
Example Code
------------

For example usage, you can view our sample notebooks:

* `10 Minues To TaxCalc`_
* `Behavior Example`_ 


.. _`quant econ`: http://quant-econ.net/py/learning_python.html
.. _`github`: http://www.github.com
.. _`git setup`: https://help.github.com/articles/set-up-git/
.. _`password setup`: https://help.github.com/articles/caching-your-github-password-in-git/
.. _`Tax Calculator's github page`: https://github.com/OpenSourcePolicyCenter/Tax-Calculator
.. _`Github Flow`: https://guides.github.com/introduction/flow/    
.. _`10 Minues To TaxCalc`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/notebooks/10_Minutes_to_Taxcalc.ipynb
.. _`Behavior Example`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/notebooks/Behavioral_example.ipynb
.. _`Continuum Analytics`: continuum.io/downloads


