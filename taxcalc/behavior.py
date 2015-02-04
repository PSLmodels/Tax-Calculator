import numpy as np
class Behavior(object): 

	def __init__(self, calcX, calcY, elast_wrt_atr = 0.4, inc_effect = 0.15):
		self.calcX = calcX
		self.calcY = calcY
		self.elast_wrt_atr = elast_wrt_atr
		self.inc_effect = inc_effect

	@property
	def behavior(self, ):
		"""
	    Modify plan Y records to account for micro-feedback effect that arrise 
	    from moving from plan X to plan Y. 
	    """
		# Calculate marginal tax rates for plan x and plan y.
		mtrX = self.calcX.mtr('e00200')
		print 'mtrX'
		print mtrX

		mtrY = self.calcY.mtr('e00200')
		print 'mtrY'
		print mtrY
		# Calculate the percent change in after-tax rate.
		pct_diff_atr = ((1-mtrY) - (1-mtrX))/(1-mtrX)


		# Calculate the magnitude of the substitution and income effects. 
		substitution_effect = (self.elast_wrt_atr * pct_diff_atr * 
								(self.calcX.c05200))
		print 'substitution_effect'
		print substitution_effect


		income_effect = self.inc_effect * (self.calcY.c05200 - self.calcX.c05200)
		print 'income_effect'
		print income_effect
		delta_inc = np.where(self.calcY.c00100 > 0 ,
					substitution_effect + income_effect, 0)

		# TODO Replace c05200 with _ospctax.
		# TODO Currently we are not recalculating tax with the substitution
		# effect before calculating the income effect. Should we be? 
		
		# Attribute the behavioral effects across itemized deductions, 
		# wages, and other income. 

		_itemized = np.where(self.calcY.c04470 < self.calcY._standard, 
								0, self.calcY.c04470)
		# TODO, verify that this is needed. 

		delta_wages = (delta_inc * self.calcY.e00200 / 
						(self.calcY.c00100 + _itemized + .001))
		
		other_inc = self.calcY.c00100 - self.calcY.e00200

		delta_other_inc = (delta_inc * other_inc / 
							(self.calcY.c00100 + _itemized + .001))

		delta_itemized = (delta_inc * _itemized / 
							(self.calcY.c00100 + _itemized + .001))

		self.calcY.e00200 = self.calcY.e00200 + delta_wages

		self.calcY.e00300 = self.calcY.e00300 + delta_other_inc

		self.calcY.e19570 = np.where(_itemized > 0, 
								self.calcY.e19570 + delta_itemized, 0)
		#TODO, we should create a behavioral modification 
		# variable instead of using e19570

		return self.calcY

