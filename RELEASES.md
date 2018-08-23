TAX-CALCULATOR RELEASE HISTORY
==============================
Go [here](https://github.com/open-source-economics/Tax-Calculator/pulls?q=is%3Apr+is%3Aclosed)
for a complete commit history.


2018-08-10 Release 0.20.2
-------------------------
(last merged pull request is
[#2048](https://github.com/open-source-economics/Tax-Calculator/pull/2048))

**API Changes**
- None

**New Features**
- Add Calculator.n65() method that uses new `elderly_dependents` input variable
  [[#2029](https://github.com/open-source-economics/Tax-Calculator/pull/2029)
  by Martin Holmer at request of Max Ghenis]
- Incorporate updated CPS and PUF input data
  [[#2032](https://github.com/open-source-economics/Tax-Calculator/pull/2032)
  by Martin Holmer and Anderson Frailey]
- Add policy parameters that allow many changes in tax treatment of charitable giving
  [[#2037](https://github.com/open-source-economics/Tax-Calculator/pull/2037)
  by Derrick Choe]
- Extrapolate CPS benefit variables in the same way as other dollar variables are extrapolated to future years
  [[#2041](https://github.com/open-source-economics/Tax-Calculator/pull/2041)
  by Martin Holmer]
- Incorporate most recent PUF input data fixing problem mentioned in [#2032](https://github.com/open-source-economics/Tax-Calculator/pull/2032)
  [[#2047](https://github.com/open-source-economics/Tax-Calculator/pull/2047)
  by Martin Holmer and Anderson Frailey], which requires new `puf.csv`
  input file with this information:
  * Byte size: 54341028
  * MD5 checksum: b64b90884406dfcff85f2ac9ba79f9bf
- Incorporate most recent CPS input data containing actuarial value of health insurance benefits
  [[#2048](https://github.com/open-source-economics/Tax-Calculator/pull/2048)
  by Martin Holmer and Anderson Frailey]

**Bug Fixes**
- Fix incorrect aging of `e00900` variable
  [[#2027](https://github.com/open-source-economics/Tax-Calculator/pull/2027)
  by Martin Holmer with bug reported by Max Ghenis]


2018-05-21 Release 0.20.1
-------------------------
(last merged pull request is
[#2005](https://github.com/open-source-economics/Tax-Calculator/pull/2005))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Fix warning logic to exclude CPS data and to fix handling of changes in standard deduction amounts
  [[#2005](https://github.com/open-source-economics/Tax-Calculator/pull/2005)
  by Martin Holmer]


2018-05-18 Release 0.20.0
-------------------------
(last merged pull request is
[#2003](https://github.com/open-source-economics/Tax-Calculator/pull/2003))

**API Changes**
- Simplify table-creation Calculator methods and related utility functions
  [[#1984](https://github.com/open-source-economics/Tax-Calculator/pull/1984)
  by Martin Holmer]
- Rename `Growfactors` class as `GrowFactors` and rename `Growdiff` class as `GrowDiff`
  [[#1996](https://github.com/open-source-economics/Tax-Calculator/pull/1996)
  by Martin Holmer]
- Add `quantity_response` utility function and remove obsolete charity and earnings response logic from Behavior class
  [[#1997](https://github.com/open-source-economics/Tax-Calculator/pull/1997)
  by Martin Holmer]
- Add empty shell of `GrowModel` class that will eventually contain a simple macroeconomic growth model with annual feedback to the microeconomic simulation
  [[#1998](https://github.com/open-source-economics/Tax-Calculator/pull/1998)
  by Martin Holmer]

**New Features**
- Streamline logic that prevents disclosure of details of PUF filing units
  [[#1979](https://github.com/open-source-economics/Tax-Calculator/pull/1979)
  by Martin Holmer]
- Add option to not include benefits in a Records object that uses CPS data
  [[#1985](https://github.com/open-source-economics/Tax-Calculator/pull/1985)
  and
  [[#1988](https://github.com/open-source-economics/Tax-Calculator/pull/1988)
  by Martin Holmer]
- Update CODING and TESTING documentation to reflect recommended usage of `pycodestyle` in place of `pep8`
  [[#1989](https://github.com/open-source-economics/Tax-Calculator/pull/1989)
  by Martin Holmer]
- Add validity checking for non-behavior assumption parameters
  [[#1992](https://github.com/open-source-economics/Tax-Calculator/pull/1992)
  by Martin Holmer]
- Add Tax-Calculator Cookbook recipe using Behavior class and its `response` method
  [[#1993](https://github.com/open-source-economics/Tax-Calculator/pull/1993)
  by Martin Holmer]
- Add Tax-Calculator Cookbook recipe showing how to create a custom table
  [[#1994](https://github.com/open-source-economics/Tax-Calculator/pull/1994)
  by Martin Holmer]
- Add Tax-Calculator Cookbook recipe showing how to use new `quantity_response` utility function
  [[#2002](https://github.com/open-source-economics/Tax-Calculator/pull/2002)
  by Martin Holmer]

**Bug Fixes**
- Fix mishandling of boolean policy parameters
  [[#1982](https://github.com/open-source-economics/Tax-Calculator/pull/1982)
  by Hank Doupe]


2018-04-19 Release 0.19.0
-------------------------
(last merged pull request is
[#1977](https://github.com/open-source-economics/Tax-Calculator/pull/1977))

**API Changes**
- Improve data quality of several CPS age variables, which causes changes in CPS tax results
  [[#1962](https://github.com/open-source-economics/Tax-Calculator/pull/1962)
  by Anderson Frailey and Martin Holmer based on bug reported by Max Ghenis]

**New Features**
- Add validity checking for revised values of behavioral response parameters
  [[#1952](https://github.com/open-source-economics/Tax-Calculator/pull/1952)
  by Hank Doupe]
- Strengthen logic that prevents disclosure of details of filing units in PUF
  [[#1972](https://github.com/open-source-economics/Tax-Calculator/pull/1972)
   [#1973](https://github.com/open-source-economics/Tax-Calculator/pull/1973)
   [#1976](https://github.com/open-source-economics/Tax-Calculator/pull/1976)
  by Martin Holmer]

**Bug Fixes**
- Fix loose checking of the data type of parameters in reform dictionaries passed to the Policy class `implement_reform` method
  [[#1960](https://github.com/open-source-economics/Tax-Calculator/pull/1960)
  by Martin Holmer based on bug reported by Hank Doupe]
- Fix diagnostic and distribution tables so that itemizers plus standard-deduction takers equals total returns
  [[#1964](https://github.com/open-source-economics/Tax-Calculator/pull/1964)
  by Martin Holmer]
- Fix confusing documentation of the data type of parameters
  [[#1970](https://github.com/open-source-economics/Tax-Calculator/pull/1970)
  by Martin Holmer as suggested by Hank Doupe]
- Fix bug in TCJA tax calculations for those with large business losses
  [[#1977](https://github.com/open-source-economics/Tax-Calculator/pull/1977)
  by Martin Holmer based on bug report by Ernie Tedeschi]


2018-03-30 Release 0.18.0
-------------------------
(last merged pull request is
[#1942](https://github.com/open-source-economics/Tax-Calculator/pull/1942))

**API Changes**
- Remove redundant `_DependentCredit_c` policy parameter and fix dependent credit phase-out logic
  [[#1937](https://github.com/open-source-economics/Tax-Calculator/pull/1937)
  by Martin Holmer]

**New Features**
- Add memory management logic to reduce memory usage
  [[#1942](https://github.com/open-source-economics/Tax-Calculator/pull/1942)
  by Martin Holmer]

**Bug Fixes**
- Replace monthly housing benefits with annual housing benefits in CPS data
  [[#1941](https://github.com/open-source-economics/Tax-Calculator/pull/1941)
  by Anderson Frailey]


2018-03-16 Release 0.17.0
-------------------------
(last merged pull request is
[#1926](https://github.com/open-source-economics/Tax-Calculator/pull/1926))

**API Changes**
- Make `run_nth_year_tax_calc_model` function return tables with all rows
  [[#1914](https://github.com/open-source-economics/Tax-Calculator/pull/1914)
  by Martin Holmer]
- Rename Calculator class `param` method as `policy_param`
  [[#1915](https://github.com/open-source-economics/Tax-Calculator/pull/1915)
  by Martin Holmer]
- Add notice of end of Python 2.7 support beginning in 2019
  [[#1923](https://github.com/open-source-economics/Tax-Calculator/pull/1923)
  by Martin Holmer]

**New Features**
- Add row names to distribution and difference tables
  [[#1913](https://github.com/open-source-economics/Tax-Calculator/pull/1913)
  by Martin Holmer]
- Add row for those with zero income in distribution and difference tables
  [[#1917](https://github.com/open-source-economics/Tax-Calculator/pull/1917)
  by Martin Holmer]
- Revise Calculator class decile_graph method to provide option for including those with zero income and/or those with negative income in the bottom decile
  [[#1918](https://github.com/open-source-economics/Tax-Calculator/pull/1918)
  by Martin Holmer]
- Add UBI benefits statistic to distribution and difference tables
  [[#1919](https://github.com/open-source-economics/Tax-Calculator/pull/1919)
  by Killian Pinkelman]
- Add two benefits statistics to distribution and difference tables
  [[#1925](https://github.com/open-source-economics/Tax-Calculator/pull/1925)
  by Anderson Frailey]

**Bug Fixes**
- None


2018-03-09 Release 0.16.2
-------------------------
(last merged pull request is
[#1911](https://github.com/open-source-economics/Tax-Calculator/pull/1911))

**API Changes**
- None

**New Features**
- Add graph of percentage change in after-tax expanded income by baseline expanded-income percentile and include it in `tc --graphs` output and in the Cookbook's basic recipe
  [[#1890](https://github.com/open-source-economics/Tax-Calculator/pull/1890)
  by Martin Holmer]
- Improve handling of those with negative or zero `expanded_income` in tables and graphs
  [[#1902](https://github.com/open-source-economics/Tax-Calculator/pull/1902)
  by Martin Holmer]
- Add three new benefits and improve imputation of interest, dividend, and pension income in CPS data
  [[#1911](https://github.com/open-source-economics/Tax-Calculator/pull/1911)
  by Anderson Frailey and Martin Holmer]

**Bug Fixes**
- Correct bottom bin name in distribution/difference tables exported to TaxBrain
  [[#1889](https://github.com/open-source-economics/Tax-Calculator/pull/1889)
  by Martin Holmer]
- Add missing check of equality of `BEN_*_value` parameters in baseline and reform Calculator objects when using `expanded_income` in tables or graphs
  [[#1894](https://github.com/open-source-economics/Tax-Calculator/pull/1894)
  by Martin Holmer]
- Correct and simplify calculation of `expanded_income`
  [[#1897](https://github.com/open-source-economics/Tax-Calculator/pull/1897)
   [#1899](https://github.com/open-source-economics/Tax-Calculator/pull/1899)
   [#1900](https://github.com/open-source-economics/Tax-Calculator/pull/1900)
   [#1901](https://github.com/open-source-economics/Tax-Calculator/pull/1901)
  by Martin Holmer and Anderson Frailey], which requires new `puf.csv`
  input file with this information:
  * Byte size: 54718219
  * MD5 checksum: e22429702920a0d927a36ea1103ba067
- Correct AGI concept used in EITC phase-out logic
  [[#1907](https://github.com/open-source-economics/Tax-Calculator/pull/1907)
  by Martin Holmer as reported by Max Ghenis]


2018-02-16 Release 0.16.1
-------------------------
(last merged pull request is
[#1886](https://github.com/open-source-economics/Tax-Calculator/pull/1886))

**API Changes**
- None

**New Features**
- Add graph of percentage change in after-tax expanded income by baseline expanded-income quintiles
  [[#1880](https://github.com/open-source-economics/Tax-Calculator/pull/1880)
  by Martin Holmer]
- Improve consistency of UBI-related head-count-by-age values in the CPS data
  [[#1882](https://github.com/open-source-economics/Tax-Calculator/pull/1882)
  by Anderson Frailey]
- Add variable to `cps.csv.gz` that facilitates matching CPS data to Tax-Calculator filing units
  [[#1885](https://github.com/open-source-economics/Tax-Calculator/pull/1885)
  by Anderson Frailey]

**Bug Fixes**
- Fix lack of calculation of `benefit_cost_total` variable
  [[#1886](https://github.com/open-source-economics/Tax-Calculator/pull/1886)
  by Anderson Frailey]


2018-02-13 Release 0.16.0
-------------------------
(last merged pull request is
[#1871](https://github.com/open-source-economics/Tax-Calculator/pull/1871))

**API Changes**
- Improve data quality of several existing CPS variables, which causes changes in CPS tax results
  [[#1853](https://github.com/open-source-economics/Tax-Calculator/pull/1853)
  by Anderson Frailey with assistance from Martin Holmer]
- Use 2011 PUF data (rather than the older 2009 PUF data), which causes changes in PUF tax results
  [[#1871](https://github.com/open-source-economics/Tax-Calculator/pull/1871)
  by Anderson Frailey and Martin Holmer], which requires new `puf.csv` input file with this information:
  * Byte size: 54714632
  * MD5 checksum: de4a59c9bce0a7d5e6c3110172237c9b

**New Features**
- Add ability to extrapolate imputed benefits and benefit-related policy parameters
  [[#1719](https://github.com/open-source-economics/Tax-Calculator/pull/1719)
  by Anderson Frailey]
- Add ability to specify the consumption value of in-kind benefits to be less than the government cost of providing in-kind benefits
  [[#1863](https://github.com/open-source-economics/Tax-Calculator/pull/1863)
  by Anderson Frailey]

**Bug Fixes**
- Improve handling of very high marginal tax rates in the `Behavior.response` method
  [[#1858](https://github.com/open-source-economics/Tax-Calculator/pull/1858)
  by Martin Holmer with assistance from Matt Jensen]


2018-01-30 Release 0.15.2
-------------------------
(last merged pull request is
[#1851](https://github.com/open-source-economics/Tax-Calculator/pull/1851))

**API Changes**
- None

**New Features**
- Add ability to specify a compound reform in the tc `--reform` option
  [[#1842](https://github.com/open-source-economics/Tax-Calculator/pull/1842)
  by Martin Holmer as requested by Ernie Tedeschi]
- Add compatible-data information for each policy parameter to user documentation
  [[#1844](https://github.com/open-source-economics/Tax-Calculator/pull/1844)
  by Martin Holmer as requested by Matt Jensen]
- Add tc `--baseline BASELINE` option that sets baseline policy equal to that specified in BASELINE reform file (rather than baseline policy being current-law poliy)
  [[#1851](https://github.com/open-source-economics/Tax-Calculator/pull/1851)
  by Martin Holmer as requested by Matt Jensen and Ernie Tedeschi]

**Bug Fixes**
- Add error checking for Calculator misuse in presence of behavioral responses
  [[#1848](https://github.com/open-source-economics/Tax-Calculator/pull/1848)
  by Martin Holmer]
- Add error checking for diagnostic_table misuse in presence of behavioral responses
  [[#1849](https://github.com/open-source-economics/Tax-Calculator/pull/1849)
  by Martin Holmer]


2018-01-20 Release 0.15.1
-------------------------
(last merged pull request is
[#1838](https://github.com/open-source-economics/Tax-Calculator/pull/1838))

**API Changes**
- None

**New Features**
- Add `cpi_inflatable` field for each parameter in the four JSON parameter files
  [[#1838](https://github.com/open-source-economics/Tax-Calculator/pull/1838)
  by Martin Holmer as requested by Hank Doupe]

**Bug Fixes**
- None


2018-01-18 Release 0.15.0
-------------------------
(last merged pull request is
[#1834](https://github.com/open-source-economics/Tax-Calculator/pull/1834))

**API Changes**
- Make objects embedded in a Calculator object private and provide Calculator class access methods to manipulate the embedded objects
  [[#1791](https://github.com/open-source-economics/Tax-Calculator/pull/1791)
  by Martin Holmer]
- Rename three UBI policy parameters to be more descriptive
  [[#1813](https://github.com/open-source-economics/Tax-Calculator/pull/1813)
  by Martin Holmer as suggested by Max Ghenis]

**New Features**
- Add validity testing of compatible_data information in `current_law_policy.json`
  [[#1614](https://github.com/open-source-economics/Tax-Calculator/pull/1614)
  by Matt Jensen with assistance from Hank Doupe]
- Add `--outdir` option to command-line `tc` tool
  [[#1801](https://github.com/open-source-economics/Tax-Calculator/pull/1801)
  by Martin Holmer as suggested by Reuben Fischer-Baum]
- Make TCJA policy current-law policy
  [[#1803](https://github.com/open-source-economics/Tax-Calculator/pull/1803)
  by Martin Holmer with assistance from Cody Kallen]
- Change minimum required pandas version from 0.21.0 to 0.22.0 and remove zsum() pandas work-around
  [[#1805](https://github.com/open-source-economics/Tax-Calculator/pull/1805)
  by Martin Holmer]
- Add policy parameter and logic needed to represent TCJA treatment of alimony received
  [[#1818](https://github.com/open-source-economics/Tax-Calculator/pull/1818)
  by Martin Holmer and Cody Kallen]
- Add policy parameters and logic needed to represent TCJA limits on pass-through income and business losses
  [[#1819](https://github.com/open-source-economics/Tax-Calculator/pull/1819)
  by Cody Kallen]
- Revise user documentation and Tax-Calculator Cookbook recipes to reflect TCJA as current-law policy
  [[#1832](https://github.com/open-source-economics/Tax-Calculator/pull/1832)
  by Martin Holmer]

**Bug Fixes**
- Fix column order in distribution table
  [[#1834](https://github.com/open-source-economics/Tax-Calculator/pull/1834)
  by Martin Holmer and Hank Doupe]


2017-12-24 Release 0.14.3
-------------------------
(last merged pull request is
[#1796](https://github.com/open-source-economics/Tax-Calculator/pull/1796))

**API Changes**
- None

**New Features**
- Change minimum required pandas version from 0.20.1 to 0.21.0
  [[#1781](https://github.com/open-source-economics/Tax-Calculator/pull/1781)
  by Martin Holmer]
- Generalize validation of boolean policy parameter values in reforms
  [[#1782](https://github.com/open-source-economics/Tax-Calculator/pull/1782)
  by Martin Holmer as requested by Hank Doupe]
- Handle small numerical differences in test results generated under Python 3.6
  [[#1795](https://github.com/open-source-economics/Tax-Calculator/pull/1795)
  by Martin Holmer with need pointed out by Matt Jensen]
- Make the `_cpi_offset` policy parameter work like other policy parameters 
  [[#1796](https://github.com/open-source-economics/Tax-Calculator/pull/1796)
  by Martin Holmer with need pointed out by Matt Jensen and Hank Doupe]

**Bug Fixes**
- None


2017-12-19 Release 0.14.2
-------------------------
(last merged pull request is
[#1775](https://github.com/open-source-economics/Tax-Calculator/pull/1775))

**API Changes**
- None

**New Features**
- Add two policy parameters that can be used to cap itemized SALT deductions as a fraction of AGI
  [[#1711](https://github.com/open-source-economics/Tax-Calculator/pull/1711)
  by Derrick Choe with assistance from Cody Kallen and Hank Doupe]
- Update "notes" in `current_law_policy.json` for policy parameters first introduced in TCJA bills
  [[#1765](https://github.com/open-source-economics/Tax-Calculator/pull/1765)
  by Max Ghenis]

**Bug Fixes**
- Standardize format of ValueError messages raised by Policy.implement_reform method
  [[#1775](https://github.com/open-source-economics/Tax-Calculator/pull/1775)
  by Martin Holmer, reported by Max Ghenis and diagnosed by Hank Doupe]


2017-12-15 Release 0.14.1
-------------------------
(last merged pull request is
[#1759](https://github.com/open-source-economics/Tax-Calculator/pull/1759))

**API Changes**
- None

**New Features**
- Add policy parameter that can cap the combined state and local income/sales and real-estate deductions
  [[#1756](https://github.com/open-source-economics/Tax-Calculator/pull/1756)
  by Cody Kallen with helpful discussion from Ernie Tedeschi and Matt Jensen]
- Add percentage change in income by income decile graph to `tc --graphs` output
  [[#1758](https://github.com/open-source-economics/Tax-Calculator/pull/1758)
  by Martin Holmer]
- Add JSON reform file for TCJA conference bill
  [[#1759](https://github.com/open-source-economics/Tax-Calculator/pull/1759)
  by Cody Kallen with review by Matt Jensen and Sean Wang]

**Bug Fixes**
- None


2017-12-11 Release 0.14.0
-------------------------
(last merged pull request is
[#1742](https://github.com/open-source-economics/Tax-Calculator/pull/1742))

**API Changes**
- Add several Calculator table methods and revise table utilities to not use Calculator object(s)
  [[#1718](https://github.com/open-source-economics/Tax-Calculator/pull/1718)
  by Martin Holmer]
- Add several Calculator graph methods and revise graph utilities to not use Calculator objects
  [[#1722](https://github.com/open-source-economics/Tax-Calculator/pull/1722)
  by Martin Holmer]
- Add Calculator ce_aftertax_income method and revise corresponding utility to not use Calculator object
  [[#1723](https://github.com/open-source-economics/Tax-Calculator/pull/1723)
  by Martin Holmer]

**New Features**
- Add new policy parameter for refunding the new CTC against all payroll taxes
  [[#1716](https://github.com/open-source-economics/Tax-Calculator/pull/1716)
  by Matt Jensen as suggested by Ernie Tedeschi]
- Remove calculation of AGI tables from the TaxBrain Interface, tbi
  [[#1724](https://github.com/open-source-economics/Tax-Calculator/pull/1724)
  by Martin Holmer as suggested by Matt Jensen and Hank Doupe]
- Add ability to specify partial customized CLI `tc --dump` output
  [[#1735](https://github.com/open-source-economics/Tax-Calculator/pull/1735)
  by Martin Holmer as suggested by Sean Wang]
- Add *Cookbook of Tested Recipes for Python Programming with Tax-Calculator*
  [[#1740](https://github.com/open-source-economics/Tax-Calculator/pull/1740)
  by Martin Holmer]
- Add calculation of two values on the ALL row of the difference table
  [[#1741](https://github.com/open-source-economics/Tax-Calculator/pull/1741)
  by Martin Holmer]

**Bug Fixes**
- Fix Behavior.response method to handle very high marginal tax rates
  [[#1698](https://github.com/open-source-economics/Tax-Calculator/pull/1698)
  by Martin Holmer, reported by Richard Evans and Jason DeBacker]
- Fix `create_distribution_table` to generate correct details for the top decile
  [[#1712](https://github.com/open-source-economics/Tax-Calculator/pull/1712)
  by Martin Holmer]


2017-11-17 Release 0.13.2
-------------------------
(last merged pull request is
[#1680](https://github.com/open-source-economics/Tax-Calculator/pull/1680))

**API Changes**
- None

**New Features**
- Add TCJA_House_Amended JSON policy reform file
  [[#1664](https://github.com/open-source-economics/Tax-Calculator/pull/1664)
  by Cody Kallen and Matt Jensen]
- Add `_cpi_offset` policy parameter that can be used to specify chained CPI indexing reforms
  [[#1667](https://github.com/open-source-economics/Tax-Calculator/pull/1667)
  by Martin Holmer]
- Add new policy parameter that changes the stacking order of child/dependent credits
  [[#1676](https://github.com/open-source-economics/Tax-Calculator/pull/1676)
  by Matt Jensen as suggested by Cody Kallen with need identified by Joint Economic Committee staff]
- Add to several TCJA reform files the provision for chained CPI indexing
  [[#1680](https://github.com/open-source-economics/Tax-Calculator/pull/1680)
  by Matt Jensen]

**Bug Fixes**
- Fix `_ACTC_ChildNum` policy parameter documentation and logic
  [[#1666](https://github.com/open-source-economics/Tax-Calculator/pull/1666)
  by Martin Holmer, reported by Ernie Tedeschi]
- Fix documentation for mis-named `n1821` input variable
  [[#1672](https://github.com/open-source-economics/Tax-Calculator/pull/1672)
  by Martin Holmer, reported by Max Ghenis]
- Fix logic of run_nth_year_gdp_elast_model function in the TaxBrainInterface
  [[#1677](https://github.com/open-source-economics/Tax-Calculator/pull/1677)
  by Martin Holmer, reported by Hank Doupe]


2017-11-10 Release 0.13.1
-------------------------
(last merged pull request is
[#1655](https://github.com/open-source-economics/Tax-Calculator/pull/1655))

**API Changes**
- None

**New Features**
- Add household and family identifiers from the CPS for the cps.csv.gz file that ships with taxcalc
  [[#1635](https://github.com/open-source-economics/Tax-Calculator/pull/1635)
  by Anderson Frailey]
- Improved documentation for the cps.csv.gz file that ships with taxcalc
  [[#1648](https://github.com/open-source-economics/Tax-Calculator/pull/1648)
  by Martin Holmer]
- Add parameter for the business income exclusion in the Senate TCJA Chairman's mark
  [[#1651](https://github.com/open-source-economics/Tax-Calculator/pull/1648)
  by Cody Kallen]
- Add TCJA reform file for the Senate Chairman's mark
  [[#1652](https://github.com/open-source-economics/Tax-Calculator/pull/1652)
  by Cody Kallen]
- Add FIPS state codes to the cps.csv.gz file that ships with taxcalc
  [[#1653](https://github.com/open-source-economics/Tax-Calculator/pull/1653)
  by Anderson Frailey]

**Bug Fixes**
- Fix an edge case related to new pass-through parameters that caused some extreme MTRs
  [[#1645](https://github.com/open-source-economics/Tax-Calculator/pull/1645)
  by Cody Kallen, reported by Richard Evans]


2017-11-07 Release 0.13.0
-------------------------
(last merged pull request is
[#1632](https://github.com/open-source-economics/Tax-Calculator/pull/1632))

**API Changes**
- Add new statistics and top-decile detail to distribution and difference tables
  [[#1605](https://github.com/open-source-economics/Tax-Calculator/pull/1605)
  by Martin Holmer]

**New Features**
- Add expanded_income and aftertax_income to distribution table
  [[#1602](https://github.com/open-source-economics/Tax-Calculator/pull/1602)
  by Martin Holmer]
- Add utility functions that generate a change-in-aftertax-income-by-decile graph
  [[#1606](https://github.com/open-source-economics/Tax-Calculator/pull/1606)
  by Martin Holmer]
- Add new dependent credits for children and non-children dependents
  [[#1615](https://github.com/open-source-economics/Tax-Calculator/pull/1615)
  by Cody Kallen]
- Add new non-refundable credit for filer and spouse
  [[#1618](https://github.com/open-source-economics/Tax-Calculator/pull/1618)
  by Cody Kallen]
- Add capability to model pass-through tax rate eligiblity rules in TCJA
  [[#1620](https://github.com/open-source-economics/Tax-Calculator/pull/1620)
  by Cody Kallen]
- Make several Personal Nonrefundable Credit parameters available to external applications like TaxBrain
  [[#1622](https://github.com/open-source-economics/Tax-Calculator/pull/1622)
  by Matt Jensen]
- Extend extrapolation to 2027 and update to June 2017 CBO baseline
  [[#1624](https://github.com/open-source-economics/Tax-Calculator/pull/1624)
  by Anderson Frailey]
- Add new reform JSON file for the Tax Cuts and Jobs Act
  [[#1625](https://github.com/open-source-economics/Tax-Calculator/pull/1625)
  by Cody Kallen]

**Bug Fixes**
- Resolve compatibility issues with Pandas 0.21.0
  [[#1629](https://github.com/open-source-economics/Tax-Calculator/pull/1629)
  by Hank Doupe]
- Cleaner solution to compatibility issues with Pandas 0.21.0
  [[#1634](https://github.com/open-source-economics/Tax-Calculator/pull/1634)
  by Hank Doupe]


2017-10-20 Release 0.12.0
-------------------------
(last merged pull request is
[#1600](https://github.com/open-source-economics/Tax-Calculator/pull/1600))

**API Changes**
- Rename read_json_param_files as read_json_param_objects
  [[#1563](https://github.com/open-source-economics/Tax-Calculator/pull/1563)
  by Martin Holmer]
- Remove arrays_not_lists argument from read_json_param_objects
  [[#1568](https://github.com/open-source-economics/Tax-Calculator/pull/1568)
  by Martin Holmer]
- Rename dropq as tbi (taxbrain interface) and refactor run_nth_year_*_model functions so that either puf.csv or cps.csv can be used as input data
  [[#1577](https://github.com/open-source-economics/Tax-Calculator/pull/1577)
  by Martin Holmer]
- Change Calculator class constructor so that it makes a deep copy of each specified object for internal use
  [[#1582](https://github.com/open-source-economics/Tax-Calculator/pull/1582)
  by Martin Holmer]
- Rename and reorder difference table columns
  [[#1584](https://github.com/open-source-economics/Tax-Calculator/pull/1584)
  by Martin Holmer]

**New Features**
- Add Calculator.reform_documentation that generates plain text documentation of a reform
  [[#1564](https://github.com/open-source-economics/Tax-Calculator/pull/1564)
  by Martin Holmer]
- Enhance stats_summary.py script and its output
  [[#1566](https://github.com/open-source-economics/Tax-Calculator/pull/1566)
  by Amy Xu]
- Add reform documentation as standard output from Tax-Calculator CLI, tc
  [[#1567](https://github.com/open-source-economics/Tax-Calculator/pull/1567)
  by Martin Holmer]
- Add parameter type checking to Policy.implement_reform method
  [[#1585](https://github.com/open-source-economics/Tax-Calculator/pull/1585)
  by Martin Holmer]
- Add `_CTC_new_for_all` policy parameter to allow credits for those with negative AGI
  [[#1595](https://github.com/open-source-economics/Tax-Calculator/pull/1595)
  by Martin Holmer]
- Narrow range of legal values for `_CDCC_c` policy parameter
  [[#1597](https://github.com/open-source-economics/Tax-Calculator/pull/1597)
  by Matt Jensen]
- Make several UBI policy parameters available to external applications like TaxBrain
  [[#1599](https://github.com/open-source-economics/Tax-Calculator/pull/1599)
  by Matt Jensen]

**Bug Fixes**
- Relax _STD and _STD_Dep minimum value warning logic
  [[#1578](https://github.com/open-source-economics/Tax-Calculator/pull/1578)
  by Martin Holmer]
- Fix macro-elasticity model logic so that GDP change in year t depends on tax rate changes in year t-1
  [[#1579](https://github.com/open-source-economics/Tax-Calculator/pull/1579)
  by Martin Holmer]
- Fix bugs in automatic generation of reform documentation having to do with policy parameters that are boolean scalars
  [[#1596](https://github.com/open-source-economics/Tax-Calculator/pull/1596)
  by Martin Holmer]


2017-09-21 Release 0.11.0
-------------------------
(last merged pull request is
[#1555](https://github.com/open-source-economics/Tax-Calculator/pull/1555))

**API Changes**
- Revise dropq distribution and difference tables used by TaxBrain
  [[#1537](https://github.com/open-source-economics/Tax-Calculator/pull/1537)
  by Anderson Frailey and Martin Holmer]
- Make dropq run_nth_year_tax_calc_model return a dictionary of results
  [[#1543](https://github.com/open-source-economics/Tax-Calculator/pull/1543)
  by Martin Holmer]

**New Features**
- Add option to cap the amount of gross itemized deductions allowed as a decimal fraction of AGI
  [[#1542](https://github.com/open-source-economics/Tax-Calculator/pull/1542)
  by Matt Jensen]
- Add dropq tables using AGI as income measure for TaxBrain use
  [[#1544](https://github.com/open-source-economics/Tax-Calculator/pull/1544)
  by Martin Holmer]
- Add JSON reform file for Brown-Khanna GAIN Act that expands the EITC
  [[#1555](https://github.com/open-source-economics/Tax-Calculator/pull/1555)
  by Matt Jensen and Martin Holmer]

**Bug Fixes**
- None


2017-09-13 Release 0.10.2
-------------------------

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Allow policy parameter suffix logic to work even when there are reform errors
  [[34561ff](https://github.com/open-source-economics/Tax-Calculator/commit/34561ffdeb23c632e248d760c0e34417df0b41f3)
  by Martin Holmer]


2017-09-08 Release 0.10.1
-------------------------

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Fix vagueness of error/warning messages for non-scalar policy parameters
  [[5536792](https://github.com/open-source-economics/Tax-Calculator/commit/5536792538c3f3e687cccc9e38b20949ac68cb9a)
  by Martin Holmer]


2017-08-28 Release 0.10.0
-------------------------
(last merged pull request is
[#1531](https://github.com/open-source-economics/Tax-Calculator/pull/1531))

**API Changes**
- Add dropq function that returns reform warnings and errors
  [[#1524](https://github.com/open-source-economics/Tax-Calculator/pull/1524)
  by Martin Holmer]

**New Features**
- Add option to use policy parameter suffixes in JSON reform files
  [[#1505](https://github.com/open-source-economics/Tax-Calculator/pull/1505)
  by Martin Holmer] and
  [[#1520](https://github.com/open-source-economics/Tax-Calculator/pull/1520)
  by Martin Holmer]
- Add rounding of wage-inflated or price-inflated parameter values to nearest cent
  [[#1506](https://github.com/open-source-economics/Tax-Calculator/pull/1506)
  by Martin Holmer]
- Add extensive checking of reform policy parameter names and values
  [[#1524](https://github.com/open-source-economics/Tax-Calculator/pull/1524)
  by Martin Holmer]

**Bug Fixes**
- None


2017-07-26 Release 0.9.2
------------------------
(last merged pull request is
[#1490](https://github.com/open-source-economics/Tax-Calculator/pull/1490))

**API Changes**
- None

**New Features**
- Add several taxcalc/reforms/earnings_shifting.* files that analyze the revenue implications of high-paid workers forming personal LLCs to contract with their former employers under the Trump2017.json reform
  [[#1464](https://github.com/open-source-economics/Tax-Calculator/pull/1464)
  by Martin Holmer]
- Add ability to read and calculate taxes with new CPS input data for 2014 and subsequent years
  [[#1484](https://github.com/open-source-economics/Tax-Calculator/pull/1484)
  by Martin Holmer]
- Add tests of ability to calculate taxes with new CPS input data
  [[#1490](https://github.com/open-source-economics/Tax-Calculator/pull/1490)
  by Martin Holmer]

**Bug Fixes**
- Fix decorators bug that appeared when numpy 1.13.1, and pandas 0.20.2 that uses numpy 1.13, recently became available
  [[#1470](https://github.com/open-source-economics/Tax-Calculator/pull/1470)
  by T.J. Alumbaugh]
- Fix records bug that appeared when numpy 1.13.1, and pandas 0.20.2 that uses numpy 1.13, recently became available
  [[#1473](https://github.com/open-source-economics/Tax-Calculator/pull/1473)
  by Martin Holmer]


2017-07-06 Release 0.9.1
------------------------
(last merged pull request is
[#1438](https://github.com/open-source-economics/Tax-Calculator/pull/1438))

**API Changes**
- None

**New Features**
- Add Form 1065 Schedule K-1 self-employment earnings to calculation of self-employment payroll taxes
  [[#1438](https://github.com/open-source-economics/Tax-Calculator/pull/1438)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 53743252
  * MD5 checksum: ca0ad8bbb05ee15b1cbefc7f1fa1f965
- Improve calculation of sub-sample weights
  [[#1441](https://github.com/open-source-economics/Tax-Calculator/pull/1441)
  by Hank Doupe]

**Bug Fixes**
- Fix personal refundable credit bug and personal nonrefundable credit bug
  [[#1450](https://github.com/open-source-economics/Tax-Calculator/pull/1450)
  by Martin Holmer]


2017-06-14 Release 0.9.0
------------------------
(last merged pull request is
[#1431](https://github.com/open-source-economics/Tax-Calculator/pull/1431))

**API Changes**
- Initial specification of public API removes several unused utility
  functions and makes private several Tax-Calculator members whose
  only role is to support public members
  [[#1424](https://github.com/open-source-economics/Tax-Calculator/pull/1424)
  by Martin Holmer]

**New Features**
- Add nonrefundable personal credit reform options
  [[#1427](https://github.com/open-source-economics/Tax-Calculator/pull/1427)
  by William Ensor]

- Add repeal personal exemptions for dependents under age 18 reform option
  [[#1428](https://github.com/open-source-economics/Tax-Calculator/pull/1428)
  by Hank Doupe]

- Switch to use of new improved `puf.csv` input file that causes small
  changes in tax results
  [[#1429](https://github.com/open-source-economics/Tax-Calculator/pull/1429)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 52486351
  * MD5 checksum: d56b649c92049e32501b2d2fc5c36c92

**Bug Fixes**
- Fix logic of gross casualty loss calculation by moving it out of
  Tax-Calculator and into the taxdata repository
  [[#1426](https://github.com/open-source-economics/Tax-Calculator/pull/1426)
  by Martin Holmer]


2017-06-08 Release 0.8.5
------------------------
(last merged pull request is
[#1416](https://github.com/open-source-economics/Tax-Calculator/pull/1416))

**API Changes**
- None

**New Features**
- Add column to differences table to show the change in tax liability
  as percentage of pre-reform after tax income
  [[#1375](https://github.com/open-source-economics/Tax-Calculator/pull/1375)
  by Anderson Frailey]
- Add policy reform file for the Renacci reform
  [[#1376](https://github.com/open-source-economics/Tax-Calculator/pull/1376),
  [#1383](https://github.com/open-source-economics/Tax-Calculator/pull/1383)
  and
  [#1385](https://github.com/open-source-economics/Tax-Calculator/pull/1385)
  by Hank Doupe]
- Add separate ceiling for each itemized deduction parameter
  [[#1385](https://github.com/open-source-economics/Tax-Calculator/pull/1385)
  by Hank Doupe]

**Bug Fixes**
- Fix bug in add_weighted_income_bins utility function
  [[#1387](https://github.com/open-source-economics/Tax-Calculator/pull/1387)
  by Martin Holmer]


2017-05-12 Release 0.8.4
------------------------
(last merged pull request is
[#1363](https://github.com/open-source-economics/Tax-Calculator/pull/1363))

**API Changes**
- None

**New Features**
- Add economic response assumption file template to documentation
  [[#1332](https://github.com/open-source-economics/Tax-Calculator/pull/1332)
  by Cody Kallen]
- Complete process of creating [user
  documentation](http://open-source-economics.github.io/Tax-Calculator/)
  [[#1355](https://github.com/open-source-economics/Tax-Calculator/pull/1355)
  by Martin Holmer]
- Add Tax-Calculator conda package for Python 3.6
  [[#1361](https://github.com/open-source-economics/Tax-Calculator/pull/1361)
  by Martin Holmer]

**Bug Fixes**
- None


2017-05-01 Release 0.8.3
------------------------
(last merged pull request is
[#1328](https://github.com/open-source-economics/Tax-Calculator/pull/1328))

**API Changes**
- None

**New Features**
- Add --test installation option to Tax-Calculator CLI
  [[#1306](https://github.com/open-source-economics/Tax-Calculator/pull/1306)
  by Martin Holmer]
- Add --sqldb SQLite3 database dump output option to CLI
  [[#1312](https://github.com/open-source-economics/Tax-Calculator/pull/1312)
  by Martin Holmer]
- Add a reform preset for the April 2017 Trump tax plan
  [[#1323](https://github.com/open-source-economics/Tax-Calculator/pull/1323)
  by Cody Kallen]
- Add Other Taxes to tables and clarify documentation
  [[#1328](https://github.com/open-source-economics/Tax-Calculator/pull/1328)
  by Martin Holmer]

**Bug Fixes**
- None


2017-04-13 Release 0.8.2
------------------------
(last merged pull request is
[#1295](https://github.com/open-source-economics/Tax-Calculator/pull/1295))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Minor edits to comments in Trump/Clinton policy reform files
  [[#1295](https://github.com/open-source-economics/Tax-Calculator/pull/1295)
  by Matt Jensen]


2017-04-13 Release 0.8.1
------------------------
(last merged pull request is
[#1293](https://github.com/open-source-economics/Tax-Calculator/pull/1293))

**API Changes**
- None

**New Features**
- Add testing for notebooks, starting with the behavior_example and
  10-minute notebooks
  [[#1198](https://github.com/open-source-economics/Tax-Calculator/pull/1198)
  by Peter Steinberg]
- Add MTR with respect to spouse earnings
  [[#1257](https://github.com/open-source-economics/Tax-Calculator/pull/1257)
  by Anderson Frailey]
- Add tax differences table to Tax-Calculator CLI --tables output
  [[#1265](https://github.com/open-source-economics/Tax-Calculator/pull/1265)
  by Martin Holmer]
- Update Jupyter Notebooks to demonstrate the latest Python API
  [[#1277](https://github.com/open-source-economics/Tax-Calculator/pull/1277)
  by Matt Jensen]
- Enable the charitable givings elasticity to vary by AGI value
  [[#1278](https://github.com/open-source-economics/Tax-Calculator/pull/1278)
  by Matt Jensen]
- Introduce records_variables.json to serve as a single source of
  truth for Records variables
  [[#1179](https://github.com/open-source-economics/Tax-Calculator/pull/1179)
  and
  [#1285](https://github.com/open-source-economics/Tax-Calculator/pull/1285)
  by Zach Risher]

**Bug Fixes**
- None


2017-03-24 Release 0.8.0
------------------------
(last merged pull request is
[#1260](https://github.com/open-source-economics/Tax-Calculator/pull/1260))

**API Changes**
- None

**New Features**
- Add ability to calculate, and possibly tax, UBI benefits
  [[#1235](https://github.com/open-source-economics/Tax-Calculator/pull/1235)
  by Anderson Frailey]
- Add additional deduction and credit haircut policy parameters
  [[#1247](https://github.com/open-source-economics/Tax-Calculator/pull/1247)
  by Anderson Frailey]
- Add constant charitable giving elasticities to behavioral response
  [[#1246](https://github.com/open-source-economics/Tax-Calculator/pull/1246)
  by Matt Jensen]
- Add another credit haircut policy parameter
  [[#1252](https://github.com/open-source-economics/Tax-Calculator/pull/1252)
  by Anderson Frailey]
- Make Tax-Calculator CLI an entry point to the taxcalc package
  [[#1253](https://github.com/open-source-economics/Tax-Calculator/pull/1253)
  by Martin Holmer]
- Add --tables option to Tax-Calculator CLI
  [[#1258](https://github.com/open-source-economics/Tax-Calculator/pull/1258)
  by Martin Holmer]

**Bug Fixes**
- None


2017-03-08 Release 0.7.9
------------------------
(last merged pull request is
[#1228](https://github.com/open-source-economics/Tax-Calculator/pull/1228))

**API Changes**
- Move simtax.py to taxcalc/validation/taxsim directory
  [[#1288](https://github.com/open-source-economics/Tax-Calculator/pull/1288)
  by Martin Holmer]

**New Features**
- Make import style more consistent
  [[#1288](https://github.com/open-source-economics/Tax-Calculator/pull/1288)
  by Martin Holmer]

**Bug Fixes**
- Add growdiff.json to MANIFEST.in
  [[#1217](https://github.com/open-source-economics/Tax-Calculator/pull/1217)
  and
  [#1219](https://github.com/open-source-economics/Tax-Calculator/pull/1219)
  by Peter Steinberg]


2017-03-01 Release 0.7.8
------------------------
(last merged pull request is
[#1206](https://github.com/open-source-economics/Tax-Calculator/pull/1206))

**API Changes**
- Redesign Growth class to support more realistic growth responses
  [[#1199](https://github.com/open-source-economics/Tax-Calculator/pull/1199)
  by Martin Holmer]

**New Features**
- Add a policy reform file for key provisions of the Ryan-Brady Better
  Way tax plan
  [[#1204](https://github.com/open-source-economics/Tax-Calculator/pull/1204)
  by Cody Kallen]
- Add a policy reform file for select provisions of the Clinton 2016
  campaign tax plan
  [[#1206](https://github.com/open-source-economics/Tax-Calculator/pull/1206)
  by Cody Kallen]

**Bug Fixes**
- None


2017-02-16 Release 0.7.7
------------------------
(last merged pull request is
[#1197](https://github.com/open-source-economics/Tax-Calculator/pull/1197))

**API Changes**
- None

**New Features**
- None

**Bug Fixes**
- Add name of new Stage3 adjustment-ratios file to MANIFEST.in
  [[#1197](https://github.com/open-source-economics/Tax-Calculator/pull/1197)
  by Anderson Frailey]


2017-02-15 Release 0.7.6
------------------------
(last merged pull request is
[#1192](https://github.com/open-source-economics/Tax-Calculator/pull/1192))

**API Changes**
- Add Stage3 adjustment ratios to target IRS-SOI data on the
  distribution of interest income
  [[#1193](https://github.com/open-source-economics/Tax-Calculator/pull/1193)
  by Anderson Frailey],
  which requires new `puf.csv` input file with this information:
  * Byte size: 51470450
  * MD5 checksum: 3a02e9909399ba85d0a7cf5e98149b90

**New Features**
- Add to diagnostic table the number of tax units with non-positive
  income and combined tax liability
  [[#1170](https://github.com/open-source-economics/Tax-Calculator/pull/1170)
  by Anderson Frailey]

**Bug Fixes**
- Correct Policy wage growth rates to agree with CBO projection
  [[#1171](https://github.com/open-source-economics/Tax-Calculator/pull/1171)
  by Martin Holmer]


2017-01-31 Release 0.7.5
------------------------
(last merged pull request is
[#1169](https://github.com/open-source-economics/Tax-Calculator/pull/1169))

**API Changes**
- None

**New Features**
- Add a Trump 2016 policy reform JSON file
  [[#1135](https://github.com/open-source-economics/Tax-Calculator/pull/1135)
  by Matt Jensen]
- Reduce size of input file by rounding weights
  [[#1158](https://github.com/open-source-economics/Tax-Calculator/pull/1158)
  by Anderson Frailey]
- Update current-law policy parameters to 2017 IRS values
  [[#1169](https://github.com/open-source-economics/Tax-Calculator/pull/1169)
  by Anderson Frailey]

**Bug Fixes**
- Index EITC investment income cap to inflation
  [[#1169](https://github.com/open-source-economics/Tax-Calculator/pull/1169)
  by Anderson Frailey]


2017-01-24 Release 0.7.4
------------------------
(last merged pull request is
[#1152](https://github.com/open-source-economics/Tax-Calculator/pull/1152))

**API Changes**
- Separate policy reforms and response assumptions into two separate
  JSON files
  [[#1148](https://github.com/open-source-economics/Tax-Calculator/pull/1148)
  by Martin Holmer]

**New Features**
- New JSON reform file examples and capabilities
  [[#1123](https://github.com/open-source-economics/Tax-Calculator/pull/1123)-[#1131](https://github.com/open-source-economics/Tax-Calculator/pull/1131)
  by Martin Holmer]

**Bug Fixes**
- Fix bugs in 10-minute notebook
  [[#1152](https://github.com/open-source-economics/Tax-Calculator/pull/1152)
  by Matt Jensen]


2017-01-24 Release 0.7.3
------------------------
(last merged pull request is
[#1113](https://github.com/open-source-economics/Tax-Calculator/pull/1113))

**API Changes**
- None

**New Features**
- Add ability to use an expression to specify a policy parameter
  [[#1081](https://github.com/open-source-economics/Tax-Calculator/pull/1081)
  by Martin Holmer]
- Expand scope of JSON reform file to include non-policy parameters
  [[#1083](https://github.com/open-source-economics/Tax-Calculator/pull/1083)
  by Martin Holmer]
- Add ability to conduct normative expected-utility analysis
  [[#1098](https://github.com/open-source-economics/Tax-Calculator/pull/1098)
  by Martin Holmer]
- Add ability to compute MTR with respect to charitable cash
  contributions
  [[#1104](https://github.com/open-source-economics/Tax-Calculator/pull/1104)
  by Cody Kallen]
- Unify environment definition by removing requirements.txt
  [[#1094](https://github.com/open-source-economics/Tax-Calculator/pull/1094)
  by Zach Risher]
- Reorganize current_law_policy.json and add section headers
  [[#1109](https://github.com/open-source-economics/Tax-Calculator/pull/1109)
  by Matt Jensen]
- Add dollar limit on itemized deductions
  [[#1084](https://github.com/open-source-economics/Tax-Calculator/pull/1084)
  by Cody Kallen]
- Add testing for Windows with Appveyor
  [[#1111](https://github.com/open-source-economics/Tax-Calculator/pull/1111)
  by T.J. Alumbaugh]

**Bug Fixes**
- Fix capital-gains-reform bug reported by Cody Kallen
  [[#1088](https://github.com/open-source-economics/Tax-Calculator/pull/1088)
  by Martin Holmer]
- Provide Pandas 0.19.1 compatibility by fixing DataFrame.to_csv()
  usage
  [[#1092](https://github.com/open-source-economics/Tax-Calculator/pull/1092)
  by Zach Risher]


2016-12-05 Release 0.7.2
------------------------
(last merged pull request is
[#1082](https://github.com/open-source-economics/Tax-Calculator/pull/1082))

**API Changes**
- None

**New Features**
- Add ability to simulate non-refundable dependent credit
  [[#1069](https://github.com/open-source-economics/Tax-Calculator/pull/1069)
  by Cody Kallen]
- Add ability to narrow investment income exclusion base
  [[#1072](https://github.com/open-source-economics/Tax-Calculator/pull/1072)
  by Martin Holmer]
- Replace use of two cmbtp_* variables with a single cmbtp variable
  [[#1077](https://github.com/open-source-economics/Tax-Calculator/pull/1077)
  by Martin Holmer],
  which requires new `puf.csv` input file with this information:
  * Byte size: 50953138
  * MD5 checksum: acbf905c8b7d29fd4b06b13e1cc8a60c

**Bug Fixes**
- None


2016-11-15 Release 0.7.1
------------------------
(last merged pull request is
[#1060](https://github.com/open-source-economics/Tax-Calculator/pull/1060))

**API Changes**
- Rename policy parameters for consistency
  [[#1051](https://github.com/open-source-economics/Tax-Calculator/pull/1051)
  by Martin Holmer]

**New Features**
- Add ability to simulate broader range of refundable CTC reforms
  [[#1055](https://github.com/open-source-economics/Tax-Calculator/pull/1055)
  by Matt Jensen]
- Add more income items into expanded_income variable
  [[#1057](https://github.com/open-source-economics/Tax-Calculator/pull/1057)
  by Martin Holmer]

**Bug Fixes**
- None


2016-11-09 Release 0.7.0
------------------------
(last merged pull request is
[#1044](https://github.com/open-source-economics/Tax-Calculator/pull/1044))

**API Changes**
- Rename and refactor old add_weighted_decile_bins utility function
  [[#1043](https://github.com/open-source-economics/Tax-Calculator/pull/1043)
  by Martin Holmer]

**New Features**
- None

**Bug Fixes**
- Remove unused argument from means_and_comparisons utility function
  [[#1044](https://github.com/open-source-economics/Tax-Calculator/pull/1044)
  by Martin Holmer]


2016-11-09 Release 0.6.9
------------------------
(last merged pull request is
[#1039](https://github.com/open-source-economics/Tax-Calculator/pull/1039))

**API Changes**
- None

**New Features**
- Add calculation of MTR wrt e26270, partnership & S-corp income
  [[#987](https://github.com/open-source-economics/Tax-Calculator/pull/987)
  by Cody Kallen]
- Add utility function that plots marginal tax rates by percentile
  [[#948](https://github.com/open-source-economics/Tax-Calculator/pull/948)
  by Sean Wang]
- Add ability to simulate Trump-style dependent care credit
  [[#999](https://github.com/open-source-economics/Tax-Calculator/pull/999)
  by Anderson Frailey]
- Add ability to simulate Clinton-style NIIT reform
  [[#1012](https://github.com/open-source-economics/Tax-Calculator/pull/1012)
  by Martin Holmer]
- Add ability to simulate Clinton-style CTC expansion
  [[#1039](https://github.com/open-source-economics/Tax-Calculator/pull/1039)
  by Matt Jensen]

**Bug Fixes**
- Fix bug in TaxGains function
  [[#981](https://github.com/open-source-economics/Tax-Calculator/pull/981)
  by Cody Kallen]
- Fix bug in multiyear_diagnostic_table utility function
  [[#988](https://github.com/open-source-economics/Tax-Calculator/pull/988)
  by Matt Jensen]
- Fix AMT bug that ignored value of AMT_CG_rt1 parameter
  [[#1000](https://github.com/open-source-economics/Tax-Calculator/pull/1000)
  by Martin Holmer]
- Fix several other minor AMT CG bugs
  [[#1001](https://github.com/open-source-economics/Tax-Calculator/pull/1001)
  by Martin Holmer]
- Move self-employment tax from income tax total to payroll tax total
  [[#1021](https://github.com/open-source-economics/Tax-Calculator/pull/1021)
  by Martin Holmer]
- Add half of self-employment tax to expanded income
  [[#1032](https://github.com/open-source-economics/Tax-Calculator/pull/1032)
  by Martin Holmer]


2016-10-07 Release 0.6.8
------------------------
(last merged pull request is
[#970](https://github.com/open-source-economics/Tax-Calculator/pull/970))

**API Changes**
- None

**New Features**
- Add ability to simulate reforms that limit benefit of itemized
  deductions
  [[#867](https://github.com/open-source-economics/Tax-Calculator/pull/867)
  by Matt Jensen]
- Add investment income exclusion policy parameter
  [[#972](https://github.com/open-source-economics/Tax-Calculator/pull/972)
  by Cody Kallen]
- Add ability to eliminate differential tax treatment of LTCG+QDIV
  income
  [[#973](https://github.com/open-source-economics/Tax-Calculator/pull/973)
  by Martin Holmer]

**Bug Fixes**
- None


2016-09-29 Release 0.6.7
------------------------
(last merged pull request is
[#945](https://github.com/open-source-economics/Tax-Calculator/pull/945))

**API Changes**
- None

**New Features**
- Add extra income tax brackets and rates
  [[#858](https://github.com/open-source-economics/Tax-Calculator/pull/858),
  Sean Wang]
- Add ability to simulate Fair Share Tax, or Buffet Rule, reforms
  [[#904](https://github.com/open-source-economics/Tax-Calculator/pull/904)
  by Anderson Frailey]
- Add ability to tax pass-through income at different rates
  [[#913](https://github.com/open-source-economics/Tax-Calculator/pull/913)
  by Sean Wang]
- Add itemized-deduction surtax exemption policy parameter
  [[#926](https://github.com/open-source-economics/Tax-Calculator/pull/926)
  by Matt Jensen]
- Add ability to simulate high-AGI surtax reforms
  [[#939](https://github.com/open-source-economics/Tax-Calculator/pull/939)
  by Sean Wang]

**Bug Fixes**
- Correct Net Investment Income Tax (NIIT) calculation
  [[#874](https://github.com/open-source-economics/Tax-Calculator/pull/874)
  by Martin Holmer]
- Correct Schedule R credit calculation
  [[#898](https://github.com/open-source-economics/Tax-Calculator/pull/898)
  by Martin Holmer]
- Remove logic for expired First-Time Homebuyer Credit
  [[#914](https://github.com/open-source-economics/Tax-Calculator/pull/914)
  by Martin Holmer]


2016-08-13 Release 0.6.6
------------------------
(last merged pull request is
[#844](https://github.com/open-source-economics/Tax-Calculator/pull/844))

**API Changes**
- None

**New Features**
- Revise code to use smaller `puf.csv` input file and make changes to
  create that input file
- Remove debugging variables from functions.py reducing execution time
  by 42 percent
  [[#833](https://github.com/open-source-economics/Tax-Calculator/pull/833)]
- Add comments to show one way to use Python debugger to trace
  Tax-Calculator code
  [[#835](https://github.com/open-source-economics/Tax-Calculator/pull/835)]
- Add tests that confirm zeroing-out CALCULATED_VARS at start leaves
  results unchanged
  [[#837](https://github.com/open-source-economics/Tax-Calculator/pull/837)]
- Revise logic used to estimate behavioral responses to policy reforms
  [[#846](https://github.com/open-source-economics/Tax-Calculator/pull/846),
  [#854](https://github.com/open-source-economics/Tax-Calculator/pull/854)
  and
  [#857](https://github.com/open-source-economics/Tax-Calculator/pull/857)]

**Bug Fixes**
- Make 2013-2016 medical deduction threshold for elderly be 7.5% of
  AGI (not 10%)
  [[#839](https://github.com/open-source-economics/Tax-Calculator/pull/839)]
- Fix typo so that two ways of limiting itemized deductions produce
  the same results
  [[#842](https://github.com/open-source-economics/Tax-Calculator/pull/842)]


2016-07-12 Release 0.6.5
------------------------
(last merged pull request is
[#820](https://github.com/open-source-economics/Tax-Calculator/pull/820))

**API Changes**
- None

**New Features**
- Add --exact option to simtax.py and inctax.py scripts
- Add calculation of Schedule R credit
- Remove _cmp variable from functions.py code

**Bug Fixes**
- Fix itemized deduction logic for charity
- Remove Numba dependency


2016-06-17 Release 0.6.4
------------------------
(last merged pull request is
[#794](https://github.com/open-source-economics/Tax-Calculator/pull/794))

**API Changes**
- Create Consumption class used to compute "effective" marginal tax rates

**New Features**
- Revise Behavior class logic
- Add unit tests to increase code coverage to 98 percent
- Add scripts to version and release

**Bug Fixes**
- Test TaxBrain handling of delayed reforms
- Move cmbtp calculation and earnings splitting logic from Records
  class to `puf.csv` file preparation
- Update Numpy and Pandas dependencies to latest versions to avoid a
  bug in the Windows conda package for Pandas 0.16.2


2016-05-09 Release 0.6.3
------------------------
(last merged pull request is
[#727](https://github.com/open-source-economics/Tax-Calculator/pull/727))

**API Changes**
- None

**New Features**
- Add --records option to simtax.py
- Add --csvdump option to inctax.py
- Add three "d" samples to Tax-Calculator versus Internet-TAXSIM comparisons
- Add first set of Tax-Calculator versus TaxBrain comparisons
- Add data and logic to implement EITC age-eligibility rules
- Update and fix 10_minutes_to_Tax-Calculator.ipynb
- Update files in taxcalc/comparison

**Bug Fixes**
- Fix Child Care Expense logic
- Exclude dependents from EITC eligibility


Before Release 0.6.2
--------------------
See commit history for pull requests before
[#650](https://github.com/open-source-economics/Tax-Calculator/pull/650)
