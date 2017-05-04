# HOW TO SPECIFY ECONOMIC RESPONSES IN A RESPONSE ASSUMPTION FILE

There is a way to specify in a text file the collection of response
assumptions that specify the nature of the non-static reform analysis
being assumed.  When stored on your local computer, such response
assumption files can be used in non-static analysis of a tax reform
either by uploading to the [TaxBrain
webapp](http://www.ospc.org/taxbrain/file/) or by using the `--assump`
option of the [tc
CLI](http://open-source-economics.github.io/Tax-Calculator/index.html#cli)
(command-line interface) to Tax-Calculator.

Here we provide links to examples of response assumption files, and
then provide a more general explanation of the structure and syntax of
assumption files.

## Examples of Response Assumption Files

The following examples have been specified in response assumption files:

- [Response Template]()

## Structure and Syntax of Assumption Files

The assumption files are JSON files.  JSON, which stands for
JavaScript Object Notation, is an easy way to specify structured
information that is widely used.  Below we provide an abstract example
of a JSON assumption file with some explanation.

Here is an abstract example of a response assumption file that
consists of several response parameters.  The structure of this file
is as follows:

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
  }
}
```

Notice that an assumption file must always contain these top-level
keys: consumption, behavior, growdiff_baseline and growdiff_response.
But any key can have an empty value like the growdiff_baseline key
above.  Empty values mean no responses, so an assumption file with
empty values for all top-level keys implies no responses of any type,
which implies static analysis of a tax reform.

The rules about structuring a non-empty value for a top-level key are
the same as for policy reform files, which are described
[here](../reforms/REFORMS.md).  The response parameter names
recognized by Tax-Calculator are listed in [this
section](http://open-source-economics.github.io/Tax-Calculator/index.html#params)
of the user documentation.
