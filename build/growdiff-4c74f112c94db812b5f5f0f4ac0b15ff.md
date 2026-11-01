# Tax-Calculator GrowDiff

Documentation of the `taxcalc.growdiff` module.

## GrowDiff

```python
class GrowDiff(last_budget_year=Policy.LAST_BUDGET_YEAR)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L14)

```text
GrowDiff is a subclass of the abstract Parameters class, and
therefore, inherits its methods (none of which are shown here).

Constructor for GrowDiff class.

Parameters
----------
last_budget_year: integer
    user-defined last parameter extrapolation year

Returns
-------
class instance: GrowDiff
```

### GrowDiff.read_json_update

```python
def read_json_update(obj, topkey)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L41)

```text
Return a revision dictionary suitable for use with update_growdiff
method generated from the specified JSON object, which can be None or
a string containing a local filename, a URL beginning with 'http'
pointing to a valid JSON file hosted online, or a valid JSON text.
```

### GrowDiff.update_growdiff

```python
def update_growdiff(self, revision, print_warnings=True, raise_errors=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L51)

```text
Update growdiff default values using specified revision dictionary.
See Parameters._update for argument documentation and details about
the expected structure of the revision dictionary.
```

### GrowDiff.has_any_response

```python
def has_any_response(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L60)

```text
Returns true if any parameter is non-zero for any year;
returns false if all parameters are zero in all years.
```

### GrowDiff.apply_to

```python
def apply_to(self, growfactors)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L73)

```text
Apply updated GrowDiff values to specified GrowFactors instance.
```

### GrowDiff.set_rates

```python
def set_rates(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growdiff.py#L85)

```text
GrowDiff class has no parameter indexing rates.
```
