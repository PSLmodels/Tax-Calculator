Cross-Checking Reform Results from TaxBrain
===========================================

The contents of this taxcalc/taxbrain directory are for use by the
core development team only and require software that is not described
elsewhere.  The purpose of the capabilities in this directory is to
test that Tax-Calculator produces essentially the same reform results
when accessed in two different ways: (1) via the TaxBrain webapp
running in the cloud and (2) via the taxcalc package running on this
computer.


Software and Data Requirements
------------------------------

In order to execute the ```reforms.py``` script in this directory, you
need to have the Python ```selenium``` package and the Python
```pyperclip``` package installed on your local computer.  Also, you
need the Chrome browser installed on you local computer.  The
```reforms.py``` script looks in the top directory of your local code
tree (the directory above taxcalc) for two things: the
selenium-compatible ```chromedriver``` program that automates the
manipulation of the TaxBrain webapp and the ```puf.csv``` data file
that is read by the taxcalc package.


Getting Started
---------------

Look at the help for the ```make_reforms.py``` and ```reforms.py```
scripts by executing the following commands:

```
$ python make_reforms.py --help
```

and

```
$ python reforms.py --help
```
