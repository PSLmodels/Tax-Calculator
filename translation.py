import pandas as pd
import math
import numpy as np

output_filename = 'translationoutput.csv' 
input_filename = 'puf2.csv'
x = pd.read_csv(input_filename)

global dim 
dim = len(x)

names = x.columns.values
namesCap = [str.upper(n) if str.isalpha(n) else n for n in names]

y = {}
for n in namesCap:
	y[n] = np.array(x[str.lower(n)])
 
locals().update(y)

AGIR1 = agir1
MIdR = MIDR



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

_almsep = np.array([39275]) 
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

_amtex = np.array([[51900, 80750, 40375, 51900, 80750, 40375], [0, 0, 0, 0, 0, 0]]) 
#AMT Exclusion

_exmpb = np.array([[200000, 300000, 150000, 250000, 300000, 150000], [0, 0, 0, 0, 0, 0]]) 
#Personal Exemption Amount 

_stded = np.array([[6100, 12200, 6100, 8950, 12200, 6100, 1000], [0, 0, 0, 0, 0, 0, 0]])
 #Standard Deduction

_brk1 = np.array([[8925, 17850, 8925, 12750, 17850, 8925], [0, 0, 0, 0, 0, 0]]) 
#10% tax rate thresholds

_brk2 = np.array([[36250, 72500, 36250, 48600, 72500, 35250], [0, 0, 0, 0, 0, 0]])
 #15% tax rate thresholds

_brk3 = np.array([[87850, 146400, 73200, 125450, 146400, 73200], [0, 0, 0, 0, 0, 0]]) 
#25% tax rate thresholds

_brk4 = np.array([[183250, 223050, 111525, 203150, 223050, 111525], [0, 0, 0, 0, 0, 0]]) 
#28% tax rate thresholds

_brk5 = np.array([[398350, 398350, 199175, 398350, 398350, 199175], [0, 0, 0, 0, 0, 0]]) 
#33% tax rate thresholds

_brk6 = np.array([[400000, 450000, 225000, 425000, 450000, 225000], [0, 0, 0, 0, 0, 0]]) 
#25% tax rate thresholds


def Puf(): 
#Run this function data input is the PUF file
	
	global e35300_0 
	e35300_0 = np.zeros((dim,))
	global e35600_0 
	e35600_0 = np.zeros((dim,))
	global e35910_0 
	e35910_0 = np.zeros((dim,))
	global x03150 
	x03150 = np.zeros((dim,))
	global e03600 
	e03600 = np.zeros((dim,))
	global e03280 
	e03280 = np.zeros((dim,))
	global e03900 
	e03900 = np.zeros((dim,))
	global e04000 
	e04000 = np.zeros((dim,))
	global e03700 
	e03700 = np.zeros((dim,))
	global c23250 
	c23250 = np.zeros((dim,))
	global e22250 
	e22250 = np.zeros((dim,))
	global e23660 
	e23660 = np.zeros((dim,))
	global f2555 
	f2555 = np.zeros((dim,))
	global e02800 
	e02800 = np.zeros((dim,))
	global e02610 
	e02610 = np.zeros((dim,))
	global e02540 
	e02540 = np.zeros((dim,))
	global e02615 
	e02615 = np.zeros((dim,))
	global SSIND 
	SSIND = np.zeros((dim,))
	global e18400 
	e18400 = np.zeros((dim,))
	global e18800 
	e18800 = np.zeros((dim,))
	global e18900 
	e18900 = np.zeros((dim,))
	global e20950
	e20950 = np.zeros((dim,))
	global e19500 
	e19500 = np.zeros((dim,))
	global e19570 
	e19570 = np.zeros((dim,))
	global e19400 
	e19400 = np.zeros((dim,))
	global c20400
	c20400 = np.zeros((dim,))
	global e20200
	e20200 = np.zeros((dim,))
	global e20900 
	e20900 = np.zeros((dim,))
	global e21000 
	e21000 = np.zeros((dim,))
	global e21010 
	e21010 = np.zeros((dim,))
	global e02600
	e02600 = np.zeros((dim,))
	global _exact 
	_exact = np.zeros((dim,))
	global e11055
	e11055 = np.zeros((dim,))
	global e00250
	e00250 = np.zeros((dim,))
	global e30100
	e30100 = np.zeros((dim,))
	global _compitem 
	_compitem = np.zeros((dim,))
	global e15360
	e15360 = np.zeros((dim,))
	global e04200
	e04200 = np.zeros((dim,))
	global e04470
	e04470 = np.zeros((dim,))
	global e37717
	e37717 = np.zeros((dim,))
	global e04805
	e04805 = np.zeros((dim,))
	global AGEP 
	AGEP = np.zeros((dim,))
	global AGES
	AGES = np.zeros((dim,))
	global PBI 
	PBI = np.zeros((dim,))
	global SBI 
	SBI = np.zeros((dim,))
	global t04470 
	t04470 = np.zeros((dim,))
	global e23250
	e23250 = np.zeros((dim,))
	global _xyztax
	#How is this variable encoded in the original code?
	_xyztax = np.zeros((dim,)) 
	global e58980
	e58980 = np.zeros((dim,))
	global c00650
	c00650 = np.zeros((dim,))
	global e24583
	e24583 = np.zeros((dim,))
	global _fixup
	_fixup = np.zeros((dim,))


	

def FilingStatus():
	#Filing based on marital status
	global _sep
	global _txp
	_sep = np.where(np.logical_or(MARS == 3, MARS == 6), 2, 1)
	_txp = np.where(np.logical_or(MARS == 2, MARS == 5), 2, 1)


def Adj(): 
	#Adjustments
	global _feided 
	global c02900
	_feided = np.maximum(e35300_0, e35600_0, + e35910_0) #Form 2555
	c02900 = (e03210 + e03260 + e03270 + e03300 + e03400 + e03500 + e03220 
	+ e03230 + e03240 + e03290 + x03150 + e03600 + e03280 + e03900 + e04000 
	+ e03700) 
	x02900 = c02900


def CapGains():
	#Capital Gains
	global _ymod
	global _ymod1
	global c02700
	c23650 = c23250 + e22250 + e23660 
	c01000 = np.maximum(-3000/_sep, c23650)
	c02700 = np.minimum(_feided, _feimax[2013-FLPDYR] * f2555) 
	_ymod1 = (e00200 + e00300 + e00600 + e00700 + e00800 + e00900 + c01000 
		+ e01100 + e01200 + e01400 + e01700 + e02000 + e02100 + e02300 + e02600 
		+ e02610 + e02800 - e02540)
	_ymod2 = e00400 + e02400/2 - c02900
	_ymod3 = e03210 + e03230 + e03240 + e02615
	_ymod = _ymod1 + _ymod2 + _ymod3


def SSBenefits():
	#Social Security Benefit Taxation
	global c02500	
	c02500 = np.where(np.logical_or(SSIND != 0, np.logical_and(MARS >= 3, MARS <= 6)), e02500, 
		np.where(_ymod < _ssb50[MARS-1], 0, 
			np.where(np.logical_and(_ymod >= _ssb50[MARS-1], _ymod < _ssb85[MARS-1]), 
				0.5 * np.minimum(_ymod - _ssb50[MARS-1], e02400), 
				np.minimum(0.85 * (_ymod - _ssb85[MARS-1]) + 0.50 * 
					np.minimum(e02400, _ssb85[MARS-1] - _ssb50[MARS-1]), 0.85 * e02400)))) 


def AGI():
	#Adjusted Gross Income	
	global _posagi
	global c00100
	global c04600
	c02650 = _ymod1 + c02500 - c02700 + e02615 #Gross Income

	c00100 = c02650 - c02900
	_agierr = e00100 - c00100  #Adjusted Gross Income
	c00100 = np.where(_fixup >= 1, c00100 + _agierr, c00100)

	_posagi = np.maximum(c00100, 0)
	_ywossbe = e00100 - e02500
	_ywossbc = c00100 - c02500

	_prexmp = XTOT * _amex[FLPDYR - 2013] 
	#Personal Exemptions (_phaseout smoothed)


	#_ratio = (_posagi - _exmpb[FLPDYR - 2013, MARS -1])/(2500/_sep)
	#_tratio = np.ceil(_ratio)
	#_dispc = np.minimum(1, np.maximum(0, 0.2 * _tratio))

	
	_dispc = np.minimum(1, 
		np.maximum(0, 0.2 * ((_posagi - _exmpb[FLPDYR -2013, MARS - 1])/(2500/_sep))))
	#This is not being calculated correctly for some data points -- FIND OUT WHY. 
	#_posagi, _sep, and the _exmpb array are all correctly inputted 
	#so I have no clue why this is happening. 

	c04600 = _prexmp * (1-_dispc)


def ItemDed(puf): 
	#Itemized Deductions
	global c04470
	global c21060
	global c21040

	# Medical #
	c17750 = 0.075 * _posagi 
	c17000 = np.maximum(0, e17500 - c17750)
	xx = 2

	# State and Local Income Tax, or Sales Tax #
	_sit1 = np.maximum(e18400, e18425)
	_sit = np.maximum(_sit1, 0)
	_statax = np.maximum(_sit, e18450)

	# Other Taxes #
	c18300 = _statax + e18500 + e18800 + e18900

	# Casulty #
	c37703 = np.where(e20500 > 0, e20500 + 0.10 * _posagi, 0)
	c20500 = np.where(e20500 > 0, c37703 - 0.10 * _posagi, 0)

	# Miscellaneous #
	c20750 = 0.02 * _posagi 
	if puf == True: 
		c20400 = e20400
		c19200 = e19200 
	else: 
		c02400 = e20550 + e20600 + e20950
		c19200 = e19500 + e19570 + e19400 + e19550
	c20800 = np.maximum(0, c20400 - c20750)

	# Charity (assumes carryover is non-cash) #
	_lim50 = np.minimum(0.50 * _posagi, e19800)
	_lim30 = np.minimum(0.30 * _posagi, e20100 + e20200)
	c19700 = np.where(e19800 + e20100 + e20200 <= 0.20 * _posagi, 
		e19800 + e20100 + e20200, _lim30 + _lim50)
    #temporary fix!??

    # Gross Itemized Deductions #
	c21060 = e20900 + c17000 + c18300 + c19200 + c19700 + c20500 + c20800 + e21000 + e21010
	
    # Itemized Deduction Limitation
	_phase2 = np.where(MARS == 1, 200000, np.where(MARS == 4, 250000, 300000))

	_itemlimit = 1
	_c21060 = c21060
	_nonlimited = c17000 + c20500 + e19570 + e21010 + e20900
	_limitratio = _phase2/_sep 

	_itemlimit = np.where(np.logical_and(c21060 > _nonlimited, c00100 > _phase2/_sep), 
		2, 1)
	_dedmin = np.where(np.logical_and(c21060 > _nonlimited, c00100 > _phase2/_sep), 
		0.8 * (c21060 - _nonlimited), 0)
	_dedpho = np.where(np.logical_and(c21060 > _nonlimited, c00100 > _phase2/_sep), 
		0.03 * np.maximum(0, _posagi - _phase2/_sep), 0)
	c21040 = np.where(np.logical_and(c21060 > _nonlimited, c00100 > _phase2/_sep), 
		np.minimum(_dedmin, _dedpho), 0)
	c04470 = np.where(np.logical_and(c21060 > _nonlimited, c00100 > _phase2/_sep), 
		c21060 - c21040, c21060)


def EI_FICA():
	# Earned Income and FICA #    
	global _earned
	_sey = e00900 + e02100
	_fica = np.maximum(0, .153 * np.minimum(_ssmax[FLPDYR - 2013], 
		e00200 + np.maximum(0, _sey) * 0.9235))
	_setax = np.maximum(0, _fica - 0.153 * e00200)
	_seyoff = np.where(_setax <= 14204, 0.5751 * _setax, 0.5 * _setax + 10067)

	c11055 = e11055

	_earned = np.maximum(0, e00200 + e00250 + e11055 + e30100 + _sey - _seyoff)


def StdDed():
	# Standard Deduction with Aged, Sched L and Real Estate # 
	global c04800
	global c60000

	c15100 = np.where(DSI == 1, np.maximum(300 + _earned, _stded[FLPDYR-2013, 6]), 0)

	c04100 = np.where(DSI == 1, np.minimum(_stded[FLPDYR-2013, MARS-1], c15100), 
		np.where(np.logical_or(_compitem == 1, 
			np.logical_and(np.logical_and(3<= MARS, MARS <=6), MIdR == 1)), 
		0, _stded[FLPDYR-2013, MARS-1]))


	c04100 = c04100 + e15360
	_numextra = AGEP + AGES + PBI + SBI 

	_txpyers = np.where(np.logical_or(np.logical_or(MARS == 2, MARS == 3), 
		MARS == 3), 2, 1)
	c04200 = np.where(np.logical_and(_exact == 1, np.logical_or(MARS == 3, MARS == 5)), 
		e04200, _numextra * _aged[_txpyers -1, FLPDYR - 2013])

	c15200 = c04200

	_standard = np.where(np.logical_and(np.logical_or(MARS == 3, MARS == 6), c04470 > 0), 
		0, c04100 + c04200)

	_othded = np.where(FDED == 1, e04470 - c04470, 0)
	#c04470 = np.where(np.logical_and(_fixup >= 2, FDED == 1), c04470 + _othded, c04470)
	c04100 = np.where(FDED == 1, 0, c04100)
	c04200 = np.where(FDED == 1, 0, c04200)
	_standard = np.where(FDED == 1, 0, _standard)


	c04500 = c00100 - np.maximum(c21060 - c21040, 
		np.maximum(c04100, _standard + e37717))
	c04800 = np.maximum(0, c04500 - c04600 - e04805)

	c60000 = np.where(_standard > 0, c00100, c04500)
	c60000 = c60000 - e04805

	#Some taxpayers iteimize only for AMT, not regular tax
	_amtstd = 0
	c60000 = np.where(np.logical_and(np.logical_and(e04470 == 0, t04470 > _amtstd), 
		np.logical_and(f6251 == 1, _exact == 1)), c00100 - t04470, c60000)

	_taxinc = np.where(np.logical_and(c04800 > 0, _feided > 0), c04800 + c02700, c04800)
	#WHAT IS %TAXER!?

	_feitax = np.zeros((dim,)) #temporaray fix

def Test(puf):
	if puf == True:
		Puf()
	FilingStatus()
	Adj()
	CapGains()
	SSBenefits()
	AGI()
	ItemDed(puf)
	EI_FICA()
	StdDed()

	outputs = (_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi, 
		c00100, c04600, c04470, c21060, _earned, c04800, c60000)
	output = np.column_stack(outputs)

	np.savetxt('output.csv', output, delimiter=',', 
		header = ('_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi, c00100, c04600, c04470, c21060, _earned, c04800, c60000') 
		, fmt = '%1.3f')
