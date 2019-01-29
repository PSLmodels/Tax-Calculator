PLANS FOR FUTURE TAX-CALCULATOR DEVELOPMENT
===========================================

Near-Term Development Plans
---------------------------

The main near-term objective is to complete the transformation of
Tax-Calculator into a microsimulation model that conducts only static
analysis of reforms.  This involves the development of other modules
that can be used along with Tax-Calculator to conduct non-static
analysis that generates both aggregate and distributional reform
results.  At least three other modules are being planned:

1. [Partial-equilibrium
behavioral-response](https://github.com/PSLmodels/Behavioral-Responses)
capabilities have been completed,

2. [Business-taxation](https://github.com/PSLmodels/Business-Taxation)
capabilities are being developed that will permit the effects of
reforms in (corporate and pass-through) business taxes to feedback to
Tax-Calculator, and

3. Macro-model capabilities are being planned that will allow
macroeconomic growth feedback to Tax-Calculator.

Once Tax-Calculator can support these other modules in the USA tax
collection of the Policy Simulation Library, it is anticipated that
the public application programming interface (API) of Tax-Calculator
will be stable.

Long-Term Development Plans
---------------------------

In the long-term Tax-Calculator will be enhanced in the following ways:

1. Fix bugs in tax-calculation logic,

2. Add new policy parameters to enable simulation of new reforms,

3. Add historical policy parameter values as they become available,

4. Update input data used by Tax-Calculator as they become available, and

5. Improve user and developer documentation.
