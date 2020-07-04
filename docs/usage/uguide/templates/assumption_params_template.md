Assumption parameters
=====================

This section contains documentation of several sets of parameters that characterize responses to a tax reform. Consumption parameters are used to compute marginal tax rates and to compute the consumption value of in-kind benefits. Growdiff parameters are used to specify baseline differences and/or reform responses in the annual rate of growth in economic variables. (Note that behavior parameters used to compute changes in input variables caused by a tax reform in a partial-equilibrium setting are not part of Tax-Calculator, but can be used via the Behavioral-Response `behresp` package in a Python program.)

The assumption parameters control advanced features of Tax-Calculator, so understanding the source code that uses them is essential. Default values of many assumption parameters are zero and are projected into the future at that value, which implies no response to the reform. The benefit value consumption parameters have a default value of one, which implies the consumption value of the in-kind benefits is equal to the government cost of providing the benefits.
