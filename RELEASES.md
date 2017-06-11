TAX-CALCULATOR RELEASE HISTORY
==============================
Go
[here](https://github.com/open-source-economics/Tax-Calculator/pulls?q=is%3Apr+is%3Aclosed)
for a complete commit history.

Release 0.9.0 on 2017-??-??
---------------------------
(last merged pull request is
[#xxxx](https://github.com/open-source-economics/Tax-Calculator/pull/xxxx))

**API Changes**
- Initial specification of public API removes several unused utility
  functions and makes private several Tax-Calculator members whose
  only role is to support public members
  [[#1424](https://github.com/open-source-economics/Tax-Calculator/pull/1424)]

**New Features**
- ...

**Bug Fixes**
- None

Release 0.8.5 on 2017-06-08
---------------------------
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
  [[#1376](https://github.com/open-source-economics/Tax-Calculator/pull/1376)
  , [#1383](https://github.com/open-source-economics/Tax-Calculator/pull/1383)
  , and
  [#1385](https://github.com/open-source-economics/Tax-Calculator/pull/1385)
  by Hank Doupe]
- Add separate ceiling for each itemized deduction parameter
  [[#1385](https://github.com/open-source-economics/Tax-Calculator/pull/1385)
  by Hank Doupe]


**Bug Fixes**
- Fix bug in add_weighted_income_bins utility function
  [[#1387](https://github.com/open-source-economics/Tax-Calculator/pull/1387)
  by Martin Holmer]


Release 0.8.4 on 2017-05-12
---------------------------
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


Release 0.8.3 on 2017-05-01
---------------------------
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


Release 0.8.2 on 2017-04-13
---------------------------
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


Release 0.8.1 on 2017-04-13
---------------------------
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


Release 0.8.0 on 2017-03-24
---------------------------
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


Release 0.7.9 on 2017-03-08
---------------------------
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


Release 0.7.8 on 2017-03-01
---------------------------
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


Release 0.7.7 on 2017-02-16
---------------------------
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


Release 0.7.6 on 2017-02-15
---------------------------
(last merged pull request is
[#1192](https://github.com/open-source-economics/Tax-Calculator/pull/1192))

**API Changes**
- Add Stage3 adjustment ratios to target IRS-SOI data on the
  distribution of interest income
  [[#1193](https://github.com/open-source-economics/Tax-Calculator/pull/1193)
  by Anderson Frailey]

**New Features**
- Add to diagnostic table the number of tax units with non-positive
  income and combined tax liability
  [[#1170](https://github.com/open-source-economics/Tax-Calculator/pull/1170)
  by Anderson Frailey]

**Bug Fixes**
- Correct Policy wage growth rates to agree with CBO projection
  [[#1171](https://github.com/open-source-economics/Tax-Calculator/pull/1171)
  by Martin Holmer]


Release 0.7.5 on 2017-01-31
---------------------------
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


Release 0.7.4 on 2017-01-24
---------------------------
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


Release 0.7.3 on 2017-01-24
---------------------------
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


Release 0.7.2 on 2016-12-05
---------------------------
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

**Bug Fixes**
- None


Release 0.7.1 on 2016-11-15
---------------------------
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


Release 0.7.0 on 2016-11-09
---------------------------
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


Release 0.6.9 on 2016-11-09
---------------------------
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


Release 0.6.8 on 2016-10-07
---------------------------
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


Release 0.6.7 on 2016-09-29
---------------------------
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


Release 0.6.6 on 2016-08-13
---------------------------
(last merged pull request is
[#844](https://github.com/open-source-economics/Tax-Calculator/pull/844))

**API Changes**
- None

**New Features**
- Revise code to use smaller puf.csv input file and make changes to
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


Release 0.6.5 on 2016-07-12
---------------------------
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


Release 0.6.4 on 2016-06-17
---------------------------
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
  class to puf.csv file preparation
- Update Numpy and Pandas dependencies to latest versions to avoid a
  bug in the Windows conda package for Pandas 0.16.2


Release 0.6.3 on 2016-05-09
---------------------------
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


Release 0.6.2 and before
------------------------
See commit history for pull requests before
[#650](https://github.com/open-source-economics/Tax-Calculator/pull/650)
