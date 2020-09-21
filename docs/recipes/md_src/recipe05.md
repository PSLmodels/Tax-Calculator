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

# Recipe 5: Redefining Expanded Income

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe is almost exactly the same as Directly Comparing Two Reforms, so you might want to read that recipe first.

This recipe introduces a powerful technique for customizing the operation of Tax-Calculator.
This calculator-customization technique is used in this recipe to redefine expanded income in a way that allows the
redefined income measure to be used seamlessly with all the other (table and graph) methods of the Calculator class.
The basic idea behind the calculator-customization technique is to derive a customized Calculator class from the Tax-Calculator Calculator class.
This is a standard [object-oriented programming](https://pslmodels.github.io/Tax-Calculator/tc_overview.html) technique.

Recipe that illustrates how to customize the taxcalc Calculator class so that
it can seamlessly use an alternative definition of expanded income.

The technique for doing this customization is standard in object-oriented
programming: a child class is derived from a parent class and then customized.
The derived child class inherits all the data and methods of the parent class,
but can be customized by adding new data and methods or by overriding inherited
methods.

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


# override the ExpandIncome calcfunction that computes "market income"


@tc.iterate_jit(nopython=True)
def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600,
                 e00700, e00800, e00900, e01100, e01200, e01400, e01500,
                 e02000, e02100, p22250, p23250, cmbtp, ptax_was,
                 expanded_income):
    """
    Calculates expanded_income as "market income" from component income types.
    """
    expanded_income = (
        e00200 +  # wage and salary income net of DC pension contributions
        pencon_p +  # tax-advantaged DC pension contributions for taxpayer
        pencon_s +  # tax-advantaged DC pension contributions for spouse
        e00300 +  # taxable interest income
        e00400 +  # non-taxable interest income
        e00600 +  # dividends
        e00700 +  # state and local income tax refunds
        e00800 +  # alimony received
        e00900 +  # Sch C business net income/loss
        e01100 +  # capital gain distributions not reported on Sch D
        e01200 +  # Form 4797 other net gain/loss
        e01400 +  # taxable IRA distributions
        e01500 +  # total pension & annuity income (including DB-plan benefits)
        e02000 +  # Sch E total rental, ..., partnership, S-corp income/loss
        e02100 +  # Sch F farm net income/loss
        p22250 +  # Sch D: net short-term capital gain/loss
        p23250 +  # Sch D: net long-term capital gain/loss
        cmbtp +  # other AMT taxable income items from Form 6251
        0.5 * ptax_was  # employer share of FICA taxes on wages/salaries
        # excluding:
        # ubi +  # total UBI benefit
        # benefit_value_total  # consumption value of all benefits received;
    )
    return expanded_income

# end overrided calcfunction used by customized Calculator class


class Calculator(tc.Calculator):
    """
    Customized Calculator class that inherits all tc.Calculator data and
    methods, overriding one method to get the desired customization.
    """
    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None):
        # use same class constructor arguments as tc.Calculator class
        super().__init__(policy=policy, records=records,
                         verbose=verbose, sync_years=sync_years,
                         consumption=consumption)

    def calc_all(self, zero_out_calc_vars=False):
        """
        Call all tax-calculation functions for the current_year.
        """
        tc.BenefitPrograms(self)
        self._calc_one_year(zero_out_calc_vars)
        tc.BenefitSurtax(self)
        tc.BenefitLimitation(self)
        tc.FairShareTax(self.__policy, self.__records)
        tc.LumpSumTax(self.__policy, self.__records)
        ExpandIncome(self.__policy, self.__records)  # customized (see above)
        tc.AfterTaxIncome(self.__policy, self.__records)

# end of customized Calculator class definition


# top-level logic of program that uses customized Calculator class

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

# specify customized Calculator objects using bpolicy and rpolicy
recs = tc.Records.cps_constructor()
calc1 = Calculator(policy=bpolicy, records=recs)
calc2 = Calculator(policy=rpolicy, records=recs)

CYR = 2018

# calculate for specified CYR
calc1.advance_to_year(CYR)
calc1.calc_all()
calc2.advance_to_year(CYR)
calc2.calc_all()

# compare aggregate individual income tax revenue in CYR
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

# print total revenue estimates for CYR
# (estimates in billons of dollars)
print('{}_REFORM1_iitax_rev($B)= {:.3f}'.format(CYR, iitax_rev1 * 1e-9))
print('{}_REFORM2_iitax_rev($B)= {:.3f}'.format(CYR, iitax_rev2 * 1e-9))
print('')

# print reform2-vs-reform1 difference table
title = 'Extract of {} income-tax difference table by expanded-income decile'
print(title.format(CYR))
print('(taxfall is count of funits with cut in income tax in reform 2 vs 1)')
print('(taxrise is count of funits with rise in income tax in reform 2 vs 1)')
print(diff_extract.to_string())
```
