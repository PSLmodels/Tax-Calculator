# Tax-Calculator Records

Documentation of the `taxcalc.records` module.

## Records

```python
class Records(data=None, start_year=None, gfactors=None, weights=None, adjust_ratios=None, exact_calculations=False, weights_scale=0.01)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L17)

```text
Records is a subclass of the abstract Data class, and therefore,
inherits its methods (none of which are shown here).

Constructor for the tax-filing-unit Records class.

Parameters
----------
data: string or Pandas DataFrame or None
    string describes CSV file in which records data reside;
    DataFrame already contains records data;
    default value is None.
    NOTE: when using custom data, set this argument to a DataFrame.
    NOTE: to use your own data for a specific year with Tax-Calculator,
    be sure to read the documentation on creating your own data file and
    then construct a Records object like this::

        mydata = pd.read_csv(<mydata.csv>)
        myrec = Records(data=mydata, start_year=<mydata_year>,
                        gfactors=None, weights=None)

    NOTE: data=None is allowed but the returned instance contains only
    the data variable information in the specified VARINFO file.

start_year: integer or None
    specifies calendar year of the input data;
    default value is None.
    Note that if specifying your own data (see above NOTE) as being
    a custom data set, be sure to explicitly set start_year to the
    custom data's calendar year.

gfactors: GrowFactors class instance or None
    containing record data growth (or extrapolation) factors.
    default value is None.

weights: Pandas DataFrame or None
    DataFrame contains data weights;
    None creates empty weights DataFrame;
    default value is None
    NOTE: when using custom weights, set this argument to a DataFrame.
    NOTE: see weights_scale documentation below.

adjust_ratios: Pandas DataFrame or None
    DataFrame contains transposed/no-index adjustment ratios;
    None creates empty adjustment-ratios DataFrame;
    default value is None.
    NOTE: when using custom ratios, set this argument to a DataFrame.
    NOTE: if specifying a DataFrame, set adjust_ratios to my_df
    defined as::

        my_df = pd.read_csv('<my_ratios.csv>', index_col=0).transpose()

exact_calculations: boolean
    specifies whether or not exact tax calculations are done without
    any smoothing of stair-step provisions in income tax law;
    default value is false.

weights_scale: float
    specifies the weights scaling factor used to convert contents
    of weights file into the s006 variable.  PUF and CPS input data
    generated in the taxdata repository use a weights_scale of 0.01,
    while TMD input data generated in the tax-microdata repository
    use a 1.0 weights_scale value.
    default value is 0.01.

Raises
------
ValueError:
    if data is not the appropriate type.
    if taxpayer and spouse variables do not add up to filing-unit total.
    if dividends is less than qualified dividends.
    if gfactors is not None or a GrowFactors class instance.
    if start_year is not an integer.
    if files cannot be found.

Returns
-------
class instance: Records

Notes
-----
Use Records.cps_constructor() to get a Records object instantiated
with CPS input data developed in the taxdata repository.

Use Records.puf_constructor() to get a Records object instantiated
with PUF input data developed in the taxdata repository.

Use Records.tmd_constructor() to get a Records object instantiated
with TMD input data developed in the tax-microdata repository.
```

### Records.cps_constructor

```python
def cps_constructor(data=None, gfactors=GrowFactors(), exact_calculations=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L202)

```text
Static method returns a Records object instantiated with CPS
input data.  This is a convenience method that eliminates the
need to specify all the details of the CPS input data.
```

### Records.puf_constructor

```python
def puf_constructor(data='puf.csv', gfactors=GrowFactors(), weights='puf_weights.csv.gz', ratios='puf_ratios.csv', exact_calculations=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L229)

```text
Static method returns a Records object instantiated with PUF
input data.  This is a convenience method that eliminates the
need to specify all the details of the PUF input data.
```

### Records.tmd_constructor

```python
def tmd_constructor(data_path: Path, weights_path: Path, growfactors: Path | GrowFactors, exact_calculations=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L256)

```text
Static method returns a Records object instantiated with TMD
input data.  This is a convenience method that eliminates the
need to specify all the details of the TMD input data.
```

### Records.increment_year

```python
def increment_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L283)

```text
Add one to current year, and also does
extrapolation, reweighting, adjusting for new current year.
```

### Records.read_cps_data

```python
def read_cps_data()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L294)

```text
Return data in cps.csv.gz as a Pandas DataFrame.
```

### Records._extrapolate

```python
def _extrapolate(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L307)

```text
Apply to variables the grow factor values for specified calendar year.
```

### Records._adjust

```python
def _adjust(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L411)

```text
Adjust value of PUF income variables to match SOI distributions
Note: adjustment must leave variables as numpy.ndarray type
```

### Records._read_ratios

```python
def _read_ratios(self, ratios)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/records.py#L421)

```text
Read Records PUF-related adjustment ratios using
specified transposed/no-index DataFrame as ratios or
create empty DataFrame if ratios is None.
```
