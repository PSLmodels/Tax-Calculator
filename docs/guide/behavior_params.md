Behavior parameters
===================

Note that logic that uses assumed behavior parameters to compute
changes in input variables caused by a tax reform in a
partial-equilibrium setting is not part of Tax-Calculator.  The
[`response`
function](https://github.com/PSLmodels/Behavioral-Responses/blob/232abc1e6b9f0a2b2f224ad887af3c19019d28d3/behresp/behavior.py#L13-L50)
in the PSLmodels Behavioral-Responses `behresp` package contains that
logic.

By default Tax-Calculator assumes no behavioral responses to a tax
reform, which is the same as saying the behavior parameters (or
elasticities) are assumed to be zero by default.  The elasticities can
be set to non-zero values in a JSON file that is formatted like
[this](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behavior/behavioral_response_template.json)).
