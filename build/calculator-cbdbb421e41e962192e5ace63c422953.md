# Tax-Calculator Calculator

Documentation of the `taxcalc.calculator` module.

## Calculator

```python
class Calculator(policy=None, records=None, verbose=False, sync_years=True, consumption=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L42)

```text
Constructor for the Calculator class.

Parameters
----------
policy: Policy class object
    this argument must be specified and object is copied for internal use

records: Records class object
    this argument must be specified and object is copied for internal use

verbose: boolean
    specifies whether or not to write to stdout data-loaded and
    data-extrapolated progress reports; default value is false.

sync_years: boolean
    specifies whether or not to synchronize policy year and records year;
    default value is true.

consumption: Consumption class object
    specifies consumption response assumptions used to calculate
    "effective" marginal tax rates; default is None, which implies
    no consumption responses assumed in marginal tax rate calculations;
    when argument is an object it is copied for internal use;
    also specifies consumption value of in-kind benefis with no in-kind
    consumption values specified implying consumption value is equal to
    government cost of providing the in-kind benefits

Raises
------
ValueError:
    if parameters are not the appropriate type.

Returns
-------
class instance: Calculator

Notes
-----
The most efficient way to specify current-law and reform Calculator
objects is as follows::

    pol = Policy()
    rec = Records.cps_constructor()
    calc1 = Calculator(policy=pol, records=rec)  # current-law
    pol.implement_reform(...)
    calc2 = Calculator(policy=pol, records=rec)  # reform

All calculations are done on the internal copies of the Policy and
Records objects passed to each of the two Calculator constructors.
```

### Calculator.increment_year

```python
def increment_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L143)

```text
Advance all embedded objects to next year.
```

### Calculator.advance_to_year

```python
def advance_to_year(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L152)

```text
The advance_to_year function gives an optional way of implementing
increment year functionality by immediately specifying the year
as input.  New year must be at least the current year.
```

### Calculator.calc_all

```python
def calc_all(self, zero_out_calc_vars=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L166)

```text
Call all tax-calculation functions for the current_year.
```

### Calculator.weighted_total

```python
def weighted_total(self, variable_name)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L179)

```text
Return all-filing-unit weighted total of named Records variable.
```

### Calculator.total_weight

```python
def total_weight(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L185)

```text
Return all-filing-unit total of sampling weights.
NOTE: var_weighted_mean = calc.weighted_total(var)/calc.total_weight()
```

### Calculator.dataframe

```python
def dataframe(self, variable_list, all_vars=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L192)

```text
Return Pandas DataFrame containing the listed variables from the
embedded Records object.  If all_vars is True, then the variable_list
is ignored and all variables used as input to and calculated by the
Calculator.calc_all() method (which does not include marginal tax
rates) are included in the returned Pandas DataFrame.
```

### Calculator.array

```python
def array(self, variable_name, variable_value=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L212)

```text
If variable_value is None, return numpy ndarray containing the
 named variable in embedded Records object.
If variable_value is not None, set named variable in embedded Records
 object to specified variable_value and return None (which can be
 ignored).
```

### Calculator.n65

```python
def n65(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L226)

```text
Return numpy ndarray containing the number of
individuals age 65+ in each filing unit.
```

### Calculator.incarray

```python
def incarray(self, variable_name, variable_add)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L236)

```text
Add variable_add to named variable in embedded Records object.
```

### Calculator.zeroarray

```python
def zeroarray(self, variable_name)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L244)

```text
Set named variable in embedded Records object to zeros.
```

### Calculator.store_records

```python
def store_records(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L250)

```text
Make internal copy of embedded Records object that can then be
restored after interim calculations that make temporary changes
to the embedded Records object.
```

### Calculator.restore_records

```python
def restore_records(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L259)

```text
Set the embedded Records object to the stored Records object
that was saved in the last call to the store_records() method.
```

### Calculator.array_len

```python
def array_len(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L270)

```text
Length of arrays in embedded Records object.
```

### Calculator.policy_param

```python
def policy_param(self, param_name, param_value=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L276)

```text
If param_value is None, return named parameter in
 embedded Policy object.
If param_value is not None, set named parameter in
 embedded Policy object to specified param_value and
 return None (which can be ignored).
```

### Calculator.consump_param

```python
def consump_param(self, param_name)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L292)

```text
Return value of named parameter in embedded Consumption object.
```

### Calculator.consump_benval_params

```python
def consump_benval_params(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L298)

```text
Return list of benefit-consumption-value parameter values
in embedded Consumption object.
```

### Calculator.reform_errors

```python
def reform_errors(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L306)

```text
Calculator class embedded Policy object's parameter_errors.
```

### Calculator.current_year

```python
def current_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L313)

```text
Calculator class current calendar year property.
```

### Calculator.data_year

```python
def data_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L320)

```text
Calculator class initial (i.e., first) records data year property.
```

### Calculator.diagnostic_table

```python
def diagnostic_table(self, num_years)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L326)

```text
Generate multi-year diagnostic table containing aggregate statistics;
this method leaves the Calculator object unchanged.

Parameters
----------
num_years : Integer
    number of years to include in diagnostic table starting
    with the Calculator object's current_year (must be at least
    one and no more than what would exceed Policy end_year)

Returns
-------
Pandas DataFrame object containing the multi-year diagnostic table
```

### Calculator.distribution_tables

```python
def distribution_tables(self, calc, groupby, pop_quantiles=False, scaling=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L357)

```text
Get results from self and calc, sort them by expanded_income into
table rows defined by groupby, compute grouped statistics, and
return tables as a pair of Pandas dataframes.
This method leaves the Calculator object(s) unchanged.
Note that the returned tables have consistent income groups (based
on the self expanded_income) even though the baseline expanded_income
in self and the reform expanded_income in calc are different.

Parameters
----------
calc : Calculator object or None
    typically represents the reform while self represents the baseline;
    if calc is None, the second returned table is None

groupby : String object
    determines how the columns in the resulting Pandas DataFrame
    are sorted; options for input are 'weighted_deciles',
    'standard_income_bins', and 'soi_agi_bins'

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

scaling : boolean
    specifies create_distribution_table utility function argument
    that determines whether table entry values are scaled or not

Returns
-------
Each of the dist1 and optional dist2 is a distribution table as a
Pandas DataFrame with DIST_TABLE_COLUMNS and groupby rows.

Notes
-----
Typical usage is::

    dist1, dist2 = calc1.distribution_tables(calc2,
                                             'weighted_deciles')
    # OR
    dist1, _ = calc1.distribution_tables(None, 'weighted_deciles')

where calc1 is a baseline Calculator object and calc2 is a reform
Calculator object.

NOTE: when groupby is 'weighted_deciles', the returned tables have 3
extra rows containing top-decile detail consisting of statistics
for the 0.90-0.95 quantile range (bottom half of top decile),
for the 0.95-0.99 quantile range, and
for the 0.99-1.00 quantile range (top one percent); and the
returned table splits the bottom decile into filing units with
negative (denoted by a 0-10n row label),
zero (denoted by a 0-10z row label), and
positive (denoted by a 0-10p row label) values of the
specified income_measure.
```

### Calculator.difference_table

```python
def difference_table(self, calc, groupby, tax_to_diff, pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L478)

```text
Get results from self and calc, sort them by expanded_income into
table rows defined by groupby, compute grouped statistics, and
return tax-difference table as a Pandas dataframe.
This method leaves the Calculator objects unchanged.
Note that the returned tables have consistent income groups (based
on the self expanded_income) even though the baseline expanded_income
in self and the reform expanded_income in calc are different.

Parameters
----------
calc : Calculator object
    calc represents the reform while self represents the baseline

groupby : String object
    determines how the columns in the resulting Pandas DataFrame
    are sorted; options for input are 'weighted_deciles' and
    'standard_income_bins'

tax_to_diff : String object
    specifies which tax to difference; options for input are
    'iitax', 'payrolltax', and 'combined'

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
The returned diff is a difference table as a Pandas DataFrame
with DIST_TABLE_COLUMNS and groupby rows.

Notes
-----
Typical usage is::

    diff = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')

where calc1 is a baseline Calculator object and calc2 is a reform
Calculator object.

NOTE: when groupby is 'weighted_deciles', the returned table has three
extra rows containing top-decile detail consisting of statistics
for the 0.90-0.95 quantile range (bottom half of top decile),
for the 0.95-0.99 quantile range, and
for the 0.99-1.00 quantile range (top one percent); and the
returned table splits the bottom decile into filing units with
negative (denoted by a 0-10n row label),
zero (denoted by a 0-10z row label), and
positive (denoted by a 0-10p row label) values of the
specified income_measure.
```

### Calculator.mtr

```python
def mtr(self, variable_str='e00200p', finite_diff=0.01, zero_out_calculated_vars=False, calc_all_already_called=False, wrt_full_compensation=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L556)

```text
Calculates the marginal payroll, individual income, and combined
tax rates for every tax filing unit, leaving the Calculator object
in exactly the same state as it would be in after a calc_all() call.

The marginal tax rates are approximated as the change in tax
liability caused by a small increase (the finite_diff) in the variable
specified by the variable_str divided by that small increase in the
variable, when wrt_full_compensation is false.

If wrt_full_compensation is true, then the marginal tax rates
are computed as the change in tax liability divided by the change
in total compensation caused by the small increase in the variable
(where the change in total compensation is the sum of the small
increase in the variable and any increase in the employer share of
payroll taxes caused by the small increase in the variable).

If using 'e00200s' as variable_str, the marginal tax rate for all
records where MARS != 2 will be missing.  If you want to perform a
function such as np.mean() on the returned arrays, you will need to
account for this.

Parameters
----------
variable_str: string
    specifies type of income or expense that is increased to compute
    the marginal tax rates.  See Notes for list of valid variables.

finite_diff: float
    specifies the finite_diff amount added to the specified variable.
    Can be positive or negative, but not zero.

zero_out_calculated_vars: boolean
    specifies value of zero_out_calc_vars parameter used in calls
    of Calculator.calc_all() method.

calc_all_already_called: boolean
    specifies whether self has already had its Calculor.calc_all()
    method called, in which case this method will not do a final
    calc_all() call but use the incoming embedded Records object
    as the outgoing Records object embedding in self.

wrt_full_compensation: boolean
    specifies whether or not marginal tax rates on earned income
    are computed with respect to (wrt) changes in total compensation
    that includes the employer share of OASDI and HI payroll taxes.

Returns
-------
A tuple of numpy arrays in the following order:
mtr_payrolltax: an array of marginal payroll tax rates.
mtr_incometax: an array of marginal individual income tax rates.
mtr_combined: an array of marginal combined tax rates, which is
the sum of mtr_payrolltax and mtr_incometax.

Notes
-----
The arguments zero_out_calculated_vars and calc_all_already_called
cannot both be true.

Valid variable_str values are:
'e00200p', taxpayer wage/salary earnings (also included in e00200);
'e00200s', spouse wage/salary earnings (also included in e00200);
'e00900p', taxpayer Schedule C self-employment income (also in e00900);
'e00300',  taxable interest income;
'e00400',  federally-tax-exempt interest income;
'e00600',  all dividends included in AGI
'e00650',  qualified dividends (also included in e00600)
'e01400',  federally-taxable IRA distribution;
'e01700',  federally-taxable pension benefits;
'e02000',  Schedule E total net income/loss
'e02400',  all social security (OASDI) benefits;
'p22250',  short-term capital gains;
'p23250',  long-term capital gains;
'e18500',  Schedule A real-estate-tax paid;
'e19200',  Schedule A interest paid;
'e26270',  S-corporation/partnership income (also included in e02000);
'e19800',  Charity cash contributions;
'e20100',  Charity non-cash contributions;
'k1bx14p', Partnership income (also included in e26270 and e02000).
```

### Calculator.mtr_graph

```python
def mtr_graph(self, calc, mars='ALL', mtr_measure='combined', mtr_variable='e00200p', alt_e00200p_text='', mtr_wrt_full_compen=False, income_measure='expanded_income', pop_quantiles=False, dollar_weighting=False, mtr_self=None, mtr_calc=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L752)

```text
Create marginal tax rate graph that can be written to an HTML
file (using the write_graph_file utility function) or shown on
the screen immediately in an interactive or notebook session
(following the instructions in the documentation of the
xtr_graph_plot utility function).

Parameters
----------
calc : Calculator object
    calc represents the reform while self represents the baseline

mars : integer or string
    specifies which filing status subgroup to show in the graph

    - 'ALL': include all filing units in sample

    - 1: include only single filing units

    - 2: include only married-filing-jointly filing units

    - 3: include only married-filing-separately filing units

    - 4: include only head-of-household filing units

mtr_measure : string
    specifies which marginal tax rate to show on graph's y axis

    - 'itax': marginal individual income tax rate

    - 'ptax': marginal payroll tax rate

    - 'combined': sum of marginal income and payroll tax rates

mtr_variable : string
    any string in the Calculator.VALID_MTR_VARS set
    specifies variable to change in order to compute marginal tax rates

alt_e00200p_text : string
    text to use in place of mtr_variable
    when mtr_variable is 'e00200p';
    if empty string then use 'e00200p'

mtr_wrt_full_compen : boolean
    see documentation of Calculator.mtr()
    argument wrt_full_compensation
    (value has an effect only if mtr_variable is 'e00200p')

income_measure : string
    specifies which income variable to show on the graph's x axis

    - 'wages': wage and salary income (e00200)

    - 'agi': adjusted gross income, AGI (c00100)

    - 'expanded_income': broader than AGI (see definition in
                         calcfunctions.py file).

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

dollar_weighting : boolean
    False implies both income_measure percentiles on x axis
    and mtr values for each percentile on the y axis are
    computed without using dollar income_measure weights (just
    sampling weights); True implies both income_measure
    percentiles on x axis and mtr values for each percentile
    on the y axis are computed using dollar income_measure
    weights (in addition to sampling weights).  Specifying
    True produces a graph x axis that shows income_measure
    (not filing unit) percentiles.

mtr_self : None or tuple
    None implies the marginal tax rates for self are computed by
    calling self.mtr() using the mtr_variable and mtr_wrt_full_compen
    arguments; otherwise, the tuple of three arrays returned by an
    earlier self.mtr() call, which avoids repeating that calculation.
    Note that it is the caller's responsibility to ensure that the
    earlier self.mtr() call used the same variable_str and
    wrt_full_compensation values as the mtr_variable and
    mtr_wrt_full_compen arguments of this method.

mtr_calc : None or tuple
    same as mtr_self except for the calc Calculator object;
    mtr_self and mtr_calc must both be None or both be tuples.

Returns
-------
graph that is a bokeh.plotting figure object
```

### Calculator.atr_graph

```python
def atr_graph(self, calc, mars='ALL', atr_measure='combined', pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L936)

```text
Create average tax rate graph that can be written to an HTML
file (using the write_graph_file utility function) or shown on
the screen immediately in an interactive or notebook session
(following the instructions in the documentation of the
xtr_graph_plot utility function).  The graph shows the mean
average tax rate for each expanded-income percentile excluding
any percentile that includes a filing unit with negative or
zero basline (self) expanded income.

Parameters
----------
calc : Calculator object
    calc represents the reform while self represents the baseline,
    where both self and calc have calculated taxes for this year
    before being used by this method

mars : integer or string
    specifies which filing status subgroup to show in the graph

    - 'ALL': include all filing units in sample

    - 1: include only single filing units

    - 2: include only married-filing-jointly filing units

    - 3: include only married-filing-separately filing units

    - 4: include only head-of-household filing units

atr_measure : string
    specifies which average tax rate to show on graph's y axis

    - 'itax': average individual income tax rate

    - 'ptax': average payroll tax rate

    - 'combined': sum of average income and payroll tax rates

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
graph that is a bokeh.plotting figure object
```

### Calculator.pch_graph

```python
def pch_graph(self, calc, pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1033)

```text
Create percentage change in after-tax expanded income graph that
can be written to an HTML file (using the write_graph_file utility
function) or shown on the screen immediately in an interactive or
notebook session (following the instructions in the documentation
of the xtr_graph_plot utility function).  The graph shows the
dollar-weighted mean percentage change in after-tax expanded income
for each expanded-income percentile excluding any percentile that
includes a filing unit with negative or zero basline (self) expanded
income.

Parameters
----------
calc : Calculator object
    calc represents the reform while self represents the baseline,
    where both self and calc have calculated taxes for this year
    before being used by this method

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
graph that is a bokeh.plotting figure object
```

### Calculator.read_json_param_objects

```python
def read_json_param_objects(reform, assump)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1094)

```text
Read JSON reform and assump objects and
return a composite dictionary containing four key:dict pairs:
'policy':dict, 'consumption':dict,
'growdiff_baseline':dict, and 'growdiff_response':dict.

Note that either of the two function arguments can be None.
If reform is None, the dict in the 'policy':dict pair is empty.
If assump is None, the dict in all the other key:dict pairs is empty.

Also note that either of the two function arguments can be strings
containing a valid JSON string (rather than a local filename).

Either of the two function arguments can also be a valid URL string
beginning with 'http' and pointing to a valid JSON file hosted online.

The reform file/URL contents or JSON string must be like this::

    {"policy": {...}} OR {...}

(in other words, the top-level policy key is optional)
and the assump file/URL contents or JSON string must be like this::

    {"consumption": {...},
     "growdiff_baseline": {...},
     "growdiff_response": {...}}

The {...} should be empty like this {} if not specifying a policy
reform or if not specifying any non-default economic assumptions
of that type.

The 'policy' subdictionary of the returned dictionary is
suitable as input into the Policy.implement_reform method.

The 'consumption' subdictionary of the returned dictionary is
suitable as input into the Consumption.update_consumption method.

The 'growdiff_baseline' subdictionary of the returned dictionary is
suitable as input into the GrowDiff.update_growdiff method.

The 'growdiff_response' subdictionary of the returned dictionary is
suitable as input into the GrowDiff.update_growdiff method.
```

### Calculator.reform_documentation

```python
def reform_documentation(params, growfactors, policy_dicts=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1148)

```text
Generate reform documentation versus current-law policy.

Parameters
----------
params: dict
    dictionary is structured like dict returned from
    the static Calculator.read_json_param_objects() method

growfactors: GrowFactors
    GrowFactors object used to construct Calculator Policy object

policy_dicts : list of dict or None
    each dictionary in list is a params['policy'] dictionary
    representing second and subsequent elements of a compound
    reform; None implies no compound reform with the simple
    reform characterized in the params['policy'] dictionary

Returns
-------
doc: String
    the documentation for the specified policy reform
```

### Calculator.ce_aftertax_income

```python
def ce_aftertax_income(self, calc, custom_params=None, require_no_agg_tax_change=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1363)

```text
Return dictionary that contains certainty-equivalent of the
expected utility of after-tax expanded income computed for
several constant-relative-risk-aversion parameter values
for each of two Calculator objects: self, which represents
the pre-reform situation, and calc, which represents the
post-reform situation, both of which MUST have had calc_call()
called before being passed to this function.

IMPORTANT NOTES: These normative welfare calculations are very
simple.  It is assumed that utility is a function of only
consumption, and that consumption is equal to after-tax
income.  This means that any assumed responses that
change work effort will not affect utility via the
correpsonding change in leisure.  And any saving response to
changes in after-tax income do not affect consumption.

The cmin value is the consumption level below which marginal
utility is considered to be constant.  This allows the handling
of filing units with very low or even negative after-tax expanded
income in the expected-utility and certainty-equivalent calculations.
```

### Calculator._taxinc_to_amt

```python
def _taxinc_to_amt(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1407)

```text
Call TaxInc through AMT functions.
```

### Calculator._calc_one_year

```python
def _calc_one_year(self, zero_out_calc_vars=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/calculator.py#L1418)

```text
Call all the functions except those in the calc_all() method.
```
