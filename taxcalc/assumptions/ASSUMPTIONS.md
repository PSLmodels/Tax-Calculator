# HOW TO SPECIFY ECONOMIC ASSUMPTIONS IN A JSON ASSUMPTION FILE

There is a way to specify in a text file the collection of economic
assumptions about how individuals and the overall economy respond to a
tax reform.

Here we provide a link to an economic assumptions template file, and
then provide a more general explanation of the structure and syntax of
assumption files.

## Example of an Economic Assumption File

The following example serves as a template:

- [Economic Assumptions Template](economic_assumptions_template.json)

## Structure and Syntax of Assumption Files

The assumption files are JSON files.  JSON, which stands for
JavaScript Object Notation, is an easy way to specify structured
information that is widely used.  Below we provide an abstract example
of a JSON assumption file with some explanation.

Here is an abstract example of an economic assumption file that
consists of several parameters.  The structure of this file is as
follows:

```
{
  "consumption": {
     <parameter_name>: {<calyear>: <parameter-value>}
  },
  "growdiff_baseline": {
  },
  "growdiff_response": {
     <parameter_name>: {<calyear>: <parameter-value>}
  }
}
```

Notice that an assumption file must always contain these top-level keys:
consumption, growdiff_baseline, and growdiff_response.
Any key can have an empty value like the growdiff_baseline key above.
Empty values mean that the default assumption parameter values are
used.

The rules about structuring a non-empty value for a top-level key are
the same as for policy reform files, which are described
[here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/reforms/REFORMS.md#how-to-specify-a-tax-reform-in-a-json-policy-reform-file).
The assumption parameter names recognized by Tax-Calculator, and their
default values, are listed in [this
section](https://PSLmodels.github.io/Tax-Calculator/uguide.html#params)
of the user guide.
