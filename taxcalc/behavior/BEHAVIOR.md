# HOW TO SPECIFY BEHAVIORAL RESPONSES IN A JSON BEHAVIOR FILE

There is a way to specify in a text file the collection of behavioral
response parameters that you want to assume about how tax units
respond to a tax reform.

Here is an [example](behavioral_responses_template.json) of a
behavioral responses file.

Every behavior file is a JSON file.  JSON, which stands for JavaScript
Object Notation, is a widely-used and easy way to specify structured
information.

Notice that a behavior file must always contain these top-level keys:
sub, inc, and cg.  More information about these three elasticities can
be found in [here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py).

Also notice that the value of these elasticities do not vary from year
to year, and thus, have no time dimension.

