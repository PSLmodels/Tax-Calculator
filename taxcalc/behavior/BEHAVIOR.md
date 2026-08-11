# HOW TO SPECIFY BEHAVIORAL RESPONSES IN A JSON BEHAVIOR FILE

There is a way to specify in a text file the collection of behavioral
response elasticities that you want to assume about how individuals
respond to a tax reform.

Here is an [example](behavioral_response_template.json) of a
behavioral responses file.

Every behavior file is a JSON file.  JSON, which stands for JavaScript
Object Notation, is an easy way to specify structured information that
is widely used.

Notice that a behavior file must always contain these top-level keys:
sub, inc, and cg.  More information about these three elasticities can
be found in [here](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behresp.py).

Also notice that the value of these three elasticities do not vary
from year to year, and thus, have no time dimension.

