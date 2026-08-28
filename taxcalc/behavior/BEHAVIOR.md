# HOW TO SPECIFY BEHAVIORAL RESPONSES IN A JSON BEHAVIOR FILE

There is a way to specify in a text file the collection of behavioral
response parameters that you want to assume about how tax units
respond to a tax reform.

Here is an [example](behavioral_responses_template.json) of a
behavioral responses file.

Every behavior file is a JSON file.  JSON, which stands for JavaScript
Object Notation, is a widely-used and easy way to specify structured
information.

Notice that a behavior file must always contain **all four** of these
top-level keys: `esf`, `sub`, `inc`, and `cg`.  Unlike the `response`
function in the Python API, which assumes an omitted parameter is zero,
the `tc` command-line interface `--behavior` option rejects a file that
has a missing or extra key.  Specify a parameter as `0.0` to turn off
that response channel.

Also notice that the value of these parameters do not vary from year
to year, and thus, have no time dimension.

The four parameters are:

- `esf`: earnings shift factor, which must be in the [0,1] range.
  
- `sub`: substitution elasticity of taxable income, which must be zero
  or positive.

- `inc`: income elasticity of taxable income, which must be zero or
  negative.

- `cg`: **semi**-elasticity of long-term capital gains, which must be
  zero or negative.  This is not the tax-rate elasticity usually
  reported in the literature; a tax-rate elasticity of -0.792
  corresponds to a `cg` value of about -3.45.

More information about these four parameters, including their exact
definitions, appropriate values, and the response equations in which
they are used, can be found on the [behavior parameters
page](https://taxcalc.pslmodels.org/guide/behavior_params.html) and in
the [`behresp` module API
documentation](https://taxcalc.pslmodels.org/api/behresp.html).
