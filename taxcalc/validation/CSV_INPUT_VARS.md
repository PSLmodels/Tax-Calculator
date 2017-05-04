CSV Input Variables
===================

This document describes CSV-formatted files that can be used as input
in the validation of Tax-Calculator.  These input files are used with
the tc CLI to Tax-Calculator to produce output files as described in
the [tc CLI section of the user
documentation](../../docs/index.html#cli).

Input Variables Documentation
-----------------------------

A list of all the input variables Tax-Calculator can use in its
calculations is available in the [Input Variables section of the user
documentation](../../docs/index.html#input).

Sample Input File
-----------------

The following input file contains only 24 of the input variables
listed above (all others are assumed to have a value of zero) and
contains only the variable-name header row and three filing-unit rows.

```
e00200p,XTOT,e00200s,e00650,e01700,e18500,EIC,RECID,p22250,e00300,e00200,age_head,f2441,age_spouse,n24,p23250,e00600,e18400,FLPDYR,e02400,e02300,MARS,e32800,e19200
8200.0,2,6200.0,1000.0,16000.0,6400.0,0,1,5000.0,7000.0,14400.0,70,0,50,0,-5000.0,1000.0,25600.0,2015,50000.0,3000.0,2,0.0,5000.0
19200.0,2,1700.0,2000.0,28000.0,3477.0,0,2,4000.0,3000.0,20900.0,70,0,50,0,2000.0,2000.0,10430.0,2015,14000.0,3000.0,2,0.0,18543.0
17300.0,2,17800.0,7000.0,12000.0,0.0,0,3,-1000.0,1000.0,35100.0,70,0,50,0,3000.0,7000.0,38408.0,2015,40000.0,2000.0,2,0.0,8642.0
```
