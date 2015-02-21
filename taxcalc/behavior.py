import numpy as np
import copy

def update_income(effect, calcY):  
	delta_inc = np.where(calcY.c00100 > 0 ,
				effect, 0)

	# Attribute the behavioral effects across itemized deductions, 
	# wages, and other income. 

	_itemized = np.where(calcY.c04470 < calcY._standard, 
							0, calcY.c04470)
	# TODO, verify that this is needed. 

	delta_wages = (delta_inc * calcY.e00200 / 
					(calcY.c00100 + _itemized + .001))
	
	other_inc = calcY.c00100 - calcY.e00200

	delta_other_inc = (delta_inc * other_inc / 
						(calcY.c00100 + _itemized + .001))

	delta_itemized = (delta_inc * _itemized / 
						(calcY.c00100 + _itemized + .001))

	calcY.e00200 = calcY.e00200 + delta_wages

	calcY.e00300 = calcY.e00300 + delta_other_inc

	calcY.e19570 = np.where(_itemized > 0, 
							calcY.e19570 + delta_itemized, 0)
	#TODO, we should create a behavioral modification 
	# variable instead of using e19570

	calcY.calc_all()

	return calcY


def behavior(calcX, calcY, elast_wrt_atr=0.4, inc_effect=0.15, update_income=update_income):
	"""
    Modify plan Y records to account for micro-feedback effect that arrise 
    from moving from plan X to plan Y. 
    """

	# Calculate marginal tax rates for plan x and plan y.
	mtrX = calcX.mtr('e00200')

	mtrY = calcY.mtr('e00200')

	# Calculate the percent change in after-tax rate.
	pct_diff_atr = ((1-mtrY) - (1-mtrX))/(1-mtrX)

	calcY_behavior = copy.deepcopy(calcY)

	# Calculate the magnitude of the substitution and income effects. 
	substitution_effect = (elast_wrt_atr * pct_diff_atr * 
							(calcX._ospctax))


	calcY_behavior = update_income(substitution_effect, calcY_behavior)


	income_effect = inc_effect * (calcY_behavior._ospctax - calcX._ospctax)

	calcY_behavior = update_income(income_effect, calcY_behavior)

	return calcY_behavior





