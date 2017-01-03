Cross-Checking Reform Results from TaxBrain and Tax-Calculator
==============================================================

The contents of this taxcalc/taxbrain directory are for use by the
core development team only.  The purpose of the cross-checking is to
test that Tax-Calculator produces essentially the same reform results
when accessed in two different ways: (1) via the TaxBrain file-upload
web page <http://www.ospc.org/taxbrain/file/> and (2) via the taxcalc
package running on a local computer.

The contents of this directory include several JSON reform files used
in the cross-checking, which should be done immediately after each
TaxBrain upgrade to a new Tax-Calculator release.

Here is an example that shows how to generate Tax-Calculator results
on a local computer after copying the `puf.csv` file to the
taxcalc/taxbrain directory:

```
$ cat file0.json
{
    // 2022 RESULTS from taxcalc-inctax and taxbrain-upload version 0.7.3
    // INCOME TAX ($B)   1711.31            1692.2     <-- diff
    // PAYROLL TAX ($B)  1485.37            1485.3     <-- same
    "policy": {
        "_SS_Earnings_c": // social security (OASDI) maximum taxable earnings
        {"2018": [400000],
         "2019": [500000],
         "2020": [600000]
        },
        "_II_em": // personal exemption amount
        {"2018": [8000]
        }
    },
    "behavior": {
    },
    "consumption": {
    },
    "growth": {
    }
}

$ python ../../inctax.py puf.csv 2022 --blowup --weights --reform file0.json
You loaded data for 2009.
Your data have been extrapolated to 2022.

$ awk '{w=$29;i+=$4*w;p+=$6*w}END{print i*1e-9,p*1e-9}' puf-22.out-inctax-file0
1711.31 1485.37
```
