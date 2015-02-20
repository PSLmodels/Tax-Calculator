import numpy as np
from .utils import expand_array
import os


class Parameters(object):


    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    params_path = os.path.join(CUR_PATH, "params.json")

    @classmethod
    def from_file(cls, file_name, **kwargs):
        import json
        with open(file_name) as f:
            params = json.loads(f.read())

        params = { k: v['value'] for k, v in params.items()}

        return cls(data=params, **kwargs)


    def __init__(self, start_year=2013, budget_years=10,
                 inflation_rate=0.02, data=None):
        self._current_year = start_year
        self._start_year = start_year

        if data:
            self._vals = data
        else:
            self._vals = self._default_data()

        # INITIALIZE
        [setattr(self, name, expand_array(np.array(val),
             inflation_rate=inflation_rate, num_years=budget_years))
             for name, val in self._vals.items()]

        self.set_year(start_year)



    def _default_data(self):
        """ Set of default parameters, if no file specified """
        import json
        with open(self.params_path) as f:
            paramfile = json.load(f)

        paramdata = { k: v['value'] for k,v in paramfile.items()}

        return paramdata

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
