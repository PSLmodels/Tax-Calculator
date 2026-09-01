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
This recipe shows how to analyze the behavioral responses to a tax reform using the Tax-Calculator behresp module.

The assumed elasticities below specify a substitution elasticity of taxable income of 0.25 and leave the income elasticity (`inc`) and the capital-gains semi-elasticity (`cg`) at their default value of zero, so only the substitution response channel is active.
Each elasticity is documented on the [behavior parameters](../guide/behavior_params) page.

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
# (the omitted 'esf', 'inc' and 'cg' parameters are assumed to be zero)
response_elasticities = {'sub': 0.25}

# specify Calculator object for analysis of reform with behavioral responses
# (the response function returns baseline and reform DataFrame objects and
#  leaves calc1 and calc2 unchanged; the discarded first DataFrame contains
#  the baseline results, which are the same as the calc1 results above)
calc2 = tc.Calculator(policy=pol, records=recs)
calc2.advance_to_year(CYR)
_, df2br = tc.response(calc1, calc2, response_elasticities)

# calculate reform income tax liabilities for CYR with behavioral response
# (weighted_total cannot be used here because the response function returns
#  a DataFrame rather than a Calculator object, so the weighting by the s006
#  filing-unit sampling weight must be done explicitly)
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

Each year in the loop below is analyzed independently: the response function is called once per year and no response computed in one year is carried over into another year.
This means that retiming behavior, most notably the realization timing of capital gains, is not being modeled.

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
    _, df2br = tc.response(calc1, calc2, response_elasticities)
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
