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

_brk2 = np.array([[36250, 72500, 36250, 48600, 72500, 35250], 
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
	global e58980
	e58980 = np.zeros((dim,))
	global c00650
	c00650 = np.zeros((dim,))
	global e24583
	e24583 = np.zeros((dim,))
	global _fixup
	_fixup = np.zeros((dim,))
	global _cmp 
	_cmp = np.zeros((dim,))
	global e59440 
	e59440 = np.zeros((dim,))
	global e59470
	e59470 = np.zeros((dim,))
	global e59400
	e59400 = np.zeros((dim,))
	global e10105
	e10105 = np.zeros((dim,))
	global e83200_0
	e83200_0 = np.zeros((dim,))
	global e59410 
	e59410 = np.zeros((dim,))
	global e59420 
	e59420 = np.zeros((dim,))
	global e74400 
	e74400 = np.zeros((dim,))
	global x62720 
	x62720  = np.zeros((dim,))
	global x60260
	x60260 = np.zeros((dim,))
	global x60240
	x60240 = np.zeros((dim,))
	global x60220
	x60220 = np.zeros((dim,))
	global x60130 
	x60130 = np.zeros((dim,))
	global x62730
	x62730 = np.zeros((dim,))
	global e60290
	e60290 = np.zeros((dim,))
	global DOBYR 
	DOBYR = np.zeros((dim,))
	global SDOBYR
	SDOBYR = np.zeros((dim,))
	global DOBMD 
	DOBMD = np.zeros((dim,))
	global SDOBMD
	SDOBMD = np.zeros((dim,))
	global e62600
	e62600 = np.zeros((dim,))
	global x62740
	x62740 = np.zeros((dim,))
	global _fixeic
	_fixeic = np.zeros((dim,))
	global e32880 
	e32880 = np.zeros((dim,))
	global e32890
	e32890 = np.zeros((dim,))
	global CDOB1 
	CDOB1 = np.zeros((dim,))
	global CDOB2 
	CDOB2 = np.zeros((dim,))	
	global e32750 
	e32750 = np.zeros((dim,))
	global e32775
	e32775 = np.zeros((dim,))
	global e33420 
	e33420 = np.zeros((dim,))
	global e33430 
	e33430 = np.zeros((dim,))
	global e33450
	e33450 = np.zeros((dim,))
	global e33460 
	e33460 = np.zeros((dim,))
	global e33465
	e33465 = np.zeros((dim,))
	global e33470 
	e33470 = np.zeros((dim,))
	global x59560
	x59560 = np.zeros((dim,))
	global EICYB1 
	EICYB1 = np.zeros((dim,))
	global EICYB2 
	EICYB2 = np.zeros((dim,))
	global EICYB3
	EICYB3 = np.zeros((dim,))
	global e83080
	e83080 = np.zeros((dim,))
	global e25360
	e25360 = np.zeros((dim,))
	global e25430 
	e25430 = np.zeros((dim,))
	global e25470 
	e25470 = np.zeros((dim,))
	global e25400 
	e25400 = np.zeros((dim,))
	global e25500 
	e25500 = np.zeros((dim,))
	global e26210 
	e26210 = np.zeros((dim,))
	global e26340 
	e26340 = np.zeros((dim,))
	global e26205 
	e26205 = np.zeros((dim,))
	global e26320 
	e26320 = np.zeros((dim,))


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
	global c23650
	global c01000
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
	c02500 = np.where(np.logical_or(SSIND != 0, 
		np.logical_and(MARS >= 3, MARS <= 6)), e02500, 
		np.where(_ymod < _ssb50[MARS-1], 0, 
			np.where(np.logical_and(_ymod >= _ssb50[MARS-1], 
				_ymod < _ssb85[MARS-1]), 
				0.5 * np.minimum(_ymod - _ssb50[MARS-1], e02400), 
				np.minimum(0.85 * (_ymod - _ssb85[MARS-1]) + 0.50 * 
					np.minimum(e02400, _ssb85[MARS-1] - _ssb50[MARS-1]), 
					0.85 * e02400)))) 


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

	c04600 = _prexmp 


def ItemDed(puf): 
	#Itemized Deductions
	global c04470
	global c21060
	global c21040

	# Medical #
	c17750 = 0.075 * _posagi 
	c17000 = np.maximum(0, e17500 - c17750)

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
	c21060 = (e20900 + c17000 + c18300 + c19200 + c19700 
		+ c20500 + c20800 + e21000 + e21010)
	
    # Itemized Deduction Limitation
	_phase2 = np.where(MARS == 1, 200000, np.where(MARS == 4, 250000, 300000))

	_itemlimit = 1
	_c21060 = c21060
	_nonlimited = c17000 + c20500 + e19570 + e21010 + e20900
	_limitratio = _phase2/_sep 

	_itemlimit = np.where(np.logical_and(c21060 > _nonlimited, 
		c00100 > _phase2/_sep), 2, 1)
	_dedmin = np.where(np.logical_and(c21060 > _nonlimited, 
		c00100 > _phase2/_sep), 0.8 * (c21060 - _nonlimited), 0)
	_dedpho = np.where(np.logical_and(c21060 > _nonlimited, 
		c00100 > _phase2/_sep), 0.03 * np.maximum(0, _posagi - _phase2/_sep), 0)
	c21040 = np.where(np.logical_and(c21060 > _nonlimited, 
		c00100 > _phase2/_sep), np.minimum(_dedmin, _dedpho), 0)
	c04470 = np.where(np.logical_and(c21060 > _nonlimited, 
		c00100 > _phase2/_sep), c21060 - c21040, c21060)


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
	global _taxinc
	global _feitax

	c15100 = np.where(DSI == 1, 
		np.maximum(300 + _earned, _stded[FLPDYR-2013, 6]), 0)

	c04100 = np.where(DSI == 1, np.minimum(_stded[FLPDYR-2013, MARS-1], c15100), 
		np.where(np.logical_or(_compitem == 1, 
			np.logical_and(np.logical_and(3<= MARS, MARS <=6), MIdR == 1)), 
		0, _stded[FLPDYR-2013, MARS-1]))


	c04100 = c04100 + e15360
	_numextra = AGEP + AGES + PBI + SBI 

	_txpyers = np.where(np.logical_or(np.logical_or(MARS == 2, MARS == 3), 
		MARS == 3), 2, 1)
	c04200 = np.where(np.logical_and(_exact == 1, 
		np.logical_or(MARS == 3, MARS == 5)), 
		e04200, _numextra * _aged[_txpyers -1, FLPDYR - 2013])

	c15200 = c04200

	_standard = np.where(np.logical_and(np.logical_or(MARS == 3, MARS == 6), 
		c04470 > 0), 
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
	_amtstd = np.zeros((dim,))
	c60000 = np.where(np.logical_and(np.logical_and(e04470 == 0, 
		t04470 > _amtstd), 
		np.logical_and(f6251 == 1, _exact == 1)), c00100 - t04470, c60000)

	_taxinc = np.where(np.logical_and(c04800 > 0, _feided > 0), 
		c04800 + c02700, c04800)
	
	_feitax = np.zeros((dim,))
	_oldfei = np.zeros((dim,))

	_feitax = Taxer(inc_in= _feided, inc_out =_feitax, MARS = MARS)
	_oldfei = Taxer(inc_in = c04800, inc_out = _oldfei, MARS = MARS)

	_feitax = np.where(np.logical_or(c04800 < 0, _feided < 0), 0, _feitax)

def XYZD():
	global c24580
	global _xyztax
	_xyztax = np.zeros((dim,))
	c05200 = np.zeros((dim,))
	_xyztax = Taxer(inc_in = _taxinc, inc_out = _xyztax, MARS= MARS)
	c05200 = Taxer(inc_in = c04800, inc_out = c05200, MARS = MARS)
	

def NonGain():
	_cglong = np.minimum(c23650, e23250 + e01100)
	_noncg = np.zeos((dim,))

def TaxGains():
	global c05750
	c24517 = np.zeros((dim,))
	c24520 = np.zeros((dim,))
	c24530 = np.zeros((dim,))
	c24553 = np.zeros((dim,))
	c24540 = np.zeros((dim,))
	c24581 = np.zeros((dim,))
	c24542 = np.zeros((dim,)) 
	_dwks16 = np.zeros((dim,))

	_hasgain = np.zeros((dim,))

	_hasgain = np.where(np.logical_or(e01000 > 0, c23650 > 0), 1, _hasgain)
	_hasgain = np.where(np.logical_or(e23250 > 0, e01100 > 0), 1, _hasgain)
	_hasgain = np.where(e00650 > 0, 1, _hasgain)

	#significance of sum() function here in original SAS code?	
	_dwks5 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, e58990 - e58980), 0)
	c24505 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, c00650 - _dwks5), 0)
	c24510 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, np.minimum(c23650, e23250)) + e01100, 0)
	#gain for tax computation

	c24510 = np.where(np.logical_and(_taxinc > 0, np.logical_and(_hasgain == 1, e01100 > 0)), e01100, c24510)
	#from app f 2008 drf

	_dwks9 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, c24510 - np.minimum(e58990, e58980)), 0)
	#e24516 gain less invest y 

	c24516 = np.maximum(0, np.minimum(e23250, c23650)) + e01100
	c24580 = _xyztax

	c24516 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24505 + _dwks9, c24516)
	_dwks12 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_dwks9, e24515 + e24518), 0)
	c24517 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24516 -_dwks12, 0)
	#gain less 25% and 28%

	c24520 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc -c24517), 0)
	#tentative TI less schD gain

	c24530 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_brk2[FLPDYR-2013, MARS-1], _taxinc), 0)
	#minimum TI for bracket

	_dwks16 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(c24520, c24530), 0)
	_dwks17 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - c24516), 0)
	c24540 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(_dwks16, _dwks17), 0)

	c24534 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24530 - _dwks16, 0)
	_dwks21 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_taxinc, c24517), 0)
	c24597 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks21 - c24534), 0)
	#income subject to 15% tax

	c24598 = 0.15 * c24597 #actual 15% tax

	_dwks25 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_dwks9, e24515), 0)
	_dwks26 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24516 + c24540, 0)
	_dwks28 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _taxinc), 0)
	c24610 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _dwks28), 0)
	c24615 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), 0.25 * c24610, 0)
	_dwks31 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24540 + c24534 + c24597 + c24610, 0)
	c24550 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - _dwks31), 0)
	c24570 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), 0.28 * c24550, 0)
	_addtax = np.zeros((dim,))
	_addtax = np.where(np.logical_and(_taxinc > 0, np.logical_and(_hasgain == 1, c24540 > _brk6[FLPDYR-2013, MARS-1])), 0.05 * c24517, _addtax)
	_addtax = np.where(np.logical_and(np.logical_and(_taxinc > 0, _hasgain == 1), np.logical_and(c24540 <= _brk6[FLPDYR-2013, MARS-1], _taxinc > _brk6[FLPDYR-2013, MARS-1])), 0.05 * np.minimum(c04800 - _brk6[FLPDYR-2013, MARS-1], c24517), _addtax)

	c24560 = np.zeros((dim,))
	c24560 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), Taxer(inc_in = c24540, inc_out = c24560, MARS = MARS), c24560)

	_taxspecial = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24598 + c24615 + c24570 + c24560 + _addtax, 0)

	c05100 = c24580
	c05100 = np.where(np.logical_and(c04800 > 0, _feided > 0), np.maximum(0, c05100 - _feitax), c05100)

	#Form 4972 - Lump Sum Distributions
	c05700 = np.zeros((dim,))

	c59430 = np.where(_cmp == 1, np.maximum(0, e59410 - e59420), 0)
	c59450 = np.where(_cmp == 1, c59430 + e59440, 0) #income plus lump sum
	c59460 = np.where(_cmp == 1, np.maximum(0, np.minimum(0.5 * c59450, 10000)) - 0.2 * np.maximum(0, c59450 - 20000), 0)
	_line17 = np.where(_cmp == 1, c59450 - c59460, 0)
	_line19 = np.where(_cmp == 1, c59450 - c59460 - e59470, 0)
	_line22 = np.where(np.logical_and(_cmp == 1, c59450 > 0), np.maximum(0, e59440 - e59440 * c59460/c59450),0)

	_line30 = np.where(_cmp == 1, 0.1 * np.maximum(0, c59450 - c59460 - e59470), 0)

	_line31 = np.where(_cmp == 1, 
		0.11 * np.minimum(_line30, 1190)
		+ 0.12 * np.minimum( 2270 - 1190, np.maximum(0, _line30 - 1190))
		+ 0.14 * np.minimum( 4530 - 2270, np.maximum(0, _line30 - 2270))
		+ 0.15 * np.minimum( 6690 - 4530, np.maximum(0, _line30 - 4530))
		+ 0.16 * np.minimum( 9170 - 6690, np.maximum(0, _line30 - 6690))
		+ 0.18 * np.minimum(11440 - 9170, np.maximum(0, _line30 - 9170))
		+ 0.20 * np.minimum(13710 - 11440, np.maximum(0, _line30 - 11440))
		+ 0.23 * np.minimum(17160 - 13710, np.maximum(0, _line30 - 13710))
		+ 0.26 * np.minimum(22880 - 17160, np.maximum(0, _line30 - 17160))
		+ 0.30 * np.minimum(28600 - 22880, np.maximum(0, _line30 - 22880))
		+ 0.34 * np.minimum(34320 - 28600, np.maximum(0, _line30 - 28600))
		+ 0.38 * np.minimum(42300 - 34320, np.maximum(0, _line30 - 34320))
		+ 0.42 * np.minimum(57190 - 42300, np.maximum(0, _line30 - 42300))
		+ 0.48 * np.minimum(85790 - 57190, np.maximum(0, _line30 - 57190)),
		0)

	_line32 = np.where(_cmp == 1, 10 * _line31, 0)
	_line36 = np.where(np.logical_and(_cmp == 1, e59440 == 0), _line32, 0)
	_line33 = np.where(np.logical_and(_cmp == 1, e59440 > 0), 0.1 * _line22, 0)
	_line34 = np.where(np.logical_and(_cmp == 1, e59440 > 0),
		0.11 * np.minimum(_line30, 1190)
		+ 0.12 * np.minimum( 2270 - 1190, np.maximum(0, _line30 - 1190))
		+ 0.14 * np.minimum( 4530 - 2270, np.maximum(0, _line30 - 2270))
		+ 0.15 * np.minimum( 6690 - 4530, np.maximum(0, _line30 - 4530))
		+ 0.16 * np.minimum( 9170 - 6690, np.maximum(0, _line30 - 6690))
		+ 0.18 * np.minimum(11440 - 9170, np.maximum(0, _line30 - 9170))
		+ 0.20 * np.minimum(13710 - 11440, np.maximum(0, _line30 - 11440))
		+ 0.23 * np.minimum(17160 - 13710, np.maximum(0, _line30 - 13710))
		+ 0.26 * np.minimum(22880 - 17160, np.maximum(0, _line30 - 17160))
		+ 0.30 * np.minimum(28600 - 22880, np.maximum(0, _line30 - 22880))
		+ 0.34 * np.minimum(34320 - 28600, np.maximum(0, _line30 - 28600))
		+ 0.38 * np.minimum(42300 - 34320, np.maximum(0, _line30 - 34320))
		+ 0.42 * np.minimum(57190 - 42300, np.maximum(0, _line30 - 42300))
		+ 0.48 * np.minimum(85790 - 57190, np.maximum(0, _line30 - 57190)),
		0)
	_line35 = np.where(np.logical_and(_cmp == 1, e59440 > 0), 10 * _line34, 0)
	_line36 = np.where(np.logical_and(_cmp == 1, e59440 > 0), np.maximum(0, _line32 - _line35), 0)
	#tax saving from 10 yr option
	c59485 = np.where(_cmp == 1, _line36, 0)
	c59490 = np.where(_cmp == 1, c59485 + 0.2 * np.maximum(0, e59400), 0)
	#pension gains tax plus

	c05700 = np.where(_cmp == 1, c59490, 0)

	_s1291 = e10105
	_parents = e83200_0
	c05750 = np.maximum(c05100 + _parents + c05700, e74400)
	_taxbc = c05750 
	x05750 = c05750 

	return c05750

 
def MUI(c05750):
	#Additional Medicare tax on unearned Income 
	c05750 = c05750
	c00100[5] = 100000000
	c05750[6] = 1234
	c05750 = np.where(c00100 > _thresx[MARS-1], 0.038 * np.minimum(e00300 + e00600 + np.maximum(0, c01000) + np.maximum(0, e02000), c00100 - _thresx[MARS-1]), c05750)
	
	

def AMTI(c62100):
	c62100 = c62100
	c62720 = c24517 + x62720 
	c60260 = e00700 + x60260
	c63100 = np.maximum(0, _taxbc - e07300)
	c60200 = np.minimum(c17000, 0.025 * _posagi)
	c60240 = c18300 + x60240
	c60220 = c20800 + x60220
	c60130 = c21040 + x60130 
	c62730 = e24515 + x62730

	_addamt = np.where(np.logical_or(_exact == 0, np.logical_and(_exact == 1, c60200 + c60220 + c60240 + e60290 > 0)), c60200 + c60240 + c60220 + e60290 - c60130, 0)

	c62100 = np.where(_cmp == 1, c62100 - e60250, c62100)

	_cmbtp = np.zeros((dim,))

	_edical = np.where(np.logical_and(puf == True, np.logical_or(_standard == 0, np.logical_and(_exact == 1, e04470 > 0))), np.maximum(0, e17500 - np.maximum(0, e00100) * 0.075), 0)

	_cmbtp = np.where(np.logical_and(puf == True, np.logical_and(np.logical_or(_standard == 0, np.logical_and(_exact == 1, e04470 > 0)), f6251 == 1)), -1 * np.minimum(_edical, 0.025 * np.maximum(0, e00100)) + e62100 + c60260 + e04470 + e21040 - _sit - e00100 - e18500 - e20800, _cmbtp)

	c62100 = np.where(np.logical_and(puf == True, np.logical_or(_standard == 0, np.logical_and(_exact == 1, e04470 > 0))), c00100 - c04470 + np.minimum(c17000, 0.025 * np.maximum(0, c00100)) + _sit + e18500 - c60260 + c20800 - c21040 + _cmbtp, c62100)

	_cmbtp = np.where(np.logical_and(puf == True, np.logical_and(_standard > 0, f6251 == 1)), e62100 - e00100 + c60260, _cmbtp)
	c62100 = np.where(np.logical_and(puf == True, np.logical_and(_standard > 0, f6251 == 1)), c00100 - c60260 + _cmbtp, c62100)

	x62100 = c62100

	_amtsepadd = np.where(np.logical_and(c62100 > _amtsep[FLPDYR-1], np.logical_or(MARS == 3, MARS == 6)), np.maximum(0, np.minimum(_almsep[FLPDYR-2013], 0.25 * (c62100 - _amtsep[FLPDYR-2013]))), 0)
	c62100 = np.where(np.logical_and(c62100 > _amtsep[FLPDYR-1], np.logical_or(MARS == 3, MARS == 6)), c62100 + _amtsepadd, c62100)

	c62600 = np.maximum(0, _amtex[FLPDYR-2013, MARS-1] - 0.25 * np.maximum(0, c62100 - _amtys[MARS-1]))

	_agep = np.where(DOBYR > 0, np.ceil((12 * (FLPDYR - DOBYR) - DOBMD/100)/12), 0)
	_ages = np.where(SDOBYR > 0, np.ceil((12 * (FLPDYR - SDOBYR) - SDOBMD/100)/12), 0)

	c62600 = np.where(np.logical_and(_cmp == 1, np.logical_and(f6251 == 1, _exact == 1)), e62600, c62600)

	#_cmp == 1 and _exact == 0 and (_agep < amtage and agep =/= 0)

	c62600 = np.where(np.logical_and(np.logical_and(_cmp == 1, _exact == 0), np.logical_and(_agep < _amtage[FLPDYR-2013], _agep != 0)), np.minimum(c62600, _earned + _almdep[FLPDYR-2013]), c62600)

	c62700 = np.maximum(0, c62100 - c62600)

	_alminc = c62700
	_amtfei = np.zeros((dim,))

	_alminc = np.where(c02700 > 0, np.maximum(0, c62100 - c62600 + c02700), _alminc)
	_amtfei = np.where(c02700 > 0, 0.26 * c02700 + 0.02 * np.maximum(0, c02700 - _almsp[FLPDYR-2013]/_sep), _amtfei)

	c62780 = 0.26 * _alminc + 0.02 * np.maximum(0, _alminc - _almsp[FLPDYR-2013]/_sep) - _amtfei

	c62900 = np.where(f6251 != 0, e62900, e07300) 
	c63000 = c62780 - c62900

	c62740 = np.minimum(np.maximum(0, c24516 + x62740), c62720 + c62730)
	c62740 = np.where(c24516 == 0, c62720 + c62730, c62740)

	_ngamty = np.maximum(0, _alminc - c62740)

	c62745 = 0.26 * _ngamty + 0.02 * np.maximum(0, _ngamty - _almsp[FLPDYR-2013]/_sep)
	y62745 = _almsp[FLPDYR-2013]/_sep
	_tamt2 = np.zeros((dim,))

	_amt5pc = np.zeros((dim,))
	_amt15pc = np.minimum(_alminc, c62720) - _amt5pc - np.minimum(np.maximum(0, _brk2[FLPDYR-2013, MARS-1] - c24520), np.minimum(_alminc, c62720))
	_amt15pc = np.where(c04800 == 0, np.maximum(0, np.minimum(_alminc, c62720) - _brk2[FLPDYR-2013, MARS-1]), _amt15pc)
	_amt25pc = np.minimum(_alminc, c62740) - np.minimum(_alminc, c62720)

	_amt25pc = np.where(c62730 == 0, 0, _amt25pc)
	c62747 = _cgrate1[FLPDYR-2013] * _amt5pc
	c62755 = _cgrate2[FLPDYR-2013] * _amt15pc
	c62770 = 0.25 * _amt25pc
	_tamt2 = c62747 + c62755 + c62770

	_amt = np.zeros((dim,))
	_amt = np.where(_ngamty > _brk6[FLPDYR-2013, MARS-1], 0.05 * np.minimum(_alminc, c62740), _amt)
	_amt = np.where(np.logical_and(_ngamty <= _brk6[FLPDYR-2013, MARS-1], _alminc > _brk6[FLPDYR-2013, MARS-1]), 0.05 * np.minimum(_aliminc - _brk6[FLPDYR-2013, MARS-1], c62740), _amt)

	c62800 = np.minimum(c62780, c62745 + _tamt2 - _amtfei)
	c63000 = c62800 - c62900 
	c63100 = _taxbc - e07300 - c05700 
	c63100 = c63100 + e10105

	c63100 = np.maximum(0, c63100)
	c63200 = np.maximum(0, c63000 - c63100)
	c09600 = c63200
	_othtax = e05800 - (e05100 + e09600)

	c05800 = _taxbc + c63200

def F2441(_earned):
	_earned = _earned
	_earned = np.where(_fixeic == 1, e59560, _earned)
	c32880 = np.where(np.logical_and(MARS == 2, puf == True), 0.5 * _earned, 0)
	c32890 = np.where(np.logical_and(MARS == 2, puf == True), 0.5 * _earned, 0)
	c32880 = np.where(np.logical_and(MARS == 2, puf == False), np.maximum(0, e32880), c32880)
	c32890 = np.where(np.logical_and(MARS == 2, puf == False), np.maximum(0, e32890), c32890)
	c32880 = np.where(MARS != 2, _earned, c32880)
	c32890 = np.where(MARS != 2, _earned, c32890)	

	_ncu13 = np.zeros((dim,))
	_ncu13 = np.where(puf == True, f2441, _ncu13)
	_ncu13 = np.where(np.logical_and(puf == False, CDOB1 > 0), _ncu13 + 1, _ncu13)
	_ncu13 = np.where(np.logical_and(puf == False, CDOB2 > 0), _ncu13 + 1, _ncu13)

	_dclim = np.minimum(_ncu13, 2) * _dcmax[FLPDYR-2013]
	c32800 = np.minimum(np.maximum(e32800, e32750 + e32775), _dclim)

def DepCareBen():
	#Part III ofdependent care benefits
	_seywage = np.where(np.logical_and(_cmp == 1, MARS == 2), np.minimum(c32880, np.minimum(c32890, np.minimum(e33420 + e33430 - e33450, e33460))), 0)
	_seywage = np.where(np.logical_and(_cmp == 1, MARS != 2), np.minimum(c32880, np.minimum(e33420 + e33430 - e33450, e33460)), _seywage)

	c33465 = np.where(_cmp == 1, e33465, 0)
	c33470 = np.where(_cmp == 1, e33470, 0)
	c33475 = np.where(_cmp == 1, np.maximum(0, np.minimum(_seywage, 5000/_sep) - c33470), 0)
	c33480 = np.where(_cmp == 1, np.maximum(0, e33420 + e33430 - e33450 - c33465 - c33475), 0)
	c32840 = np.where(_cmp == 1, c33470 + c33475, 0)
	c32800 = np.where(_cmp == 1, np.minimum(np.maximum(0, _dclim - c32840), np.maximum(0, e32750 + e32775 - c32840)), 0)

	c33000 = np.where(MARS == 2, np.maximum(0, np.minimum(c32800, np.minimum(c32880, c32890))), 0)
	c33000 = np.where(MARS != 2, np.maximum(0, np.minimum(c32800, _earned)), c33000)


def ExpEarnedInc():
	#Expenses limited to earned income

	_tratio  = np.where(_exact == 1, np.ceil(np.maximum((c00100 - _agcmax[FLPDYR-2013])/2000, 0)), 0)
	c33200 = np.where(_exact == 1, c33000 * 0.01 * np.maximum(20, _pcmax[FLPDYR-2013] - np.minimum(15, _tratio)), 0)
	c33200 = np.where(_exact != 1, c3300 * 0.01 * np.maximum(20, _pcmax[FLPDYR-2013] - np.maximum((c00100 - _agcmax[FLPDYR-2013])/2000, 0)), c33200)

	c33400 = np.minimum(np.maximum(0, np.maximum(c05800 - e07300, c33200)))
	#amount of the credit

	c07180 = np.where(e07180 == 0, 0, c33400)


def RateRed(c05800):
	#rate reduction credit for 2001 only, is this needed?
	c05800 = c05800 
	c07970 = np.zeros((dim,))
	x07970 = c07970

	c05800 = np.where(_fixup >= 3, c05800 + _othtax, c05800)

	c59560 = np.where(_exact == 1, x59560, _earned)


def NumDep():
	#Number of dependents for EIC 

	_ieic = np.zeros((dim,))

	EICYB1_1 = np.where(EICYB1 < 0, 0, EICYB1)
	EICYB2_2 = np.where(EICYB2 < 0, 0, EICYB2)
	EICYB3_3 = np.where(EICYB3 < 0, 0, EICYB3)

	_ieic = np.where(puf == True, EIC, EICYB1_1 + EICYB2_2 + EICYB3_3)

	#Modified AGI only through 2002 

	_modagi = c00100 + e00400 
	c59660 = np.zeros((dim,))

	_val_ymax = np.where(np.logical_and(MARS == 2, _modagi > 0), _ymax[_ieic-1, FLPDYR-2013] + _joint[FLPDYR-2013], 0)
	_val_ymax = np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(MARS == 4, np.logical_or(MARS == 5, MARS == 7)))), _ymax[_ieic-1, FLPDYR-2013], _val_ymax)
	c59660 = np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(MARS == 4, np.logical_or(MARS == 5, np.logical_or(MARS == 2, MARS == 7))))), np.minimum(_rtbase[_ieic-1, FLPDYR-2013] * c59560, _crmax[_ieic-1, FLPDYR-2013]), c59560)
	_preeitc =  np.where(np.logical_and(_modagi > 0, np.logical_or(MARS == 1, np.logical_or(MARS == 4, np.logical_or(MARS == 5, np.logical_or(MARS == 2, MARS == 7))))), c59660, 0)

	c59660 = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), np.logical_and(_modagi > 0, np.logical_or(_modagi > _val_ymax, c59560 > _val_ymax))), np.maximum(0, c59660 - _rtless[_ieic-1, FLPDYR-2013] * (np.maximum(_modagi, c59560) - _val_ymax)), c59560)
	_val_rtbase = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), _modagi > 0), _rtbase[_ieic-1, FLPDYR-2013] * 100, 0)
	_val_rtless = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), _modagi > 0), _rtless[_ieic-1, FLPDYR-2013] * 100, 0)

	_dy = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), _modagi > 0), e00400 + e83080 + e00300 + e00600 
		+ np.maximum(0, np.maximum(0, e01000) - np.maximum(0, e40223))
		+ np.maximum(0, np.maximum(0, e25360) - e25430 - e25470 - e25400 - e25500)
		+ np.maximum(0, e26210 + e26340 + e27200 - np.absolute(e26205) - np.absolute(e26320)), 0)

	c59660 = np.where(np.logical_and(np.logical_and(MARS != 3, MARS != 6), np.logical_and(_modagi > 0, _dy > _dylim[FLPDYR-2013])), 0, c59660)

	c59660 = np.where(np.logical_and(np.logical_and(_cmp == 1, _ieic == 0), np.logical_and(np.logical_and(SOIYR - DOBYR >= 25, SOIYR - DOBYR < 65), np.logical_and(SOIYR - SDOBYR >= 25, SOIYR - SDOBYR < 65))), 0, c59660)
	c59660 = np.where(np.logical_and(_ieic == 0, np.logical_or(np.logical_or(_agep < 25, _agep >= 65), np.logical_or(_ages < 25, _ages >= 65))), 0, c59660)

def ChildTaxCredit():
	#Child Tax Credit

	c11070 = np.zeros((dim,))
	c07220 = np.zeros((dim,))
	c07230 = np.zeros((dim,))
	_precrd = np.zeros((dim,))

	_num = np.where(MARS == 2, 2, 1)

	_nctcr = n24

	_precrd = _chmax[FLPDYR-2013] * _nctcr 
	_ctcagi = e00100 + _feided

	_precrd = np.where(np.logical_and(_ctcagi > _cphase[MARS-1], _exact == 1), np.maximum(0, _precrd - 50 * np.ceil(np.maximum(0, _ctcagi - _cphase[MARS-1])/1000)), 0)
	_precrd = np.where(np.logical_and(_ctcagi > _cphase[MARS-1], _exact != 1), np.maximum(0, _precrd - 50 * (np.maximum(0, _ctcagi - _cphase[MARS-1]) + 500)/1000), _precrd)

def HopeCredit():
	#Hope credit for 1998-2009, I don't think this is needed 
	#Leave blank for now, ask Dan
	#SAS lnies 951 - 972

def AmOppCr():
	#American Opportunity Credit 2009+ 

	


def Taxer(inc_in, inc_out, MARS):
	low = np.where(inc_in < 3000, 1, 0)
	med = np.where(np.logical_and(inc_in >= 3000, inc_in < 100000), 1, 0)

	_a1 = inc_in/100
	_a2 = np.floor(_a1)
	_a3 = _a2*100
	_a4 = (_a1 - _a2) * 100

	_a5 = np.zeros((dim,))
	_a5 = np.where(np.logical_and(low == 1, _a4 < 25), 13, _a5)
	_a5 = np.where(np.logical_and(low == 1, np.logical_and(_a4 >= 25, _a4 < 50)), 38, _a5)
	_a5 = np.where(np.logical_and(low == 1, np.logical_and(_a4 >= 50, _a4 < 75)), 63, _a5)
	_a5 = np.where(np.logical_and(low == 1, _a4 >= 75), 88, _a5)

	_a5 = np.where(np.logical_and(med == 1, _a4 < 50), 25, _a5)
	_a5 = np.where(np.logical_and(med == 1, _a4 >= 50), 75, _a5)

	_a5 = np.where(inc_in == 0, 0, _a5)

	_a6 = np.where(np.logical_or(low==1, med ==1), _a3 + _a5, inc_in)

	inc_out = (_rt1[FLPDYR-2013] * np.minimum(_a6, _brk1[FLPDYR-2013, MARS-1])
		+ _rt2[FLPDYR-2013] 
		* np.minimum(_brk2[FLPDYR-2013, MARS-1] - _brk1[FLPDYR-2013, MARS-1],
			np.maximum(0, _a6 - _brk1[FLPDYR-2013, MARS-1]))
		+ _rt3[FLPDYR-2013]
		* np.minimum(_brk3[FLPDYR-2013, MARS-1] - _brk2[FLPDYR-2013, MARS-1],
			np.maximum(0, _a6 - _brk2[FLPDYR-2013, MARS-1]))
		+ _rt4[FLPDYR-2013]
		* np.minimum(_brk4[FLPDYR-2013, MARS-1] - _brk3[FLPDYR-2013, MARS-1],
			np.maximum(0, _a6 - _brk3[FLPDYR-2013, MARS-1]))
		+ _rt5[FLPDYR-2013]
		* np.minimum(_brk5[FLPDYR-2013, MARS-1] - _brk4[FLPDYR-2013, MARS-1],
			np.maximum(0, _a6 - _brk4[FLPDYR-2013, MARS-1]))
		+ _rt6[FLPDYR-2013]
		* np.minimum(_brk6[FLPDYR-2013, MARS-1] - _brk5[FLPDYR-2013, MARS-1],
			np.maximum(0, _a6 - _brk5[FLPDYR-2013, MARS-1]))
		+ _rt7[FLPDYR-2013] * np.maximum(0, _a6 -_brk6[FLPDYR-2013, MARS-1]))

	return inc_out


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
	XYZD()
	NonGain()
	TaxGains()
	MUI(c05750 = c05750)

	outputs = (_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi, 
		c00100, c04600, c04470, c21060, _earned, c04800, c60000, c05750)
	output = np.column_stack(outputs)

	np.savetxt('output.csv', output, delimiter=',', 
		header = ('_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi,' 
			'c00100, c04600, c04470, c21060, _earned, c04800, c60000, c05750') 
		, fmt = '%1.3f')
