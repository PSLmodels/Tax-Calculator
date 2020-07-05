Upgrading to Tax-Calculator 2.0
===============================

Tax-Calculator version 2.0 (and higher) is incompatible with earlier
versions.  The tax logic is unchanged, but 2.0 introduces a simplified
and standardized way of specifying tax reforms (or economic assumption
changes).  This note explains what you have to do in order to use
Tax-Calculator version 2.0 and higher.

What you need to do is change the way you specify tax policy reforms.
Obviously, you need to do this only for reforms you want to analyze
using Tax-Calculator 2.0 and higher.

The details of what to do depend on whether you are in the habit of
specifying reforms in JSON files (as demonstrated in the [user
guide](https://PSLmodels.github.io/Tax-Calculator/index.html) and
[cookbook](https://PSLmodels.github.io/Tax-Calculator/cookbook.html))
or whether you take a low-level approach and specify reforms as Python
dictionaries directly in your Python scripts (as done in hundreds of
Tax-Calculator tests).

In both cases you need to do the following:

1. Remove the leading underscore character from each parameter name.

2. Remove the brackets around the value of scalar parameters (i.e.,
   those that do not vary by filing-unit type, number of EITC-eligible
   children, or type of itemized deduction, and therefore, are just a
   single value in any year).

3. Remove **one** of the double set of brackets around the values of
   vector parameters(i.e., those that are not scalar parameters).
   This will leave vector parameter values enclosed in just one pair
   of brackets.

4. Only if you are changing whether a parameter is (wage or price)
   indexed for inflation, you need to change the trailing `_cpi`
   characters to be `-indexed` (making sure to use a dash and not an
   underscore).

5. Only if you are changing CPI offset policy, you need to change the
   old parameter name `_cpi_offset` to `CPI_offset`.

That is all that needs to be done to convert JSON reform (or
assumption) files so that they work with Tax-Calculator 2.0 and
higher.  (If you have many JSON reform files that you want to convert,
the first three steps may be able to be automated using the
`Tax-Calculator/new_json.py` script, but be sure to read the short
script before using it.  If your JSON reform files are not formatted
in the way extected by the `new_json.py` script, then make the changes
in the above steps by hand editing each JSON file.)

If you have specified reforms (or changes in economic assumption
parameters) directly in your Python scripts using dictionaries, then
there is another set of changes you need to make to each of those
dictionaries.  In older versions of Tax-Calcualtor, each reform
dictionary was structured using a `year : param : value` format.
Here is an example of the old format after making the changes
listed above:

```
reform = {
   2020: {
       'SS_Earnings_c': 200000,
   2021: {
       'SS_Earnings_c': 300000,
       'SS_Earnings_c-indexed': False
   },
   2022: {
       'STD': [14000, 28000, 14000, 21000, 28000]
   }
}
```

Notice that the primary keys in the above dictionary are years and the
secondary keys are parameter names.  Beginning with Tax-Calculator
2.0, that order is reversed making the new `param : year : value`
format consistent with the format of the JSON reform files.

So, the above dictionary needs to be converted (by hand editing) to
the following:

```
reform = {
   'SS_Earnings_c': {2020: 200000,
                     2021: 300000},
   'SS_Earnings_c-indexed': {2021: False},
   'STD': {2022: [14000, 28000, 14000, 21000, 28000]}
}
```

If you have any problems or questions converting your reforms for
use with Tax-Calculator 2.0, please raise an issue
[here](https://github.com/PSLmodels/Tax-Calculator/issues).
