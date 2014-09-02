import pandas as pd
import math
import numpy as np

output_filename = 'translationoutput.csv'

from puf_2_picle import unpicle
puf_dict = unpicle('test/y2.pickle')

# This should be dealt with so that we don't keep referencing the same array
# simply find all uses of this and figure out if they're called for (mostly not)
DIMARRAY = np.zeros((139651,))


AGIR1 = puf_dict['agir1']
MIdR = puf_dict['MIDR']


# import our special function for reading planX and planY (see json_io for details)
import json_io

planX = json_io.read_plans('test/planX.json')


def Puf(master_puf, dim_key='PUF DIM'):
    # dim = len(master_puf)
    with open('test/zeros.json') as defaults_file:
        default_var_names = json_io.load(defaults_file)
    dim = master_puf[dim_key]
    default_var_dict = dict((var, np.zeros((dim,))) 
        for var in default_var_names)
    # return dict(master_puf, **default_var_dict)
    master_puf.update(default_var_dict)
    


def FilingStatus():
    #Filing based on marital status
    global _sep
    global _txp
    _sep = np.where(np.logical_or(puf_dict['MARS'] == 3, puf_dict['MARS'] == 6), 2, 1)
    _txp = np.where(np.logical_or(puf_dict['MARS'] == 2, puf_dict['MARS'] == 5), 2, 1)


def Adj(): 
    #Adjustments
    global _feided 
    global c02900
    _feided = np.maximum(puf_dict['e35300_0'], puf_dict['e35600_0'], + puf_dict['e35910_0']) #Form 2555
    c02900 = (puf_dict['e03210'] + puf_dict['e03260'] + puf_dict['e03270'] + puf_dict['e03300'] + puf_dict['e03400'] + puf_dict['e03500'] + puf_dict['e03220'] 
    + puf_dict['e03230'] + puf_dict['e03240'] + puf_dict['e03290'] + puf_dict['x03150'] + puf_dict['e03600'] + puf_dict['e03280'] + puf_dict['e03900'] + puf_dict['e04000'] 
    + puf_dict['e03700']) 
    x02900 = c02900


def CapGains():
    #Capital Gains
    global _ymod
    global _ymod1
    global c02700
    global c23650
    global c01000
    c23650 = puf_dict['c23250'] + puf_dict['e22250'] + puf_dict['e23660'] 
    c01000 = np.maximum(-3000/_sep, c23650)
    c02700 = np.minimum(_feided, planX['feimax'][2013-puf_dict['FLPDYR']] * puf_dict['f2555']) 
    _ymod1 = (puf_dict['e00200'] + puf_dict['e00300'] + puf_dict['e00600'] + puf_dict['e00700'] + puf_dict['e00800'] + puf_dict['e00900'] + c01000 
        + puf_dict['e01100'] + puf_dict['e01200'] + puf_dict['e01400'] + puf_dict['e01700'] + puf_dict['e02000'] + puf_dict['e02100'] + puf_dict['e02300'] + puf_dict['e02600'] 
        + puf_dict['e02610'] + puf_dict['e02800'] - puf_dict['e02540'])
    _ymod2 = puf_dict['e00400'] + puf_dict['e02400']/2 - c02900
    _ymod3 = puf_dict['e03210'] + puf_dict['e03230'] + puf_dict['e03240'] + puf_dict['e02615']
    _ymod = _ymod1 + _ymod2 + _ymod3


def SSBenefits():
    #Social Security Benefit Taxation
    global c02500   
    c02500 = np.where(np.logical_or(puf_dict['SSIND'] != 0, 
        np.logical_and(puf_dict['MARS'] >= 3, puf_dict['MARS'] <= 6)), puf_dict['e02500'], 
        np.where(_ymod < planX['ssb50'][puf_dict['MARS']-1], 0, 
            np.where(np.logical_and(_ymod >= planX['ssb50'][puf_dict['MARS']-1], 
                _ymod < planX['ssb85'][puf_dict['MARS']-1]), 
                0.5 * np.minimum(_ymod - planX['ssb50'][puf_dict['MARS']-1], puf_dict['e02400']), 
                np.minimum(0.85 * (_ymod - planX['ssb85'][puf_dict['MARS']-1]) + 0.50 * 
                    np.minimum(puf_dict['e02400'], planX['ssb85'][puf_dict['MARS']-1] - planX['ssb50'][puf_dict['MARS']-1]), 
                    0.85 * puf_dict['e02400'])))) 


def AGI():
    #Adjusted Gross Income  
    global _posagi
    global c00100
    global c04600
    c02650 = _ymod1 + c02500 - c02700 + puf_dict['e02615'] #Gross Income

    c00100 = c02650 - c02900
    _agierr = puf_dict['e00100'] - c00100  #Adjusted Gross Income
    c00100 = np.where(puf_dict['fixup'] >= 1, c00100 + _agierr, c00100)

    _posagi = np.maximum(c00100, 0)
    _ywossbe = puf_dict['e00100'] - puf_dict['e02500']
    _ywossbc = c00100 - c02500

    _prexmp = puf_dict['XTOT'] * planX['amex'][puf_dict['FLPDYR'] - 2013] 
    #Personal Exemptions (_phaseout smoothed)

    c04600 = _prexmp 


def ItemDed(puf): 
    #Itemized Deductions
    global c04470
    global c21060
    global c21040
    global c17000
    global c18300
    global c20800
    global _sit

    # Medical #
    c17750 = 0.075 * _posagi 
    c17000 = np.maximum(0, puf_dict['e17500'] - c17750)

    # State and Local Income Tax, or Sales Tax #
    _sit1 = np.maximum(puf_dict['e18400'], puf_dict['e18425'])
    _sit = np.maximum(_sit1, 0)
    _statax = np.maximum(_sit, puf_dict['e18450'])

    # Other Taxes #
    c18300 = _statax + puf_dict['e18500'] + puf_dict['e18800'] + puf_dict['e18900']

    # Casulty #
    c37703 = np.where(puf_dict['e20500'] > 0, puf_dict['e20500'] + 0.10 * _posagi, 0)
    c20500 = np.where(puf_dict['e20500'] > 0, c37703 - 0.10 * _posagi, 0)

    # Miscellaneous #
    c20750 = 0.02 * _posagi 
    if puf == True: 
        puf_dict['c20400'] = puf_dict['e20400']
        c19200 = puf_dict['e19200'] 
    else: 
        c02400 = puf_dict['e20550'] + puf_dict['e20600'] + puf_dict['e20950']
        c19200 = puf_dict['e19500'] + puf_dict['e19570'] + puf_dict['e19400'] + puf_dict['e19550']
    c20800 = np.maximum(0, puf_dict['c20400'] - c20750)

    # Charity (assumes carryover is non-cash) #
    _lim50 = np.minimum(0.50 * _posagi, puf_dict['e19800'])
    _lim30 = np.minimum(0.30 * _posagi, puf_dict['e20100'] + puf_dict['e20200'])
    c19700 = np.where(puf_dict['e19800'] + puf_dict['e20100'] + puf_dict['e20200'] <= 0.20 * _posagi, 
        puf_dict['e19800'] + puf_dict['e20100'] + puf_dict['e20200'], _lim30 + _lim50)
    #temporary fix!??

    # Gross Itemized Deductions #
    c21060 = (puf_dict['e20900'] + c17000 + c18300 + c19200 + c19700 
        + c20500 + c20800 + puf_dict['e21000'] + puf_dict['e21010'])
    
    # Itemized Deduction Limitation
    _phase2 = np.where(puf_dict['MARS'] == 1, 200000, np.where(puf_dict['MARS'] == 4, 250000, 300000))

    _itemlimit = 1
    _c21060 = c21060
    _nonlimited = c17000 + c20500 + puf_dict['e19570'] + puf_dict['e21010'] + puf_dict['e20900']
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
    global _sey
    global _setax
    # Earned Income and FICA #    
    global _earned
    _sey = puf_dict['e00900'] + puf_dict['e02100']
    _fica = np.maximum(0, .153 * np.minimum(planX['ssmax'][puf_dict['FLPDYR'] - 2013], 
        puf_dict['e00200'] + np.maximum(0, _sey) * 0.9235))
    _setax = np.maximum(0, _fica - 0.153 * puf_dict['e00200'])
    _seyoff = np.where(_setax <= 14204, 0.5751 * _setax, 0.5 * _setax + 10067)

    c11055 = puf_dict['e11055']

    _earned = np.maximum(0, puf_dict['e00200'] + puf_dict['e00250'] + puf_dict['e11055'] + puf_dict['e30100'] + _sey - _seyoff)


def StdDed():
    # Standard Deduction with Aged, Sched L and Real Estate # 
    global c04800
    global c60000
    global _taxinc
    global _feitax
    global _standard

    c15100 = np.where(puf_dict['DSI'] == 1, 
        np.maximum(300 + _earned, planX['stded'][puf_dict['FLPDYR']-2013, 6]), 0)

    c04100 = np.where(puf_dict['DSI'] == 1, np.minimum(planX['stded'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], c15100), 
        np.where(np.logical_or(puf_dict['compitem'] == 1, 
            np.logical_and(np.logical_and(3<= puf_dict['MARS'], puf_dict['MARS'] <=6), MIdR == 1)), 
        0, planX['stded'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1]))


    c04100 = c04100 + puf_dict['e15360']
    _numextra = puf_dict['AGEP'] + puf_dict['AGES'] + puf_dict['PBI'] + puf_dict['SBI'] 

    _txpyers = np.where(np.logical_or(np.logical_or(puf_dict['MARS'] == 2, puf_dict['MARS'] == 3), 
        puf_dict['MARS'] == 3), 2, 1)
    c04200 = np.where(np.logical_and(puf_dict['exact'] == 1, 
        np.logical_or(puf_dict['MARS'] == 3, puf_dict['MARS'] == 5)), 
        puf_dict['e04200'], _numextra * planX['aged'][_txpyers -1, puf_dict['FLPDYR'] - 2013])

    c15200 = c04200

    _standard = np.where(np.logical_and(np.logical_or(puf_dict['MARS'] == 3, puf_dict['MARS'] == 6), 
        c04470 > 0), 
        0, c04100 + c04200)

    _othded = np.where(puf_dict['FDED'] == 1, puf_dict['e04470'] - c04470, 0)
    #c04470 = np.where(np.logical_and(puf_dict['fixup'] >= 2, puf_dict['FDED'] == 1), c04470 + _othded, c04470)
    c04100 = np.where(puf_dict['FDED'] == 1, 0, c04100)
    c04200 = np.where(puf_dict['FDED'] == 1, 0, c04200)
    _standard = np.where(puf_dict['FDED'] == 1, 0, _standard)


    c04500 = c00100 - np.maximum(c21060 - c21040, 
        np.maximum(c04100, _standard + puf_dict['e37717']))
    c04800 = np.maximum(0, c04500 - c04600 - puf_dict['e04805'])

    c60000 = np.where(_standard > 0, c00100, c04500)
    c60000 = c60000 - puf_dict['e04805']

    #Some taxpayers iteimize only for AMT, not regular tax
    # IK: why do we need _amtstd and not just compare with zero?
    _amtstd = DIMARRAY
    c60000 = np.where(np.logical_and(np.logical_and(puf_dict['e04470'] == 0, 
        puf_dict['t04470'] > _amtstd), 
        np.logical_and(puf_dict['f6251'] == 1, puf_dict['exact'] == 1)), c00100 - puf_dict['t04470'], c60000)

    _taxinc = np.where(np.logical_and(c04800 > 0, _feided > 0), 
        c04800 + c02700, c04800)
    
    _feitax = Taxer(inc_in= _feided, inc_out =[], mars= puf_dict['MARS'])
    _oldfei = Taxer(inc_in = c04800, inc_out =[], mars= puf_dict['MARS'])

    _feitax = np.where(np.logical_or(c04800 < 0, _feided < 0), 0, _feitax)

def XYZD():
    global c24580
    global _xyztax
    _xyztax = Taxer(inc_in = _taxinc, inc_out =[], mars= puf_dict['MARS'])
    c05200 = Taxer(inc_in = c04800, inc_out =[], mars= puf_dict['MARS'])
    

def NonGain():
    _cglong = np.minimum(c23650, puf_dict['e23250'] + puf_dict['e01100'])

def TaxGains():
    global c05750
    global c24517
    global _taxbc
    global c24516
    global c24520
    global c05700
    # IK: unused vars!
    # c24553 = DIMARRAY
    # c24581 = DIMARRAY
    # c24542 = DIMARRAY

    _hasgain = np.where(np.logical_or(puf_dict['e01000'] > 0, c23650 > 0), 1, 0)
    _hasgain = np.where(np.logical_or(puf_dict['e23250'] > 0, puf_dict['e01100'] > 0), 1, _hasgain)
    _hasgain = np.where(puf_dict['e00650'] > 0, 1, _hasgain)

    #significance of sum() function here in original SAS code?  
    _dwks5 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, puf_dict['e58990'] - puf_dict['e58980']), 0)
    c24505 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, puf_dict['c00650'] - _dwks5), 0)
    c24510 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, np.minimum(c23650, puf_dict['e23250'])) + puf_dict['e01100'], 0)
    #gain for tax computation

    c24510 = np.where(np.logical_and(_taxinc > 0, np.logical_and(_hasgain == 1, puf_dict['e01100'] > 0)), puf_dict['e01100'], c24510)
    #from app f 2008 drf

    _dwks9 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, c24510 - np.minimum(puf_dict['e58990'], puf_dict['e58980'])), 0)
    #puf_dict['e24516'] gain less invest y 

    c24516 = np.maximum(0, np.minimum(puf_dict['e23250'], c23650)) + puf_dict['e01100']
    c24580 = _xyztax

    c24516 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24505 + _dwks9, c24516)
    _dwks12 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_dwks9, puf_dict['e24515'] + puf_dict['e24518']), 0)
    c24517 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24516 -_dwks12, 0)
    #gain less 25% and 28%

    c24520 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc -c24517), 0)
    #tentative TI less schD gain

    c24530 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(planX['brk2'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], _taxinc), 0)
    #minimum TI for bracket

    _dwks16 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(c24520, c24530), 0)
    _dwks17 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - c24516), 0)
    c24540 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(_dwks16, _dwks17), 0)

    c24534 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24530 - _dwks16, 0)
    _dwks21 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_taxinc, c24517), 0)
    c24597 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks21 - c24534), 0)
    #income subject to 15% tax

    c24598 = 0.15 * c24597 #actual 15% tax

    _dwks25 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.minimum(_dwks9, puf_dict['e24515']), 0)
    _dwks26 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24516 + c24540, 0)
    _dwks28 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _taxinc), 0)
    c24610 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _dwks25 - _dwks28), 0)
    c24615 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), 0.25 * c24610, 0)
    _dwks31 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24540 + c24534 + c24597 + c24610, 0)
    c24550 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), np.maximum(0, _taxinc - _dwks31), 0)
    c24570 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), 0.28 * c24550, 0)
    _addtax = np.where(np.logical_and(_taxinc > 0, np.logical_and(_hasgain == 1, c24540 > planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1])), 0.05 * c24517, 0.0)
    _addtax = np.where(np.logical_and(np.logical_and(_taxinc > 0, _hasgain == 1), np.logical_and(c24540 <= planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], _taxinc > planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1])), 0.05 * np.minimum(c04800 - planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], c24517), _addtax)

    c24560 = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), Taxer(inc_in = c24540, inc_out =[], mars= puf_dict['MARS']), 0)

    _taxspecial = np.where(np.logical_and(_taxinc > 0, _hasgain == 1), c24598 + c24615 + c24570 + c24560 + _addtax, 0)

    c05100 = c24580
    c05100 = np.where(np.logical_and(c04800 > 0, _feided > 0), np.maximum(0, c05100 - _feitax), c05100)

    #Form 4972 - Lump Sum Distributions

    c59430 = np.where(puf_dict['cmp'] == 1, np.maximum(0, puf_dict['e59410'] - puf_dict['e59420']), 0)
    c59450 = np.where(puf_dict['cmp'] == 1, c59430 + puf_dict['e59440'], 0) #income plus lump sum
    c59460 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(0.5 * c59450, 10000)) - 0.2 * np.maximum(0, c59450 - 20000), 0)
    _line17 = np.where(puf_dict['cmp'] == 1, c59450 - c59460, 0)
    _line19 = np.where(puf_dict['cmp'] == 1, c59450 - c59460 - puf_dict['e59470'], 0)
    _line22 = np.where(np.logical_and(puf_dict['cmp'] == 1, c59450 > 0), np.maximum(0, puf_dict['e59440'] - puf_dict['e59440'] * c59460/c59450),0)

    _line30 = np.where(puf_dict['cmp'] == 1, 0.1 * np.maximum(0, c59450 - c59460 - puf_dict['e59470']), 0)

    _line31 = np.where(puf_dict['cmp'] == 1, 
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

    _line32 = np.where(puf_dict['cmp'] == 1, 10 * _line31, 0)
    _line36 = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['e59440'] == 0), _line32, 0)
    _line33 = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['e59440'] > 0), 0.1 * _line22, 0)
    _line34 = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['e59440'] > 0),
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
    _line35 = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['e59440'] > 0), 10 * _line34, 0)
    _line36 = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['e59440'] > 0), np.maximum(0, _line32 - _line35), 0)
    #tax saving from 10 yr option
    c59485 = np.where(puf_dict['cmp'] == 1, _line36, 0)
    c59490 = np.where(puf_dict['cmp'] == 1, c59485 + 0.2 * np.maximum(0, puf_dict['e59400']), 0)
    #pension gains tax plus

    c05700 = np.where(puf_dict['cmp'] == 1, c59490, 0)

    _s1291 = puf_dict['e10105']
    _parents = puf_dict['e83200_0']
    c05750 = np.maximum(c05100 + _parents + c05700, puf_dict['e74400'])
    _taxbc = c05750 
    x05750 = c05750 

    return c05750

 
def MUI(c05750):
    #Additional Medicare tax on unearned Income 
    c05750 = c05750
    c00100[5] = 100000000
    c05750[6] = 1234
    c05750 = np.where(c00100 > planX['thresx'][puf_dict['MARS']-1], 0.038 * np.minimum(puf_dict['e00300'] + puf_dict['e00600'] + np.maximum(0, c01000) + np.maximum(0, puf_dict['e02000']), c00100 - planX['thresx'][puf_dict['MARS']-1]), c05750)
    
    

def AMTI(puf):
    global c05800
    global _othtax
    global _agep
    global _ages
    c62720 = c24517 + puf_dict['x62720'] 
    c60260 = puf_dict['e00700'] + puf_dict['x60260']
    c63100 = np.maximum(0, _taxbc - puf_dict['e07300'])
    c60200 = np.minimum(c17000, 0.025 * _posagi)
    c60240 = c18300 + puf_dict['x60240']
    c60220 = c20800 + puf_dict['x60220']
    c60130 = c21040 + puf_dict['x60130'] 
    c62730 = puf_dict['e24515'] + puf_dict['x62730']

    _addamt = np.where(np.logical_or(puf_dict['exact'] == 0, np.logical_and(puf_dict['exact'] == 1, c60200 + c60220 + c60240 + puf_dict['e60290'] > 0)), c60200 + c60240 + c60220 + puf_dict['e60290'] - c60130, 0)


    c62100 = np.where(puf_dict['cmp'] == 1, _addamt + puf_dict['e60300'] + puf_dict['e60860'] + puf_dict['e60100'] + puf_dict['e60840'] + puf_dict['e60630'] + puf_dict['e60550'] + puf_dict['e60720'] + puf_dict['e60430'] + puf_dict['e60500'] + puf_dict['e60340'] + puf_dict['e60680'] + puf_dict['e60600'] + puf_dict['e60405'] + puf_dict['e60440'] + puf_dict['e60420'] + puf_dict['e60410'] + puf_dict['e61400'] + puf_dict['e60660'] - c60260 - puf_dict['e60480'] - puf_dict['e62000'] + c60000, 0)


    c62100 = np.where(puf_dict['cmp'] == 1, c62100 - puf_dict['e60250'], c62100)

    _edical = np.where(np.logical_and(puf == True, np.logical_or(_standard == 0, np.logical_and(puf_dict['exact'] == 1, puf_dict['e04470'] > 0))), np.maximum(0, puf_dict['e17500'] - np.maximum(0, puf_dict['e00100']) * 0.075), 0)

    _cmbtp = np.where(np.logical_and(puf == True, np.logical_and(np.logical_or(_standard == 0, np.logical_and(puf_dict['exact'] == 1, puf_dict['e04470'] > 0)), puf_dict['f6251'] == 1)), -1 * np.minimum(_edical, 0.025 * np.maximum(0, puf_dict['e00100'])) + puf_dict['e62100'] + c60260 + puf_dict['e04470'] + puf_dict['e21040'] - _sit - puf_dict['e00100'] - puf_dict['e18500'] - puf_dict['e20800'], 0)

    c62100 = np.where(np.logical_and(puf == True, np.logical_or(_standard == 0, np.logical_and(puf_dict['exact'] == 1, puf_dict['e04470'] > 0))), c00100 - c04470 + np.minimum(c17000, 0.025 * np.maximum(0, c00100)) + _sit + puf_dict['e18500'] - c60260 + c20800 - c21040 + _cmbtp, c62100)

    _cmbtp = np.where(np.logical_and(puf == True, np.logical_and(_standard > 0, puf_dict['f6251'] == 1)), puf_dict['e62100'] - puf_dict['e00100'] + c60260, _cmbtp)
    c62100 = np.where(np.logical_and(puf == True, np.logical_and(_standard > 0, puf_dict['f6251'] == 1)), c00100 - c60260 + _cmbtp, c62100)

    x62100 = c62100

    _amtsepadd = np.where(np.logical_and(c62100 > planX['amtsep'][puf_dict['FLPDYR']-2013], np.logical_or(puf_dict['MARS'] == 3, puf_dict['MARS'] == 6)), np.maximum(0, np.minimum(planX['almsep'][puf_dict['FLPDYR']-2013], 0.25 * (c62100 - planX['amtsep'][puf_dict['FLPDYR']-2013]))), 0)
    c62100 = np.where(np.logical_and(c62100 > planX['amtsep'][puf_dict['FLPDYR']-2013], np.logical_or(puf_dict['MARS'] == 3, puf_dict['MARS'] == 6)), c62100 + _amtsepadd, c62100)

    c62600 = np.maximum(0, planX['amtex'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1] - 0.25 * np.maximum(0, c62100 - planX['amtys'][puf_dict['MARS']-1]))

    _agep = np.where(puf_dict['DOBYR'] > 0, np.ceil((12 * (puf_dict['FLPDYR'] - puf_dict['DOBYR']) - puf_dict['DOBMD']/100)/12), 0)
    _ages = np.where(puf_dict['SDOBYR'] > 0, np.ceil((12 * (puf_dict['FLPDYR'] - puf_dict['SDOBYR']) - puf_dict['SDOBMD']/100)/12), 0)

    c62600 = np.where(np.logical_and(puf_dict['cmp'] == 1, np.logical_and(puf_dict['f6251'] == 1, puf_dict['exact'] == 1)), puf_dict['e62600'], c62600)

    #puf_dict['cmp'] == 1 and puf_dict['exact'] == 0 and (_agep < amtage and agep =/= 0)

    c62600 = np.where(np.logical_and(np.logical_and(puf_dict['cmp'] == 1, puf_dict['exact'] == 0), np.logical_and(_agep < planX['amtage'][puf_dict['FLPDYR']-2013], _agep != 0)), np.minimum(c62600, _earned + planX['almdep'][puf_dict['FLPDYR']-2013]), c62600)

    c62700 = np.maximum(0, c62100 - c62600)

    _alminc = c62700

    _alminc = np.where(c02700 > 0, np.maximum(0, c62100 - c62600 + c02700), _alminc)
    # CHECK IF WE WANT TO SET THIS TO ZERO
    _amtfei = np.where(c02700 > 0, 0.26 * c02700 + 0.02 * np.maximum(0, c02700 - planX['almsp'][puf_dict['FLPDYR']-2013]/_sep), 0)

    c62780 = 0.26 * _alminc + 0.02 * np.maximum(0, _alminc - planX['almsp'][puf_dict['FLPDYR']-2013]/_sep) - _amtfei

    c62900 = np.where(puf_dict['f6251'] != 0, puf_dict['e62900'], puf_dict['e07300']) 
    c63000 = c62780 - c62900

    c62740 = np.minimum(np.maximum(0, c24516 + puf_dict['x62740']), c62720 + c62730)
    c62740 = np.where(c24516 == 0, c62720 + c62730, c62740)

    _ngamty = np.maximum(0, _alminc - c62740)

    c62745 = 0.26 * _ngamty + 0.02 * np.maximum(0, _ngamty - planX['almsp'][puf_dict['FLPDYR']-2013]/_sep)
    y62745 = planX['almsp'][puf_dict['FLPDYR']-2013]/_sep

    _amt5pc = DIMARRAY
    _amt15pc = np.minimum(_alminc, c62720) - _amt5pc - np.minimum(np.maximum(0, planX['brk2'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1] - c24520), np.minimum(_alminc, c62720))
    _amt15pc = np.where(c04800 == 0, np.maximum(0, np.minimum(_alminc, c62720) - planX['brk2'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1]), _amt15pc)
    _amt25pc = np.minimum(_alminc, c62740) - np.minimum(_alminc, c62720)

    _amt25pc = np.where(c62730 == 0, 0, _amt25pc)
    c62747 = planX['cgrate1'][puf_dict['FLPDYR']-2013] * _amt5pc
    c62755 = planX['cgrate2'][puf_dict['FLPDYR']-2013] * _amt15pc
    c62770 = 0.25 * _amt25pc
    _tamt2 = c62747 + c62755 + c62770

    # AMT referenced in np.where before its assigned, setting to zero
    # check this though
    _amt = np.where(_ngamty > planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], 0.05 * np.minimum(_alminc, c62740), 0)
    _amt = np.where(np.logical_and(_ngamty <= planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], _alminc > planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1]), 0.05 * np.minimum(_alminc - planX['brk6'][puf_dict['FLPDYR']-2013, puf_dict['MARS']-1], c62740), _amt)

    c62800 = np.minimum(c62780, c62745 + _tamt2 - _amtfei)
    c63000 = c62800 - c62900 
    c63100 = _taxbc - puf_dict['e07300'] - c05700 
    c63100 = c63100 + puf_dict['e10105']

    c63100 = np.maximum(0, c63100)
    c63200 = np.maximum(0, c63000 - c63100)
    c09600 = c63200
    _othtax = puf_dict['e05800'] - (puf_dict['e05100'] + puf_dict['e09600'])

    c05800 = _taxbc + c63200

def F2441(puf, _earned):
    global c32880
    global c32890
    global _dclim
    _earned = _earned
    _earned = np.where(puf_dict['fixeic'] == 1, puf_dict['e59560'], _earned)
    c32880 = np.where(np.logical_and(puf_dict['MARS'] == 2, puf == True), 0.5 * _earned, 0)
    c32890 = np.where(np.logical_and(puf_dict['MARS'] == 2, puf == True), 0.5 * _earned, 0)
    c32880 = np.where(np.logical_and(puf_dict['MARS'] == 2, puf == False), np.maximum(0, puf_dict['e32880']), c32880)
    c32890 = np.where(np.logical_and(puf_dict['MARS'] == 2, puf == False), np.maximum(0, puf_dict['e32890']), c32890)
    c32880 = np.where(puf_dict['MARS'] != 2, _earned, c32880)
    c32890 = np.where(puf_dict['MARS'] != 2, _earned, c32890)   

    # check if setting nu13 to zero by default is best
    _ncu13 = np.where(puf == True, puf_dict['f2441'], 0)
    _ncu13 = np.where(np.logical_and(puf == False, puf_dict['CDOB1'] > 0), _ncu13 + 1, _ncu13)
    _ncu13 = np.where(np.logical_and(puf == False, puf_dict['CDOB2'] > 0), _ncu13 + 1, _ncu13)

    _dclim = np.minimum(_ncu13, 2) * planX['dcmax'][puf_dict['FLPDYR']-2013]
    c32800 = np.minimum(np.maximum(puf_dict['e32800'], puf_dict['e32750'] + puf_dict['e32775']), _dclim)

def DepCareBen():
    global c33000
    #Part III ofdependent care benefits
    _seywage = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['MARS'] == 2), np.minimum(c32880, np.minimum(c32890, np.minimum(puf_dict['e33420'] + puf_dict['e33430'] - puf_dict['e33450'], puf_dict['e33460']))), 0)
    _seywage = np.where(np.logical_and(puf_dict['cmp'] == 1, puf_dict['MARS'] != 2), np.minimum(c32880, np.minimum(puf_dict['e33420'] + puf_dict['e33430'] - puf_dict['e33450'], puf_dict['e33460'])), _seywage)

    c33465 = np.where(puf_dict['cmp'] == 1, puf_dict['e33465'], 0)
    c33470 = np.where(puf_dict['cmp'] == 1, puf_dict['e33470'], 0)
    c33475 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(_seywage, 5000/_sep) - c33470), 0)
    c33480 = np.where(puf_dict['cmp'] == 1, np.maximum(0, puf_dict['e33420'] + puf_dict['e33430'] - puf_dict['e33450'] - c33465 - c33475), 0)
    c32840 = np.where(puf_dict['cmp'] == 1, c33470 + c33475, 0)
    c32800 = np.where(puf_dict['cmp'] == 1, np.minimum(np.maximum(0, _dclim - c32840), np.maximum(0, puf_dict['e32750'] + puf_dict['e32775'] - c32840)), 0)

    c33000 = np.where(puf_dict['MARS'] == 2, np.maximum(0, np.minimum(c32800, np.minimum(c32880, c32890))), 0)
    c33000 = np.where(puf_dict['MARS'] != 2, np.maximum(0, np.minimum(c32800, _earned)), c33000)


def ExpEarnedInc():
    global c07180
    #Expenses limited to earned income

    _tratio  = np.where(puf_dict['exact'] == 1, np.ceil(np.maximum((c00100 - planX['agcmax'][puf_dict['FLPDYR']-2013])/2000, 0)), 0)
    c33200 = np.where(puf_dict['exact'] == 1, c33000 * 0.01 * np.maximum(20, planX['pcmax'][puf_dict['FLPDYR']-2013] - np.minimum(15, _tratio)), 0)
    c33200 = np.where(puf_dict['exact'] != 1, c33000 * 0.01 * np.maximum(20, planX['pcmax'][puf_dict['FLPDYR']-2013] - np.maximum((c00100 - planX['agcmax'][puf_dict['FLPDYR']-2013])/2000, 0)), c33200)

    c33400 = np.minimum(np.maximum(0, c05800 - puf_dict['e07300']), c33200)
    #amount of the credit

    c07180 = np.where(puf_dict['e07180'] == 0, 0, c33400)


def RateRed(c05800):
    global c59560
    global c07970
    #rate reduction credit for 2001 only, is this needed?
    c05800 = c05800 
    c07970 = DIMARRAY
    # what is the purpose of below line?
    x07970 = c07970

    c05800 = np.where(puf_dict['fixup'] >= 3, c05800 + _othtax, c05800)

    c59560 = np.where(puf_dict['exact'] == 1, puf_dict['x59560'], _earned)


def NumDep(puf):
    global c59660
    #Number of dependents for puf_dict['EIC'] 

    EICYB1_1 = np.where(puf_dict['EICYB1'] < 0, 0.0, puf_dict['EICYB1'])
    EICYB2_2 = np.where(puf_dict['EICYB2'] < 0, 0.0, puf_dict['EICYB2'])
    EICYB3_3 = np.where(puf_dict['EICYB3'] < 0, 0.0, puf_dict['EICYB3'])

    _ieic = np.where(puf == True, puf_dict['EIC'], EICYB1_1 + EICYB2_2 + EICYB3_3)

    _ieic = _ieic.astype(int)

    print(_ieic)
    print(_ieic.dtype)


    #Modified AGI only through 2002 

    _modagi = c00100 + puf_dict['e00400']

    _val_ymax = np.where(np.logical_and(puf_dict['MARS'] == 2, _modagi > 0), planX['ymax'][_ieic-1, puf_dict['FLPDYR']-2013] + planX['joint'][puf_dict['FLPDYR']-2013], 0)
    _val_ymax = np.where(np.logical_and(_modagi > 0, np.logical_or(puf_dict['MARS'] == 1, np.logical_or(puf_dict['MARS'] == 4, np.logical_or(puf_dict['MARS'] == 5, puf_dict['MARS'] == 7)))), planX['ymax'][_ieic-1, puf_dict['FLPDYR']-2013], _val_ymax)
    c59660 = np.where(np.logical_and(_modagi > 0, np.logical_or(puf_dict['MARS'] == 1, np.logical_or(puf_dict['MARS'] == 4, np.logical_or(puf_dict['MARS'] == 5, np.logical_or(puf_dict['MARS'] == 2, puf_dict['MARS'] == 7))))), np.minimum(planX['rtbase'][_ieic-1, puf_dict['FLPDYR']-2013] * c59560, planX['crmax'][_ieic-1, puf_dict['FLPDYR']-2013]), c59560)
    _preeitc =  np.where(np.logical_and(_modagi > 0, np.logical_or(puf_dict['MARS'] == 1, np.logical_or(puf_dict['MARS'] == 4, np.logical_or(puf_dict['MARS'] == 5, np.logical_or(puf_dict['MARS'] == 2, puf_dict['MARS'] == 7))))), c59660, 0)

    c59660 = np.where(np.logical_and(np.logical_and(puf_dict['MARS'] != 3, puf_dict['MARS'] != 6), np.logical_and(_modagi > 0, np.logical_or(_modagi > _val_ymax, c59560 > _val_ymax))), np.maximum(0, c59660 - planX['rtless'][_ieic-1, puf_dict['FLPDYR']-2013] * (np.maximum(_modagi, c59560) - _val_ymax)), c59560)
    _val_rtbase = np.where(np.logical_and(np.logical_and(puf_dict['MARS'] != 3, puf_dict['MARS'] != 6), _modagi > 0), planX['rtbase'][_ieic-1, puf_dict['FLPDYR']-2013] * 100, 0)
    _val_rtless = np.where(np.logical_and(np.logical_and(puf_dict['MARS'] != 3, puf_dict['MARS'] != 6), _modagi > 0), planX['rtless'][_ieic-1, puf_dict['FLPDYR']-2013] * 100, 0)

    _dy = np.where(np.logical_and(np.logical_and(puf_dict['MARS'] != 3, puf_dict['MARS'] != 6), _modagi > 0), puf_dict['e00400'] + puf_dict['e83080'] + puf_dict['e00300'] + puf_dict['e00600'] 
        + np.maximum(0, np.maximum(0, puf_dict['e01000']) - np.maximum(0, puf_dict['e40223']))
        + np.maximum(0, np.maximum(0, puf_dict['e25360']) - puf_dict['e25430'] - puf_dict['e25470'] - puf_dict['e25400'] - puf_dict['e25500'])
        + np.maximum(0, puf_dict['e26210'] + puf_dict['e26340'] + puf_dict['e27200'] - np.absolute(puf_dict['e26205']) - np.absolute(puf_dict['e26320'])), 0)

    c59660 = np.where(np.logical_and(np.logical_and(puf_dict['MARS'] != 3, puf_dict['MARS'] != 6), np.logical_and(_modagi > 0, _dy > planX['dylim'][puf_dict['FLPDYR']-2013])), 0, c59660)

    c59660 = np.where(np.logical_and(np.logical_and(puf_dict['cmp'] == 1, _ieic == 0), np.logical_and(np.logical_and(puf_dict['SOIYR'] - puf_dict['DOBYR'] >= 25, puf_dict['SOIYR'] - puf_dict['DOBYR'] < 65), np.logical_and(puf_dict['SOIYR'] - puf_dict['SDOBYR'] >= 25, puf_dict['SOIYR'] - puf_dict['SDOBYR'] < 65))), 0, c59660)
    c59660 = np.where(np.logical_and(_ieic == 0, np.logical_or(np.logical_or(_agep < 25, _agep >= 65), np.logical_or(_ages < 25, _ages >= 65))), 0, c59660)

def ChildTaxCredit():
    global _num
    global c07230
    global _precrd
    global _nctcr
    #Child Tax Credit
    #This var actually gets used in nonedcredit and c1040
    c07230 = DIMARRAY

    _num = np.where(puf_dict['MARS'] == 2, 2, 1)

    _nctcr = puf_dict['n24']

    _precrd = planX['chmax'][puf_dict['FLPDYR']-2013] * _nctcr 
    _ctcagi = puf_dict['e00100'] + _feided

    _precrd = np.where(np.logical_and(_ctcagi > planX['cphase'][puf_dict['MARS']-1], puf_dict['exact'] == 1), np.maximum(0, _precrd - 50 * np.ceil(np.maximum(0, _ctcagi - planX['cphase'][puf_dict['MARS']-1])/1000)), 0)
    _precrd = np.where(np.logical_and(_ctcagi > planX['cphase'][puf_dict['MARS']-1], puf_dict['exact'] != 1), np.maximum(0, _precrd - 50 * (np.maximum(0, _ctcagi - planX['cphase'][puf_dict['MARS']-1]) + 500)/1000), _precrd)

#def HopeCredit():
    #Hope credit for 1998-2009, I don't think this is needed 
    #Leave blank for now, ask Dan
    #SAS lnies 951 - 972

def AmOppCr():
    global c87521
    #American Opportunity Credit 2009+ 
    c87482 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(puf_dict['e87482'], 4000)), 0)
    c87487 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(puf_dict['e87487'], 4000)), 0)
    c87492 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(puf_dict['e87492'], 4000)), 0)
    c87497 = np.where(puf_dict['cmp'] == 1, np.maximum(0, np.minimum(puf_dict['e87497'], 4000)), 0)

    c87483 = np.where(np.maximum(0, c87482 - 2000) == 0, c87482, 2000 + 0.25 * np.maximum(0, c87482 - 2000))
    c87488 = np.where(np.maximum(0, c87487 - 2000) == 0, c87487, 2000 + 0.25 * np.maximum(0, c87487 - 2000))
    c87493 = np.where(np.maximum(0, c87492 - 2000) == 0, c87492, 2000 + 0.25 * np.maximum(0, c87492 - 2000))
    c87498 = np.where(np.maximum(0, c87497 - 2000) == 0, c87497, 2000 + 0.25 * np.maximum(0, c87497 - 2000))

    c87521 = c87483 + c87488 + c87493 + c87498

def LLC(puf):
    #Lifetime Learning Credit
    global c87550

    c87540 = np.where(puf == True, np.minimum(puf_dict['e87530'], planX['learn'][puf_dict['FLPDYR']-2013]), 0)
    c87550 = np.where(puf == True, 0.2 * c87540, 0)

    c87530 = np.where(puf == False, puf_dict['e87526'] + puf_dict['e87522'] + puf_dict['e87524'] + puf_dict['e87528'], 0)
    c87540 = np.where(puf == False, np.minimum(c87530, planX['learn'][puf_dict['FLPDYR']-2013]), c87540)
    c87550 = np.where(puf == False, 0.2 * c87540, c87550)

def RefAmOpp():
    #Refundable American Opportunity Credit 2009+

    c87654 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), 90000 * _num, 0)
    c87656 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), c00100, 0)
    c87658 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), np.maximum(0, c87654 - c87656), 0)
    c87660 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), 10000 * _num, 0)
    c87662 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), 1000 * np.minimum(1, c87658/c87660), 0)
    c87664 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), c87662 * c87521/1000, 0)
    c87666 = np.where(np.logical_and(puf_dict['cmp'] == 1, np.logical_and(c87521 > 0, puf_dict['EDCRAGE'] == 1)), 0, 0.4 * c87664)
    c10960 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), c87666, 0)
    c87668 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), c87664 - c87666, 0)
    c87681 = np.where(np.logical_and(puf_dict['cmp'] == 1, c87521 > 0), c87666, 0)

def NonEdCr(c87550):
    global c07220
    #Nonrefundable Education Credits

    #Form 8863 Tentative Education Credits
    c87560 = c87550

    #Phase Out
    c87570 = np.where(puf_dict['MARS'] == 2, planX['edphhm'][puf_dict['FLPDYR']-2013] * 1000, planX['edphhs'][puf_dict['FLPDYR']-2013] * 1000)
    c87580 = c00100
    c87590 = np.maximum(0, c87570 - c87580)
    c87600 = 10000 * _num
    c87610 = np.minimum(1, c87590/c87600)
    c87620 = c87560 * c87610

    _ctc1 = c07180 + puf_dict['e07200'] + c07230

    _ctc2 = puf_dict['e07240'] + puf_dict['e07960'] + puf_dict['e07260']
    _regcrd = _ctc1 + _ctc2
    _exocrd = puf_dict['e07700'] + puf_dict['e07250']
    _exocrd = _exocrd + puf_dict['t07950'] 
    _ctctax = c05800 - _regcrd - _exocrd
    c07220 = np.minimum(_precrd, np.maximum(0, _ctctax)) 
    #lt tax owed

def AddCTC(puf):
    #Additional Child Tax Credit

    #Part I of 2005 form 8812
    c82925 = np.where(_nctcr > 0, _precrd, 0)
    c82930 = np.where(_nctcr > 0, c07220, 0)
    c82935 = np.where(_nctcr > 0, c82925 - c82930, 0)
    #CTC not applied to tax

    c82880 = np.where(_nctcr > 0, np.maximum(0, puf_dict['e00200'] + puf_dict['e82882'] + puf_dict['e30100'] + np.maximum(0, _sey) - 0.5 * _setax), 0)
    c82880 = np.where(np.logical_and(_nctcr > 0, puf_dict['exact'] == 1), puf_dict['e82880'], c82880)
    h82880 = np.where(_nctcr > 0, c82880, 0)
    c82885 = np.where(_nctcr > 0, np.maximum(0, c82880 - planX['ealim'][puf_dict['FLPDYR']-2013]), 0)
    c82890 = np.where(_nctcr > 0, planX['adctcrt'][puf_dict['FLPDYR']-2013] * c82885, 0)

    #Part II of 2005 form 8812
    c82900 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), 0.0765 * np.minimum(planX['ssmax'][puf_dict['FLPDYR']-2013], c82880), 0)
    c82905 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), puf_dict['e03260'] + puf_dict['e09800'], 0)
    c82910 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), c82900 + c82905, 0)
    c82915 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), c59660 + puf_dict['e11200'], 0)
    c82920 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), np.maximum(0, c82910 - c82915), 0)
    c82937 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), np.maximum(c82890, c82920), 0)

    #Part II of 2005 form 8812
    c82940 = np.where(np.logical_and(_nctcr <= 2, c82890 > 0), np.minimum(c82890, c82935), c82890)
    c82940 = np.where(np.logical_and(_nctcr > 2, c82890 >= c82935), c82935, c82940)
    c82940 = np.where(np.logical_and(_nctcr > 2, c82890 < c82935), np.minimum(c82935, c82937), c82940)

    c11070 = c82940

    e59660 = np.where(puf == True, puf_dict['e59680'] + puf_dict['e59700'] + puf_dict['e59720'], 0)
    _othadd = puf_dict['e11070'] - c11070

    c11070 = np.where(puf_dict['fixup'] >= 4, c11070 + _othadd, c11070)

    # if c11070 eq 0 then do over _a8812; _a8812 = 0;end;
    # What does this line mean? -- Ask Dan

# def F5405():
    #Form 5405 First-Time Homebuyer Credit
    #not needed

    # c64450 = DIMARRAY

def C1040(puf):
    global c08795
    global c09200
    global c07100 
    global _eitc
    #Credits 1040 line 48

    c07100 = puf_dict['e07180'] + puf_dict['e07200'] + c07220 + c07230 + puf_dict['e07250'] + puf_dict['e07600'] + puf_dict['e07600'] + puf_dict['e07260'] + c07970 + puf_dict['e07300'] + puf_dict['x07400'] + puf_dict['e07500'] + puf_dict['e07700'] + puf_dict['e08000']

    y07100 = c07100

    c07100 = c07100 + puf_dict['e07240']
    c07100 = c07100 + puf_dict['e08001']
    c07100 = c07100 + puf_dict['e07960'] + puf_dict['e07970']
    c07100 = c07100 + puf_dict['e07980']

    x07100 = c07100
    c07100 = np.minimum(c07100, c05800)

    #Tax After credits 1040 line 52

    _eitc = c59660
    c08795 = np.maximum(0, c05800 - c07100)

    c08800 = c08795
    e08795 = np.where(puf == True, puf_dict['e08800'], 0)

    #Tax before refundable credits

    c09200 = c08795 + puf_dict['e09900'] + puf_dict['e09400'] + puf_dict['e09800'] + puf_dict['e10000'] + puf_dict['e10100']
    c09200 = c09200 + puf_dict['e09700']
    c09200 = c09200 + puf_dict['e10050']
    c09200 = c09200 + puf_dict['e10075']
    c09200 = c09200 + puf_dict['e09805']
    c09200 = c09200 + puf_dict['e09710'] + puf_dict['e09720']

def DEITC():
    global c59700
    #check this variable
    global c10950 
    c10950 = DIMARRAY
    #Decomposition of EITC 

    c59680 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, c08795 <= c59660)), c08795, 0)
    _comb = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, c08795 <= c59660)), c59660 - c59680, 0)

    c59680 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, c08795 > c59660)), c59660, c59680)
    _comb = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, c08795 > c59660)), 0, _comb)

    c59700 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(_comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 > _comb)))), _comb, 0)
    c59700 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(_comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 <= _comb)))), c09200 - c08795, c59700)
    c59720 = np.where(np.logical_and(c08795 > 0, np.logical_and(c59660 > 0, np.logical_and(_comb > 0, np.logical_and(c09200 - c08795 > 0, c09200 - c08795 <= _comb)))), c59660 - c59680 - c59700, 0)

    c59680 = np.where(np.logical_and(c08795 == 0, c59660 > 0), 0, c59680)
    c59700 = np.where(np.logical_and(c08795 == 0, np.logical_and(c59660 > 0, np.logical_and(c09200 > 0, c09200 > c59660))), c59660, c59700)
    c59700 = np.where(np.logical_and(c08795 == 0, np.logical_and(c59660 > 0, c09200 <= 0)), c09200, c59700)
    c59720 = np.where(np.logical_and(c08795 == 0, np.logical_and(c59660 > 0, c09200 <= 0)), c59660 - c59700, c59720)

    #Ask dan about this section of code! Line 1231 - 1241

    _compb = np.where(np.logical_and(c08795 <= 0, c59660 <= 0), 0, 0)
    c59680 = np.where(np.logical_and(c08795 <= 0, c59660 <= 0), 0, c59680)
    c59700 = np.where(np.logical_and(c08795 <= 0, c59660 <= 0), 0, c59700)
    c59720 = np.where(np.logical_and(c08795 <= 0, c59660 <= 0), 0, c59720)

    c07150 = c07100 + c59680
    c07150 = c07150

def SOIT(_eitc):
    _eitc = _eitc

    #SOI Tax (Tax after non-refunded credits plus tip penalty)
    c10300 = c09200 - puf_dict['e10000'] - puf_dict['e59680'] - c59700
    c10300 = c10300 - puf_dict['e11070']
    c10300 = c10300 - puf_dict['e11550']
    c10300 = c10300 - puf_dict['e11580']
    c10300 = c10300 - puf_dict['e09710'] - puf_dict['e09720'] - puf_dict['e11581'] - puf_dict['e11582']
    c10300 = c10300 - puf_dict['e87900'] - puf_dict['e87905'] - puf_dict['e87681'] - puf_dict['e87682']
    c10300 = c10300 - c10300 - c10950 - puf_dict['e11451'] - puf_dict['e11452']
    c10300 = c09200 - puf_dict['e09710'] - puf_dict['e09720'] - puf_dict['e10000'] - puf_dict['e11601'] - puf_dict['e11602']
    c10300 = np.maximum(c10300 , 0)

    #Ignore refundable partof _eitc to obtain SOI income tax

    _eitc = np.where(c09200 <= _eitc, c09200, _eitc)
    c10300 = np.where(c09200 <= _eitc, 0, c10300)






def Taxer(inc_in, inc_out, mars):
    low = np.where(inc_in < 3000, 1, 0)
    med = np.where(np.logical_and(inc_in >= 3000, inc_in < 100000), 1, 0)

    _a1 = inc_in/100
    _a2 = np.floor(_a1)
    _a3 = _a2*100
    _a4 = (_a1 - _a2) * 100

    _a5 = np.where(np.logical_and(low == 1, _a4 < 25), 13, 0)
    _a5 = np.where(np.logical_and(low == 1, np.logical_and(_a4 >= 25, _a4 < 50)), 38, _a5)
    _a5 = np.where(np.logical_and(low == 1, np.logical_and(_a4 >= 50, _a4 < 75)), 63, _a5)
    _a5 = np.where(np.logical_and(low == 1, _a4 >= 75), 88, _a5)

    _a5 = np.where(np.logical_and(med == 1, _a4 < 50), 25, _a5)
    _a5 = np.where(np.logical_and(med == 1, _a4 >= 50), 75, _a5)

    _a5 = np.where(inc_in == 0, 0, _a5)

    _a6 = np.where(np.logical_or(low==1, med ==1), _a3 + _a5, inc_in)

    inc_out = (planX['rt1'][puf_dict['FLPDYR']-2013] * np.minimum(_a6, planX['brk1'][puf_dict['FLPDYR']-2013, mars-1])
        + planX['rt2'][puf_dict['FLPDYR']-2013] 
        * np.minimum(planX['brk2'][puf_dict['FLPDYR']-2013, mars-1] - planX['brk1'][puf_dict['FLPDYR']-2013, mars-1],
            np.maximum(0, _a6 - planX['brk1'][puf_dict['FLPDYR']-2013, mars-1]))
        + planX['rt3'][puf_dict['FLPDYR']-2013]
        * np.minimum(planX['brk3'][puf_dict['FLPDYR']-2013, mars-1] - planX['brk2'][puf_dict['FLPDYR']-2013, mars-1],
            np.maximum(0, _a6 - planX['brk2'][puf_dict['FLPDYR']-2013, mars-1]))
        + planX['rt4'][puf_dict['FLPDYR']-2013]
        * np.minimum(planX['brk4'][puf_dict['FLPDYR']-2013, mars-1] - planX['brk3'][puf_dict['FLPDYR']-2013, mars-1],
            np.maximum(0, _a6 - planX['brk3'][puf_dict['FLPDYR']-2013, mars-1]))
        + planX['rt5'][puf_dict['FLPDYR']-2013]
        * np.minimum(planX['brk5'][puf_dict['FLPDYR']-2013, mars-1] - planX['brk4'][puf_dict['FLPDYR']-2013, mars-1],
            np.maximum(0, _a6 - planX['brk4'][puf_dict['FLPDYR']-2013, mars-1]))
        + planX['rt6'][puf_dict['FLPDYR']-2013]
        * np.minimum(planX['brk6'][puf_dict['FLPDYR']-2013, mars-1] - planX['brk5'][puf_dict['FLPDYR']-2013, mars-1],
            np.maximum(0, _a6 - planX['brk5'][puf_dict['FLPDYR']-2013, mars-1]))
        + planX['rt7'][puf_dict['FLPDYR']-2013] * np.maximum(0, _a6 -planX['brk6'][puf_dict['FLPDYR']-2013, mars-1]))

    return inc_out


def write_out_csv(outputs, out_name):
    output = np.column_stack(outputs)

    np.savetxt('output.csv', output, delimiter=',', 
        header = ('_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi,' 
            'c00100, c04600, c04470, c21060, _earned, c04800, c60000, c05750') 
        , fmt = '%1.3f')


def write_out_json(outputs, out_name):
    out_labels = (
        '_sep', '_txp', '_feided', 'c02900', '_ymod', 'c02700', 'c02500', 
        '_posagi','c00100', 'c04600', 'c04470', 'c21060', '_earned', 'c04800',
         'c60000', 'c05750')
    out_dict = dict(zip(out_labels, outputs))
    with open(out_name, 'w') as out_file:
        json_io.dump(out_dict, out_file, cls=json_io.NumpyArrayJSON, indent=1)


def Test(deficient_puf, puf_dict):
    if deficient_puf:
        puf_dict = Puf(puf_dict)
    FilingStatus()
    Adj()
    CapGains()
    SSBenefits()
    AGI()
    ItemDed(deficient_puf)
    EI_FICA()
    StdDed()
    XYZD()
    NonGain()
    TaxGains()
    MUI(c05750 = c05750)
    AMTI(deficient_puf)
    F2441(deficient_puf, _earned = _earned)
    DepCareBen()
    ExpEarnedInc()
    RateRed(c05800 = c05800)
    NumDep(deficient_puf)
    ChildTaxCredit()
    AmOppCr()
    LLC(deficient_puf)
    RefAmOpp()
    NonEdCr(c87550 = c87550)
    AddCTC(deficient_puf)
    # F5405()
    C1040(deficient_puf)
    DEITC()
    SOIT(_eitc = _eitc)

    outputs = (_sep, _txp, _feided, c02900, _ymod, c02700, c02500, _posagi, 
        c00100, c04600, c04470, c21060, _earned, c04800, c60000, c05750)

    write_out_json(outputs, 'output.json')
    # write_out_csv(outputs, 'output.csv')



Test(True, puf_dict)
