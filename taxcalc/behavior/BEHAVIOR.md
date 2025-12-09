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
be found in [here](https://github.com/PSLmodels/Behavioral-Responses/blob/232abc1e6b9f0a2b2f224ad887af3c19019d28d3/behresp/behavior.py#L13-L50).

Also notice that the value of these three elasticities do not vary
from year to year, and thus, have no time dimension.

