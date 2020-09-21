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

# Recipe 1: Directly Comparing Two Reforms

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe shows how to compare two reforms (instead of comparing a reform to current-law policy)
and also shows how to use the reform files available on the Tax-Calculator website
(instead of reform files on your computer’s disk).

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

import pandas as pd
import taxcalc as tc

# read an "old" reform file
# ("old" means the reform file is defined relative to pre-TCJA policy)
REFORMS_PATH = '../../taxcalc/reforms/'

# specify reform dictionary for pre-TCJA policy
reform1 = tc.Policy.read_json_reform(REFORMS_PATH + '2017_law.json')

# specify reform dictionary for TCJA as passed by Congress in late 2017
reform2 = tc.Policy.read_json_reform(REFORMS_PATH + 'TCJA.json')

# specify Policy object for pre-TCJA policy
bpolicy = tc.Policy()
bpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
assert not bpolicy.parameter_errors

# specify Policy object for TCJA reform relative to pre-TCJA policy
rpolicy = tc.Policy()
rpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
assert not rpolicy.parameter_errors
rpolicy.implement_reform(reform2, print_warnings=False, raise_errors=False)
assert not rpolicy.parameter_errors

# specify Calculator objects using bpolicy and rpolicy
recs = tc.Records.cps_constructor()
calc1 = tc.Calculator(policy=bpolicy, records=recs)
calc2 = tc.Calculator(policy=rpolicy, records=recs)

CYR = 2018

# calculate for specified CYR
calc1.advance_to_year(CYR)
calc1.calc_all()
calc2.advance_to_year(CYR)
calc2.calc_all()

# compare aggregate individual income tax revenue in cyr
iitax_rev1 = calc1.weighted_total('iitax')
iitax_rev2 = calc2.weighted_total('iitax')

# construct reform-vs-baseline difference table with results for income deciles
diff_table = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tax_cut', 'tax_inc',
                'tot_change', 'mean', 'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'taxfall(#m)', 'taxrise(#m)',
                'agg_diff($b)', 'mean_diff($)', 'aftertax_income_diff(%)']
for dname, ename in zip(dif_colnames, ext_colnames):
    diff_extract[ename] = diff_table[dname]

# print total revenue estimates for cyr
# (estimates in billons of dollars)
print('{}_REFORM1_iitax_rev($B)= {:.3f}'.format(CYR, iitax_rev1 * 1e-9))
print('{}_REFORM2_iitax_rev($B)= {:.3f}'.format(CYR, iitax_rev2 * 1e-9))
print('')
```

Print reform2-vs-reform1 difference table

```{code-cell} ipython3
:hide-output: false

title = 'Extract of {} income-tax difference table by expanded-income decile'
print(title.format(CYR))
print('(taxfall is count of funits with cut in income tax in reform 2 vs 1)')
print('(taxrise is count of funits with rise in income tax in reform 2 vs 1)')
print(diff_extract.to_string())
```
