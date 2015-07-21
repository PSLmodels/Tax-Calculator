"""
Replaces functions called in test.run() with versions decorated with a cumulative_timer for each function'
"""


from taxcalc.calculate import *
from taxcalc.puf import *
from .timer_utils import cumulative_timer, time_this

timers = []

FilingStatus_timer = cumulative_timer("FilingStatus()", avg_time=True)
timers.append(FilingStatus_timer)
FilingStatus = time_this(FilingStatus, FilingStatus_timer)

Adj_timer = cumulative_timer("Adj()", avg_time=True)
timers.append(Adj_timer)
Adj = time_this(Adj, Adj_timer)

CapGains_timer = cumulative_timer("CapGains()", avg_time=True)
timers.append(CapGains_timer)
CapGains = time_this(CapGains, CapGains_timer)

SSBenefits_timer = cumulative_timer("SSBenefits()", avg_time=True)
timers.append(SSBenefits_timer)
SSBenefits = time_this(SSBenefits, SSBenefits_timer)

AGI_timer = cumulative_timer("AGI()", avg_time=True)
timers.append(AGI_timer)
AGI = time_this(AGI, AGI_timer)

ItemDed_timer = cumulative_timer("ItemDed()", avg_time=True)
timers.append(ItemDed_timer)
ItemDed = time_this(ItemDed, ItemDed_timer)

EI_FICA_timer = cumulative_timer("EI_FICA()", avg_time=True)
timers.append(EI_FICA_timer)
EI_FICA = time_this(EI_FICA, EI_FICA_timer)

StdDed_timer = cumulative_timer("StdDed()", avg_time=True)
timers.append(StdDed_timer)
StdDed = time_this(StdDed, StdDed_timer)

XYZD_timer = cumulative_timer("XYZD()", avg_time=True)
timers.append(XYZD_timer)
XYZD = time_this(XYZD, XYZD_timer)

NonGain_timer = cumulative_timer("NonGain()", avg_time=True)
timers.append(NonGain_timer)
NonGain = time_this(NonGain, NonGain_timer)

TaxGains_timer = cumulative_timer("TaxGains()", avg_time=True)
timers.append(TaxGains_timer)
TaxGains = time_this(TaxGains, TaxGains_timer)

MUI_timer = cumulative_timer("MUI()", avg_time=True)
timers.append(MUI_timer)
MUI = time_this(MUI, MUI_timer)

AMTI_timer = cumulative_timer("AMTI()", avg_time=True)
timers.append(AMTI_timer)
AMTI = time_this(AMTI, AMTI_timer)

F2441_timer = cumulative_timer("F2441()", avg_time=True)
timers.append(F2441_timer)
F2441 = time_this(F2441, F2441_timer)

DepCareBen_timer = cumulative_timer("DepCareBen()", avg_time=True)
timers.append(DepCareBen_timer)
DepCareBen = time_this(DepCareBen, DepCareBen_timer)

ExpEarnedInc_timer = cumulative_timer("ExpEarnedInc()", avg_time=True)
timers.append(ExpEarnedInc_timer)
ExpEarnedInc = time_this(ExpEarnedInc, ExpEarnedInc_timer)

RateRed_timer = cumulative_timer("RateRed()", avg_time=True)
timers.append(RateRed_timer)
RateRed = time_this(RateRed, RateRed_timer)

NumDep_timer = cumulative_timer("NumDep()", avg_time=True)
timers.append(NumDep_timer)
NumDep = time_this(NumDep, NumDep_timer)

ChildTaxCredit_timer = cumulative_timer("ChildTaxCredit()", avg_time=True)
timers.append(ChildTaxCredit_timer)
ChildTaxCredit = time_this(ChildTaxCredit, ChildTaxCredit_timer)

AmOppCr_timer = cumulative_timer("AmOppCr()", avg_time=True)
timers.append(AmOppCr_timer)
AmOppCr = time_this(AmOppCr, AmOppCr_timer)

LLC_timer = cumulative_timer("LLC()", avg_time=True)
timers.append(LLC_timer)
LLC = time_this(LLC, LLC_timer)

RefAmOpp_timer = cumulative_timer("RefAmOpp()", avg_time=True)
timers.append(RefAmOpp_timer)
RefAmOpp = time_this(RefAmOpp, RefAmOpp_timer)

NonEdCr_timer = cumulative_timer("NonEdCr)", avg_time=True)
timers.append(NonEdCr_timer)
NonEdCr = time_this(NonEdCr, NonEdCr_timer)

AddCTC_timer = cumulative_timer("AddCTC()", avg_time=True)
timers.append(AddCTC_timer)
AddCTC = time_this(AddCTC, AddCTC_timer)

F5405_timer = cumulative_timer("F5405()", avg_time=True)
timers.append(F5405_timer)
F5405 = time_this(F5405, F5405_timer)

C1040_timer = cumulative_timer("C1040()", avg_time=True)
timers.append(C1040_timer)
C1040 = time_this(C1040, C1040_timer)

DEITC_timer = cumulative_timer("DEITC()", avg_time=True)
timers.append(DEITC_timer)
DEITC = time_this(DEITC, DEITC_timer)

SOIT_timer = cumulative_timer("SOIT()", avg_time=True)
timers.append(SOIT_timer)
SOIT = time_this(SOIT, SOIT_timer)



