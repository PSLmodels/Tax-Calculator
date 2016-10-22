# HOW TO SPECIFY TAX REFORMS

First an example of a complex tax reform, then links to reform files
that specify individual reform provisions.  These reform provisions
can be combined to construct more complex tax reform proposals.

## Example Reform File

Here is an example of a tax reform proposal that consists of several
reform provisions.

```
// Example of a reform file suitable for Policy read_json_reform_file function.
// This JSON file can contain any number of trailing //-style comments, which
// will be removed before the contents are converted from JSON to a dictionary.
// The primary keys are policy parameters and secondary keys are years.
// Both the primary and secondary key values must be enclosed in quotes (").
// Boolean variables are specified as true or false (no quotes; all lowercase).
{
    "_AMT_tthd": // AMT taxinc threshold separating the two AMT tax brackets
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
}
```

## Example Reform Provisions

These are organized in the order that policy parameters are presented
on the [TaxBrain webpage](http://www.ospc.org/taxbrain/).

### Payroll Taxes



### Social Security Taxability



### Adjustments



### Exemptions



### Standard Deduction



### Personal Refundable Credit



### Itemized Deductions



### Regular Taxes



### Alternative Minimum Tax



### Nonrefundable Credits



### Other Taxes



### Refundable Credits


