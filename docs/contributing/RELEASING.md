Releasing Tax-Caclculator Packages
==================================

The following outlines the process to release Tax-Calculator Packages
on Conda-Forge and creating a new branch to fix a bug in a previous
release.

Create new `taxcalc` packages
=============================
```
--> merge master branch into X-Y-Z branch

--> on branch X-Y-Z, edit docs/about/releases.md to finalize X.Y.Z info

--> specify release X.Y.Z in setup.py and taxcalc/__init__.py and docs/index.md

--> run `python update_pcl.py`  [to update policy_current_law.json if needed]

--> run `python ppp.py`  [to update policy_current_law.json if needed]

--> run `python extend_tcja.py > ext.json`  [to update reforms/ext.json]

--> run `make tctest-jit`  [to make sure JIT decorators are not hiding bugs]

--> run `make pytest-all`  [or `pytest -m pre_release -n4` in taxcalc subdir]

--> run `make package`  [to make local taxcalc package available]

--> cd taxcalc/validation ; ./tests_35.sh ; .fix. ; cd ../..

--> make clean  [to remove taxcalc package]

--> commit X-Y-Z branch and push to origin

--> merge X-Y-Z branch into master branch on GitHub

--> on local master branch, ./gitsync

--> create release X.Y.Z on GitHub using master branch

--> Create new package on Conda-Forge for release X.Y.Z

--> open a PR to github.com/conda-forge/taxcalc-feedstock where you change the `recipe/meta.yaml` file by updating (1) the version number to X.Y.Z and (2) the checksum to reflect the checksum for the tarball for release X.Y.Z in the Tax-Calculator GitHub repo

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

--> email Tax-Calculator user list about the new release and packages
```


Creating a new branch to fix a bug in an old release
====================================================

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