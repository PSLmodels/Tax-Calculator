import numpy as np
import copy

def behavior(calcX, calcY, elast_wrt_atr = 0.4, inc_effect = 0.15):
	"""
    Modify plan Y records to account for micro-feedback effect that arrise 
    from moving from plan X to plan Y. 
    """

	# Calculate marginal tax rates for plan x and plan y.
	mtrX = calcX.mtr('e00200')

	mtrY = calcY.mtr('e00200')

	# Calculate the percent change in after-tax rate.
	pct_diff_atr = ((1-mtrY) - (1-mtrX))/(1-mtrX)


	# Calculate the magnitude of the substitution and income effects. 
	substitution_effect = (elast_wrt_atr * pct_diff_atr * 
							(calcX.c05200))


	income_effect = inc_effect * (calcY.c05200 - calcX.c05200)

	delta_inc = np.where(calcY.c00100 > 0 ,
				substitution_effect + income_effect, 0)

	# TODO Replace c05200 with _ospctax.
	# TODO Currently we are not recalculating tax with the substitution
	# effect before calculating the income effect. Should we be? 
	
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

	calcY_behavior = copy.deepcopy(calcY)

	calcY_behavior.e00200 = calcY_behavior.e00200 + delta_wages

	calcY_behavior.e00300 = calcY_behavior.e00300 + delta_other_inc

	calcY_behavior.e19570 = np.where(_itemized > 0, 
							calcY_behavior.e19570 + delta_itemized, 0)
	#TODO, we should create a behavioral modification 
	# variable instead of using e19570

	return calcY_behavior

