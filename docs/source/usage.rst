Using the Tax Calculator 
========================

Brief overview? 

For a fast paced introduction to the Python programming language, `quant econ`_ is a good starting place for economists who are new to the language. 

Setup
-------------
1. Create a github_ user account
2. Install git on your local machine by following steps 1-4 on `git setup`_
3. Tell Git to remember your Github password by following steps 1-4 on `password setup`_ 
4. Create your own remote version of OSPC's tax calculator by clicking "Fork" in the upper right hand corner of the `Tax Calculator's github page`_
5. From your command line or terminal, navigate to the directory on your computer where you would like the repo to live and create a local copy of your tax calculator fork by entering:

.. code-block:: python

   >>> git clone https://github.com/[github-username]/tax-calculator.git

6. Make it easier to *push* your local work to others and *pull* others' work to your local machine by adding remote repositories by entering on the command line:

.. code-block:: python

   >>> git remote add origin https://github.com/[github-username]/tax-calculator.git
   >>> git remote add upstream https://github.com/opensourcepolicycenter/tax-calculator.git

Workflow
--------

This is a general overview of the `Github Flow`_.

Following the style above, the following describes a basic workflow for the Tax Calculator package. Other workflows may be neccesary in some situations, in which case other contributors will help you. 

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

6. When you are ready for others to review your code, make your final commit, and push your branch to your remote fork. 

.. code-block:: python

	>>> git push origin [new-branch-name]

7. Ask others to review your changes by directing them to github.com/[Github Username]/Tax-Calculator/[new-branch-name]. 

8. Wait for feedback and instructions on how to proceed. 


	
Example Code
------------

For example usuage, you can view our sample notebooks:

* `10 Minues To TaxCalc`_
* `Behavior Example`_ 


.. _`quant econ`: http://quant-econ.net/py/learning_python.html
.. _github: http://www.github.com
.. _`git setup`: https://help.github.com/articles/set-up-git/
.. _`password setup`: https://help.github.com/articles/caching-your-github-password-in-git/
.. _`Tax Calculator's github page`: https://github.com/OpenSourcePolicyCenter/Tax-Calculator
.. _`Github Flow`: https://guides.github.com/introduction/flow/    
.. _`10 Minues To TaxCalc`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/10_Minutes_to_Taxcalc.ipynb
.. _`Behavior Example`: http://nbviewer.ipython.org/github/OpenSourcePolicyCenter/Tax-Calculator/blob/master/docs/Behavioral_example.ipynb


