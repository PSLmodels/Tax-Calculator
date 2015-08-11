"""
Replaces functions called in test.run()
with versions decorated with '@time_this(main_timer)'

This calls a cumulative timer that is ran for each of the functions below,
raw calculation time can be printed by calling
'print(main_timer)' at the end of the testing script.
"""


from taxcalc.calculate import *
from taxcalc.puf import *
from .timer_utils import cumulative_timer, time_this

from timer_utils import cumulative_timer, time_this

main_timer = cumulative_timer("All Fuctions, no CSV calls, no concat calls")

# Below are the functions called in the run() method in test.py.
# This is equivalent to decorating each function in taxcalc.calculate
# with @time_this(main_timer).
# To time a single function, not as a running total,
# use decorator simply as @time_this or func = time_this(func).


Calculator = time_this(Calculator, main_timer)
set_input_data = time_this(set_input_data, main_timer)
update_globals_from_calculator = time_this(update_globals_from_calculator,
                                           main_timer)
update_calculator_from_module = time_this(update_calculator_from_module,
                                          main_timer)

FilingStatus = time_this(FilingStatus, main_timer)
Adj = time_this(Adj, main_timer)
CapGains = time_this(CapGains, main_timer)
SSBenefits = time_this(SSBenefits, main_timer)
AGI = time_this(AGI, main_timer)
ItemDed = time_this(ItemDed, main_timer)
EI_FICA = time_this(EI_FICA, main_timer)
StdDed = time_this(StdDed, main_timer)
XYZD = time_this(XYZD, main_timer)
NonGain = time_this(NonGain, main_timer)
TaxGains = time_this(TaxGains, main_timer)
MUI = time_this(MUI, main_timer)
AMTI = time_this(AMTI, main_timer)
F2441 = time_this(F2441, main_timer)
DepCareBen = time_this(DepCareBen, main_timer)
ExpEarnedInc = time_this(ExpEarnedInc, main_timer)
RateRed = time_this(RateRed, main_timer)
NumDep = time_this(NumDep, main_timer)
ChildTaxCredit = time_this(ChildTaxCredit, main_timer)
AmOppCr = time_this(AmOppCr, main_timer)
LLC = time_this(LLC, main_timer)
RefAmOpp = time_this(RefAmOpp, main_timer)
NonEdCr = time_this(NonEdCr, main_timer)
AddCTC = time_this(AddCTC, main_timer)
F5405 = time_this(F5405, main_timer)
C1040 = time_this(C1040, main_timer)
DEITC = time_this(DEITC, main_timer)
SOIT = time_this(SOIT, main_timer)
