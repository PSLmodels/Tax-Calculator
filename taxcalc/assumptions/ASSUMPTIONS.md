# HOW TO SPECIFY ECONOMIC ASSUMPTIONS IN A JSON ASSUMPTION FILE

There is a way to specify in a text file the collection of economic
assumptions about how individuals and the overall economy respond to a
tax reform.  When stored on your local computer, such economic
assumption files can be used in the analysis of a tax reform
either by uploading to the [TaxBrain
webapp](http://www.ospc.org/taxbrain/file/) or by using the `--assump`
option of the [tc
CLI](http://open-source-economics.github.io/Tax-Calculator/index.html#cli)
(command-line interface) to Tax-Calculator.

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
  "behavior": {
     <parameter_name>: {<calyear>: <parameter-value>,
     <parameter_name>: {<calyear>: <parameter-value>},
     ...,
     <parameter_name>: {<calyear>: <parameter-value>,
                        ...,
                        <calyear>: <parameter-value>}
  },
  "growdiff_baseline": {
  },
  "growdiff_response": {
     <parameter_name>: {<calyear>: <parameter-value>}
  },
  "growmodels": {
     <parameter_name>: {<calyear>: <parameter-value>}
  }
}
```

Notice that an assumption file must always contain these top-level keys:
consumption, behavior, growdiff_baseline, growdiff_response and growmodel.
Any key can have an empty value like the growdiff_baseline key above.
Empty values mean that the default assumption parameter values are
used.

Including just these four key:value pairs in the assumption file indicates
that the GrowModel is inactive.  To activate the GrowModel, simply add a
fifth key:value pair like this when you want to use the default parameter
values of the GrowModel:
```
  ,
  "growmodel": {
  } 
```
or add fifth key:value pair like this when you want to customize the
GrowModel parameter values:
```
  ,
  "growmodel": {
     <parameter_name>: {<calyear>: <parameter-value>}
  } 
```

The rules about structuring a non-empty value for a top-level key are
the same as for policy reform files, which are described
[here](../reforms/REFORMS.md).  The assumption parameter names
recognized by Tax-Calculator, and there default values, are listed in
[this
section](http://open-source-economics.github.io/Tax-Calculator/index.html#params)
of the user documentation.
