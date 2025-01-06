"""
Test Data class and its methods.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_data.py
# pylint --disable=locally-disabled test_data.py

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from taxcalc import Data, GrowFactors


# Test specification and use of simple Data-derived class.
# This derived class is called Recs and it contains aged data.
#
# The following pytest fixture specifies the VARINFO file for the
# Recs class, which is defined in the test_recs_class function.


VARINFO_JSON = """
{
  "read": {
    "RECID": {
      "required": true,
      "type": "int",
      "desc": "Unique numeric identifier for record"
    },
    "MARS": {
      "required": true,
      "type": "int",
      "desc": "Filing (marital) status [1..5]"
    },
    "e00300": {
      "type": "float",
      "desc": "Taxable interest income"
    },
    "s006": {
      "type": "float",
      "desc": "Record sampling weight"
    }
  },
  "calc": {
    "expanded_income": {
      "type": "float"
    }
  }
}
"""


@pytest.fixture(scope='module', name='recs_varinfo_file')
def fixture_recs_varinfo_json_file():
    """
    Define JSON VARINFO file for Data-derived Recs class.
    """
    with tempfile.NamedTemporaryFile(mode='a', delete=False) as pfile:
        pfile.write(VARINFO_JSON + '\n')
    pfile.close()
    yield pfile
    os.remove(pfile.name)


def test_recs_class(recs_varinfo_file, cps_subsample):
    """
    Specify Data-derived Recs class and test it.
    """

    class Recs(Data):
        """
        The Recs class is derived from the abstract base Data class.
        """
        VARINFO_FILE_NAME = recs_varinfo_file.name
        VARINFO_FILE_PATH = ''

        def __init__(self, data, start_year, gfactors, weights):
            super().__init__(data, start_year, gfactors, weights)

        def _extrapolate(self, year):
            val = getattr(self, 'e00300')
            setattr(
                self, 'e00300', val * self.gfactors.factor_value('AINTS', year)
            )

    # test Recs class for incorrect instantiation:
    with pytest.raises(ValueError):
        Recs(data=[], start_year=2000,
             gfactors=None, weights=None)
    with pytest.raises(ValueError):
        Recs(data=cps_subsample, start_year=[],
             gfactors=None, weights=None)
    with pytest.raises(ValueError):
        Recs(data=cps_subsample, start_year=2000,
             gfactors=None, weights='')
    with pytest.raises(ValueError):
        Recs(data=cps_subsample, start_year=2000,
             gfactors=GrowFactors(), weights=None)
    with pytest.raises(ValueError):
        Recs(data=cps_subsample, start_year=2000,
             gfactors='', weights='')
    # test Recs class for correct instantiation with no aging of data:
    syr = 2014
    rec = Recs(data=cps_subsample, start_year=syr,
               gfactors=None, weights=None)
    assert np.all(getattr(rec, 'MARS') != 0)
    assert getattr(rec, 'data_year') == syr
    assert getattr(rec, 'current_year') == syr
    sum_e00300_in_syr = getattr(rec, 'e00300').sum()
    rec.increment_year()
    assert getattr(rec, 'data_year') == syr
    assert getattr(rec, 'current_year') == syr + 1
    sum_e00300_in_syr_plus_one = getattr(rec, 'e00300').sum()
    assert np.allclose([sum_e00300_in_syr], [sum_e00300_in_syr_plus_one])
    del rec
    # test Recs class for correct instantiation with aging of data
    wghts_path = os.path.join(GrowFactors.FILE_PATH, 'cps_weights.csv.gz')
    wghts_df = pd.read_csv(wghts_path)
    rec = Recs(data=cps_subsample, start_year=syr,
               gfactors=GrowFactors(), weights=wghts_df)
    assert isinstance(rec, Recs)
    assert np.all(getattr(rec, 'MARS') != 0)
    assert getattr(rec, 'data_year') == syr
    assert getattr(rec, 'current_year') == syr
    sum_s006_in_syr = getattr(rec, 's006').sum()
    sum_e00300_in_syr = getattr(rec, 'e00300').sum()
    rec.increment_year()
    assert getattr(rec, 'data_year') == syr
    assert getattr(rec, 'current_year') == syr + 1
    sum_s006_in_syr_plus_one = getattr(rec, 's006').sum()
    assert sum_s006_in_syr_plus_one > sum_s006_in_syr
    sum_e00300_in_syr_plus_one = getattr(rec, 'e00300').sum()
    assert sum_e00300_in_syr_plus_one > sum_e00300_in_syr
    # test private methods:
    # pylint: disable=protected-access
    rec._read_data(data=None)
    rec._read_weights(weights=None)
    with pytest.raises(ValueError):
        rec._read_weights(weights=[])
