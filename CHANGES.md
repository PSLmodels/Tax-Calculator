TAX-CALCULATOR CHANGE HISTORY
=============================


Changes in release 0.24.0 on 2018-12-14
---------------------------------------

- Make taxcalc packages available for Python 3.7 as well as for Python 3.6.


Changes in release 0.23.4 on 2018-12-13
---------------------------------------

- Fix obscure bug regarding rules for determining eligibility for the child AMT exemption that was discovered during recent validation work.


Changes in release 0.23.3 on 2018-12-05
---------------------------------------

- Fix minor error in calculation of AMT for those in the 18 to 23 age range.  This changes estimated aggregate income tax liability in 2018 by only 0.06 of one percent.


Changes in release 0.23.2 on 2018-11-22
---------------------------------------

- Make create_diagnostic_table utility function work better when using the Behavioral-Responses behresp package.  This is illustrated in [cookbook recipe
2](https://PSLmodels.github.io/Tax-Calculator/cookbook.html#recipe02).


Changes in release 0.23.1 on 2018-11-20
---------------------------------------

- Add ability to pass pandas DataFrame as the adjust_ratios argument to Records class constructor.  This makes the adjust_ratios argument like the data and weights arguments in this respect.


Changes in release 0.23.0 on 2018-11-13
---------------------------------------

- Remove confusing filer variable from list of usable input variables.  This will generate a message that Tax-Calculator is ignoring the filer variable as long as input data contain a variable with that name.

- Remove useless start_year and num_years arguments of constructor for the Policy, Consumption, and GrowDiff classes.

- Add deprecated warning to Behavior class constructor and documentation because Behavior class will be removed from Tax-Calculator in the near future.

- Revise [cookbook recipe 2](https://PSLmodels.github.io/Tax-Calculator/cookbook.html#recipe02) to show use of new Behavioral-Responses behresp package as alternative to deprecated Behavior class.


Changes in release 0.22.2 on 2018-10-26
---------------------------------------

- Add _EITC_basic_frac policy parameter so that an Earned and Basic Income Tax Credit (EBITC) reform can be analyzed.


Changes in release 0.22.1 on 2018-10-25
---------------------------------------

- Add Records class read_cps_data static method to make it easier to test other models in the Policy Simulation Library collection of USA tax models.


Changes in release 0.22.0 on 2018-10-24
---------------------------------------

- Refactor tbi functions so that other models in the Policy Simulation Library (PSL) collection of USA tax models can easily produce the tables expected by TaxBrain.

- Add ability to read online JSON reform/assumption files located at URLs beginning with 'http'.  This is illustrated in [cookbook recipe 1](https://PSLmodels.github.io/Tax-Calculator/cookbook.html#recipe01).

- Fix bug in create_difference_table utility function that affected accuracy of the ubi variable and benefit-total variables in the difference table.


Changes in release 0.21.0 on 2018-09-11
---------------------------------------

- Require Python 3.6 to run Tax-Calculator source code or conda package.  This change is being made because pandas is dropping development for Python 2.7 beginning in 2019.


Changes in release 0.20.3 on 2018-09-06
---------------------------------------

- Incorporate new PUF input data that include imputed values of itemizeable expenses for non-itemizers.  This enables simulation of reforms that lower the standard deduction below where is was before TCJA when using PUF.

- Incorporate new PUF input data that include imputed values of pension contributions.  This increases payroll tax revenue because (unlike the income tax) it taxes pension contributions when using PUF.

- Fix other-benefits values in CPS input data.  This is relevant primarily for users simulating the repeal of other benefits as part a UBI reform, but it also affects expanded income in the distribution tables when using CPS.

- **LAST RELEASE COMPATIBLE WITH PYTHON 2.7**


Changes in releases before 0.20.3
---------------------------------
See more technical descriptions of changes in releases before 0.20.3
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/RELEASES.md#2018-08-10-release-0202).
