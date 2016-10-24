2015 CSV Output Variables Documentation
=======================================

First a list of output variables that we need in order to conduct
cross-model validation activities and then an example of a small
CSV-formatted output file.

Output Variables List
---------------------

The following table includes the federal tax output variables (in no
particular order) included in CSV-formatted output files.

| Var-name | IRS-form | Form-line | Var-description
| :------- | :------- | :-------- | :--------------
| V01 | - | - | integer RECID for filing unit from input file
| V02 | - | - | calendar year for which tax output is calculated
| V04 | - | - | total income taxes (see NOTE below for details)
| V06 | - | - | total payroll taxes (see NOTE below for details)
| V10 | 1040 | 37 | adjusted gross income
| V12 | 1040 | 20b | social security benefits included in AGI
| V14 | 1040 | 42 | personal exemption after phase-out
| V15 | 1040 | - | p.e. phase-out = 4000 times line6d minus line42
| V17 | 1040 | 40 | itemized deductions after phase-out (zero for non-itemizer)
| V16 | Sch A | - | i. d. phase-out = sum of right-hand lines4-28 minus line29
| V18 | 1040 | 43 | regular taxable income
| V19 | 1040 | 44 | regular tax on regular taxable income
| V26 | 6251 | 28 | AMT taxable income
| V27 | 1040 | 45 | AMT liability
| V22 | 1040 | 52 | child tax credit (adjusted)
| V23 | 1040 | 67 | child tax credit (refunded)
| V24 | 1040 | 49 | credit for child care expenses
| V25 | 1040 | 66a | earned income credit

**NOTE on composition of payroll taxes (V06) and income taxes (V04):**

The total payroll taxes (V06) variable is assumed to include the
following components: (a) employee plus employer share of OASDI FICA
taxes; (b) employee plus employer share of HI FICA taxes; (c)
self-employment tax from Form 1040 line57; and (d) additional Medicare
tax from from Form 1040 line62a or Form 8959 line18.  These payroll
tax components are calculated under the assumption that taxpayer and
spouse, if present, each hold only one wage-or-salary job during the
year so that Form 1040 line71 is always zero, and that employers
(illegally) never withhold for the Additional Medicare Tax so that
Form 8959 line24 is always zero.

The total income taxes (V04) variable is assumed to include all the
Form 1040 components except for the payroll tax components (c) and (d)
defined above.  In other words, on Form 1040 the V04 amount is line63
minus line57 minus line62a.

Example Output File
-------------------

The following output file contains only the variable-name header row
and one filing-unit row.
```
V01,V02,V04,V06,V10,V12,V14,V15,V16,V17,V18,V19,V22,V23,V24,V25,V26,V27
99,2015,4866,2203.20,66440,25040,8000,0,0,0,44590,4866,0,0,0,0,66440,0
```
Note that the ordering of the variables is irrelevant in CSV-formatted
files.
