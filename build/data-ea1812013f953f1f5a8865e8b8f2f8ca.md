# Tax-Calculator Data

Documentation of the `taxcalc.data` module.

## Data

```python
class Data(data, start_year, gfactors=None, weights=None, weights_scale=0.01)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L16)

```text
Inherit from this class for Records and other collections of
cross-sectional data that need to have growth factors and sample
weights to age the data to years after the start_year.

Parameters
----------
data: string or Pandas DataFrame
    string describes CSV file in which data reside;
    DataFrame already contains cross-sectional data for start_year.
    NOTE: data=None is allowed but the returned instance contains only
    the data variable information in the specified VARINFO file.
    NOTE: when using custom data, set this argument to a DataFrame.

start_year: integer
    specifies calendar year of the input data.

gfactors: None or GrowFactors class instance
    None implies empty growth factors DataFrame;
    instance contains data growth factors.

weights: None or string or Pandas DataFrame
    None creates empty sample weights DataFrame.
    string describes CSV file in which sample weights reside;
    DataFrame already contains sample weights.
    NOTE: when using custom weights, set this argument to a DataFrame.
    NOTE: assumes weights are integers that are 100 times the real weights.

weights_scale: float
    specifies the weights scaling factor used to convert contents
    of weights file into the s006 variable.  PUF and CPS input data
    generated in the taxdata repository use a weights_scale of 0.01,
    while TMD input data generated in the tax-microdata repository
    use a 1.0 weights_scale value.

Raises
------
ValueError:
    if data is not a string or a DataFrame instance.
    if start_year is not an integer.
    if gfactors is not None or a GrowFactors class instance
    if weights is not None or a string or a DataFrame instance.
    if gfactors and weights are not consistent.
    if files cannot be found.

Returns
-------
class instance: Data
```

### Data.data_year

```python
def data_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L128)

```text
Data class original data year property.
```

### Data.current_year

```python
def current_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L135)

```text
Data class current calendar year property.
```

### Data.array_length

```python
def array_length(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L142)

```text
Length of arrays in Data class's DataFrame.
```

### Data.increment_year

```python
def increment_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L148)

```text
Add one to current year; and also does extrapolation & reweighting
of data for the new current year if self._aging_data is True.
```

### Data._read_var_info

```python
def _read_var_info(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L167)

```text
Read Data variables metadata from JSON file and
specifies static variable name sets listed above.
```

### Data._read_data

```python
def _read_data(self, data)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L203)

```text
Read data from file or use specified DataFrame as data.
```

### Data.zero_out_changing_calculated_vars

```python
def zero_out_changing_calculated_vars(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L269)

```text
Set to zero all variables in the self.CHANGING_CALCULATED_VARS set.
```

### Data._read_weights

```python
def _read_weights(self, weights)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L278)

```text
Read sample weights from file or
use specified DataFrame as weights or
create empty DataFrame if None.
```

### Data._extrapolate

```python
def _extrapolate(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/data.py#L301)

```text
Apply to data variables the growth factor values for specified year.
```
