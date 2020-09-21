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

# Recipe 3: Creating a Custom Table

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe shows how to prepare a custom table.

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
import numpy as np

# use publicly-available CPS input file
recs = tc.Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = tc.Policy()
calc = tc.Calculator(policy=pol, records=recs)

CYR = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc.advance_to_year(CYR)
calc.calc_all()

# tabulate custom table showing number of filing units receiving EITC
# and the average positive EITC amount by IRS-SOI AGI categories
vardf = calc.dataframe(['s006', 'c00100', 'eitc'])
vardf = tc.add_income_table_row_variable(vardf, 'c00100', tc.SOI_AGI_BINS)
gbydf = vardf.groupby('table_row', as_index=False)
```

Filing Units Receiving EITC and Average Positive EITC by AGI Category

```{code-cell} ipython3
:hide-output: false

# print AGI table with ALL row at bottom
results = '{:23s}\t{:8.3f}\t{:8.3f}'
colhead = '{:23s}\t{:>8s}\t{:>8s}'
print(colhead.format('AGI Category', 'Num(#M)', 'Avg($K)'))
tot_recips = 0.
tot_amount = 0.
idx = 0
for grp_interval, grp in gbydf:
    recips = grp[grp['eitc'] > 0]['s006'].sum() * 1e-6
    tot_recips += recips
    amount = (grp['eitc'] * grp['s006']).sum() * 1e-9
    tot_amount += amount
    if recips > 0:
        avg = amount / recips
    else:
        avg = np.nan
    glabel = '[{:.8g}, {:.8g})'.format(grp_interval.left, grp_interval.right)
    print(results.format(glabel, recips, avg))
    idx += 1
avg = tot_amount / tot_recips
print(results.format('ALL', tot_recips, avg))
```
