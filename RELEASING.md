RELEASING TAX-CALCULATOR CONDA PACKAGES
=======================================

```
--> on branch X-Y-Z, edit RELEASES.md and CHANGES.md to finalize X.Y.Z info

--> merge master branch into X-Y-Z branch

--> edit "version = 'X.Y.Z'" in read-the-docs/source/conf.py

--> run `make tctest-jit`  [to make sure JIT decorators are not hiding bugs]

--> run `make pytest-all`  [or `pytest -m pre_release -n4` in taxcalc]

--> run `make package`  [to make taxcalc package available in docs]

--> run `conda install -c PSLmodels behresp --yes`  [to make behresp available]

--> cd docs/cookbook ; python test_recipes.py ; .fix. ; python make_cookbook.py

--> cd .. ; ./index_results.sh ; .fix. ; python make_index.py

--> cd .. ; make clean  [to remove taxcalc and behresp packages]

--> commit X-Y-Z branch and push to origin

--> merge X-Y-Z branch into master branch on GitHub

--> on local master branch, ./gitsync

--> create release X.Y.Z on GitHub using master branch

--> `pbrelease Tax-Calculator taxcalc X.Y.Z --also37` [to build/upload packages]

--> email policybrain-modelers list about the new release and packages
```

LATER: create new X-Y-Z branch that will hold RELEASES.md info for next release



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
