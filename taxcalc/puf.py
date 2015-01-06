"""
This file reads input csv file and saves the variables 
"""

import pandas as pd
import numpy as np
import os.path

def set_input_data(calc):
    x = calc.tax_data
    dim = len(x)
    calc.dim = dim
    names = x.columns.values
    calc.names = names
    y = {}
    for n in names:
        y[n] = np.array(x[n])

    calc.AGIR1 = y['agir1']
    calc.DSI = y['dsi']
    calc.EFI = y['efi']
    calc.EIC = y['eic']
    calc.ELECT = y['elect']
    calc.FDED = y['fded']
    calc.FLPDYR = y['flpdyr']
    calc.FLPDMO = y['flpdmo']
    calc.f2441 = y['f2441']
    calc.f3800 = y['f3800']
    calc.f6251 = y['f6251']
    calc.f8582 = y['f8582']
    calc.f8606 = y['f8606']
    calc.IE = y['ie']
    calc.MARS = y['mars']
    calc.MIdR = y['midr']
    calc.n20 = y['n20']
    calc.n24 = y['n24']
    calc.n25 = y['n25']
    calc.PREP = y['prep']
    calc.SCHB = y['schb']
    calc.SCHCF = y['schcf']
    calc.SCHE = y['sche']
    calc.STATE = y['state']
    calc.TFORM = y['tform']
    calc.TXST = y['txst']
    calc.XFPT = y['xfpt']
    calc.XFST = y['xfst']
    calc.XOCAH = y['xocah']
    calc.XOCAWH = y['xocawh']
    calc.XOODEP = y['xoodep']
    calc.XOPAR = y['xopar']
    calc.XTOT = y['xtot']
    calc.e00200 = y['e00200']
    calc.e00300 = y['e00300']
    calc.e00400 = y['e00400']
    calc.e00600 = y['e00600']
    calc.e00650 = y['e00650']
    calc.e00700 = y['e00700']
    calc.e00800 = y['e00800']
    calc.e00900 = y['e00900']
    calc.e01000 = y['e01000']
    calc.e01100 = y['e01100']
    calc.e01200 = y['e01200']
    calc.e01400 = y['e01400']
    calc.e01500 = y['e01500']
    calc.e01700 = y['e01700']
    calc.e02000 = y['e02000']
    calc.e02100 = y['e02100']
    calc.e02300 = y['e02300']
    calc.e02400 = y['e02400']
    calc.e02500 = y['e02500']
    calc.e03150 = y['e03150']
    calc.e03210 = y['e03210']
    calc.e03220 = y['e03220']
    calc.e03230 = y['e03230']
    calc.e03260 = y['e03260']
    calc.e03270 = y['e03270']
    calc.e03240 = y['e03240']
    calc.e03290 = y['e03290']
    calc.e03300 = y['e03300']
    calc.e03400 = y['e03400']
    calc.e03500 = y['e03500']
    calc.e00100 = y['e00100']
    calc.p04470 = y['p04470']
    calc.e04250 = y['e04250']
    calc.e04600 = y['e04600']
    calc.e04800 = y['e04800']
    calc.e05100 = y['e05100']
    calc.e05200 = y['e05200']
    calc.e05800 = y['e05800']
    calc.e06000 = y['e06000']
    calc.e06200 = y['e06200']
    calc.e06300 = y['e06300']
    calc.e09600 = y['e09600']
    calc.e07180 = y['e07180']
    calc.e07200 = y['e07200']
    calc.e07220 = y['e07220']
    calc.e07230 = y['e07230']
    calc.e07240 = y['e07240']
    calc.e07260 = y['e07260']
    calc.e07300 = y['e07300']
    calc.e07400 = y['e07400']
    calc.e07600 = y['e07600']
    calc.p08000 = y['p08000']
    calc.e07150 = y['e07150']
    calc.e06500 = y['e06500']
    calc.e08800 = y['e08800']
    calc.e09400 = y['e09400']
    calc.e09700 = y['e09700']
    calc.e09800 = y['e09800']
    calc.e09900 = y['e09900']
    calc.e10300 = y['e10300']
    calc.e10700 = y['e10700']
    calc.e10900 = y['e10900']
    calc.e59560 = y['e59560']
    calc.e59680 = y['e59680']
    calc.e59700 = y['e59700']
    calc.e59720 = y['e59720']
    calc.e11550 = y['e11550']
    calc.e11070 = y['e11070']
    calc.e11100 = y['e11100']
    calc.e11200 = y['e11200']
    calc.e11300 = y['e11300']
    calc.e11400 = y['e11400']
    calc.e11570 = y['e11570']
    calc.e11580 = y['e11580']
    calc.e11581 = y['e11581']
    calc.e11582 = y['e11582']
    calc.e11583 = y['e11583']
    calc.e10605 = y['e10605']
    calc.e11900 = y['e11900']
    calc.e12000 = y['e12000']
    calc.e12200 = y['e12200']
    calc.e17500 = y['e17500']
    calc.e18425 = y['e18425']
    calc.e18450 = y['e18450']
    calc.e18500 = y['e18500']
    calc.e19200 = y['e19200']
    calc.e19550 = y['e19550']
    calc.e19800 = y['e19800']
    calc.e20100 = y['e20100']
    calc.e19700 = y['e19700']
    calc.e20550 = y['e20550']
    calc.e20600 = y['e20600']
    calc.e20400 = y['e20400']
    calc.e20800 = y['e20800']
    calc.e20500 = y['e20500']
    calc.e21040 = y['e21040']
    calc.p22250 = y['p22250']
    calc.e22320 = y['e22320']
    calc.e22370 = y['e22370']
    calc.p23250 = y['p23250']
    calc.e24515 = y['e24515']
    calc.e24516 = y['e24516']
    calc.e24518 = y['e24518']
    calc.e24535 = y['e24535']
    calc.e24560 = y['e24560']
    calc.e24598 = y['e24598']
    calc.e24615 = y['e24615']
    calc.e24570 = y['e24570']
    calc.p25350 = y['p25350']
    calc.e25370 = y['e25370']
    calc.e25380 = y['e25380']
    calc.p25470 = y['p25470']
    calc.p25700 = y['p25700']
    calc.e25820 = y['e25820']
    calc.e25850 = y['e25850']
    calc.e25860 = y['e25860']
    calc.e25940 = y['e25940']
    calc.e25980 = y['e25980']
    calc.e25920 = y['e25920']
    calc.e25960 = y['e25960']
    calc.e26110 = y['e26110']
    calc.e26170 = y['e26170']
    calc.e26190 = y['e26190']
    calc.e26160 = y['e26160']
    calc.e26180 = y['e26180']
    calc.e26270 = y['e26270']
    calc.e26100 = y['e26100']
    calc.e26390 = y['e26390']
    calc.e26400 = y['e26400']
    calc.e27200 = y['e27200']
    calc.e30400 = y['e30400']
    calc.e30500 = y['e30500']
    calc.e32800 = y['e32800']
    calc.e33000 = y['e33000']
    calc.e53240 = y['e53240']
    calc.e53280 = y['e53280']
    calc.e53410 = y['e53410']
    calc.e53300 = y['e53300']
    calc.e53317 = y['e53317']
    calc.e53458 = y['e53458']
    calc.e58950 = y['e58950']
    calc.e58990 = y['e58990']
    calc.p60100 = y['p60100']
    calc.p61850 = y['p61850']
    calc.e60000 = y['e60000']
    calc.e62100 = y['e62100']
    calc.e62900 = y['e62900']
    calc.e62720 = y['e62720']
    calc.e62730 = y['e62730']
    calc.e62740 = y['e62740']
    calc.p65300 = y['p65300']
    calc.p65400 = y['p65400']
    calc.e68000 = y['e68000']
    calc.e82200 = y['e82200']
    calc.t27800 = y['t27800']
    calc.e27860 = y['s27860']
    calc.p27895 = y['p27895']
    calc.e87500 = y['e87500']
    calc.e87510 = y['e87510']
    calc.e87520 = y['e87520']
    calc.e87530 = y['e87530']
    calc.e87540 = y['e87540']
    calc.e87550 = y['e87550']
    calc.RECID = y['recid']
    calc.s006 = y['s006']
    calc.s008 = y['s008']
    calc.s009 =  y['s009']
    calc.WSAMP = y['wsamp']
    calc.TXRT = y['txrt']

    """
    Previously defined in the Puf() function
    """

    calc.e35300_0 = np.zeros((dim,))
    calc.e35600_0 = np.zeros((dim,))
    calc.e35910_0 = np.zeros((dim,))
    calc.x03150 = np.zeros((dim,))
    calc.e03600 = np.zeros((dim,))
    calc.e03280 = np.zeros((dim,))
    calc.e03900 = np.zeros((dim,))
    calc.e04000 = np.zeros((dim,))
    calc.e03700 = np.zeros((dim,))
    calc.c23250 = np.zeros((dim,))
    calc.e22250 = calc.p22250
    calc.e23660 = np.zeros((dim,))
    calc.f2555 = np.zeros((dim,))
    calc.e02800 = np.zeros((dim,))
    calc.e02610 = np.zeros((dim,))
    calc.e02540 = np.zeros((dim,))
    calc.e02615 = np.zeros((dim,))
    calc.SSIND = np.zeros((dim,))
    calc.e18400 = np.zeros((dim,))
    calc.e18800 = np.zeros((dim,))
    calc.e18900 = np.zeros((dim,))
    calc.e20950 = np.zeros((dim,))
    calc.e19500 = np.zeros((dim,))
    calc.e19570 = np.zeros((dim,))
    calc.e19400 = np.zeros((dim,))
    calc.c20400 = np.zeros((dim,))
    calc.e20200 = np.zeros((dim,))
    calc.e20900 = np.zeros((dim,))
    calc.e21000 = np.zeros((dim,))
    calc.e21010 = np.zeros((dim,))
    calc.e02600 = np.zeros((dim,))
    calc._exact = np.zeros((dim,))
    calc.e11055 = np.zeros((dim,))
    calc.e00250 = np.zeros((dim,))
    calc.e30100 = np.zeros((dim,))
    
    calc.e15360 = np.zeros((dim,))
    calc.e04200 = np.zeros((dim,))
    calc.e04470 = calc.p04470
    calc.e37717 = np.zeros((dim,))
    calc.e04805 = np.zeros((dim,))
    calc.AGEP = np.zeros((dim,))
    calc.AGES = np.zeros((dim,))
    calc.PBI = np.zeros((dim,))
    calc.SBI = np.zeros((dim,))
    calc.t04470 = np.zeros((dim,))
    calc.e23250 = calc.p23250
    calc.e58980 = np.zeros((dim,))
    calc.c00650 = np.zeros((dim,))
    calc.c00100 = np.zeros((dim,))
    calc.c04470 = np.zeros((dim,))
    calc.c04600 = np.zeros((dim,))
    calc.c21060 = np.zeros((dim,))
    calc.c21040 = np.zeros((dim,))
    calc.c17000 = np.zeros((dim,))
    calc.c18300 = np.zeros((dim,))
    calc.c20800 = np.zeros((dim,))
    calc.c02900 = np.zeros((dim,))
    calc.c02700 = np.zeros((dim,))
    calc.c23650 = np.zeros((dim,))
    calc.c01000 = np.zeros((dim,))
    calc.c02500 = np.zeros((dim,))
    calc.e24583 = np.zeros((dim,))
    calc._fixup = np.zeros((dim,))
    calc._cmp = np.zeros((dim,))
    calc.e59440 = np.zeros((dim,))
    calc.e59470 = np.zeros((dim,))
    calc.e59400 = np.zeros((dim,))
    calc.e10105 = np.zeros((dim,))
    calc.e83200_0 = np.zeros((dim,))
    calc.e59410 = np.zeros((dim,))
    calc.e59420 = np.zeros((dim,))
    calc.e74400 = np.zeros((dim,))
    calc.x62720  = np.zeros((dim,))
    calc.x60260 = np.zeros((dim,))
    calc.x60240 = np.zeros((dim,))
    calc.x60220 = np.zeros((dim,))
    calc.x60130 = np.zeros((dim,))
    calc.x62730 = np.zeros((dim,))
    calc.e60290 = np.zeros((dim,))
    calc.DOBYR = np.zeros((dim,))
    calc.SDOBYR = np.zeros((dim,))
    calc.DOBMD = np.zeros((dim,))
    calc.SDOBMD = np.zeros((dim,))
    calc.e62600 = np.zeros((dim,))
    calc.x62740 = np.zeros((dim,))
    calc._fixeic = np.zeros((dim,))
    calc.e32880 = np.zeros((dim,))
    calc.e32890 = np.zeros((dim,))
    calc.CDOB1 = np.zeros((dim,))
    calc.CDOB2 = np.zeros((dim,))	
    calc.e32750 = np.zeros((dim,))
    calc.e32775 = np.zeros((dim,))
    calc.e33420 = np.zeros((dim,))
    calc.e33430 = np.zeros((dim,))
    calc.e33450 = np.zeros((dim,))
    calc.e33460 = np.zeros((dim,))
    calc.e33465 = np.zeros((dim,))
    calc.e33470 = np.zeros((dim,))
    calc.x59560 = np.zeros((dim,))
    calc.EICYB1 = np.zeros((dim,))
    calc.EICYB2 = np.zeros((dim,))
    calc.EICYB3 = np.zeros((dim,))
    calc.e83080 = np.zeros((dim,))
    calc.e25360 = np.zeros((dim,))
    calc.e25430 = np.zeros((dim,))
    calc.e25470 = calc.p25470
    calc.e25400 = np.zeros((dim,))
    calc.e25500 = np.zeros((dim,))
    calc.e26210 = np.zeros((dim,))
    calc.e26340 = np.zeros((dim,))
    calc.e26205 = np.zeros((dim,))
    calc.e26320 = np.zeros((dim,))
    calc.e87482 = np.zeros((dim,))
    calc.e87487 = np.zeros((dim,))
    calc.e87492 = np.zeros((dim,))
    calc.e87497 = np.zeros((dim,))
    calc.e87526 = np.zeros((dim,))
    calc.e87522 = np.zeros((dim,))
    calc.e87524 = np.zeros((dim,))
    calc.e87528 = np.zeros((dim,))
    calc.EDCRAGE = np.zeros((dim,))
    calc.e07960 = np.zeros((dim,))
    calc.e07700 = np.zeros((dim,))
    calc.e07250 = np.zeros((dim,))
    calc.t07950 = np.zeros((dim,))
    calc.e82882 = np.zeros((dim,))
    calc.e82880 = np.zeros((dim,))
    calc.e07500 = np.zeros((dim,))
    calc.e08000 = calc.p08000
    calc.e08001 = np.zeros((dim,))
    calc.e07970 = np.zeros((dim,))
    calc.e07980 = np.zeros((dim,))
    calc.e10000 = np.zeros((dim,))
    calc.e10100 = np.zeros((dim,))
    calc.e10050 = np.zeros((dim,))
    calc.e10075 = np.zeros((dim,))
    calc.e09805 = np.zeros((dim,))
    calc.e09710 = np.zeros((dim,))
    calc.e09720 = np.zeros((dim,))
    calc.e87900 = np.zeros((dim,))
    calc.e87905 = np.zeros((dim,))
    calc.e87681 = np.zeros((dim,))
    calc.e87682 = np.zeros((dim,))
    calc.e11451 = np.zeros((dim,))
    calc.e11452 = np.zeros((dim,))
    calc.e11601 = np.zeros((dim,))
    calc.e11602 = np.zeros((dim,))
    calc.e60300 = np.zeros((dim,))
    calc.e60860 = np.zeros((dim,))
    calc.e60100 = calc.p60100
    calc.e60840 = np.zeros((dim,))
    calc.e60630 = np.zeros((dim,))
    calc.e60550 = np.zeros((dim,))
    calc.e60720 = np.zeros((dim,))
    calc.e60430 = np.zeros((dim,))
    calc.e60500 = np.zeros((dim,))
    calc.e60340 = np.zeros((dim,))
    calc.e60680 = np.zeros((dim,))
    calc.e60600 = np.zeros((dim,))
    calc.e60405 = np.zeros((dim,))
    calc.e60440 = np.zeros((dim,))
    calc.e60420 = np.zeros((dim,))
    calc.e60410 = np.zeros((dim,))
    calc.e61400 = np.zeros((dim,))
    calc.e60660 = np.zeros((dim,))
    calc.e60480 = np.zeros((dim,))
    calc.e62000 = np.zeros((dim,))
    calc.e60250 = np.zeros((dim,))
    calc.e40223 = np.zeros((dim,))
    calc._sep = np.zeros((dim,))
    calc._earned = np.zeros((dim,))
    calc._sey = np.zeros((dim,))
    calc._setax = np.zeros((dim,))
    calc._feided = np.zeros((dim,))
    calc._ymod = np.zeros((dim,))
    calc._ymod1 = np.zeros((dim,))
    calc._posagi = np.zeros((dim,))
    calc._sit = np.zeros((dim,))
    calc.SOIYR = np.repeat(2008, dim)
    calc.xtxcr1xtxcr10 = np.zeros((dim,))

    """
    Previously defined in TaxGain()
    """
    calc._hasgain = np.zeros(dim)
    calc._dwks5 = np.zeros(dim)
    calc.c24505 = np.zeros(dim)
    calc.c24510 = np.zeros(dim)
    calc._dwks9 = np.zeros(dim)
    calc.c24516 = np.zeros(dim)
    calc._dwks12 = np.zeros(dim)
    calc.c24517 = np.zeros(dim)
    calc.c24520 = np.zeros(dim)
    calc.c24530 = np.zeros(dim)
    calc._dwks16 = np.zeros(dim)
    calc._dwks17 = np.zeros(dim)
    calc.c24540 = np.zeros(dim)
    calc.c24534 = np.zeros(dim)
    calc._dwks21 = np.zeros(dim)
    calc.c24597 = np.zeros(dim)
    calc.c24598 = np.zeros(dim)
    calc._dwks25 = np.zeros(dim)
    calc._dwks26 = np.zeros(dim)
    calc._dwks28 = np.zeros(dim)
    calc.c24610 = np.zeros(dim)
    calc.c24615 = np.zeros(dim)
    calc._dwks31 = np.zeros(dim)
    calc.c24550 = np.zeros(dim)
    calc.c24570 = np.zeros(dim)
    calc._addtax = np.zeros(dim)
    calc.c24560 = np.zeros(dim)
    calc._taxspecial = np.zeros(dim)
    calc.c24580 = np.zeros(dim)
    calc.c05100 = np.zeros(dim)
    calc.c59430 = np.zeros(dim)
    calc.c59450 = np.zeros(dim)
    calc.c59460 = np.zeros(dim)
    calc._line17 = np.zeros(dim)
    calc._line19 = np.zeros(dim)
    calc._line22 = np.zeros(dim)
    calc._line30 = np.zeros(dim)
    calc._line31 = np.zeros(dim)
    calc._line32 = np.zeros(dim)
    calc._line36 = np.zeros(dim)
    calc._line33 = np.zeros(dim)
    calc._line34 = np.zeros(dim)
    calc._line35 = np.zeros(dim)
    calc.c59485 = np.zeros(dim)
    calc.c59490 = np.zeros(dim)
    calc.c05700 = np.zeros(dim)
    calc._s1291 = np.zeros(dim)
    calc._parents = np.zeros(dim)
    calc.c05750 = np.zeros(dim)
    calc._taxbc = np.zeros(dim)
    
    """
    Previously defined in ItemDed()
    """
    calc.c17750 = np.zeros(dim)
    calc._sit1 = np.zeros(dim)
    calc._statax = np.zeros(dim)
    calc.c37703 = np.zeros(dim)
    calc.c20500 = np.zeros(dim)
    calc.c20750 = np.zeros(dim)
    calc.c20400 = np.zeros(dim)
    calc.c19200 = np.zeros(dim)
    calc.c19700 = np.zeros(dim)
    calc._nonlimited = np.zeros(dim)
    calc._phase2_i = np.zeros(dim)
    calc._limitratio = np.zeros(dim)

    """
    Previously defined in AMTI()
    """
    calc.c62720 = np.zeros(dim)
    calc.c60260 = np.zeros(dim)
    calc.c63100 = np.zeros(dim)
    calc.c60200 = np.zeros(dim)
    calc.c60240 = np.zeros(dim)
    calc.c60220 = np.zeros(dim)
    calc.c60130 = np.zeros(dim)
    calc.c62730 = np.zeros(dim)
    calc._addamt = np.zeros(dim)
    calc.c62100 = np.zeros(dim)
    calc._cmbtp = np.zeros(dim)
    calc._edical = np.zeros(dim)
    calc._amtsepadd = np.zeros(dim)
    calc.c62600 = np.zeros(dim)
    calc._agep = np.zeros(dim)
    calc._ages = np.zeros(dim)
    calc.c62700 = np.zeros(dim)
    calc._alminc = np.zeros(dim)
    calc._amtfei = np.zeros(dim)
    calc.c62780 = np.zeros(dim)
    calc.c62900 = np.zeros(dim)
    calc.c63000 = np.zeros(dim)
    calc.c62740 = np.zeros(dim)
    calc._ngamty = np.zeros(dim)
    calc.c62745 = np.zeros(dim)
    calc.y62745 = np.zeros(dim)
    calc._tamt2 = np.zeros(dim)
    calc._amt5pc = np.zeros(dim)
    calc._amt15pc = np.zeros(dim)
    calc._amt25pc = np.zeros(dim)
    calc.c62747 = np.zeros(dim)
    calc.c62755 = np.zeros(dim)
    calc.c62770 = np.zeros(dim)
    calc._amt = np.zeros(dim)
    calc.c62800 = np.zeros(dim)
    calc.c09600 = np.zeros(dim)
    calc._othtax = np.zeros(dim)
    calc.c05800 = np.zeros(dim)

    """ 
    Previously defined in f2441()
    """
    calc.c32880 = np.zeros(dim) 
    calc.c32890 = np.zeros(dim)
    calc._ncu13 = np.zeros(dim)
    calc._dclim = np.zeros(dim)
    calc.c32800 = np.zeros(dim)

    """
    Previously defined in DepCareBen()
    """

    calc._seywage = np.zeros(dim) 
    calc.c33465 = np.zeros(dim) 
    calc.c33470 = np.zeros(dim) 
    calc.c33475 = np.zeros(dim) 
    calc.c33480 = np.zeros(dim) 
    calc.c32840 = np.zeros(dim) 
    calc.c33000 = np.zeros(dim) 

    """
    Previously defined in ExpEarnedInc()
    """
    calc._tratio = np.zeros(dim)
    calc.c33200 = np.zeros(dim)
    calc.c33400 = np.zeros(dim)
    calc.c07180 = np.zeros(dim)

    """
    Previously defined in RateRed()
    """
    calc.c07970 = np.zeros(dim)
    calc.c59560 = np.zeros(dim)

    """
    Previously defined in NumDep()
    """
    calc._ieic = np.zeros(dim)
    calc._modagi = np.zeros(dim)
    calc.c59660 = np.zeros(dim)
    calc._val_ymax = np.zeros(dim)
    calc._preeitc = np.zeros(dim)
    calc._val_rtbase = np.zeros(dim)
    calc._val_rtless = np.zeros(dim)
    calc._dy = np.zeros(dim)
    calc.EICYB1_1 = np.zeros(dim)
    calc.EICYB2_2 = np.zeros(dim) 
    calc.EICYB3_3 = np.zeros(dim) 

    """
    Previously defined in ChildTaxCredit()
    """
    calc.c11070 = np.zeros(dim) 
    calc.c07220 = np.zeros(dim) 
    calc.c07230 = np.zeros(dim) 
    calc._num = np.zeros(dim) 
    calc._nctcr = np.zeros(dim) 
    calc._precrd = np.zeros(dim) 
    calc._ctcagi = np.zeros(dim) 

    """
    Previously defined in AmOppCr()
    """
    calc.c87482 = np.zeros(dim) 
    calc.c87487 = np.zeros(dim) 
    calc.c87492 = np.zeros(dim) 
    calc.c87497 = np.zeros(dim) 
    calc.c87483 = np.zeros(dim) 
    calc.c87488 = np.zeros(dim) 
    calc.c87493 = np.zeros(dim) 
    calc.c87498 = np.zeros(dim) 
    calc.c87521 = np.zeros(dim) 

    """
    Previously defined in LLC()
    """
    calc.c87540 = np.zeros(dim) 
    calc.c87550 = np.zeros(dim) 
    calc.c87530 = np.zeros(dim) 

    """
    Previously defined in RefAmOpp()
    """
    calc.c87654 = np.zeros(dim) 
    calc.c87656 = np.zeros(dim) 
    calc.c87658 = np.zeros(dim) 
    calc.c87660 = np.zeros(dim) 
    calc.c87662 = np.zeros(dim) 
    calc.c87664 = np.zeros(dim) 
    calc.c87666 = np.zeros(dim) 
    calc.c10960 = np.zeros(dim) 
    calc.c87668 = np.zeros(dim) 
    calc.c87681 = np.zeros(dim) 

    """
    Previously defined in NonEdCr()
    """

    calc.c87560 = np.zeros(dim) 
    calc.c87570 = np.zeros(dim) 
    calc.c87580 = np.zeros(dim) 
    calc.c87590 = np.zeros(dim) 
    calc.c87600 = np.zeros(dim) 
    calc.c87610 = np.zeros(dim) 
    calc.c87620 = np.zeros(dim) 
    calc._ctc1 = np.zeros(dim) 
    calc._ctc2 = np.zeros(dim) 
    calc._regcrd = np.zeros(dim) 
    calc._exocrd = np.zeros(dim) 
    calc._ctctax = np.zeros(dim) 
    calc.c07220 = np.zeros(dim) 

    """
    Previously defined in AddCTC()
    """
    calc.c82940 = np.zeros(dim) 
    calc.c82925 = np.zeros(dim) 
    calc.c82930 = np.zeros(dim) 
    calc.c82935 = np.zeros(dim) 
    calc.c82880 = np.zeros(dim) 
    calc.h82880 = np.zeros(dim) 
    calc.c82885 = np.zeros(dim) 
    calc.c82890 = np.zeros(dim) 
    calc.c82900 = np.zeros(dim) 
    calc.c82905 = np.zeros(dim) 
    calc.c82910 = np.zeros(dim) 
    calc.c82915 = np.zeros(dim) 
    calc.c82920 = np.zeros(dim) 
    calc.c82937 = np.zeros(dim) 
    calc.c82940 = np.zeros(dim) 
    calc.c11070 = np.zeros(dim) 
    calc.e59660 = np.zeros(dim) 
    calc._othadd = np.zeros(dim) 

    """
    Previously defined in C1040()
    """
    calc.c07100 = np.zeros(dim) 
    calc.y07100 = np.zeros(dim) 
    calc.x07100 = np.zeros(dim) 
    calc.c08795 = np.zeros(dim) 
    calc.c08800 = np.zeros(dim) 
    calc.e08795 = np.zeros(dim) 
    calc.c09200 = np.zeros(dim) 
    calc.x07400 = np.zeros(dim) 
    calc._eitc = np.zeros(dim)

    """
    Previously defined in DEITC()
    """
    calc.c59680 = np.zeros(dim) 
    calc.c59700 = np.zeros(dim) 
    calc.c59720 = np.zeros(dim) 
    calc._comb = np.zeros(dim) 
    calc.c07150 = np.zeros(dim) 
    calc.c10950 = np.zeros(dim) 

    """
    Previously defined in SOIT()
    """
    calc.c10300 = np.zeros(dim)












