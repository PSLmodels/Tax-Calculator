# Tax-Calculator Utilities

Documentation of the `taxcalc.utils` module.

## unweighted_sum

```python
def unweighted_sum(dframe, col_name)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L137)

```text
Return unweighted sum of Pandas DataFrame col_name items.
```

## weighted_sum

```python
def weighted_sum(dframe, col_name)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L144)

```text
Return weighted sum of Pandas DataFrame col_name items.
```

## add_quantile_table_row_variable

```python
def add_quantile_table_row_variable(dframe, income_measure, num_quantiles, pop_quantiles=False, decile_details=False, weight_by_income_measure=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L151)

```text
   Add a variable to specified Pandas DataFrame, dframe, that specifies
   the table row and is called 'table_row'.

   When weight_by_income_measure=False, the rows hold an equal number of
   people if pop_quantiles=True or an equal number of filing units if
   pop_quantiles=False.

   When weight_by_income_measure=True, the rows hold an equal number
   of income dollars.

   This function assumes that specified dframe contains columns for
   the specified income_measure and for sample weights, s006, and when
   pop_quantiles=True, number of exemptions, XTOT.

.  When num_quantiles is 10 and decile_details is True,
   the bottom decile is broken up into three subgroups
   (neg, zero, and pos income_measure)
   and the top decile is broken into three subgroups
   (90-95, 95-99, and top 1%).
   
```

## add_income_table_row_variable

```python
def add_income_table_row_variable(dframe, income_measure, bin_edges)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L247)

```text
Add a variable to specified Pandas DataFrame, dframe, that specifies the
table row and is called 'table_row'.  The rows are defined by the
specified bin_edges function argument.  Note that the bin groupings
are LEFT INCLUSIVE, which means that bin_edges=[1,2,3,4] implies these
three bin groupings: [1,2), [2,3), [3,4).

Parameters
----------
dframe: Pandas DataFrame
    the object to which we are adding bins

income_measure: String
    specifies income variable used to construct bins

bin_edges: list of scalar bin edges

Returns
-------
dframe: Pandas DataFrame
    the original input plus the added 'table_row' column
```

## get_sums

```python
def get_sums(dframe)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L279)

```text
Compute unweighted sum of items in each column of Pandas DataFrame, dframe.

Returns
-------
Pandas Series object containing column sums indexed by dframe column names.
```

## create_distribution_table

```python
def create_distribution_table(vdf, groupby, income_measure, pop_quantiles=False, scaling=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L294)

```text
Get results from vdf, sort them by expanded_income based on groupby,
and return them as a table.

Parameters
----------
vdf : Pandas DataFrame including columns named in DIST_TABLE_COLUMNS list
    for example, an object returned from the distribution_table_dataframe
    function in the Calculator distribution_tables method

groupby : String object
    determines how the rows in the resulting Pandas DataFrame are
    sorted; options for input are 'weighted_deciles',
    'standard_income_bins', and 'soi_agi_bins'

income_measure: String object
    determines which variable is used to sort rows; options for input
    are 'expanded_income' and 'expanded_income_baseline'

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

scaling : boolean
    specifies whether or not table entry values are scaled

Returns
-------
distribution table as a Pandas DataFrame with DIST_TABLE_COLUMNS and
groupby rows.

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

## create_difference_table

```python
def create_difference_table(vdf1, vdf2, groupby, tax_to_diff, pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L441)

```text
Get results from two different vdf, construct tax difference results,
and return the difference statistics as a table.

Parameters
----------
vdf1 : Pandas DataFrame including columns named in DIFF_VARIABLES list
       for example, object returned from a dataframe(DIFF_VARIABLES) call
       on the basesline Calculator object

vdf2 : Pandas DataFrame including columns in the DIFF_VARIABLES list
       for example, object returned from a dataframe(DIFF_VARIABLES) call
       on the reform Calculator object

groupby : String object
    determines how the rows in the resulting Pandas DataFrame are
    sorted; options for input are 'weighted_deciles',
    'standard_income_bins', and 'soi_agi_bins'

tax_to_diff : String object
    specifies which tax to difference; options for input are
    'iitax', 'payrolltax', and 'combined'

pop_quantiles : boolean
    specifies whether or not weighted_deciles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
difference table as a Pandas DataFrame with DIFF_TABLE_COLUMNS and
groupby rows.

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

## create_diagnostic_table

```python
def create_diagnostic_table(dframe_list, year_list)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L658)

```text
Extract diagnostic table from list of Pandas DataFrame objects
returned from a Calculator dataframe(DIST_VARIABLES) call for
each year in the specified list of years.

Parameters
----------
dframe_list : list of Pandas DataFrame objects containing the variables

year_list : list of calendar years corresponding to the dframe_list

Returns
-------
Pandas DataFrame object containing the diagnostic table
```

## mtr_graph_data

```python
def mtr_graph_data(vdf, year, mars='ALL', mtr_measure='combined', mtr_variable='e00200p', alt_e00200p_text='', mtr_wrt_full_compen=False, income_measure='expanded_income', pop_quantiles=False, dollar_weighting=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L790)

```text
Prepare marginal tax rate data needed by xtr_graph_plot utility function.

Parameters
----------
vdf : a Pandas DataFrame object containing variables and marginal tax rates
    (See Calculator.mtr_graph method for required elements of vdf.)

year : integer
    specifies calendar year of the data in vdf

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
    text to use in place of mtr_variable when mtr_variable is 'e00200p';
    if empty string then use 'e00200p'

mtr_wrt_full_compen : boolean
    see documentation of Calculator.mtr() argument wrt_full_compensation
    (value has an effect only if mtr_variable is 'e00200p')

income_measure : string
    specifies which income variable to show on the graph's x axis

    - 'wages': wage and salary income (e00200)

    - 'agi': adjusted gross income, AGI (c00100)

    - 'expanded_income': sum of AGI, non-taxable interest income,
      non-taxable social security benefits, and employer share of
      FICA taxes.

pop_quantiles : boolean
    specifies whether or not quantiles contain an equal number
    of people (True) or an equal number of filing units (False)

dollar_weighting : boolean
    False implies both income_measure percentiles on x axis and
    mtr values for each percentile on the y axis are computed
    without using dollar income_measure weights (just sampling weights);
    True implies both income_measure percentiles on x axis and
    mtr values for each percentile on the y axis are computed
    using dollar income_measure weights (in addition to sampling weights).
    Specifying True produces a graph x axis that shows income_measure
    (not filing unit) percentiles.

Returns
-------
dictionary object suitable for passing to xtr_graph_plot utility function
```

## atr_graph_data

```python
def atr_graph_data(vdf, year, mars='ALL', atr_measure='combined', pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L972)

```text
Prepare average tax rate data needed by xtr_graph_plot utility function.

Parameters
----------
vdf : a Pandas DataFrame object containing variables and tax liabilities
    (See Calculator.atr_graph method for required elements of vdf.)

year : integer
    specifies calendar year of the data in vdf

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
    specifies whether or not quantiles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
dictionary object suitable for passing to xtr_graph_plot utility function
```

## xtr_graph_plot

```python
def xtr_graph_plot(data, width=850, height=500, xlabel='', ylabel='', title='', legendloc='bottom_right')
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1100)

```text
Plot marginal/average tax rate graph using data returned from either the
mtr_graph_data function or the atr_graph_data function.

Parameters
----------
data : dictionary object returned from ?tr_graph_data() utility function

width : integer
    width of plot expressed in pixels

height : integer
    height of plot expressed in pixels

xlabel : string
    x-axis label; if '', then use label generated by ?tr_graph_data

ylabel : string
    y-axis label; if '', then use label generated by ?tr_graph_data

title : string
    graph title; if '', then use title generated by ?tr_graph_data

legendloc : string
    options: 'top_right', 'top_left', 'bottom_left', 'bottom_right'
    specifies location of the legend in the plot

Returns
-------
bokeh.plotting figure object containing a raster graphics plot

Notes
-----
USAGE EXAMPLE::

  gdata = mtr_graph_data(...)
  gplot = xtr_graph_plot(gdata)

THEN when working interactively in a Python notebook::

  bp.show(gplot)

OR when executing script using Python command-line interpreter::

  bp.output_file('graph-name.html', title='?TR by Income Percentile')
  bp.show(gplot)  [OR bp.save(gplot) WILL JUST WRITE FILE TO DISK]

WILL VISUALIZE GRAPH IN BROWSER AND WRITE GRAPH TO SPECIFIED HTML FILE

To convert the visualized graph into a PNG-formatted file, click on
the "Save" icon on the Toolbar (located in the top-right corner of
the visualized graph) and a PNG-formatted file will written to your
Download directory.

The ONLY output option the bokeh.plotting figure has is HTML format,
which (as described above) can be converted into a PNG-formatted
raster graphics file.  There is no option to make the bokeh.plotting
figure generate a vector graphics file such as an EPS file.
```

## pch_graph_data

```python
def pch_graph_data(vdf, year, pop_quantiles=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1200)

```text
Prepare percentage change in after-tax expanded income data needed by
pch_graph_plot utility function.

Parameters
----------
vdf : a Pandas DataFrame object containing variables
    (See Calculator.pch_graph method for required elements of vdf.)

year : integer
    specifies calendar year of the data in vdf

pop_quantiles : boolean
    specifies whether or not quantiles contain an equal number
    of people (True) or an equal number of filing units (False)

Returns
-------
dictionary object suitable for passing to pch_graph_plot utility function
```

## pch_graph_plot

```python
def pch_graph_plot(data, width=850, height=500, xlabel='', ylabel='', title='')
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1267)

```text
Plot percentage change in after-tax expanded income using data returned
from the pch_graph_data function.

Parameters
----------
data : dictionary object returned from ?tr_graph_data() utility function

width : integer
    width of plot expressed in pixels

height : integer
    height of plot expressed in pixels

xlabel : string
    x-axis label; if '', then use label generated by pch_graph_data

ylabel : string
    y-axis label; if '', then use label generated by pch_graph_data

title : string
    graph title; if '', then use title generated by pch_graph_data

Returns
-------
bokeh.plotting figure object containing a raster graphics plot

Notes
-----
See Notes to xtr_graph_plot function.
```

## write_graph_file

```python
def write_graph_file(figure, filename, title)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1330)

```text
Write HTML file named filename containing figure.
The title is the text displayed in the browser tab.

Parameters
----------
figure : bokeh.plotting figure object

filename : string
    name of HTML file to which figure is written; should end in .html

title : string
    text displayed in browser tab when HTML file is displayed in browser

Returns
-------
Nothing
```

## isoelastic_utility_function

```python
def isoelastic_utility_function(consumption, crra, cmin)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1355)

```text
Calculate and return utility of consumption.

Parameters
----------
consumption : float
  consumption for a filing unit

crra : non-negative float
  constant relative risk aversion parameter

cmin : positive float
  consumption level below which marginal utility is assumed to be constant

Returns
-------
utility of consumption
```

## expected_utility

```python
def expected_utility(consumption, probability, crra, cmin)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1388)

```text
Calculate and return expected utility of consumption.

Parameters
----------
consumption : numpy array
  consumption for each filing unit

probability : numpy array
  samplying probability of each filing unit

crra : non-negative float
  constant relative risk aversion parameter of isoelastic utility function

cmin : positive float
  consumption level below which marginal utility is assumed to be constant

Returns
-------
expected utility of consumption array
```

## certainty_equivalent

```python
def certainty_equivalent(exputil, crra, cmin)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1415)

```text
Calculate and return certainty-equivalent of exputil of consumption
assuming an isoelastic utility function with crra and cmin as parameters.

Parameters
----------
exputil : float
  expected utility value

crra : non-negative float
  constant relative risk aversion parameter of isoelastic utility function

cmin : positive float
  consumption level below which marginal utility is assumed to be constant

Returns
-------
certainty-equivalent of specified expected utility, exputil
```

## ce_aftertax_expanded_income

```python
def ce_aftertax_expanded_income(df1, df2, custom_params=None, require_no_agg_tax_change=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1447)

```text
Return dictionary that contains certainty-equivalent of the
expected utility of after-tax expanded income computed for
several constant-relative-risk-aversion parameter values
for each of two Pandas DataFrame objects: df1, which represents
the pre-reform situation, and df2, which represents the
post-reform situation.  Both DataFrame objects must contain
's006', 'combined', and 'expanded_income' columns.

IMPORTANT NOTES: These normative welfare calculations are very simple.
It is assumed that utility is a function of only consumption, and that
consumption is equal to after-tax income.  This means that any assumed
responses that change work effort will not affect utility via the
correpsonding change in leisure.  And any saving response to changes
in after-tax income do not affect consumption.

The cmin value is the consumption level below which marginal utility
is considered to be constant.  This allows the handling of filing units
with very low or even negative after-tax expanded income in the
expected-utility and certainty-equivalent calculations.
```

## read_egg_csv

```python
def read_egg_csv(fname, index_col=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1525)

```text
Read from egg the file named fname that contains CSV data and
return pandas DataFrame containing the data.
```

## read_egg_json

```python
def read_egg_json(fname)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1540)

```text
Read from egg the file named fname that contains JSON data and
return dictionary containing the data.
```

## delete_file

```python
def delete_file(filename)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1555)

```text
Remove specified file if it exists.
```

## bootstrap_se_ci

```python
def bootstrap_se_ci(data, seed, num_samples, statistic, alpha)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1563)

```text
Return bootstrap estimate of standard error of statistic and
bootstrap estimate of 100*(1-2*alpha)% confidence interval for statistic
in a dictionary along with specified seed and nun_samples (B) and alpha.
```

## json_to_dict

```python
def json_to_dict(jsontext)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/utils.py#L1590)

```text
Convert specified JSON text into an ordered Python dictionary.

Parameters
----------
jsontext: string
    JSON text that may contain comments, which will be removed

Raises
------
ValueError:
    if jsontext contains a JSON syntax error after comments are removed

Returns
-------
dictionary: collections.OrderedDict
    JSON data expressed as an ordered Python dictionary
```
