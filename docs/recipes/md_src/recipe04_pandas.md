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

# Recipe 4: Estimating Differential Reform Response - pandas version

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe shows how to estimate the reform response in charitable giving when the response elasticities vary by earnings group.
It employs the groupby technique used in the Creating a Custom Table recipe, so you might want to read that recipe first.

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
import pandas as pd
import numpy as np
import behresp

# use publicly-available CPS input file
recs = tc.Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = tc.Policy()
calc1 = tc.Calculator(policy=pol, records=recs)

CYR = 2020

# calculate current-law tax liabilities for CYR
calc1.advance_to_year(CYR)
calc1.calc_all()

# calculate marginal tax rate wrt cash charitable giving
(_, _, mtr1) = calc1.mtr('e19800', calc_all_already_called=True,
                         wrt_full_compensation=False)

# specify Calculator object for static analysis of reform policy
# TODO: Move this reform online so this can be run non-locally.
pol.implement_reform(tc.Policy.read_json_reform('_static/reformB.json'))
calc2 = tc.Calculator(policy=pol, records=recs)

# calculate reform tax liabilities for cyr
calc2.advance_to_year(CYR)
calc2.calc_all()

# calculate marginal tax rate wrt cash charitable giving
(_, _, mtr2) = calc2.mtr('e19800', calc_all_already_called=True,
                         wrt_full_compensation=False)

# extract variables needed for quantity_response function
# (note the aftertax price is 1+mtr because mtr wrt charity is non-positive)
vdf = calc1.dataframe(['s006', 'e19800', 'e00200'])
vdf['price1'] = 1.0 + mtr1
vdf['price2'] = 1.0 + mtr2
vdf['atinc1'] = calc1.array('aftertax_income')
vdf['atinc2'] = calc2.array('aftertax_income')

# group filing units into earnings groups with different response elasticities
# (note earnings groups are just an example based on no empirical results)
EARNINGS_BINS = [-9e99, 50e3, 9e99]  # Two groups: below and above $50,000.
vdf['table_row'] = pd.cut(vdf.e00200, EARNINGS_BINS, right=False).astype(str)

vdf['price_elasticity'] = np.where(vdf.e00200 < EARNINGS_BINS[1],
                                   -0.1, -0.4)
vdf['income_elasticity'] = 0.1

# create copies of vdf and subset by price elasticity
vdf_1 = vdf.copy()
vdf_2 = vdf.copy()

vdf_1 = vdf_1.loc[vdf_1['price_elasticity']==-0.1]
vdf_2 = vdf_2.loc[vdf_2['price_elasticity']==-0.4]

# Calculate response based on features of each filing unit.
# Call quantity_response for each subset (i.e. vdf_1 and vdf_2)
vdf_1['response'] = behresp.quantity_response(quantity=vdf_1.e19800,
                                              price_elasticity=-0.1,
                                              aftertax_price1=vdf_1.price1,
                                              aftertax_price2=vdf_1.price2,
                                              income_elasticity=0.1,
                                              aftertax_income1=vdf_1.atinc1,
                                              aftertax_income2=vdf_1.atinc2)

vdf_2['response'] = behresp.quantity_response(quantity=vdf_2.e19800,
                                              price_elasticity=-0.4,
                                              aftertax_price1=vdf_2.price1,
                                              aftertax_price2=vdf_2.price2,
                                              income_elasticity=0.1,
                                              aftertax_income1=vdf_2.atinc1,
                                              aftertax_income2=vdf_2.atinc2)

vdf = pd.concat([vdf_1, vdf_2])

# Add weighted totals.
# Can also use microdf as mdf.add_weighted_totals(vdf, ['response', 'e19800'])
vdf['e19800_b'] = vdf.s006 * vdf.e19800 / 1e9
vdf['response_b'] = vdf.s006 * vdf.response / 1e9
vdf['funits_m'] = vdf.s006 / 1e6

SUM_VARS = ['funits_m', 'e19800_b', 'response_b']
# Sum weighted total columns for each income group.
grouped = vdf.groupby('table_row')[SUM_VARS].sum()
# Add a total row and make the index a column for printing.
grouped.loc['TOTAL'] = grouped.sum()
grouped.reset_index(inplace=True)

# Calculate percent response and drop unnecessary total.
grouped['pct_response'] = 100 * grouped.response_b / grouped.e19800_b
grouped.drop('e19800_b', axis=1, inplace=True)

# Rename columns for printing.
grouped.columns = ['Earnings Group', 'Num(#M)', 'Resp($B)', 'Resp(%)']
```

Result: Response in Charitable Giving by Earnings Group

```{code-cell} ipython3
:hide-output: false

grouped.round(3)
```
