import pandas as pd
import math
import numpy as np

output_filename = 'translationoutput.csv' 
input_filename = 'puf.csv'
x = pd.read_csv(input_filename)

names = x.columns.values

y = {}

for n in names:
	y[n] = np.array(x[n])

AGIR1 = y['AGIR1']
DSI = y['DSI']
EFI = y['EFI']
EIC = y['EIC']
ELECT = y['ELECT']
FDED = y['FDED']
FLPDYR = y['FLPDYR']
FLPDMO = y['FLPDMO']
F2441 = y['F2441']
F3800 = y['F3800']
F6251 = y['F6251']
F8582 = y['F8582']
F8606 = y['F8606']
IE = y['IE']
MARS = y['MARS']
MIdR = y['MIdR']
N20 = y['N20']
N24 = y['N24']
N25 = y['N25']
PREP = y['PREP']
SCHB = y['SCHB']
SCHCF = y['SCHCF']
SCHE = y['SCHE']
STATE = y['STATE']
TFORM = y['TFORM']
TXST = y['TXST']
XFPT = y['XFPT']
XFST = y['XFST']
XOCAH = y['XOCAH']
XOCAWH = y['XOCAWH']
XOODEP = y['XOODEP']
XOPAR = y['XOPAR']
XTOT = y['XTOT']
E00200 = y['E00200']
E00300 = y['E00300']
E00400 = y['E00400']
E00600 = y['E00600']
E00650 = y['E00650']
E00700 = y['E00700']
E00800 = y['E00800']
E00900 = y['E00900']
E01000 = y['E01000']
E01100 = y['E01100']
E01200 = y['E01200']
E01400 = y['E01400']
E01500 = y['E01500']
E01700 = y['E01700']
E02000 = y['E02000']
E02100 = y['E02100']
E02300 = y['E02300']
E02400 = y['E02400']
E02500 = y['E02500']
E03150 = y['E03150']
E03210 = y['E03210']
E03220 = y['E03220']
E03230 = y['E03230']
E03260 = y['E03260']
E03270 = y['E03270']
E03240 = y['E03240']
E03290 = y['E03290']
E03300 = y['E03300']
E03400 = y['E03400']
E03500 = y['E03500']
E00100 = y['E00100']
P04470 = y['P04470']
E04250 = y['E04250']
E04600 = y['E04600']
E04800 = y['E04800']
E05100 = y['E05100']
E05200 = y['E05200']
E05800 = y['E05800']
E06000 = y['E06000']
E06200 = y['E06200']
E06300 = y['E06300']
E09600 = y['E09600']
E07180 = y['E07180']
E07200 = y['E07200']
E07220 = y['E07220']
E07230 = y['E07230']
E07240 = y['E07240']
E07260 = y['E07260']
E07300 = y['E07300']
E07400 = y['E07400']
E07600 = y['E07600']
P08000 = y['P08000']
E07150 = y['E07150']
E06500 = y['E06500']
E08800 = y['E08800']
E09400 = y['E09400']
E09700 = y['E09700']
E09800 = y['E09800']
E09900 = y['E09900']
E10300 = y['E10300']
E10700 = y['E10700']
E10900 = y['E10900']
E59560 = y['E59560']
E59680 = y['E59680']
E59700 = y['E59700']
E59720 = y['E59720']
E11550 = y['E11550']
E11070 = y['E11070']
E11100 = y['E11100']
E11200 = y['E11200']
E11300 = y['E11300']
E11400 = y['E11400']
E11570 = y['E11570']
E11580 = y['E11580']
E11581 = y['E11581']
E11582 = y['E11582']
E11583 = y['E11583']
E10605 = y['E10605']
E11900 = y['E11900']
E12000 = y['E12000']
E12200 = y['E12200']
E17500 = y['E17500']
E18425 = y['E18425']
E18450 = y['E18450']
E18500 = y['E18500']
E19200 = y['E19200']
E19550 = y['E19550']
E19800 = y['E19800']
E20100 = y['E20100']
E19700 = y['E19700']
E20550 = y['E20550']
E20600 = y['E20600']
E20400 = y['E20400']
E20800 = y['E20800']
E20500 = y['E20500']
E21040 = y['E21040']
P22250 = y['P22250']
E22320 = y['E22320']
E22370 = y['E22370']
P23250 = y['P23250']
E24515 = y['E24515']
E24516 = y['E24516']
E24518 = y['E24518']
E24535 = y['E24535']
E24560 = y['E24560']
E24598 = y['E24598']
E24615 = y['E24615']
E24570 = y['E24570']
P25350 = y['P25350']
E25370 = y['E25370']
E25380 = y['E25380']
P25470 = y['P25470']
P25700 = y['P25700']
E25820 = y['E25820']
E25850 = y['E25850']
E25860 = y['E25860']
E25940 = y['E25940']
E25980 = y['E25980']
E25920 = y['E25920']
E25960 = y['E25960']
E26110 = y['E26110']
E26170 = y['E26170']
E26190 = y['E26190']
E26160 = y['E26160']
E26180 = y['E26180']
E26270 = y['E26270']
E26100 = y['E26100']
E26390 = y['E26390']
E26400 = y['E26400']
E27200 = y['E27200']
E30400 = y['E30400']
E30500 = y['E30500']
E32800 = y['E32800']
E33000 = y['E33000']
E53240 = y['E53240']
E53280 = y['E53280']
E53410 = y['E53410']
E53300 = y['E53300']
E53317 = y['E53317']
E53458 = y['E53458']
E58950 = y['E58950']
E58990 = y['E58990']
P60100 = y['P60100']
P61850 = y['P61850']
E60000 = y['E60000']
E62100 = y['E62100']
E62900 = y['E62900']
E62720 = y['E62720']
E62730 = y['E62730']
E62740 = y['E62740']
P65300 = y['P65300']
P65400 = y['P65400']
E68000 = y['E68000']
E82200 = y['E82200']
T27800 = y['T27800']
S27860 = y['S27860']
P27895 = y['P27895']
E87500 = y['E87500']
E87510 = y['E87510']
E87520 = y['E87520']
E87530 = y['E87530']
E87540 = y['E87540']
E87550 = y['E87550']
RECID = y['RECID']
S006 = y['S006']
S008 = y['S008']
S009 =  y['S009']
WSAMP = y['WSAMP']
TXRT = y['TXRT']

_adctcrt = np.array([0.15]) #Rate for additional ctc

_aged = np.array([[1500],[1200]]) #Extra std. ded. for aged

_almdep = np.array([6950]) #Child AMT Exclusion base

_almsp = np.array([179500]) #AMT bracket

_amex = np.array([3900]) #Personal Exemption

_amtage = np.array([24]) #Age for full AMT exclusion

_amtsep = np.array([232500]) #AMT Exclusion

_almsep = np.array([39275]) #Extra alminc for married sep

_agcmax = np.array([15000]) #??

_cgrate1 = np.array([0.10]) #Initial rate on long term gains

_cgrate2 = np.array([0.20]) #Normal rate on long term gains

_chmax = np.array([1000]) #Max Child Tax Credit per child 

_crmax = np.array([[487],[3250],[5372],[6044]]) #Max earned income credit

_dcmax = np.array([3000]) #Max dependent care expenses 

_dylim = np.array([3300]) #Limits for Disqualified Income

_ealim = np.array([3000]) #Max earn ACTC

_edphhs = np.array([63]) #End of educ phaseout - singles

_edphhm = np.array([126]) #End of educ phaseout - married 

_feimax = np.array([97600]) #Maximum foreign earned income exclusion

#_hopelm = np.array([1200])

_joint = np.array([0]) #Extra to ymax for joint

_learn = np.array([10000]) #Expense limit for the LLC

_pcmax = np.array([35]) #Maximum Percentage for f2441

_phase = np.array([172250]) #Phase out for itemized

_rtbase = np.array([[0.0765], [0.3400], [0.4000], [0.4000]]) #EIC base rate

_rtless = np.array([[0.0765], [0.1598], [0.2106], [0.2106]]) #EIC _phaseout rate

_ssmax = np.array([115800]) #SS Maximum taxable earnings

_ymax = np.array([[7970], [17530], [17530], [17530]]) #Start of EIC _phaseout

_rt1 = np.array([0.1]) #10% rate

_rt2 = np.array([0.15]) #15% rate

_rt3 = np.array([0.25]) #25% rate

_rt4 = np.array([0.28]) #28% rate

_rt5 = np.array([0.33]) #33% rate

_rt6 = np.array([0.35]) #35% rate

_rt7 = np.array([0.396]) #39.6% rate



def Comp(): 

	# Factors for joint or separate filing #

	_sep = np.where(np.logical_or(MARS == 3, MARS == 6), 2, 1)
	_txp = np.where(np.logical_or(MARS== 2, MARS == 5), 2, 1)


	# Form 2555 #

	_feided = np.zeros((139651,))
	#= np.maximum(E35300_0, E35600_0, + E35910_0) 


	# Adjustments #

	C02900 = E03210 + E03260 + E03270 + E03300 + E03400 + E03500 + E03220 + E03230 + E03240 + E03290
	# + x03150 + e03600 + e03280 + e03900 + e04000 + e03700 
	X02900 = C02900


	# Capital Gains #

	C23650 = np.zeros((139651,))
	#= C23250 + E22250 + E23660 
	C01000 = np.maximum(-3000/_sep, C23650)

	C02700 = np.zeros((139651,))
	#= np.minimum(_feided, _feimax[2013-FLPDYR] * F2555) - F2555 missing

	_ymod1 = E00200 + E00300 + E00600 + E00700 + E00800 + E00900 + C01000 + E01100 + E01200 + E01400 + E01700 + E02000 + E02100 + E02300 
	# E02800 + E02610 + E02600 - E02540
	_ymod2 = E00400 + E02400/2 - C02900
	_ymod3 = E03210 + E03230 + E03240
	# + E02615
	_ymod = _ymod1 + _ymod2 + _ymod3


	# Taxation of Social Security Benefits # 

	C02500 = np.zeros((139651,))
	#= np.where(np.logical_or(SSIND != 0, 3 <= MARS <= 6), E02500, np.minimum(0.85 * (_ymod - _ssb85[MARS]) + 0.50 * np.minimum(E02400, _ssb85[MARS] - _ssb50[MARS]), 0.85 * E02400))
	#= np.where(_ymod < _ssb50[MARS], 0, np.minimum(0.85 * (_ymod - _ssb85[MARS]) + 0.50 * np.minimum(E02400, _ssb85[MARS] - _ssb50[MARS]), 0.85 * E02400))
	#= np.where(np.logical_and(_ymod > _ssb50[MARS], _ymod < _ssb85[MARS]), 0.5 * np.minimum(_ymod - _ssb50[MARS], E02400), np.minimum(0.85 * (_ymod - _ssb85[MARS]) + 0.50 * np.minimum(E02400, _ssb85[MARS] - _ssb50[MARS]), 0.85 * E02400)) 

	
	# Gross Income #

	C02650 = _ymod1 + C02500 - C02700 
	#+ E02615


	# Adjusted Gross Income #
	
	C00100 = C02650 - C02900
	_agierr = E00100 - C00100
	#if _fixup >= 1 then C00100 = C00100 + _agierr

	_posagi = np.maximum(C00100, 0)
	_ywossbe = E00100 - E02500
	_ywossbc = C00100 - C02500


	# Personal Exemptions (_phaseout smoothed) #

	#if _exact: What is _exact??? 

	_dispc = 0

	C04600 = _prexmp * (1-_dispc)


	# Itemized Deductions #

	# Medical #
	C17750 = 0.75 * _posagi 
	C17000 = np.maximum(0, E17500 - C17750)
	xx = 2

	# State and Local Income Tax, or Sales Tax #
	







	
	
