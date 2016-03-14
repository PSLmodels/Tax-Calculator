import pandas as pd


def percentage_change_gdp(calc1, calc2, elasticity=0.0):
    mtr_fica_x, mtr_iit_x, mtr_combined_x = calc1.mtr()
    mtr_fica_y, mtr_iit_y, mtr_combined_y = calc2.mtr()

    after_tax_mtr_x = (1 - ((mtr_combined_x) * calc1.records.c00100 *
                       calc1.records.s006).sum() /
                       (calc1.records.c00100 * calc1.records.s006).sum())

    after_tax_mtr_y = (1 - ((mtr_combined_y) * calc2.records.c00100 *
                       calc2.records.s006).sum() /
                       (calc2.records.c00100 * calc2.records.s006).sum())

    diff_avg_mtr_combined_y = after_tax_mtr_y - after_tax_mtr_x
    percent_diff_mtr = diff_avg_mtr_combined_y / after_tax_mtr_x

    gdp_effect_y = percent_diff_mtr * elasticity

    print(("%.5f" % gdp_effect_y))

    return gdp_effect_y
