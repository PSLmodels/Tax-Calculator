import numpy as np
from .utils import expand_array
import os
import json
from pkg_resources import resource_stream, Requirement

DEFAULT_START_YEAR = 2013

class Parameters(object):


    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    PARAM_FILENAME = "params.json"
    params_path = os.path.join(CUR_PATH, PARAM_FILENAME)

    #Mapping of year to inflation rate
    __rates = {2013:0.015, 2014:0.020, 2015:0.022, 2016:0.020, 2017:0.021,
               2018:0.022, 2019:0.023, 2020:0.024, 2021:0.024, 2022:0.024,
               2023:0.024, 2024:0.024}

    @classmethod
    def from_file(cls, file_name, **kwargs):
        if file_name:
            with open(file_name) as f:
                params = json.loads(f.read())
        else:
            params = None

        return cls(data=params, **kwargs)


    def __init__(self, start_year=DEFAULT_START_YEAR, budget_years=12,
                 inflation_rate=None, inflation_rates=None, data=None,
                 **kwargs):

        if inflation_rate and inflation_rates:
            raise ValueError("Can only specify either one constant inflation"
                             " rate or a list of inflation rates")

        self._inflation_rates = None

        if inflation_rate:
            self._inflation_rates = [inflation_rate] * budget_years

        if inflation_rates:
            assert len(inflation_rates) == budget_years
            self._inflation_rates = [inflation_rates[start_year + i]
                                     for i in range(0, budget_years)]


        if not self._inflation_rates:
            self._inflation_rates = [self.__rates[start_year + i]
                                     for i in range(0, budget_years)]

        self._current_year = start_year
        self._start_year = start_year
        self._budget_years = budget_years

        if data:
            self._vals = data
        else:
            self._vals = default_data(metadata=True)

        # INITIALIZE
        for name, data in self._vals.items():
            cpi_inflated =  data.get('cpi_inflated', False)
            values = data['value']
            setattr(self, name, expand_array(values,
                inflate=cpi_inflated, inflation_rates=self._inflation_rates,
                num_years=budget_years))

        self.set_year(start_year)

    def update(self, year_mods):
        """
        Take a dictionary of year: {name:val} mods and set them on this Parameters object.
        'year_mods' is a dictionary of year: mods where mods is a dict of key:value pairs
        and key_cpi:Bool pairs. The key_cpi:Bool pairs indicate if the value for 'key'
        should be inflated

        Parameters:
        ----------
        mods: dict
        """

        if not all(isinstance(k, int) for k in year_mods.keys()):
            raise ValueError("Every key must be a year, e.g. 2011, 2012, etc.")

        for year, mods in year_mods.items():

            num_years_to_expand = (self.start_year + self.budget_years) - year
            for name, values in mods.items():
                if name.endswith("_cpi"):
                    continue
                cpi_inflated = mods.get(name + "_cpi", False)

                if year == self.start_year and year == self.current_year:
                    nval = expand_array(values,
                                        inflate=cpi_inflated,
                                        inflation_rates=self._inflation_rates,
                                        num_years=num_years_to_expand)
                    setattr(self, name, nval)

                elif year <= self.current_year and year >= self.start_year:
                    # advance until the parameter is in line with the current
                    # year
                    num_years_to_skip=self.current_year - year
                    inf_rates = [self.__rates[year + i]
                                 for i in range(0, num_years_to_expand)]

                    nval = expand_array(values,
                                        inflate=cpi_inflated,
                                        inflation_rates=inf_rates,
                                        num_years=num_years_to_expand)

                    if self.current_year > self.start_year:
                        cur_val = getattr(self, name)
                        offset = self.current_year - self.start_year
                        cur_val[offset:] = nval[num_years_to_skip:]
                    else:
                        setattr(self, name, nval[num_years_to_skip:])

                else: # year > current_year
                    msg = ("Can't specify a parameter for a year that is in the"
                           " future because we don't know how to fill in the "
                           " values for the years between {0} and {1}.")
                    raise ValueError(msg.format(self.current_year, year))


            # Set up the '_X = [a, b,...]' variables as 'X = a'
            self.set_year(self._current_year)

    @property
    def current_year(self):
        return self._current_year

    @property
    def start_year(self):
        return self._start_year

    @property
    def budget_years(self):
        return self._budget_years

    def increment_year(self):
        self._current_year += 1
        self.set_year(self._current_year)

    def set_year(self, yr):
        for name, vals in self._vals.items():
            arr = getattr(self, name)
            setattr(self, name[1:], arr[yr-self._start_year])


def default_data(metadata=False, start_year=None):
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

    if start_year:
        for k, v in params.items():
            first_year = v.get('start_year', DEFAULT_START_YEAR)
            assert isinstance(first_year, int)

            if start_year < first_year:
                msg = "Can't set a start year of {0}, because it is before {1}"
                raise ValueError(msg.format(start_year, first_year))

            #Set the new start year:
            v['start_year'] = start_year

            #Work with the values
            vals = v['value']
            last_year_for_data = first_year + len(vals) - 1

            if last_year_for_data < start_year:
                if v['row_label']:
                    v['row_label'] = ["2015"]
                #Need to produce new values
                new_val = vals[-1]
                if v['cpi_inflated'] is True:
                    if isinstance(new_val, list):
                        for y in range(last_year_for_data, start_year):
                            new_val = [x * (1.0 + Parameters._Parameters__rates[y]) for x in new_val]
                    else:
                        for y in range(last_year_for_data, start_year):
                            new_val *= 1.0 + Parameters._Parameters__rates[y]
                #Set the new values
                v['value'] = [new_val]

            else:
                #Need to get rid of [first_year, ..., start_year-1] values
                years_to_chop = start_year - first_year
                if v['row_label']:
                    v['row_label'] = v['row_label'][years_to_chop:]
                v['value'] = v['value'][years_to_chop:]

    if (metadata):
        return params
    else:
        return { k: v['value'] for k,v in params.items()}
