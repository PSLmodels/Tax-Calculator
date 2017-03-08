from taxcalc.calculate import *
from taxcalc.policy import *
from taxcalc.behavior import *
from taxcalc.consumption import *
from taxcalc.filings import *
from taxcalc.growfactors import *
from taxcalc.growdiff import *
from taxcalc.records import *
from taxcalc.taxcalcio import *
from taxcalc.utils import *
from taxcalc.decorators import *
from taxcalc.macro_elasticity import *
from taxcalc.dropq import *

from taxcalc._version import get_versions
__version__ = get_versions()['version']
del get_versions
