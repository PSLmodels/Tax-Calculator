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

There are four behavior parameters, none of which has a time
dimension (that is, each is a single value that applies to every year
being analyzed):

`esf`: earnings shift factor, defined as the fraction of the
reform-induced increase (decrease) in employer payroll tax liability
that is shifted to the employee as a decrease (increase) in earnings,
with the remainder shifted to the employee as a decrease (increase) in
nontaxable benefits such as employer-provided health insurance.  Must
be in the [0,1] range; JCT assumes a 0.85 value.  Holding the `esf`
fraction of gross compensation --- earnings plus employer payroll tax
--- fixed in this way is an accounting convention rather than a
behavioral response, so any earnings shift is applied *before* the
three elasticities below are used, and their responses are then layered
on top of it.  The shift is calculated separately for each earner,
because the OASDI payroll tax is capped per person while the HI payroll
tax is uncapped: an earner below the OASDI cap receives a proportional
earnings change, whereas for an earner above the cap the OASDI portion
of the change is a lump sum that leaves their marginal wage unaffected.
See the {doc}`../api/behresp` page for the equations.

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
all four of the `esf`, `sub`, `inc`, and `cg` keys.
