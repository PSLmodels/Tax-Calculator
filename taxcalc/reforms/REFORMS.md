# HOW TO SPECIFY TAX REFORMS

First an example of a complex tax reform, then links to reform files
that specify individual reform provisions.  These reform provisions
can be combined to construct more complex tax reform proposals that
are stored as text files on your local computer.  Such reform
proposals can then be uploaded to the [TaxBrain
webapp](http://www.ospc.org/taxbrain/file/) (or used on your local
computer with the `--reform` option to the `inctax.py` command-line
interface to Tax-Calculator) to estimate reform effects.

## Example JSON Reform File

Here is an abstract example of a tax reform proposal that consists of
several reform provisions.  The structure of this file is as follows:

```
{
  "policy": {
     <parameter_name>: {<calyear>: <parameter-value>,
                        ...,
                        <calyear>: <parameter-value>},
     <parameter_name>: {<calyear>: <parameter-value>},
     ...,
     <parameter_name>: {<calyear>: <parameter-value>,
                        ...,
                        <calyear>: <parameter-value>}
  }
}
```

Notice each pair of reform provision is separated by commas.
Each reform provision may have one or multiple year-value pairs.
Also, the <parameter_name> and <calyear> must be enclosed in quotes (").
The <parameter_value> is enclosed in single brackets when
the <parameter_value> is a scalar and enclosed in double brackets when
the <parameter_value> is a vector.  The most common vector of values
is one that varies by filing status (MARS) with the vector containing
six parameter values for single, married filing joint, married filing
separate, head of household, widow, separate.

A concrete example of a JSON reform file characterizes the 2016 Trump
Campaign Tax Plan is [here](Trump2016.json).

## Example Policy Reform Provisions

These are organized in the order that policy parameters are presented
on the [TaxBrain webpage](http://www.ospc.org/taxbrain/).  They can be
copied and pasted into a file and then edited in order to represent a
complex reform proposal.

The value of each of these policy parameters under current law is
shown in [this JSON file](../current_law_policy.json).

### Payroll Taxes

[Raise OASDI and HI payroll tax rates](ptaxes0.json)

[Raise OASDI maximum taxable earnings](ptaxes1.json)

[Eliminate OASDI maximum taxable earnings](ptaxes2.json)

[Raise Additional Medicare Tax (Form 8959) tax rate and
thresholds](ptaxes3.json)

### Social Security Taxability

Links will be added here.

### Adjustments

[Specify AGI exclusion of some fraction of investment
income](adjust0.json)

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

## Example Behavioral-Response Assumptions

The definition of each of behavioral-response parameter is shown in
[this JSON file](../behavior.json).

A link will be added here.

## Example Consumption-Response Assumptions

The definition of each of consumption-response parameter (used in
marginal tax rate calculations) is shown in [this JSON
file](../consumption.json).

A link will be added here.

## Example Growth-Response Assumptions

The definition of each of growth-response parameter is shown in [this
JSON file](../growth.json).

A link will be added here.
