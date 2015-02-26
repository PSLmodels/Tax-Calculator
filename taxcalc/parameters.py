import numpy as np
from .utils import expand_array
import os
import json
from pkg_resources import resource_stream, Requirement

class Parameters(object):


    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    PARAM_FILENAME = "params.json"
    params_path = os.path.join(CUR_PATH, PARAM_FILENAME)

    @classmethod
    def from_file(cls, file_name, **kwargs):
        with open(file_name) as f:
            params = json.loads(f.read())

        return cls(data=params, **kwargs)


    def __init__(self, start_year=2013, budget_years=10,
                 inflation_rate=0.02, data=None):
        self._current_year = start_year
        self._start_year = start_year

        if data:
            self._vals = data
        else:
            self._vals = default_data(metadata=True)

        # INITIALIZE
        for name, data in self._vals.items():
            cpi_inflated =  data.get('cpi_inflated', False)
            values = data['value']
            setattr(self, name, expand_array(np.array(values),
                inflate=cpi_inflated, inflation_rate=inflation_rate,
                num_years=budget_years))

        self.set_year(start_year)

    @property
    def current_year(self):
        return self._current_year

    @property
    def start_year(self):
        return self._start_year

    def increment_year(self):
        self._current_year += 1
        self.set_year(self._current_year)

    def set_year(self, yr):
        for name, vals in self._vals.items():
            arr = getattr(self, name)
            setattr(self, name[1:], arr[yr-self._start_year])


def default_data(metadata=False):
    """ Retreive of default parameters """
    parampath = Parameters.params_path
    if not os.path.exists(parampath):
        path_in_egg = os.path.join("taxcalc", Parameters.PARAM_FILENAME)
        buf = resource_stream(Requirement.parse("taxcalc"), path_in_egg)
        _bytes = buf.read()
        as_string = _bytes.decode("utf-8")
        params = json.loads(as_string)
    else:
        with open(Parameters.params_path) as f:
            params = json.load(f)

    if (metadata):
        return params
    else:
        return { k: v['value'] for k,v in params.items()}
