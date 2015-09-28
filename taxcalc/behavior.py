import numpy as np
import copy


def update_income(behavioral_effect, calcY):
    delta_inc = np.where(calcY.records.c00100 > 0, behavioral_effect, 0)

    # Attribute the behavioral effects across itemized deductions,
    # wages, and other income.

    _itemized = np.where(calcY.records.c04470 < calcY.records._standard,
                         0,
                         calcY.records.c04470)

    delta_wages = np.where(calcY.records.c00100 + _itemized > 0,
                           (delta_inc * calcY.records.e00200 /
                            (calcY.records.c00100 + _itemized)),
                           0)

    other_inc = calcY.records.c00100 - calcY.records.e00200

    delta_other_inc = np.where(calcY.records.c00100 + _itemized > 0,
                               (delta_inc * other_inc /
                                (calcY.records.c00100 + _itemized)),
                               0)

    delta_itemized = np.where(calcY.records.c00100 + _itemized > 0,
                              (delta_inc * _itemized /
                               (calcY.records.c00100 + _itemized)),
                              0)

    calcY.records.e00200 = calcY.records.e00200 + delta_wages

    calcY.records.e00300 = calcY.records.e00300 + delta_other_inc

    calcY.records.e19570 = np.where(_itemized > 0,
                                    calcY.records.e19570 + delta_itemized, 0)
    # TODO, we should create a behavioral modification
    # variable instead of using e19570

    calcY.calc_all()

    return calcY


def behavior(calcX, calcY, update_income=update_income):
    """
    Modify plan Y records to account for micro-feedback effect that arrise
    from moving from plan X to plan Y.
    """

    # Calculate marginal tax rates for plan x and plan y.
    mtrX = calcX.mtr('e00200')

    mtrY = calcY.mtr('e00200')

    # Calculate the percent change in after-tax rate.
    pct_diff_atr = ((1 - mtrY) - (1 - mtrX)) / (1 - mtrX)

    # Calculate the magnitude of the substitution and income effects.
    substitution_effect = (calcY.params.BE_sub * pct_diff_atr *
                           (calcX.records.c04800))

    income_effect = calcY.params.BE_inc * (calcY.records._ospctax -
                                           calcX.records._ospctax)
    calcY_behavior = copy.deepcopy(calcY)

    combined_behavioral_effect = income_effect + substitution_effect

    calcY_behavior = update_income(combined_behavioral_effect,
                                   calcY_behavior)

    return calcY_behavior
