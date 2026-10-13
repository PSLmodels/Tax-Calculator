# Tax-Calculator Policy

Documentation of the `taxcalc.policy` module.

## Policy

```python
class Policy(gfactors=None, last_budget_year=LAST_BUDGET_YEAR, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L15)

```text
Policy is a subclass of the abstract Parameters class, and
therefore, inherits its methods (none of which are shown here).

Constructor for the federal tax policy class.

Parameters
----------
gfactors: GrowFactors class instance or None
    containing price inflation rates and wage growth rates used
    to index policy paramaters

last_budget_year: integer
    user-defined last parameter extrapolation year

Raises
------
ValueError:
    if gfactors is not a GrowFactors class instance or None.

Returns
-------
class instance: Policy
```

### Policy.number_of_years

```python
def number_of_years(last_budget_year=LAST_BUDGET_YEAR)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L50)

```text
Static method returns number of policy parameters years given
user-defined last_budget_year.
```

### Policy.read_json_reform

```python
def read_json_reform(obj)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L189)

```text
Return a reform dictionary suitable for use with implement_reform
method generated from the specified JSON object, which can be None or
a string containing a local filename, a URL beginning with 'http'
pointing to a valid JSON file hosted online, or a valid JSON text.
```

### Policy.implement_reform

```python
def implement_reform(self, reform: dict, print_warnings=True, raise_errors=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L198)

```text
Implement reform using a Tax-Calculator-style reform dictionary.
```

### Policy.parameter_list

```python
def parameter_list()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L221)

```text
Returns list of parameter names in the policy_current_law.json file.
```

### Policy.set_rates

```python
def set_rates(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/policy.py#L233)

```text
Initialize policy parameter indexing rates.
```
