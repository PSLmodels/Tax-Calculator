"""
Non Puf related variables
"""

import numpy as np

_adctcrt = np.array([0.15])
 #Rate for additional ctc

_aged = np.array([[1500],[1200]]) 
#Extra std. ded. for aged

_almdep = np.array([6950]) 
#Child AMT Exclusion base

_almsp = np.array([179500]) 
#AMT bracket

_amex = np.array([3900]) 
#Personal Exemption

_amtage = np.array([24]) 
#Age for full AMT exclusion

_amtsep = np.array([232500]) 
#AMT Exclusion

_almsep = np.array([39375]) 
#Extra alminc for married sep

_agcmax = np.array([15000]) 
#??

_cgrate1 = np.array([0.10]) 
#Initial rate on long term gains

_cgrate2 = np.array([0.20]) 
#Normal rate on long term gains

_chmax = np.array([1000]) 
#Max Child Tax Credit per child 

_crmax = np.array([[487],[3250],[5372],[6044]]) 
#Max earned income credit

_dcmax = np.array([3000]) 
#Max dependent care expenses 

_dylim = np.array([3300]) 
#Limits for Disqualified Income

_ealim = np.array([3000]) 
#Max earn ACTC

_edphhs = np.array([63]) 
#End of educ phaseout - singles

_edphhm = np.array([126]) 
#End of educ phaseout - married 

_feimax = np.array([97600]) 
#Maximum foreign earned income exclusion

#_hopelm = np.array([1200])

_joint = np.array([0]) 
#Extra to ymax for joint

_learn = np.array([10000]) 
#Expense limit for the LLC

_pcmax = np.array([35]) 
#Maximum Percentage for f2441

_phase = np.array([172250]) 
#Phase out for itemized

_rtbase = np.array([[0.0765], [0.3400], [0.4000], [0.4000]]) 
#EIC base rate

_rtless = np.array([[0.0765], [0.1598], [0.2106], [0.2106]]) 
#EIC _phaseout rate

_ssmax = np.array([115800]) 
#SS Maximum taxable earnings

_ymax = np.array([[7970], [17530], [17530], [17530]]) 
#Start of EIC _phaseout

_rt1 = np.array([0.1]) 
#10% rate

_rt2 = np.array([0.15]) 
#15% rate

_rt3 = np.array([0.25]) 
#25% rate

_rt4 = np.array([0.28]) 
#28% rate

_rt5 = np.array([0.33]) 
#33% rate

_rt6 = np.array([0.35]) 
#35% rate

_rt7 = np.array([0.396]) 
#39.6% rate

_amtys = np.array([112500, 150000, 75000, 112500, 150000, 75000]) 
#AMT Phaseout Start

_cphase = np.array([75000, 110000, 55000, 75000, 75000, 55000]) 
#Child Tax Credit Phase-Out

_thresx = np.array([200000, 250000, 125000, 200000, 250000, 125000]) 
#Threshold for add medicare

_ssb50 = np.array([25000, 32000, 0, 25000, 25000, 0]) 
#SS 50% taxability threshold

_ssb85 = np.array([34000, 44000, 0, 34000, 34000, 0]) 
#SS 85% taxability threshold 

_amtex = np.array([[51900, 80750, 40375, 51900, 80750, 40375], 
	[0, 0, 0, 0, 0, 0]]) 
#AMT Exclusion

_exmpb = np.array([[200000, 300000, 150000, 250000, 300000, 150000], 
	[0, 0, 0, 0, 0, 0]]) 
#Personal Exemption Amount 

_stded = np.array([[6100, 12200, 6100, 8950, 12200, 6100, 1000], 
	[0, 0, 0, 0, 0, 0, 0]])
 #Standard Deduction

_brk1 = np.array([[8925, 17850, 8925, 12750, 17850, 8925], 
	[0, 0, 0, 0, 0, 0]]) 
#10% tax rate thresholds

_brk2 = np.array([[36250, 72500, 36250, 48600, 72500, 36250], 
	[0, 0, 0, 0, 0, 0]])
 #15% tax rate thresholds

_brk3 = np.array([[87850, 146400, 73200, 125450, 146400, 73200], 
	[0, 0, 0, 0, 0, 0]]) 
#25% tax rate thresholds

_brk4 = np.array([[183250, 223050, 111525, 203150, 223050, 111525], 
	[0, 0, 0, 0, 0, 0]]) 
#28% tax rate thresholds

_brk5 = np.array([[398350, 398350, 199175, 398350, 398350, 199175], 
	[0, 0, 0, 0, 0, 0]]) 
#33% tax rate thresholds

_brk6 = np.array([[400000, 450000, 225000, 425000, 450000, 225000], 
	[0, 0, 0, 0, 0, 0]]) 
#25% tax rate thresholds

__all__ = [loc for loc in locals().keys() if "__" not in loc]
