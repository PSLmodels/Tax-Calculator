Roadmap
=======

Because Tax-Calculator itself does only static analysis of federal
individual income and payroll taxes, it must interact with other
models in order to analyze business taxes or conduct non-static
analysis. These other models typically use Tax-Calculator to estimate
reform-induced changes in after-tax incomes and marginal tax rates,
and then use that information to calculate how other taxes or
non-static behavior cause changes in individual incomes or
expenses. These changes are then fed back to Tax-Calculator so that
individual tax liabilities, as well as aggregate and distribution
results, can be recalculated. All these interactions between
Tax-Calculator and other models are handled by
[Tax-Brain](https://github.com/PSLmodels/Tax-Brain#tax-brain).

The **future development of Tax-Calculator** itself will focus on the
following activities:

* Fix bugs in tax-calculation logic.

* Update existing current-law policy parameter values as they become
  available each year.

* Update filing-unit data used by Tax-Calculator as they become
  available.

* Improve documentation of model logic and data.

* Develop AI-assisted **model-use agent** that allows conversational
  CLI use.

* Develop AI-assisted **structural-enhancement agent** that makes it
  easier to implement (locally and privately) the Python code required
  to simulate a reform not parameterized by existing model parameters.
