Releasing Tax-Caclculator Packages
==================================

The following outlines the process for releasing a new `taxcalc` package.

In the top-level Tax-Calculator directory, do the following:

```
--> run `git switch master`  [to get on master branch]

--> run `./gitsync`  [to ensure master is up-to-date with GitHub version]

--> run `make clean`  [to remove any local taxcalc package]

--> run `git checkout -b X-Y-Z`  [to create X-Y-Z (e.g., `4-4-1`) branch]

--> on branch X-Y-Z, edit docs/about/releases.md to finalize X.Y.Z info

--> specify release X.Y.Z in setup.py, taxcalc/__init__.py, docs/index.md

--> run `python update_pcl.py`  [to update policy_current_law.json if needed]

--> run `python ppp.py`  [to update policy_current_law.json if needed]

--> run `python extend_tcja.py > ext.json`  [to update reforms/ext.json]

--> run `make cstest`  [to confirm project coding style is being followed]

--> run `make pytest-all`  [or `pytest -m pre_release -n4` in taxcalc subdir]

--> run `make tctest-jit`  [to make sure JIT decorators are not hiding bugs]

--> commit X-Y-Z branch and push to origin

--> open new GitHub pull request using your X-Y-Z branch
```

Then ask [@jdebacker](https://github.com/jdebacker/) to review and
merge the pull request and create the package.


### Notes on creating package for distribution

```
--> merge X-Y-Z branch into master branch on GitHub

--> on local master branch, ./gitsync

--> create release X.Y.Z on GitHub using master branch

--> create new package on Conda-Forge for release X.Y.Z

--> open a PR to github.com/conda-forge/taxcalc-feedstock where
    you change the `recipe/meta.yaml` file by updating:
    (1) the version number to X.Y.Z and
    (2) the checksum to reflect the checksum for the
        tarball for release X.Y.Z in the Tax-Calculator GitHub repo
```
