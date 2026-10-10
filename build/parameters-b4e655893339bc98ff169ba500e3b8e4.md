# Tax-Calculator Parameters

Documentation of the `taxcalc.parameters` module.

## CompatibleDataSchema

```python
class CompatibleDataSchema()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L14)

```text
Schema for compatible_data object

.. code-block :: json

    {
        "compatible_data": {"puf": true, "cps": false, "tmd": true}
    }
```

## Parameters

```python
class Parameters(start_year=None, num_years=None, last_known_year=None, removed=None, redefined=None, wage_indexed=None, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L36)

```text
Base class that wraps ParamTools, providing parameter indexing
for tax policy in the ``adjust`` method and convenience methods
like ``set_year`` for classes inheriting from it. It also provides
a backwards-compatible layer for Tax-Calculator versions prior to 3.0.

The defaults file path may be set through the defaults class attribute
variable or through the ``DEFAULTS_FILE_NAME`` /
``DEFAULTS_FILE_PATH work`` flow.

A custom getter method is implemented so that the value of a parameter
over all allowed years can conveniently be retrieved by adding an
underscore before the variable name (e.g. ``EITC_c`` vs ``_EITC_c``).

This class inherits methods from ParamTools like ``items``:

    .. code-block :: python

        import taxcalc as tc
        pol = tc.Policy()

        for name, value in pol.items():
            print(name, value)

        # parameter_indexing_CPI_offset [0.]
        # FICA_ss_trt_employer [0.062]
        # SS_Earnings_c [113700.]

Check out the ParamTools
`documentation <https://paramtools.dev/api/reference.html>`_
for more information on these inherited methods.
```

### Parameters.adjust

```python
def adjust(self, params_or_path, print_warnings=True, raise_errors=True, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L127)

```text
Update parameter values using a ParamTools styled adjustment.

Parameters
----------
params_or_path : Dict, str
    New parameter values in the paramtools format. For example:

    .. code-block:: json

        {
            "standard_deduction": [
                {"year": 2024, "marital_status": "single",
                 "value": 10000.0},
                {"year": 2024, "marital_status": "joint",
                 "value": 10000.0}
            ],
            "ss_rate": [{"year": 2024, "value": 0.2}]}
        }

print_warnings : Boolean
    Print parameter warnings or not
raise_errors: Boolean
    Raise errors as a ValidationError. If False, they will be stored
    in the errors attribute.


Returns
-------
adjustment : Dict
    Parsed paremeter dictionary
```

### Parameters.adjust_with_indexing

```python
def adjust_with_indexing(self, params_or_path, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L207)

```text
Adjust parameter values with the following indexing logic:

1. If "parameter_indexing_CPI_offset" is adjusted, first set
   parameter_indexing_CPI_offset to zero before implementing the
   adjusted parameter_indexing_CPI_offset to avoid stacking
   adjustments. Then, revert all values of indexed parameters to
   the 'known' values:

    a. The current values of parameters that are being adjusted are
       deleted after the first year in which
       parameter_indexing_CPI_offset is adjusted.
    b. The current values of parameters that are not being adjusted
       (i.e. are not in params) are deleted after the last known year,
       with the exception of parameters that revert to their pre-TCJA
       values in 2026. Instead, these (2026) parameter values are
       recalculated using the new inflation rates.

    After the 'unknown' values have been deleted, the last known value
    is extrapolated through the budget window. If there are indexed
    parameters in the adjustment, they will be included in the final
    adjustment call (unless their indexed status is changed).

2. If the "indexed" status is updated for any parameter:

    a. If a parameter has values that are being adjusted before
       the indexed status is adjusted, update those parameters first.
    b. Extend the values of that parameter to the year in which
       the status is changed.
    c. Change the indexed status for the parameter.
    d. Update parameter values in adjustment that are adjusted after
       the year in which the indexed status changes.
    e. Using the new "-indexed" status, extend the values of that
       parameter through the remaining years or until the -indexed
       status changes again.

3. Update all parameters that are not indexing related, i.e. they are
   not "parameter_indexing_CPI_offset" or do not end with "-indexed".

4. Returns parsed adjustment with all adjustments, including "-indexed"
   parameters.

Notable side-effects:

- All values of a parameter whose indexed status is adjusted are
  wiped out after the year in which the value is adjusted for the
  same hard-coding reason.
```

### Parameters.get_index_rate

```python
def get_index_rate(self, param, lte_val)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L503)

```text
Initalize indexing data and return the indexing rate value
depending on the parameter name and lte_val (that is, the
label_to_extend_val), the value of label_to_extend.
Returns: rate to use for indexing.
```

### Parameters.set_rates

```python
def set_rates(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L516)

```text
This method is implemented by classes inheriting Parameters.
```

### Parameters.wage_growth_rates

```python
def wage_growth_rates(self, year=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L522)

```text
Returns wage growth rates used in parameter indexing.
```

### Parameters.inflation_rates

```python
def inflation_rates(self, year=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L531)

```text
Returns price inflation rates used in parameter indexing.
```

### Parameters.initialize

```python
def initialize(self, start_year, num_years, last_known_year=None, removed=None, redefined=None, wage_indexed=None, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L542)

```text
Legacy method for initializing a Parameters instance. Projects
should use the __init__ method in the future.
```

### Parameters._update

```python
def _update(self, revision, print_warnings, raise_errors)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L559)

```text
A translation layer on top of ``adjust``. Projects
that have historically used the ``_update`` method with
Tax-Calculator styled adjustments can continue to do so
without making any changes to how they handle adjustments.

Converts reforms that are compatible with Tax-Calculator:

.. code-block:: python

    adjustment = {
        "standard_deduction": {2024: [10000.0, 10000.0]},
        "ss_rate": {2024: 0.2}
    }

into reforms that are compatible with ParamTools:

.. code-block:: python

    {
        "standard_deduction": [
            {"year": 2024, "marital_status": "single",
             "value": 10000.0},
            {"year": 2024, "marital_status": "joint",
             "value": 10000.0}
        ],
        "ss_rate": [{"year": 2024, "value": 0.2}]}
    }
```

### Parameters.set_year

```python
def set_year(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L677)

```text
Specify parameter year
```

### Parameters.current_year

```python
def current_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L682)

```text
Propery docstring
```

### Parameters.start_year

```python
def start_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L687)

```text
Propery docstring
```

### Parameters.end_year

```python
def end_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L692)

```text
Propery docstring
```

### Parameters.num_years

```python
def num_years(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L697)

```text
Propery docstring
```

### Parameters.parameter_errors

```python
def parameter_errors(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L702)

```text
Propery docstring
```

### Parameters._read_json_revision

```python
def _read_json_revision(obj, topkey)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L707)

```text
Read JSON revision specified by ``obj`` and ``topkey``
returning a single revision dictionary suitable for
use with the ``Parameters._update`` or ``Parameters.adjust`` methods.
The obj function argument can be ``None`` or a string, where the
string can be:

  - Path for a local file
  - Link pointing to a valid JSON file
  - Valid JSON text

The ``topkey`` argument must be a string containing the top-level
key in a compound-revision JSON text for which a revision
dictionary is returned.  If the specified ``topkey`` is not among
the top-level JSON keys, the ``obj`` is assumed to be a
non-compound-revision JSON text for the specified ``topkey``.

Some examples of valid links are::

    HTTP: https://raw.githubusercontent.com/PSLmodels/
          Tax-Calculator/master/taxcalc/reforms/2017_law.json

    Github API: github://PSLmodels:Tax-Calculator@master/
                taxcalc/reforms/2017_law.json

Checkout the ParamTools `docs`_ for more information on valid
file URLs.

.. _docs: https://paramtools.dev/_modules/paramtools/
   parameters.html#Parameters.read_params
```

### Parameters.metadata

```python
def metadata(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L775)

```text
Returns parameter specification.
```

### Parameters.years_in_revision

```python
def years_in_revision(revision)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L782)

```text
Returns list of years in specified revision dictionary, which is
assumed to have a param:year:value format.
```

### Parameters.__getattr__

```python
def __getattr__(self, attr)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L797)

```text
Get the value of a parameter over all years by accessing it
with an underscore in front of its name: ``pol._EITC_c`` instead of
``pol.EITC_c``.
```

### Parameters.extend_func

```python
def extend_func(self, param: str, extend_vo: paramtools.ValueObject, known_vo: paramtools.ValueObject, extend_grid: List, label: str)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L812)

```text
Method for applying indexing rates to extended parameter values.
Returns:
- `extend_vo`: New `paramtools.ValueObject`.
```

## is_paramtools_format

```python
def is_paramtools_format(params: Union[TaxcalcReform, ParamToolsAdjustment])
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/parameters.py#L893)

```text
Check first item in ``params`` to determine if it is using the ParamTools
adjustment or the Tax-Calculator reform format.
If first item is a ``dict``, then it is likely be a Tax-Calculator reform.
Otherwise, it is likely to be a ParamTools format.

Parameters
----------
params: dict
    Either a ParamTools or Tax-Calculator styled parameters ``dict``.

    .. code-block:: python

        # ParamTools style format:
        {
            "ss_rate": {2024: 0.2}
        }

        # Tax-Calculator style format:
        {
            "ss_rate": [{"year": 2024, "value": 0.2}]}
        }

Returns
-------
bool:
  Whether ``params`` is likely to be a ParamTools formatted
  adjustment or not.
```
