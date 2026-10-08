# Tax-Calculator GrowFactors

Documentation of the `taxcalc.growfactors` module.

## GrowFactors

```python
class GrowFactors(growfactors_filename=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L14)

```text
Constructor for the GrowFactors class.

Parameters
----------
growfactors_filename: None or string
    string is path to the CSV file in which grow factors reside;
    default value of None uses file containing puf/cps grow factors.

Raises
------
ValueError:
    if growfactors_filename is neither None or a string.
    if growfactors_filename string points to a non-existent file.

Returns
-------
class instance: GrowFactors

Notes
-----
Typical usage is "gfactor = GrowFactors()", which produces an object
containing baseline growth factors in the GrowFactors.FILE_NAME file,
which is used to extrapolate cps and puf data from the taxdata repository,
and is used to index policy parameters.
```

### GrowFactors.first_year

```python
def first_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L96)

```text
GrowFactors class first_year property.
```

### GrowFactors.last_year

```python
def last_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L103)

```text
GrowFactors class last_year property.
```

### GrowFactors.price_inflation_rates

```python
def price_inflation_rates(self, firstyear, lastyear)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L109)

```text
Return list of price inflation rates rounded to four decimal digits.
```

### GrowFactors.wage_growth_rates

```python
def wage_growth_rates(self, firstyear, lastyear)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L127)

```text
Return list of wage growth rates rounded to four decimal digits.
```

### GrowFactors.factor_value

```python
def factor_value(self, name, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L145)

```text
Return value of factor with specified name for specified year.
```

### GrowFactors.update

```python
def update(self, name, year, diff)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/growfactors.py#L161)

```text
Add to self.gfdf (for name and year) the specified diff amount.
```
