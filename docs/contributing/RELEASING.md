RELEASING TAX-CALCULATOR CONDA PACKAGES
=======================================

```
====> CREATE NEW TAXCALC PACKAGES <====

--> on branch X-Y-Z, edit RELEASES.md to finalize X.Y.Z info

--> specify release X.Y.Z in setup.py and taxcalc/__init__.py

--> merge master branch into X-Y-Z branch

--> run `make tctest-jit`  [to make sure JIT decorators are not hiding bugs]

--> run `make pytest-all`  [or `pytest -m pre_release -n4` in taxcalc subdir]

--> run `make package`  [to make local taxcalc package available]

--> cd taxcalc/validation ; ./tests.sh ; .fix. ; cd ../..

--> specify release X.Y.Z in index.md

--> cd .. ; make clean  [to remove taxcalc package]

--> commit X-Y-Z branch and push to origin

--> merge X-Y-Z branch into master branch on GitHub

--> on local master branch, ./gitsync

--> create release X.Y.Z on GitHub using master branch

--> run `pbrelease Tax-Calculator taxcalc X.Y.Z` [to build and upload packages]

====> ADD NEW DEPENDENCY OR UPDATE MINIMUM REQUIRED VERSION <====

--> add or update `run` list in `requirements` section of `conda.recipe/meta.yaml`

--> add or update package in `environment.yaml`
    (this may have already been done in the PR that added or updated the
     dependency.)

--> update `dev_pkgs` list in `test_4package.py:test_for_consistency` and make sure
    the updated test passes

====> CREATE NEW BEHRESP PACKAGES (if necessary) <====

--> create Behavioral-Responses packages

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