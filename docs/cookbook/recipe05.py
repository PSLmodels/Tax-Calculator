"""
Tax-Calculator Python Cookbook Recipe 5.
"""
import sys
import pandas as pd
from taxcalc import Policy, Records, Calculator


class CustomizedCalculator(Calculator):
    """
    Customized taxcalc.Calculator class that inherits all Calculator methods
    and calcfunctions, overriding some to get the desired customization.
    """
    def __init__(self, policy=None, records=None, verbose=False,
                 sync_years=True, consumption=None):
        # use same class constructor arguments as taxcalc.Calculator class
        super().__init__(policy=policy, records=records,
                         verbose=verbose, sync_years=sync_years,
                         consumption=consumption)
# end of CustomizedCalculator class definition

# begin overrided calcfunctions used by CustomizedCalculator class

@iterate_jit(nopython=True)
def ExpandIncome(e00200, pencon_p, pencon_s, e00300, e00400, e00600,
                 e00700, e00800, e00900, e01100, e01200, e01400, e01500,
                 e02000, e02100, p22250, p23250,
                 cmbtp, ptax_was, benefit_value_total, ubi,
                 expanded_income):
    """
    Calculates expanded_income from component income types.
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
        0.5 * ptax_was +  # employer share of FICA taxes on wages/salaries
        ubi +  # total UBI benefit
        benefit_value_total  # consumption value of all benefits received;
        # see the BenefitPrograms function in this file for details on
        # exactly how the benefit_value_total variable is computed
    )
    return expanded_income

# end overrided calcfunctions used by CustomizedCalculator class


def main():
    """
    Top-level logic of the recipe05.py program.
    """
    # read an "old" reform file from Tax-Calculator website
    # ("old" means the reform file is defined relative to pre-TCJA policy)
    reforms_url = ('https://raw.githubusercontent.com/'
                   'PSLmodels/Tax-Calculator/master/taxcalc/reforms/')

    # specify reform dictionary for pre-TCJA policy
    reform1 = Policy.read_json_reform(reforms_url + '2017_law.json')

    # specify reform dictionary for TCJA as passed by Congress in late 2017
    reform2 = Policy.read_json_reform(reforms_url + 'TCJA.json')

    # specify Policy object for pre-TCJA policy
    bpolicy = Policy()
    bpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
    assert not bpolicy.parameter_errors

    # specify Policy object for TCJA reform relative to pre-TCJA policy
    rpolicy = Policy()
    rpolicy.implement_reform(reform1, print_warnings=False, raise_errors=False)
    assert not rpolicy.parameter_errors
    rpolicy.implement_reform(reform2, print_warnings=False, raise_errors=False)
    assert not rpolicy.parameter_errors

    # specify CustomizedCalculator objects using bpolicy and rpolicy
    recs = Records.cps_constructor()
    calc1 = CustomizedCalculator(policy=bpolicy, records=recs)
    calc2 = CustomizedCalculator(policy=rpolicy, records=recs)

    cyr = 2018

    # calculate for specified cyr
    calc1.advance_to_year(cyr)
    calc1.calc_all()
    calc2.advance_to_year(cyr)
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
    print('{}_REFORM1_iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev1 * 1e-9))
    print('{}_REFORM2_iitax_rev($B)= {:.3f}'.format(cyr, iitax_rev2 * 1e-9))
    print('')

    # print reform2-vs-reform1 difference table
    title = 'Extract of {} income-tax difference table by expanded-income decile'
    print(title.format(cyr))
    print('(taxfall is count of funits with cut in income tax in reform 2 vs 1)')
    print('(taxrise is count of funits with rise in income tax in reform 2 vs 1)')
    print(diff_extract.to_string())

    return 0
# end of main()


if __name__ == '__main__':
    sys.exit(main())
