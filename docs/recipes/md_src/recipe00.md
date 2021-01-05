---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: '0.8'
    jupytext_version: 1.5.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Basic Recipe: Static Analysis of a Simple Reform

This is the recipe you should follow first.
Mastering this recipe is a prerequisite for all the other recipes in this cookbook.

## Imports

```{code-cell} ipython3
:tags: [remove-cell]

# Install conda and taxcalc if in Google Colab.
import sys
if 'google.colab' in sys.modules and 'taxcalc' not in sys.modules:
    !wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    !bash Miniconda3-latest-Linux-x86_64.sh -bfp /usr/local
    # Append path to be able to run packages installed with conda
    # This must correspond to the conda Python version, which may differ from
    # the base Colab Python installation.
    sys.path.append('/usr/local/lib/python3.8/site-packages')
    # Install PSL packages from Anaconda
    !yes | conda install -c conda-forge paramtools
    !yes | conda install -c PSLmodels taxcalc
```

```{code-cell} ipython3
:hide-output: false

import taxcalc as tc
import pandas as pd
from bokeh.io import show, output_notebook
```

## Setup

Use publicly-available CPS input file.

NOTE: if you have access to the restricted-use IRS-SOI PUF-based input file
and you have that file (named ‘puf.csv’) located in the directory
where this script is located, then you can substitute the following
statement for the prior statement:

``
recs = tc.Records()
``

```{code-cell} ipython3
:hide-output: false

recs = tc.Records.cps_constructor()
```

Specify Calculator object for static analysis of current-law policy.

```{code-cell} ipython3
:hide-output: false

pol = tc.Policy()
calc1 = tc.Calculator(policy=pol, records=recs)
```

NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
so we can continue to use pol and recs in this script without any
concern about side effects from Calculator method calls on calc1.

```{code-cell} ipython3
:hide-output: false

CYR = 2020
```

Calculate aggregate current-law income tax liabilities for CYR.

```{code-cell} ipython3
:hide-output: false

calc1.advance_to_year(CYR)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')
```

Read JSON reform file and use (the default) static analysis assumptions.

```{code-cell} ipython3
:hide-output: false

reform_filename = '_static/reformA.json'
params = tc.Calculator.read_json_param_objects(reform_filename, None)
```

Specify Calculator object for static analysis of reform policy.

```{code-cell} ipython3
:hide-output: false

pol.implement_reform(params['policy'])
calc2 = tc.Calculator(policy=pol, records=recs)
```

## Calculate

Calculate reform income tax liabilities for CYR.

```{code-cell} ipython3
:hide-output: false

calc2.advance_to_year(CYR)
calc2.calc_all()
itax_rev2 = calc2.weighted_total('iitax')
```

## Results

Print total revenue estimates for 2018.

*Estimates in billons of dollars rounded to nearest hundredth of a billion.*

```{code-cell} ipython3
:hide-output: false

print('{}_CLP_itax_rev($B)= {:.3f}'.format(CYR, itax_rev1 * 1e-9))
print('{}_REF_itax_rev($B)= {:.3f}'.format(CYR, itax_rev2 * 1e-9))
```

Generate several other standard results tables.

```{code-cell} ipython3
:hide-output: false

# Aggregate diagnostic tables for CYR.
clp_diagnostic_table = calc1.diagnostic_table(1)
ref_diagnostic_table = calc2.diagnostic_table(1)

# Income-tax distribution for CYR with CLP and REF results side-by-side.
dist_table1, dist_table2 = calc1.distribution_tables(calc2, 'weighted_deciles')
assert isinstance(dist_table1, pd.DataFrame)
assert isinstance(dist_table2, pd.DataFrame)
dist_extract = pd.DataFrame()
dist_extract['funits(#m)'] = dist_table1['count']
dist_extract['itax1($b)'] = dist_table1['iitax']
dist_extract['itax2($b)'] = dist_table2['iitax']
dist_extract['aftertax_inc1($b)'] = dist_table1['aftertax_income']
dist_extract['aftertax_inc2($b)'] = dist_table2['aftertax_income']

# Income-tax difference table by expanded-income decile for CYR.
diff_table = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tot_change', 'mean', 'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'agg_diff($b)', 'mean_diff($)', 'aftertaxinc_diff(%)']
for dname, ename in zip(dif_colnames, ext_colnames):
    diff_extract[ename] = diff_table[dname]
```

## Plotting

Generate a decile graph and display it using Bokeh (will render in Jupyter, not in webpage).

```{code-cell} ipython3
:hide-output: false

fig = calc1.pch_graph(calc2)
output_notebook()
show(fig)
```

## Print tables

CLP diagnostic table for CYR.

```{code-cell} ipython3
:hide-output: false

clp_diagnostic_table
```

REF diagnostic table for CYR.

```{code-cell} ipython3
:hide-output: false

ref_diagnostic_table
```

Extract of CYR distribution tables by baseline expanded-income decile.

```{code-cell} ipython3
:hide-output: false

dist_extract
```

Extract of CYR income-tax difference table by expanded-income decile.

```{code-cell} ipython3
:hide-output: false

diff_extract
```
