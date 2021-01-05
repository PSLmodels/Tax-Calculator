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

# Recipe 6: Analyzing a Non-Parametric Reform

This is an advanced recipe that should be followed only after mastering the basic recipe.
This recipe shows how to customize the Calculator class so that it can analyze a tax reform
that cannot be characterized using existing policy parameters (in this case a pseudo Cost-of-Living Refund reform).
It uses, in a more extensive way, the object-oriented programming inheritance technique introduced in Redefining Expanded Income,
so you might want to read that recipe first.

Recipe that illustrates how to customize the taxcalc Calculator class so that
it can analyze a non-parametric reform (that is, a reform that cannot be
represented using existing taxcalc Policy parameters.

The technique for doing this customization is standard in object-oriented
programming: a child class is derived from a parent class and then customized.
The derived child class inherits all the data and methods of the parent class,
but can be customized by adding new data and methods or by overriding inherited
methods.

The reform used to illustrate this programming technique is somewhat like
the Cost-of-Living Refund, a refundable credit that was being discussed in
tax policy circles during 2019 as a replacement for the EITC.  But the
reform analyzed here is not exactly like the Cost-of-Living Refund, so we
call it a pseudo cost-of-living refund to emphasize that it is not meant
to be an accurate representation of the Cost-of-Living Refund proposal.

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

import numpy as np
import taxcalc as tc


class Calculator(tc.Calculator):
    """
    Customized Calculator class that inherits all tc.Calculator data and
    methods, adding or overriding some to get the desired customization.
    """
    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None,
                 # above are the tc.Calculator constructor arguments
                 # below is new constructor argument used in customization
                 colr_active=False):
        # call the parent class constructor
        super().__init__(policy=policy, records=records,
                         verbose=verbose, sync_years=sync_years,
                         consumption=consumption)
        # remember whether pseudo_COLR policy is active or not
        self.colr_active = colr_active
        # declare colr_param dictionary that will contain pseudo COLR policy
        self.colr_param = dict()

    def specify_pseudo_colr_policy(self):
        """
        Specify policy parameters for the COLR policy in the current_year.
        See use of these parameters below in the pseudo_colr_amount method.
        """
        # reform implementation year
        reform_year = 2020
        # specify dictionary of parameter names and values for reform_year
        self.colr_param = {
            # credit phase-in rate on earnings
            'COLR_rt': 1.0,
            # ceiling on refundable credit varies by filing-unit type, MARS
            'COLR_c': np.array([4000, 8000, 4000, 4000, 4000],
                               dtype=np.float64),
            # credit phase-out start AGI level varies by filing-unit type, MARS
            'COLR_ps': np.array([30000, 50000, 30000, 30000, 30000],
                                dtype=np.float64),
            # credit phase-out rate per dollar of AGI above COLR_ps level
            'COLR_prt': 0.2
        }
        # set pseudo COLR parameter values for current year
        this_year = self.current_year
        if self.colr_active and this_year >= reform_year:
            # set inflation-indexed values of COLR_c and COLR_ps for this year
            irates = self.__policy.inflation_rates()
            syr = tc.Policy.JSON_START_YEAR
            for name in ['COLR_c', 'COLR_ps']:
                value = self.colr_param[name]
                for year in range(reform_year, this_year):
                    value *= (1.0 + irates[year - syr])
                self.colr_param[name] = np.round(value, 2)  # to nearest penny
        else:  # if policy not active or if this year is before the reform year
            # set ceiling to zero
            self.colr_param['COLR_c'] = np.array([0.0, 0.0, 0.0, 0.0, 0.0],
                                                 dtype=np.float64)
        tracing = False  # set to True to see parameter values for this year
        if tracing:
            for name in self.colr_param:
                print('> {} {} {}'.format(
                    this_year, name, self.colr_param[name]
                ))

    def pseudo_colr_amount(self):
        """
        Calculate pseudo Cost-of-Living Refund amount.
        Note this is simply meant to illustrate a Python programming technique;
        this function does NOT calculate an exact Cost-of-Living Refund amount.
        See setting of parameters above in specify_pseudo_COLR_policy method.
        """
        recs = self.__records
        # create MARS-specific policy parameter arrays
        mars_indicators = [recs.MARS == 1, recs.MARS == 2, recs.MARS == 3,
                           recs.MARS == 4, recs.MARS == 5]
        colr_c = np.select(mars_indicators, self.colr_param['COLR_c'])
        colr_ps = np.select(mars_indicators, self.colr_param['COLR_ps'])
        colr_rt = self.colr_param['COLR_rt']
        colr_prt = self.colr_param['COLR_prt']
        # compute colr_amt
        amt_pre_phaseout = np.minimum(recs.e00200 * colr_rt, colr_c)
        phaseout = np.maximum((recs.c00100 - colr_ps) * colr_prt, 0.)
        colr_amt = np.maximum(amt_pre_phaseout - phaseout, 0.)
        setattr(recs, 'colr_amount', colr_amt)
        # reduce income and combined taxes because COLR is a refundable credit
        recs.iitax -= colr_amt
        recs.combined -= colr_amt
        # delete local arrays used only in this method
        del mars_indicators
        del colr_c
        del colr_ps
        del amt_pre_phaseout
        del phaseout
        del colr_amt

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
        # specify new method to set pseudo COLR policy parameters
        self.specify_pseudo_colr_policy()  # (see above)
        # call new method to calculate pseudo COLR amount
        self.pseudo_colr_amount()  # (see above)
        tc.ExpandIncome(self.__policy, self.__records)
        tc.AfterTaxIncome(self.__policy, self.__records)

# end of customized Calculator class definition


# top-level logic of program that uses customized Calculator class

policy1 = tc.Policy()  # baseline policy is current-law policy
policy2 = tc.Policy()  # parametric reform, reformC.json, eliminates EITC

# TODO: Move to the web so this can be done standalone.
policy2.implement_reform(tc.Policy.read_json_reform('_static/reformC.json'))

# specify customized Calculator objects for baseline and reform:
#   baseline calc1 uses policy1 (current-law) and colr_active=False
#   reform calc2 uses policy2 (no EITC) and colr_active=True
cps_records = tc.Records.cps_constructor()
calc1 = Calculator(policy=policy1, records=cps_records, colr_active=False)
calc2 = Calculator(policy=policy2, records=cps_records, colr_active=True)

# calculate tax liabilities for years around the reform year
CYR_FIRST = 2019
CYR_LAST = 2022
for cyr in range(CYR_FIRST, CYR_LAST + 1):
    # advance to and calculate for specified cyr
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    calc2.advance_to_year(cyr)
    calc2.calc_all()
    # tabulate weighted amounts
    funits = calc1.total_weight()
    itax1 = calc1.weighted_total('iitax')
    itax2 = calc2.weighted_total('iitax')
    eitc1 = calc1.weighted_total('eitc')
    eitc2 = calc2.weighted_total('eitc')
    colr1 = calc1.weighted_total('colr_amount')
    colr2 = calc2.weighted_total('colr_amount')
    # print weighted amounts for cyr
    if cyr == CYR_FIRST:
        print('YEAR  UNITS   ITAX1   ITAX2  EITC1  EITC2  COLR1  COLR2')
    line = '{}  {:.1f}  {:.1f}  {:.1f}  {:5.1f}  {:5.1f}  {:5.1f}  {:5.1f}'
    print(line.format(cyr, funits * 1e-6,
                      itax1 * 1e-9, itax2 * 1e-9,
                      eitc1 * 1e-9, eitc2 * 1e-9,
                      colr1 * 1e-9, colr2 * 1e-9))
```
