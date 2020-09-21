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

# Recipe 2: Estimating Behavioral Response to Reform

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe shows how to analyze the behavioral responses to a tax reform using the Behavioral-Responses behresp package.

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
    !yes | conda install -c PSLmodels taxcalc behresp
```

```{code-cell} ipython3
:hide-output: false

import taxcalc as tc
import behresp

# use publicly-available CPS input file
recs = tc.Records.cps_constructor()

# specify baseline Calculator object representing current-law policy
pol = tc.Policy()
calc1 = tc.Calculator(policy=pol, records=recs)

CYR = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc1.advance_to_year(CYR)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# specify Calculator object for static analysis of reform policy
pol.implement_reform(tc.Policy.read_json_reform('_static/reformA.json'))
calc2 = tc.Calculator(policy=pol, records=recs)

# calculate reform income tax liabilities for cyr under static assumptions
calc2.advance_to_year(CYR)
calc2.calc_all()
itax_rev2sa = calc2.weighted_total('iitax')

# specify assumed non-zero response-function substitution elasticity
response_elasticities = {'sub': 0.25}

# specify Calculator object for analysis of reform with behavioral responses
calc2 = tc.Calculator(policy=pol, records=recs)
calc2.advance_to_year(CYR)
_, df2br = behresp.response(calc1, calc2, response_elasticities)

# calculate reform income tax liabilities for CYR with behavioral response
itax_rev2br = (df2br['iitax'] * df2br['s006']).sum()

# print total income tax revenue estimates for CYR
# (estimates in billons of dollars)
print('{}_CURRENT_LAW_P__itax_rev($B)= {:.3f}'.format(CYR, itax_rev1 * 1e-9))
print('{}_REFORM_STATIC__itax_rev($B)= {:.3f}'.format(CYR, itax_rev2sa * 1e-9))
print('{}_REFORM_DYNAMIC_itax_rev($B)= {:.3f}'.format(CYR, itax_rev2br * 1e-9))
```

Create multi-year diagnostic tables for
1. baseline,
2. reform excluding behavioral responses, and
3. reform including behavioral responses

```{code-cell} ipython3
:hide-output: false

NUM_YEARS = 3  # number of diagnostic table years beginning with CYR
dtable1 = calc1.diagnostic_table(NUM_YEARS)
dtable2 = calc2.diagnostic_table(NUM_YEARS)
dvar_list3 = list()
year_list3 = list()
for year in range(CYR, CYR + NUM_YEARS):
    calc1.advance_to_year(year)
    calc2.advance_to_year(year)
    _, df2br = behresp.response(calc1, calc2, response_elasticities)
    dvar_list3.append(df2br)
    year_list3.append(year)
dtable3 = tc.create_diagnostic_table(dvar_list3, year_list3)
```

Diagnostic table for baseline:

```{code-cell} ipython3
:hide-output: false

dtable1
```

Diagnostic table for reform, excluding behavioral responses:

```{code-cell} ipython3
:hide-output: false

dtable2
```

Diagnostic table for reform, including behavioral responses:

```{code-cell} ipython3
:hide-output: false

dtable3
```
