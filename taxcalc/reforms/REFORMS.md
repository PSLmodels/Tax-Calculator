# HOW TO SPECIFY A TAX REFORM IN A JSON POLICY REFORM FILE

A tax reform consists of a collection of reform provisions.  There is
a way to specify in a text file the collection of reform provisions
that make up a reform proposal.  When stored on your local computer,
such reform files can be used to estimate reform effects either by
uploading to the [TaxBrain webapp](http://www.ospc.org/taxbrain/file/)
or by using the `--reform` option of the [Tax-Calculator command-line
tool,
tc](http://open-source-economics.github.io/Tax-Calculator/index.html#cli).

Here we provide links to several reform files that specify historical
reform proposals, and then provide a more general explanation of the
structure and syntax of reform files.

## Tax Reforms Defined Relative to TCJA Policy

Note that the current-law (that is, TCJA) values of each tax policy
parameter are shown in the [Policy Parameters section of the user
documentation](http://open-source-economics.github.io/Tax-Calculator/index.html#pol).

- [Pre-TCJA Policy](2017_law.json)

## Tax Reforms Defined Relative to pre-TCJA Policy

Read the answer to [Question 1 in this
FAQ](https://github.com/open-source-economics/Tax-Calculator/issues/1830)
to see how to use the compound-reform techique to analyze the reforms
in this section.

- [2016 Trump Campaign Tax Plan](Trump2016.json)

- [2016 Clinton Campaign Tax Plan](Clinton2016.json)

- [2016 Ryan-Brady "Better Way" Tax Plan](RyanBrady.json)

- [2017 Trump Administration Tax Plan](Trump2017.json)

- [2017 Brown-Khanna GAIN Act](BrownKhanna.json)

- [2017 Tax Cuts and Jobs Act, House version](TCJA_House.json)

- [2017 Tax Cuts and Jobs Act, Passed House version](TCJA_House_Amended.json)

- [2017 Tax Cuts and Jobs Act, Senate version](TCJA_Senate.json)

- [2017 Tax Cuts and Jobs Act, Passed Senate version](TCJA_Senate_120117.json)

- [2017 Tax Cuts and Jobs Act, Conference bill](TCJA_Reconciliation.json)

## Structure and Syntax of Reform Files

The reform files are JSON files.  JSON, which stands for JavaScript
Object Notation, is an easy and widely used way to specify structured
information.  First we provide an abstract example of a JSON reform
file with some explanation, and then we provide links to a few
hypothetical reform files that illustrate their expressive range.

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
five parameter values for single, married filing joint, married filing
separate, head of household, widow.

The following hypothetical payroll tax reforms, all of which are
defined relative to pre-TCJA policy, illustrate the flexibility that
reform files provide in expressing complex tax reforms.

[Raise OASDI and HI payroll tax rates](ptaxes0.json)

[Raise OASDI maximum taxable earnings](ptaxes1.json)

[Eliminate OASDI maximum taxable earnings](ptaxes2.json)

[Raise Additional Medicare Tax (Form 8959) tax rate and
thresholds and index thresholds](ptaxes3.json)
