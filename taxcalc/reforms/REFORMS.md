# HOW TO SPECIFY TAX REFORMS

First an example of a complex tax reform, then links to reform files
that specify individual reform provisions.  These reform provisions
can be combined to construct more complex tax reform proposals that
are stored as text files on your local computer.  Such reform
proposals can then be uploaded to the [TaxBrain
webapp](http://www.ospc.org/taxbrain/file/) (or used on your local
computer) to estimate reform effects.

## Example Reform File

Here is an example of a tax reform proposal that consists of several
reform provisions.  The structure of this file is as follows:

```
{
  "policy": {
     <parameter_name>: {<calyear>: <parameter-value>,
                        ...
                        <calyear>: <parameter-value>},
     <parameter_name>: {<calyear>: <parameter-value>},
     ...
     <parameter_name>: {<calyear>: <parameter-value>,
                        ...
                        <calyear>: <parameter-value>}
  },
  "behavior": {
     <parameter_name>: {<calyear>: <parameter-value>},
     ...
     <parameter_name>: {<calyear>: <parameter-value>}
  },
  "growth": {
     <parameter_name>: {<calyear>: <parameter-value>}
  },
  "consumption": {
     <parameter_name>: {<calyear>: <parameter-value>}
  }
```

Notice each reform provision (except the last one) must end in a
comma.  Each reform provision may have one or multiple year-value
pairs.  Also, the <parameter_name> and <calyear> must be enclosed in
quotes (").  The <parameter_value> is enclosed in single brackets when
the <parameter_value> is a scalar and enclosed in double brackets when
the <parameter_value> is a vector.  The most common vector of values
is one that varies by filing status (MARS) with the vector containing
six parameter values for single, married filing joint, married filing
separate, head of household, widow, separate.

```
// Example of a reform file suitable for local use or uploading to TaxBrain.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// Within each "policy", "behavior", "growth", and "consumption" object, the
// primary keys are parameters and secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
  "policy": {
    "param_code": {
        "ALD_Investment_ec_base_code": "e00300 + e00650 + p23250"
    },
    "_ALD_Investment_ec_base_code_active":
    {"2016": [true]
    },
    "_AMT_brk1": // top of first AMT tax bracket
    {"2015": [200000],
     "2017": [300000]
    },
    "_EITC_c": // maximum EITC amount by number of qualifying kids (0,1,2,3+)
    {"2016": [[ 900, 5000,  8000,  9000]],
     "2019": [[1200, 7000, 10000, 12000]]
    },
    "_II_em": // personal exemption amount (see indexing changes below)
    {"2016": [6000],
     "2018": [7500],
     "2020": [9000]
    },
    "_II_em_cpi": // personal exemption amount indexing status
    {"2016": false, // values in future years are same as this year value
     "2018": true   // values in future years indexed with this year as base
    },
    "_SS_Earnings_c": // social security (OASDI) maximum taxable earnings
    {"2016": [300000],
     "2018": [500000],
     "2020": [700000]
    },
    "_AMT_em_cpi": // AMT exemption amount indexing status
    {"2017": false, // values in future years are same as this year value
     "2020": true   // values in future years indexed with this year as base
    }
  },
  "behavior": {
  },
  "growth": {
  },
  "consumption": {
  }
}
```

## Example Reform Provisions

These are organized in the order that policy parameters are presented
on the [TaxBrain webpage](http://www.ospc.org/taxbrain/).  They can be
copied and pasted into a file and then edited in order to represent a
complex reform proposal.

The value of each of these policy parameters under current law is
shown in [this JSON file](../current_law_policy.json).

### Payroll Taxes

[Raise OASDI and HI payroll tax rates](ptaxes0.txt)

[Raise OASDI maximum taxable earnings](ptaxes1.txt)

[Eliminate OASDI maximum taxable earnings](ptaxes2.txt)

[Raise Additional Medicare Tax (Form 8959) tax rate and
thresholds](ptaxes3.txt)

### Social Security Taxability

Links will be added here.

### Adjustments

[Specify AGI exclusion of some fraction of investment
income](adjust0.txt)

Other links will be added here.

### Exemptions

Links will be added here.

### Standard Deduction

Links will be added here.

### Personal Refundable Credit

Links will be added here.

### Itemized Deductions

Links will be added here.

### Regular Taxes

Links will be added here.

### Alternative Minimum Tax

Links will be added here.

### Nonrefundable Credits

Links will be added here.

### Other Taxes

Links will be added here.

### Refundable Credits

Links will be added here.
