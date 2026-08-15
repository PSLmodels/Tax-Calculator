Behavior parameters
===================

Note that logic that uses assumed behavior parameters to compute
changes in input variables caused by a tax reform in a
partial-equilibrium setting is contained in the `response` function in
the Tax-Calculator `behresp` module.  The complete documentation of
that function, including the response equations and the way responses
are applied to input variables, is on the {doc}`../api/behresp` page.

By default Tax-Calculator assumes no behavioral responses to a tax
reform, which is the same as saying the behavior parameters (or
elasticities) are assumed to be zero by default.  The elasticities can
be set to non-zero values in a JSON file that is formatted like
[this](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/behavior/behavioral_responses_template.json).

There are three behavior parameters, none of which has a time
dimension (that is, each is a single value that applies to every year
being analyzed):

`sub`: substitution elasticity of taxable income, defined as the
proportional change in taxable income divided by the proportional
change in the marginal net-of-tax rate (1-MTR) on taxpayer earnings
caused by the reform.  Must be zero or positive.  Empirical estimates
in the literature are typically in the 0.1 to 0.4 range.

`inc`: income elasticity of taxable income, defined as the dollar
change in taxable income divided by the dollar change in after-tax
income caused by the reform.  Must be zero or negative.  Values used
in practice are typically small in absolute value, in the 0.0 to -0.2
range.

`cg`: **semi**-elasticity of long-term capital gains, defined as the
change in the logarithm of long-term capital gains divided by the
change in the marginal tax rate on long-term capital gains caused by
the reform.  Must be zero or negative.  Be aware that this is not the
tax-rate elasticity usually reported in the literature, and that the
two differ by roughly a factor of four: the JCT-CBO tax-rate
elasticity estimate of -0.792 corresponds to a `cg` semi-elasticity of
about -3.45.  Specifying `cg` equal to a published tax-rate elasticity
is a common mistake that generates a much smaller capital-gains
response than intended.  See the {doc}`../api/behresp` page for the
details of this conversion.

When the elasticities are used in a Python program, they are supplied
in a dictionary passed to the `response` function, and any omitted
elasticity is assumed to be zero.  When they are used with the `tc`
command-line interface `--behavior` option, the JSON file must contain
all three of the `sub`, `inc`, and `cg` keys.
