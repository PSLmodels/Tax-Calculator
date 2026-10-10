# Tax-Calculator Consumption

Documentation of the `taxcalc.consumption` module.

## Consumption

```python
class Consumption(last_budget_year=Policy.LAST_BUDGET_YEAR)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L14)

```text
Consumption is a subclass of the abstract Parameters class, and
therefore, inherits its methods (none of which are shown here).

Constructor for Consumption class.

Parameters
----------
last_budget_year: integer
    user-defined last parameter extrapolation year

Returns
-------
class instance: Consumption
```

### Consumption.read_json_update

```python
def read_json_update(obj)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L41)

```text
Return a revision dictionary suitable for use with update_consumption
method derived from the specified JSON object, which can be None or
a string containing a local filename, a URL beginning with 'http'
pointing to a valid JSON file hosted online, or a valid JSON text.
```

### Consumption.update_consumption

```python
def update_consumption(self, revision, print_warnings=True, raise_errors=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L50)

```text
Update consumption default values using specified revision dictionary.
See Parameters._update for argument documentation and details about
the expected structure of the revision dictionary.
```

### Consumption.has_response

```python
def has_response(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L63)

```text
Return true if any MPC parameters are positive for current_year or
if any BEN value parameters are less than one for current_year;
return false if all MPC parameters are zero and all BEN value
parameters are one
```

### Consumption.response

```python
def response(self, records, income_change)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L78)

```text
Changes consumption-related records variables given income_change
and the current values of the MPC consumption parameters
```

### Consumption.benval_params

```python
def benval_params(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L90)

```text
Returns list of BEN_*_value parameter values
```

### Consumption.set_rates

```python
def set_rates(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/consumption.py#L97)

```text
Consumption class has no parameter indexing rates.
```
