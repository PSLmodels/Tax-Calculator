"""
Non Puf related variables
"""

import numpy as np

_adctcrt = np.array([0.15])
 #Rate for additional ctc

_aged = np.array([  [1500, 1200],
                    [1550, 1200],
                    [1550, 1250]]) 
#Extra std. ded. for aged // (CPI-U)  

_almdep = np.array([7150,
                    7250,
                    7400,]) 
#Child AMT Exemption base // UPDATE SAS // (CPI-U)

_almsp = np.array([ 179500,
                    182500,
                    185400,]) 
#AMT bracket // (CPI-U)

_amex = np.array([  3900,
                    3950,
                    4000,]) 
#Personal Exemption // (CPI-U) 

_amtage = np.array([24]) 
#Age for full AMT exclusion

_amtsep = np.array([238550,
                    242450,]) 
#AMT Exclusion // UPDATE SAS // (CPI-U)

_almsep = np.array([40400,
                    41050,]) 
#Extra alminc for married sep // UPDATE SAS // (CPI-U)

_agcmax = np.array([15000]) 
#??

_cgrate1 = np.array([0.10]) 
#Initial rate on long term gains

_cgrate2 = np.array([0.20]) 
#Normal rate on long term gains

_chmax = np.array([ 1000,
                    1000,
                    1000,
                    1000,
                    1000,
                    500,]) #Scheduled to decrease to 500 in 2018         
#Max Child Tax Credit per child 

#                   0kids  1kid    2kids   3+kids
_crmax = np.array([ [487, 3250, 5372, 6044],
                    [496, 3305, 5460, 6143],
                    [503, 3359, 5548, 6242],]) 
#Max earned income credit // (CPI-U)

_dcmax = np.array([3000]) 
#Max dependent care expenses 

_dylim = np.array([ 3300,
                    3350,
                    3400]) 
#Limits for Disqualified Income // (CPI-U)

_ealim = np.array([ 3000,
                    3000,
                    3000,
                    3000,
                    3000,
                    10000,]) #scheduled to return to 10,000 in 2018, afterwards indexed to inflation. 
#Max earn ACTC // CPI-U after 2018. 

_edphhs = np.array([63,
                    64,
                    65,]) 
#End of educ phaseout - singles // (CPI-U)

_edphhm = np.array([126,
                    128,
                    130,]) 
#End of educ phaseout - married // (CPI-U)

_feimax = np.array([97600,
                    99200,
                    100800]) 
#Maximum foreign earned income exclusion

#_hopelm = np.array([1200])

#                    0kids 1kid  2kids 3+kids
_joint = np.array([ [5340, 5340, 5340, 5340],
                    [5430, 5430, 5430, 5430],
                    [5510, 5520, 5520, 5520],])

#Extra to ymax for joint // UPDATE SAS // (CPI-U)

_learn = np.array([10000]) 
#Expense limit for the Lifetime Learning Credit

_pcmax = np.array([35]) 
#Maximum Percentage for f2441


#                    singl   joint   sep     hh      widow   sep
_phase2 = np.array([[250000, 300000, 150000, 275000, 300000, 150000],
                    [254200, 305050, 152525, 279650, 305050, 152525],
                    [258250, 309900, 154950, 284050, 309900, 154950],])
#Itemized deduction limitation AGI threshhold  // UPDATE SAS // rename // (CPI-U)

#                    0kids   1kid    2kids   3+kids
_rtbase = np.array([[0.0765, 0.3400, 0.4000, 0.4500]]) 
#EIC base rate // UPDATE SAS

#                    0kids   1kid    2kids   3+kids
_rtless = np.array([[0.0765, 0.1598, 0.2106, 0.2106]]) 
#EIC _phaseout rate

_ssmax = np.array([ 113700,
                    117000,
                    118500]) 
#SS Maximum taxable earnings // UPDATE SAS // (CPI-U)
#http://www.ssa.gov/oact/cola/cbb.html

#                    0kids 1kid   2kids  3+kids
_ymax = np.array([  [7970, 17530, 17530, 17530],
                    [8110, 17830, 17830, 17830],
                    [8240, 18110, 18110, 18110]]) 
#Start of EIC _phaseout // (CPI-U)

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

#                    singl   joint   sep    hh      widow   sep
_amtys = np.array([ [115400, 153900, 76950, 115400, 153900, 76950],
                    [117300, 156500, 78250, 117300, 156500, 78250],
                    [119200, 158900, 79450, 119200, 158900, 79450],]) 
#AMT Phaseout Start // UPDATE SAS //  (CPI-U)

#                  singl   joint   sep    hh      widow   sep
_cphase = np.array([75000, 110000, 55000, 75000, 75000, 55000]) 
#Child Tax Credit Phase-Out

#                   singl   joint   sep    hh      widow   sep
_thresx = np.array([200000, 250000, 125000, 200000, 250000, 125000]) 
#Threshold for add medicare

#                  singl  joint sep hh     widow  sep
_ssb50 = np.array([25000, 32000, 0, 25000, 25000, 0]) 
#SS 50% taxability threshold

#                  singl  joint sep hh    widow  sep
_ssb85 = np.array([34000, 44000, 0, 34000, 34000, 0]) 
#SS 85% taxability threshold 

#                   singl   joint  sep    hh     widow  sep
_amtex = np.array([ [51900, 80800, 40400, 51900, 80800, 40400], 
                    [52800, 82100, 41050, 52800, 82100, 41050],
                    [53600, 83400, 41700, 53600, 83400, 41700],]) 
#AMT Exclusion // UPDATE SAS // (CPI-U) 

#                   singl    joint   sep     hh      widow   sep
_exmpb = np.array([ [250000, 300000, 150000, 275000, 300000, 150000], 
                    [254200, 305050, 152525, 279650, 305050, 152525],
                    [258250, 309900, 154950, 284040, 309900, 154950],]) 
#Personal Exemption Amount // UPDATE SAS // check on widow&sep // (CPI-U)

#                   singl  joint  sep   hh    widow  sep   dep
_stded = np.array([ [6100, 12200, 6100, 8950, 12200, 6100, 1000], 
                    [6200, 12400, 6200, 9100, 12400, 6200, 1000],
                    [6300, 12600, 6300, 9250, 12600, 6300, 1050],])
 #Standard Deduction // (CPI-U)

#                   singl  joint  sep   hh     widow  sep
_brk1 = np.array([  [8925, 17850, 8925, 12750, 17850, 8925], 
                    [9075, 18150, 9075, 12950, 18150, 9075],
                    [9225, 18450, 9225, 13150, 18450, 9225],]) 
#10% tax rate thresholds // (CPI-U)

#                   singl   joint  sep    hh     widow  sep
_brk2 = np.array([  [36250, 72500, 36250, 48600, 72500, 36250], 
                    [36900, 73800, 36900, 49400, 73800, 36900],
                    [37450, 74900, 37450, 50200, 74900, 37450],])
 #15% tax rate thresholds // (CPI-U)

#                   singl   joint   sep    hh      widow   sep
_brk3 = np.array([  [87850, 146400, 73200, 125450, 146400, 73200], 
                    [89350, 148850, 74425, 127550, 148850, 74425],
                    [90750, 151200, 75600, 129600, 151200, 75600],]) 
#25% tax rate thresholds // (CPI-U)

#                    singl   joint   sep     hh      widow   sep
_brk4 = np.array([  [183250, 223050, 111525, 203150, 223050, 111525], 
                    [186350, 226850, 113425, 206600, 226850, 113425],
                    [189300, 230450, 115225, 209850, 230450, 115225],]) 
#28% tax rate thresholds // (CPI-U)

#                   singl    joint   sep     hh      widow   sep
_brk5 = np.array([  [398350, 398350, 199175, 398350, 398350, 199175], 
                    [405100, 405100, 202550, 405100, 405100, 202550],
                    [411500, 411500, 205750, 411500, 411500, 205750],]) 
#33% tax rate thresholds //  (CPI-U)

#                    singl   joint   sep     hh      widow   sep
_brk6 = np.array([  [400000, 450000, 225000, 425000, 450000, 225000], #Young's from 2013 paper are wrong (fiscal cliff)
                    [406750, 457600, 228800, 432200, 457600, 228800],
                    [413200, 464850, 223425, 439000, 464850, 223425],]) 
#35% tax rate thresholds  // (CPI-U)

__all__ = [loc for loc in locals().keys() if "__" not in loc]
