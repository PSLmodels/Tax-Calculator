import os
import sys
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, "../../"))
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
import tempfile
from numba import jit, vectorize, guvectorize
from taxcalc import *
from taxcalc.utils import expand_array

tax_dta_path = os.path.join(CUR_PATH, "../../tax_all1991_puf.gz")


def test_create_records():
    r = Records(tax_dta_path)
    assert r

def test_create_records_from_file():
    r = Records.from_file(tax_dta_path)
    assert r
