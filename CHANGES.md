TAX-CALCULATOR CHANGE HISTORY
=============================


2018-11-22 Release 0.23.2
-------------------------
**New Features**
- Refactor `create_diagnostic_table` utility function to work better when using the Behavioral-Repsonses `behresp` package
  [[#2126](https://github.com/open-source-economics/Tax-Calculator/pull/2126)
  by Martin Holmer responding to question from Ernie Tedeschi]


2018-11-20 Release 0.23.1
-------------------------
**Bug Fixes**
- Replace buggy Parameters.default_data() with Policy.metadata() method
  [[#2119](https://github.com/open-source-economics/Tax-Calculator/pull/2119)
  by Martin Holmer with bug reported by Hank Doupe]
- Add ability to pass Pandas DataFrame as the `adjust_ratios` argument to Records class constructor
  [[#2121](https://github.com/open-source-economics/Tax-Calculator/pull/2121)
  by Martin Holmer with bug reported by Anderson Frailey]
- Revise Cookbook recipe 1 to show easier way to access reform files on website
  [[#2122](https://github.com/open-source-economics/Tax-Calculator/pull/2122)
  by Martin Holmer]


2018-11-13 Release 0.23.0
-------------------------
**API Changes**
- Remove confusing `filer` variable from list of usable input variables
  [[#2102](https://github.com/open-source-economics/Tax-Calculator/pull/2102)
  by Martin Holmer]
- Remove useless `start_year` and `num_years` arguments of constructor for the Policy, Consumption, and GrowDiff classes
  [[#2103](https://github.com/open-source-economics/Tax-Calculator/pull/2103)
  by Martin Holmer]
- Add deprecated warning to Behavior class constructor and documentation because Behavior class will be removed from Tax-Calculator in a future release
  [[#2105](https://github.com/open-source-economics/Tax-Calculator/pull/2105)
  by Martin Holmer]
- Remove `versioneer.py` and `taxcalc/_version.py` and related code now that Package-Builder is handling version specification
  [[#2111](https://github.com/open-source-economics/Tax-Calculator/pull/2111)
  by Martin Holmer]
**New Features**
- Revise Cookbook recipe 2 to show use of new Behavioral-Responses behresp package as alternative to deprecated Behavior class
  [[#2107](https://github.com/open-source-economics/Tax-Calculator/pull/2107)
  by Martin Holmer]


2018-10-26 Release 0.22.2
-------------------------
**New Features**
- Add _EITC_basic_frac policy parameter so that an Earned and Basic Income Tax Credit (EBITC) reform can be analyzed
  [[#2094](https://github.com/open-source-economics/Tax-Calculator/pull/2094)
  by Martin Holmer]


2018-10-25 Release 0.22.1
-------------------------
*New Features**
- Add Records.read_cps_data static method to make it easier to test other models in the Policy Simulation Library collection of USA tax models
  [[#2090](https://github.com/open-source-economics/Tax-Calculator/pull/2090)
  by Martin Holmer]


2018-10-24 Release 0.22.0
-------------------------
**API Changes**
- Refactor `tbi` functions so that other models in the Policy Simulation Library (PSL) collection of USA tax models can easily produce the tables expected by TaxBrain
  [[#2087](https://github.com/open-source-economics/Tax-Calculator/pull/2087)
  by Martin Holmer]
**New Features**
- Add more detailed pull-request work-flow documentation
  [[#2071](https://github.com/open-source-economics/Tax-Calculator/pull/2071)
  by Martin Holmer]
- Add Travis-CI-build badge to `README.md` file
  [[#2078](https://github.com/open-source-economics/Tax-Calculator/pull/2078)
  by Philipp Kats]
- Add ability to read online JSON reform/assumption files located at URLs beginning with `http`
  [[#2079](https://github.com/open-source-economics/Tax-Calculator/pull/2079)
  by Anderson Frailey]
- Add Python-version and code-coverage badges to `README.md` file
  [[#2080](https://github.com/open-source-economics/Tax-Calculator/pull/2080)
  by Martin Holmer]
**Bug Fixes**
- Fix syntax error in `gitpr.bat` Windows batch script
  [[#2084](https://github.com/open-source-economics/Tax-Calculator/pull/2084)
  by Martin Holmer]
- Fix bug in create_difference_table utility function that affected the `ubi` and `benefit_*_total` variables
  [[#2087](https://github.com/open-source-economics/Tax-Calculator/pull/2087)
  by Martin Holmer]


2018-09-11 Release 0.21.0 : first release compatible only with Python 3.6
-------------------------------------------------------------------------
**API Changes**
- Require Python 3.6 to run Tax-Calculator source code or conda package
  [[#2058](https://github.com/open-source-economics/Tax-Calculator/pull/2058)
  by Martin Holmer], which requires new `puf.csv` input file (see [taxdata pull request 283](https://github.com/open-source-economics/taxdata/pull/283) for details) with this information:
  * Byte size: 56415698
  * MD5 checksum: 3f1c7c2b16b6394a9148779db992bed1


2018-09-06 Release 0.20.3 : LAST RELEASE COMPATIBLE WITH PYTHON 2.7
-------------------------------------------------------------------
**New Features**
- Incorporate new PUF input data that include imputed values of itemizeable expenses for non-itemizers
  [[#2052](https://github.com/open-source-economics/Tax-Calculator/pull/2052)
  by Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 55104059
  * MD5 checksum: 9929a03b2d93a628d5057cc17d032e52
- Incorporate new CPS input data that include different `other_ben` values
  [[#2055](https://github.com/open-source-economics/Tax-Calculator/pull/2055)
  by Martin Holmer]
- Incorporate new PUF input data that include imputed values of pension contributions
  [[#2056](https://github.com/open-source-economics/Tax-Calculator/pull/2056)
  by Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 56415698
  * MD5 checksum: a10091a770472254c50f8985d8839162


Before Release 0.20.3
---------------------
See more technical descriptions of releases before 0.20.3 [here](https://github.com/open-source-economics/Tax-Calculator/blob/master/RELEASES.md#2018-08-10-release-0202).
