# Tax-Calculator IO

Documentation of the `taxcalc.taxcalcio` module.

## TaxCalcIO

```python
class TaxCalcIO(input_data, tax_year, baseline, reform, assump, behavior, runid=0, silent=True)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L29)

```text
Constructor for the Tax-Calculator Input-Output class.

TaxCalcIO class constructor call must be followed by init() call.

Parameters
----------
input_data: string or Pandas DataFrame
    string is name of INPUT file that is CSV formatted containing
    variable names in the Records USABLE_READ_VARS set, or
    Pandas DataFrame is INPUT data containing variable names in
    the Records USABLE_READ_VARS set.  INPUT vsrisbles not in the
    Records USABLE_READ_VARS set can be present but are ignored.

tax_year: integer
    calendar year for which taxes will be computed for INPUT.

baseline: None or string
    None implies baseline policy is current-law policy, or
    string is name of optional BASELINE file that is a JSON
    reform file.

reform: None or string
    None implies no policy reform (current-law policy), or
    string is name of optional REFORM file(s).

assump: None or string
    None implies economic assumptions are standard assumptions,
    or string is name of optional ASSUMP file.

behavior: None or string
    None implies behavioral response elasticities are all zero,
    or string is name of optional BEHAVIOR file.

runid: int
    run id value to use for simpler output file names

silent: boolean
    whether or not to suppress action messages.

Returns
-------
class instance: TaxCalcIO
```

### TaxCalcIO.delete_output_files

```python
def delete_output_files(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L133)

```text
Delete all output files derived from self.output_filename.
```

### TaxCalcIO.init

```python
def init(self, input_data, tax_year, baseline, reform, assump, behavior, exact_calculations)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L149)

```text
TaxCalcIO class post-constructor method that completes initialization.

Parameters
----------
First six are same as the first six of the TaxCalcIO constructor:
    input_data, tax_year, baseline, reform, assump, behavior.

exact_calculations: boolean
    specifies whether or not exact tax calculations are done without
    any smoothing of "stair-step" provisions in the tax law.
```

### TaxCalcIO.tax_year

```python
def tax_year(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L288)

```text
Return calendar year for which TaxCalcIO calculations are being done.
```

### TaxCalcIO.output_filepath

```python
def output_filepath(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L294)

```text
Return full path to output file named in TaxCalcIO constructor.

Note that output files are written using the bare
self.output_filename, so they are located in the current working
directory, which is what this method returns a path into.
```

### TaxCalcIO.advance_to_year

```python
def advance_to_year(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L304)

```text
Update self.output_filename and create Calculator objects for year.
```

### TaxCalcIO.analyze

```python
def analyze(self, output_params=False, output_jsonparams=False, output_tables=False, output_graphs=False, output_dump=False, dump_varlist=None)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L335)

```text
Conduct tax analysis.

Parameters
----------
output_params: boolean
   whether or not to write baseline and reform policy parameter
   values to separate text files

output_jsonparams: boolean
   whether the baseline and reform policy parameter files written
   when output_params is True use JSON format rather than text format

output_tables: boolean
   whether or not to generate and write distributional tables
   to a text file

output_graphs: boolean
   whether or not to generate and write HTML graphs of average
   and marginal tax rates by income percentile

output_dump: boolean
   whether or not to write SQLite3 database with baseline and
   reform tables each containing the variables in dump_varlist.

dump_varlist: list
   list of variables to include in dumpdb output;
   list must include at least one variable.

Returns
-------
Nothing
```

### TaxCalcIO.write_policy_params_files

```python
def write_policy_params_files(self, jsonparams=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L438)

```text
Write baseline and reform policy parameter values to separate files.
```

### TaxCalcIO.dump_variables

```python
def dump_variables(self, dumpvars_str)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L472)

```text
Return list of variable names extracted from dumpvars_str, plus
minimal baseline/reform variables even if not in dumpvars_str.
Also, appends to self.errmsg if any specified variables are not valid.
```

### TaxCalcIO._filename_for_year

```python
def _filename_for_year(self, year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L522)

```text
Return output file name for the specified year.
```

### TaxCalcIO._output_filename_with

```python
def _output_filename_with(self, ext)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L528)

```text
Return self.output_filename with its trailing .xxx replaced by ext.

Note that only the trailing .xxx is replaced because the stem or
tail of the output file name may itself contain the .xxx string.
```

### TaxCalcIO._check_input_data

```python
def _check_input_data(self, input_data)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L537)

```text
Check the INPUT data specified in the constructor, appending any
errors to self.errmsg, and return the year-independent part of the
output file name.
```

### TaxCalcIO._check_tmd_files

```python
def _check_tmd_files(self, input_data, stem)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L581)

```text
Check the TMD weights and growfactors files that are in the same
folder as the TMD INPUT file, appending any errors to self.errmsg.
Return the stem of the output file name, which includes any
TMD_AREA value.
```

### TaxCalcIO._check_file_arg

```python
def _check_file_arg(self, arg, label, check_files)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L621)

```text
Check the type of the optional arg, which must be None or a file
specification string that is checked by the check_files method,
and return the fragment used in constructing output file names.
```

### TaxCalcIO._read_behavior_file

```python
def _read_behavior_file(self, behavior)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L635)

```text
Read the BEHAVIOR file into self.behvdict and check the elasticity
names and values it contains, appending any errors to self.errmsg.
Return True if no errors were found; otherwise return False.
```

### TaxCalcIO._read_poldicts

```python
def _read_poldicts(filespec, specified)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L678)

```text
Return list containing the policy parameter dictionary in each of
the (possibly several) JSON files named in the BASELINE or REFORM
filespec; return an empty list if no filespec was specified.
```

### TaxCalcIO._make_growdiff

```python
def _make_growdiff(self, growdiff_dict, last_b_year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L691)

```text
Return GrowDiff object updated using growdiff_dict, appending any
parameter errors to self.errmsg.
```

### TaxCalcIO._check_policy_files

```python
def _check_policy_files(self, filespec, label)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L703)

```text
Check validity of the (possibly compound) BASELINE or REFORM filespec,
appending any errors to self.errmsg, and return the name fragment used
in constructing output file names.
```

### TaxCalcIO._check_single_json_file

```python
def _check_single_json_file(self, path, label)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L737)

```text
Check name and existence of the single ASSUMP or BEHAVIOR file,
appending any errors to self.errmsg, and return the name fragment
used in constructing output file names.
```

### TaxCalcIO._make_policy

```python
def _make_policy(policy_gfactors, last_b_year)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L757)

```text
Return Policy object that uses the specified growfactors.
```

### TaxCalcIO._apply_poldicts

```python
def _apply_poldicts(self, pol, poldicts)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L766)

```text
Implement each reform dict in poldicts on the pol Policy object,
appending any parameter errors to self.errmsg.
```

### TaxCalcIO._make_records

```python
def _make_records(self, gfactors, input_data, tax_year, exact_calculations)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L786)

```text
Construct and return a Records object using the specified gfactors
and the input data type implied by the constructor arguments.
```

### TaxCalcIO._make_calculator

```python
def _make_calculator(self, policy, records, verbose)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L815)

```text
Construct and return a Calculator object from the specified policy
and records objects.
```

### TaxCalcIO._copy_dump_into_calc

```python
def _copy_dump_into_calc(self, calc, br_dump)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L828)

```text
Copy behavioral-response dump DataFrame values back into the calc
object, skipping the marginal-tax-rate columns.

Note that after this method is called, the calc object contains
input and output variables that incorporate behavioral responses,
which means those variables are no longer the ones that a plain
calc_all() call on the calc object would generate from its own
Policy parameters.  Any subsequent calc_all() call on the calc
object would recalculate output variables from the response-
adjusted input variables; the mtr method is called with
calc_all_already_called=True in order to avoid doing that.
```

### TaxCalcIO._write_params

```python
def _write_params(self, calc, ext, label, jsonparams=False)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L853)

```text
Write policy parameter values from calc to the ext output file.
```

### TaxCalcIO._write_tables_file

```python
def _write_tables_file(self)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L883)

```text
Write tables to text file.
```

### TaxCalcIO._write_decile_table

```python
def _write_decile_table(dfx, tfile, year, tkind='Totals')
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L934)

```text
Write to tfile the tkind decile table using dfx DataFrame.
```

### TaxCalcIO._write_graph_files

```python
def _write_graph_files(self, mtr_bas, mtr_ref)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L990)

```text
Write graphs to HTML files, using the mtr_bas and mtr_ref tuples
of marginal tax rate arrays (returned by the mtr method of the
baseline and reform Calculator objects) to construct the MTR graph.
All graphs contain same number of filing units in each quantile.
```

### TaxCalcIO._write_empty_graph_file

```python
def _write_empty_graph_file(fname, title, reason)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L1034)

```text
Write HTML graph file with title but no graph for specified reason.
```

### TaxCalcIO._write_dumpdb_table

```python
def _write_dumpdb_table(dframe, tname, dbcon)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L1048)

```text
Write dframe contents to a new tname table in the dbcon database.

Note that this produces the same table schema and contents as
dframe.to_sql(tname, dbcon, index=False) but is substantially
faster for the wide dump tables because the rows are passed to
SQLite directly without the pandas to_sql overhead.
```

### TaxCalcIO._write_dumpdb_file

```python
def _write_dumpdb_file(self, dump_varlist, mtr_bas, mtr_ref)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/taxcalcio.py#L1066)

```text
Write dump output to SQLite database file, where mtr_bas and
mtr_ref are either None (when dump_varlist contains no MTR
variables) or the (ptax, itax, combined) tuples of marginal tax
rate arrays returned by the mtr method of the baseline and reform
Calculator objects.
```
