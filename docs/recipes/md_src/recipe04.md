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

# Recipe 4: Estimating Differential Reform Response

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
# TODO: Move this reform online so it can be read non-locally.
pol.implement_reform(tc.Policy.read_json_reform('_static/reformB.json'))
calc2 = tc.Calculator(policy=pol, records=recs)

# calculate reform tax liabilities for CYR
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
earnings_bins = [-9e99, 50e3, 9e99]  # two groups: below and above $50,000
vdf = tc.add_income_table_row_variable(vdf, 'e00200', earnings_bins)
gbydf = vdf.groupby('table_row', as_index=False)

# compute percentage response in charitable giving
# (note elasticity values are just an example based on no empirical results)
PRICE_ELASTICITY = [-0.1, -0.4]
INCOME_ELASTICITY = [0.1, 0.1]
print('\nResponse in Charitable Giving by Earnings Group')
results = '{:18s}\t{:8.3f}\t{:8.3f}\t{:8.2f}'
colhead = '{:18s}\t{:>8s}\t{:>8s}\t{:>8s}'
print(colhead.format('Earnings Group', 'Num(#M)', 'Resp($B)', 'Resp(%)'))
tot_funits = 0.
tot_response = 0.
tot_baseline = 0.
idx = 0
for grp_interval, grp in gbydf:
    funits = grp['s006'].sum() * 1e-6
    tot_funits += funits
    response = behresp.quantity_response(grp['e19800'],
                                         PRICE_ELASTICITY[idx],
                                         grp['price1'],
                                         grp['price2'],
                                         INCOME_ELASTICITY[idx],
                                         grp['atinc1'],
                                         grp['atinc2'])
    grp_response = (response * grp['s006']).sum() * 1e-9
    tot_response += grp_response
    grp_baseline = (grp['e19800'] * grp['s006']).sum() * 1e-9
    tot_baseline += grp_baseline
    pct_response = 100. * grp_response / grp_baseline
    glabel = '[{:.8g}, {:.8g})'.format(grp_interval.left, grp_interval.right)
    print(results.format(glabel, funits, grp_response, pct_response))
    idx += 1
pct_response = 100. * tot_response / tot_baseline
print(results.format('ALL', tot_funits, tot_response, pct_response))
```
