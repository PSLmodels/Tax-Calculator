**SETUP**

1. Make a user account at [github.com](www.github.com).

2. Install git on your local machine by following steps 1-4 at [help.github.com/articles/set-up-git/](https://help.github.com/articles/set-up-git/)

3. Tell Git to remember your Github password by following steps 1-4 at [help.github.com/articles/caching-your-github-password-in-git/](https://help.github.com/articles/caching-your-github-password-in-git/)

4. Create your own remote version of OSPC's tax calculator by clicking "Fork" in the upper right hand corner of [www.github.com/OpenSourcePolicyCenter/Tax-Calculator](https://github.com/OpenSourcePolicyCenter/Tax-Calculator). 

5.  From your command line or terminal, navigate to the directory on your computer where you would like the repo to live and create a local copy of your tax calculator fork by entering,

	`git clone https://github.com/[github-username]/tax-calculator.git`

6. Make it easier to *push* your local work to others and *pull* others' work to your local machine by adding remote repositories by entering on the command line, 

	`git remote add origin https://github.com/[github-username]/tax-calculator.git`
	`git remote add upstream https://github.com/opensourcepolicycenter/tax-calculator.git`

**CONTRIBUTING WORKFLOW**

The following describes a basic workflow. Other workflows may be neccesary in some situations, in which case other contributors will help you. 
	
1. Before you edit the calculator locally, make sure you have the latest version:
	1. Download content from the main OSPC tax-calculator repository by entering on the command line from your working director:
	
		`git fetch upstream`
		
	2. Repositories can have several paths, or "branches", of development happening simultaneously. Switch to the branch where you would like to begin your work, most likely this will be the "master" branch. 
	
		`git checkout master` 
	
	3. Combine the latest changes from the main OSPC  tax-calculator repository with your local changes. 
	
		`git merge upstream/master`
		
2. Create a new branch on your local machine to make your desired changes. 
		
		`git checkout -b [new-branch-name]`
		
3. MAKE LOCAL CHANGES! 

4. As you go, frequently test that your changes have not introduced bugs and/or degraded the accuracy of the tax calculator by running

	`py.test` from inside ...\tax-calculator\taxcalc

5. As you go, if the tests are passing, commit your changes by entering:

	`git add .`
	`git commit -m '[description-of-your-commit]'`
	
6. When you are ready for others to review your code, make your final commit, and push your branch to your remote fork. 

	`git push origin [new-branch-name]`
	
7. Ask others to review your changes by directing them to github.com/[Github Username]/Tax-Calculator/[new-branch-name]. 

8. Wait for feedback and instructions on how to proceed. 



