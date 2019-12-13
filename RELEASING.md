RELEASING TAX-CALCULATOR CONDA PACKAGES
=======================================

```
====> CREATE NEW TAXCALC PACKAGES <====

--> on branch X-Y-Z, edit RELEASES.md and CHANGES.md to finalize X.Y.Z info

--> specify release X.Y.Z in setup.py and taxcalc/__init__.py

--> merge master branch into X-Y-Z branch

--> run `make tctest-jit`  [to make sure JIT decorators are not hiding bugs]

--> run `make pytest-all`  [or `pytest -m pre_release -n4` in taxcalc subdir]

--> run `make package`  [to make local taxcalc package available]

--> cd taxcalc/validation ; ./tests.sh ; .fix. ; cd ../..

--> cd docs ; ./uguide_results.sh ; .fix. ; python make_uguide.py

--> specify release X.Y.Z in index.htmx ; python make_tc_pages.py

--> cd .. ; make clean  [to remove taxcalc package]

--> commit X-Y-Z branch and push to origin

--> merge X-Y-Z branch into master branch on GitHub

--> on local master branch, ./gitsync

--> create release X.Y.Z on GitHub using master branch

--> run `pbrelease Tax-Calculator taxcalc X.Y.Z` [to build and upload packages]

====> CREATE NEW BEHRESP PACKAGES (if necessary) <====

--> create Behavioral-Responses packages

====> CREATE NEW PYTHON COOKBOOK <====

--> run `conda install -c PSLmodels behresp --yes`  [to make behresp available]

--> on new branch X-Y-Z-cookbook

--> cd docs/cookbook ; python test_recipes.py ; .fix. ; python make_cookbook.py

--> merge X-Y-Z-cookbook branch and push to origin

--> merge X-Y-Z-cookbook branch into master branch on GitHub

--> on local master branch, ./gitsync

--> execute `touch docs/index.html`
--> execute `touch docs/uguide.html`
--> execute `touch docs/cookbook.html`

====> NOTIFY OTHER DEVELOPERS <====

--> email policybrain-modelers list about the new release and packages
```


CREATING NEW BRANCH TO FIX BUG IN OLD RELEASE
=============================================

Useful when tip of master branch includes major changes since old release.

EXAMPLE: fix bug in release 1.4.0 and then release 1.4.1

```
$ cd ~/work/PSL/Tax-Calculator

$ git checkout master

$ git checkout  -b 1-4-1  1.4.0

--> fix bug on branch 1-4-1, test, commit bug fix

$ git push upstream 1-4-1

--> create release 1.4.1 using GitHub releases GUI citing branch 1-4-1

--> then in order to merge bug-fix into master branch and future releases
    beginning with 1.5.0, do the following:

$ git checkout master

$ git merge 1-4-1
```
