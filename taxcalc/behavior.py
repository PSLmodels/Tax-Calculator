import numpy as np
import copy


def update_income(behavioral_effect, calc_y):
    delta_inc = np.where(calc_y.records.c00100 > 0, behavioral_effect, 0)

    # Attribute the behavioral effects across itemized deductions,
    # wages, and other income.

    _itemized = np.where(calc_y.records.c04470 < calc_y.records._standard,
                         0,
                         calc_y.records.c04470)

    delta_wages = np.where(calc_y.records.c00100 + _itemized > 0,
                           (delta_inc * calc_y.records.e00200 /
                            (calc_y.records.c00100 + _itemized)),
                           0)

    other_inc = calc_y.records.c00100 - calc_y.records.e00200

    delta_other_inc = np.where(calc_y.records.c00100 + _itemized > 0,
                               (delta_inc * other_inc /
                                (calc_y.records.c00100 + _itemized)),
                               0)

    delta_itemized = np.where(calc_y.records.c00100 + _itemized > 0,
                              (delta_inc * _itemized /
                               (calc_y.records.c00100 + _itemized)),
                              0)

    calc_y.records.e00200 = calc_y.records.e00200 + delta_wages

    calc_y.records.e00300 = calc_y.records.e00300 + delta_other_inc

    calc_y.records.e19570 = np.where(_itemized > 0,
                                     calc_y.records.e19570 + delta_itemized, 0)
    # TODO, we should create a behavioral modification
    # variable instead of using e19570

    calc_y.calc_all()

    return calc_y


def behavior(calc_x, calc_y, update_income=update_income):
    """
    Modify plan Y records to account for micro-feedback effect that arrise
    from moving from plan X to plan Y.
    """

    # Calculate marginal tax rates for plan x and plan y.
    mtrX = calc_x.mtr('e00200')

    mtrY = calc_y.mtr('e00200')

    # Calculate the percent change in after-tax rate.
    pct_diff_atr = ((1 - mtrY) - (1 - mtrX)) / (1 - mtrX)

    # Calculate the magnitude of the substitution and income effects.
    substitution_effect = (calc_y.params.BE_sub * pct_diff_atr *
                           (calc_x.records.c04800))

    income_effect = calc_y.params.BE_inc * (calc_y.records._ospctax -
                                            calc_x.records._ospctax)
    calc_y_behavior = copy.deepcopy(calc_y)

    combined_behavioral_effect = income_effect + substitution_effect

    calc_y_behavior = update_income(combined_behavioral_effect,
                                    calc_y_behavior)

    return calc_y_behavior
